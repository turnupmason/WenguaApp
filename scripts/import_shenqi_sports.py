"""CLI wrapper for source-preserving sports chapter 16 archive generation."""
import argparse
from pathlib import Path
from scripts.build_shenqi_16_from_15 import build

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--base',required=True,type=Path)
    p.add_argument('--source',required=True,type=Path)
    p.add_argument('--output',required=True,type=Path)
    p.add_argument('--index-dir',required=True,type=Path)
    args=p.parse_args()
    build(args.base,args.source,args.output,args.index_dir,Path(__file__).resolve().parents[1]/'schema/migrations/011_sports_source_qualification.sql')
if __name__=='__main__':main()
