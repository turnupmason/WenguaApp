"""One reproducibly randomized REAL 2025 eastern-clock health chart.

No chart interpolation, no external network, no unsupported middle-five
hosting, no unknown 甲 self day stem, no case outcome labels, no clinical claim.
Usage: python -m scripts.preview_health_random_2025_intrinsic_vnext [output.json]
"""
from __future__ import annotations
from datetime import datetime,timedelta
from pathlib import Path
from random import Random
from zoneinfo import ZoneInfo
import json,sys

from src.wengua.astro_calendar import solar_chart_clock
from src.wengua.casting_shenqi import bureau_for_term,layout_from_explicit_bureau
from src.wengua.health_text_pipeline_vnext_review import auto_cast_health_review_text
from src.wengua.health_intrinsic_scoring_vnext import catalog_validation
from src.wengua.health_quant_overlay_vnext import render_palace_signed_score

SEED=20251024
TZ="America/New_York"
FIRST=datetime(2025,2,1,1,tzinfo=ZoneInfo(TZ))
INQUIRY={"intent":"severity","relationship":"self",
         "consultation_context":"direct_self"}


def generate_random_2025():
    candidates=[(FIRST+timedelta(days=d)).replace(hour=h)
                for d in range(310) for h in range(1,24,2)]
    Random(SEED).shuffle(candidates)
    discarded=[]
    for moment in candidates:
        iso=moment.isoformat()
        try:
            cal=solar_chart_clock(iso,TZ)
            pillars=cal["four_pillars"]
            bureau=bureau_for_term(pillars["day"],cal["active_solar_term"])
            chart=layout_from_explicit_bureau(
                dun=bureau["dun"],ju=bureau["ju"],hour_ganzhi=pillars["hour"])
            report=auto_cast_health_review_text(
                iso=iso,timezone_name=TZ,inquiry=INQUIRY)
            if report["four_pillars"]!=pillars:
                raise AssertionError("Reported pillars differ from real cast")
        except ValueError as exc:
            discarded.append({"iso":iso,"reason":str(exc)})
            continue
        if int(iso[:4])!=2025:raise AssertionError("Need year 2025 only")
        net=report["full_health_role_strength_network"]
        q=net["candidate_five_grade_quantization"]
        roles={}
        for role,d in q["roles"].items():
            pal=d["palace_score"]
            roles[role]={
                "palace":d["palace"],"stars":d["star"]["per_star"],
                "door":{"symbol":d["door"]["symbol"],
                        "baseline":d["door"].get("baseline"),
                        "actual_tier":d["door"].get("strength"),
                        "score":d["door"].get("score")},
                "god":{"symbol":d["deity"]["symbol"],
                       "relation":d["deity"].get("nominal_relation"),
                       "strength":d["deity"].get("tier"),
                       "score":d["deity"].get("score"),
                       "no_month":True},
                "ordered_stem_patterns":[{
                    "key":x["key"],"name":x["name"],
                    "source_status":x["source_rule"]["status"],
                    "score":x["score"],
                    "original_book_line":(
                        x["actual_book_source"]["source_line_internal"]
                        if x["actual_book_source"] else None)}
                    for x in d["pattern"]["matches"]],
                "known_signed_subtotal":pal["known_subtotal"],
                "unresolved":pal["unresolved_categories"],
                "palace_score":pal["score"],"grade":pal["grade"],
                "status":pal["status"],
                "detailed_text":render_palace_signed_score(d)}
        output={
            "status":"real_random_2025_chart_candidate_not_clinical",
            "seed":SEED,"candidate_hour_basis":"2025 US/Eastern real double-hours",
            "selected_rank":"first valid chart after a deterministic uniform shuffle",
            "discarded_chart_candidates":len(discarded),
            "discarded_reasons_sample":discarded[:8],
            "instant":iso,"timezone":TZ,
            "four_pillars":report["four_pillars"],
            "solar_term":report["solar_term"],
            "bureau":report["bureau"],"chart_facts":report["chart_facts"],
            "nine_palaces":report["nine_palaces"],
            "nine_palace_conditions":report["nine_palace_condition_facts"],
            "macro":report["first_stage_macro"],
            "role_polarity_and_energy":roles,
            "auxiliary_qian_kun":{
                k:{"palace":v["palace"],"role":v["role"],
                   "relation_to_illness":v["relation_to_illness"]}
                for k,v in net["qian_kun_auxiliary_observations"].items()},
            "role_to_tianrui":net["role_group_reviews"],
            "net_quantization":q["summary"],
            "user_ordered81_coverage":catalog_validation(),
            "reading_text":report["reading_text"],
            "not_a_medicine_or_prognosis":True,
        }
        return output
    raise AssertionError("No valid source-bound health chart from 2025 candidate clock")


def main():
    r=generate_random_2025()
    if len(sys.argv)>1:
        dest=Path(sys.argv[1]);dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_text(json.dumps(r,ensure_ascii=False,indent=2),
                        encoding="utf-8")
    print("WENGUA_2025_RANDOM_SUMMARY "+json.dumps({
        "instant":r["instant"],"seed":r["seed"],
        "four_pillars":r["four_pillars"],"bureau":r["bureau"],
        "macro":{"five":r["macro"]["five_not_encounter_triggered"],
                 "star":r["macro"]["fuyin_fanyin"]["star"],
                 "door":r["macro"]["fuyin_fanyin"]["door"]},
        "selected_palace_energies":{
            k:{"palace":v["palace"],"stars":[{
                "name":x["symbol"],"score":x["score"],
                "tier":x.get("tier")} for x in v["stars"]],
                "door":v["door"],"god":v["god"],
                "pairs":v["ordered_stem_patterns"],
                "known":v["known_signed_subtotal"],"grade":v["grade"],
                "status":v["status"],"unresolved":v["unresolved"]}
            for k,v in r["role_polarity_and_energy"].items()},
        "overall":r["net_quantization"]
    },ensure_ascii=False,separators=(",",":")))
    print("WENGUA_2025_RANDOM_READING "+r["reading_text"])

if __name__=="__main__":main()
