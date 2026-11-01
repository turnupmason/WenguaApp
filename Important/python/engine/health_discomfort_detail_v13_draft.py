"""V13 additional *traditional* location evidence, not medical diagnosis.

Reads the real two carried stars and physical earth plate separately, plus
independent patient versus Tianrui door semantics. Source is an unverified
user compilation, so it cannot override the book body map or frozen V8.
"""
from __future__ import annotations
from functools import lru_cache
import json
from pathlib import Path
from typing import Any, Mapping
from .health_discomfort_location_draft import load_traditional_location_candidates

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/"data/knowledge/health_discomfort/body_location_condition_detail_v13_20261101.json"
SCHEMA="wengua_health_discomfort_v13_condition_detail_20261101"
PALACES=frozenset((1,2,3,4,6,7,8,9))


@lru_cache(maxsize=1)
def detail_policy() -> dict[str,Any]:
    doc=json.loads(SOURCE.read_text(encoding="utf8"))
    if (doc.get("schema")!=SCHEMA or doc.get("topic_id")!="health.discomfort"
        or doc.get("status")!="research_draft_not_public"
        or doc.get("source",{}).get("book_id") is not None
        or len(doc.get("carrier_precedence",()))!=3
        or tuple(x.get("role") for x in doc["carrier_precedence"])!=
        ("tianrui_sky","tianqin_sky","illness_earth")
        or not doc.get("source_conflicts")
        or any(value is not False for key,value in doc.get("public_gate",{}).items()
               if key not in ("need_native_swift_parity","need_independent_book_case_review"))
        or any(doc["public_gate"].get(key) is not True for key in
               ("need_native_swift_parity","need_independent_book_case_review"))):
        raise ValueError("Invalid unapproved V13 body detail source")
    regions=doc["body_axis"]
    all_physical=[]
    for name,expected in (("upper",{9,4,2}),("middle",{3,7}),
                          ("lower",{8,1,6})):
        if set(regions[name]["palaces"])!=expected:
            raise ValueError("Unverified physical body region map")
        all_physical.extend(regions[name]["palaces"])
    if len(all_physical)!=8 or set(all_physical)!=PALACES:
        raise ValueError("Body region covers eight physical palaces exactly")
    if regions["middle"].get("symbolic_centre")!=5:
        raise ValueError("Centre five is a symbolic location only")
    return doc


def inspect_detail(*,chart:Mapping[str,Any],illness_palace:int,
                   patient_cell:Mapping[str,Any],location:Mapping[str,Any],
                   patient_sex:str|None=None,
                   patient_age_group:str|None=None) -> dict[str,Any]:
    """Only evidence with an actual symbol, actual role and source provenance."""
    doc=detail_policy()
    palaces=chart.get("palaces")
    if (not isinstance(palaces,dict)
        or set(palaces)!={str(i) for i in range(1,10)}
        or type(illness_palace) is not int or illness_palace not in PALACES
        or location.get("tianrui_palace")!=illness_palace
        or patient_cell.get("palace") not in PALACES
        or patient_sex not in (None,"male","female")
        or patient_age_group not in (None,"young","adult","elder")):
        raise ValueError("Real patient, actual Tianrui and nine palaces required")
    site=palaces[str(illness_palace)]
    if (site["palace"]!=illness_palace
        or palaces[str(patient_cell["palace"])]["door"]!=patient_cell["door"]):
        raise ValueError("Actual role door was not read from the actual palace")
    sky=[s["carried_stem"] for s in site["heaven_stars"]
         if s["star"]=="天芮星"]
    bird=[s["carried_stem"] for s in site["heaven_stars"]
          if s["star"]=="天禽星"]
    if (len(sky)!=1 or len(bird)>1
        or sky[0]!=location.get("actual_sky_stem")
        or (bird[0] if bird else None)!=location.get("companion_stem")
        or site["earth_stem"]!=location.get("actual_earth_stem")):
        raise ValueError("True sky/earth carrier evidence inconsistent")
    region=next(k for k,v in doc["body_axis"].items()
                if isinstance(v,dict) and illness_palace in v.get("palaces",[]))
    notes=load_traditional_location_candidates()
    illness_door=site["door"]
    patient_door=patient_cell["door"]
    illness_deity=site["deity"]
    if (illness_door not in notes["doors"] or patient_door not in notes["doors"]
        or illness_deity not in notes["deities"]):
        raise ValueError("Cannot invent or transfer door or deity")
    # The earth plate may be a clue in the user notes *when* a verified
    # month/rest-prison source predicate exists. It currently does not.
    carriers=[
        {"role":"tianrui_sky","symbol":sky[0],"physical_palace":illness_palace,
         "rank":1,"conditional_eligible":True},
        {"role":"tianqin_sky","symbol":bird[0] if bird else None,
         "physical_palace":illness_palace,"rank":2,
         "conditional_eligible":bool(bird)},
        {"role":"illness_earth","symbol":site["earth_stem"],
         "physical_palace":illness_palace,"rank":3,
         "conditional_eligible":False,
         "missing_condition":"source_verified_earth_rest_or_prison_and_month"},
    ]
    # Kun two may host the centre earth stem for the second 81 pair.
    # The physical centre is not a place with ordinary stars/door/deity.
    host_earth=(palaces["5"]["earth_stem"] if illness_palace==2 else None)
    # Additional sex/age refinements remain named, unapproved *candidates*.
    # Never silently infer a sex or age, and never map a candidate to a disease.
    conditional=[]
    if illness_palace==6 and patient_age_group in ("young","elder"):
        conditional.append({"id":"qian_age_subtypes",
                            "observed":patient_age_group,
                            "status":"unverified_candidate"})
    if illness_palace==1 and patient_sex=="male":
        conditional.append({"id":"male_tianrui_kan","observed":"male",
                            "status":"unverified_candidate"})
    if illness_palace==7 and sky[0] in ("壬","癸") and patient_sex:
        conditional.append({"id":"gender_ren_gui_dui",
                            "observed":patient_sex,"status":"unverified_candidate"})
    if illness_palace in (3,7):
        conditional.append({"id":"zhen_dui_front_back",
                            "observed":"candidate_front" if illness_palace==3
                                       else "candidate_back",
                            "status":"unverified_candidate"})
    if illness_door=="伤门":
        conditional.append({"id":"tianrui_shangmen_injury",
                            "observed":"actual_same_palace",
                            "status":"unverified_candidate"})
    return {
        "schema":SCHEMA,"source_status":doc["status"],
        "anatomical_region":region,
        "anatomical_region_zh":{"upper":"上部","middle":"中部",
                                "lower":"下部"}[region],
        "symbolic_centre_only":5,
        "carriers":carriers,
        "kun_centre_host_earth_stem":host_earth,
        "illness_door":illness_door,"patient_door":patient_door,
        "illness_door_meaning":notes["doors"][illness_door]["illness"],
        "patient_door_meaning":notes["doors"][patient_door]["patient"],
        "illness_deity":illness_deity,
        "illness_deity_meaning":notes["deities"][illness_deity]["illness"],
        "different_door_roles":True,
        "patient_sex_resolved":patient_sex,
        "conditional_signals":conditional,
        "patient_age_group_explicit":patient_age_group,
        "user_age_specific_location_selected":False,
        "illness_duration": {
            "candidate_from_sector":doc["disease_duration"][location["sector"]]["candidate"],
            "source_status":"unverified_user_generalization",
            "new_or_old_determined":False,
            "customer_phrase_allowed":False,
        },
        "sky_earth_pair":(sky[0],site["earth_stem"]),
        "combined_disease_confirmed":False,
        "true_medical_diagnosis":None,
        "severity_or_death_result":None,
    }
