"""V29 fixed template: one monthly fact per medicinal symbol per paragraph.

A non-destructive refinement to the full original-book V28 results. No GPT,
network, arbitrary author-answer modification or duplicated 月废/月囚 text.
"""
from __future__ import annotations
import json
from pathlib import Path
from .health_severity_v28 import analyze_health_severity_v28
from .health_severity_v22 import _find_star,_find_heaven_stem,_palace,FORBIDDEN_CUSTOMER
from .health_severity_v27 import _directed

TEMPLATE=Path(__file__).resolve().parents[2]/"data/knowledge/phrase_library/health_v29/severity_fixed_template.json"

def analyze_health_severity_v29(*,chart,inquiry,calendar=None,db_path=None):
    old=analyze_health_severity_v28(chart=chart,inquiry=inquiry,calendar=calendar,db_path=db_path)
    pack=json.loads(TEMPLATE.read_text("utf8"))
    if len(pack["sections"])!=11:
        raise ValueError("Complete immutable 11-part V29 template required")
    doc,_=_find_star(chart,"天心星")
    med=_find_heaven_stem(chart,"乙")
    ill,_=_find_star(chart,"天芮星")
    if med is None:raise ValueError("No Yi medicine palace")
    timing=old["audit"]["medical_timing_v28"]
    # Monthly facts have already been stated once. Remaining limitations must
    # reference independent portal/emptiness/tomb/striking evidence only.
    other=[x for x in timing["limits"] if not x.startswith(("天心月","乙奇月"))]
    slots={
      "doctor_palace":_palace(doc),"medicine_palace":_palace(med),
      "doctor_month_stage":timing["doc_month"],"medicine_month_stage":timing["yi_month"],
      "doctor_strength_judgement":"医生象"+timing["doctor_meaning"],
      "medicine_strength_judgement":"医药象"+timing["yi_meaning"],
      "doctor_effect":_directed(doc,ill,"doctor"),
      "medicine_effect":_directed(med,ill,"medicine"),
      "medical_obstacles":("；"+"；".join(other[:4])) if other else ""
    }
    template=next(x for x in pack["sections"] if x["id"]=="07_medicine")
    text=template["format"].format_map(slots)
    if any(word in text for word in tuple(FORBIDDEN_CUSTOMER)+tuple(pack["validation"]["no_tokens"])):
        raise ValueError("V29 fixed customer template invalid")
    if "{" in text or "}" in text:
        raise ValueError("V29 unresolved static slot")
    for status in ("天心月废","天心月囚","乙奇月囚","乙奇月死"):
        if text.count(status)>1:raise ValueError("Repeated monthly strength statement: "+status)
    result=[]
    for section in old["sections"]:
        result.append({**section,"text":text} if section["id"]=="07_medicine" else section)
    audit={**old["audit"],"v28_original_unchanged":True,
           "v29_no_duplicate_medical_month_state":True,
           "runtime_gpt_calls":0,"runtime_network_calls":0,
           "user_review_status":"pending"}
    return {**old,"schema":pack["schema"],
            "sections":result,"reading_text":"\n\n".join(x["title"]+"："+x["text"] for x in result),
            "audit":audit,"user_accepted":False}
