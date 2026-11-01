"""Research-only traditional body-location sector and evidence precedence.

This module selects a classical body-map branch, not an actual illness organ.
It is independent of frozen V8 severity scoring and the iOS production router.
"""
from __future__ import annotations
import json
from functools import lru_cache
from pathlib import Path
from typing import Mapping, Any

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/"data/knowledge/health_discomfort/inner_outer_priority_policy_20261031.json"
SCHEMA="health_discomfort_inner_outer_v12_source_linked_20261031"
RING=set((1,2,3,4,6,7,8,9))


@lru_cache(maxsize=1)
def policy():
    data=json.loads(SOURCE.read_text(encoding="utf8"))
    if (data.get("schema")!=SCHEMA or data.get("status")!="research_draft_not_enabled"
        or set(data.get("inner_by_dun",{}))!={"yang","yin"}
        or set(data.get("outer_by_dun",{}))!={"yang","yin"}
        or not data.get("source") or not all(data.get("exceptions",{}).values())):
        raise ValueError("Unverified traditional location rule source")
    for dun in ("yang","yin"):
        a=set(data["inner_by_dun"][dun])
        b=set(data["outer_by_dun"][dun])
        if len(a)!=4 or len(b)!=4 or (a&b) or a|b!=RING:
            raise ValueError("Eight actual palaces must partition into two rings")
    if (set(data["inner_by_dun"]["yang"])!=set(data["outer_by_dun"]["yin"])
        or set(data["inner_by_dun"]["yin"])!=set(data["outer_by_dun"]["yang"])):
        raise ValueError("Yin and Yang must invert actual body-map branch")
    return data


def classify(*,dun:str,palace:int):
    p=policy()
    if dun not in ("yin","yang") or type(palace)!=int or palace not in RING:
        raise ValueError("No nonphysical middle palace or unknown dun")
    sector="inner" if palace in p["inner_by_dun"][dun] else "outer"
    return {"sector":sector,"label":"体内" if sector=="inner" else "体表",
            "opposite":"体表" if sector=="inner" else "体内",
            "source_state":"user_rule_book_case_crosschecked_not_diagnostic"}


def inspect_priority(*,chart:Mapping[str,Any],body:Mapping[str,Any],
                     patient_palace:int,hour_palace:int,injury_palace:int):
    if (chart.get("school_id")!="shijia_zhuanpan"
        or chart.get("casting_variant")!="shenqi_book_explicit_bureau_v1"
        or not isinstance(chart.get("palaces"),dict)
        or set(chart["palaces"])!={str(i) for i in range(1,10)}):
        raise ValueError("Actual nine-palace source chart required")
    ill=body["tianrui_palace"]
    if any(type(p)!=int or p not in RING for p in
           (ill,patient_palace,hour_palace,injury_palace)):
        raise ValueError("Real noncentral palace required for each selected role")
    cell=chart["palaces"][str(ill)]
    real=[s for s in cell["heaven_stars"] if s["star"]=="天芮星"]
    if (len(real)!=1 or real[0]["carried_stem"]!=body["tianrui_carried_stem"]
        or chart["palaces"][str(injury_palace)]["door"]!="伤门"):
        raise ValueError("Tianrui or actual injury door source is inconsistent")
    sector=classify(dun=chart["dun"],palace=ill)
    chosen=list(body["internal_symbol_candidates"] if sector["sector"]=="inner"
                else body["surface_symbol_candidates"])
    alternate=list(body["surface_symbol_candidates"] if sector["sector"]=="inner"
                   else body["internal_symbol_candidates"])
    if not chosen or not alternate:raise ValueError("Both source body groups required")
    cond=policy()["modality"]
    candidates=[]
    for kind,symbol,outerkey,innerkey in (
        ("door",cell["door"],"outer_door","inner_door"),
        ("deity",cell["deity"],"outer_deity","inner_deity"),
        ("sky_stem",real[0]["carried_stem"],"outer_stem","inner_stem")):
        tendency=("outer" if symbol in cond[outerkey] else
                  "inner" if symbol in cond[innerkey] else None)
        if tendency:
            candidates.append({
                "kind":kind,"symbol":symbol,"palace":ill,"tendency":tendency,
                "agreement":"supports" if tendency==sector["sector"] else "conflicts",
                "source_status":"user_candidate_not_absolute"})
    return {**sector,"tianrui_palace":ill,"focus_candidates":chosen,
            "alternative_candidates":alternate,
            "actual_sky_stem":real[0]["carried_stem"],"actual_earth_stem":cell["earth_stem"],
            "illness_door":cell["door"],"illness_deity":cell["deity"],
            "companion_stem":next((s["carried_stem"] for s in cell["heaven_stars"]
                                  if s["star"]=="天禽星"),None),
            "modal_evidence":candidates,
            "counterevidence":[x for x in candidates if x["agreement"]=="conflicts"],
            "patient_palace":patient_palace,"hour_palace":hour_palace,
            "injury_palace":injury_palace,
            "one_organ_confirmed":False,"medical_diagnosis":None,
            "health_outcome":None,"v80_score":None,
            "new_old_status":None,"source_plane_convention_only":True}
