"""One real board => V3.9 fixed client reading verbatim plus V4.2 budgeted score.

Five source pre-question problems: exact previous 3 + 2 additional health
event families not selected for V4.1 weight tuning. The latter are not
secret future/clinical blind trials; source metadata only, not book endings.
"""
from __future__ import annotations
import hashlib,json
from pathlib import Path
from scripts.replay_all_historical_health_v31_v33 import CASES
from src.wengua.astro_calendar import solar_chart_clock
from src.wengua.casting_shenqi import bureau_for_term,layout_from_explicit_bureau
from src.wengua.health_severity_v42_integrated import analyze_health_severity_v42

ROOT=Path(__file__).resolve().parents[1]
PARENT=ROOT/"archives/sqlite/WenguaApp_双书194案例_81原书病情格局校核V4_1_完整研究库.sqlite3"
PARENT_SHA="f90e9de80b24a852c26d4957e4e91234f86b76c9289cbc9f4738eb1b735bf01a"
EARLIER=ROOT/"data/evaluation/health_v39/user_noon_two_seeded_book_families_V39_SEALED.json"
IDS=[
  "user_20261022_1200_EDT",
  "kaiwu.health.19950219.brother_paralysis",
  "shenqi.health.19961102.on_site_health",
  "shenqi.health.19960316.self_surgery",
  "shenqi.health.19960727.father_illness",
]
def evaluate(db_path=PARENT):
    path=Path(db_path)
    if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=PARENT_SHA:
        raise ValueError("V4.2 parent must be exact complete source V4.1")
    earlier=json.loads(EARLIER.read_text("utf8"))
    old_by_id={x["case_id"]:x for x in earlier["records"]}
    if len(old_by_id)!=3:raise ValueError("The three V3.9 sealed client readings changed")
    records=[]
    for id in IDS:
        if id=="user_20261022_1200_EDT":
            dt="2026-10-22T12:00:00-04:00"
            cast_time=solar_chart_clock(dt,"America/New_York")
            columns=cast_time["four_pillars"]
            if columns!={"year":"丙午","month":"戊戌","day":"己巳","hour":"庚午"}:
                raise ValueError("Actual user pillars changed")
            bureau=bureau_for_term(columns["day"],cast_time["active_solar_term"])
            inquiry={"intent":"severity","relationship":"self","consultation_context":"direct_self"}
            story="current user: self question, not book case"
        else:
            spec=next((x for x in CASES if x["id"]==id),None)
            if spec is None or spec["original_intent"]!="health":
                raise ValueError("Must be a real first question about health only")
            dt=spec["date"]+"T"+spec["clock"]+":00+08:00"
            cast_time=solar_chart_clock(dt,"Asia/Shanghai")
            columns=cast_time["four_pillars"]
            if (columns["day"],columns["hour"])!=(spec["day"],spec["hour"]):
                raise ValueError("Book's real first-question pillars mismatch")
            bureau={"dun":spec["dun"],"ju":spec["ju"],"source_override":True}
            inquiry={"intent":"severity","relationship":spec["relation"],
              "consultation_context":spec.get("context","direct_proxy")}
            for src,dest in (("sex","patient_sex"),
                             ("relative_specific","relative_specific"),
                             ("birth_ganzhi","patient_birth_ganzhi")):
                if spec.get(src):inquiry[dest]=spec[src]
            story="ancient actual first question only; no author diagnosis used"
        chart=layout_from_explicit_bureau(
            dun=bureau["dun"],ju=bureau["ju"],hour_ganzhi=columns["hour"])
        if id!="user_20261022_1200_EDT":
            if (chart["value_star"],chart["value_door"])!=(spec["star"],spec["door"]):
                raise ValueError("Book's value star/door differs from new chart")
        calendar={"year_ganzhi":columns["year"],
           "month_ganzhi":columns["month"],"day_ganzhi":columns["day"],
           "hour_ganzhi":columns["hour"],"month_branch":columns["month"][1]}
        actual=analyze_health_severity_v42(
            chart=chart,inquiry=inquiry,calendar=calendar,db_path=path)
        raw=actual["exact_original_v39_reading"]
        historical_rerun=old_by_id.get(id)
        if historical_rerun and raw!=historical_rerun["reading_text"]:
            raise ValueError("DO NOT rewrite user-stage-accepted V3.9 customer text: "+id)
        q=actual["scoring"]
        records.append({
          "family_id":id,"datetime":dt,"source_scope":story,
          "four_pillars":columns,"original_question":inquiry,
          "bureau":bureau,"value_star":chart["value_star"],
          "value_door":chart["value_door"],
          "original_v39_reading_sha256":hashlib.sha256(raw.encode("utf8")).hexdigest(),
          "old_v39_reading_byte_identical":historical_rerun is None or raw==historical_rerun["reading_text"],
          "new_integrated_reading_sha256":hashlib.sha256(actual["reading_text"].encode("utf8")).hexdigest(),
          "V39_exact_legacy_customer_text":raw,
          "V42_integrated_customer_text":actual["reading_text"],
          "V42_integrated_extra_section":actual["sections"][-1],
          "old_verdict":actual["traditional_v39_qualitative_verdict"],
          "stage_actor_audit":actual["chart_evidence"]["source12_stage_for_actors"],
          "complete_real_chart_facts":actual["chart_evidence"],
          "symbolic_scoring":q,
          "new_medical_diagnosis":False,
          "author_book_outcome_used":False,
          "user_approved":False
        })
    return {"schema":"wengua_v42_unified_v39_qualitative_full12_six_budget_numeric",
       "parent_exact_full_V41_sha256":PARENT_SHA,
       "same_3_old_plus_two_distinct_first_health_questions":True,
       "case_ids_in_source_fixed_order":IDS,
       "no_original_book_post_event_outcome_input":True,
       "stages_all_source_anchors_validated":True,
       "score_is_not_a_medical_probability":True,
       "user_approved":False,"records":records}
if __name__=="__main__":
    r=evaluate()
    print(json.dumps({"cases":[{
        "id":x["family_id"],"original_v39_sha":x["original_v39_reading_sha256"],
        "v39_unchanged":x["old_v39_reading_byte_identical"],
        "score":x["symbolic_scoring"]["observed_or_unspecified_nominal"]["score"],
        "range":x["symbolic_scoring"]["scenario_range"],
        "scenario":x["symbolic_scoring"]["conditional_scenarios"],
        "patient_stages":x["stage_actor_audit"]["patient"]["all_actual_branch_stages"],
        "illness_stages":x["stage_actor_audit"]["tianrui_heaven"]["all_actual_branch_stages"]
        } for x in r["records"]]},ensure_ascii=False,indent=2))
