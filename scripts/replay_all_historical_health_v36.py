"""V3.6 corrected V3.4 twelve-source-event re-evaluation: source conditions only.

This never edits old V3.1 or V3.4 sealed files. Real question date/hour,
book bureau, first-question known person/sex and actual hidden six-instrument
facts; no original author conclusion or later feedback is used.
"""
from __future__ import annotations
import hashlib,json
from pathlib import Path
from scripts.replay_all_historical_health_v31_v33 import CASES
from src.wengua.astro_calendar import solar_chart_clock
from src.wengua.casting_shenqi import layout_from_explicit_bureau
from src.wengua.health_severity_v36 import analyze_health_severity_v36

ROOT=Path(__file__).resolve().parents[1]
PARENT=ROOT/"archives/sqlite/WenguaApp_双书194案例_患者双重制病优先V3_5_完整研究库.sqlite3"
PARENT_SHA="35940c872435cb3017710557b83bc8600fcff436e35510212b33b3f202ae2b9a"

def evaluate(*,db_path=PARENT):
    db=Path(db_path)
    if not db.exists() or hashlib.sha256(db.read_bytes()).hexdigest()!=PARENT_SHA:
        raise ValueError("V3.6 requires exact immutable full V3.4 parent")
    if len(CASES)!=12 or len({x["id"] for x in CASES})!=12:
        raise ValueError("Twelve unique book illness event families required")
    records=[]
    for spec in CASES:
        row={"family_id":spec["id"],"source_date":spec["date"],"source_day":spec["day"],
          "source_hour":spec["hour"],"source_intent":spec["original_intent"],
          "review":"pending","author_answer_used":False,"later_feedback_used":False,
          "source_clock_minute_attested":spec["minute_known"],
          "template":"health_severity_v36","result":"pending"}
        try:
            t=spec["date"]+"T"+spec["clock"]+":00+08:00"
            cal=solar_chart_clock(t,"Asia/Shanghai")["four_pillars"]
            if cal["day"]!=spec["day"] or cal["hour"]!=spec["hour"]:
                raise ValueError("Book clock does not match source original day/hour")
            chart=layout_from_explicit_bureau(dun=spec["dun"],ju=spec["ju"],hour_ganzhi=spec["hour"])
            if chart["value_star"]!=spec["star"] or chart["value_door"]!=spec["door"]:
                raise ValueError("Book value star/door differ from V3.6 genuine recasting")
            question={"intent":"severity","relationship":spec["relation"],
                      "consultation_context":spec.get("context","direct_proxy")}
            if spec.get("sex"):question["patient_sex"]=spec["sex"]
            if spec["id"]=="kaiwu.final.recovery":
                # Source opening explicitly says son-in-law was born in 1964
                # (甲辰); first-question context, not later outcome disclosure.
                question["patient_birth_ganzhi"]="甲辰"
            if spec.get("birth_ganzhi"):question["patient_birth_ganzhi"]=spec["birth_ganzhi"]
            if spec.get("relative_specific"):question["relative_specific"]=spec["relative_specific"]
            # The animal/person source role was previously unsupported; user now
            # supplied exact animal-hour / spouse-Yi / son-in-law-hour rules.
            caldict={"year_ganzhi":cal["year"],"month_ganzhi":cal["month"],
                "day_ganzhi":cal["day"],"hour_ganzhi":cal["hour"],"month_branch":cal["month"][1]}
            rendered=analyze_health_severity_v36(chart=chart,inquiry=question,calendar=caldict,db_path=db)
            content=rendered["reading_text"]
            row.update(result="rendered",traditional_severity=rendered["audit"]["v35_patient_first_decision"]["verdict"],
             previous_v34_severity=rendered["audit"]["v35_patient_first_decision"]["previous_provisional_verdict"],
             patient_priority=rendered["audit"]["v35_patient_first_decision"],
             corrected_17_composite_predicates=rendered["audit"]["v36_17_source_rechecked_composites"],
             supplied_natal_reference_palace=rendered["audit"]["v35_patient_birth_reference"],
             reading=content,sha256=hashlib.sha256(content.encode()).hexdigest(),
             sections=rendered["sections"],
             role_evidence=rendered["audit"]["v34_patient_binding"],
             double_control=rendered["audit"]["v34_double_control"],
             medicine_copalace=rendered["audit"]["v34_treatment_co_palace"],
             ordered_pairs=rendered["audit"]["v34_42_directional_pairs"],
             composites=rendered["audit"]["v34_17_composite_conditions"],
             original_board_reproduction_quality=(
                "OCR missing stem cells: independently generated chart only, not verified original printed palace completeness"
                if spec["id"]=="kaiwu.health.19980621.rooster_illness" else
                "final chapter original OCR nine-palace grid spatial layout unverified; book value star/door checked only"
                if spec["id"]=="kaiwu.final.recovery" else
                "specified source book hour and value star/door matched casting engine"))
        except (ValueError,KeyError,IndexError,TypeError) as e:
            row.update(result="blocked",reason=type(e).__name__+": "+str(e))
        records.append(row)
    return {"schema":"wengua_health_v34_all_original_12_no_answer_inputs",
      "parent_full_v33_sha256":PARENT_SHA,
      "old_v31_v33_v34_v35_readouts_untouched":True,"n_event_families":12,
      "date_time_is_hour_anchor_not_false_exact_minute":True,
      "clinical_prediction_validation":False,
      "samples":records,
      "counts":{"rendered":sum(z["result"]=="rendered" for z in records),
        "blocked":sum(z["result"]=="blocked" for z in records)}}

if __name__=="__main__":
    j=evaluate()
    for x in j["samples"]:
        print(x["family_id"],x["result"],x.get("traditional_severity",""),x.get("reason",""),x.get("sha256",""))
    print("COUNTS",json.dumps(j["counts"],ensure_ascii=False))
