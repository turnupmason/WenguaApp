"""One user's genuine original-date four pillars (NOT a book outcome replay):
丙午年 戊戌月 己巳日 庚午时, 2026-10-22 noon America/New_York.

Run ONLY real astronomical calendar -> author source bureau -> genuine
nine-palace cast -> V3.7 offline source-traceable illness-severity test.
User gave no relationship; this first test explicitly selects 本人问健康.
"""
from __future__ import annotations
import hashlib,json
from pathlib import Path
from src.wengua.astro_calendar import solar_chart_clock
from src.wengua.casting_shenqi import bureau_for_term,layout_from_explicit_bureau
from src.wengua.health_severity_v37 import analyze_health_severity_v37

ROOT=Path(__file__).resolve().parents[1]
PARENT=ROOT/"archives/sqlite/WenguaApp_双书194案例_时支驿马三奇得使V3_6_完整研究库.sqlite3"
PARENT_SHA="dc086d67e2ebb477b47ce27f39e7d58879ac33bbd56715152230e638862be9d8"
PILLARS={"year":"丙午","month":"戊戌","day":"己巳","hour":"庚午"}

def test_case(*,db_path=PARENT):
    db=Path(db_path)
    if not db.exists() or hashlib.sha256(db.read_bytes()).hexdigest()!=PARENT_SHA:
        raise ValueError("Only exact V3.6 complete 194 original source database accepted")
    calendar=solar_chart_clock("2026-10-22T12:00:00-04:00","America/New_York")
    if calendar["four_pillars"]!=PILLARS:
        raise ValueError("Original requested four pillars do not match astronomical local date/time")
    if calendar["active_solar_term"]!="寒露":
        raise ValueError("Wrong 2026-10-22 actual solar term")
    bureau=bureau_for_term(PILLARS["day"],calendar["active_solar_term"])
    if (bureau["dun"],bureau["ju"],bureau["yuan"])!=("yin",9,"middle"):
        raise ValueError("Actual mid-yuan cold dew should be yin bureau nine under original supported method")
    chart=layout_from_explicit_bureau(dun=bureau["dun"],ju=bureau["ju"],
             hour_ganzhi=PILLARS["hour"])
    if chart["value_star"]!="天英星" or chart["value_door"]!="景门" or chart["value_star_palace"]!=7:
        raise ValueError("Expected sourced value-star/door chart not reproduced")
    request={"intent":"severity","relationship":"self","consultation_context":"direct_self"}
    cal={"year_ganzhi":PILLARS["year"],"month_ganzhi":PILLARS["month"],
         "day_ganzhi":PILLARS["day"],"hour_ganzhi":PILLARS["hour"],
         "month_branch":"戌"}
    readout=analyze_health_severity_v37(chart=chart,inquiry=request,calendar=cal,db_path=db)
    audit=readout["audit"]
    person_role=audit["v34_patient_binding"]
    if person_role["stem"]!="己":
        raise ValueError("Actual patient cannot be replaced by current-hour 庚")
    cells={}
    for p,c in chart["palaces"].items():
        cells[p]={
          "palace":c["palace"],"gua":c["gua"],"earth_stem":c["earth_stem"],
          "heaven_stars":c["heaven_stars"],"door":c["door"],"deity":c["deity"],
          "roles":sorted(set(role for q in audit["v37_81_ordered_full_book_pairs"]
                             if q["palace"]==int(p) for role in q["roles"]))}
    reading=readout["reading_text"]
    if not reading or len(readout["sections"])!=10: # sex unknown: 10/11
        raise ValueError("Expected complete 10-section gender-unknown fixed disease readout")
    return {
      "schema":"wengua_v37_2026_10_22_user_noon_true_bureau_source_test",
      "source":"user_provided_four_pillars_2026-10-22",
      "timestamp_local":"2026-10-22T12:00:00-04:00",
      "local_timezone":"America/New_York",
      "pillars":PILLARS,
      "question":"本人问疾病轻重（上下文明确；未给症状和出生年命）",
      "health_subintent":"severity_only",
      "calendar":calendar,
      "bureau":bureau,
      "chart":{"dun":chart["dun"],"ju":chart["ju"],"xun_shou":chart["xun_shou"],
         "hidden_stem":chart["hidden_stem"],"value_star":chart["value_star"],
         "value_star_palace":chart["value_star_palace"],
         "value_door":chart["value_door"],
         "value_door_palace":chart["value_door_palace"],
         "palaces":cells},
      "roles":{"patient_stem":"己",
          "patient_palace":person_role["main_palace"] if "main_palace" in person_role else None},
      "traditional_provisional_verdict":audit["v37_previous_v36_verdict"],
      "traditional_v37_verdict":audit["v37_actual_health_priority_verdict"],
      "double_evidence":audit["v37_2_sided_double_evidence"],
      "actual_all_nine_source_pairs":audit["v37_81_ordered_full_book_pairs"],
      "matched_42_user_health_pairs":audit["v34_42_directional_pairs"],
      "seventeen_composite_checks":audit["v36_17_source_rechecked_composites"],
      "same_palace_medicine":audit["v34_treatment_co_palace"],
      "readout_sections":readout["sections"],
      "reading_text":reading,"reading_sha256":hashlib.sha256(reading.encode("utf8")).hexdigest(),
      "author_outcome_used":False,
      "actual_real_world_medical_certainty":False,
      "user_review":"pending"}

if __name__=="__main__":
    case=test_case()
    print(json.dumps({k:v for k,v in case.items() if k not in
      ("calendar","chart","actual_all_nine_source_pairs",
       "matched_42_user_health_pairs","seventeen_composite_checks",
       "readout_sections","reading_text")},ensure_ascii=False,indent=2))
    print("V3.7 TRUE FIXED TEMPLATE READING:\n"+case["reading_text"])
