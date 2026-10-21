"""Read a real supplied marriage chart JSON and audit its book-source facts.

This interface cannot publish a definite marital prediction while calendar,
remaining traditional relation rules and source-backed outcome weighting are
unverified. It intentionally returns full structured JSON research evidence.
Usage:
  python -m scripts.run_marriage_json_study --input /path/chart_question.json \
      --database /path/full_194_book_marriage_V1_4.sqlite3 \
      --output /path/audited_study.json
"""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
from src.wengua.marriage_runtime import inspect_marriage_chart_json

def main(argv=None):
 p=argparse.ArgumentParser(description="Source-grounded JSON-to-marriage evidence study, no invented forecast")
 p.add_argument("--input",required=True,help="Complete source-cast JSON + explicit marriage scene inquiry")
 p.add_argument("--database",required=True,help="Full immutable WenguaApp source case/22-scene SQLite")
 p.add_argument("--output",help="JSON audit output; prints to stdout if omitted")
 a=p.parse_args(argv)
 incoming=Path(a.input)
 db=Path(a.database)
 if not incoming.is_file():p.error("Input JSON file does not exist")
 if not db.is_file():p.error("Full source SQLite file does not exist")
 try:
  payload=json.loads(incoming.read_text(encoding="utf8"))
  result=inspect_marriage_chart_json(db_path=db,payload=payload)
 except (ValueError,TypeError,KeyError,json.JSONDecodeError) as err:
  p.error("Input is not a trustworthy complete source-tested chart: "+str(err))
 serial=json.dumps(result,ensure_ascii=False,indent=2)+"\n"
 if a.output:
  dest=Path(a.output)
  if dest.resolve()==incoming.resolve() or dest.resolve()==db.resolve():
   p.error("Refuse to overwrite input source JSON or immutable book SQLite")
  dest.parent.mkdir(parents=True,exist_ok=True)
  dest.write_text(serial,encoding="utf8")
 else:sys.stdout.write(serial)
 return result
if __name__=="__main__":main()
