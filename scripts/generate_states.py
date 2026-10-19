import argparse
import json
from pathlib import Path
from src.wengua.core import state_index

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output",default="local/state-index.json")
    a=p.parse_args()
    output=Path(a.output)
    if output.exists():raise FileExistsError("No overwriting old indexes")
    output.parent.mkdir(parents=True,exist_ok=True)
    entries=state_index()
    assert len(entries)==1080 and len({x["state_id"] for x in entries})==1080
    output.write_text(json.dumps(entries,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("Created 1080 UNVERIFIED state index records, not calculated charts.")

if __name__=="__main__":
    main()
