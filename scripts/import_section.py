import argparse
import json
from pathlib import Path
from src.wengua.database import import_section

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--db",default="local/wengua.sqlite3")
    p.add_argument("--book",required=True,choices=("shenqi","kaiwu"))
    p.add_argument("--key",required=True)
    p.add_argument("--title",required=True)
    p.add_argument("--file",type=Path,required=True)
    a=p.parse_args()
    if not a.file.is_file():p.error("No such local chapter file")
    print(json.dumps(import_section(a.db,a.book,a.key,a.title,
                                    a.file.read_text(encoding="utf-8")),ensure_ascii=False))

if __name__=="__main__":
    main()
