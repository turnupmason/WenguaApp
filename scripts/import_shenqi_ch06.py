"""Append user-supplied Chapter 6 to the existing private Wengua SQLite."""
import argparse
import json
from pathlib import Path
from src.wengua.compile_shenqi_ch06 import import_chapter6

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--db",default="local/wengua.sqlite3")
    p.add_argument("--source-file",type=Path,required=True,
                   help="Exact original UTF-8 Chapter 6 file, stored privately")
    args=p.parse_args()
    print(json.dumps(import_chapter6(args.db,args.source_file),ensure_ascii=False,indent=2))
if __name__=="__main__":
    main()
