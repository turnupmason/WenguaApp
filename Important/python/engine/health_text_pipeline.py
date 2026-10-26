"""Active public callable flow for the future iOS app:

  actual timezone-aware clock -> real solar term and 4 pillars ->
  source original yin/yang bureau, full true nine-palace structure ->
  independent, role-aware V3.9 evidence and case-conditioned text ->
  verified complete 12-lifecycle facts for five true roles ->
  same eleven-slot traditional customer reading, NO SCORES.

App UI integration waits for user's explicit V3.9.1 sample approval.
"""
from __future__ import annotations
from pathlib import Path
from .astro_calendar import solar_chart_clock
from .casting_shenqi import bureau_for_term,layout_from_explicit_bureau
from .health_severity_v391_active import analyze_health_severity_v391
ROOT=Path(__file__).resolve().parents[2]
DEFAULT_DB=ROOT/"archives/sqlite/WenguaApp_双书194案例_V391纯断词十二长生_完整研究库.sqlite3"

def auto_cast_health_v39_text(*,iso:str,timezone_name:str,inquiry:dict,db_path=None):
    if not iso or not timezone_name or inquiry.get("intent")!="severity":
        raise ValueError("Require real instant/timezone and traditional illness-severity inquiry")
    clock=solar_chart_clock(iso,timezone_name)
    pillars=clock["four_pillars"]
    bureau=bureau_for_term(pillars["day"],clock["active_solar_term"])
    chart=layout_from_explicit_bureau(dun=bureau["dun"],ju=bureau["ju"],hour_ganzhi=pillars["hour"])
    cal={"year_ganzhi":pillars["year"],"month_ganzhi":pillars["month"],
         "day_ganzhi":pillars["day"],"hour_ganzhi":pillars["hour"],
         "month_branch":pillars["month"][1]}
    results=analyze_health_severity_v391(chart=chart,inquiry=inquiry,
        calendar=cal,db_path=db_path or DEFAULT_DB)
    return {
        "version":"V3.9.1","mode":"traditional_source_text_only",
        "instant":iso,"timezone":timezone_name,"four_pillars":pillars,
        "actual_solar_term":clock["active_solar_term"],
        "bureau":bureau,
        "chart":{"palaces":chart["palaces"],"value_star":chart["value_star"],
                 "value_door":chart["value_door"],"xun_shou":chart["xun_shou"]},
        "text_sections":results["sections"],"reading_text":results["reading_text"],
        "source_internal_evidence":results["source_chart_evidence"],
        "numeric_scoring_enabled":False,"score":None,
        "customer_medical_validity":False}
