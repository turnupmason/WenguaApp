"""Run with the actual local original chapter and the existing private user SQLite."""
import argparse,json
from src.wengua.compile_shenqi_lost_property import import_lost_property
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--db",required=True)
    p.add_argument("--source",required=True)
    a=p.parse_args()
    print(json.dumps(import_lost_property(a.db,a.source),ensure_ascii=False,indent=2))
if __name__=="__main__":main()
