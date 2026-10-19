import argparse
from src.wengua.database import initialize

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--db",default="local/wengua.sqlite3")
    a=p.parse_args()
    initialize(a.db)
    print("Initialized local database for two books; no original book text imported.")

if __name__=="__main__":
    main()
