"""Add this one original Shenqi travel chapter without deleting prior SQLite chapters."""
import argparse,json
from pathlib import Path
from src.wengua.compile_shenqi_travel import import_travel_chapter
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--db",default="local/wengua.sqlite3")
 p.add_argument("--source-file",type=Path,required=True)
 a=p.parse_args()
 print(json.dumps(import_travel_chapter(a.db,a.source_file),ensure_ascii=False,indent=2))
if __name__=="__main__": main()
