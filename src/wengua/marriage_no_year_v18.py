"""V1.8 optional-nianming author method: a missing birth year is NOT a blocker.

Read original author rule at Shenqi marriage ch2 l5/l9/l11/l54/l107,
Kaiwu marriage l39/l75/l79/l281/l285. Resolve usable symbols from real
heavenly chart, not invented birth years.  Birth year participates when
provided; no-year is a separate AUTHOR METHOD PATH and never makes up an
actor's gender, state of mind, medical condition, or future outcome.
Old V1.6/V1.7 source-case decisions/errors are immutable and retained.
"""
from __future__ import annotations
from pathlib import Path
import hashlib
import json
import sqlite3
from .marriage_runtime import ELEMENTS,element_relation,inspect_marriage_chart_json
from .marriage_book_combinator_v17 import (
    analyze_marriage_v17,compute_author_combinations,load_author_source_rules)
from .marriage_judgment_v16 import _source_witnesses,_load_rules_and_source
from .astro_calendar import branch_periods,EPHEMERIS_VERSION
from .timing_engine import derive_timing_candidates
from .book_timing_runtime import load_source_timing_rules
ROOT=Path(__file__).resolve().parents[2]
KAIWU=ROOT/"sources/kaiwu/开悟之门_恋爱婚姻预测.txt"
SHENQI_HASH="64c7e9c1c0e646814c11644809277f71587d21736bdbd49679e6ad65611303c9"
KAIWU_HASH="4df9dfe432daec759df4f0e01449bc4a2381eb4251e1290a0d99d199e467fa01"
SOURCE_LINES={"shenqi":[5,9,11,54,107],"kaiwu":[39,75,79,281,285]}
POSITIVES={"比和","生","受生"}
NEGATIVES={"克","受克"}

def _original_rules(db):
    """Verify line existence against exact original chapter source SHA."""
    shenqi=db.execute("""SELECT original_text,sha256 FROM sections
        WHERE book_id='shenqi' AND section_key='marriage_prediction_ch02'""").fetchone()
    if not shenqi or shenqi[1]!=SHENQI_HASH:
        raise ValueError("Missing original Shenqi marriage method text and SHA")
    if hashlib.sha256(shenqi[0].encode("utf8")).hexdigest()!=SHENQI_HASH:
        raise ValueError("Shenqi original-text SHA mismatch")
    raw=KAIWU.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=KAIWU_HASH:
        raise ValueError("Kaiwu original marriage SHA mismatch")
    lines={"shenqi":shenqi[0].splitlines(),"kaiwu":raw.decode("utf8").splitlines()}
    result={}
    for book,nums in SOURCE_LINES.items():
        for n in nums:
            if n>len(lines[book]) or not lines[book][n-1].strip():
                raise ValueError(f"{book} original source line {n} missing")
            item=lines[book][n-1]
            result[f"{book}.line{n}"]={
                "book_id":book,"section_key":("marriage_prediction_ch02" if book=="shenqi"
                                   else "marriage_prediction_ch02_section02"),
                "line":n,"whole_chapter_sha256":(SHENQI_HASH if book=="shenqi" else KAIWU_HASH),
                "original_line_sha256":hashlib.sha256(item.encode("utf8")).hexdigest(),
                "source_excerpt":item}
    # Guard directly against arbitrary "年命必需" policy: l11 says兼看年命,
    # whereas l5 already establishes 乙庚、六合 without an asserted birth year.
    if "乙" not in result["shenqi.line5"]["source_excerpt"] or "庚" not in result["shenqi.line5"]["source_excerpt"]:
        raise ValueError("No original marriage basic yongshen source at line5")
    return result

def _person_year(base,role):
    actor=base["actual_year_stem_candidate_binding"].get(role,{})
    if actor.get("status")!="year_stem_palace_candidate_only_not_selected_primary_yongshen":
        return None
    locations=actor.get("candidate_palace_cells",[])
    if len(locations)!=1:return None
    p=locations[0]["palace"]
    return p if p!=5 else None

def _sole_palace(base,key):
    v=base["role_candidates_not_final_yongshen"].get(key,[])
    return v[0]["palace"] if len(v)==1 and v[0]["palace"]!=5 else None

def _signal(a,b,role,book_ref):
    if a is None or b is None:return None
    rel=element_relation(ELEMENTS[a],ELEMENTS[b])
    return {"role":role,"from_palace":a,"to_palace":b,
            "from_element":ELEMENTS[a],"to_element":ELEMENTS[b],
            "five_element_relation":rel,
            "direction":("support" if rel in POSITIVES else "counter"),
            "source_ref":book_ref,
            "not_a_verified_real_world_personality_judgment":True}

def _bound_person_roles(payload,base,original_rules):
    inquiry=payload["inquiry"]
    relationship=inquiry.get("relationship")
    subj=_person_year(base,"subject")
    partner=_person_year(base,"partner")
    male=_sole_palace(base,"geng_traditional_candidate")
    female=_sole_palace(base,"yi_traditional_candidate")
    liuhe=_sole_palace(base,"liuhe")
    day=_sole_palace(base,"day_stem_palaces")
    hour=_sole_palace(base,"hour_stem_palaces")
    if liuhe is None:
        raise ValueError("Cannot invent missing central or duplicated 六合 palace")
    # Year is an optional overlay: never create a fake year, force genders,
    # or treat a day/hour event coordinate as a named partner.
    subj_is_known=subj is not None
    partner_is_known=partner is not None
    actor_mode=("both_years" if subj_is_known and partner_is_known else
                "one_year_optional" if subj_is_known or partner_is_known else
                "no_year_optional")
    author_sources=[
        original_rules["shenqi.line5"],
        original_rules["shenqi.line11"] if subj_is_known or partner_is_known else original_rules["shenqi.line54"],
        original_rules["kaiwu.line281"],
        original_rules["kaiwu.line285"]]
    return {
        "strategy":actor_mode,"relationship":relationship,
        "subject_year_palace":subj,
        "partner_year_palace":partner,
        "missing_year_does_not_create_missing_person_error":True,
        "day_palace_not_necessarily_subject":day,
        "hour_palace_is_event_not_automatically_partner":hour,
        "yi_traditional_partner_symbol":female,"geng_traditional_partner_symbol":male,
        "liuhe_marriage_symbol":liuhe,
        "source_rule_links":author_sources,
        "birth_year_supplement_used_only_when_supplied":subj_is_known or partner_is_known,
        "sexual_orientation_and_actual_gender_never_inferred":True
    }

def _fallback_decision(base,role,source_rules,combo):
    """Compare independent author symbols without an arbitrary points system."""
    yi,geng=role["yi_traditional_partner_symbol"],role["geng_traditional_partner_symbol"]
    liuhe=role["liuhe_marriage_symbol"]
    day,hour=role["day_palace_not_necessarily_subject"],role["hour_palace_is_event_not_automatically_partner"]
    if None in (yi,geng,liuhe,day,hour):
        return {"outcome":"unresolved","role_mode":role["strategy"],
                "support":[],"counter":[],"why":"original symbol carrier or source-specific center hosting unresolved"}
    supporting=[];counter=[]
    # Source line 5 defines the 乙庚/六合 traditional relation; it does NOT
    # prove these generic symbols are the actual two humans involved.
    primary=_signal(geng,yi,"traditional_乙庚_relation_not_two_known_people",
                    source_rules["shenqi.line5"])
    event=_signal(day,hour,"day_querent_and_hour_event_only",
                  source_rules["kaiwu.line281"])
    liuhe_to_yi=_signal(liuhe,yi,"liuhe_to_乙",
                       source_rules["shenqi.line5"])
    liuhe_to_geng=_signal(liuhe,geng,"liuhe_to_庚",
                         source_rules["shenqi.line5"])
    srcs=[primary,event,liuhe_to_yi,liuhe_to_geng]
    for r in srcs:
        (supporting if r["direction"]=="support" else counter).append(r)
    role_mode=role["strategy"]
    # If exactly one person's year is known, use it ONLY as specific
    # corroboration/contra; never treat missing partner year as required.
    actual=role["subject_year_palace"] or role["partner_year_palace"]
    if actual is not None:
        x=_signal(liuhe,actual,"liuhe_to_known_actor_year",
                  source_rules["shenqi.line11"])
        (supporting if x["direction"]=="support" else counter).append(x)
    # All three independently justified families (乙庚, 日时, 六合)
    # must corroborate before giving a determinate reading. Mixed evidence
    # remains mixed; neither "all positive" nor "all negative" implies
    # science-based certainty.
    event_support=event["direction"]=="support"
    primary_support=primary["direction"]=="support"
    all_marriage_support=(liuhe_to_yi["direction"]=="support"
                          and liuhe_to_geng["direction"]=="support")
    all_marriage_counter=(liuhe_to_yi["direction"]=="counter"
                          and liuhe_to_geng["direction"]=="counter")
    if primary_support and event_support and all_marriage_support:
        outcome="success"
    elif not primary_support and not event_support and all_marriage_counter:
        outcome="failure"
    else:
        outcome="mixed"
    # A single source condition must NOT get a 100% definite outcome.
    crucial={yi,geng,liuhe,day,hour}
    direct_conflicts=[
       r for category in ("six_yi_striking_punishment","sanqi_tomb",
                          "door_pressure_strength")
       for r in combo["source_rule_matches"][category]
       if r["palace"] in crucial and
          not (category=="door_pressure_strength" and
               r.get("qualifier",{}).get("force")=="blocked_by_month_strength")]
    if outcome=="success" and direct_conflicts:outcome="mixed"
    if outcome=="success" and (
        combo["fu_yin_fan_yin"]["star_fanyin"] and
        combo["fu_yin_fan_yin"]["door_fanyin"]):outcome="mixed"
    return {
        "outcome":outcome,"role_mode":role_mode,
        "support":supporting,"counter":counter,
        "special_palace_counterevidence":direct_conflicts,
        "source_rule_precedence":[
            "inference_question_person_identity_first_no_fabricated_year",
            "乙庚_symbolic_traditional_couple",
            "六合_marriage_situation_bidirectional",
            "day_hour_question_and_event_not_spouse",
            "known_birth_year_only_as_available_overlay",
            "independent_source_击刑入墓门迫反吟_counterevidence"],
        "case_specific_past_author_answer_not_loaded":True,
        "traditional_interpretation_not_real_world_verification":True,
        "missing_birth_year_not_a_decision_failure":True}

def analyze_marriage_v18(*,db_path,payload,held_out_family_id=None):
    """Actual chart, no required year, no case-answer leakage, no invented dates."""
    base=inspect_marriage_chart_json(db_path=db_path,payload=payload)
    if not base["calendar_independently_verified"]:
        return {"status":"blocked_calendar_not_verified","publication_ready":False,
                "reason":"Requires local time+IANA zone for confirmed source cast"}
    with sqlite3.connect(f"file:{Path(db_path).resolve()}?mode=ro",uri=True) as db:
        refs=_original_rules(db)
        witness=_source_witnesses(db,payload["inquiry"]["scene_id"],
                                 held_out_family_id=held_out_family_id)
    if not witness["pre_event_method_witnesses"]:
        return {"status":"blocked_no_nonheldout_source_method_witness",
                "heldout_family_id":held_out_family_id,"publication_ready":False}
    role=_bound_person_roles(payload,base,refs)
    combo=compute_author_combinations(base["source_chart"],
                                     base["astronomical_local_calendar_receipt"])
    if role["strategy"]=="both_years":
        prior=analyze_marriage_v17(db_path=db_path,payload=payload,
                                   held_out_family_id=held_out_family_id)
        judgment=prior.get("judgment",{})
        outcome=prior.get("traditional_initial_outcome","unresolved")
        compat_timing=prior.get("conditionally_defensible_timing")
        method="v17_author_book_with_actual_year_coordinates"
    else:
        judgment=_fallback_decision(base,role,refs,combo)
        outcome=judgment["outcome"]
        compat_timing=None
        method="original_author_乙庚_六合_日时_without_required_year"
    # Require source-applied condition before calculating a selected period.
    # The old generic 乙庚 heuristic cannot take an unspecified person's
    # birth year, and it cannot infer an unasked event (e.g. affair).
    clock=base["astronomical_local_calendar_receipt"]
    period=None
    liuhe_branches=set(base["factor_audit"]["xun_kong"]["evidence"]["xun_kong_branches"])
    from .marriage_runtime import PALACE_BRANCHES
    active_void=sorted(set(PALACE_BRANCHES[role["liuhe_marriage_symbol"]]) & liuhe_branches)
    timing_candidates=[]
    if outcome in ("success","failure") and active_void:
        timemethod="clash_empty" if outcome=="success" else "fill_empty"
        key="successful_outcome:4" if outcome=="success" else "failed_outcome:3"
        source=load_source_timing_rules()[key]
        windows=branch_periods(payload["calendar_inputs"]["local_time_iso"],
                               payload["calendar_inputs"]["iana_timezone"],
                               granularity="month",days_ahead=370)
        timing_candidates=derive_timing_candidates(
            empty_branches=active_void,periods=windows,granularity="month",
            method=timemethod,reference_iso=payload["calendar_inputs"]["local_time_iso"],
            calendar_method_version=EPHEMERIS_VERSION,calendar_receipt=clock["sha256"],
            source_method_ref=f"kaiwu/analysis_judgment_ch04/v1:line{source['source_line']}")
        if timing_candidates:period=timing_candidates[0]
    # Only source-matched, non-ambiguous period; don't invent a period for a
    # scene with no precise event or no usable trigger. "mixed" is not a date.
    if outcome=="mixed" or outcome=="unresolved":
        period=None
    return {
        "status":"v18_source_author_initial_decision_no_year_optional",
        "scene_id":base["scene_id"],"question":base["actual_input_inquiry"]["question_text"],
        "year_role_binding":role,"decision_engine":method,
        "traditional_initial_outcome":outcome,
        "evidence_decision":judgment,
        "source_multi_factor_conditions":combo,
        "source_rule_refs":refs,
        "prior_method_witness_holdout":witness,
        "source_conditioned_timing_candidates":timing_candidates,
        "primary_timing_if_justified":period,
        "legacy_v17_prior_timing_retained_only_if_same_verdict":(
            compat_timing is not None and compat_timing.get("outcome")==outcome),
        "no_year_caused_block":False,
        "missing_year_no_year_value_invented":True,
        "author_future_feedback_used_in_initial_decision":False,
        "complete_all_24_source_factors_not_yet_proven":True,
        "suitable_for_independent_real_world_accuracy_claim":False,
        "publication_ready":False,
        "cannot_make_specific_person_attitude_claim_without_identification":True,
        "gpt_full_200_character_phrase_enabled":False,
        "next_required_validation":"all_24_original_rules_and_untouched_event_family_holdout"}
