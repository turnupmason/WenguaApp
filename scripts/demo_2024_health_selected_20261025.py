"""One reproducible 2024 illness-severity TEACHING chart (not a real patient).

Fix a seeded date/time selection and choose first cast that is technically
bindable for a direct-self query; never inspect a chart's fortune to select
the example. The 15-day one-real-event once rule does not apply to offline
historical software testing, nor is this an ancient-book case.
"""
from __future__ import annotations
import json
import random
from datetime import datetime, timedelta
from pathlib import Path

from src.wengua.health_text_pipeline_vnext_review import auto_cast_health_review_text

ZONE="America/New_York"
INQUIRY={"intent":"severity","relationship":"self",
         "consultation_context":"direct_self","patient_sex":"male"}
OUTPUT=Path("artifacts/demo_2024_health_selected_20261025.json")


def make_report():
    # Seed and selection rule fixed BEFORE observing any outcome.
    rng=random.Random(20241025)
    offsets=list(range(0,240))
    rng.shuffle(offsets)
    skipped=[]
    for offset in offsets:
        day=datetime(2024,3,15,13,0)+timedelta(days=offset)
        # March 15-November 9, 2024: all 13:00 local clocks observe EDT.
        iso=day.isoformat()+"-04:00"
        try:
            report=auto_cast_health_review_text(
                iso=iso,timezone_name=ZONE,inquiry=INQUIRY)
        except (ValueError,KeyError) as exc:
            # Self-year hidden 甲 or centre transfer source gaps: don't invent.
            skipped.append({"instant":iso,"reason":str(exc)[:170]})
            continue
        report["demonstration_selection"]={
            "seed":20241025,
            "random_draw_candidates":len(offsets),
            "technical_unavailable_before_first_cast":skipped,
            "selection_not_conditioned_on_good_bad_score":True,
            "not_real_health_case":True,"not_book_case":True}
        return report
    raise ValueError("No fully castable real date in seeded 2024 selection")


def main():
    report=make_report()
    if not report["instant"].startswith("2024-"):
        raise AssertionError("Illustration must belong to 2024")
    net=report["full_health_role_strength_network"]
    q=net["candidate_five_grade_quantization"]
    selected=set(report["scored_relevant_palaces"])
    expected={x["palace"] for x in net["nodes"].values()}|{2,6}
    if selected!=expected:raise AssertionError("Scored unrelated palace")
    if set(report["nine_palace_condition_facts"])!={str(k) for k in selected}:
        raise AssertionError("Unexpected downstream unrelated palace computation")
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    OUTPUT.write_text(json.dumps(report,ensure_ascii=False,indent=2,default=str),
                      encoding="utf-8")
    print("TEACHING_2024_INSTANT",report["instant"])
    print("TECHNICAL_SKIPS",len(report["demonstration_selection"][
        "technical_unavailable_before_first_cast"]))
    print("CAST",json.dumps({
        "pillars":report["four_pillars"],
        "solar_term":report["solar_term"],
        "bureau":report["bureau"],
        "xun_shou":report["chart_facts"]["xun_shou"],
        "selected_palaces":sorted(selected),
        "all_nine_cast_count":len(report["nine_palaces"]),
        "first_stage_macro":report["first_stage_macro"],
    },ensure_ascii=False,default=str))
    print("FINAL_SCORE",json.dumps(q["summary"],ensure_ascii=False,default=str))
    for key,item in q["roles"].items():
        print("ROLE",key,json.dumps({
            "palace":item["palace"],
            "star":item["star"],"door":item["door"],
            "deity":item["deity"],"pattern":item["pattern"],
            "palace_score":item["palace_score"],
        },ensure_ascii=False,default=str))
    for key,item in q["auxiliary_qian_kun"].items():
        print("AUX",key,json.dumps({
            "palace":item["palace"],"palace_score":item["palace_score"]},
            ensure_ascii=False,default=str))
    for key,item in net["role_group_reviews"].items():
        print("REL",key,json.dumps(item,ensure_ascii=False,default=str))
    print("=== COMPLETE SEVERITY READING ===")
    for section in report["sections"]:
        print("SECTION",section["id"],section["title"])
        print(section["text"])
    print("=== END 2024 HISTORICAL SOFTWARE SIMULATION ===")


if __name__=="__main__":
    main()
