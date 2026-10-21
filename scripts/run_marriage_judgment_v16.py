"""Executable V1.6 JSON -> independent original-book marriage outcome & timing.

No author verdict labels or book later feedback enter the inference function.
New real-person forecasting remains a traditional *research* judgment, not an
empirically validated prediction. The returned publication_ready remains false
until the global 24-factor+six-layer gate is fully satisfied.

python -m scripts.run_marriage_judgment_v16 --input in.json \
  --database <latest_complete_sqlite> --output judgment.json
"""
from __future__ import annotations
import argparse,json,sys,sqlite3
from pathlib import Path
from src.wengua.marriage_judgment_v16 import analyze_marriage_unseen_chart
def main(argv=None):
 p=argparse.ArgumentParser(description="Source-bound marriage initial judgment and real conditional timing")
 p.add_argument("--input",required=True,help="Existing nine-palace chart + real question, actors and civil clock")
 p.add_argument("--database",required=True,help="Full original two-book 194-case V1.6 SQLite database")
 p.add_argument("--output",help="Separate JSON containing complete initial evidence and applicable timing")
 p.add_argument("--exclude-event-family",help="Research only: completely exclude family from original method witnesses")
 a=p.parse_args(argv)
 source=Path(a.input);db=Path(a.database)
 if not source.is_file() or not db.is_file():
  p.error("Input chart JSON and complete two-book SQLite must exist")
 if a.output and Path(a.output).resolve() in (source.resolve(),db.resolve()):
  p.error("Never overwrite input book source or historical full SQLite archive")
 try:
  incoming=json.loads(source.read_text(encoding="utf8"))
  output=analyze_marriage_unseen_chart(
   db_path=db,payload=incoming,held_out_family_id=a.exclude_event_family)
 except (ValueError,TypeError,KeyError,RuntimeError,sqlite3.Error) as error:
  p.error("Cannot responsibly form source-book answer: "+str(error))
 result=json.dumps(output,ensure_ascii=False,indent=2)+"\n"
 if a.output:
  dest=Path(a.output)
  dest.parent.mkdir(parents=True,exist_ok=True)
  dest.write_text(result,encoding="utf8")
 else:sys.stdout.write(result)
 return output
if __name__=="__main__":
 main()
