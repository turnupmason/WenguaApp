"""V3.1 immutable incremental correction: patient↔hour disease direction.

V3.0 archive and sealed readouts are preserved as a failed-but-audited
research step. V3.1 changes only the exact hourly patient relationship
through a new literal fixed template, not by GPT rewriting predictions.
"""
from __future__ import annotations
import json
from pathlib import Path
from .health_severity_v30 import analyze_health_severity_v30
from .health_severity_v29 import analyze_health_severity_v29
from .health_severity_v22 import _find_heaven_stem,FORBIDDEN_CUSTOMER
from .health_dynamic_v21 import bind_patient
from .health_severity_v26 import _direction
from .health_severity_v27 import _clinical_role_sign
from .marriage_runtime import ELEMENTS,element_relation

ROOT=Path(__file__).resolve().parents[2]
TEMPLATE=ROOT/"data/knowledge/phrase_library/health_v31/severity_fixed_template.json"

def patient_vs_disease_hour_relation(chart,person):
    event=_find_heaven_stem(chart,chart["hour_ganzhi"][0])
    if not event:raise ValueError("Current hour stem must have a real chart palace")
    relation=element_relation(ELEMENTS[person["palace"]],ELEMENTS[event["palace"]])
    text=_direction(person,event,"患者宫","时干病事宫")
    interpretation=_clinical_role_sign("patient",relation).replace("病宫","时干病事宫")
    return {"relation":relation,"source_palace":person["palace"],
            "event_palace":event["palace"],"text":text,
            "significance":interpretation,
            "source_rule":"user_2026_10_22_日干为人时干病，人克病兮可去瘥，病克人兮忧险应"}

def analyze_health_severity_v31(*,chart,inquiry,calendar=None,db_path=None):
    if inquiry.get("intent")!="severity":
        raise ValueError("Other four user-unapproved health subintents must not run")
    v30=analyze_health_severity_v30(chart=chart,inquiry=inquiry,calendar=calendar,db_path=db_path)
    # The older bad V3.0 Section-08 sentence is not copied into V3.1.
    v29=analyze_health_severity_v29(chart=chart,inquiry=inquiry,calendar=calendar,db_path=db_path)
    original=next(x["text"] for x in v29["sections"] if x["id"]=="08_hour")
    person=bind_patient(chart,inquiry,calendar)["main_cell"]
    if person is None:raise ValueError("Cannot interpret a missing patient")
    direction=patient_vs_disease_hour_relation(chart,person)
    templates=json.loads(TEMPLATE.read_text("utf8"))
    if len(templates["sections"])!=11:raise ValueError("Missing complete source template")
    fmt=next(x["format"] for x in templates["sections"] if x["id"]=="08_hour")
    new=fmt.format_map({
        "v29_original_hour":original.rstrip("。"),
        "actual_patient_vs_hour":direction["text"],
        "health_direction_verdict":direction["significance"]})
    bad=tuple(FORBIDDEN_CUSTOMER)+tuple(templates["validation"]["no_tokens"])
    if any(x in new for x in bad) or "{" in new or "}" in new or "。。" in new:
        raise ValueError("Invalid customer-facing v31 temporal relationship phrase")
    sections=[{**x,"text":new} if x["id"]=="08_hour" else x for x in v30["sections"]]
    audit={**v30["audit"],"v30_original_readout_unchanged":True,
           "v31_patient_hour_direction":direction,
           "v31_used_actual_patient_and_actual_hour":True,
           "v31_used_correct_health_specific_sign":True,
           "user_content_accepted":False,
           "runtime_gpt_calls":0,"runtime_network_calls":0}
    return {**v30,"schema":templates["schema"],"sections":sections,
            "reading_text":"\n\n".join(x["title"]+"："+x["text"] for x in sections),
            "audit":audit,"user_accepted":False}
