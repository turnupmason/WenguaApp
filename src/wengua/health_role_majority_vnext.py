"""One source-qualified symbolic direction PER selected role-to-illness group.

Only the user-registered health severity roles are candidates. A matched
control 5x5 grid is consulted at most once in the ACTUAL control direction;
nominal 五行生/同宫 does not silently become a fabricated control outcome.
Physical pairs are deduplicated; one doctor+medicine co-palace is not two votes.
Candidate signed scoring is implemented independently; this legacy evidence
vote is preserved as explanation, NOT a replacement for raw ±5 user score.
"""
from __future__ import annotations

from .selected_duel_table_vnext import (
    matchup,CONTROL_CONFIDENT,CONTROL_LIMITED)
from .health_palace_detailed_vnext import void_kwargs

GROUP_ROLES=("doctor","medicine","patient","hour","natal","gender","chief")
CONTROL_IMPAIRED=frozenset((
    "克制失效","完全失控","系统性失控","反侮受损","终极解体","丧失能力",
))
ELIGIBLE_CONFIDENCE=frozenset((
    "source_case_specific","user_explicit_direction_verified_by_actual_chart",
))


def assess_disease_relationships(*,roles,edges,role_confidence):
    """Return auditable per-role interpretations and one majority vote/pair.

    One role-pair can have one control result ONLY if a real 克 direction
    exists. For the inverse relationship, illness is the actual source
    (not a second fight between unrelated palace strengths).
    """
    reviews={}
    evidence={"favorable":[],"adverse":[],"pending":[]}
    votes={}
    candidates={}
    for key in roles:
        if key=="illness":continue
        if not (key in GROUP_ROLES or key.startswith("extra_")):continue
        item=roles[key]
        if key=="gender" and item["role"]!="乾坤性别辅助宫":continue
        edge=edges.get(key+"->illness")
        if edge is None:continue
        relation=edge["relation"]
        actual=edge
        # With 病宫克本方: check illness's actual 克 role with illness as
        # SOURCE, not by pretending the role's source strength restrains disease.
        if relation=="被克":
            actual=matchup(roles["illness"]["primary_strength_25"],
                           item["primary_strength_25"],
                           actor_role="illness",target_role=key,
                           **void_kwargs(roles["illness"]["complete_palace"],
                                         item["complete_palace"]))
        outcome=actual["control_result"]
        decided="pending";why=""
        if relation in ("克","被克"):
            if actual["control_status"]!="matched":
                why="克制矩阵不能核定："+str(actual["control_status"])
            elif actual["ability"]=="条件待核":
                why="存在入墓／击刑／门迫等其他条件，克制原格保留但不直接计票"
            elif outcome in CONTROL_CONFIDENT or outcome in CONTROL_LIMITED:
                decided="favorable" if relation=="克" else "adverse"
                why=("本方制病" if relation=="克" else "病宫制本方")+"："+str(outcome)
            elif outcome in CONTROL_IMPAIRED:
                # A failed attempt to control disease is not evidence that
                # disease has become more severe; avoid a false negative vote.
                decided="pending"
                why="本宫名义相克但实际克制难落实："+str(outcome)
            else:
                why="克制原格未归类，保留候选："+str(outcome)
        elif relation in ("生","被生","同宫","比和"):
            # These directions are actual physical facts, not a second
            # strength duel and not an invented +3 or a certainty of harm.
            # Both real role symbols retain their own original 200-cell
            # strengths, even if doctor and medicine share a palace.
            ap=item["primary_strength_25"].get("strength_label") or "待核"
            bp=roles["illness"]["primary_strength_25"].get("strength_label") or "待核"
            why=("真实关系"+relation+"；本方用神力量"+ap+
                 "，天芮病星力量"+bp+
                 "；没有单独验证的本关系结果积分矩阵，不把方向当作已经成功施力")
        
        else:
            why="来源关系未核"
        phy=edge["physical_relation_id"]
        review={
            "role_key":key,"role":item["role"],"palace":item["palace"],
            "illness_palace":roles["illness"]["palace"],"relation":relation,
            "direction":decided,"why":why,
            "energy":item["primary_strength_25"]["strength_label"],
            "target_energy":roles["illness"]["primary_strength_25"]["strength_label"],
            "god_tendency":item["complete_palace"]["deity"]["polarity"],
            "void":item["void_classification"],
            "control_status":actual["control_status"],
            "control_result":outcome,
            "control_scenario":actual["control_scenario"],
            "actual_control_source":actual["actor"],
            "physical_relation_id":phy,
            "counts_once_per_physical_pair":True,
            "not_clinically_valid":True}
        reviews[key]=review
        # Evaluate ALL different selected symbols in a shared physical
        # palace independently. Merge only their evidence vote afterward:
        # a weak Tianxin cannot hide the independently successful Yi there.
        candidates.setdefault(phy,[]).append(key)
    for phy,keys in candidates.items():
        # An actually verified signifier takes precedence over the first
        # pending role alias. Different physical palaces still vote once.
        rank={"favorable":2,"adverse":2,"pending":0}
        chosen=max(keys,key=lambda k:rank.get(reviews[k]["direction"],0))
        votes[phy]=chosen
        for key in keys:
            reviews[key]["counted_in_majority"]=key==chosen
            if key!=chosen:reviews[key]["dedup_of"]=chosen
        selected=reviews[chosen]
        direction=selected["direction"]
        evidence[direction].append({
            "id":"relationship_group:"+phy,
            "edge_id":chosen+"->illness",
            "direction":direction,
            "roles":[reviews[k]["role"] for k in keys],
            "independent_role_reviews":[
                {"role":k,"strength":reviews[k]["energy"],
                 "direction":reviews[k]["direction"],
                 "control_result":reviews[k]["control_result"]}
                for k in keys],
            "why":selected["why"],
            "source":"user_200_cell_domain_selected_research_only",
            "group_dedup":True})
    qualified=role_confidence in ELIGIBLE_CONFIDENCE
    n_good=len(evidence["favorable"])
    n_bad=len(evidence["adverse"])
    state=("favorable" if n_good>n_bad else
           "adverse" if n_bad>n_good else "unresolved")
    if not qualified:state="unresolved"
    return {
        "reviews":reviews,"evidence":evidence,
        "decisive_state":state,
        "selection_confident":qualified,
        "reason":("已核角色逐组判定，按不重复实际物理关系的吉凶条数比较"
                  if qualified else
                  "患者用神身份仍为候选，不能拿其关系数量断死活"),
        "counted_physical_pairs":sorted(votes),
        "favorable":n_good,"adverse":n_bad,
        "pending":len(evidence["pending"]),
        "no_numerical_severity_score":True,
    }
