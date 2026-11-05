"""Real Windows stdlib CLI and 12 MiB software-only authenticated delivery."""
from pathlib import Path
import base64
import hashlib
import hmac
import json
import os
import subprocess
import tempfile
from unittest.mock import patch
from src.wengua import course_delivery_v1 as d
from tests.test_course_delivery_v1 import fixture
import unlock_course_v51 as cli


def main():
    if os.name!='nt':raise RuntimeError('Actual Windows required')
    f,key,blob=fixture()
    with tempfile.TemporaryDirectory() as t:
        root=Path(t);(root/'fixture.enc').write_bytes(blob);manifest=root/'manifest.json'
        manifest.write_text(json.dumps({'file':'fixture.enc','ciphertext_sha256':hashlib.sha256(blob).hexdigest(),
            'archive_name':'fixture.zip','archive_sha256':f['plain_sha256']}),encoding='utf8')
        with patch.object(d,'ROOT',root),patch.object(cli,'MANIFEST',manifest):
            cli.main(['--key',key.hex(),'--output',str(root/'restored.zip')])
        assert (root/'restored.zip').read_bytes()==f['plaintext_utf8'].encode('utf8')
    plain=bytes(range(256))*49152
    enc,iv,_=d.authenticate(blob,key)
    payload=json.dumps({k:base64.b64encode(v).decode() for k,v in [('key',enc),('iv',iv),('cipher',plain)]})
    encrypted=subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-Command',
        d.WINDOWS_DECRYPT.replace('CreateDecryptor','CreateEncryptor')],input=payload,
        capture_output=True,text=True,timeout=120,check=True)
    body=d.MAGIC+iv+base64.b64decode(encrypted.stdout.strip(),validate=True)
    envelope=body+hmac.new(d.derive_keys(key)[1],body,hashlib.sha256).digest()
    with tempfile.TemporaryDirectory() as t:
        dest=Path(t)/'software.zip'
        d.install(envelope,key,dest,expected_sha256=hashlib.sha256(plain).hexdigest())
        assert dest.read_bytes()==plain
    print('V5.1_REAL_WINDOWS_CLI_AND_12_MIB_AES_PASSED; no private key, books, model or CUDA used')

if __name__=='__main__':main()
