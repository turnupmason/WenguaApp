"""Import one source-complete pregnancy chapter and retrofit old health book verdicts."""
import argparse,json
from pathlib import Path
from src.wengua.compile_shenqi_pregnancy import import_pregnancy_chapter
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--db",default="local/wengua.sqlite3")
    p.add_argument("--source-file",required=True,type=Path)
    a=p.parse_args()
    print(json.dumps(import_pregnancy_chapter(a.db,a.source_file),ensure_ascii=False,indent=2))
if __name__=="__main__":main()
