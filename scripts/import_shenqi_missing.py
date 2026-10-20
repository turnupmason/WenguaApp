"""Import a source-exact chapter into an existing PRIVATE SQLite without replacing older chapters."""
import argparse,json
from pathlib import Path
from src.wengua.compile_shenqi_missing import import_missing_chapter
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--db",default="local/wengua.sqlite3")
 p.add_argument("--source-file",type=Path,required=True)
 a=p.parse_args()
 print(json.dumps(import_missing_chapter(a.db,a.source_file),ensure_ascii=False,indent=2))
if __name__=="__main__":main()
