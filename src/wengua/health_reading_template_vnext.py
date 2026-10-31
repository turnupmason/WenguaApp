"""The real, user-editable GitHub text template entrypoint.

The row texts live ONLY in the imported Excel -> TSV source. The template
controls phrasing and section titles, never hand-maintains 81 case values.
V11 detailed role evidence; frozen V8 source arithmetic and matrices unchanged.
"""
from __future__ import annotations
from functools import lru_cache
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/"data/templates/health_severity_vnext/reading_template.json"
FIELDS=("heaven","earth","name","polarity",
        "classical_text","classical_meaning","imagery")


@lru_cache(maxsize=1)
def template():
    raw=json.loads(SOURCE.read_text(encoding="utf-8"))
    if raw.get("schema") != "health_severity_user_editable_template_v20261031_v11_full_evidence":
        raise ValueError("Unknown user health reading template version")
    if any(not isinstance(raw.get(key),dict) for key in
           ("section_titles","macros")):
        raise ValueError("Template must include titles and macros objects")
    for key in ("macro","role","no_natal","illness","role_score",
                "role_relation","gender_note","auxiliary",
                "overall_resolved","overall_pending","verdict","timing",
                "selected_target_power","selected_role_summary",
                "tianxian_regular","tianxian_fuyin",
                "tianxian_evidence_regular","tianxian_evidence_fuyin",
                "kun_host_note","palace_compact",
                "macro_five_customer","macro_clear_customer",
                "macro_pace_slow","macro_pace_fast",
                "macro_pace_mixed","macro_pace_unset",
                "summary_concise"):
        if not isinstance(raw["macros"].get(key),str):
            raise ValueError("Missing template macro: "+key)
    if not isinstance(raw.get("formation"),str):
        raise ValueError("Missing 81-formation template text")
    return raw


def render(slot,**values):
    """Use only deliberate named placeholders; no implicit missing defaults."""
    try:return template()["macros"][slot].format_map(values)
    except KeyError as exc:raise ValueError(
        "Unknown/missing placeholder in user template slot "+slot+": "+str(exc))


def title(slot,**values):
    try:return template()["section_titles"][slot].format_map(values)
    except KeyError as exc:raise ValueError(
        "Unknown/missing section title placeholder: "+slot+": "+str(exc))


def formation_sentence(pair):
    """Exactly seven known literal user-supplied Excel fields per real pair."""
    args={key:pair[key] for key in FIELDS}
    return template()["formation"].format_map(args)
