"""Compile private, user-supplied Shenqi fourth & fifth chapter knowledge."""
import argparse
import json
from pathlib import Path

from src.wengua.compile_shenqi_ch45 import ingest_local

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--db",default="local/wengua.sqlite3",
                   help="Local SQLite only; do not commit this database to public GitHub")
    p.add_argument("--source-file",type=Path,required=True,
                   help="Exact original combined chapter 4/5 UTF-8 text file")
    a=p.parse_args()
    print(json.dumps(ingest_local(a.db,a.source_file),ensure_ascii=False,indent=2))
if __name__=="__main__":
    main()
