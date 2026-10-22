"""V4.1 research candidate: user-proposed ALL 81 heavenly/earth weights with
AUTHOR-SOURCE illness-specific semantic gates and PHYSICAL palace roles.

Never automatically invert a disease-palace sign. Source book specifically
says 戊丙、丙戊 are generally lucky but traditionally illness-adverse.
Book specifically says 丙辛 illness favorable, versus user's chronic=-15.
Missing duration, role, conditional door/status => UNDECIDED/UNSCORED.
Outputs every matched candidate; author line and SHA only in INTERNAL audit.
No verified clinical score/probability; old V3.9 and V4.0 archives immutable.
"""
from __future__ import annotations
import json,re
from pathlib import Path
from .health_symbolic_score_v40 import calculate_health_symbolic_score_v40
from .health_severity_v22 import _find_star,_find_heaven_stem
from .health_dynamic_v21 import bind_patient
from .health_severity_v37 import actual_81_pair_context,load_81_book_pairs

ROOT=Path(__file__).resolve().parents[2]
CONFIG=ROOT/"data/knowledge/score_models/health_severity_v41/ordered81_user_weight_candidates.json"
SUPPLEMENTS=ROOT/"data/knowledge/phrase_library/health_v30/user_20261022_pair_catalog.json"

def all81_proposed():
    cfg=json.loads(CONFIG.read_text("utf8"))
    book=load_81_book_pairs()
    x=cfg["candidate_pairs"]
    assert len(x)==len(book)==81
    assert len(set(z["pair_key"] for z in x))==81
    for row in x:
        assert row["pair_key"] in book
        assert row["pair_key"]==row["top"]+"/"+row["bottom"]
        assert row["proposed_points"] is not None or row.get("duration_points")
    return cfg,{z["pair_key"]:z for z in x}

def _author_disease_direction(source):
    # Source-specific disease meaning is distinct from generic "好事" luck.
    if re.search(r"测(?:人)?疾病也不凶",source):
        return "traditional_illness_favorable"
    if re.search(r"测病也主凶|测病遇此格|测疾病.{0,30}不仅不吉|如测疾病.{0,60}显示病重|主男女疾病垂危|测病亦大凶",source):
        return "traditional_illness_adverse"
    return "not_explicitly_health_qualified"

def _safe_proposal(key,proposal,source,duration):
    if proposal.get("requires_duration") and duration not in ("new","chronic"):
        return (None,"requires_original_new_or_chronic")
    val=proposal.get("duration_points",{}).get(duration) if proposal.get("duration_points") else proposal["proposed_points"]
    if val is None:return (None,"unprovided_duration_weight")
    explicit=_author_disease_direction(source)
    if explicit=="traditional_illness_favorable" and val<0:
        return (None,"source_vs_user_negative_conflict")
    if explicit=="traditional_illness_adverse" and val>0:
        return (None,"source_vs_user_positive_conflict")
    return (int(val),"eligible_value_if_role_and_other_book_conditions_supported")

def _same_role_roles(chart,patient,ill,doctor,yi,hour):
    return {"patient":patient["palace"],"illness":ill["palace"],
            "doctor":doctor["palace"],"medicine":yi["palace"],
            "event":hour["palace"]}

def audit_scoring_81(*,chart,inquiry,calendar):
    """Author books ALWAYS outrank user proposal for health; store disagreements."""
    if not calendar or "month_branch" not in calendar:
        raise ValueError("True calendar required, no invented year/medical detail")
    conf,requested=all81_proposed()
    p=bind_patient(chart,inquiry,calendar)["main_cell"]
    ill,_=_find_star(chart,"天芮星")
    doctor,_=_find_star(chart,"天心星")
    yi=_find_heaven_stem(chart,"乙")
    hour=_find_heaven_stem(chart,chart["hour_ganzhi"][0])
    if any(v is None for v in (p,ill,doctor,yi,hour)):
        raise ValueError("Incomplete real source actor/chart")
    actual=actual_81_pair_context(chart,p,ill,doctor,yi,hour)
    supplement=json.loads(SUPPLEMENTS.read_text("utf8"))
    suppl={r["heaven"]+"/"+r["earth"]:r for r in supplement["pairs"]}
    if len(suppl)!=42:raise ValueError("Preserve 42 supplemental medically themed conditions")
    duration=inquiry.get("illness_duration")
    out=[];signed=[];used=set()
    roles=_same_role_roles(chart,p,ill,doctor,yi,hour)
    for a in actual:
        req=requested[a["pair_key"]]
        key=a["pair_key"]
        source=a["source_original"]
        book=_author_disease_direction(source)
        val,val_status=_safe_proposal(key,req,source,duration)
        priority_role=None
        for role in ("patient","illness","doctor","medicine","event"):
            if roles[role]==a["palace"]:
                priority_role=role
                break
        # Only the genuine Tianrui star's carried stem gets the primary
        # illness role. A Tianqin companion in SAME palace is separately
        # audited and may not produce a second illness score.
        if priority_role=="illness" and a["star"]!="天芮星":
            priority_role="illness_companion_unscored"
        same_palace_tag=(a["palace"],key)
        status="source_condition_unresolved"
        final_delta=0
        if same_palace_tag in used:status="duplicated_same_palace_source_pair"
        elif priority_role=="illness_companion_unscored":
            status="illness_companion_only_no_double_vote"
        elif val is None:
            status=val_status
        elif book=="not_explicitly_health_qualified":
            status="no_specific_health_semantics_do_not_invert_or_medicalize"
        elif book=="traditional_illness_favorable" and val>0:
            # An explicit book health benefit can be counted, including
            # illness palace with NO sign inversion. Default duration
            # qualifier must still be observed.
            status="book_illness_favorable_and_user_sign_aligned"
            final_delta=val
        elif book=="traditional_illness_adverse" and val<0:
            status="book_illness_adverse_and_user_sign_aligned"
            final_delta=val
        else:status="book_and_user_sick_question_disagree"
        # Enforce source action prerequisites after any polarity selection.
        if final_delta and ("门迫" in source or "击刑" in source or "入墓" in source):
            # A conditional “unless impaired” qualification is present, but
            # the point value wasn't independently tuned to it. Mark unknown
            # unless all gates are separately verified in a future version.
            status="conditional_star_door_punishment_tomb_gate_pending"
            final_delta=0
        # Actual stem-pair is matched via real star's carried stem and earth;
        # no substitution of a source *alias* in place of the author.
        if final_delta:
            used.add(same_palace_tag)
            signed.append({"rule_id":"v41_pair_"+key.replace("/","_"),"family":"original_81_book_pair",
                "palace":a["palace"],"star":a["star"],"role":priority_role,
                "source_qualified":book,"points":final_delta,
                "source_pair_key":key})
        s=suppl.get(key)
        out.append({
            "matched_actual_palace":a["palace"],"matched_actual_star":a["star"],
            "actual_role":priority_role,
            "ordered_pair":key,"source_book_name":a["title"],
            "user_proposed_alias":req["user_alias"],
            "user_proposed_numeric_weight":req["proposed_points"],
            "user_proposed_duration_weights":req.get("duration_points"),
            "original_book_health_semantics":book,
            "supplement_source_id":s["id"] if s else None,
            "supplement_mode":s["mode"] if s else None,
            "source_line_internal_only":a["source_line"],
            "source_sha256_internal_only":a["source_sha256"],
            "match_status":status,
            "applied_delta":final_delta,
            "source_is_clinically_validated":False
        })
    if len(out)!=9:
        raise ValueError("Expected precisely 9 real heavenly-star stems, including Tianqin companion")
    return {"source_81_total":81,"supplement_42_total":42,
        "matched_real_star_pairs":out,"eligible_book_explicit_ledger":signed,
        "applied_pair_total":sum(z["points"] for z in signed),
        "unscored_pair_count":sum(z["applied_delta"]==0 for z in out),
        "not_an_unconditional_81_pair_multiplier":True}

def calculate_health_symbolic_score_v41(*,chart,inquiry,calendar):
    base=calculate_health_symbolic_score_v40(chart=chart,inquiry=inquiry,calendar=calendar)
    cfg,pairs=all81_proposed()
    audit=audit_scoring_81(chart=chart,inquiry=inquiry,calendar=calendar)
    previous=base["ledger"]
    # V4.0 already used ORIGINAL bad patient formation as part of its
    # double-adverse interaction. Once an explicit pair gets its own -20,
    # remove V4.0's -8 interaction to avoid counting this evidence twice.
    patient_pair_adverse=any(z["role"]=="patient" and z["points"]<0
       for z in audit["eligible_book_explicit_ledger"])
    removed=[]
    if patient_pair_adverse:
        removed=[z for z in previous
            if z["id"]=="double_adverse_distinct_chain_penalty"]
        previous=[z for z in previous
            if z["id"]!="double_adverse_distinct_chain_penalty"]
    adjusted=list(previous)+audit["eligible_book_explicit_ledger"]
    signed=sum(z["points"] for z in adjusted)
    raw=base["baseline"]+signed
    return {
        "schema":"wengua_health_v41_original_81_book_constrained_scoring_prototype",
        "version":"V4.1","status":"draft_awaiting_user_source_review",
        "score_label":"古籍病势象意实验分，不是医学健康指数或概率",
        "baseline":100,"previous_v40_raw":base["raw_score"],
        "previous_v40_visible":base["display_score_0_100"],
        "revised_raw_score":raw,"revised_display_score":max(0,min(100,raw)),
        "source_constrained_pair_increment":audit["applied_pair_total"],
        "removed_duplicate_interactions":removed,
        "evidence_ledger":adjusted,"book_pair_source_audit":audit,
        "source_uncertainties":base["unscored_unknowns"]+
            [{"id":"81_source_pair_role_conditions_pending",
              "reason":"81天盘地盘原文是领域通用知识，并非全部具有明确测病分值"}],
        "actual_medical_risk_probability":None,
        "real_health_or_treatment_outcome_predicted":False,
        "users_81_weights_signed_off":False,
        "old_v39_and_v40_outputs_unchanged":True,
        "historical_book_feedback_seen_by_model":False
    }
