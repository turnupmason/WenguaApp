"""Append Shenqi health source and six full author cases to existing private SQLite."""
import argparse
import json
from pathlib import Path
from src.wengua.compile_shenqi_health_cases import import_health_chapter

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--db",default="local/wengua.sqlite3")
    p.add_argument("--source-file",type=Path,required=True,
                   help="Exact original health chapter TXT (not tracked by Git)")
    a=p.parse_args()
    print(json.dumps(import_health_chapter(a.db,a.source_file),ensure_ascii=False,indent=2))
if __name__=="__main__":
    main()
