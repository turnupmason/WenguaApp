"""Import Shenqi business chapter into an existing private SQLite without replacing prior chapters."""
import argparse
import json
from pathlib import Path
from src.wengua.compile_shenqi_business import import_business_chapter

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--db",default="local/wengua.sqlite3")
    p.add_argument("--source-file",required=True,type=Path,help="717-line source file, private and not tracked in Git")
    options=p.parse_args()
    print(json.dumps(import_business_chapter(options.db,options.source_file),ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
