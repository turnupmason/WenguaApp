"""ACTIVE V3.9.1 HEALTH SEVERITY: real chart -> original V3.9 evidence ->
full book-verified ten-stem 12-lifecycle role facts -> SAME 11-slot customer text.

Does NOT import or run V4.0/V4.1/V4.2 symbolic scoring. Historic numeric
experiments stay in immutable old archives, but are NEVER called from here.
Customer-visible lines/SHA and all actual medical claims are forbidden.
"""
from __future__ import annotations
import json
from pathlib import Path
from .health_severity_v39 import analyze_health_severity_v39
from .health_severity_v38 import _customer_clean
from .health_lifecycle_v391 import (source_full12,all_actual_palace_stage_facts,
    stage_for_stem_at_actual_palace,stage_text)
from .health_dynamic_v21 import bind_patient
from .health_severity_v22 import _find_star,_find_heaven_stem,_palace

ROOT=Path(__file__).resolve().parents[2]
TEMPLATE=ROOT/"data/knowledge/phrase_library/health_v391/severity_text_full12_template.json"
EXTENDED=("03_illness","05_patient","07_medicine","08_hour")

def analyze_health_severity_v391(*,chart,inquiry,calendar,db_path):
    if not calendar or calendar["hour_ganzhi"]!=chart["hour_ganzhi"]:
        raise ValueError("A real calendar and matching real hour chart are required")
    cfg=json.loads(TEMPLATE.read_text("utf8"))
    if cfg["version"]!="V3.9.1" or not cfg["scoring_disabled"]:
        raise ValueError("Only source-verified, score-free V3.9.1 output is active")
    base=analyze_health_severity_v39(
        chart=chart,inquiry=inquiry,calendar=calendar,db_path=db_path)
    lookup=source_full12()
    inventory=all_actual_palace_stage_facts(chart,calendar,table=lookup)
    bound=bind_patient(chart,inquiry,calendar)
    patient=bound["main_cell"]
    ill,illstar=_find_star(chart,"天芮星")
    doc,docstar=_find_star(chart,"天心星")
    yi=_find_heaven_stem(chart,"乙")
    hour=_find_heaven_stem(chart,chart["hour_ganzhi"][0])
    if not all((patient,ill,illstar,doc,docstar,yi,hour)):
        raise ValueError("A required original-book role has no actual palace")
    patient_life=stage_for_stem_at_actual_palace(bound["stem"],patient["palace"],table=lookup)
    illness_life=stage_for_stem_at_actual_palace(illstar["carried_stem"],ill["palace"],table=lookup)
    doctor_life=stage_for_stem_at_actual_palace(docstar["carried_stem"],doc["palace"],table=lookup)
    yi_life=stage_for_stem_at_actual_palace("乙",yi["palace"],table=lookup)
    hour_life=stage_for_stem_at_actual_palace(chart["hour_ganzhi"][0],hour["palace"],table=lookup)
    already=base["audit"]["v38_actual_illness_derived_tomb_extinct_void"]
    if illness_life["has_tomb"]!=already["tomb_branch_in_illness_palace"]:
        raise ValueError("Original V3.9 illness tomb source disagrees with complete 12-cycle")
    if illness_life["has_extinction"]!=already["extinct_branch_in_illness_palace"]:
        raise ValueError("Original V3.9 illness extinction source disagrees with complete 12-cycle")
    # Existing baseline V3.9 already explains tomb/absolute separately,
    # so listing its source life stages does NOT count as another negative.
    illness_note=("这与上文的入墓、绝地是同一组宫位事实，不再另断一次。"
                  if illness_life["has_tomb"] or illness_life["has_extinction"] else
                  "此为病宫携干的盘面状态，应与天芮旺衰及医药关系合看。")
    patient_note=("本宫含两个地支，两种阶段需同时参看，不可择其一。"
                  if len(patient_life["actual_stage_facts"])==2 else
                  "此为患者用干的宫位状态，还须参看病宫生克与旬空。")
    formats=cfg["slot_extensions"]
    role=str(bound["label"]).replace("此次为","")
    context={
      "illness_stem":illstar["carried_stem"],"illness_palace":_palace(ill),
      "illness_stages":stage_text(illness_life),"illness_note":illness_note,
      "patient_identity":role,"patient_stem":bound["stem"],
      "patient_palace":_palace(patient),"patient_stages":stage_text(patient_life),
      "patient_note":patient_note,
      "doctor_stem":docstar["carried_stem"],"doctor_palace":_palace(doc),
      "doctor_stages":stage_text(doctor_life),
      "yi_palace":_palace(yi),"yi_stages":stage_text(yi_life),
      "hour_stem":chart["hour_ganzhi"][0],"hour_palace":_palace(hour),
      "hour_stages":stage_text(hour_life)}
    items=[]
    if len(base["sections"]) not in (10,11):
        raise ValueError("Expected exact V3.9 eleven-slot structure (sex may be omitted)")
    for section in base["sections"]:
        k=section["id"]
        if k not in formats:
            items.append(dict(section))
            continue
        addition=_customer_clean(formats[k].format_map(context))
        prior=section["text"]
        new=_customer_clean(prior+" "+addition)
        if not new.startswith(prior):
            raise ValueError("Cannot overwrite or paraphrase V3.9 source-qualified prose")
        items.append({**section,"text":new})
    used={x["id"] for x in items}
    if len(used&set(EXTENDED))!=4 or len(items)!=len(base["sections"]):
        raise ValueError("All four role-scoped lifecycle additions must appear within original slots")
    reading="\n\n".join(s["title"]+"："+s["text"] for s in items)
    _customer_clean(reading)
    if "100分" in reading or "健康指数" in reading or "吉凶概率" in reading:
        raise ValueError("No abandoned numerical scoring in V3.9.1 text")
    return {
      "schema":"wengua_v391_active_v39_evidence_full12_no_score",
      "version":"V3.9.1",
      "status":"candidate_user_review",
      "template":str(TEMPLATE.relative_to(ROOT)),
      "original_v39_reading":base["reading_text"],
      "original_v39_sections":base["sections"],
      "sections":items,"reading_text":reading,
      "source_chart_evidence":{
        "complete_eight_palaces_full12":inventory,
        "patient":patient_life,"illness_tianrui_heaven":illness_life,
        "doctor_tianxin_heaven":doctor_life,
        "medicine_yi":yi_life,"hour_event":hour_life,
        "roles":{"patient_palace":patient["palace"],"illness_palace":ill["palace"],
             "doctor_palace":doc["palace"],"yi_palace":yi["palace"],
             "hour_palace":hour["palace"]},
        "v39_original_book_pair_catalog_size":len(base["audit"]["v37_81_ordered_full_book_pairs"]),
        "v39_health_supplement_size":len(base["audit"]["v34_42_directional_pairs"]),
        "v39_complex_conditions_size":len(base["audit"]["v36_17_source_rechecked_composites"]),
        "v39_original_traditional_verdict":base["audit"]["v37_actual_health_priority_verdict"],
        "v39_original_unmodified":True,"all_old_numeric_scoring_disabled":True,
        "line_hash_source_provenance_audit_only":True},
      "score":None,"probability":None,"user_approved":False,
      "clinical_medical_validity":False}
