"""Restore selected archived CI reports into ignored local/ with exact SHA256."""
import argparse
import hashlib
import json
from pathlib import Path
import tarfile
from src.wengua.qwen_book_loop_v3 import ROOT,private_output


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('paths',nargs='*');parser.add_argument('--all',action='store_true')
    parser.add_argument('--output',type=Path,default=Path('local/restored_ci_history'))
    args=parser.parse_args();out=private_output(args.output)
    manifest=json.loads((ROOT/'docs/history/ci_reports_manifest.json').read_text(encoding='utf8'))
    archive=ROOT/manifest['archive']
    if hashlib.sha256(archive.read_bytes()).hexdigest()!=manifest['archive_sha256']:raise ValueError('History archive changed')
    entries={x['path']:x for x in manifest['members']}
    names=list(entries) if args.all else args.paths
    if not names:parser.error('Supply exact docs/... report names or --all')
    if any(n not in entries for n in names):raise ValueError('Unknown historical report')
    with tarfile.open(archive,'r:xz') as tar:
        for name in names:
            p=Path(name)
            if p.is_absolute() or '..' in p.parts:raise ValueError('Unsafe history name')
            raw=tar.extractfile(name).read();expected=entries[name]
            if len(raw)!=expected['bytes'] or hashlib.sha256(raw).hexdigest()!=expected['sha256']:raise ValueError('Historical member changed')
            dest=out/name;dest.parent.mkdir(parents=True,exist_ok=True)
            if dest.exists():
                if dest.read_bytes()!=raw:raise ValueError('Changed existing report preserved: '+str(dest))
            else:
                with dest.open('xb') as f:f.write(raw)
            print(dest)

if __name__=='__main__':main()
