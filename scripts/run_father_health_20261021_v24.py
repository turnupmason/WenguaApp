"""Real second user test: 戊辰日癸亥时, for father; offline-only group display."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

from src.wengua.astro_calendar import solar_chart_clock
from src.wengua.casting_shenqi import bureau_for_term, layout_from_explicit_bureau
from src.wengua.health_severity_v24 import analyze_health_severity_v24

ROOT=Path(__file__).resolve().parents[1]
DB=ROOT/"archives/sqlite/WenguaApp_双书194案例_父亲测病与病宫合并断词V2_3_完整研究库.sqlite3"
TIME="2026-10-21T21:30:00-04:00"
ZONE="America/New_York"
EXPECTED={"year":"丙午","month":"戊戌","day":"戊辰","hour":"癸亥"}


def run(*,db_path=DB, birth_ganzhi=None):
    calculated=solar_chart_clock(TIME,ZONE)
    if calculated["four_pillars"]!=EXPECTED:
        raise ValueError("Actual local 4-pillar calendar does not match user request")
    bureau=bureau_for_term(EXPECTED["day"],calculated["active_solar_term"])
    chart=layout_from_explicit_bureau(
        dun=bureau["dun"],ju=bureau["ju"],hour_ganzhi=EXPECTED["hour"])
    inquiry={
        "intent":"severity","relationship":"father",
        "consultation_context":"direct_proxy",
    }
    if birth_ganzhi:
        inquiry["patient_birth_ganzhi"]=birth_ganzhi
    cal={
        "year_ganzhi":EXPECTED["year"],"month_ganzhi":EXPECTED["month"],
        "day_ganzhi":EXPECTED["day"],"hour_ganzhi":EXPECTED["hour"],
        "month_branch":EXPECTED["month"][1]
    }
    result=analyze_health_severity_v24(
        chart=chart,inquiry=inquiry,calendar=cal,db_path=db_path)
    result["test_receipt"]={
        "four_pillars":EXPECTED,"input_time":TIME,"timezone":ZONE,
        "solar_term":calculated["active_solar_term"],"bureau":bureau,
        "chart":chart,"patient_relation":"father",
        "father_birth_year_not_provided":not bool(birth_ganzhi),
        "source_db_sha256":hashlib.sha256(Path(db_path).read_bytes()).hexdigest(),
        "clinically_verified":False,"other_intents_approved":False
    }
    return result


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--database",default=str(DB))
    parser.add_argument("--birth-ganzhi")
    parser.add_argument("--output")
    a=parser.parse_args()
    report=run(db_path=Path(a.database),birth_ganzhi=a.birth_ganzhi)
    if a.output:
        dest=Path(a.output)
        if dest.exists():
            parser.error("Original reports are immutable; choose another output")
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(report["reading_text"])
    print("INTERNAL_RECEIPT="+json.dumps({
        "source_db_sha256":report["test_receipt"]["source_db_sha256"],
        "sections":len(report["sections"]),"bureau":report["test_receipt"]["bureau"],
        "father_role":report["audit"]["role_binding"]["role_name"],
        "unknown_factors":len(report["audit"]["unknown_factor_ids"]),
        "render":"stdlib_python_only","user_accepted":False
    },ensure_ascii=False))


if __name__=="__main__":
    main()
