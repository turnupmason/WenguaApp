from pathlib import Path
from tempfile import TemporaryDirectory
import base64
import hashlib
import hmac
import json
import subprocess
import unittest
from unittest.mock import Mock

from src.wengua import course_delivery_v1 as d


def fixture():
    f=json.loads((d.ROOT/'tests/fixtures/course_delivery_cipher.json').read_text(encoding='utf8'))
    return f,bytes.fromhex(f['key_hex']),base64.b64decode(f['envelope_base64'])


class PrivateCourseDelivery(unittest.TestCase):
    def test_fixture_authenticates_and_keys_are_domain_separated(self):
        f,key,blob=fixture();enc,iv,cipher=d.authenticate(blob,key)
        self.assertNotEqual(*d.derive_keys(key));self.assertEqual(len(enc),32);self.assertEqual(len(iv),16);self.assertEqual(len(cipher)%16,0)

    def test_wrong_key_and_every_envelope_region_tampering_rejected_before_decryption(self):
        f,key,blob=fixture();decrypt=Mock()
        with TemporaryDirectory() as tmp:
            for payload,secret in [(blob,b'0'*32),*( (blob[:i]+bytes([blob[i]^1])+blob[i+1:],key) for i in [0,9,28,len(blob)-1])]:
                with self.subTest(index=payload[:8]),self.assertRaises(ValueError):
                    d.install(payload,secret,Path(tmp)/'x.zip',expected_sha256=f['plain_sha256'],decrypt=decrypt)
            self.assertFalse((Path(tmp)/'x.zip').exists())
        decrypt.assert_not_called()

    def test_authenticated_bad_cipher_length_rejected(self):
        f,key,blob=fixture();_,mac=d.derive_keys(key);body=blob[:-33];bad=body+hmac.new(mac,body,hashlib.sha256).digest()
        with self.assertRaises(ValueError):d.authenticate(bad,key)

    def test_success_exact_sha_and_idempotent_existing_output(self):
        f,key,blob=fixture();plain=f['plaintext_utf8'].encode()
        with TemporaryDirectory() as tmp:
            path=Path(tmp)/'Downloads'/'file.zip'
            self.assertEqual(d.install(blob,key,path,expected_sha256=f['plain_sha256'],decrypt=lambda *a:plain),path)
            self.assertEqual(path.read_bytes(),plain)
            d.install(blob,key,path,expected_sha256=f['plain_sha256'],decrypt=lambda *a:plain)
            self.assertFalse(list(path.parent.glob('*.pending')))

    def test_wrong_plain_hash_never_installs_and_different_file_never_overwritten(self):
        f,key,blob=fixture()
        with TemporaryDirectory() as tmp:
            path=Path(tmp)/'file.zip'
            with self.assertRaisesRegex(ValueError,'SHA256'):d.install(blob,key,path,expected_sha256=f['plain_sha256'],decrypt=lambda *a:b'wrong')
            self.assertFalse(path.exists());path.write_bytes(b'keep me')
            with self.assertRaises(FileExistsError):d.install(blob,key,path,expected_sha256=f['plain_sha256'],decrypt=lambda *a:f['plaintext_utf8'].encode())
            self.assertEqual(path.read_bytes(),b'keep me')

    def test_windows_builtin_crypto_command_uses_stdin_and_no_key_in_argv(self):
        f,key,blob=fixture();k,iv,c=d.authenticate(blob,key);plain=f['plaintext_utf8'].encode()
        run=Mock(return_value=subprocess.CompletedProcess([],0,base64.b64encode(plain).decode(),''))
        self.assertEqual(d.windows_decrypt(k,iv,c,runner=run),plain)
        args,kw=run.call_args;self.assertEqual(args[0][0],'powershell.exe')
        self.assertNotIn(base64.b64encode(k).decode(),str(args));payload=json.loads(kw['input'])
        self.assertEqual(base64.b64decode(payload['key']),k);self.assertEqual(kw['timeout'],120)

    def test_builtin_crypto_failure_and_invalid_output_stop_without_plaintext_logging(self):
        f,key,blob=fixture();k,iv,c=d.authenticate(blob,key)
        for result in [subprocess.CompletedProcess([],1,'secret output','secret error'),subprocess.CompletedProcess([],0,'not base64','')]:
            with self.assertRaises(RuntimeError) as caught:d.windows_decrypt(k,iv,c,runner=lambda *a,**kw:result)
            self.assertNotIn('secret',str(caught.exception))

    def test_public_ciphertext_hash_and_original_plain_release_hash_match_manifest(self):
        m=json.loads(d.MANIFEST.read_text());r=json.loads((d.ROOT/'data/knowledge/qwen_course_v4/release.json').read_text())
        self.assertEqual(hashlib.sha256((d.ROOT/m['file']).read_bytes()).hexdigest(),m['ciphertext_sha256'])
        self.assertEqual(m['archive_sha256'],r['archive_sha256']);self.assertFalse(m['master_key_published'])
