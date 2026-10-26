"""Tianrui illness-star 5 x 5 preliminary symbolic matrix; REVIEW-ONLY.

Tianrui is EARTH. Its OWN seasonal states are the nine-star
旺/相/休/囚/废 system, never the ordinary stem 旺/相/休/囚/死.
The directed relation is FROM STAR to PALACE, not the other way around.

25 labels are user-proposed traditional images, NOT verified biomedical
prognoses or fully authored book case rules. One matrix fact per chart.
Every result also checks actual landing-palace monthly vitality and its
individual void/tomb/punishment/door-pressure limitations, which may defer
the proposed polarity. This matrix never fabricates 旬空真/假 determination.
"""
from __future__ import annotations

from .marriage_runtime import element_relation
from .semantic_lookup import STAR_ELEMENT

STAR="天芮星"
MONTH_STAGES=("旺","相","休","囚","废")
RELATION_KEYS=("宫克星","星生宫","星克宫","宫生星","宫星比和")
STAR_RELATIONS={"受克":"宫克星","生":"星生宫","克":"星克宫",
                "受生":"宫生星","比和":"宫星比和"}
# Source: user-provided 2026-10-23 25 traditional hypotheses, NOT book-verified
# and not allowed to introduce clinical assertions.
TITLES={
 "宫克星":("强弩受挫","萌芽被扼","兵败如山倒","关押绞杀","斩草除根"),
 "星生宫":("疯狂消耗","排毒宣泄","残存流逝","油尽灯枯","灰飞烟灭"),
 "星克宫":("病魔猖獗","病情扩散","贼心不死","自不量力／反侮","蚍蜉撼树"),
 "宫生星":("养虎为患","迅速恶化","养精蓄锐","顽固包庇","百足之虫"),
 "宫星比和":("全面爆发","结党营私","负隅顽抗","潜伏菌群","无害残留"),
}
# A preliminary *symbolic* direction, gated below by the palace's ability
# to do what the relation says; descriptions of treatment/cancer/survival are
# explicitly outside this matrix.
SYMBOLIC_TENDENCY={
 "宫克星":("favorable",)*5,
 "星生宫":("favorable",)*5,
 "星克宫":("adverse","adverse","adverse","pending","pending"),
 "宫生星":("adverse",)*5,
 "宫星比和":("adverse","adverse","adverse","pending","pending"),
}
EXPLANATIONS={
 "宫克星":"宫五行名义上克天芮，需看宫有没有力量制约病星",
 "星生宫":"天芮名义上生宫而泄气，泄气程度仍取决于星宫旺弱",
 "星克宫":"天芮名义上克落宫，是否攻得动必须比较双方旺弱",
 "宫生星":"落宫名义上生扶天芮，是否扶得动须看宫的承载力量",
 "宫星比和":"宫星同五行，只有同气事实，不能推断双方绝对力量相等",
}
STRONG=frozenset(("旺","相"))
WEAK_STAR=frozenset(("囚","废"))
WEAK_PALACE=frozenset(("囚","死"))


def inspect_tianrui_25(*,star_month,star_element,palace_element,
                       palace_month,void_branches=(),
                       sky_tombs=(),earth_tombs=(),
                       striking_stems=(),door_pressure=False):
    """Calculate ONE actual Tianrui star-palace case, not a tally of 25 votes.

    relation_from_star is computed from five-element facts, never chosen from
    a user label. Strictly rejects ordinary '死' for nine-star stage.
    """
    if star_element!=STAR_ELEMENT[STAR]:
        raise ValueError("Tianrui is earth; don't relabel original star")
    if star_month not in MONTH_STAGES:
        raise ValueError("Tianrui nine-star month must be 旺相休囚废, not 死")
    if palace_month not in ("旺","相","休","囚","死"):
        raise ValueError("Palace's ordinary five-element month stage required")
    relative=element_relation(star_element,palace_element)
    category=STAR_RELATIONS[relative]
    pos=MONTH_STAGES.index(star_month)
    blocked_by=[]
    if void_branches:blocked_by.append("旬空真/假条件待核")
    if sky_tombs:blocked_by.append("天盘入墓")
    if earth_tombs:blocked_by.append("地盘入墓")
    if striking_stems:blocked_by.append("六仪击刑")
    if door_pressure:blocked_by.append("门迫")
    # This is an explicit eligibility gate, NOT a weighted score.
    if blocked_by:
        status="obstructed"
        reasoning="宫内空墓刑迫等限制尚待合断，不能仅由月令与星宫关系定有效"
    elif category=="宫克星":
        if palace_month in STRONG and star_month in ("休","囚","废"):
            status="supported";reasoning="宫较有力、病星较弱，制病方向有条件发挥"
        elif palace_month in WEAK_PALACE and star_month in STRONG:
            status="limited";reasoning="弱宫难克旺星，不把名义宫克当作已经制病"
        else:
            status="conditional";reasoning="宫克星虽已核，双方强弱不足以单独定制病成败"
    elif category=="星生宫":
        if star_month in STRONG and palace_month in STRONG:
            status="supported";reasoning="星有余气、宫可承受，泄气象有条件显现"
        elif star_month in WEAK_STAR and palace_month in STRONG:
            status="limited";reasoning="星本弱、生宫有心无力，仍只记录轻微泄气候选"
        else:
            status="conditional";reasoning="星生宫已核，但泄气的实际作用仍须合宫气"
    elif category=="星克宫":
        if star_month in STRONG and palace_month in WEAK_PALACE:
            status="supported";reasoning="旺星克弱宫，传统攻宫象较易发生"
        elif star_month in WEAK_STAR and palace_month in STRONG:
            status="limited";reasoning="弱病难克旺宫，仅是反制候选而非病人已无恙"
        else:
            status="conditional";reasoning="星克宫方向已核，宫的抵抗力仍须合断"
    elif category=="宫生星":
        if palace_month in STRONG:
            status="supported";reasoning="宫旺相有生扶能力，病星受扶候选"
        elif palace_month in WEAK_PALACE and star_month in STRONG:
            status="limited";reasoning="宫弱难生旺星，不把名义生扶算成有效滋养"
        else:
            status="conditional";reasoning="宫生星虽已核，弱宫的生扶效力尚不确定"
    else:
        # 比和只 proves same elemental direction, never a second independent
        # evidence of 旺 or an automatic tumor/recurrence implication.
        if star_month in STRONG and palace_month in STRONG:
            status="supported";reasoning="星宫同气且均有月令支持"
        elif star_month in WEAK_STAR and palace_month in WEAK_PALACE:
            status="limited";reasoning="星宫同气但双方均弱，不自动推出吉凶"
        else:
            status="conditional";reasoning="同五行不等于同力量，须继续审查空墓门神"
    proposed=SYMBOLIC_TENDENCY[category][pos]
    vote=proposed if status=="supported" and proposed!="pending" else "pending"
    return {
        "schema":"health_tianrui_star_palace_25_v1",
        "star":STAR,"star_element":star_element,
        "star_month":star_month,"palace_element":palace_element,
        "palace_month":palace_month,
        "relation_from_star":relative,"category":category,
        "case_id":f"tianrui_25:{category}:{star_month}",
        "case_number":RELATION_KEYS.index(category)*5+pos+1,
        "traditional_title":TITLES[category][pos],
        "source_type":"user_proposed_symbolic_hypothesis_not_original_author_verified",
        "source_description":EXPLANATIONS[category],
        "effectiveness":status,"why":reasoning,
        "symbolic_tendency_candidate":proposed,
        "eligible_evidence_direction":vote,"restrictions":blocked_by,
        "one_matrix_case_only":True,
        "medical_diagnosis_or_prognosis":False,
    }


def validate_matrix():
    assert len(TITLES)==len(RELATION_KEYS)==5
    assert set(TITLES)==set(SYMBOLIC_TENDENCY)==set(RELATION_KEYS)
    assert all(len(TITLES[k])==len(SYMBOLIC_TENDENCY[k])==5 for k in RELATION_KEYS)
    return 25
