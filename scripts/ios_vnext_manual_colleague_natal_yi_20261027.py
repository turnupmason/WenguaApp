"""Verifiable one-off original four-pillar health test, never resample to change verdict.

User-supplied: 己丑 戊辰 辛卯 丁酉; colleague natal Yi STEM only, no known birth branch or sex.
2009-04-16 17:00 America/New_York is the candidate instant; reject if pillars do not match.
Use existing colleague / casting_month_stem candidate source ONLY.
Never introduce elder Qian/Kun, assumed sex, or an unprovided natal stem.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import json
from src.wengua.health_text_pipeline_vnext_review import auto_cast_health_review_text

INSTANT = "2009-04-16T17:00:00-04:00"
EXPECTED = ["己丑", "戊辰", "辛卯", "丁酉"]
INQUIRY = {
    "intent": "severity",
    "relationship": "colleague",
    "consultation_context": "direct_proxy",
    "patient_birth_stem": "乙",
}

def produce():
    r = auto_cast_health_review_text(
        iso=INSTANT, timezone_name="America/New_York", inquiry=INQUIRY
    )
    pillars = r["four_pillars"]
    actual = [pillars[k] for k in ("year", "month", "day", "hour")]
    if actual != EXPECTED:
        raise AssertionError(
            "DO NOT reinterpret supplied pillars or resample: "
            f"expected={EXPECTED} actual={actual}"
        )
    q = r["full_health_role_strength_network"]["candidate_five_grade_quantization"]
    roles = {
        k: {
            "palace": v["palace"],
            "components": {
                "star": v["star"]["score"],
                "door": v["door"]["score"],
                "deity": v["deity"]["score"],
                "pattern": v["pattern"]["score"],
            },
            "raw": v["palace_score"]["raw_sum"],
            "score": v["palace_score"]["score"],
            "void": v["palace_score"]["void_state"],
        }
        for k, v in q["roles"].items()
    }
    auxiliaries = {
        k: {"palace": v["palace"], "score": v["palace_score"]["score"]}
        for k, v in q["auxiliary_qian_kun"].items()
    }
    controls = {
        k: {
            "direction": v["relation"],
            "cell": v.get("control_result"),
            "scenario": v.get("control_scenario"),
        }
        for k, v in r["full_health_role_strength_network"]["role_group_reviews"].items()
    }
    return {
        "schema": "wengua_ios_random_batch_vnext_20261026_v2",
        "seed": 2009041617,
        "timezone": "America/New_York",
        "selection": "fixed original clock; colleague month-stem conditional; natal Yi explicitly provided no birth branch; no elder palace",
        "rejected": [],
        "cases": [{
            "draw": 1,
            "instant": INSTANT,
            "relationship": "同事",
            "patient_sex": None,
            "patient_birth_ganzhi": None,
            "patient_birth_stem": "乙",
            "context": "direct_proxy",
            "four_pillars": pillars,
            "solar_term": r["solar_term"],
            "bureau": r["bureau"],
            "firstStage": r["first_stage_macro"]["five_not_encounter_triggered"],
            "summary": q["summary"],
            "roles": roles,
            "auxiliaries": auxiliaries,
            "controls": controls,
            "evidenceDirection": r["verdict"]["state"],
            "source_sections": r["sections"],
            "python_reading_text": r["reading_text"],
            "tianrui25": r["qualitative_palace_relationships"]["天芮星月令×星宫五行25格"],
            "macro": r["first_stage_macro"],
        }],
    }

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", required=True)
    args = ap.parse_args()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    data = produce()
    output.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf8")
    print("MANUAL_COLLEAGUE_NO_NATAL_NO_ELDER_PILLARS="+json.dumps({
        "instant": INSTANT,
        "four_pillars": data["cases"][0]["four_pillars"],
        "solar_term": data["cases"][0]["solar_term"],
        "bureau": data["cases"][0]["bureau"],
        "relationship_used": data["cases"][0]["relationship"],
        "birth_ganzhi": None,
        "birth_stem": "乙",
        "source_sections": len(data["cases"][0]["source_sections"]),
    }, ensure_ascii=False))
