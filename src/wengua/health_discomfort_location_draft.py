"""Draft, source-linked body PALACE symbol research for health.discomfort.

This module DOES NOT diagnose symptoms, classify real disease, decide medical
treatment, calculate V8 illness severity, or create a customer-facing verdict.
The health.discomfort iOS topic must remain disabled until book/source conditions
and native Swift full text parity are separately approved.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from .casting_shenqi import RING, STARS

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "data/knowledge/shenqi/health_prediction_ch01/method_index.json"
REVIEW_SCHEMA = "wengua_shenqi_health_method_v1"

TRADITIONAL_NOTES = ROOT / "data/knowledge/health_discomfort/traditional_body_clue_candidates_20261029.json"


def load_traditional_location_candidates(path: Path | None = None) -> dict[str, Any]:
    """External user compilation: structured draft, not source-approved book rules."""
    raw = json.loads((path or TRADITIONAL_NOTES).read_text(encoding="utf8"))
    if (raw.get("schema") != "wengua_health_discomfort_user_notes_candidates_v1"
            or raw.get("status") != "draft_unverified_external_notes"
            or raw.get("release_approved") is not False
            or raw.get("medical_diagnosis_allowed") is not False
            or set(raw.get("palace", {})) != {str(i) for i in RING}
            or set(raw.get("stems", {})) != set("甲乙丙丁戊己庚辛壬癸")
            or set(raw.get("doors", {})) !=
            {"开门", "休门", "生门", "伤门", "杜门", "景门", "死门", "惊门"}
            or set(raw.get("deities", {})) !=
            {"值符", "螣蛇", "太阴", "六合", "白虎", "玄武", "九地", "九天"}):
        raise ValueError("External health-body candidates must remain source-gated and complete")
    return raw


def load_body_source(path: Path | None = None) -> dict[int, dict[str, Any]]:
    raw = json.loads((path or SOURCE).read_text(encoding="utf8"))
    if (raw.get("schema") != REVIEW_SCHEMA or raw.get("book_id") != "shenqi"
            or raw.get("chapter_id") != "health_prediction_ch01"
            or not raw.get("source_sha256")):
        raise ValueError("Unverified body-map source or chapter identity")
    rows = raw.get("body_palace_mappings", [])
    if len(rows) != 8:
        raise ValueError("An actual eight-palace anatomical source is required")
    result: dict[int, dict[str, Any]] = {}
    for row in rows:
        palace = row.get("palace")
        if (palace not in RING or palace in result
                or row.get("review_status") != "draft"
                or row.get("is_medical_diagnosis") is not False
                or row.get("source_lines") != [5, 7]
                or not isinstance(row.get("surface"), list)
                or not isinstance(row.get("internal"), list)):
            raise ValueError(f"Invalid/unsupported source body palace {palace!r}")
        result[palace] = row
    if set(result) != set(RING):
        raise ValueError("Incomplete outer-palace body source")
    return result


def inspect_traditional_body_clues(
    chart: Mapping[str, Any], *, source: Path | None = None
) -> dict[str, Any]:
    """Read actual chart facts; emit TWO alternative source groups, not an answer.

    An inner/outer label is NOT inferred from the yin/yang bureau alone.
    Different times can share the same physical palace but differ in source
    star carriers, injury-door and person binding; all must be reviewed later.
    """
    if (chart.get("school_id") != "shijia_zhuanpan"
            or chart.get("casting_variant") != "shenqi_book_explicit_bureau_v1"):
        raise ValueError("A real shijia zhuanpan source chart is required")
    cells = chart.get("palaces")
    if not isinstance(cells, dict) or set(cells) != {str(i) for i in range(1, 10)}:
        raise ValueError("Nine actual palace facts required")
    positions: list[int] = []
    all_stars: list[str] = []
    injury_doors: list[int] = []
    for i in range(1, 10):
        p = cells[str(i)]
        if p.get("palace") != i or not isinstance(p.get("heaven_stars"), list):
            raise ValueError("Invalid actual palace environment")
        if i == 5:
            if p.get("door") is not None or p.get("deity") is not None or p["heaven_stars"]:
                raise ValueError("Cannot fabricate middle palace ordinary symbols")
            continue
        if p.get("door") is None or p.get("deity") is None:
            raise ValueError("Selected body domain requires complete real environment")
        if p["door"] == "伤门":
            injury_doors.append(i)
        for s in p["heaven_stars"]:
            if not isinstance(s, dict) or not isinstance(s.get("carried_stem"), str):
                raise ValueError("Missing actual carried sky stem")
            all_stars.append(s.get("star"))
            if s.get("star") == "天芮星":
                positions.append(i)
    if (len(positions) != 1 or len(injury_doors) != 1
            or len(all_stars) != 9 or set(all_stars) != set(STARS.values())):
        raise ValueError("Inconsistent Tianrui, injury-door or nine-star plate")
    rows = load_body_source(source)
    spot = positions[0]
    pair = rows[spot]
    external = load_traditional_location_candidates()
    illness = cells[str(spot)]
    sky = next(s["carried_stem"] for s in illness["heaven_stars"]
               if s["star"] == "天芮星")
    companion = next((s["carried_stem"] for s in illness["heaven_stars"]
                      if s["star"] == "天禽星"), None)
    if sky not in external["stems"] or (
            companion is not None and companion not in external["stems"]):
        raise ValueError("Unrecognized actual sky carrier")
    door, deity = illness["door"], illness["deity"]
    if door not in external["doors"] or deity not in external["deities"]:
        raise ValueError("Missing true illness door or deity")
    return {
        "external_notes_status": external["status"],
        "external_palace_candidates": external["palace"][str(spot)],
        "tianrui_stem_main_clues": external["stems"][sky],
        "tianqin_stem_secondary_clues": (
            external["stems"][companion] if companion else None),
        "illness_door_clues": external["doors"][door]["illness"],
        "illness_deity_clues": external["deities"][deity]["illness"],
        "patient_door_clues": None,
        "inner_outer_decision": None,
        "new_old_decision": None,
        "cancer_or_other_diagnosis": None,
        "customer_template_approved": False,
        "topic_id": "health.discomfort",
        "release_status": "source_research_only_not_approved_or_public",
        "source_book": "神奇之门",
        "source_id": "shenqi/health_prediction_ch01/method_index.json",
        "source_lines": pair["source_lines"],
        "tianrui_palace": spot,
        "tianrui_trigram": pair["trigram"],
        "tianrui_carried_stem": next(
            s["carried_stem"] for s in cells[str(spot)]["heaven_stars"]
            if s["star"] == "天芮星"),
        "surface_symbol_candidates": list(pair["surface"]),
        "internal_symbol_candidates": list(pair["internal"]),
        "injury_door_palace_for_secondary_review": injury_doors[0],
        "needs": [
            "real_patient_role_and_relationship",
            "verified_inner_outer_rule",
            "hour_stem_actual_palace",
            "door_deity_carried_stem_and_formation_condition",
            "independent_confirmatory_or_conflicting_source",
        ],
        "conclusion": None,
        "diagnosis": None,
        "medical_claim": False,
        "v80_score": None,
    }
