"""Wengua V-next selected two-table engine, user-exact 2026-10-23 grids.

TABLE ONE: the exact user nine-star 5x5 month × physical landing relation
(the historical day/door/stem rules remain separate). Only chosen factors run.

TABLE TWO: exact USER_DUEL_5X5 table, row = initiator's factor power, column =
recipient's factor power. A second query on the same 25-cell TABLE TWO
compares the actual landing palaces' power. Both literal results remain in
the audit; no invented coarse "强/相持/弱" categories erase original wording.
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
VERSION="selected_two_table_duel_v2_exact_user_25"


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
    """Inspect exactly two chosen signifiers. Preserve BOTH exact 5x5 labels."""
    for item in (first,second):
        if item["strength_label"] not in TIERS or item["palace_strength_label"] not in TIERS:
            raise ValueError("Two complete table-one facts required")
    relation=relation_between_palaces(first,second)
    symbol_result=user_duel_lookup(first["strength_label"],second["strength_label"])
    palace_result=user_duel_lookup(first["palace_strength_label"],
                                   second["palace_strength_label"])
    restrictions=tuple(dict.fromkeys(
        tuple(first.get("restrictions",()))+tuple(second.get("restrictions",()))))
    backfire_risk=BACKFIRE in (symbol_result,palace_result)
    side_results=(symbol_result,palace_result)
    both_winning=all(x in SUCCESS for x in side_results)
    both_losing=all(x in (FAIL,BACKFIRE) for x in side_results)
    # Only a real actor-palace 克 or 生 opens a directionally meaningful
    # *action gate*. Other relations still retain both raw comparison labels.
    # Mixing winning and losing factors/palaces is unresolved, not a new score.
    if relation not in ("克","生"):
        ability="不适用"
        reason="实际两宫不是本方克/生对方；保留强弱对抗原值，不冒充作用已实现"
    elif restrictions:
        ability="条件待核"
        reason="空亡／入墓／击刑／门迫候选须核定；原表胜负不自动生效"
    elif both_winning:
        ability="能"
        reason="本方符号和本方落宫对对方均命中用户原表中的明确胜出格"
    elif both_losing:
        ability="不能"
        reason="本方符号和落宫对对方均不胜；保留原表反伤格而不当成临床伤害"
    elif MARGINAL in side_results and not any(x in (FAIL,BACKFIRE) for x in side_results):
        ability="艰难"
        reason="至少一侧仅为原表的勉强胜出；不能按充分胜出计"
    else:
        ability="条件待核"
        reason="符号与落宫双方输赢不一致；必须由专题完整证据裁决"
    return {
        "version":VERSION,
        "table_two_version":USER_DUEL_TABLE_VERSION,
        "actor":actor_role,"target":target_role,
        "actor_fact_id":first["fact_id"],"target_fact_id":second["fact_id"],
        "actor_palace":first["palace"],"target_palace":second["palace"],
        "physical_relation_id":"%s:%s"%tuple(sorted((first["palace"],second["palace"]))),
        "relation":relation,
        "symbol_duel_result":symbol_result,
        "palace_duel_result":palace_result,
        "symbol_contrast":symbol_result, # compatibility: exact, not coarse
        "palace_contrast":palace_result,
        "actor_strength":first["strength_label"],
        "target_strength":second["strength_label"],
        "actor_palace_strength":first["palace_strength_label"],
        "target_palace_strength":second["palace_strength_label"],
        "ability":ability,"why":reason,
        "backfire_risk_symbolic":backfire_risk,
        "both_winning_cells":both_winning,
        "both_losing_cells":both_losing,
        "raw_user_duel_cells_preserved":True,
        "restrictions":restrictions,
        "requires_domain_rule":True,
        "medical_validity_claimed":False,
    }


def table_one(kind,symbol,month_branch,palace,*,plane="heaven",restrictions=()):
    """Alias for reusable fixed TABLE ONE; only selected symbol is inspected."""
    return inspect_strength_25(
        kind,symbol,month_branch,palace,plane=plane,restrictions=restrictions)
