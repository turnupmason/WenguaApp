"""Wengua V-next TABLE TWO: deterministic duel of two inspected factors.

TABLE ONE is inspect_strength_25: monthly state × symbol-palace relation.
TABLE TWO is a fixed 5x5 two-sided symbol comparison, fixed 5x5 palace
comparison, and fixed 3x3 outcome table. The domain decides WHICH two
signifiers to compare and WHAT favorable/adverse means. No all-palace loop.
All labels are review hypotheses, never medical efficacy or prognosis.
"""
from __future__ import annotations

from .factor_energy_25_rules import TIERS, inspect_strength_25
from .semantic_lookup import CONTROLS,GENERATES

# Fixed comparison labels: row=attacker strength, col=target strength.
# Only (大/极大) against (小/极小) is dominant. Everything else contested.
STRONG_WEAK_5X5 = {
    "极小": ("相持","相持","相持","弱","弱"),
    "小":   ("相持","相持","相持","弱","弱"),
    "中等": ("相持","相持","相持","相持","相持"),
    "大":   ("强","强","相持","相持","相持"),
    "极大": ("强","强","相持","相持","相持"),
}
# Table two needs BOTH factor comparison and palace comparison.
DUEL_OUTCOMES_3X3 = {
    "强":{"强":"能","相持":"艰难","弱":"艰难"},
    "相持":{"强":"艰难","相持":"艰难","弱":"艰难"},
    "弱":{"强":"艰难","相持":"艰难","弱":"不能"},
}
assert set(STRONG_WEAK_5X5)==set(TIERS)
assert all(len(x)==5 for x in STRONG_WEAK_5X5.values())
assert all(len(v)==3 for v in DUEL_OUTCOMES_3X3.values())
VERSION="selected_two_table_duel_v1"


def relation_between_palaces(actor,target):
    if actor["palace"]==target["palace"]:
        return "同宫"
    a,b=actor["palace_element"],target["palace_element"]
    if a==b:return "比和"
    if CONTROLS[a]==b:return "克"
    if CONTROLS[b]==a:return "被克"
    if GENERATES[a]==b:return "生"
    if GENERATES[b]==a:return "被生"
    raise ValueError("Invalid actual palace element relation")


def matchup(first,second,*,actor_role,target_role):
    """Compare exactly two already selected TABLE ONE facts, no more."""
    for item in (first,second):
        if item["strength_label"] not in TIERS or item["palace_strength_label"] not in TIERS:
            raise ValueError("Two complete table-one facts required")
    relation=relation_between_palaces(first,second)
    i,j=TIERS.index(first["strength_label"]),TIERS.index(second["strength_label"])
    ci,cj=TIERS.index(first["palace_strength_label"]),TIERS.index(second["palace_strength_label"])
    star_cmp=STRONG_WEAK_5X5[TIERS[i]][j]
    palace_cmp=STRONG_WEAK_5X5[TIERS[ci]][cj]
    restrictions=tuple(dict.fromkeys(first.get("restrictions",())+second.get("restrictions",())))
    nominal=DUEL_OUTCOMES_3X3[star_cmp][palace_cmp]
    if relation in ("克","生"):
        ability="条件待核" if restrictions else nominal
    else:
        ability="不适用"
    return {
        "version":VERSION,"actor":actor_role,"target":target_role,
        "actor_fact_id":first["fact_id"],"target_fact_id":second["fact_id"],
        "actor_palace":first["palace"],"target_palace":second["palace"],
        "physical_relation_id":"%s:%s"%tuple(sorted((first["palace"],second["palace"]))),
        "relation":relation,"symbol_contrast":star_cmp,"palace_contrast":palace_cmp,
        "actor_strength":first["strength_label"],"target_strength":second["strength_label"],
        "actor_palace_strength":first["palace_strength_label"],
        "target_palace_strength":second["palace_strength_label"],
        "ability":ability,"restrictions":restrictions,
        "requires_domain_rule":True,"medical_validity_claimed":False,
    }


def table_one(kind,symbol,month_branch,palace,*,plane="heaven",restrictions=()):
    """Explicit alias for reusable hard-coded TABLE ONE (no duplicated table)."""
    return inspect_strength_25(
        kind,symbol,month_branch,palace,plane=plane,restrictions=restrictions)
