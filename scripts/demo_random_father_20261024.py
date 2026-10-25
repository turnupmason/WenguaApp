"""Reproducible randomly drawn clock for user-requested FATHER severity dry run.

Draw recorded at request time: 2026-11-16 21:00 EST from 2026-11-01
through 2026-12-18 odd-numbered local clock hours. Simulated study, NOT
a real father's diagnosis, not a 195th verified historical case.
Execute in GitHub Actions with the existing repository/runtime intact.
"""
from __future__ import annotations

import json
from pathlib import Path

from src.wengua.health_text_pipeline_vnext_review import auto_cast_health_review_text

CASE_INSTANT = "2026-11-16T21:00:00-05:00"
ZONE = "America/New_York"
INQUIRY = {
    "intent": "severity",
    "relationship": "father",
    "consultation_context": "direct_proxy",
}
OUT = Path("artifacts/random_father_severity_20261024.json")


def make_report():
    report = auto_cast_health_review_text(
        iso=CASE_INSTANT, timezone_name=ZONE, inquiry=dict(INQUIRY))
    if report["instant"] != CASE_INSTANT:
        raise ValueError("Calendar response did not preserve actual input instant")
    if report["audit"]["primary_role_palace"] != 6:
        raise ValueError("Father role must bind from original source to 乾六宫")
    if len(report["nine_palaces"]) != 9:
        raise ValueError("Real chart needs all nine palaces")
    if any(str(k) not in report["nine_palaces"] for k in range(1, 10)):
        raise ValueError("Incomplete actual nine palaces")
    net = report["full_health_role_strength_network"]
    if "candidate_five_grade_quantization" not in net:
        raise ValueError("Must use newest signed star-door-god-pattern rules")
    if "chief" not in net["nodes"]:
        raise ValueError("Omitted latest 八神值符 role")
    if "first_stage_macro" not in report:
        raise ValueError("Five-not-encounter, fuyin and fanyin must be first")
    return report


def main():
    report = make_report()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )
    print("=== WENGUA FATHER SIMULATION -- REPRODUCIBLE RANDOM DRAW ===")
    print("REQUEST_CANDIDATE:", CASE_INSTANT, ZONE)
    print("QUESTION: 父亲的病情严重程度（随机教学盘、并非父亲实际病情）")
    print("CAST:", json.dumps({
        "four_pillars": report["four_pillars"],
        "solar_term": report["solar_term"],
        "bureau": report["bureau"],
        "chart_facts": report["chart_facts"],
    }, ensure_ascii=False, default=str))
    print("MACRO:", json.dumps(report["first_stage_macro"], ensure_ascii=False))
    print("=== ALL NINE REAL CAST PALACES ===")
    for palace in (4,9,2,3,5,7,8,1,6):
        cell = report["nine_palaces"][str(palace)]
        conditions = report["nine_palace_condition_facts"][str(palace)]
        print("PALACE", palace, json.dumps({
            "cell": cell,
            "conditions": conditions,
        }, ensure_ascii=False, default=str))
    print("=== SELECTED ROLE ENERGY, DISEASE RELATION, VOID ===")
    net=report["full_health_role_strength_network"]
    q=net["candidate_five_grade_quantization"]
    for key,node in net["nodes"].items():
        role=q["roles"].get(key)
        relation=net["role_group_reviews"].get(key)
        print("ROLE",key,json.dumps({
            "role":node.get("role"), "palace":node.get("palace"),
            "symbol":node.get("symbol"),"strength":node.get("strength"),
            "month_stage":node.get("month_stage"),
            "void":node.get("void_classification"),
            "deity_energy":node.get("deity_energy"),
            "role_illness_relation":relation,
            "quantization":role,
        }, ensure_ascii=False, default=str))
    print("=== DIRECTED EDGES ===")
    for edge_id,edge in net["directed_edges"].items():
        if edge_id.endswith("->illness"):
            print("EDGE",edge_id,json.dumps({
                "relation":edge.get("relation"),
                "actor_strength":edge.get("actor_strength"),
                "target_strength":edge.get("target_strength"),
                "control_status":edge.get("control_status"),
                "control_result":edge.get("control_result"),
                "control_scenario":edge.get("control_scenario"),
                "ability":edge.get("ability"),
            }, ensure_ascii=False, default=str))
    print("=== FIVE-LEVEL SCORE AND VERDICT ===")
    print("SCORE", json.dumps(q["summary"],ensure_ascii=False,default=str))
    print("VERDICT",json.dumps(report["verdict"],ensure_ascii=False,default=str))
    print("=== COMPLETE USER-FACING SECTIONS ===")
    for section in report["sections"]:
        print("SECTION",section["id"],section["title"],"\n",section["text"])
    print("=== READOUT END; JSON artifact:",OUT,"===")


if __name__ == "__main__":
    main()
