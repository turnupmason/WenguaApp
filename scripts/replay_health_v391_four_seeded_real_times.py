"""Fixed-seed random genuine 2026 dates+local hours, 4 simulated self questions.

Uses REAL astronomy solar terms, calendar month, 置闰原术 path and genuine
hourly Xun plate. Randomness is frozen BEFORE chart generation so one
cannot pick favorable charts after seeing a user's wish. All 4 are demos,
NOT personal health diagnosis, old book events or medically true outcomes.
"""
from __future__ import annotations
import hashlib,json,random
from datetime import datetime,timedelta
from pathlib import Path
from zoneinfo import ZoneInfo
from src.wengua.astro_calendar import solar_chart_clock
from src.wengua.casting_shenqi import bureau_for_term,layout_from_explicit_bureau
from src.wengua.health_severity_v391_active import analyze_health_severity_v391

ROOT=Path(__file__).resolve().parents[1]
PARENT=ROOT/"archives/sqlite/WenguaApp_双书194案例_完整十二长生合并V39评分V4_2_完整研究库.sqlite3"
PARENT_SHA="f76b26200d8ed945621139217fcd63d55dddd010c1e4a2848d4e9ad544b3ec66"
SEED_PHRASE="Wengua-V3.9.1-Full12-NoScores-FourFirstQuestions-20261022"
SEED_SHA=hashlib.sha256(SEED_PHRASE.encode("utf8")).hexdigest()
LOCAL_ZONE="America/New_York"
# Dates not used in V3.9 or V4.2 calibration, realistic 2-hour local times
# selected BEFORE any casting. Avoid hour rollover and DST 01:00 ambiguity.
TIMES=(5,9,13,17,21)
CANDIDATES=[datetime(2026,10,25,tzinfo=ZoneInfo(LOCAL_ZONE))+
            timedelta(days=i,hours=hour)
            for i in range(30) for hour in TIMES]
SELECTED=sorted(random.Random(int(SEED_SHA,16)).sample(CANDIDATES,4))

def evaluate(db_path=PARENT):
    db=Path(db_path)
    if not db.is_file() or hashlib.sha256(db.read_bytes()).hexdigest()!=PARENT_SHA:
        raise ValueError("Read only from the exact full V4.2 parent with source 194 originals")
    results=[]
    for stamp in SELECTED:
        iso=stamp.isoformat(timespec="seconds")
        computed=solar_chart_clock(iso,LOCAL_ZONE)
        pillars=computed["four_pillars"]
        if len(pillars)!=4 or len(pillars["hour"])!=2:
            raise ValueError("No genuine original four pillars for sample time")
        bureau=bureau_for_term(pillars["day"],computed["active_solar_term"])
        chart=layout_from_explicit_bureau(dun=bureau["dun"],ju=bureau["ju"],hour_ganzhi=pillars["hour"])
        q={"intent":"severity","relationship":"self",
            "consultation_context":"direct_self"}
        cal={"year_ganzhi":pillars["year"],"month_ganzhi":pillars["month"],
             "day_ganzhi":pillars["day"],"hour_ganzhi":pillars["hour"],
             "month_branch":pillars["month"][1]}
        response=analyze_health_severity_v391(
             chart=chart,inquiry=q,calendar=cal,db_path=db)
        if len(response["sections"])!=10 or len(response["source_chart_evidence"]["complete_eight_palaces_full12"]["outer_eight_palaces"])!=8:
            raise ValueError("Invalid fixed text sections or incomplete actual chart")
        date_id=stamp.strftime("%Y%m%d_%H%M")
        results.append({
         "case_id":"random_sample_self_"+date_id,
         "source":"deterministic_random_real_solar_hour_chart_not_real_patient",
         "local_datetime":iso,"timezone":LOCAL_ZONE,
         "four_pillars":pillars,"solar_term":computed["active_solar_term"],
         "bureau":bureau,"xun_shou":chart["xun_shou"],
         "value_star":chart["value_star"],"value_door":chart["value_door"],
         "person_inquiry":q,"original_v39_reading":response["original_v39_reading"],
         "original_v39_reading_sha256":hashlib.sha256(
             response["original_v39_reading"].encode("utf8")).hexdigest(),
         "new_v391_customer_sections":response["sections"],
         "v391_customer_reading_text":response["reading_text"],
         "v391_customer_reading_sha256":hashlib.sha256(
             response["reading_text"].encode("utf8")).hexdigest(),
         "book_verifiable_chart_facts":response["source_chart_evidence"],
         "no_numerical_score":response["score"] is None,
         "book_author_outcome_never_used":True,"customer_template_review_pending":True,
         "real_health_prognosis_claimed":False})
    if len(results)!=4 or len({x["case_id"] for x in results})!=4:
        raise ValueError("Must randomly generate exactly 4 distinct test local time charts")
    return {"schema":"wengua_v391_four_seeded_true_hour_auto_casts_text_no_score",
      "source_complete_v42_parent_sha256":PARENT_SHA,
      "frozen_random_seed":SEED_PHRASE,"frozen_seed_sha256":SEED_SHA,
      "four_selection_local_isos":[x.isoformat(timespec="seconds") for x in SELECTED],
      "number_of_new_ancient_book_events_added":0,
      "all_samples_assume_self_no_birth_sex_duration":True,
      "all_V39_original_sections_retained":True,
      "all_12_lifecycle_source_facts_calculated":True,
      "all_scoring_experiments_inactive":True,
      "await_user_content_signoff":True,"samples":results}

if __name__=="__main__":
    j=evaluate()
    print(json.dumps({"seed_sha":j["frozen_seed_sha256"],
        "results":[{"id":z["case_id"],"datetime":z["local_datetime"],
          "pillars":z["four_pillars"],"term":z["solar_term"],
          "bureau":z["bureau"],"patient_life":z["book_verifiable_chart_facts"]["patient"],
          "illness_life":z["book_verifiable_chart_facts"]["illness_tianrui_heaven"],
          "verdict":z["book_verifiable_chart_facts"]["v39_original_traditional_verdict"],
          "length":len(z["v391_customer_reading_text"])}
        for z in j["samples"]]},ensure_ascii=False,indent=2))
