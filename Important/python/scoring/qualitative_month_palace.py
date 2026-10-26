"""Shared source-grounded qualitative strength comparator for ALL Qimen domains.

The directional five-element relation and ability to exert it are different.
Compare the actual symbol monthly state and its landing palace's own monthly
state separately for BOTH sides before discussing any 克/生/比和.
No numeric index, no automatic life/death, market, marriage, court or medical
prediction. Extreme 反侮/反克 labels remain conditional research candidates.
"""
from __future__ import annotations

STRONG=frozenset(("旺","相"))
WEAK=frozenset(("囚","废","死"))
VALID_STAGES=frozenset(("旺","相","休","囚","废","死"))

def effect_of_relation(relation,actor_stage,target_stage,*,blocked=False):
    """A relation is a directional FACT, its effectiveness is a separate claim."""
    if relation not in ("克","生","受克","受生","比和"):
        raise ValueError("Invalid five-element relationship")
    if actor_stage not in VALID_STAGES or target_stage not in VALID_STAGES:
        return {"effect":"unknown","why":"月令旺弱未核定；仅记录生克方向"}
    if blocked:
        return {"effect":"obstructed","why":"施力符号有已核空墓刑迫，生克难当作实得"}
    if relation=="比和":
        return {"effect":"same_element","why":"同气不等于力量相等，须比较双方旺弱"}
    if actor_stage in WEAK and target_stage in STRONG:
        return {"effect":"limited","why":"施力方月令弱、受力方月令强，不能仅凭相克/相生断成功"}
    if actor_stage in STRONG and target_stage in WEAK:
        return {"effect":"supported","why":"施力方旺相、受力方较弱，相应作用较容易显现"}
    return {"effect":"conditional","why":"月令不能单独证明最终作用，仍需核空墓刑迫与同宫格局"}


def compare_vigor_before_control(relation,*,actor_symbol_month,
                                 target_symbol_month,actor_palace_month,
                                 target_palace_month,blocked=False):
    """First test a named symbol's month THEN both actual landing palaces.

    This is a conditional interpretation of the user's 旺者克衰、衰者难克
    research rule, NOT a clinical or proven outcome. A star's strength cannot
    silently be substituted with just its palace's element, or vice versa.
    Distinct 'nominal' and 'effective' statuses are always retained.

    Two high-contrast branches:
      weak actor -> nominal 克 -> strong target => 反侮候选 / no control
      strong actor -> nominal 受克 <- weak target => 反克候选 /
      the weak target's nominal control cannot settle the outcome.
    """
    valid=(actor_symbol_month,target_symbol_month,
           actor_palace_month,target_palace_month)
    if relation not in ("克","生","受克","受生","比和"):
        raise ValueError("Invalid directional relation")
    if any(v not in VALID_STAGES for v in valid):
        return {"nominal_relation":relation,"effect":"unknown",
                "power_class":"unverified_month_and_palace",
                "why":"星及落宫旺衰必须分别核实，不可凭五行方向单断"}
    if blocked:
        return {"nominal_relation":relation,"effect":"obstructed",
                "power_class":"blocked_by_actual_palace_condition",
                "why":"存在空墓刑迫候选，实际发挥仍须核条件"}
    actor_both_weak=(actor_symbol_month in WEAK and actor_palace_month in WEAK)
    target_both_strong=(target_symbol_month in STRONG and
                        target_palace_month in STRONG)
    actor_both_strong=(actor_symbol_month in STRONG and
                       actor_palace_month in STRONG)
    target_both_weak=(target_symbol_month in WEAK and
                      target_palace_month in WEAK)
    if relation=="克" and actor_both_weak and target_both_strong:
        return {"nominal_relation":relation,"effect":"limited",
                "power_class":"反侮候选",
                "why":"虽名义克目标，但施力符号与落宫均弱、目标符号与落宫均旺；弱者难克旺者，不把名义相克当成已经克制"}
    if relation=="受克" and actor_both_strong and target_both_weak:
        return {"nominal_relation":relation,"effect":"resists_weak_attack",
                "power_class":"反克候选",
                "why":"虽名义受对方克，但对方符号与落宫均弱、自身符号与落宫均旺；弱克难奏效，不能推断最终结果"}
    # For other nominal interactions, retain direction and vigor distinction.
    src=effect_of_relation(relation,actor_symbol_month,target_symbol_month)
    if actor_symbol_month in WEAK and target_symbol_month in STRONG:
        src={**src,"effect":"limited",
             "why":"符号月令弱而对方旺，即使落宫补助仍须另验；不能视为制病已成"}
    if actor_symbol_month in STRONG and target_symbol_month in WEAK:
        src={**src,"effect":"supported",
             "why":"符号月令旺而对方弱，有发挥作用的条件，仍需看双方落宫和空墓刑迫"}
    if actor_symbol_month in STRONG and actor_palace_month in WEAK:
        src={**src,"effect":"conditional",
             "why":"星旺但落宫弱，内外旺弱冲突，不能只用星旺直接推论"}
    if actor_symbol_month in WEAK and actor_palace_month in STRONG:
        src={**src,"effect":"conditional",
             "why":"星弱但落宫旺，须区分星自身与落宫承载力，暂不反向定论"}
    return {"nominal_relation":relation,"power_class":"ordinary_conditional",
            **src}


