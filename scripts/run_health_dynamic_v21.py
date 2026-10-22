"""Generate full-length source-literature health text from a REAL nine-palace cast.

Input payload:
{"chart": <existing original-chart JSON>, "calendar": {...},
 "inquiry": {"relationship": "father", "consultation_context":"direct_proxy",
             "intent":"severity", "patient_birth_ganzhi": null}}

No cloud GPT and no medical prognosis.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.wengua.health_dynamic_v21 import analyze_health_v21


def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument("--input",required=True)
    p.add_argument("--output",required=True)
    p.add_argument("--database",help="read-only original two-book complete SQLite",default=None)
    a=p.parse_args(argv)
    source,dest=Path(a.input).resolve(),Path(a.output).resolve()
    if source==dest:
        p.error("Refuse to overwrite source input")
    payload=json.loads(source.read_text(encoding="utf-8"))
    report=analyze_health_v21(
        chart=payload["chart"],inquiry=payload["inquiry"],
        calendar=payload.get("calendar") or payload.get("calendar_inputs") or {},
        db_path=a.database)
    if dest.exists():
        p.error("Refuse to overwrite existing reading; retain all previous outputs")
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"intent":report["intent"],"sections":len(report["sections"]),
                      "output":str(dest),"status":report["status"]},ensure_ascii=False))


if __name__=="__main__":
    main()
