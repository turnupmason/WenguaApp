"""Safely import the complete Shenqi education/exam chapter into private SQLite."""
import argparse,json
from pathlib import Path
from src.wengua.compile_shenqi_education import import_education_chapter
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--db",default="local/wengua.sqlite3")
    p.add_argument("--source-file",type=Path,required=True,help="Original UTF-8 text; kept private")
    a=p.parse_args()
    print(json.dumps(import_education_chapter(a.db,a.source_file),ensure_ascii=False,indent=2))
if __name__=="__main__":main()
