"""Add NONAPPROVED mechanical reference candidates for EVERY stored original author step."""
import argparse,json
from src.wengua.database import initialize,connect
from src.wengua.case_reasoning_trace import backfill_existing_case_traces
def main():
    p=argparse.ArgumentParser();p.add_argument("--db",required=True);a=p.parse_args()
    initialize(a.db)
    with connect(a.db) as c:result=backfill_existing_case_traces(c)
    print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
