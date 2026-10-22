"""Offline only: user four-pillar severity preview via ACTUAL Wengua project code.

The displayed reading_text comes directly from the 21 template formats and
Python-calculated slots, no GPT/LLM rewrite, no network and no manual polishing.
All other health intents remain unreviewed.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from src.wengua.astro_calendar import solar_chart_clock
from src.wengua.casting_shenqi import bureau_for_term,layout_from_explicit_bureau
from src.wengua.health_severity_v22 import analyze_health_severity_v22

ROOT=Path(__file__).resolve().parents[1]
DEFAULT_DB=ROOT/"archives/sqlite/WenguaApp_双书194案例_疾病有向生克修正与历法校验V2_1_完整研究库.sqlite3"
# Verified traditional anchor is a local date/zone consistent with user's
# four pillars. This does not assert a unique timestamp from four pillars.
TIME="2026-10-21T19:30:00-04:00"
ZONE="America/New_York"
PILLARS={"year":"丙午","month":"戊戌","day":"戊辰","hour":"壬戌"}


def run(*,who="self",context="direct_self",db_path=DEFAULT_DB,birth_ganzhi=None):
    calendar=solar_chart_clock(TIME,ZONE)
    if calendar["four_pillars"]!=PILLARS:
        raise ValueError("Astronomical calendar four pillars differ from test input")
    method=bureau_for_term(PILLARS["day"],calendar["active_solar_term"])
    chart=layout_from_explicit_bureau(dun=method["dun"],ju=method["ju"],
                                      hour_ganzhi=PILLARS["hour"])
    inquiry={"intent":"severity","relationship":who,
             "consultation_context":context}
    if birth_ganzhi:
        inquiry["patient_birth_ganzhi"]=birth_ganzhi
    calendar_fields={
        "year_ganzhi":PILLARS["year"],"month_ganzhi":PILLARS["month"],
        "day_ganzhi":PILLARS["day"],"hour_ganzhi":PILLARS["hour"],
        "month_branch":PILLARS["month"][1]}
    result=analyze_health_severity_v22(chart=chart,inquiry=inquiry,
                                      calendar=calendar_fields,db_path=db_path)
    result["test_receipt"]={
        "civil_time":TIME,"timezone":ZONE,"original_pillars":PILLARS,
        "solar_term":calendar["active_solar_term"],"bureau":method,
        "chart":chart,"role_assumption_unconfirmed":True,
        "db_sha256":hashlib.sha256(Path(db_path).read_bytes()).hexdigest(),
        "user_other_four_intents_approved":False}
    return result


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--db",default=str(DEFAULT_DB))
    p.add_argument("--role",default="self")
    p.add_argument("--context",default="direct_self")
    p.add_argument("--birth-ganzhi",default=None)
    p.add_argument("--output",default=None,help="Write a NEW immutable JSON report")
    a=p.parse_args()
    r=run(who=a.role,context=a.context,db_path=Path(a.db),
          birth_ganzhi=a.birth_ganzhi)
    if a.output:
        dest=Path(a.output)
        if dest.exists():raise ValueError("Refuse to overwrite previous reading report")
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_text(json.dumps(r,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(r["reading_text"])
    print("INTERNAL_RECEIPT="+json.dumps({
        "sections":len(r["sections"]),"mode":r["audit"]["render_mode"],
        "unknown_factors":len(r["audit"]["unknown_factor_ids"]),
        "source_pair":r["audit"]["stem_pair_source"]["id"],
        "door_press_palaces":r["audit"]["actual_door_press_palaces"],
        "accepted_by_user":False
    },ensure_ascii=False))


if __name__=="__main__":
    main()
