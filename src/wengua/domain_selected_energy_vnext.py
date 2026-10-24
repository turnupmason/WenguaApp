"""Select ONLY requested signifiers, then TABLE ONE, then TABLE TWO.

The actual nine-palace chart already exists. Domain + subtopic + original
patient relationship choose signifiers first. No full 9-palace × all-symbol
Cartesian product, no unconditional Qian+Kun, no fictional birth-life.
Other domains must register their verified own selection/interaction rules.
This is candidate ancient-symbolic reasoning, NOT medical guidance.
"""
from __future__ import annotations

from .selected_duel_table_vnext import table_one, matchup
from .factor_energy_25_rules import format_strength_template
from .health_severity_v22 import _find_star, _find_heaven_stem
from .health_dynamic_v21 import _cell
from .health_severity_v25 import fuyin_fanyin_facts
from .health_tianrui_25_matrix import inspect_tianrui_25
from .health_severity_v34 import HORSE
from .semantic_lookup import STAR_ELEMENT
from .health_palace_detailed_vnext import (
    inspect_complete_selected_palace,void_kwargs,render_complete_selected_palace)
from .health_role_majority_vnext import assess_disease_relationships
from .health_macro_facts_vnext import first_stage_macro,render_first_stage_macro
from .health_quant_overlay_vnext import inspect_selected_quantization,render_quant_review
from .marriage_runtime import ELEMENTS,element_relation

# Other subtopics will be added only when their original source conditions
# and relevant person-role bindings are implemented and tested.
DOMAIN_CASE_TEMPLATES = {
    ("health", "severity"): (
        "illness", "doctor", "medicine", "patient",
        "natal_if_provided", "hour", "gender_palace_if_known",
        "book_profile_auxiliary_if_bound",
    ),
}
# Exact domain choice of meaningful two-way relationships; not all pairs.
HEALTH_EDGES = (
    ("doctor","illness"),("doctor","patient"),
    ("medicine","illness"),("medicine","patient"),
    ("patient","illness"),("illness","patient"),
    ("natal","illness"),("natal","patient"),
    ("hour","illness"),("hour","patient"),
    ("gender","illness"),("gender","patient"),
)
# Interpret strong, domain-eligible edges only; neither the table nor
# the Qian/Kun sex correspondence automatically becomes a verdict vote.
HEALTH_POLARITY = {
    ("doctor","illness","克"): "favorable",
    ("medicine","illness","克"): "favorable",
    ("patient","illness","克"): "favorable",
    ("natal","illness","克"): "favorable",
    ("doctor","patient","生"): "favorable",
    ("medicine","patient","生"): "favorable",
    ("doctor","illness","生"): "adverse",
    ("medicine","illness","生"): "adverse",
    ("patient","illness","生"): "adverse",
    ("illness","patient","克"): "adverse",
}
ROLE_TITLES={"illness":"天芮病宫","doctor":"天心医生","medicine":"乙奇医药",
             "patient":"患者用神","natal":"患者年命","hour":"时干事体",
             "gender":"乾坤性别辅助宫"}


def selected_health_sequence(*,chart,calendar,actor,inquiry,matched_pairs=()):
    """Return existing V-next report contract with a SELECTIVE energy audit."""
    from .health_palace_sequence_vnext import inspect_palace
    if inquiry.get("intent")!="severity":
        raise ValueError("Only book-grounded health severity subtype is implemented")
    # First-stage global conditions are calculated immediately after casting,
    # BEFORE the domain-selected per-palace energy and 81-case analysis.
    macro_facts=first_stage_macro(chart=chart,calendar=calendar)
    month=calendar["month_branch"]
    schema=("health",inquiry["intent"])
    if schema not in DOMAIN_CASE_TEMPLATES:
        raise ValueError("No verified domain/subtopic selection template")
    raw={}
    ill,_=_find_star(chart,"天芮星")
    doc,_=_find_star(chart,"天心星")
    yi=_find_heaven_stem(chart,"乙")
    hour=_find_heaven_stem(chart,chart["hour_ganzhi"][0])
    patient=actor.get("main_cell")
    for k,c in (("illness",ill),("doctor",doc),("medicine",yi),
                ("patient",patient),("hour",hour)):
        if not c:raise ValueError("Actual chosen signifier palace missing: "+k)
    raw.update(illness=(ill,"star","天芮星"),
               doctor=(doc,"star","天心星"),
               medicine=(yi,"stem","乙"),
               patient=(patient,"stem",actor["stem"]),
               hour=(hour,"stem",chart["hour_ganzhi"][0]))

    natal_name=inquiry.get("patient_birth_ganzhi") or inquiry.get("subject_year_ganzhi")
    if natal_name and not actor.get("birth_cell"):
        # Jia hiding method or invalid placement has NOT been independently
        # resolved; don't fabricate a visible natal stem.
        missing_natal="provided_but_actual_stem_palace_unresolved"
    elif natal_name:
        raw["natal"]=(actor["birth_cell"],"stem",natal_name[0])
        missing_natal=None
    else:
        missing_natal="not_provided"

    sex=inquiry.get("patient_sex")
    if actor.get("relationship")=="wife":sex="female"
    if actor.get("relationship")=="husband":sex="male"
    if sex not in (None,"male","female"):
        raise ValueError("Gender must be male/female or omitted")
    gender_palace={"male":6,"female":2}.get(sex)
    if gender_palace is not None:
        cell=_cell(chart,gender_palace)
        if not cell:raise ValueError("Actual gender auxiliary palace absent")
        # Gender auxiliary is a PALACE observation, not an invented natal
        # or chosen medicine stem. Its resident star is the context anchor.
        resident=(cell["heaven_stars"][0]["star"] if cell["heaven_stars"]
                  else None)
        raw["gender"]=(cell,"star" if resident else "stem",
                       resident or cell["earth_stem"])

    used={t[0]["palace"] for t in raw.values()}
    bound_extras={x["palace"] for x in actor.get("extra_cells",()) if x}
    for palace in sorted(bound_extras):
        if palace in (2,6) and palace!=gender_palace:
            continue
        if palace in used:
            continue
        cell=_cell(chart,palace)
        if not cell or palace==5:
            continue
        raw["extra_"+str(palace)]=(cell,"stem",cell["earth_stem"])
        used.add(palace)

    inspected={}
    one_cache={}
    physical_inspections=set()
    for key,(cell,kind,symbol) in raw.items():
        index=cell["palace"]
        cachekey=(index,kind,symbol)
        if cachekey not in one_cache:
            record=inspect_palace(
                chart=chart,cell=cell,role=ROLE_TITLES.get(key,"原书辅助宫"+str(index)),
                month_branch=month,star=symbol if kind=="star" else None,
                stem=symbol if kind=="stem" else None)
            obstacles=tuple(
                (["旬空待辨"] if record["void_branches"] else [])+
                (["天盘入墓"] if record["sky_tombs"] else [])+
                (["地盘入墓"] if record["earth_tombs"] else [])+
                (["六仪击刑"] if record["striking_stems"] else [])+
                (["门迫"] if record["door_pressure"] else []))
            energy=table_one(kind,symbol,month,index,restrictions=obstacles)
            physical_inspections.add(index)
            one_cache[cachekey]=(record,energy)
        record,energy=one_cache[cachekey]
        view={**record,"role":ROLE_TITLES.get(key,"原书辅助宫"+str(index)),
              "primary_strength_25":energy,
              "all_symbol_strength_25":[energy]}
        view["complete_palace"]=inspect_complete_selected_palace(
            chart=chart,cell=cell,record=view,month_branch=month,
            primary_factor=energy,matched_pairs=matched_pairs)
        view["void_classification"]=view["complete_palace"]["void"]["classification"]
        inspected[key]=view

    # User's latest instruction: ALWAYS observe the real 乾、坤 palaces
    # as secondary context and compare their nominal palace relationship
    # with Tianrui.  This does NOT bind both as the patient, fabricate a
    # gender, or duplicate votes if one is already the primary patient.
    auxiliary_palaces={}
    for alias,pid in (("qian",6),("kun",2)):
        palace_cell=_cell(chart,pid)
        if palace_cell is None:raise ValueError("Real Qian/Kun palace missing")
        resident=palace_cell["heaven_stars"]
        selected_star=resident[0]["star"] if resident else None
        observed=inspect_palace(
            chart=chart,cell=palace_cell,
            role=("乾六宫辅助观察" if pid==6 else "坤二宫辅助观察"),
            month_branch=month,star=selected_star,
            stem=palace_cell["earth_stem"] if selected_star is None else None)
        inspected_detail=inspect_complete_selected_palace(
            chart=chart,cell=palace_cell,record=observed,
            month_branch=month,matched_pairs=matched_pairs)
        auxiliary_palaces[alias]={
            "palace":pid,"role":observed["role"],
            "complete_palace":inspected_detail,
            "relation_to_illness":element_relation(
                ELEMENTS[pid],ELEMENTS[inspected["illness"]["palace"]]),
            "used_only_as_auxiliary":True,
            "cannot_vote_without_role_source":True,
            "patient_identity_not_implied":True,
        }

    edges={}
    unique_pair={}
    edges_template=list(HEALTH_EDGES)
    for key in inspected:
        if key.startswith("extra_"):
            edges_template.extend(((key,"illness"),(key,"patient")))
    for a,b in edges_template:
        if a not in inspected or b not in inspected or a==b:continue
        x,y=inspected[a],inspected[b]
        edge=matchup(
            x["primary_strength_25"],y["primary_strength_25"],
            actor_role=a,target_role=b,
            **void_kwargs(x["complete_palace"],y["complete_palace"]))
        eid=a+"->"+b
        edges[eid]=edge

    candidate={"favorable":[],"adverse":[],"pending":[]}
    for (a,b), direction_map in ((key,HEALTH_POLARITY.get(key))
                                  for key in edges_template):
        eid=a+"->"+b
        if eid not in edges:continue
        edge=edges[eid]
        result=direction_map.get(edge["relation"]) if isinstance(direction_map,dict) else None
        # For all other combinations, resolve the outcome only by domain rules.
        if not result:
            result=HEALTH_POLARITY.get((a,b,edge["relation"]))
        if not result:continue
        if a in ("gender","hour") or a.startswith("extra_"):
            continue
        if edge["relation"] not in ("克","生"):continue
        physical=edge["physical_relation_id"]
        if edge["ability"]=="能":
            if physical in unique_pair:
                continue
            unique_pair[physical]=eid
            candidate[result].append({
                "id":"research_duel:"+physical,"edge_id":eid,
                "direction":result,"fact_ids":[edge["actor_fact_id"],edge["target_fact_id"]],
                "source":"domain_specific_rule_hypothesis_not_author_verified"})
        else:
            candidate["pending"].append({
                "id":"research_pending:"+eid,"edge_id":eid,
                "direction":"pending","why":edge["ability"]})

    favor=len(candidate["favorable"]);against=len(candidate["adverse"])
    stance=("favorable" if favor>against else "adverse" if against>favor else "unresolved")
    confident=actor.get("confidence") in (
        "source_case_specific","user_explicit_direction_verified_by_actual_chart")
    # This is an explicit candidate-vote direction, NOT a clinically valid
    # finding or a verified ancient-author outcome.
    traditional_candidate=("古籍规则研究候选偏吉" if stance=="favorable" else
                           "古籍规则研究候选偏凶" if stance=="adverse" else
                           "候选吉凶尚不明")
    verdict={
        "state":stance if confident and (favor or against) else "unresolved",
        "label":traditional_candidate,
        "reason":"按专题取用的独立有效候选对抗吉凶去重比较，需原著案例再校准",
        "decisive_chain":"candidate_duels_only" if confident and (favor or against) else None,
        "no_numeric_health_score":True,"unvalidated_tiers":True}
    macro=macro_facts["fuyin_fanyin"]
    tianrui=inspected["illness"]
    t25=inspect_tianrui_25(
        star_month=tianrui["month_stage"],
        star_element=STAR_ELEMENT["天芮星"],
        palace_element=tianrui["element"],
        palace_month=tianrui["palace_month_stage"],
        void_branches=tianrui["void_branches"],
        sky_tombs=tianrui["sky_tombs"],
        earth_tombs=tianrui["earth_tombs"],
        striking_stems=tianrui["striking_stems"],
        door_pressure=tianrui["door_pressure"])
    # Keep the source-aware Tianrui 25-case interpretation as ONE compound
    # candidate observation, never double-vote raw monthly stage + relation.
    if t25["eligible_evidence_direction"] in ("favorable","adverse","pending","neutral"):
        direction=t25["eligible_evidence_direction"]
        if direction not in candidate:
            candidate["neutral"]=[]
        candidate[direction].append({
            "id":"illness:tianrui_25:"+str(tianrui["palace"]),
            "direction":direction,
            "text":"天芮传统格局候选："+t25["traditional_title"],
            "source":"existing_tianrui_25_source_qualified_review",
            "roles":["天芮病宫"]})
    # The old slim edge candidates remain a historical calculation, but the
    # authoritative user workflow counts complete role-to-illness groups.
    groups=assess_disease_relationships(
        roles=inspected,edges=edges,role_confidence=actor.get("confidence"))
    candidate=groups["evidence"]
    direction=t25["eligible_evidence_direction"]
    if direction in ("favorable","adverse","pending","neutral"):
        candidate.setdefault(direction,[]).append({
            "id":"illness:tianrui_25:"+str(tianrui["palace"]),
            "direction":direction,
            "text":"天芮传统格局候选："+t25["traditional_title"],
            "source":"existing_tianrui_25_source_qualified_review",
            "roles":["天芮病宫"]})
    # One global 五不遇时 adverse signal, NOT one per role or per 81-case
    # match. It is a general traditional warning, separate from tempo.
    if macro_facts["five_not_encounter_triggered"]:
        candidate["adverse"].append({
            "id":"macro:five_not_encounter:"+chart["hour_ganzhi"],
            "direction":"adverse",
            "text":"五不遇时主诸事凶的独立全局凶时信号",
            "source":"kaiwu_ch04_original_five_not_encounter_user_priority",
            "roles":["全局时辰"],"not_clinical_diagnosis":True})
    favor=len(candidate["favorable"]);against=len(candidate["adverse"])
    counts={"qualified_favorable":favor,"qualified_adverse":against,
            "pending_conditions":len(candidate["pending"])}
    # Include the single eligible disease-symbol compound before final tally,
    # so the displayed good/bad numbers and provisional direction agree.
    stance=("favorable" if favor>against else "adverse" if against>favor
            else "unresolved")
    verdict["state"]=stance if confident and (favor or against) else "unresolved"
    verdict["label"]=("古籍规则研究候选偏吉" if stance=="favorable"
                      else "古籍规则研究候选偏凶" if stance=="adverse"
                      else "候选吉凶尚不明")
    verdict["decisive_chain"]=(
        "complete_selected_palaces_majority_plus_one_illness_compound"
        if confident and (favor or against) else None)
    # Preserve original Tianrui compound and reviewer provenance as one fact,
    # never automatically counted again as independent candidate duel.
    nodes={k:{
        "role":r["role"],"palace":r["palace"],"name":r["name"],
        "kind":r["primary_strength_25"]["kind"],
        "symbol":r["primary_strength_25"]["symbol"],
        "strength":r["primary_strength_25"]["strength_label"],
        "month_stage":r["primary_strength_25"]["symbol_month_stage"],
        "palace_month_stage":r["palace_month_stage"],
        "fact_id":r["primary_strength_25"]["fact_id"],
        "palace_context":{"door":r["door"],"deity":r["deity"],
                          "sky_stars":r["heaven"],"earth_stem":r["earth_stem"]},
        "deity_energy":r["complete_palace"]["deity"],
        "void_classification":r["void_classification"],
        "door_energy":r["complete_palace"]["door"],
        "heaven_stem_energy":r["complete_palace"]["heaven_stems"],
        "earth_stem_energy":r["complete_palace"]["earth_stem"],
        "source_81_palace_formations":r["complete_palace"]["ordered_book_81_pairs"],
    } for k,r in inspected.items()}
    network={
        "schema":"selected_domain_signifier_network_vnext_1",
        "mode":"selective","domain":"health","subtopic":"severity",
        "factor_one_nine_star_table":"user_exact_nine_star_5x5_20261023",
        "factor_two_duel_table":"user_5x5_control_with_void_20261023_v3_corrected_roles",
        "factor_one_stem_table":"user_stem_life_stage_x_month_relation_20261023_v1",
        "factor_one_door_table":"user_door_month_x_palace_relation_20261023_v1",
        "nodes":nodes,"directed_edges":edges,
        "complete_selected_palace_audits":{
            k:v["complete_palace"] for k,v in inspected.items()},
        "qian_kun_auxiliary_observations":auxiliary_palaces,
        "void_rule_version":"user_20261024_void_horse_cancels_first_v2",
        "first_stage_macro":macro_facts,
        "year_role_status":missing_natal or "bound_from_supplied_real_year",
        "selected_gender_palace":gender_palace,
        "unselected_gender_palace":(2 if gender_palace==6 else
                                    6 if gender_palace==2 else None),
        "table_one_queries":len(one_cache),"table_two_queries":len(edges),
        "inspected_palace_ids":sorted(physical_inspections),
        "precomputed_cartesian_pairs_materialized":False,
        "domain_template_version":"health_severity_complete_palace_vnext_2",
        "physical_evidence_pairs_counted_once":groups["counted_physical_pairs"],
        "role_group_reviews":groups["reviews"],
        "role_group_selection_confident":groups["selection_confident"],
        "independent_candidate_favorable":favor,
        "independent_candidate_adverse":against,
        "conditional_candidate_unresolved":len(candidate["pending"]),
        "clinical_prediction":False}
    new_quant=inspect_selected_quantization(
        selected_roles=inspected,qian_kun_observations=auxiliary_palaces,
        first_stage_macro=macro_facts)
    network["candidate_five_grade_quantization"]=new_quant
    interactions={
        "天芮星月令×星宫五行25格":t25,
        "table_two_selected_edges":edges,
    }
    result={
        "schema":"health_selective_complete_palace_review_vnext_2",
        "selected_energy_pipeline":True,
        "macro":macro,
        "first_stage_macro":macro_facts,"selected_roles":inspected,
        "ordered_roles":[inspected[k] for k in inspected],
        "interactions":interactions,
        "full_health_role_strength_network":network,
        "verdict":verdict,
        "evidence":candidate,
        "counts":counts,
        "missing_natal":missing_natal,
        "gender_palace":gender_palace,
        "qian_kun_auxiliary_observations":auxiliary_palaces,
        "book_pair_source_hits":len(matched_pairs),
        "role_group_majority":groups,
        "candidate_five_grade_quantization":new_quant,
        "not_medical_outcome":True,
    }
    return result


def selected_health_sections(result,*,actor,chart):
    """Concise user-facing fixed template: selected roles only."""
    roles=result["selected_roles"];net=result["full_health_role_strength_network"]
    edges=net["directed_edges"]
    macro=result["macro"]
    sections=[]
    def push(code,title,message):
        sections.append({"id":code,"title":title,"text":message})
    push("01_macro","起盘总纲：五不遇时、伏吟、反吟",
         render_first_stage_macro(result["first_stage_macro"]))
    key_order=(("illness","02","天芮病宫"),
               ("doctor","03","天心医生"),
               ("medicine","04","乙奇医药"),
               ("patient","05","患者用神"),
               ("hour","06","时干事体"),
               ("natal","07","患者年命"),
               ("gender","08","乾坤辅助宫"))
    for key,serial,title in key_order:
        if key=="natal" and key not in roles:
            push(serial,title,"患者未提供可核的真实生年干支或落宫，本次不使用年命。")
            continue
        if key not in roles:continue
        r=roles[key];energy=r["primary_strength_25"]
        text=render_complete_selected_palace(r["complete_palace"])
        if key=="illness":
            t25=result["interactions"]["天芮星月令×星宫五行25格"]
            text+="传统病星格局候选「"+t25["traditional_title"]+"」，其独立条件："+t25["why"]+"。"
        group=result["role_group_majority"]["reviews"].get(key)
        if group:
            outcome=("偏吉" if group["direction"]=="favorable" else
                     "偏凶" if group["direction"]=="adverse" else "待核")
            text+=(" 对天芮病宫"+group["relation"]+"；"+group["why"]+
                   "；本组"+outcome+"。")
        if key=="gender":
            text+="仅为实际性别辅助宫，不自动作为患者主要用神。"
        push(serial,title,text)
    for key in roles:
        if not key.startswith("extra_"):continue
        x=roles[key]
        push("08_"+key,"源书辅助宫",
             render_complete_selected_palace(x["complete_palace"])+
             "按来源取用，不能仅因旺就判吉。")
    # These are always real chart palaces, even when patient sex is
    # unspecified; they remain auxiliary observations, not natal/sex votes.
    qk=result["qian_kun_auxiliary_observations"]
    auxiliary_texts=[]
    for alias in ("qian","kun"):
        ob=qk[alias]
        auxiliary_texts.append(
            ob["role"]+"："+render_complete_selected_palace(ob["complete_palace"])+
            " 与天芮病宫"+ob["relation_to_illness"]+
            "，仅供人物关系辅助，不直接计独立吉凶票。")
    push("09_qian_kun_auxiliary","乾坤宫辅助观察",
         " ".join(auxiliary_texts))
    push("89_quant","五级能量量化合断",
         render_quant_review(result["candidate_five_grade_quantization"]))
    v=result["verdict"];n=result["counts"]
    q=result["candidate_five_grade_quantization"]["summary"]
    if q["score"] is None:
        conclusion=("最终五级量化吉凶尚不能定；尚有未核的星门神格来源"+
                    "或尚无合计超五档时的正式分档规则。")
    else:
        conclusion=("最终五级量化象意为"+q["grade"]+
                    "（"+str(q["score"])+"分）。")
    push("90_review","全部证据合断",
         conclusion+"旧版定性证据仅作对照："+v["label"]+
         "；去重有利"+str(n["qualified_favorable"])+
         "条、不利"+str(n["qualified_adverse"])+
         "条、未定"+str(n["pending_conditions"])+
         "条，不能替代当前五级总分。"+
         "伏吟反吟只管缓急；传统研究象意不能代替真实诊断或用药。")
    push("91_timing","时空及应期",
         "驿马参考"+HORSE[chart["hour_ganzhi"][1]]+
         "；应期还需原书空墓、冲合、填实和具体问事条件共同触发，"+
         "证据不足时不虚构具体日期。")
    return sections
