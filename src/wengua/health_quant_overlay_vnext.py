"""Real selected-palace adapter to NEW user five-grade research arithmetic.

This layer cannot invent:
 - intrinsic polarity for all nine stars, especially neutral/conditional stars;
 - the TWO door interpretation cases promised, but not yet specified;
 - a numeric deity power conversion (prior source has only 更/微 吉凶);
 - a source-verified 吉/凶 designation plus all executable gates for 81
   ordered heaven+earth stem patterns.
All those facts are saved rather than guessed, so a numeric final can be
pending even though the hand-authored example is exactly reproducible.
"""
from __future__ import annotations

from .health_five_level_quant_vnext import (
    points,palace_tally,multi_palace_tally,pattern_grade,VERSION)

# Role-bound condition only, not a universal auspice claim about all stars.
ROLE_STAR_POLARITY={"illness":("天芮星","凶"),
                    "doctor":("天心星","吉")}


def _quantize_one(role,detail,*,five_not_encounter):
    if detail["palace"]==5:
        raise ValueError("No invented middle-five star/door/god")
    star_score=None
    star_audit={"status":"source_polarity_pending"}
    selected=ROLE_STAR_POLARITY.get(role)
    if selected:
        name,sign=selected
        chosen=next((x["strength"] for x in detail["stars"]
                     if x["name"]==name),None)
        if chosen and chosen.get("strength_label"):
            star_score=points(chosen["strength_label"],sign)
            star_audit={"status":"calculated","symbol":name,
                        "tier":chosen["strength_label"],
                        "polarity":sign,"score":star_score,
                        "scope":"health_role_not_general_star_definition"}
    door=detail["door"]
    # User says 八门有两种情况, but the question does not define either
    # situation's auspice conditions. Exact tier is still usable as a fact.
    door_audit={"status":"two_door_conditions_missing",
                "symbol":door["symbol"] if door else None,
                "strength":door.get("strength_label") if door else None,
                "symbol_palace_relation":door.get("user_cell_col") if door else None}
    deity=detail["deity"]
    god_audit={
        "status":"deity_five_tier_conversion_missing",
        "symbol":deity["name"],"auspice":deity["polarity"],
        "nominal_relation":deity["relation"],
        "month_stage_is_not_used":True}
    # An 81 title is evidence that the ordered pair occurred, NOT that
    # its actual 吉凶 predicate was fully true in the user inquiry.
    patterns=[]
    for pair in detail["ordered_book_81_pairs"]:
        patterns.append({
            "fact_id":pair["fact_id"],"name":pair["name"],
            "status":"source_pattern_auspice_and_gate_pending",
            "eligible":pair["can_vote"],
            "reason":pair["reason"],
            "source_line_internal":pair["source_line_internal"],
            "source_sha256_internal":pair["source_sha256_internal"]})
    pattern_audit={"status":"pattern_full_source_gate_and_polarity_pending",
                   "matches":patterns,"default_tier":"中等",
                   "verified_81_pattern_count":sum(1 for p in patterns if p["eligible"])}
    # Always inspect strength data for real heavenly stems and Earth stem,
    # but do not invent 81 吉/凶 conversion before the source gating.
    summary=palace_tally(
        factors={"star":star_score,"door":None,"deity":None,"pattern":None},
        door_break=bool(door and door.get("user_cell_col")=="门破"),
        five_not_encounter=bool(five_not_encounter),
        void_state=detail["void"]["classification"],
        horse_cleared_void=bool(detail["void"].get("horse_cleared_void")))
    return {"role":role,"palace":detail["palace"],
            "star":star_audit,"door":door_audit,
            "deity":god_audit,"pattern":pattern_audit,
            "real_heaven_stem_facts":detail["heaven_stems"],
            "real_earth_stem_fact":detail["earth_stem"],
            "palace_score":summary,
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
                   "个宫缺完整门／神／格局转换来源")
    if summary["needs_final_band_rule"]:
        sub.append("跨宫累计分已超五级范围，最终分档规则未定")
    return ("五级宫内量化已建立逐宫审查；"+
            "，".join(sub or ["最终分档待核"])+"，"+
            "暂不生成虚构的极大吉／极大凶最终结论。"+
            "旧版按吉凶证据条数的合断只作定性对照。")
