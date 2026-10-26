"""Wengua research V-next: newest user-corrected 8 x 25-cell strength/control grids.

Literal entries only. Do not interpolate, infer original-author calibration,
silently change 宫迫/门破, or re-enable older duplicate true-void versions.
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

# User corrected the palace-over-door second column to 宫迫; the
# door-over-palace third column remains their exact label 门破.
# These original names are not inferred aliases for a new opening method.
DOOR_COLUMNS=("被宫生","宫迫","门破","生宫","比和")
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

# User's latest complete revision after comparing vacant-palace effects.
# The earlier v1/v2 text, including mistaken duplicate true-void attacker
# headings, stays immutable in docs/USER_7_GRID... and USER_8_GRID... and Git.
CONTROL_NORMAL={
    "极小":("有效克制","有效克制","微弱克制","克制失效","反侮受损"),
    "小":("高效克制","有效克制","有效克制","微弱克制","克制失效"),
    "中等":("强力主克","高效克制","有效克制","有效克制","微弱克制"),
    "大":("绝对主克","强力主克","高效克制","有效克制","有效克制"),
    "极大":("极限压制","绝对主克","强力主克","高效克制","有效克制"),
}
# 已核假空 / actual source palace is void.
CONTROL_FAKE_VOID_ATTACKER={
    "极小":("减力克制","微弱克制","克制失效","反侮受损","完全失控"),
    "小":("有效克制","减力克制","反侮受损","完全失控","完全失控"),
    "中等":("高效克制","有效克制","减力克制","微弱克制","完全失控"),
    "大":("强力主克","高效克制","有效克制","减力克制","微弱克制"),
    "极大":("绝对主克","强力主克","高效克制","有效克制","减力克制"),
}
# 已核假空 / actual target palace is void.
CONTROL_FAKE_VOID_TARGET={
    "极小":("高效克制","有效克制","完全失控","完全失控","完全失控"),
    "小":("强力主克","高效克制","减力克制","完全失控","完全失控"),
    "中等":("强力主克","有效主克","微弱克制","效力递减","克制失效"),
    "大":("绝对主克","强力主克","有效主克","微弱克制","效力递减"),
    "极大":("完全清除","完全清除","绝对主克","强力主克","微弱克制"),
}
# 已核真空 / actual source palace is void.
CONTROL_TRUE_VOID_ATTACKER={
    "极小":("完全失控","完全失控","完全失控","完全失控","完全失控"),
    "小":("完全失控","完全失控","完全失控","完全失控","完全失控"),
    "中等":("完全失控","完全失控","完全失控","完全失控","完全失控"),
    "大":("微弱克制","微弱克制","完全失控","完全失控","完全失控"),
    "极大":("减力克制","微弱克制","完全失控","完全失控","完全失控"),
}
# 已核真空 / actual target palace is void.
CONTROL_TRUE_VOID_TARGET={
    "极小":("完全失控","完全失控","完全失控","完全失控","完全失控"),
    "小":("完全失控","完全失控","完全失控","完全失控","完全失控"),
    "中等":("完全失控","完全失控","完全失控","完全失控","完全失控"),
    "大":("完全失控","完全失控","完全失控","微弱克制","完全失控"),
    "极大":("完全失控","完全失控","完全失控","减力克制","微弱克制"),
}
# The old singular fake_attacker_A symbol is kept as an explicit
# compatibility alias only; it now resolves to the corrected latest table.
CONTROL_FAKE_VOID_ATTACKER_A=CONTROL_FAKE_VOID_ATTACKER
CONTROL_GRID_BY_ID={
    "normal":CONTROL_NORMAL,
    "fake_void_attacker":CONTROL_FAKE_VOID_ATTACKER,
    "fake_void_target":CONTROL_FAKE_VOID_TARGET,
    "true_void_attacker":CONTROL_TRUE_VOID_ATTACKER,
    "true_void_target":CONTROL_TRUE_VOID_TARGET,
}
CONTROL_GRID_VERSION="user_5x5_control_with_void_20261023_v3_corrected_roles"
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
                    attacker_true_void=False,target_true_void=False,
                    attacker_void_unknown=False,target_void_unknown=False,
                    attacker_fake_void_variant=None,attacker_true_void_variant=None):
    """Exactly ONE of five current 25-cell tables, never two palace duels.

    Caller must independently verify fake vs true emptiness. A bare Xun Kong
    flag is NOT verification of fake or true void. The v2 A/B variants are
    historical mistakes and not selectable in the corrected source table.
    """
    if palace_relation!="克":
        return {"status":"not_control_relation","result":None,
                "reason":"仅施力宫实际克受力宫可使用克制矩阵，其他关系交给专题书法",
                "table_version":CONTROL_GRID_VERSION}
    for x in (actor_power,target_power):
        if x not in COLS:raise ValueError("Need two resolved table-one powers")
    if attacker_fake_void_variant is not None or attacker_true_void_variant is not None:
        raise ValueError("Superseded A/B void variants are not valid in latest tables")
    if attacker_void_unknown or target_void_unknown:
        return {"status":"void_type_pending","result":None,
                "reason":"九宫空亡已提示但真假或适用条件未核，暂不查定向矩阵",
                "table_version":CONTROL_GRID_VERSION}
    flags=(attacker_fake_void,target_fake_void,attacker_true_void,target_true_void)
    if sum(bool(x) for x in flags)>1:
        return {"status":"both_void_unspecified","result":None,
                "reason":"用户未提供双方同时空亡及真假组合的独立克制表",
                "table_version":CONTROL_GRID_VERSION}
    key=("fake_void_attacker" if attacker_fake_void
         else "fake_void_target" if target_fake_void
         else "true_void_attacker" if attacker_true_void
         else "true_void_target" if target_true_void
         else "normal")
    return {"status":"matched","scenario":key,
            "result":raw_cell(CONTROL_GRID_BY_ID[key],actor_power,target_power),
            "actor_power":actor_power,"target_power":target_power,
            "table_version":CONTROL_GRID_VERSION,
            "user_original_cell":True}
