"""Query source-indexed symbolic relations, independently of generation/AI.

All returns are cultural/source-extraction candidates, not final predictions.
"""
from __future__ import annotations
from collections import Counter
from functools import lru_cache
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
DATA=ROOT/"data/knowledge/shenqi/shijia_symbols_ch04/relations_and_lifecycle.json"
SYMMETRIC={"stem_combine","stem_clash","branch_clash","branch_harm",
           "branch_six_harmony","branch_three_meeting","branch_three_harmony"}
DIRECTED={"branch_punishment","branch_self_punishment"}

@lru_cache(maxsize=1)
def _data():
    result=json.loads(DATA.read_text(encoding="utf-8"))
    if result.get("schema")!="wengua_shenqi_symbol_relations_v1":
        raise ValueError("Unknown symbolic relationship data")
    return result

def related(kind, members):
    """Return all exact candidates; only symmetric types allow reordering.

    A 3-member punishment cycle is directional in the original text; callers
    cannot quietly invert the rule to obtain a desired conclusion.
    """
    if not isinstance(members,(tuple,list)) or not members or any(not isinstance(x,str) for x in members):
        raise ValueError("Specify complete symbol membership")
    if kind not in SYMMETRIC|DIRECTED:
        raise ValueError("Unsupported relation kind")
    m=tuple(members)
    found=[]
    for row in _data()["relations"]:
        if row["kind"]!=kind:continue
        target=tuple(row["members"])
        if kind in SYMMETRIC:
            match=Counter(m)==Counter(target)
        elif kind=="branch_punishment" and row.get("attributes",{}).get("mutual"):
            match=Counter(m)==Counter(target)
        elif kind=="branch_punishment" and row.get("attributes",{}).get("directed_cycle"):
            match=len(m)==3 and m in (target,target[1:]+target[:1],target[2:]+target[:2])
        else:
            match=m==target
        if match:found.append(row)
    return found

def stem_stage(stem,stage):
    if stage not in ("长生","帝旺","死","墓","绝"):
        raise ValueError("Unknown source stage")
    for row in _data()["stem_life_stages"]:
        if row["stem"]==stem:
            return {"status":"draft_source_fact","branch":row["stages"][stage],
                    "source_lines":row["source_lines"],"stem":stem,"stage":stage}
    raise ValueError("Unknown heavenly stem")

def door_season(door,season):
    if door.endswith("门"):door=door[:-1]
    row=next((x for x in _data()["door_seasons"] if x["door"]==door),None)
    if row is None:raise ValueError("Unknown eight door")
    stages=[stage for stage,values in row["seasonal_states"].items() if season in values]
    if len(stages)>1:raise ValueError("Contradictory original season stages")
    return {"status":"draft_source_fact" if stages else "unspecified_in_original",
            "door":door,"season":season,"stage":stages[0] if stages else None,
            "source_lines":row["source_lines"]}
