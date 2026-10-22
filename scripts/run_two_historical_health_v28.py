"""V2.8: the user's actual two sealed historical health cases, no answer leakage."""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from scripts.run_two_historical_health_v27 import evaluate as earlier, PARENT_DB as V27_PARENT, draw
from src.wengua.health_severity_v28 import analyze_health_severity_v28
ROOT=Path(__file__).resolve().parents[1]
V27_FULL_DB=ROOT/"archives/sqlite/WenguaApp_双书194案例_疾病五不遇时乾坤与两例封存V2_7_完整研究库.sqlite3"
def evaluate(db_path=V27_FULL_DB):
    old=earlier(db_path=V27_PARENT)
    if tuple(old["selected_ids"])!=draw()[0]:
        raise ValueError("Sealed historical selection must never be changed")
    result=[]
    for p in old["predictions"]:
        calendar={"year_ganzhi":p["year_ganzhi"],"month_ganzhi":p["month_ganzhi"],
                  "day_ganzhi":p["day_ganzhi"],"hour_ganzhi":p["hour_ganzhi"],
                  "month_branch":p["month_ganzhi"][1]}
        relation="self" if p["patient_sex"] is None else "older_relative"
        inquiry={"intent":"severity","relationship":relation,
                 "consultation_context":"direct_self" if relation=="self" else "direct_proxy"}
        if p["patient_sex"]:
            inquiry.update(patient_sex=p["patient_sex"],relative_specific="aunt")
        current=analyze_health_severity_v28(chart=p["full_chart"],
            inquiry=inquiry,calendar=calendar,db_path=db_path)
        fulltext=current["reading_text"]
        result.append({"case_id":p["case_id"],"day":p["day_ganzhi"],"hour":p["hour_ganzhi"],
            "new_readout":fulltext,"new_readout_sha256":hashlib.sha256(fulltext.encode()).hexdigest(),
            "old_sealed_readout_sha256":p["readout_sha256"],"sections":current["sections"],
            "old_traditional_verdict":p["traditional_verdict"],
            "new_traditional_verdict":current["audit"]["traditional_verdict"]["verdict"],
            "medical_timing":current["audit"]["medical_timing_v28"],
            "tomb_punishment":current["audit"]["actual_tomb_punishment_v28"],
            "book_case_outcome_read":False,"user_review_status":"pending",
            "not_medical_diagnosis":True})
    return {"schema":"V28_followup_of_2_frozen_historical_readings",
            "prior_sealed_event_ids":old["selected_ids"],"new_predictions":result,
            "prior_original_predictions_overwritten":False,
            "book_case_answers_used":False}
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--output",required=True)
    args=p.parse_args()
    result=evaluate()
    out=Path(args.output)
    if out.exists():raise ValueError("Immutable trials cannot be overwritten")
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    for n,r in enumerate(result["new_predictions"],1):
        print(f"HEALTH_V28_CASE_{n}_BEGIN")
        print(r["new_readout"])
        print(f"HEALTH_V28_CASE_{n}_SHA="+r["new_readout_sha256"])
        print(f"HEALTH_V28_CASE_{n}_END")
