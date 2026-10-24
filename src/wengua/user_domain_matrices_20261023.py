"""Wengua research V-next: user-authored 2026-10-23 5x5 factor and control grids.

Literal entries only. Do not interpolate, infer original-author calibration,
silently repair a label (门破 vs 门迫), or change contradictory source variants.
Full chart already exists: only query a selected role/pair as needed.
"""
from __future__ import annotations

from .factor_energy_25_rules import TIERS, USER_STAR_25, USER_STAR_RELATIONS
from .factor_energy_review import inspect_symbol_energy
from .semantic_lookup import CONTROLS, GENERATES
from .health_severity_template import MONTH_ELEMENTS

COLS=TIERS # 极小 小 中等 大 极大
POWER_RELATIONS=("宫生符号","宫克符号","符号克宫","符号生宫","比和")
# The user's 九星 grid matches prior USER_STAR_25 byte-for-byte.
STAR_POWER=dict(USER_STAR_25)

# User wrote 门破 (not silently changed into the traditional 门迫).
# Physical five-element relationship is "门克宫", but the original label
# 门破 survives in the published user grid and audit.
DOOR_COLUMNS=("被宫生","被宫克","门破","生宫","比和")
DOOR_POWER={
    "旺":("极大","中等","大","大","极大"),
    "相":("极大","小","中等","中等","大"),
    "休":("大","极小","小","小","中等"),
    "囚":("中等","极小","极小","极小","小"),
    "死":("小","极小","极小","极小","极小"),
}
# Unlike the star/door grids, the STEM column relates to MONTH (not palace);
# its ROW is the independent twelve-lifecycle observation in the REAL palace.
STEM_COLUMNS=("被月令生","被月令克","克月令","生月令","比和")
STEM_STAGE_ROWS={
    "长生":"长生/冠带/临官/帝旺/沐浴",
    "冠带":"长生/冠带/临官/帝旺/沐浴",
    "临官":"长生/冠带/临官/帝旺/沐浴",
    "帝旺":"长生/冠带/临官/帝旺/沐浴",
    "沐浴":"长生/冠带/临官/帝旺/沐浴",
    "胎":"胎 / 养","养":"胎 / 养",
    "衰":"衰 / 病","病":"衰 / 病",
    "囚":"囚",
    "死":"死 / 墓 / 绝","墓":"死 / 墓 / 绝","绝":"死 / 墓 / 绝",
}
STEM_POWER={
    "长生/冠带/临官/帝旺/沐浴":("极大","中等","大","大","极大"),
    "胎 / 养":("极大","小","中等","中等","大"),
    "衰 / 病":("大","极小","小","小","中等"),
    "囚":("中等","极小","极小","极小","小"),
    "死 / 墓 / 绝":("小","极小","极小","极小","极小"),
}
# Twelve lifecycle has 12 states and does NOT include 囚. The user
# additionally gave 囚, stored but never invented as a lifecycle stage.

# Original user grid #1. No void.
CONTROL_NORMAL={
    "极小":("有效克制","有效克制","微弱克制","克制失效","反侮受损"),
    "小":("高效克制","有效克制","有效克制","微弱克制","克制失效"),
    "中等":("强力主克","高效克制","有效克制","有效克制","微弱克制"),
    "大":("绝对主克","强力主克","高效克制","有效克制","有效克制"),
    "极大":("极限压制","绝对主克","强力主克","高效克制","有效克制"),
}
# Original user grid #2: 施力方宫空亡 (假空) — variant 1, label AS GIVEN.
CONTROL_FAKE_VOID_ATTACKER_A={
    "极小":("减力克制","微弱克制","克制失效","反侮受损","系统性失控"),
    "小":("有效克制","减力克制","反侮受损","系统性失控","系统性失控"),
    "中等":("高效克制","有效克制","减力克制","微弱克制","克制失效"),
    "大":("强力主克","高效克制","有效克制","减力克制","微弱克制"),
    "极大":("绝对主克","强力主克","高效克制","有效克制","减力克制"),
}
# Original user grid #3: 受力方宫空亡 (假空).
CONTROL_FAKE_VOID_TARGET={
    "极小":("微弱克制","效力递减","克制失效","完全失控","完全失控"),
    "小":("有效主克","微弱克制","效力递减","克制失效","完全失控"),
    "中等":("强力主克","有效主克","微弱克制","效力递减","克制失效"),
    "大":("绝对主克","强力主克","有效主克","微弱克制","效力递减"),
    "极大":("完全清除","绝对主克","强力主克","有效主克","微弱克制"),
}
# Corrected 2026-10-23 user grid #4 is actually 施力方宫空亡(真空).
# Previously archived as fake_void_attacker_B; preserve that historical
# name as an alias for provenance only; it must NOT be a selectable fake grid.
CONTROL_TRUE_VOID_ATTACKER_A={
    "极小":("有效克制","减力克制","效力递减","克制失效","完全失控"),
    "小":("减力克制","效力递减","效力递减","克制失效","完全失控"),
    "中等":("断续克制","效力递减","克制失效","完全失控","完全失控"),
    "大":("克制失效","克制失效","完全失控","完全失控","完全失控"),
    "极大":("完全失控","完全失控","完全失控","完全失控","完全失控"),
}
# Another new user grid has the *same heading* 施力方宫空亡(真空)
# but distinct literal cells. No distinguishing premise was provided.
CONTROL_TRUE_VOID_ATTACKER_B={
    "极小":("终极解体","终极解体","终极解体","终极解体","终极解体"),
    "小":("丧失能力","丧失能力","完全失控","完全失控","完全失控"),
    "中等":("克制失效","克制失效","完全失控","完全失控","完全失控"),
    "大":("断续克制","效力递减","效力递减","克制失效","完全失控"),
    "极大":("微弱克制","断续克制","效力递减","克制失效","完全失控"),
}
# Historical identifier retained for audit/regression compatibility, not
# exposed in the live dispatch table (its input label was corrected).
CONTROL_FAKE_VOID_ATTACKER_B=CONTROL_TRUE_VOID_ATTACKER_A

CONTROL_GRID_BY_ID={
    "normal":CONTROL_NORMAL,
    "fake_void_attacker_A":CONTROL_FAKE_VOID_ATTACKER_A,
    "fake_void_target":CONTROL_FAKE_VOID_TARGET,
    "true_void_attacker_A":CONTROL_TRUE_VOID_ATTACKER_A,
    "true_void_attacker_B":CONTROL_TRUE_VOID_ATTACKER_B,
}
CONTROL_GRID_VERSION="user_5x5_control_with_void_20261023_v2_true_void"
STEM_POWER_VERSION="user_stem_life_stage_x_month_relation_20261023_v1"
DOOR_POWER_VERSION="user_door_month_x_palace_relation_20261023_v1"

for table in (*CONTROL_GRID_BY_ID.values(),STAR_POWER,DOOR_POWER,STEM_POWER):
    assert len(table)==5 and all(len(row)==5 for row in table.values())
assert tuple(USER_STAR_RELATIONS)==POWER_RELATIONS


def raw_cell(table, row, col, *, row_order=None, col_order=COLS):
    if row not in table or col not in col_order:raise ValueError("Unknown table row or column")
    return table[row][col_order.index(col)]


def stem_month_relation(stem_element,month_element):
    """Column names exactly as provided; direction month -> stem matters."""
    if stem_element==month_element:return "比和"
    if GENERATES[month_element]==stem_element:return "被月令生"
    if CONTROLS[month_element]==stem_element:return "被月令克"
    if CONTROLS[stem_element]==month_element:return "克月令"
    if GENERATES[stem_element]==month_element:return "生月令"
    raise ValueError("Invalid stem/month elements")


def lookup_selected_factor(kind,symbol,month_branch,palace,*,plane="heaven",
                           restrictions=()):
    """Return one chosen factor energy; all factual alternative stages retained."""
    from .factor_energy_25_rules import inspect_strength_25
    if kind not in ("star","stem","door","deity"):
        raise ValueError("Unknown selected signifier type")
    # These baseline facts always preserve original eight-door and twelve-life
    # observations. Note per-palace life can contain TWO branch-based stages.
    source=inspect_strength_25(kind,symbol,month_branch,palace,
                               plane=plane,restrictions=restrictions)
    if kind=="deity":return source
    if kind=="star":
        stage=source["symbol_month_stage"]
        relation=source["nominal_relation_from_symbol"]
        strength=raw_cell(STAR_POWER,stage,relation,col_order=POWER_RELATIONS)
        return {**source,"strength_label":strength,"table_version":"user_exact_nine_star_5x5_20261023",
                "user_cell_row":stage,"user_cell_col":relation}
    if kind=="door":
        stage=source["symbol_month_stage"]
        relation=source["nominal_relation_from_symbol"]
        strength=raw_cell(DOOR_POWER,stage,relation,col_order=POWER_RELATIONS)
        return {**source,"strength_label":strength,"table_version":DOOR_POWER_VERSION,
                "user_cell_row":stage,"user_cell_col":
                   DOOR_COLUMNS[POWER_RELATIONS.index(relation)],
                "user_original_door_label_preserved":True}
    # Ten stems: ROW is *actual palace twelve-lifecycle* group, COLUMN is
    # relation of the actual verified month element against the stem element.
    source_facts=source["palace_twelve_life_facts"]
    groups=tuple(dict.fromkeys(STEM_STAGE_ROWS[x["stage"]] for x in source_facts))
    rel=stem_month_relation(source["symbol_element"],MONTH_ELEMENTS[month_branch])
    options=tuple({ "row":g, "strength":raw_cell(STEM_POWER,g,rel,col_order=STEM_COLUMNS)}
                  for g in groups)
    labels=tuple(dict.fromkeys(x["strength"] for x in options))
    stage_ambiguous=len(labels)!=1
    return {
        **source,
        "strength_label":labels[0] if not stage_ambiguous else None,
        "table_version":STEM_POWER_VERSION,
        "user_cell_col":rel,
        "user_cell_row":groups[0] if len(groups)==1 else None,
        "stem_life_rows_at_real_palace":list(groups),
        "stem_life_source_facts":source_facts,
        "stem_life_candidate_cells":list(options),
        "stem_life_strength_pending":stage_ambiguous,
        "stem_month_relation_with_stage_independent":True,
        "legacy_stem_month_x_palace_strength":source["strength_label"],
        # Two branch stages producing DIFFERENT powers are genuinely
        # unresolved mapping, not a second opponent duel or a fabricated win.
        "effective_status":"ambiguous_two_palace_branches_wait_source_rule"
                           if stage_ambiguous else source["effective_status"],
    }


def inspect_control(*,actor_power,target_power,palace_relation,
                    attacker_fake_void=False,target_fake_void=False,
                    attacker_fake_void_variant=None,
                    attacker_true_void=False,target_true_void=False,
                    attacker_true_void_variant=None,
                    attacker_void_unknown=False,target_void_unknown=False):
    """One source-selected matrix lookup; corrected fake/true void provenance.

    One real 克 pair gets ONE final result only when void scenario is
    determined. Both supplied true-void attacker matrices have the exact
    same header but DIFFERENT literal entries, so never auto-pick A or B.
    """
    if palace_relation!="克":
        return {"status":"not_control_relation","result":None,
                "reason":"仅施力宫实际克受力宫使用克制专表",
                "table_version":CONTROL_GRID_VERSION}
    for x in (actor_power,target_power):
        if x not in COLS:raise ValueError("Need two resolved table-one powers")
    if attacker_void_unknown or target_void_unknown:
        return {"status":"void_type_pending","result":None,
                "reason":"已知空亡候选未核真假，不能臆选真假空表",
                "table_version":CONTROL_GRID_VERSION}
    if attacker_fake_void_variant not in (None,"A"):
        raise ValueError("Corrected source has ONE fake-void attacker grid; historic fake B is TRUE A")
    if attacker_true_void_variant not in (None,"A","B"):
        raise ValueError("True-void attacker variant must be source A or B")

    flags=(attacker_fake_void,target_fake_void,
           attacker_true_void,target_true_void)
    if sum(bool(x) for x in flags)>1:
        return {"status":"both_void_unspecified","result":None,
                "reason":"用户未提供双宫同时空亡、真假组合的专用矩阵",
                "table_version":CONTROL_GRID_VERSION}
    if target_true_void:
        return {"status":"target_true_void_unspecified","result":None,
                "reason":"用户未提供受力方宫真空的专用矩阵",
                "table_version":CONTROL_GRID_VERSION}
    if attacker_fake_void:
        key="fake_void_attacker_A"
    elif target_fake_void:
        key="fake_void_target"
    elif attacker_true_void:
        if attacker_true_void_variant not in ("A","B"):
            return {"status":"duplicate_true_attacker_label_pending",
                    "result":None,
                    "candidate_tables":(
                        {"id":"true_void_attacker_A","result":raw_cell(
                            CONTROL_TRUE_VOID_ATTACKER_A,actor_power,target_power)},
                        {"id":"true_void_attacker_B","result":raw_cell(
                            CONTROL_TRUE_VOID_ATTACKER_B,actor_power,target_power)},
                    ),
                    "reason":"两张不同25格原表都写施力方宫空亡(真空)，条件未明不能自动择表",
                    "table_version":CONTROL_GRID_VERSION}
        key="true_void_attacker_"+attacker_true_void_variant
    else:
        key="normal"
    return {"status":"matched","scenario":key,
            "result":raw_cell(CONTROL_GRID_BY_ID[key],actor_power,target_power),
            "actor_power":actor_power,"target_power":target_power,
            "table_version":CONTROL_GRID_VERSION,
            "user_original_cell":True}
