"""Reproducible *random, real* calendar charts for inspecting the V-next template.

Seeded for review reproducibility, with condition coverage for the two user
门破 exceptions. Does NOT invent old-book case outcomes or a clinical prognosis.
Usage:
  python -m scripts.preview_health_random_complete_20261024 artifacts/random_health.json
"""
from __future__ import annotations

from datetime import datetime,timedelta
from pathlib import Path
from random import Random
from zoneinfo import ZoneInfo
import json
import sys

from src.wengua.astro_calendar import solar_chart_clock
from src.wengua.casting_shenqi import bureau_for_term,layout_from_explicit_bureau
from src.wengua.health_text_pipeline_vnext_review import auto_cast_health_review_text

SEED=20261024
TZ="America/New_York"
INQUIRY={"intent":"severity","relationship":"self",
         "consultation_context":"direct_self"}
BASE=datetime(2026,10,26,1,tzinfo=ZoneInfo(TZ))
HOURS=tuple(range(1,23,2))


def _candidate_clock():
    moments=[(BASE+timedelta(days=d)).replace(hour=h)
             for d in range(18) for h in HOURS]
    Random(SEED).shuffle(moments)
    for moment in moments:
        iso=moment.isoformat()
        try:
            cal=solar_chart_clock(iso,TZ)
            p=cal["four_pillars"]
            bureau=bureau_for_term(p["day"],cal["active_solar_term"])
            chart=layout_from_explicit_bureau(
                dun=bureau["dun"],ju=bureau["ju"],hour_ganzhi=p["hour"])
        except ValueError:
            # Original-method boundary: uncertain solar-term instant OR
            # value door's unresolved centre-5 hosting. Do not interpolate
            # month/term, fabricate a centre-door, or fake the chart.
            continue
        cells=chart["palaces"]
        flags=tuple(
            key for key,door,palace in (
                ("生门坎免减级","生门",1),
                ("景门乾免减级","景门",6))
            if cells[str(palace)]["door"]==door)
        yield iso,flags


def _small_cell(cell):
    return {
        "palace":cell["palace"],"deity":cell["deity"],
        "stars":[x["star"]+"("+x["carried_stem"]+")"
                 for x in cell["heaven_stars"]],
        "door":cell["door"],"earth_stem":cell["earth_stem"],
    }


def _simplify(report,flags):
    net=report["full_health_role_strength_network"]
    quant=net["candidate_five_grade_quantization"]
    roles={}
    for k,detail in net["complete_selected_palace_audits"].items():
        q=quant["roles"][k]
        roles[k]={
            "palace":detail["palace"],"palace_name":detail["palace_name"],
            "stars":[{"name":x["name"],
                      "strength":x["strength"]["strength_label"],
                      "month":x["strength"]["symbol_month_stage"]}
                     for x in detail["stars"]],
            "god":{"name":detail["deity"]["name"],
                   "relation":detail["deity"]["relation"],
                   "polarity":detail["deity"]["polarity"]},
            "door":{"name":detail["door"]["symbol"],
                    "strength":detail["door"]["strength_label"],
                    "month":detail["door"]["symbol_month_stage"],
                    "palace_relation":detail["door"]["user_cell_col"],
                    "two_level_shift":q["door"]["applied_door_break_shift"],
                    "exempt":q["door"]["penalty_policy"]["no_extra_two_level_shift"]},
            "heaven_stems":[{"name":v["symbol"],"strength":v["strength_label"]}
                            for v in detail["heaven_stems"]],
            "earth_stem":{"name":detail["earth_stem"]["symbol"],
                          "strength":detail["earth_stem"]["strength_label"]},
            "source_book_patterns":[{"name":x["name"],"usable":x["can_vote"]}
                                    for x in detail["ordered_book_81_pairs"]],
            "void":detail["void"]["classification"],
            "horses":detail["horse_branch"],
            "tombs":{"heaven":detail["sky_tombs"],
                     "earth":detail["earth_tombs"]},
            "striking_stems":detail["striking_stems"],
            "door_pressure":detail["door_pressure"],
            "role_tianrui":net["role_group_reviews"].get(k),
            "quant":{"known_subtotal":q["palace_score"]["known_subtotal"],
                     "unresolved":q["palace_score"]["unresolved_categories"],
                     "score":q["palace_score"]["score"],
                     "grade":q["palace_score"]["grade"],
                     "status":q["palace_score"]["status"]},
        }
    return {
        "iso":report["instant"],"timezone":report["timezone"],
        "selection":"seeded_random_real_clock_filter_for_door_exception",
        "seed":SEED,"triggered_exception_examples":flags,
        "four_pillars":report["four_pillars"],"solar_term":report["solar_term"],
        "bureau":report["bureau"],"chart_facts":report["chart_facts"],
        "nine_palaces":{k:_small_cell(v) for k,v in report["nine_palaces"].items()},
        "macro":report["first_stage_macro"],"roles":roles,
        "auxiliary_qian_kun":{k:{"palace":x["palace"],
                                 "relation_to_illness":x["relation_to_illness"]}
                              for k,x in net["qian_kun_auxiliary_observations"].items()},
        "quantization_summary":quant["summary"],
        "traditional_review_verdict":report["verdict"],
        "traditional_evidence_counts":report["evidence_counts"],
        "reading_text":report["reading_text"],
        "not_clinical":True,
    }


def generate_random_cases():
    # First occurrence of each of two user door-break exceptions, plus one
    # third independent randomly selected chart. This is a SHOWCASE
    # selection, never an independent held-out accuracy evaluation.
    candidates=list(_candidate_clock())
    reports=[];failures=[];selected_ids=set()
    def attempt(pair):
        iso,flags=pair
        if iso in selected_ids:return False
        try:
            r=auto_cast_health_review_text(
                iso=iso,timezone_name=TZ,inquiry=INQUIRY)
        except ValueError as exc:
            # Invalid source bound or unresolved centre-5 hosting is a
            # legitimate excluded candidate, not license to substitute a
            # fictitious patient or fake calendar facts.
            failures.append({"iso":iso,"reason":str(exc)})
            selected_ids.add(iso)
            return False
        reports.append(_simplify(r,flags))
        selected_ids.add(iso)
        return True
    # Cover both user exception patterns using real randomly ordered casts.
    # Each must ALSO pass all original self-patient source-identity gates.
    for wanted in ("生门坎免减级","景门乾免减级"):
        for pair in candidates:
            if wanted not in pair[1]:continue
            if attempt(pair):break
    for pair in candidates:
        if len(reports)>=3:break
        attempt(pair)
    if len(reports)!=3:
        raise AssertionError("Could not generate three actual self-charts")
    return {"seed":SEED,"timezone":TZ,"intent":"health/severity/self",
            "search_window":"2026-10-26 ... 2026-11-12, real odd-hour time spans",
            "generated_count":len(reports),"discarded_unbound":len(failures),
            "exception_observed":sorted(set(
                flag for sample in reports
                for flag in sample["triggered_exception_examples"])),
            "status":"real_cast_research_preview_not_blind_outcomes",
            "samples":reports}


def main():
    payload=generate_random_cases()
    if len(sys.argv)>1:
        path=Path(sys.argv[1]);path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps(payload,ensure_ascii=False,indent=2),
                        encoding="utf-8")
    print("WENGUA_RANDOM_CASE_JSON "+json.dumps(
        payload,ensure_ascii=False,separators=(",",":")))


if __name__=="__main__":main()
