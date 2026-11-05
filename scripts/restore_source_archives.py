"""Explicitly restore historical SQLite inputs, verifying compressed and raw SHA256."""
import argparse
import json
from src.wengua.archive_snapshots import CATALOG,source_database


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('names',nargs='*');parser.add_argument('--all',action='store_true')
    args=parser.parse_args()
    if not args.all and not args.names:parser.error('Supply exact archive names or --all')
    names=[e['name'] for e in json.loads(CATALOG.read_text(encoding='utf8'))['entries']] if args.all else args.names
    for name in names:print(source_database(name))

if __name__=='__main__':main()
