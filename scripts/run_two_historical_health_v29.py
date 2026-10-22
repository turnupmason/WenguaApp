"""V29 updated two historical samples, preserving BOTH original v27 and v28 seals."""
from __future__ import annotations
import json,hashlib
from pathlib import Path
from scripts.run_two_historical_health_v27 import evaluate as old_evaluate
from scripts.run_two_historical_health_v28 import evaluate as v28_evaluate
from src.wengua.health_severity_v29 import analyze_health_severity_v29
ROOT=Path(__file__).resolve().parents[1]
LATEST_DB=ROOT/"archives/sqlite/WenguaApp_双书194案例_及时医治入墓击刑V2_8_完整研究库.sqlite3"
def evaluate(db_path=LATEST_DB):
    old=old_evaluate()
    prior=v28_evaluate()
    outputs=[]
    for original,v28 in zip(old["predictions"],prior["new_predictions"]):
        assert original["case_id"]==v28["case_id"]
        sex=original["patient_sex"]
        question={"intent":"severity",
          "relationship":"older_relative" if sex else "self",
          "consultation_context":"direct_proxy" if sex else "direct_self"}
        if sex:question.update(patient_sex=sex,relative_specific="aunt")
        cal={"year_ganzhi":original["year_ganzhi"],"month_ganzhi":original["month_ganzhi"],
             "day_ganzhi":original["day_ganzhi"],"hour_ganzhi":original["hour_ganzhi"],
             "month_branch":original["month_ganzhi"][1]}
        final=analyze_health_severity_v29(chart=original["full_chart"],
           inquiry=question,calendar=cal,db_path=db_path)
        txt=final["reading_text"]
        outputs.append({"case_id":original["case_id"],"sections":final["sections"],
           "readout":txt,"sha256":hashlib.sha256(txt.encode()).hexdigest(),
           "original_v27_sha":original["readout_sha256"],
           "unchanged_v28_sha":v28["new_readout_sha256"],
           "verdict":final["audit"]["traditional_verdict"]["verdict"],
           "medical_timing":final["audit"]["medical_timing_v28"],
           "other_original_book_outcome_used":False,
           "content_review":"pending",
           "not_a_real_medical_prognosis":True})
    return {"schema":"V29_two_existing_historical_cases_refined_static_health",
            "original_v27_and_v28_readings_preserved":True,
            "original_book_answers_not_used":True,"samples":outputs}
