"""Source-grounded Chapter 6 research methods layered on earlier WenguaApp facts.

No inference result here is a prediction; all methods remain draft.
Do not use birth relationships to silently replace the querent (日干).
"""
from __future__ import annotations
import json
from functools import lru_cache
from pathlib import Path
from .core import cycle60
from .semantic_lookup import GUAS,STAR_ELEMENT,GENERATES,CONTROLS

ROOT=Path(__file__).resolve().parents[2]
INDEX=ROOT/"data/knowledge/shenqi/application_overview_ch06/method_index.json"
INNER_YANG={1,8,3,4}
INNER_YIN={9,2,7,6}
SUBJECT_YONGSHEN={
    "self":("stem:日干",),
    "parent":("stem:年干",),
    "mother":("stem:年干","trigram:坤"),
    "father":("stem:年干","trigram:乾"),
    "child":("stem:时干",),
    "young_son":("stem:时干","trigram:艮"),
    "young_daughter":("stem:时干","trigram:兑"),
    "sibling":("stem:月干",),
    "older_sister":("stem:月干","trigram:巽"),
    "younger_brother":("stem:月干","trigram:艮"),
    "colleague":("stem:月干",)
}

@lru_cache(maxsize=1)
def source_index():
    obj=json.loads(INDEX.read_text(encoding="utf-8"))
    if obj.get("schema")!="wengua_shenqi_ch06_method_index_v1":
        raise ValueError("Unknown method index version")
    return obj

def count_units():
    """Do not confuse indexed states and palace-position records with temporal copies."""
    return {"state_keys":2*9*60,"outer_palace_positions_per_state":8,
            "palace_records":8*2*9*60,"repeated_full_charts_claim":"not_established",
            "logic":"18 bureau variants x 60 hour ganzhi = 1080 state keys; each has 8 outer palace positions; 8640 is not a count of separately repeated temporal whole charts"}

def yin_yang_inner_outer(dun,palace):
    if dun not in ("yang","yin") or type(palace) is not int or palace not in range(1,10):
        raise ValueError("Known yin/yang and actual palace 1..9 required")
    if palace==5:
        return {"status":"unresolved_center_palace","distance":None,
                "source_lines":[198,198]}
    inner=INNER_YANG if dun=="yang" else INNER_YIN
    near=palace in inner
    return {"status":"source_rule_candidate","zone":"inner" if near else "outer",
            "distance":"near" if near else "far","speed":"fast" if near else "slow",
            "source_lines":[198,198],"never_guarantees_event_timing":True}

def _element_relation(a,b):
    if a==b:return "equal"
    if GENERATES[a]==b:return "a_generates_b"
    if GENERATES[b]==a:return "b_generates_a"
    if CONTROLS[a]==b:return "a_controls_b"
    if CONTROLS[b]==a:return "b_controls_a"
    raise ValueError("Unknown five-element relation")

def horizontal_between_palaces(left,right):
    """Cross-palace stems/doors/stars compare the two PALACES' five elements."""
    if type(left) is not int or type(right) is not int or left not in GUAS or right not in GUAS:
        raise ValueError("Missing known palace")
    return {"status":"source_rule_candidate","left_palace":left,"right_palace":right,
            "relation":_element_relation(GUAS[left][1],GUAS[right][1]),
            "based_on":"palace_elements_not_intrinsic_symbol_elements",
            "source_lines":[194,194]}

def vertical_star_palace(star,palace):
    """Within one palace use actual star five element versus this palace."""
    if star not in STAR_ELEMENT or type(palace) is not int or palace not in GUAS:
        raise ValueError("Known star and palace required")
    if palace==5:
        return {"status":"unresolved_center_star_host","source_lines":[196,196]}
    return {"status":"source_rule_candidate","relation":_element_relation(STAR_ELEMENT[star],GUAS[palace][1]),
            "star_element":STAR_ELEMENT[star],"palace_element":GUAS[palace][1],
            "source_lines":[196,196]}

def five_no_encounter(day_stem,hour_ganzhi):
    if not isinstance(day_stem,str) or day_stem not in "甲乙丙丁戊己庚辛壬癸" or hour_ganzhi not in cycle60():
        raise ValueError("Trusted day stem and actual sexagenary hour required")
    entries=source_index()["five_no_encounter"]
    matching=[x for x in entries if x["day_stem"]==day_stem and x["hour_ganzhi"]==hour_ganzhi]
    return {"status":"source_rule_candidate","matches":matching,
            "is_five_no_encounter":bool(matching),
            "real_world_outcome":"not_established"}

def host_guest_hour(hour_ganzhi):
    if hour_ganzhi not in cycle60():raise ValueError("Valid hour ganzhi required")
    stem=hour_ganzhi[0]
    return {"status":"source_rule_candidate",
            "preferred_traditional_role":"guest" if stem in "甲乙丙丁戊" else "host",
            "hour_stem":stem,"source_lines":[98,100],
            "caveat":"Other formation and strength evidence may qualify this tendency"}

def _matching_domain(domain):
    x=source_index()["yongshen_candidates"]
    return [r for r in x if r["domain"] in (domain,"general")]

def yongshen_candidates(domain,subject_relation,*,birth_year_known=False):
    if not isinstance(domain,str) or not domain:
        raise ValueError("Topic required; do not guess from vague natural language")
    if subject_relation not in SUBJECT_YONGSHEN:
        return {"status":"needs_explicit_subject_relationship",
                "relation":subject_relation,"candidates":[]}
    chosen=SUBJECT_YONGSHEN[subject_relation]
    # Distinguish the actual person about whom the inquiry is made from the
    # questioner. Do not use both day stem and unrelated period stems as subject.
    relevant=[r for r in source_index()["yongshen_candidates"]
             if r["domain"] in (domain,"general","general_personal")]
    if domain=="health":
        relevant+=[r for r in source_index()["yongshen_candidates"] if r["domain"]=="health"]
    relevant_ids={r["symbol_concept_id"] for r in relevant}
    if birth_year_known:relevant_ids.add("stem:年命")
    return {"status":"draft_yongshen_research_candidates",
            "subject_role":subject_relation,"subject_symbols":list(chosen),
            "questioner_symbol":"stem:日干",
            "supporting_domain_candidates":relevant,
            "reference_symbols":sorted(relevant_ids),
            "birth_year_used":bool(birth_year_known),
            "caveat":"Subject relation controls the primary personal role; reference symbols are not automatically applicable"}

def timing_candidate_requirements(available_fields):
    if not isinstance(available_fields,(tuple,set,list)):
        raise ValueError("Explicit set of verified chart facts required")
    available=set(available_fields)
    data=source_index()["timing_candidates"]
    out=[]
    for row in data:
        missing=[x for x in row["requires"] if x not in available]
        out.append({"concept_id":row["concept_id"],"source_lines":row["source_lines"],
                    "requirements_satisfied":not missing,"missing":missing,
                    "approved_for_specific_date":False})
    return {"status":"research_timing_only","methods":out,
            "specific_calendar_date":None,
            "must_select_relevant_method_and_granularity":True}
