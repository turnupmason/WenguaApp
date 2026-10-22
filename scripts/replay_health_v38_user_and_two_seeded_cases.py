"""V3.8 deterministic user test and two *seeded random* real book families.

The selection seed is fixed BEFORE touching actual predicted text, based only
on exact immutable V3.7 SHA + user-provided four-pillars string. The source
metadata includes initial question, casting date, original bureau, role;
NO author answer, post-event feedback, retrospective class is loaded.
"""
from __future__ import annotations
import hashlib,json,random
from pathlib import Path
from scripts.replay_all_historical_health_v31_v33 import CASES
from src.wengua.astro_calendar import solar_chart_clock
from src.wengua.casting_shenqi import bureau_for_term,layout_from_explicit_bureau
from src.wengua.health_severity_v38 import analyze_health_severity_v38

ROOT=Path(__file__).resolve().parents[1]
PARENT=ROOT/"archives/sqlite/WenguaApp_双书194案例_81组天地干与双重吉凶V3_7_完整研究库.sqlite3"
PARENT_SHA="f927956e98bb4c193b0be6291c1e01edd31ee61a60b150900095fea0264931d7"
SEED_INPUT="V3.8|"+PARENT_SHA+"|丙午-戊戌-己巳-庚午"
SEED_SHA=hashlib.sha256(SEED_INPUT.encode("utf8")).hexdigest()
RANDOM_INDICES=random.Random(int(SEED_SHA,16)).sample(range(len(CASES)),2)
PINNED_CASE_IDS=[
  "kaiwu.health.19950219.brother_paralysis",
  "shenqi.health.19961102.on_site_health",
]
if [CASES[i]["id"] for i in RANDOM_INDICES]!=PINNED_CASE_IDS:
    raise ValueError("Random family draw changed; do not reroll after seeing predictions")

def _check_db(db_path):
    f=Path(db_path)
    if not f.exists() or hashlib.sha256(f.read_bytes()).hexdigest()!=PARENT_SHA:
        raise ValueError("Requires exact, immutable latest FULL V3.7 parent archive")
    return f

def evaluate(*,db_path=PARENT):
    db=_check_db(db_path)
    records=[]
    for case_i,spec in enumerate([None]+[CASES[i] for i in RANDOM_INDICES]):
        if spec is None:
            timestamp="2026-10-22T12:00:00-04:00"
            computed=solar_chart_clock(timestamp,"America/New_York")
            pillars=computed["four_pillars"]
            if pillars!={"year":"丙午","month":"戊戌","day":"己巳","hour":"庚午"}:
                raise ValueError("User original four pillars not astronomical date")
            bureau=bureau_for_term(pillars["day"],computed["active_solar_term"])
            if (bureau["dun"],bureau["ju"])!=("yin",9):
                raise ValueError("Wrong source bureau for user's current noon")
            chart=layout_from_explicit_bureau(dun=bureau["dun"],ju=bureau["ju"],hour_ganzhi=pillars["hour"])
            q={"intent":"severity","relationship":"self","consultation_context":"direct_self"}
            family="user_20261022_1200_EDT";origin="2026 real user question, NOT an ancient book case"
            anchored=True; original_intent="severity"
        else:
            timestamp=spec["date"]+"T"+spec["clock"]+":00+08:00"
            computed=solar_chart_clock(timestamp,"Asia/Shanghai")
            pillars=computed["four_pillars"]
            if pillars["day"]!=spec["day"] or pillars["hour"]!=spec["hour"]:
                raise ValueError("Historical source original hour inconsistent with independent calendar "+spec["id"])
            bureau={"dun":spec["dun"],"ju":spec["ju"],"solar_term":computed["active_solar_term"],"source_bureau_override":True}
            chart=layout_from_explicit_bureau(dun=bureau["dun"],ju=bureau["ju"],hour_ganzhi=pillars["hour"])
            if chart["value_star"]!=spec["star"] or chart["value_door"]!=spec["door"]:
                raise ValueError("Book value symbol first-question evidence differs from cast "+spec["id"])
            q={"intent":"severity","relationship":spec["relation"],
               "consultation_context":spec.get("context","direct_proxy")}
            if spec.get("sex"):q["patient_sex"]=spec["sex"]
            if spec.get("relative_specific"):q["relative_specific"]=spec["relative_specific"]
            if spec.get("birth_ganzhi"):q["patient_birth_ganzhi"]=spec["birth_ganzhi"]
            if spec["id"]=="kaiwu.final.recovery":q["patient_birth_ganzhi"]="甲辰"
            family=spec["id"];origin="original-book first question only"
            anchored=bool(spec["minute_known"]);original_intent=spec["original_intent"]
        caldict={"year_ganzhi":pillars["year"],"month_ganzhi":pillars["month"],
                 "day_ganzhi":pillars["day"],"hour_ganzhi":pillars["hour"],
                 "month_branch":pillars["month"][1]}
        derived=analyze_health_severity_v38(chart=chart,inquiry=q,calendar=caldict,db_path=db)
        reading=derived["reading_text"]
        audit=derived["audit"]
        person=next(c for c in chart["palaces"].values()
                    if c["palace"]==audit["v37_2_sided_double_evidence"].get("patient_palace",-1)) if "patient_palace" in audit["v37_2_sided_double_evidence"] else None
        from src.wengua.health_dynamic_v21 import bind_patient
        actual_patient=bind_patient(chart,q,caldict)["main_cell"]
        ill_fact=audit["v38_actual_illness_derived_tomb_extinct_void"]
        row={
           "selection_index":case_i,
           "case_id":family,"origin":origin,
           "original_question_intent":original_intent,
           "cast_datetime":timestamp,"exact_minute_verified":anchored,
           "four_pillars":pillars,"solar_term":computed["active_solar_term"],
           "casting_bureau":bureau,
           "xun_shou":chart["xun_shou"],
           "value_star":chart["value_star"],"value_door":chart["value_door"],
           "relationship":q["relationship"],"patient_palace":actual_patient["palace"],
           "illness_palace":ill_fact["illness_palace"],
           "illness_stem_tomb_absence":ill_fact,
           "book_81_ordered_pairs_current_chart":audit["v37_81_ordered_full_book_pairs"],
           "user_42_stem_pairs_audit":audit["v34_42_directional_pairs"],
           "composites_17_audit":audit["v36_17_source_rechecked_composites"],
           "two_sided_evidence":audit["v37_2_sided_double_evidence"],
           "traditional_research_verdict":audit["v37_actual_health_priority_verdict"],
           "original_author_conclusion_used_as_input":False,
           "source_post_event_feedback_used_as_input":False,
           "medical_validity_claim":False,
           "template_version":"V3.8",
           "reading_text":reading,
           "readout_sha256":hashlib.sha256(reading.encode("utf8")).hexdigest(),
           "sections":derived["sections"],
           "user_review":"pending",
           "book_case_board_caveat":(
             "Source first-hour bureau star and door matched but original OCR source palace-by-palace not all independently checked"
             if spec is not None else "True 2026 user civil clock and source fixed casting variant, not a clinic record")
        }
        records.append(row)
    if len(records)!=3 or len({r["case_id"] for r in records})!=3:
        raise ValueError("Must seal user sample + exactly two distinct randomly selected ancient families")
    return {
        "schema":"wengua_health_v38_random_two_ancient_and_user_real_noon_pre_outcome_predictions",
        "full_parent_v37_sha256":PARENT_SHA,
        "rng_seed_input":SEED_INPUT,"rng_seed_sha256":SEED_SHA,
        "random_selection_indices":RANDOM_INDICES,
        "randomly_selected_family_ids":PINNED_CASE_IDS,
        "random_draw_frozen_before_outputs":True,
        "historical_known_family_not_a_secret_blind_test":True,
        "all_original_book_outcomes_excluded":True,
        "new_templates_pending_user_professional_review":True,
        "total_sealed_tests":3,"records":records}

if __name__=="__main__":
    j=evaluate()
    print(json.dumps({"seed":j["rng_seed_sha256"],
      "family_ids":j["randomly_selected_family_ids"],
      "results":[{"id":x["case_id"],"date":x["cast_datetime"],
                  "main":x["traditional_research_verdict"],
                  "illness_stage":x["illness_stem_tomb_absence"],
                  "sha":x["readout_sha256"]} for x in j["records"]]},ensure_ascii=False,indent=2))
    for x in j["records"]:print("\n==== "+x["case_id"]+" ====\n"+x["reading_text"])
