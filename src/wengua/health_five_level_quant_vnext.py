"""User's NEW 2026-10-24 five-grade signed *traditional-symbolic* tally.

This is a SEPARATE, explicitly new candidate method, NOT resurrecting discarded
V4.2 scores, NOT changing frozen V3.9.1, and NOT a medical diagnosis.

Transparent +1..+5 for 吉, -1..-5 for 凶, 0 exclusively neutral/假空.
Only actually grounded symbol polarity with a real five-level energy enters\na resolved current score. Neutral doors are explicit zero; same-palace\nstars and actual ordered pairs are preserved individually, never clamped.
"""
from __future__ import annotations

TIERS=("极小","小","中等","大","极大")
POINT={name:i+1 for i,name in enumerate(TIERS)}
SIGNS={"吉":1,"凶":-1}
STAGE_EXTREME=frozenset(("长生","冠带","临官","帝旺","沐浴"))
STAGE_LARGE=frozenset(("胎","养"))
VERSION="user_health_five_grade_signed_20261025_v3_void_mitigates_and_restores"


def points(tier,polarity):
    if tier not in POINT or polarity not in SIGNS:
        raise ValueError("Need an explicit five-tier grade AND 吉/凶 source")
    return POINT[tier]*SIGNS[polarity]


def label(score):
    """Literal five labels from -5..+5; 0 is zero, not false auspiciousness."""
    if not isinstance(score,int) or isinstance(score,bool) or abs(score)>5:
        raise ValueError("One grade must be an integer between -5 and +5")
    if score==0:return "中性0分"
    return TIERS[abs(score)-1]+("吉" if score>0 else "凶")


def saturate(score):
    """User-confirmed final grade: <=-5 always 极大凶; >=+5 极大吉.

    Preserve the pre-saturation signed sum independently for auditing.
    """
    if not isinstance(score,int) or isinstance(score,bool):
        raise ValueError("Raw score must be integer")
    return max(-5,min(5,score))


def downgrade_strength(tier,levels):
    if tier not in POINT or not isinstance(levels,int) or levels<0:
        raise ValueError("Only explicit five-tier downgrade steps")
    return TIERS[max(0,POINT[tier]-1-levels)]


def pattern_grade(*,polarity,heaven_stage=None,heaven_tomb=False,
                  heaven_punishment=False,earth_tomb=False,
                  earth_punishment=False,source_gate_verified=False):
    """One verified 81 ordered 天盘+地盘格; never convert book name alone.

    Basic pattern potency = 中等 (3). Heaven long-life top group -> 极大 (5),
    胎/养 -> 大 (4). Remaining stages retain basic 中等 pending further
    source instruction; two actual-branch stages with DIFFERENT grade are
    not collapsed. Heaven and earth each independently lose 1 tier for
    tomb and 1 for punishment (never lower than 极小).
    """
    if polarity not in SIGNS:raise ValueError("Pattern needs sourced 吉/凶")
    if heaven_stage is None:
        options=(3,)
    elif isinstance(heaven_stage,str):
        stages=(heaven_stage,)
        options=tuple(dict.fromkeys(
            5 if s in STAGE_EXTREME else 4 if s in STAGE_LARGE else 3
            for s in stages))
    else:
        stages=tuple(heaven_stage)
        if not stages:raise ValueError("No actual heavenly stem stage")
        options=tuple(dict.fromkeys(
            5 if s in STAGE_EXTREME else 4 if s in STAGE_LARGE else 3
            for s in stages))
    if len(options)!=1:
        return {"status":"heaven_two_life_groups_pending","score":None,
                "candidate_base_tiers":[TIERS[i-1] for i in options],
                "source_gate_verified":source_gate_verified,
                "version":VERSION}
    step=int(bool(heaven_tomb))+int(bool(heaven_punishment))+(
         int(bool(earth_tomb))+int(bool(earth_punishment)))
    grade=max(1,options[0]-step)
    score=grade*SIGNS[polarity] if source_gate_verified else None
    return {"status":"calculated" if source_gate_verified else "source_gate_pending",
            "score":score,"candidate_score":grade*SIGNS[polarity],
            "base_tier":TIERS[options[0]-1],
            "after_restrictions_tier":TIERS[grade-1],
            "total_downgrade":step,
            "heaven_tomb":bool(heaven_tomb),
            "heaven_punishment":bool(heaven_punishment),
            "earth_tomb":bool(earth_tomb),
            "earth_punishment":bool(earth_punishment),
            "source_gate_verified":bool(source_gate_verified),
            "version":VERSION}


# User-authored 2026-10-24 explicit exceptions to the TWO-LEVEL
# 门破 penalty. These are still physical 门克宫 in the *200-cell* strength
# table. Exemption affects ONLY the extra -2 stage; neither door strength
# nor door auspice polarity is rewritten.
DOOR_BREAK_NO_PENALTY=frozenset({("生门",1),("景门",6)})
DOOR_BREAK_POLICY_VERSION="health_door_break_two_exception_cases_20261024_v1"


def door_break_penalty_policy(*,door_name,palace,door_relation):
    """Return literal user exception matched against a REAL palace and door.

    门克宫 may be recorded as 门破; only the two named real cases skip the
    separate two-level adverse shift. Other genuinely verified 门破 cases
    retain the existing shift; 宫迫 or 比和 never trigger that shift.
    Do NOT infer the door's 吉/凶 from the physical break alone.
    """
    if not isinstance(palace,int) or palace not in range(1,10):
        raise ValueError("Require actual numbered chart palace")
    if door_relation not in ("门破","宫迫","被宫生","生宫","比和"):
        raise ValueError("Only user-provided door/palace relation")
    actual=door_relation=="门破"
    exempt=actual and (door_name,palace) in DOOR_BREAK_NO_PENALTY
    return {
        "version":DOOR_BREAK_POLICY_VERSION,
        "door":door_name,"palace":palace,
        "raw_relation":door_relation,
        "has_door_break":actual,
        "no_extra_two_level_shift":exempt,
        "apply_extra_two_level_shift":actual and not exempt,
        "two_level_shift":0 if not actual or exempt else 2,
        "why":("生门落坎或景门落乾：虽门克宫（门破），按用户最新规则不额外降两级"
               if exempt else
               "实际门破按现有规则另外降两级" if actual else
               "非门破，不触发门破额外降级"),
        "door_month_palace_200_cell_strength_unchanged":True,
        "door_polarity_not_inferred":True,
    }


def adverse_shift(score,levels=2):
    """五不遇时/门破: 吉减两级(底=极小吉); 凶增两级(顶=极大凶).

    This signed FIVE-LEVEL adjustment is applied to a palace's grade, not
    a second fight and not 2 additional independent verdict votes.
    """
    if not isinstance(score,int) or isinstance(score,bool) or abs(score)>5:
        raise ValueError("Shift needs a resolved signed grade -5..5")
    if not isinstance(levels,int) or levels<0:raise ValueError("Levels >=0")
    if score>0:return max(1,score-levels)
    if score<0:return max(-5,score-levels)
    return 0


def void_shift_three(score,*,void_state):
    """User 2026-10-25 signed palace grade rule, identical TODAY for 真/假空.

    +2/-3 -> -1/0; -2/-3 -> +1/0. No made-up -5 extreme for true void.
    Timing is separate: fake may restore on 冲/填, true may not.
    """
    if not isinstance(score,int) or isinstance(score,bool) or abs(score)>5:
        raise ValueError("Void shift requires bounded integer palace score")
    if void_state not in ("not_void","fake_void","true_void"):
        raise ValueError("Void state must come from actual nine palace")
    if void_state=="not_void" or score==0:return score
    return score-3 if score>0 else score+3


def palace_tally(*,factors,door_break=False,five_not_encounter=False,
                 void_state="not_void",horse_cleared_void=False):
    """Current sign of a REAL palace, then an explicit +/-3 emptiness shift.

    Unresolved book-conditioned patterns should be provided as known zero by
    their source gate (not as proof a favourable pattern actually activates).
    Genuine missing required star/door/deity still remains unresolved rather
    than pretending it has zero force.
    """
    if void_state not in ("not_void","fake_void","true_void"):
        raise ValueError("Need actual real-chart void classification")
    if horse_cleared_void and void_state!="not_void":
        raise ValueError("Horse-cleared void must be not_void")
    if len(factors)!=4 or set(factors)!={"star","door","deity","pattern"}:
        raise ValueError("Need precisely star, door, deity, ordered pattern")
    seen={};unresolved=[];instances={}
    for k,v in factors.items():
        if v is None:
            unresolved.append(k);continue
        components=tuple(v) if isinstance(v,(list,tuple)) else (v,)
        if isinstance(v,(list,tuple)) and (k not in ("star","pattern") or not components):
            raise ValueError("Only star/pattern can contain multiple real scored items")
        for value in components:
            if (not isinstance(value,int) or isinstance(value,bool)
                or abs(value)>5):
                raise ValueError("Only a source-known signed energy tier or documented neutral factor")
        seen[k]=sum(components);instances[k]=list(components)
    subtotal=sum(seen.values())
    complete=not unresolved
    raw_sum=subtotal if complete else None
    # Separate established whole-chart adversity from each palace's empty
    # status; the historical adverse_shift semantics still exist unchanged.
    if not complete:
        final=None;before_void=None;status="incomplete_components"
    else:
        before_void=saturate(subtotal)
        if five_not_encounter:before_void=adverse_shift(before_void,2)
        if door_break:before_void=adverse_shift(before_void,2)
        final=void_shift_three(before_void,void_state=void_state)
        status=("void_signed_three_shift" if void_state!="not_void" else
                "saturated_five_grade" if abs(subtotal)>5 else "calculated")
    return {
        "version":VERSION,"status":status,"components":seen,
        "component_instances":instances,"known_neutral_door":factors.get("door")==0,
        "unresolved_categories":unresolved,"known_subtotal":subtotal,
        "raw_sum":raw_sum,"score_before_void":before_void,
        "void_adjustment":(final-before_void if final is not None else None),
        "void_adjustment_rule":"positive_minus_3_negative_plus_3_zero_unchanged",
        "five_not_encounter":bool(five_not_encounter),"door_break":bool(door_break),
        "void_state":void_state,"horse_cleared_void":bool(horse_cleared_void),
        "timing_can_refill_or_clash":(True if void_state=="fake_void" else
                                     False if void_state=="true_void" else None),
        "timing_rules_deferred":True,
        "score":final,"grade":label(final) if final is not None else None,
        "raw_sum_exceeds_five":raw_sum is not None and abs(raw_sum)>5,
        "saturated_from_raw":raw_sum if raw_sum is not None and abs(raw_sum)>5 else None,
        "score_is_research_only":True,
    }


def multi_palace_tally(*,palaces):
    """Selected distinct physical palaces only; sum POST-VOID palace scores.

    Full original source arithmetic is retained independently. A shared
    illness/chief or medicine/hour or Qian/role palace counts exactly once.
    """
    chosen={};duplicate=[]
    for role,row in palaces.items():
        pid=row["palace"]
        if pid in chosen:
            duplicate.append({"role":role,"palace":pid,
                              "already_counted_role":chosen[pid][0]})
        else:chosen[pid]=(role,row)
    pending=[str(pid) for pid,(_,row) in chosen.items()
             if row.get("score") is None]
    raw_known=sum(row.get("raw_sum") if row.get("raw_sum") is not None else
                  row.get("known_subtotal",0)
                  for _,row in chosen.values())
    actual_known=sum(row["score"] for _,row in chosen.values()
                     if row.get("score") is not None)
    score=saturate(actual_known) if not pending else None
    return {
        "version":VERSION,
        "status":"unresolved_palaces" if pending else
                 "saturated_five_grade" if abs(actual_known)>5 else "calculated",
        "raw_known_sum":raw_known,
        "post_void_known_sum":actual_known,
        "effective_palace_scores":{str(pid):row.get("score")
                                   for pid,(_,row) in chosen.items()},
        "raw_grade_if_all_known":label(score) if score is not None else None,
        "provisional_known_grade":label(saturate(actual_known)),
        "provisional_is_not_final":bool(pending),
        "pending_palaces":pending,
        "duplicate_physical_roles":duplicate,
        "unique_palace_count":len(chosen),"score":score,
        "grade":label(score) if score is not None else None,
        "needs_final_band_rule":False,
        "user_extreme_cutoff":5,
        "sum_after_each_palace_void_adjustment":True,
        "not_a_medical_assessment":True,
    }
