"""Register the author's book-success verdicts for the six earlier health cases."""
import argparse,json
from src.wengua.book_verdict_sync import sync_health_book_outcomes
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--db",default="local/wengua.sqlite3")
    a=p.parse_args()
    print(json.dumps(sync_health_book_outcomes(a.db),ensure_ascii=False,indent=2))
if __name__=="__main__":main()
