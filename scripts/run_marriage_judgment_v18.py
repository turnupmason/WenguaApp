"""Run WenguaApp marriage traditional book-method research WITHOUT a birth year.

  python -m scripts.run_marriage_judgment_v18 --input inquiry.json \
    --database archives/sqlite/WenguaApp_..._V1_8_完整研究库.sqlite3 \
    --output studied_result.json

Accepts optional inquiry.subject/partner.year_ganzhi; when omitted the
original-book 乙庚, 六合 and 日干/时干 event methods remain usable.
No claimed independent verification of real-world marriage success, health,
third-party wrongdoing, or exact future events. The output is a sourced
research-stage interpretation with a reproducible audit.
"""
from __future__ import annotations
import argparse,json,sqlite3,sys
from pathlib import Path
from src.wengua.marriage_no_year_v18 import analyze_marriage_v18

def main(argv=None):
 p=argparse.ArgumentParser(description="Original-source marriage methods with optional birth years")
 p.add_argument("--input",required=True,help="Full verified chart JSON and actual marriage scene question")
 p.add_argument("--database",required=True,help="Latest complete two-book 194-case V1.8 SQLite")
 p.add_argument("--output",help="Write independent JSON result; default prints stdout")
 p.add_argument("--exclude-event-family",help="Research holdout only: exclude an entire historical family")
 a=p.parse_args(argv)
 source=Path(a.input);db=Path(a.database)
 if not source.is_file() or not db.is_file():
  p.error("Both original chart-question JSON and complete SQLite must exist")
 if a.output and Path(a.output).resolve() in (source.resolve(),db.resolve()):
  p.error("Cannot overwrite original source JSON or historical SQLite")
 try:
  incoming=json.loads(source.read_text(encoding="utf8"))
  result=analyze_marriage_v18(db_path=db,payload=incoming,
                             held_out_family_id=a.exclude_event_family)
 except (ValueError,TypeError,KeyError,RuntimeError,sqlite3.Error) as exc:
  p.error("Cannot validate source chart/roles or original methods: "+str(exc))
 output=json.dumps(result,ensure_ascii=False,indent=2)+"\n"
 if a.output:
  target=Path(a.output)
  target.parent.mkdir(parents=True,exist_ok=True)
  target.write_text(output,encoding="utf8")
 else:
  sys.stdout.write(output)
 return result

if __name__=="__main__":main()
