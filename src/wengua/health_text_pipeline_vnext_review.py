"""Preview-only end-to-end route, V3.9.1 published route is NOT changed.

Usage: auto_cast_health_review_text(iso=..., timezone_name=..., inquiry=...)
"""
from __future__ import annotations
from .astro_calendar import solar_chart_clock
from .casting_shenqi import bureau_for_term,layout_from_explicit_bureau
from .health_severity_vnext_review import analyze_health_severity_review
from .health_text_pipeline import DEFAULT_DB

def auto_cast_health_review_text(*,iso,timezone_name,inquiry,db_path=None):
    if not iso or not timezone_name or not isinstance(inquiry,dict) or inquiry.get("intent")!="severity":
        raise ValueError("Require exact instant, timezone and illness-severity intent")
    clock=solar_chart_clock(iso,timezone_name)
    pillars=clock["four_pillars"]
    bureau=bureau_for_term(pillars["day"],clock["active_solar_term"])
    chart=layout_from_explicit_bureau(
        dun=bureau["dun"],ju=bureau["ju"],hour_ganzhi=pillars["hour"])
    cal={"year_ganzhi":pillars["year"],"month_ganzhi":pillars["month"],
         "day_ganzhi":pillars["day"],"hour_ganzhi":pillars["hour"],
         "month_branch":pillars["month"][1]}
    review=analyze_health_severity_review(
        chart=chart,inquiry=inquiry,calendar=cal,db_path=db_path or DEFAULT_DB)
    return {
        "version":"vnext_preview_only","status":"review_not_public",
        "instant":iso,"timezone":timezone_name,
        "four_pillars":pillars,"solar_term":clock["active_solar_term"],
        "bureau":bureau,
        "chart_facts":{"xun_shou":chart["xun_shou"],
                       "value_star":chart["value_star"],
                       "value_door":chart["value_door"]},
        "verdict":review["verdict"],"sections":review["sections"],
        "reading_text":review["reading_text"],
        "evidence_counts":review["evidence_counts"],
        "evidence_ledger":review["evidence_ledger"],
        "ordered_palace_roles":review["ordered_palace_roles"],
        "macro_fuyin_fanyin":review["macro_fuyin_fanyin"],
        "qualitative_palace_relationships":review["qualitative_palace_relationships"],
        "audit":review["audit"],
        "no_scoring":True,"medical_validity_claimed":False
    }
