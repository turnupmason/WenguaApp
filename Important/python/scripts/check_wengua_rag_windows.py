"""Actual Windows FTS, existing casting and stdlib authenticated decryption."""
from pathlib import Path
import hashlib,json,os,tempfile
from unittest.mock import patch
from src.wengua import book_rag as r,course_delivery_v1 as d
from tests.test_book_rag import fixture as source_fixture
from tests.test_course_delivery_v1 import fixture as cipher_fixture
import unlock_wengua_rag as unlock


def main():
    if os.name!='nt':raise RuntimeError('Actual Windows required')
    (r.ROOT/'local').mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(dir=r.ROOT/'local') as tmp:
        root=Path(tmp);path=root/'index.sqlite3';r.build_index([source_fixture()],path)
        with r.Index(path) as index:
            assert index.search('软件规则条件')['documents']
            assert all(d['kind']=='rule' for d in index.search('后来结果')['documents'])
        f,key,blob=cipher_fixture();(root/'software.enc').write_bytes(blob)
        manifest=root/'manifest.json';manifest.write_text(json.dumps({'file':'software.enc','ciphertext_sha256':hashlib.sha256(blob).hexdigest(),'archive_name':'software.zip','archive_sha256':f['plain_sha256']}),encoding='utf8')
        with patch.object(d,'ROOT',root),patch.object(unlock,'MANIFEST',manifest):
            unlock.main(['--key',key.hex(),'--output',str(root/'restored.zip')])
        assert (root/'restored.zip').read_bytes()==f['plaintext_utf8'].encode('utf8')
    print('WENGUA_RAG_REAL_WINDOWS_FTS_AND_NATIVE_DECRYPT_PASSED; software fixtures only; no books/key/GPU used')

if __name__=='__main__':main()
