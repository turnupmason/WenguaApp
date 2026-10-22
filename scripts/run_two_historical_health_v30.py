"""Two original Wengua historic cases, re-rendered by V3.0 fixed curriculum.

No original outcome is supplied to the evaluator. Previous v27/v28/v29
readout SHAs preserved; no chart answered after viewing the ending.
"""
from __future__ import annotations
import hashlib,json
from pathlib import Path
from scripts.run_two_historical_health_v27 import evaluate as base_evaluate
from src.wengua.health_severity_v30 import analyze_health_severity_v30
ROOT=Path(__file__).resolve().parents[1]
LATEST_DB=ROOT/"archives/sqlite/WenguaApp_双书194案例_精简医药旺衰应期V2_9_完整研究库.sqlite3"

def evaluate(*,db_path=LATEST_DB):
    old=base_evaluate()
    outputs=[]
    for item in old["predictions"]:
        question={"intent":"severity","relationship":"older_relative" if item["patient_sex"] else "self",
                  "consultation_context":"direct_proxy" if item["patient_sex"] else "direct_self"}
        if item["patient_sex"]:
            question.update(patient_sex=item["patient_sex"],relative_specific="aunt")
        cal={"year_ganzhi":item["year_ganzhi"],"month_ganzhi":item["month_ganzhi"],
             "day_ganzhi":item["day_ganzhi"],"hour_ganzhi":item["hour_ganzhi"],
             "month_branch":item["month_ganzhi"][1]}
        r=analyze_health_severity_v30(chart=item["full_chart"],
             inquiry=question,calendar=cal,db_path=db_path)
        txt=r["reading_text"]
        outputs.append({
             "case_id":item["case_id"],"source_four_pillars":cal,
             "sections":r["sections"],"readout":txt,
             "sha256":hashlib.sha256(txt.encode("utf8")).hexdigest(),
             "previous_v27_sha":item["readout_sha256"],
             "provisional_traditional_verdict":r["audit"]["traditional_verdict"]["verdict"],
             "v30_method_audit":r["audit"]["v30_rules"],
             "source_book_answer_used":False,"not_actual_medical_prediction":True,
             "user_review":"pending"})
    return {"schema":"wengua_v30_user_20261022_disease_curriculum_2_historical_probes",
        "prior_v27_v28_v29_seals_untouched":True,
        "prior_second_v27_review_only":"user_confirmed_not_automatically_transferred",
        "source_author_endings_used":False,
        "samples":outputs}

if __name__=="__main__":
    report=evaluate()
    for r in report["samples"]:
        print("HEALTH_V30_BEGIN "+r["case_id"])
        print(r["readout"])
        print("SHA256="+r["sha256"])
        print("HEALTH_V30_END "+r["case_id"])
