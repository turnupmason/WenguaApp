"""Import source-derived first-chapter metadata into local Wengua SQLite."""
import argparse,json
from src.wengua.chapter_ingest import register_chapter_knowledge

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--db",default="local/wengua.sqlite3")
    p.add_argument("--source-file",help="Optional exact private source txt file; never Git uploaded")
    a=p.parse_args()
    print(json.dumps(register_chapter_knowledge(a.db,source_file=a.source_file),ensure_ascii=False))

if __name__=="__main__":
    main()
