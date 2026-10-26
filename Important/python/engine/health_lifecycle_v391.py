"""No score runtime: full 10-stem x 12 lifecycle source facts for the V3.9 reader.

Derived from the FIVE original book anchor states per stem, verified at
runtime; source file itself was sealed by V4.2 but NO V4.2 scoring code,
module budgets, numeric interpretations or medical prognosis are imported.
Centre 5 does not get fabricated ordinary stars, doors or deities.
"""
from __future__ import annotations
import json
from pathlib import Path
from .symbol_relations import stem_stage
from .marriage_runtime import PALACE_BRANCHES, hourly_void_branches
ROOT=Path(__file__).resolve().parents[2]
FULL12=ROOT/"data/knowledge/score_models/health_severity_v42/twelve_life_stages_source_anchor_full.json"
ANCHORS=("长生","帝旺","死","墓","绝")

def source_full12():
    data=json.loads(FULL12.read_text("utf8"))
    if data["schema"]!="wengua_stem_full12_source_anchor_derived_v42":
        raise ValueError("Only exact verified original book 12-stage source facts permitted")
    lookup={r["stem"]:r for r in data["stem_tables"]}
    if len(lookup)!=10:raise ValueError("Ten stem source tables required")
    for stem,row in lookup.items():
        if len(row["stage_to_branch"])!=12 or len(row["branch_to_stage"])!=12:
            raise ValueError("Full twelve stage source corruption")
        for stage in ANCHORS:
            book=stem_stage(stem,stage)
            if row["stage_to_branch"][stage]!=book["branch"]:
                raise ValueError("Original book lifecycle anchor mismatch: "+stem+"/"+stage)
    return lookup

def stage_for_stem_at_actual_palace(stem,palace,*,table=None):
    book=table or source_full12()
    if palace==5 or palace not in PALACE_BRANCHES or stem not in book:
        raise ValueError("Must have actual outer palace and readable stem")
    branches=PALACE_BRANCHES[palace]
    life=[{"branch":b,"stage":book[stem]["branch_to_stage"][b]} for b in branches]
    return {"stem":stem,"palace":palace,"palace_branches":list(branches),
            "actual_stage_facts":life,"has_tomb":any(x["stage"]=="墓" for x in life),
            "has_extinction":any(x["stage"]=="绝" for x in life),
            "independent_of_month_strength":True,
            "book_5_source_anchors_verified":True}

def all_actual_palace_stage_facts(chart,calendar,*,table=None):
    lookup=table or source_full12()
    if chart["hour_ganzhi"]!=calendar["hour_ganzhi"]:
        raise ValueError("Calculated hour and chart hour differ")
    facts=[]
    for palace in range(1,10):
        if palace==5:
            c=chart["palaces"]["5"]
            if c["heaven_stars"] or c["door"] or c["deity"]:
                raise ValueError("Centre five has no invented ordinary symbols")
            continue
        c=chart["palaces"][str(palace)]
        facts.append({"palace":palace,"earth_stem":c["earth_stem"],
            "door":c["door"],"deity":c["deity"],
            "heaven":[{"star":star["star"],
                "carried_stem":star["carried_stem"],
                "lifecycle":stage_for_stem_at_actual_palace(
                    star["carried_stem"],palace,table=lookup)}
                for star in c["heaven_stars"]]})
    return {"ten_stems":10,"total_source_stages":120,
       "outer_eight_palaces":facts,"xun_void":hourly_void_branches(chart["hour_ganzhi"]),
       "source_book_anchor_checked":True}

def stage_text(x):
    return "、".join(y["branch"]+y["stage"] for y in x["actual_stage_facts"])
