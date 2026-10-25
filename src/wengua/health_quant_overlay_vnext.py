"""2026-10-24 current user classification: signed real palace star/door/god/pattern.

Every real resident star contributes; god follows five palace relationships
WITHOUT month, and neutral Du/Jing doors contribute explicit zero. Exact
source-specific 81 stem-pair exceptions, two-branch life uncertainty and
unknown final >5 grade bands are audit-gated. Frozen V3.9.1 is untouched.
"""
from __future__ import annotations

from .health_five_level_quant_vnext import (
    points,palace_tally,multi_palace_tally,pattern_grade,VERSION,
    door_break_penalty_policy)

from .health_intrinsic_scoring_vnext import (
    star_score,door_score,god_score,resolve_ordered_pair,
    catalog_validation,VERSION as INTRINSIC_VERSION)
from .health_five_level_quant_vnext import label as grade_label

def _matching_restriction(entries,stem):
    """Only a genuinely explicit stem-labelled source fact matches."""
    for item in entries:
        if isinstance(item,dict):
            label=item.get("stem") or item.get("heaven_stem") or item.get("earth_stem")
            if label==stem:return True
        elif item==stem:return True
    return False


def _quantize_one(role,detail,*,five_not_encounter):
    """Score the four categories using user's latest exact symbolic rules.

    Four categories can contain multiple REAL stars or 81 pairs, but not
    multiple invented votes for a single chart source. Per factor baseline
    remains visible beside actual 200-cell strength.
    """
    if detail["palace"]==5:
        raise ValueError("No invented middle-five star/door/god")
    star_entries=[]
    for entry in detail["stars"]:
        st=entry["strength"]
        star_entries.append(star_score(entry["name"],st.get("strength_label")))
    valid_stars=[x["score"] for x in star_entries if x.get("score") is not None]
    star_values=(valid_stars[0] if len(valid_stars)==1
                 else valid_stars if len(valid_stars)>1 else None)
    if len(valid_stars)!=len(star_entries):star_values=None
    star_audit={
        "status":"calculated" if star_values is not None else "some_real_star_strength_pending",
        "per_star":star_entries,
        "score":sum(valid_stars) if star_values is not None else None,
        "intrinsic_baselines":[v.get("baseline") for v in star_entries],
        "co_palace_source_stars_not_silenced":True,
        "user_rule_version":INTRINSIC_VERSION,
        "polarity":next((x["polarity"] for x in star_entries if
                         x.get("polarity") is not None),None),
    }
    door=detail["door"]
    door_policy=(door_break_penalty_policy(
        door_name=door["symbol"],palace=detail["palace"],
        door_relation=door["user_cell_col"])
        if door else None)
    door_out=(door_score(door["symbol"],door.get("strength_label"))
              if door else {"status":"no_real_door","score":None})
    door_audit={**door_out,"symbol":door["symbol"] if door else None,
        "strength":door.get("strength_label") if door else None,
        "symbol_palace_relation":door.get("user_cell_col") if door else None,
        "penalty_policy":door_policy,
        "applied_door_break_shift":door_policy["two_level_shift"] if door_policy else 0,
        "strength_lookup_unchanged":True,
        "neutral_door_is_known_zero":door_out.get("score")==0}
    deity=detail["deity"]
    god_audit=god_score(deity["name"],deity.get("nominal_relation"))
    god_audit.update({"auspice":deity["polarity"],"relation":deity["relation"],
        "month_stage_is_not_used":True,
        "intrinsic_polarity_is_user_explicit":True})
    earth=detail["earth_stem"]
    bottom=earth["symbol"] if earth else None
    heaven={x["symbol"]:x for x in detail["heaven_stems"]}
    origin={(p["heaven"],p["earth"]):p
            for p in detail["ordered_book_81_pairs"]}
    pairs=[]
    for top,stem_fact in heaven.items():
        if not bottom:continue
        candidate=resolve_ordered_pair(top,bottom,door_name=door["symbol"] if door else None)
        stages=[s["stage"] for s in stem_fact.get("palace_twelve_life_facts",())
                if s.get("stage")]
        if not stages: stages=None
        # Restriction facts must identify the SPECIFIC original stem; don't
        # charge another cohost's tomb twice.
        heavenly_tomb=_matching_restriction(detail.get("sky_tombs",()),top)
        earthly_tomb=_matching_restriction(detail.get("earth_tombs",()),bottom)
        heaven_penalty=_matching_restriction(detail.get("striking_stems",()),top)
        earth_penalty=_matching_restriction(detail.get("striking_stems",()),bottom)
        actual_source=origin.get((top,bottom))
        polarity=candidate.get("polarity")
        gate_ok=candidate["status"] in (
            "user_exact_unconditional","user_door_condition_satisfied",
            "user_gender_condition_satisfied")
        if polarity in ("吉","凶"):
            graded=pattern_grade(
                polarity=polarity,heaven_stage=stages,
                heaven_tomb=heavenly_tomb,earth_tomb=earthly_tomb,
                heaven_punishment=heaven_penalty,earth_punishment=earth_penalty,
                source_gate_verified=gate_ok)
        else:
            graded={"status":"source_polarity_or_context_pending","score":None}
        pairs.append({
            "key":candidate["key"],"name":candidate["user_rows"][0]["title"] if candidate["user_rows"] else "未分类",
            "source_rule":candidate,
            "actual_book_source":actual_source,
            "heaven_lifecycle":stages,
            "grade":graded,
            "score":graded.get("score"),
            "status":graded.get("status"),
            "book_illness_conflict":candidate["status"]=="book_illness_conflict_pending",
            "no_invented_author_outcome":True,
        })
    applied=[p["score"] for p in pairs if p["score"] is not None]
    pattern_score=(0 if not pairs else
                   applied[0] if len(applied)==len(pairs)==1 else
                   applied if len(applied)==len(pairs) else None)
    pattern_audit={
        "status":("calculated" if pattern_score is not None
                  else "user_source_or_81_context_pending"),
        "matches":pairs,
        "score":sum(applied) if pattern_score is not None else None,
        "pending":[p["key"] for p in pairs if p["score"] is None],
        "explicit_81_coverage":catalog_validation(),
        "default_tier":"中等","base_per_user_pattern":3,
        "preserve_book_source_conditions":True}
    summary=palace_tally(
        factors={"star":star_values,
                 "door":door_out["score"],
                 "deity":god_audit.get("score"),
                 "pattern":pattern_score},
        door_break=bool(door_policy and door_policy["apply_extra_two_level_shift"]),
        five_not_encounter=bool(five_not_encounter),
        void_state=detail["void"]["classification"],
        horse_cleared_void=bool(detail["void"].get("horse_cleared_void")))
    return {"role":role,"palace":detail["palace"],
            "star":star_audit,"door":door_audit,
            "deity":god_audit,"pattern":pattern_audit,
            "real_heaven_stem_facts":detail["heaven_stems"],
            "real_earth_stem_fact":detail["earth_stem"],
            "palace_score":summary,
            "intrinsic_user_baselines_applied":True,
            "source_coverage":catalog_validation(),
            "scope":"user_candidate_health_severity_not_clinical"}


def inspect_selected_quantization(*,selected_roles,
                                  qian_kun_observations,first_stage_macro):
    """Do not count same real palace twice in numeric summary."""
    five=first_stage_macro["five_not_encounter_triggered"]
    roles={}
    aggregate={}
    for key,row in selected_roles.items():
        if key.startswith("extra_") or key in (
                "illness","doctor","medicine","patient",
                "hour","natal","gender"):
            detail=row["complete_palace"]
            item=_quantize_one(key,detail,five_not_encounter=five)
            roles[key]=item
            # User: score only truly selected relationship roles; stage-one
            # illness still included. Physical duplicates merge at total.
            aggregate[key]={"palace":item["palace"],
                            "score":item["palace_score"]["score"]}
    qian_kun={}
    for k,row in qian_kun_observations.items():
        qian_kun[k]=_quantize_one(
            k,row["complete_palace"],five_not_encounter=five)
        qian_kun[k]["auxiliary_only_not_auto_counted"]=True
    return {"version":VERSION,"roles":roles,
            "auxiliary_qian_kun":qian_kun,
            "summary":multi_palace_tally(palaces=aggregate),
            "incomplete_conversion_not_silently_scored":True,
            "source_condition_gate_required":True,
            "not_a_medical_diagnosis":True}


def render_palace_signed_score(item):
    """Report EVERY known star/door/god and ordered stem pair, no fake final."""
    star=item["star"]
    descriptions=[]
    for st in star["per_star"]:
        descriptions.append(
            st["symbol"]+"基准"+str(st.get("baseline","待核"))+
            "，200格现值"+str(st.get("tier") or "待核")+
            ("→"+st["label"]+"（"+str(st["score"])+"）" if
             st.get("label") else "→待核"))
    door=item["door"]
    descriptions.append(
        str(door.get("symbol"))+"门基准"+str(door.get("baseline","待核"))+
        "，200格"+str(door.get("strength") or "待核")+
        ("→"+str(door.get("label"))+"（"+str(door["score"])+"）"
         if door.get("score") is not None else "→待核"))
    god=item["deity"]
    descriptions.append(
        str(god.get("symbol"))+"神基准"+str(god.get("baseline","待核"))+
        "，对宫"+str(god.get("nominal_relation"))+
        "→"+str(god.get("tier") or "待核")+
        ("、"+str(god.get("label"))+"（"+str(god["score"])+"）"
         if god.get("score") is not None else "→待核"))
    pattern=item["pattern"]
    if not pattern["matches"]:
        descriptions.append("天地有序格无核定本次候选")
    for pair in pattern["matches"]:
        sub=pair["name"]+"（"+pair["key"]+"）"
        sc=pair["score"]
        descriptions.append(
            sub+(("→"+grade_label(sc)+"（"+str(sc)+"）")
                 if sc is not None else
                 "→"+str(pair["source_rule"]["status"])+"待核"))
    palace=item["palace_score"]
    if palace["grade"] is not None:
        final="本宫当前"+str(palace["score"])+"分："+palace["grade"]
    elif palace["score"] is not None:
        final="本宫当前"+str(palace["score"])+"分（"+str(palace["status"])+"）"
    else:
        final=("本宫已核分项小计"+str(palace["known_subtotal"])+
               "，尚缺"+"/".join(palace["unresolved_categories"])+
               "；总分/五级待核（"+palace["status"]+"）")
    return "；".join(descriptions)+"；"+final+"。"


def render_quant_review(report):
    summary=report["summary"]
    score=summary["score"]
    if score is not None:
        return ("五级宫内量化研究合计"+str(score)+"分（"+
                summary["grade"]+"）。共"+
                str(summary["unique_palace_count"])+
                "个不重复相关宫；此结果仅为用户规则研究象意。")
    sub=[]
    if summary["pending_palaces"]:
        sub.append("仍有"+str(len(summary["pending_palaces"]))+
                   "个宫的81格原书条件／干长生择支等尚待核")
    if summary["needs_final_band_rule"]:
        sub.append("跨宫累计分超五级范围，用户尚未给正式分档规则")
    return ("现已逐宫核算星、门、八神的带符号五级能量和有序天地格；"+
            "，".join(sub or ["最终分档待核"])+"。"+
            "不重复相关宫的当前已核分值为"+
            str(summary["raw_known_sum"])+"；"+
            "暂不生成虚构的极大吉／极大凶最终结论。"+
            "旧版吉凶票仅作定性对照。")
