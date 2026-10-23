"""Cross-domain *precomputed* symbol energy combinations (V-next only).

Four user-selected primary directed symbol-palace relations x five month
stages = 20; the fifth physically valid relation 符号克宫 is never dropped:
it is the explicit five-case overflow branch, preserving all original 25s.
A deity has NO own monthly stage, so 4 nominal deity-palace relations form
the primary grid (with a fifth physical exception); its landing palace
season can still be inspected independently.

Pair grids are MATERIALIZED at import from hard-coded source matrix cells,
not created opportunistically per reading. Tier labels are uncalibrated
hypotheses, NOT ancient validated forecasts or real-world health outcomes.
"""
from __future__ import annotations

from itertools import product

from .factor_energy_25_rules import (
    RELATIONS, STAR_STAGES, EARTH_STAGES, TIERS, RANK,
    lookup_25, compare_role_strength,
)

# Explicit user template. '克宫' is real, but NOT silently substituted for
# any of these four relations; both directions remain queryable.
PRIMARY_RELATIONS=("宫生符号","宫克符号","符号生宫","比和")
EXTRA_RELATION="符号克宫"
PALACE_INTERACTIONS=("克","被克","生","被生")
SPECIAL_INTERACTIONS=("比和","同宫")
MONTHS={"star":STAR_STAGES,"door":EARTH_STAGES,"stem":EARTH_STAGES}
SOURCE_VERSION="cross_layer_energy20_pair_grid_v1"


def _one(kind,stage,relation):
    source=lookup_25(kind,stage,relation)
    return {"kind":kind,"month_stage":stage,"symbol_palace_relation":relation,
            "strength":source["strength"],
            "source_case_number_25":source["case_number"],
            "status":"uncalibrated_review_heuristic"}


# A fully materialized 20-case main branch for each of star/door/stem.
LAYER20={
    kind:{(stage,relation):_one(kind,stage,relation)
          for stage,relation in product(stages,PRIMARY_RELATIONS)}
    for kind,stages in MONTHS.items()
}
# A separate five-case real-world branch for 符号克宫, one per season.
LAYER5_EXCEPTION={
    kind:{stage:_one(kind,stage,EXTRA_RELATION) for stage in stages}
    for kind,stages in MONTHS.items()
}
# Gods: no 'god monthly stage'. The landing palace's monthly state is a
# separate context dimension, not a hidden five-state score for the god.
GOD4={relation:{"kind":"deity","symbol_palace_relation":relation,
               "god_month_stage":None,
               "status":"needs_actual_palace_month_environment"}
      for relation in PRIMARY_RELATIONS}
GOD_EXCEPTION={"symbol_palace_relation":EXTRA_RELATION,
               "god_month_stage":None,
               "status":"needs_actual_palace_month_environment"}

# Every possible 20×20 for seasonal layers is available *before a chart is
# inspected*. Includes 9 ordered kind combinations (star/door/stem).
PAIR20X20={
    (a,b):{(akey,bkey):{
        "actor":LAYER20[a][akey],"target":LAYER20[b][bkey],
        "actor_strength":LAYER20[a][akey]["strength"],
        "target_strength":LAYER20[b][bkey]["strength"],
        "comparison_only":"actor_stronger" if
            RANK[LAYER20[a][akey]["strength"]]>RANK[LAYER20[b][bkey]["strength"]]
            else "target_stronger" if
            RANK[LAYER20[a][akey]["strength"]]<RANK[LAYER20[b][bkey]["strength"]]
            else "equal_tier",
    } for akey,bkey in product(LAYER20[a],LAYER20[b])}
    for a,b in product(MONTHS,MONTHS)
}

# User's additional 4×20 stem-star relationship layer: four **inter-palace
# directed actions** versus the 20-category STAR state. This is a useful
# projection, NOT a replacement for the stem's own 20-category strength.
STEM_STAR_4X20={
    (direction,star_state):{
        "palace_interaction":direction,
        "star_state":LAYER20["star"][star_state],
        "needs_actual_stem20_and_both_palace_months":True,
    }
    for direction,star_state in product(PALACE_INTERACTIONS,LAYER20["star"])
}

# Fully materialized follow-through: 4 relationship directions x the actual
# 20 stem categories x 20 star categories = 1600 before palace conditions.
STEM_STAR_4X20X20={
    (direction,stem_state,star_state):{
        "palace_interaction":direction,
        "stem_state":LAYER20["stem"][stem_state],
        "star_state":LAYER20["star"][star_state],
        "strength_comparison":PAIR20X20[("stem","star")][stem_state,star_state]["comparison_only"],
        "needs_both_actual_palace_months_and_conditions":True,
    }
    for direction,stem_state,star_state in product(
        PALACE_INTERACTIONS,LAYER20["stem"],LAYER20["star"])
}

# 4 deity-to-symbol relationship positions x 20 seasonal cases. These are
# dimensional catalogs only, not a claim that deity itself has seasonal qi.
GOD4X20={
    kind:{(relation,state):{
        "god_relation":GOD4[relation],
        "target_symbol_state":LAYER20[kind][state],
        "needs_actual_deity_palace_month":True,
    } for relation,state in product(GOD4,LAYER20[kind])}
    for kind in MONTHS
}

assert set(PRIMARY_RELATIONS)|{EXTRA_RELATION}==set(RELATIONS)
assert all(len(x)==20 for x in LAYER20.values())
assert all(len(x)==5 for x in LAYER5_EXCEPTION.values())
assert len(GOD4)==4
assert all(len(x)==400 for x in PAIR20X20.values())
assert len(STEM_STAR_4X20)==80
assert len(STEM_STAR_4X20X20)==1600
assert all(len(x)==80 for x in GOD4X20.values())


def single_case(fact):
    """A strength fact from inspect_strength_25; never infer unknown values."""
    kind=fact["kind"]
    relation=fact["nominal_relation_from_symbol"]
    if kind=="deity":
        if fact["symbol_month_stage"] is not None:
            raise ValueError("Deity cannot acquire fabricated own-month five stages")
        if relation in GOD4:
            return {"path":"deity_four","god":GOD4[relation],
                    "palace_month":fact["palace_month_stage"]}
        if relation==EXTRA_RELATION:
            return {"path":"deity_fifth_physical","god":GOD_EXCEPTION,
                    "palace_month":fact["palace_month_stage"]}
        raise ValueError("Unsupported deity-palace direction")
    stage=fact["symbol_month_stage"]
    key=(stage,relation)
    if kind not in LAYER20:
        raise ValueError("Unsupported factor kind")
    if key in LAYER20[kind]:
        return {"path":"main_4x5_20","case":LAYER20[kind][key]}
    if relation==EXTRA_RELATION and stage in LAYER5_EXCEPTION[kind]:
        return {"path":"required_fifth_physical",
                "case":LAYER5_EXCEPTION[kind][stage]}
    raise ValueError("Source factor has incomplete real moon/relation")


def compare_full_factors(actor,target,*,actor_name="施力方",target_name="受力方"):
    """Both own states, two actual palace states, and their directed clash."""
    a=single_case(actor);b=single_case(target)
    akey=(actor["symbol_month_stage"],actor["nominal_relation_from_symbol"])
    bkey=(target["symbol_month_stage"],target["nominal_relation_from_symbol"])
    pair=None
    if actor["kind"] in MONTHS and target["kind"] in MONTHS:
        pair=PAIR20X20[(actor["kind"],target["kind"])].get((akey,bkey))
    comparison=compare_role_strength(
        actor,target,actor_name=actor_name,target_name=target_name)
    # The full 20×20 is not allowed to replace the actual two-palace verdict:
    # 5th relations and same-palace naturally take the explicit fallback.
    return {**comparison,"schema":SOURCE_VERSION,
            "actor_case":a,"target_case":b,
            "precomputed_20x20_pair":pair,
            "fallback_reason":None if pair else
                "第五种实际关系/八神情形，已由独立分支保真",
            "actor_palace_month":actor["palace_month_stage"],
            "target_palace_month":target["palace_month_stage"],
            "needs_domain_yongshen_and_original_book_conditions":True,
            "predictive_validity_claimed":False,
            "additional_evidence_vote":False}


def format_full_pair(paired):
    a=paired["actor"];b=paired["target"]
    return (f"{a}、{b}分别查自身关系（{paired['actor_case']['path']}、"
            f"{paired['target_case']['path']}），"
            f"自身力量{paired['actor_strength']}/{paired['target_strength']}，"
            f"宫位月令{paired['actor_palace_month']}/{paired['target_palace_month']}，"
            f"宫力{paired['actor_palace_strength']}/{paired['target_palace_strength']}；"
            f"两宫{paired['relation']}，能否克动：{paired['ability_to_control']}。"
            f"{paired['why']}")
