"""Two source-case deterministic V3.1 previews, after V3.0 hour/person role fix."""
from __future__ import annotations
import json,hashlib
from pathlib import Path
from scripts.run_two_historical_health_v27 import evaluate as base_evaluate
from src.wengua.health_severity_v31 import analyze_health_severity_v31
ROOT=Path(__file__).resolve().parents[1]
LATEST_DB=ROOT/"archives/sqlite/WenguaApp_双书194案例_疾病古籍补充规则V3_0_完整研究库.sqlite3"
V30_SEAL=ROOT/"data/evaluation/health_v30/two_historical_supplement_V30_SEALED.json"

def evaluate(*,db_path=LATEST_DB):
    prior={x["case_id"]:x for x in json.loads(V30_SEAL.read_text("utf8"))["samples"]}
    sources=base_evaluate()
    result=[]
    for x in sources["predictions"]:
        question={"intent":"severity","relationship":"older_relative" if x["patient_sex"] else "self",
             "consultation_context":"direct_proxy" if x["patient_sex"] else "direct_self"}
        if x["patient_sex"]:question.update(patient_sex=x["patient_sex"],relative_specific="aunt")
        cal={"year_ganzhi":x["year_ganzhi"],"month_ganzhi":x["month_ganzhi"],
             "day_ganzhi":x["day_ganzhi"],"hour_ganzhi":x["hour_ganzhi"],
             "month_branch":x["month_ganzhi"][1]}
        revised=analyze_health_severity_v31(chart=x["full_chart"],inquiry=question,calendar=cal,db_path=db_path)
        content=revised["reading_text"]
        item={"case_id":x["case_id"],
           "readout":content,"sections":revised["sections"],
           "sha256":hashlib.sha256(content.encode("utf8")).hexdigest(),
           "v30_original_sha256":prior[x["case_id"]]["sha256"],
           "v27_original_sha256":x["readout_sha256"],
           "hour_patient_evidence":revised["audit"]["v31_patient_hour_direction"],
           "traditional_verdict":revised["audit"]["traditional_verdict"]["verdict"],
           "book_author_feedback_not_used":True,
           "user_review":"pending"}
        if len(content)==0:raise ValueError("Empty revised reading")
        result.append(item)
    return {"schema":"wengua_v31_user_20261022_corrected_hour_patient_relationship",
            "prior_v27_v28_v29_v30_seals_preserved":True,
            "original_book_author_answers_not_used":True,
            "samples":result}

if __name__=="__main__":
    x=evaluate()
    for r in x["samples"]:
        print("V31_BEGIN "+r["case_id"])
        print(r["readout"])
        print("SHA256="+r["sha256"])
        print("V31_END "+r["case_id"])
