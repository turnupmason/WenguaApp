"""Actual Windows .NET AES round trip, with public software fixture only."""
from pathlib import Path
import os
import tempfile
import base64
import hashlib
import hmac
import json
import subprocess
from unittest.mock import patch
from src.wengua import course_delivery_v1 as d
from tests.test_course_delivery_v1 import fixture


def main():
    if os.name!='nt':raise RuntimeError('This check must run on real Windows')
    f,key,blob=fixture()
    with tempfile.TemporaryDirectory() as tmp:
        path=Path(tmp)/'Downloads'/'fixture.zip'
        d.install(blob,key,path,expected_sha256=f['plain_sha256'])
        assert path.read_bytes()==f['plaintext_utf8'].encode('utf8')
        d.install(blob,key,path,expected_sha256=f['plain_sha256'])
        bad=bytearray(blob);bad[-1]^=1
        try:d.install(bytes(bad),key,Path(tmp)/'bad.zip',expected_sha256=f['plain_sha256'])
        except ValueError:pass
        else:raise AssertionError('Tampered ciphertext accepted')
        assert not (Path(tmp)/'bad.zip').exists()
    # Exercise the full CLI with a public software fixture manifest.
    with tempfile.TemporaryDirectory() as tmp:
        root=Path(tmp);(root/'fixture.enc').write_bytes(blob)
        manifest=root/'manifest.json'
        manifest.write_text(json.dumps({'file':'fixture.enc','ciphertext_sha256':hashlib.sha256(blob).hexdigest(),
            'archive_name':'fixture.zip','archive_sha256':f['plain_sha256']}),encoding='utf8')
        with patch.object(d,'ROOT',root),patch.object(d,'MANIFEST',manifest):
            assert d.main(['--key',key.hex(),'--output',str(root/'restored.zip')])==0
        assert (root/'restored.zip').read_bytes()==f['plaintext_utf8'].encode('utf8')
    # A 4 MiB payload catches Windows stdin/JSON/base64 limits that tiny
    # vectors miss. It contains no real book text, course key or model data.
    plain=bytes(range(256))*16384
    enc,iv,_=d.authenticate(blob,key)
    payload=json.dumps({'key':base64.b64encode(enc).decode(),'iv':base64.b64encode(iv).decode(),
                        'cipher':base64.b64encode(plain).decode()})
    result=subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-Command',
        d.WINDOWS_DECRYPT.replace('CreateDecryptor','CreateEncryptor')],input=payload,
        capture_output=True,text=True,timeout=120,check=True)
    cipher=base64.b64decode(result.stdout.strip(),validate=True)
    body=d.MAGIC+iv+cipher
    mac=d.derive_keys(key)[1]
    envelope=body+hmac.new(mac,body,hashlib.sha256).digest()
    with tempfile.TemporaryDirectory() as tmp:
        output=Path(tmp)/'large.zip'
        d.install(envelope,key,output,expected_sha256=hashlib.sha256(plain).hexdigest())
        assert output.read_bytes()==plain
    print('REAL_WINDOWS_AES_AND_SHA_PASSED; full CLI and 4_MiB_software_fixture; original training runtime unchanged')

if __name__=='__main__':main()
