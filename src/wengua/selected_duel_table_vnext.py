"""Wengua V-next selected two-table engine, user-exact 2026-10-23 grids.

TABLE ONE: the exact user nine-star 5x5 month × physical landing relation
(the historical day/door/stem rules remain separate). Only chosen factors run.

TABLE TWO: exact USER_DUEL_5X5, row = first selected factor's single
TABLE ONE strength, column = second selected factor's single TABLE ONE
strength. One lookup per selected pair, never a separate landing-palace
strength contest. Palace strength remains available as a raw chart fact.
Palace five-elements direction and obstructions are a separate applicability
gate. Table labels are research hypotheses, not book-validated treatment
success, historical event predictions, or clinical injury.
"""
from __future__ import annotations

from .factor_energy_25_rules import TIERS, inspect_strength_25
from .semantic_lookup import CONTROLS,GENERATES

# Original 2026-10-23 user-authored table, copied cell-for-cell.
USER_DUEL_5X5 = {
    "极小": ("干得过","干得过","勉强干得过","干不过","硬干反而受伤"),
    "小":   ("轻松干得过","干得过","干得过","勉强干得过","干不过"),
    "中等": ("非常简单干得过","轻松干得过","干得过","干得过","勉强干得过"),
    "大":   ("碾压式干得过","非常简单干得过","轻松干得过","干得过","干得过"),
    "极大": ("世界级压制干得过","碾压式干得过","非常简单干得过","轻松干得过","干得过"),
}
DUEL_COLUMN_TIERS=("极小","小","中等","大","极大")
USER_DUEL_TABLE_VERSION="user_exact_duel_5x5_20261023"
# Preserve old code's previous coarse 5x5 and 3x3 *as historical records*
# but do NOT use either of these matrices for new readings.
STRONG_WEAK_5X5 = {
    "极小": ("相持","相持","相持","弱","弱"),
    "小":   ("相持","相持","相持","弱","弱"),
    "中等": ("相持","相持","相持","相持","相持"),
    "大":   ("强","强","相持","相持","相持"),
    "极大": ("强","强","相持","相持","相持"),
}
DUEL_OUTCOMES_3X3 = {
    "强":{"强":"能","相持":"艰难","弱":"艰难"},
    "相持":{"强":"艰难","相持":"艰难","弱":"艰难"},
    "弱":{"强":"艰难","相持":"艰难","弱":"不能"},
}
assert set(USER_DUEL_5X5)==set(TIERS)==set(DUEL_COLUMN_TIERS)
assert all(len(row)==len(TIERS) for row in USER_DUEL_5X5.values())
VERSION="selected_two_table_duel_v3_single_lookup"


def user_duel_lookup(actor_strength, target_strength):
    """ONE O(1) hard-coded user-defined winner cell, never generalized."""
    if actor_strength not in USER_DUEL_5X5 or target_strength not in DUEL_COLUMN_TIERS:
        raise ValueError("Both strengths must be one of the five stated tiers")
    return USER_DUEL_5X5[actor_strength][DUEL_COLUMN_TIERS.index(target_strength)]


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


# This is not another invented graded matrix. The user's raw 25 cell labels
# must survive. These sets ONLY gate whether two separate successful
# comparisons and the actual directed five-element relation are sufficient
# for a provisional action in a domain-specific evidence workflow.
SUCCESS=frozenset({
    "干得过","轻松干得过","非常简单干得过",
    "碾压式干得过","世界级压制干得过",
})
MARGINAL="勉强干得过"
FAIL="干不过"
BACKFIRE="硬干反而受伤"


def matchup(first,second,*,actor_role,target_role):
    """One user-authored 25-cell strength matchup; no second palace duel.

    TABLE ONE already combines the chosen symbol's month-stage and actual
    symbol-to-landing-palace relationship into strength_label. Each selected
    factor therefore has ONE final power label from TABLE ONE.
    Palace-month facts remain independently auditable CONTEXT, not another
    opponent or a source of a fictional 'strength contradiction'.
    """
    for item in (first,second):
        if item["strength_label"] not in TIERS or item["palace_strength_label"] not in TIERS:
            raise ValueError("Both genuine table-one facts are required")
    relation=relation_between_palaces(first,second)
    result=user_duel_lookup(first["strength_label"],second["strength_label"])
    restrictions=tuple(dict.fromkeys(
        tuple(first.get("restrictions",()))+tuple(second.get("restrictions",()))))

    # Role relevance and unresolved obstructions are interpretation guards,
    # not additional power contests or override tables.
    if relation not in ("克","生"):
        ability="不适用"
        reason="本方宫未主动克或生对方宫；保留胜负格，供专题确认是否反向比较"
    elif restrictions:
        ability="条件待核"
        reason="旬空入墓击刑门迫待核实；不修改表二唯一胜负格"
    elif result in SUCCESS:
        ability="能"
        reason="双方表一力量均已包含月令和本身落宫关系，表二胜负格为胜出"
    elif result==MARGINAL:
        ability="艰难"
        reason="表二唯一胜负格为勉强胜出"
    elif result in (FAIL,BACKFIRE):
        ability="不能"
        reason="表二唯一胜负格为未胜出或传统反伤象意候选"
    else:
        raise ValueError("Unrecognized user-authored duel label")
    return {
        "version":VERSION,"table_two_version":USER_DUEL_TABLE_VERSION,
        "actor":actor_role,"target":target_role,
        "actor_fact_id":first["fact_id"],"target_fact_id":second["fact_id"],
        "actor_palace":first["palace"],"target_palace":second["palace"],
        "physical_relation_id":"%s:%s"%tuple(sorted((first["palace"],second["palace"]))),
        "relation":relation,
        "duel_result":result,
        "symbol_duel_result":result,
        "symbol_contrast":result,
        "actor_strength":first["strength_label"],
        "target_strength":second["strength_label"],
        "actor_palace_strength":first["palace_strength_label"],
        "target_palace_strength":second["palace_strength_label"],
        "palace_strength_is_context_only":True,
        "table_two_lookups_for_pair":1,
        "ability":ability,"why":reason,
        "backfire_risk_symbolic":result==BACKFIRE,
        "raw_user_duel_cells_preserved":True,
        "restrictions":restrictions,
        "requires_domain_rule":True,"medical_validity_claimed":False,
    }


def table_one(kind,symbol,month_branch,palace,*,plane="heaven",restrictions=()):
    """Alias for reusable fixed TABLE ONE; only selected symbol is inspected."""
    return inspect_strength_25(
        kind,symbol,month_branch,palace,plane=plane,restrictions=restrictions)
