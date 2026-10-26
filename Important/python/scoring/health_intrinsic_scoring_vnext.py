"""2026-10-24 user-authored intrinsic 吉凶 plus existing 200-cell physical energy.

This is the CURRENT candidate rule layer, not frozen V3.9.1 or obsolete
V4.2 0–100 scoring. Literal defaults are recorded separately from the
month/palace five-tier ACTUAL strength; no unsupported ad-hoc interpolation.
Ordered 81 unique positions completed by user: 82 rows, retaining one duplicated 庚/己 source record.
Historic original book disease-specific contradictions remain blocked.
"""
from __future__ import annotations

import json
from pathlib import Path

from .health_five_level_quant_vnext import points,label
from .user_domain_matrices_20261023 import COLS

CATALOG_PATH=Path(__file__).resolve().parents[2]/(
    "data/knowledge/score_models/health_severity_vnext/"
    "user_intrinsic_and_ordered_pairs_20261024_v3_81_completed.json")
CATALOG=json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
STARS=CATALOG["stars"]
DOORS=CATALOG["doors"]
GODS=CATALOG["gods"]
GOD_RELATIONS=CATALOG["god_relations"]
STEM_CATALOG=json.loads((CATALOG_PATH.parent/"user_ten_stem_intrinsic_20261024_v2.json").read_text(encoding="utf-8"))
STEM_INTRINSIC=STEM_CATALOG["stems"]
JIA_HIDDEN_INTRINSIC=STEM_CATALOG["jia_hidden_baselines"]
USER_PATTERN_ROWS=tuple(CATALOG["records"])
PAIR_ROWS={}
for _row in USER_PATTERN_ROWS:
    PAIR_ROWS.setdefault(_row["key"],[]).append(_row)
PAIR_ROWS={k:tuple(v) for k,v in PAIR_ROWS.items()}
BOOK_HEALTH_CONFLICTS=frozenset(CATALOG["book_health_exception_keys"])
POSITIVE_DOORS=frozenset(("开门","休门","生门"))
NEGATIVE_DOORS=frozenset(("死门","惊门","伤门"))
NEUTRAL_DOORS=frozenset(("杜门","景门"))

assert len(STARS)==9 and len(DOORS)==8 and len(GODS)==8
assert len(USER_PATTERN_ROWS)==82 and len(PAIR_ROWS)==81
assert len(CATALOG["coverage"]["missing_pairs"])==0
assert set(GOD_RELATIONS)=={"符号生宫","符号克宫","比和","宫克符号","宫生符号"}
VERSION="health_user_intrinsic_baselines_200_cell_v20261024_v3_81complete"


def _signed_power(name,source,actual_tier):
    """Baseline explicitly retained; current five-grade energy uses 200 cell.

    No additional invented interpolation between baseline and monthly tier:
    intrinsic default supplies POLARITY and basic power, while the user's
    200-cell factor strength supplies *actual* current magnitude.
    """
    if name not in source:
        return {"status":"unknown_symbol","symbol":name,"score":None}
    baseline=source[name]
    if baseline==0:
        return {"status":"neutral","symbol":name,"baseline":0,
                "tier":actual_tier,"score":0,"label":"中平0分",
                "rule":"neutral_even_when_symbol_power_is_high","version":VERSION}
    if actual_tier not in COLS:
        return {"status":"actual_strength_pending","symbol":name,
                "baseline":baseline,"score":None,"tier":actual_tier,
                "version":VERSION}
    polarity="吉" if baseline>0 else "凶"
    score=points(actual_tier,polarity)
    return {"status":"calculated","symbol":name,
            "baseline":baseline,"baseline_label":label(baseline),
            "polarity":polarity,"tier":actual_tier,"score":score,
            "label":label(score),
            "rule":"intrinsic_polarity_x_exact_200cell_strength",
            "version":VERSION}


def star_score(name,actual_tier):
    return _signed_power(name,STARS,actual_tier)


def door_score(name,actual_tier):
    return _signed_power(name,DOORS,actual_tier)


def god_score(name,nominal_relation):
    if name=="腾蛇":name="螣蛇"
    if name not in GODS:
        return {"status":"unknown_god","symbol":name,"score":None}
    if nominal_relation not in GOD_RELATIONS:
        return {"status":"missing_real_god_palace_relation",
                "symbol":name,"baseline":GODS[name],"score":None}
    tier=GOD_RELATIONS[nominal_relation]
    out=_signed_power(name,GODS,tier)
    out["nominal_relation"]=nominal_relation
    out["month_stage"]=None
    out["source_has_month_adjustment"]=False
    return out


def stem_intrinsic_score(stem, *, xun_shou=None):
    """Signed USER default, independent of 200-cell monthly stem magnitude.

    Never pretend 甲 visibly appears in a palace or assign the 甲申 -3 to
    all Jia cycles. These are provenance/polarity observations, NOT a
    fifth palace point category on top of the four-user-example items.
    """
    if stem=="甲":
        if xun_shou not in JIA_HIDDEN_INTRINSIC:
            return {"status":"jia_xun_not_resolved","stem":"甲",
                    "xun_shou":xun_shou,"baseline":None}
        value=JIA_HIDDEN_INTRINSIC[xun_shou]
    elif stem in STEM_INTRINSIC:
        value=STEM_INTRINSIC[stem]
    else:
        raise ValueError("Unknown stem intrinsic default")
    return {"status":"user_intrinsic_default","stem":stem,
            "xun_shou":xun_shou if stem=="甲" else None,
            "hidden_in":"庚" if stem=="甲" and xun_shou=="甲申" else None,
            "baseline":value,
            "polarity":"吉" if value>0 else "凶" if value<0 else "中平",
            "not_an_extra_fifth_palace_component":True,
            "source":"user_ten_stem_intrinsic_20261024_v2"}


def resolve_ordered_pair(top,bottom,*,door_name=None,illness_domain=True,
                         sex=None):
    """Literal supplied declaration by ORDERED pair; no book title fuzzy match.

    User completed the last four pairs; 庚/己 retains two historical source variants.
    Original books explicitly disagree on particular generic favourable
    patterns for measuring illness, so preserve source conflict without
    taking the optimistic outcome as qualified sickness evidence.
    """
    key=top+"/"+bottom
    declared=PAIR_ROWS.get(key,())
    base={"key":key,"top":top,"bottom":bottom,"user_rows":list(declared),
          "source_version":VERSION,"score":None,
          "not_clinical":True}
    if not declared:
        return {**base,"status":"user_pair_not_supplied",
                "reason":"用户本次81种有序组合中此项未单独给吉凶；保留既存原书来源"}
    if len(declared)==1 and declared[0].get("user_supplied") and declared[0].get("book_title_mismatch"):
        # Latest USER-DECLARED name/polarity drives current scoring, while
        # the distinct ancient-book name+SHA is retained for future
        # line-by-line interpretation and NEVER silently relabelled.
        row=declared[0]
        return {**base,"status":"user_latest_four_added_with_book_name_conflict",
                "polarity":row["polarity"],"baseline":row["baseline"],
                "conditional":False,"user_title":row["title"],
                "book_excerpt_sha256":row["book_excerpt_sha256"],
                "book_source_line":row["book_source_line"],
                "book_original_excerpt":row["book_original_title_from_source"],
                "original_book_name_not_overwritten":True,
                "reason":"用户补齐81格按最新基础吉凶分；古籍同有序组合名称不同，双版本并存"}
    if len(declared)!=1:
        return {**base,"status":"duplicate_user_pair_variants_pending",
                "reason":"相同有序天地干出现多种断语，不以最后一条自动覆盖条件格"}
    # 2026-10-24 explicit HEALTH scoring correction: 乙加乙默认为凶 -3,
    # although the original general-purpose text called it 日奇伏吟 and
    # required an activity context. Preserve that original record unedited.
    if illness_domain and key=="乙/乙":
        return {**base,"status":"user_health_explicit_jiayi_override",
                "polarity":"凶","baseline":-3,
                "conditional":False,"reason":"用户最新明确乙加乙问病为凶格默认-3；原文条件型格局并存不覆盖",
                "historical_text_remains_conditional":True}
    row=declared[0]
    if illness_domain and key in BOOK_HEALTH_CONFLICTS:
        return {**base,"status":"book_illness_conflict_pending",
                "candidate_polarity":row["polarity"],
                "reason":"书内测病专述与普通谋事吉凶存在冲突，保留双轨，需原书测病条件"}
    polarity=row["polarity"]
    gate=row["gate"]
    if gate=="unconditional" and polarity in ("吉","凶"):
        return {**base,"status":"user_exact_unconditional",
                "polarity":polarity,"baseline":3 if polarity=="吉" else -3,
                "conditional":False,
                "reason":"按本轮用户明确的基础吉凶定位录入"}
    if gate in ("door_good","door_gate"):
        if door_name in POSITIVE_DOORS:
            if polarity=="吉":return {**base,"status":"user_door_condition_satisfied",
                                     "polarity":"吉","baseline":3,
                                     "conditional":True,"reason":"门吉条件实际满足"}
            return {**base,"status":"door_good_has_no_single_adverse_predicate",
                    "reason":"本格门吉表现不同，不能按条件型凶格强扣"}
        if door_name in NEGATIVE_DOORS:
            # Only genuine wordings with 门凶 explicitly adverse can vote
            # when the pair is placed in the conditional category.
            if "门凶" in row["explain"]:
                return {**base,"status":"user_door_condition_satisfied",
                        "polarity":"凶","baseline":-3,"conditional":True,
                        "reason":"本条原文字面门凶条件实际满足"}
        return {**base,"status":"conditional_door_gate_pending",
                "reason":"门的吉凶条件不满足或为中平，保留用户双向文字"}
    if gate=="gender" and sex in ("male","female"):
        return {**base,"status":"user_gender_condition_satisfied",
                "polarity":"吉" if sex=="male" else "凶",
                "baseline":3 if sex=="male" else -3,
                "conditional":True,"reason":"男吉女凶，使用实际已给的患者性别"}
    return {**base,"status":"conditional_context_pending",
            "reason":"原断语需要求事/动静/性别或门的独立条件，不可仅有格名就打分"}


def catalog_validation():
    return {"expected_pair_positions":81,"literal_supplied_rows":len(USER_PATTERN_ROWS),
            "distinct_declared_pairs":len(PAIR_ROWS),
            "missing_pair_keys":CATALOG["coverage"]["missing_pairs"],
            "duplicate":CATALOG["coverage"]["duplicate_pairs"],
            "book_illness_conflicts":sorted(BOOK_HEALTH_CONFLICTS)}
