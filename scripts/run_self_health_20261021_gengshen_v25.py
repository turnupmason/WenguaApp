"""Third independent user four-pillar fixture: 戊辰日庚申时, direct self.

No remote inference; strict local calendar -> chart -> source DB -> Python
phrases only. Correct "更申" as "庚申" after 五鼠遁 check.
"""
from __future__ import annotations
import argparse,json,hashlib
from pathlib import Path
from src.wengua.astro_calendar import solar_chart_clock
from src.wengua.casting_shenqi import bureau_for_term,layout_from_explicit_bureau
from src.wengua.health_severity_v25 import analyze_health_severity_v25

ROOT=Path(__file__).resolve().parents[1]
PARENT_DB=ROOT/"archives/sqlite/WenguaApp_双书194案例_父亲测病断词复核修正V2_4_完整研究库.sqlite3"
STAMP="2026-10-21T15:30:00-04:00"
ZONE="America/New_York"
PILLARS={"year":"丙午","month":"戊戌","day":"戊辰","hour":"庚申"}

def run(*,db_path=PARENT_DB,illness_duration=None):
    calculated=solar_chart_clock(STAMP,ZONE)
    if calculated["four_pillars"]!=PILLARS:
        raise ValueError("Actual calendar does not match 庚申 time and 戊辰 day")
    bureau=bureau_for_term(PILLARS["day"],calculated["active_solar_term"])
    chart=layout_from_explicit_bureau(dun=bureau["dun"],ju=bureau["ju"],hour_ganzhi=PILLARS["hour"])
    calendar={"year_ganzhi":PILLARS["year"],"month_ganzhi":PILLARS["month"],
              "day_ganzhi":PILLARS["day"],"hour_ganzhi":PILLARS["hour"],
              "month_branch":PILLARS["month"][1]}
    inquiry={"intent":"severity","relationship":"self","consultation_context":"direct_self"}
    if illness_duration:
        inquiry["illness_duration"]=illness_duration
    result=analyze_health_severity_v25(chart=chart,inquiry=inquiry,calendar=calendar,db_path=db_path)
    result["test_receipt"]={
        "time":STAMP,"zone":ZONE,"four_pillars":PILLARS,
        "solar_term":calculated["active_solar_term"],
        "bureau":bureau,"chart":chart,
        "sqlite_sha256":hashlib.sha256(Path(db_path).read_bytes()).hexdigest(),
        "patient_is_self":True,"other_four_intents_approved":False,
        "not_medical_diagnosis":True,
    }
    return result

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--database",default=str(PARENT_DB))
    ap.add_argument("--illness-duration",choices=("new","chronic"))
    ap.add_argument("--output")
    a=ap.parse_args()
    report=run(db_path=Path(a.database),illness_duration=a.illness_duration)
    if a.output:
        f=Path(a.output)
        if f.exists():raise ValueError("Refuse overwrite of earlier test")
        f.parent.mkdir(parents=True,exist_ok=True)
        f.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n","utf8")
    print(report["reading_text"])
    print("AUDIT="+json.dumps({
        "fuyin_fanyin":report["audit"]["fuyin_fanyin"],
        "verdict":report["audit"]["binary_traditional_conclusion"]["verdict"],
        "visible_sections":report["audit"]["visible_sections"],
        "runtime_llm_calls":0,
    },ensure_ascii=False))

if __name__=="__main__":main()
