"""Import Shenqi employment source as intact cases into a private append-only SQLite DB."""
import argparse,json
from pathlib import Path
from src.wengua.compile_shenqi_employment import import_employment_chapter
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--db",default="local/wengua.sqlite3")
    parser.add_argument("--source-file",type=Path,required=True)
    args=parser.parse_args()
    print(json.dumps(import_employment_chapter(args.db,args.source_file),ensure_ascii=False,indent=2))
if __name__=="__main__":
    main()
