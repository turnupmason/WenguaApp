"""Restore the private WenguaApp RAG sources using the existing delivery key."""
import argparse,hashlib,json,os,re
from pathlib import Path
from src.wengua import course_delivery_v1 as delivery

MANIFEST=delivery.ROOT/'data/delivery/book_rag_v1/manifest.json'

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--key');p.add_argument('--key-file',type=Path);p.add_argument('--output',type=Path)
    a=p.parse_args(argv)
    if a.key and a.key_file:p.error('Choose --key or --key-file')
    if os.name!='nt':raise RuntimeError('This decryptor uses Windows .NET. The restored library/index can be copied to Mac for CPU retrieval.')
    value=a.key or (a.key_file.read_text(encoding='utf-8-sig') if a.key_file else input('粘贴之前的教材口令（此处输入可见，回车确认）：'))
    value=value.strip()
    if not re.fullmatch(r'[0-9a-fA-F]{64}',value):raise ValueError('Expected the same 64-character delivery key used for V4/V5.1')
    manifest=json.loads(MANIFEST.read_text(encoding='utf8'));blob=(delivery.ROOT/manifest['file']).read_bytes()
    if hashlib.sha256(blob).hexdigest()!=manifest['ciphertext_sha256']:raise ValueError('Encrypted RAG package changed')
    path=delivery.install(blob,bytes.fromhex(value),a.output or Path.home()/'Downloads'/manifest['archive_name'],expected_sha256=manifest['archive_sha256'])
    print('RAG source package restored and SHA256 verified: '+str(path))
    print('CPU build/search does not load GPU or change the running V5.1 training.')
    print('Next: local\\qwen_env\\Scripts\\python.exe -X utf8 run_wengua_rag.py build')
    return 0

if __name__=='__main__':raise SystemExit(main())
