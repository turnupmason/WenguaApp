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
from .user_domain_matrices_20261023 import (
    lookup_selected_factor,inspect_control,CONTROL_GRID_VERSION)

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
VERSION="selected_table_v5_corrected_fake_true_source_target"


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


def matchup(first,second,*,actor_role,target_role,
            attacker_fake_void=False,target_fake_void=False,
            attacker_true_void=False,target_true_void=False,
            attacker_true_void_variant=None,
            attacker_fake_void_variant=None):
    """One control matrix query per selected actual actor->target relationship.

    Normal 克 and verified source/target fake or true void use the
    user's newest corrected exact 25-cell matrices. The previous '干得过' table remains a historical reference,
    NOT an additional fight. Palace strengths are NOT pitted separately.
    """
    relation=relation_between_palaces(first,second)
    a,b=first.get("strength_label"),second.get("strength_label")
    restrictions=tuple(dict.fromkeys(
        tuple(first.get("restrictions",()))+tuple(second.get("restrictions",()))))
    unresolved_power=(a not in TIERS or b not in TIERS)
    void_uncertain_a=("旬空待辨" in first.get("restrictions",()))
    void_uncertain_b=("旬空待辨" in second.get("restrictions",()))
    if unresolved_power:
        control={"status":"factor_power_pending","result":None,
                 "reason":"用神真实落宫十二长生可能跨两个不同档，缺原著择支法，不能虚构唯一力量",
                 "table_version":CONTROL_GRID_VERSION}
    else:
        control=inspect_control(
            actor_power=a,target_power=b,palace_relation=relation,
            attacker_fake_void=attacker_fake_void,
            target_fake_void=target_fake_void,
            attacker_true_void=attacker_true_void,
            target_true_void=target_true_void,
            attacker_true_void_variant=attacker_true_void_variant,
            attacker_fake_void_variant=attacker_fake_void_variant,
            attacker_void_unknown=void_uncertain_a and not (
                attacker_fake_void or attacker_true_void),
            target_void_unknown=void_uncertain_b and not (
                target_fake_void or target_true_void))
    out=control.get("result")
    if control["status"]=="not_control_relation":
        ability="不适用"
    elif control["status"]!="matched":
        ability="条件待核"
    elif restrictions:
        # Control grid can select a proven void variant without masking
        # unrelated tomb/door-punishment evidence.
        unverified=[
            x for x in restrictions
            if x!="旬空待辨" or not (
                attacker_fake_void or target_fake_void or
                attacker_true_void or target_true_void)]
        ability="条件待核" if unverified else (
            "能" if out in CONTROL_CONFIDENT else
            "艰难" if out in CONTROL_LIMITED else "不能")
    else:
        ability=("能" if out in CONTROL_CONFIDENT else
                 "艰难" if out in CONTROL_LIMITED else "不能")
    # Explicitly retain the separate original raw source conditions; do
    # not imply void is 'fake' merely because Xun Kong branches are present.
    return {
        "version":VERSION,"table_two_version":CONTROL_GRID_VERSION,
        "actor":actor_role,"target":target_role,
        "actor_fact_id":first["fact_id"],"target_fact_id":second["fact_id"],
        "actor_palace":first["palace"],"target_palace":second["palace"],
        "physical_relation_id":"%s:%s"%tuple(sorted((first["palace"],second["palace"]))),
        "relation":relation,
        "duel_result":out,"control_result":out,
        "control_status":control["status"],
        "control_scenario":control.get("scenario"),
        "control_candidates":control.get("candidate_tables",()),
        "control_reason":control.get("reason"),
        "actor_strength":a,"target_strength":b,
        "actor_palace_strength":first["palace_strength_label"],
        "target_palace_strength":second["palace_strength_label"],
        "palace_strength_is_context_only":True,
        "table_two_lookups_for_pair":1 if control["status"]=="matched" else 0,
        "ability":ability,
        "why":control.get("reason") or "五行方向与用户25格克制原表独立核实",
        "backfire_risk_symbolic":out in ("反侮受损",),
        "raw_user_duel_cells_preserved":True,
        "restrictions":restrictions,"requires_domain_rule":True,
        "medical_validity_claimed":False,
    }

# Final candidate ability labels are independent from the raw user cell.
# All void cases are resolved by a SINGLE selected corrected user matrix.
# These labels do NOT add invented 5x5 gradations: they only decide whether
# verified candidate evidence can be provisionally used by a source-role
# domain. The exact original expression is always control_result.
CONTROL_CONFIDENT=frozenset((
    "有效克制","高效克制","强力主克","绝对主克","极限压制",
    "有效主克","完全清除",
))
CONTROL_LIMITED=frozenset((
    "微弱克制","减力克制","断续克制","效力递减",
))

def table_one(kind,symbol,month_branch,palace,*,plane="heaven",restrictions=()):
    """Alias for reusable fixed TABLE ONE; only selected symbol is inspected."""
    return lookup_selected_factor(
        kind,symbol,month_branch,palace,plane=plane,restrictions=restrictions)
