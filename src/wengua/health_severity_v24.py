"""V2.4 accurate father-year role and six-disease-palace merged prose.

All rendering is pure deterministic Python str.format_map of actual local
casting+book SQLite facts. No GPT, no network, no model-driven rewriting.
The other four health topic templates are UNAPPROVED and not accessed.
"""
from __future__ import annotations

import json
from pathlib import Path

from .health_severity_v22 import (
    analyze_health_severity_v22, _find_star, _body, _relation, _palace,
    _qualified, _door_detail, _meaning_stem, _meaning_door,
    _meaning_deity, _read, FORBIDDEN_CUSTOMER, SHENQI
)
from .health_dynamic_v21 import bind_patient
from .marriage_runtime import ELEMENTS,element_relation

ROOT=Path(__file__).resolve().parents[2]
TEMPLATE=ROOT/"data/knowledge/phrase_library/health_v24/severity_father_corrected_template.json"
SKIPPED={"04_illness_star","05_body_part","08_stem_pair","09_formations","10_deity","11_door"}
DIRECTIONS={
    "克":"病星受落宫克制",
    "生":"病星得落宫生扶",
    "比和":"宫星同气",
    "受生":"病星生扶落宫",
    "受克":"病星克制落宫",
}


def _illness_group(chart,base,pack):
    ill,carrier=_find_star(chart,"天芮星")
    body=_read(SHENQI)
    surface,internal=_body(body,ill["palace"])
    pair=base["audit"]["stem_pair_source"]
    if pair["id"]!="heaven_over_earth:"+carrier["carried_stem"]+":"+ill["earth_stem"]:
        raise ValueError("Stem pair source does not correspond to actual illness palace")
    others=[x["star"] for x in ill["heaven_stars"] if x["star"]!="天芮星"]
    other_star="与"+"、".join(others)+"同" if others else "独"
    rel=element_relation(ELEMENTS[ill["palace"]],"土")
    door_rel=_door_detail(ill)
    pressure=base["audit"]["actual_door_press_palaces"]
    if ill["palace"] in pressure:
        pressured="病宫"+ill["door"]+"形成门迫"
    else:
        pressured="病宫"+ill["door"]+"不成门迫"
    elsewhere=[chart["palaces"][str(x)] for x in pressure if x!=ill["palace"]]
    if elsewhere:
        pressured+="；另有"+"、".join(_palace(x)+x["door"] for x in elsewhere)+"形成门迫"
    near={
        "死门":"天芮与死门同宫，疾病、闭塞之象相连",
        "生门":"天芮与生门同宫，病星与生机之象并现",
        "休门":"天芮与休门同宫，病星与调养之象并现",
        "开门":"天芮与开门同宫，病星与开启之象并现",
    }.get(ill["door"],"天芮与"+ill["door"]+"同宫，"+_meaning_door(ill["door"])+"之象相连")
    if pair["category"]=="source_named_obstruction":
        near+="；"+pair["name"]+"主纠缠难安"
    slots={
        "other_stars":other_star,
        "palace":_palace(ill),"palace_element":ELEMENTS[ill["palace"]],
        "heaven_stem":carrier["carried_stem"],"earth_stem":ill["earth_stem"],
        "door":ill["door"],"deity":ill["deity"],
        "star_palace_relation":_palace(ill)+"属"+ELEMENTS[ill["palace"]]+"，"+DIRECTIONS[rel],
        "surface":surface,"internal":internal,
        "heaven_meaning":_meaning_stem(carrier["carried_stem"],chart,ill),
        "earth_meaning":_meaning_stem(ill["earth_stem"],chart,ill),
        "pair_name":pair["name"],"pair_meaning":pair["short"],
        "door_meaning":_meaning_door(ill["door"]),
        "deity_meaning":_meaning_deity(ill["deity"]),
        "door_palace_relation":door_rel,
        "palace_pressure":pressured,
        "combined_symbol_meaning":near
    }
    if pair["category"]=="source_named_general" and carrier["carried_stem"]==ill["earth_stem"]:
        slots["pair_meaning"]="天盘地盘均为"+carrier["carried_stem"]+"，"+_meaning_stem(carrier["carried_stem"],chart,ill)+"之象重见"
    text=pack["group"]["format"].format_map(slots)
    return {"id":pack["group"]["id"],"title":pack["group"]["title"],"text":text}


def _father_auxiliary(chart,inquiry,calendar,pack):
    if inquiry["relationship"]!="father":
        return None
    role=bind_patient(chart,inquiry,calendar)
    matches=[c for c in role["extra_cells"] if c["palace"]==6]
    if len(matches)!=1:
        raise ValueError("Father requires exactly one source-backed Qian-6 reference")
    father=matches[0]
    ill,_=_find_star(chart,"天芮星")
    suffix=_relation(father,ill,"父亲乾宫","病宫")
    slots={
        "father_palace":_palace(father),
        "father_contents":_qualified(father),
        "father_door":father["door"],
        "father_door_meaning":_meaning_door(father["door"]),
        "father_deity":father["deity"],
        "father_deity_meaning":_meaning_deity(father["deity"]),
        "father_relation":suffix,
    }
    return {key:value.format_map(slots) for key,value in pack["father_aux"].items()}


def _father_accurate_prose(chart,inquiry,calendar,pack,base):
    """Compute father patient/auxiliary from THIS chart, without GPT."""
    from .health_severity_v22 import (
        _yes_void, _find_heaven_stem, _phase_from_chart)
    role=bind_patient(chart,inquiry,calendar)
    person=role["main_cell"]
    aux=next((c for c in role["extra_cells"] if c["palace"]==6),None)
    if not person or not aux or role["stem"]!=calendar.get("year_ganzhi","")[:1]:
        raise ValueError("Father's year-stem and Qian palace must both be valid")
    ill,_=_find_star(chart,"天芮星")
    doctor,_=_find_star(chart,"天心星")
    yi=_find_heaven_stem(chart,"乙")
    if not yi:
        raise ValueError("Medicine stem cannot be silently dropped")
    pair=base["audit"]["stem_pair_source"]
    others="、".join(v["star"] for v in ill["heaven_stars"] if v["star"]!="天芮星")
    month=calendar.get("month_branch")
    stage=_phase_from_chart(ill,month)
    pr=element_relation(ELEMENTS[ill["palace"]],"土")
    star_edge=(
      _palace(ill)+"属土，与天芮土比和，宫星同气"
      if pr=="比和" else
      _palace(ill)+"属"+ELEMENTS[ill["palace"]]+"，克天芮土，病星受制"
      if pr=="克" else
      _palace(ill)+"与天芮有"+pr+"关系")
    person_void=_yes_void(chart,person)
    patient_empty=(_palace(person)+"逢空亡，"+person["door"]+"吉象受虚"
                   if person_void else
                   _palace(person)+"不逢空亡")
    rel_doc=_relation(doctor,ill,"天心宫","病宫")
    rel_yi=_relation(yi,ill,"乙奇宫","病宫")
    if stage in ("旺","相") and ill["door"]=="死门" and person_void:
        judgement=("病星月令有气并临死门，父亲用神宫逢空，病困象偏重；"
                   "但"+person["door"]+"主"+_meaning_door(person["door"])+
                   "，天心与乙奇仍有各自的五行关系，吉凶交见，不能只凭死门断极凶")
    elif stage in ("旺","相") and ill["door"]=="死门":
        judgement=("病星月令有气且临死门，传统病象偏滞；"
                   "父亲用神、乾宫与医药宫仍有相互生克，吉凶需合参")
    elif ill["door"] in ("生门","休门","开门"):
        judgement=("病星与"+ill["door"]+"同宫，兼看父亲用神、乾宫及医药宫的生克，"
                    "此盘传统吉凶象并见")
    else:
        judgement=("依据病星、父亲年干用神及乾宫医药关系合参，"
                    "不能单由一门决定病情")
    birth=inquiry.get("patient_birth_ganzhi") or inquiry.get("subject_year_ganzhi")
    slots={
      "year_stem":role["stem"],"person_palace":_palace(person),
      "person_contents":_qualified(person),"person_door":person["door"],
      "person_door_meaning":_meaning_door(person["door"]),
      "person_deity":person["deity"],"person_deity_meaning":_meaning_deity(person["deity"]),
      "person_relation":_relation(person,ill,"父亲年干宫","病宫"),
      "person_void":patient_empty,
      "aux_contents":_qualified(aux),
      "aux_relation":_relation(aux,ill,"父亲乾宫","病宫"),
      "ill_palace":_palace(ill),"ill_door":ill["door"],
      "ill_deity":ill["deity"],
      "other_stars":others or "同宫诸星",
      "pair_name":pair["name"],
      "month_branch":month or "本",
      "ill_stage":stage or "未定",
      "star_edge":star_edge,
      "doctor_relation":rel_doc,"yi_relation":rel_yi,
      "decision":judgement,"time_sentence":"此盘不定具体应期",
      "birth_line":("另参父亲出生年命"+birth if birth else
                    "未提供出生年命，本次不取年命"),
    }
    return {
      "01_question":pack["father_intro"].format_map(slots),
      "13_patient":pack["father_patient"].format_map(slots),
      "21_summary":pack["father_summary"].format_map(slots),
    }


def analyze_health_severity_v24(*,chart,inquiry,calendar=None,db_path=None):
    """16 user-visible paragraphs, preserving all 21 original calculation facets."""
    if inquiry.get("intent")!="severity":
        raise ValueError("Other four health domains remain unreviewed and blocked")
    # Reuse existing factual evaluator; no free-text regeneration.
    base=analyze_health_severity_v22(
        chart=chart,inquiry=inquiry,calendar=calendar,db_path=db_path)
    pack=_read(TEMPLATE)
    expected=set(pack["group"]["source_ids"])
    if expected!=SKIPPED or len(base["sections"])!=21:
        raise ValueError("Six same-palace sources must all be retained")
    group=_illness_group(chart,base,pack)
    aux=_father_auxiliary(chart,inquiry,calendar or {},pack)
    father_prose=(_father_accurate_prose(chart,inquiry,calendar or {},pack,base)
                  if inquiry["relationship"]=="father" else {})
    output=[]
    for item in base["sections"]:
        if item["id"]=="04_illness_star":
            output.append(group)
        elif item["id"] in SKIPPED:
            continue
        else:
            value=dict(item)
            if value["id"] in father_prose:
                value["text"]=father_prose[value["id"]]
            elif aux:
                if value["id"]=="13_patient":
                    value["text"]+="。"+aux["full"]
                elif value["id"]=="19_counter":
                    value["text"]+="。"+aux["evidence"]
                elif value["id"]=="21_summary":
                    value["text"]+="。"+aux["summary"]
            output.append(value)
    if len(output)!=16:
        raise AssertionError("6 existing sections replaced with one => 16")
    if len({x["id"] for x in output})!=16:
        raise AssertionError("Duplicated visible section")
    for x in output:
        if any(token in x["text"] for token in FORBIDDEN_CUSTOMER):
            raise ValueError("Customer-facing engineering message leaked")
        if "{" in x["text"] or "}" in x["text"]:
            raise ValueError("Unresolved offline template slot")
    rendered="\n\n".join(x["title"]+"："+x["text"] for x in output)
    audit=dict(base["audit"])
    audit.update({
        "effective_summary_uses_father_conditions":bool(father_prose),
        "previous_generic_v22_summary_reused":False if father_prose else True,
        "display_group_sources":list(pack["group"]["source_ids"]),
        "internal_original_sections":base["sections"],
        "original_facts_retained":21,
        "visible_paragraphs":16,
        "merged_disease_palace_facts":6,
        "no_gpt_network_or_rewrite":True,
        "father_qian_auxiliary_included":bool(aux),
        "user_acceptance":"pending"
    })
    return {
        "schema":pack["schema"],"domain":"health","intent":"severity",
        "status":"offline_grouped_prose_pending_user_review",
        "sections":output,"reading_text":rendered,
        "audit":audit,
        "provenance":base["source_provenance"]
    }
