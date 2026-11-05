"""Restore the v5 private course using the same privately delivered v4 key."""
import argparse
import getpass
import hashlib
import json
import os
from pathlib import Path
import re
from src.wengua import course_delivery_v1 as delivery
MANIFEST=delivery.ROOT/'data/delivery/course_v5/manifest.json'


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--key');parser.add_argument('--output',type=Path)
    args=parser.parse_args(argv)
    manifest=json.loads(MANIFEST.read_text(encoding='utf8'))
    blob=(delivery.ROOT/manifest['file']).read_bytes()
    if hashlib.sha256(blob).hexdigest()!=manifest['ciphertext_sha256']:raise ValueError('Encrypted delivery changed')
    if os.name!='nt':raise RuntimeError('Run this entry on the Windows training computer')
    value=args.key or getpass.getpass('Paste the private v4 delivery key: ')
    if not re.fullmatch(r'[0-9a-fA-F]{64}',value):raise ValueError('Expected the private 64-character hex key')
    path=delivery.install(blob,bytes.fromhex(value),args.output or Path.home()/'Downloads'/manifest['archive_name'],expected_sha256=manifest['archive_sha256'])
    print('V5 course restored and SHA256 verified: '+str(path))
    print('After the running V4 finishes, in PowerShell: .\\train_wengua_v5.cmd')
    return 0

if __name__=='__main__':raise SystemExit(main())
