"""First-stage macro facts immediately following the real chart.

Original authored book rules already exist: five_not_encounter (day/hour
stems, SAME yin/yang + hour controls day), and verified 8-star/8-door
fuyin_fanyin_facts. Do not reinvent any original casting rules.
"""
from __future__ import annotations

from .health_severity_v27 import five_not_encounter
from .health_severity_v25 import fuyin_fanyin_facts

# 天显时 +2 per distinct participating outer palace, or +1.5 if 伏吟.
# Sum half units first, then floor ONCE. No 200/81 source changes.
TIANXIAN_HOURS={
    "甲":("甲子","甲戌"),"己":("甲子","甲戌"),
    "乙":("甲申",),"庚":("甲申",),
    "丙":("甲午",),"辛":("甲午",),
    "丁":("甲辰",),"壬":("甲辰",),
    "戊":("甲寅",),"癸":("甲寅",),
}
def tianxian_hour(day_ganzhi, hour_ganzhi):
    """Exact 六甲时 mapping, rejecting partial branches or guessed stems."""
    if len(day_ganzhi)!=2 or len(hour_ganzhi)!=2:
        return False
    return hour_ganzhi in TIANXIAN_HOURS.get(day_ganzhi[0], ())


def tianxian_palace_bonus(palace_count, *, triggered, fuyin):
    """Sum integer half-units over UNIQUE active exterior palaces, floor once."""
    if type(palace_count) is not int or not 0<=palace_count<=8:
        raise ValueError("Expected 0..8 distinct participating outer palaces")
    return palace_count*(3 if fuyin else 4)//2 if triggered else 0


def first_stage_macro(*,chart,calendar):
    """Always calculate these three before inspecting any selected palace.

    五不遇时: source says 凶时, but not a sufficient condition to diagnose
    death; count at most ONE independent general adverse source warning.
    伏吟/反吟: tempo condition, never an automatic second good/bad vote.
    """
    if calendar["day_ganzhi"][:1]=="":
        raise ValueError("Valid day pillar required")
    five=five_not_encounter(calendar["day_ganzhi"],chart["hour_ganzhi"])
    tianxian=tianxian_hour(calendar["day_ganzhi"],chart["hour_ganzhi"])
    fy=fuyin_fanyin_facts(chart)
    fuyin=fy["star"]=="伏吟" or fy["door"]=="伏吟"
    fanyin=fy["star"]=="反吟" or fy["door"]=="反吟"
    tempo=("slow" if fuyin and not fanyin else
           "fast" if fanyin and not fuyin else
           "mixed" if fuyin and fanyin else "not_assessed_from_fuyin")
    return {
        "version":"user_health_macro_first_20261023_v1",
        "five_not_encounter":five,
        "five_not_encounter_triggered":five["triggered"],
        "tianxian_hour_triggered":tianxian,
        "tianxian_per_palace_half_units":(3 if fuyin else 4) if tianxian else 0,
        "tianxian_scope":"distinct_selected_outer_palaces_floor_once",
        "five_not_encounter_tendency":"general_adverse" if five["triggered"] else "not_present",
        "fuyin_fanyin":fy,
        "star_fuyin":fy["star"]=="伏吟",
        "door_fuyin":fy["door"]=="伏吟",
        "star_fanyin":fy["star"]=="反吟",
        "door_fanyin":fy["door"]=="反吟",
        "tempo":tempo,
        "tempo_is_not_auspiciousness":True,
        "separate_from_role_strength":True,
        "not_a_clinical_prediction":True,
    }


def render_first_stage_macro(facts):
    five=facts["five_not_encounter"]
    if five["triggered"]:
        first=("五不遇时成立（时干"+five["hour_stem"]+
               "克日干"+five["day_stem"]+"且阴阳相同）；"+
               "按用户规则，五不遇时主诸事凶，为全局一项不利象，"+
               "不能单凭此象断病亡。")
    else:
        first=("不构成五不遇时（已按日干、时干五行克制及阴阳同类核对）。")
    fy=facts["fuyin_fanyin"]
    prefix="九星"+fy["star"]+"、八门"+fy["door"]+"。"
    t=facts["tempo"]
    pace=("伏吟主慢，反吟主快；本盘星门分别命中，缓急并列待具体条件核定。"
          if t=="mixed" else
          "伏吟主慢。" if t=="slow" else
          "反吟主快。" if t=="fast" else
          "本盘无整盘伏吟反吟，不凭此三项擅断缓急。")
    # Read the approved editable template, not an unversioned hardcoded
    # sentence. Whether 伏吟 reduces 天显 comes from the ACTUAL macro facts.
    from .health_reading_template_vnext import render
    if facts.get("tianxian_hour_triggered"):
        good=render("tianxian_fuyin" if facts.get("star_fuyin") or
                    facts.get("door_fuyin") else "tianxian_regular")
    else:
        good=""
    return first+" "+good+prefix+pace+" 缓急不自动等于吉凶。"
