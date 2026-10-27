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
    inspect_complete_selected_palace,void_kwargs,render_complete_selected_palace,
    normalize_new_door_relation)
from .health_role_majority_vnext import assess_disease_relationships
from .health_relationship_language_vnext import explain_selected_role
from .health_macro_facts_vnext import first_stage_macro,render_first_stage_macro
from .health_quant_overlay_vnext import inspect_selected_quantization,render_quant_review,render_palace_compact_score
from .health_reading_template_vnext import render as render_slot,title as template_title
from .marriage_runtime import ELEMENTS,element_relation

# Other subtopics will be added only when their original source conditions
# and relevant person-role bindings are implemented and tested.
DOMAIN_CASE_TEMPLATES = {
    ("health", "severity"): (
        "illness", "doctor", "medicine", "patient",
        "natal_if_provided", "hour", "chief_protection",
        "gender_palace_if_known","book_profile_auxiliary_if_bound",
    ),
}
# Exact domain choice of meaningful two-way relationships; not all pairs.
HEALTH_EDGES = (
    ("doctor","illness"),("medicine","illness"),
    ("patient","illness"),("hour","illness"),
    ("chief","illness"),("natal","illness"),
    ("gender","illness"),
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
             "gender":"乾坤性别辅助宫",
             "chief":"值符护持宫"}


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

    # Eight-deity 值符: its ACTUAL palace is a further selected health
    # protection role, not the eight-star 值符 (or an invented new palace).
    chief_cells=[c for c in chart["palaces"].values()
                 if c.get("deity")=="值符"]
    if len(chief_cells)!=1:
        raise ValueError("A real cast must have one actual 值符 deity palace")
    chief_cell=chief_cells[0]
    if chief_cell["palace"]==5:
        raise ValueError("Do not invent ordinary middle-five resident god")
    chief_star=(chief_cell["heaven_stars"][0]["star"]
                if chief_cell["heaven_stars"] else None)
    raw["chief"]=(chief_cell,"star" if chief_star else "stem",
                  chief_star or chief_cell["earth_stem"])

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
    # Only explicitly older-generation patients bind 乾/坤. Sex alone
    # must NEVER introduce an additional palace for friends, spouses, peers,
    # ordinary relatives or children.
    elder=actor.get("relationship") in {"father","mother","parent","older_relative"}
    gender_palace={"male":6,"female":2}.get(sex) if elder else None
    if gender_palace is not None:
        cell=_cell(chart,gender_palace)
        if not cell:raise ValueError("Actual gender auxiliary palace absent")
        # Gender auxiliary is a PALACE observation, not an invented natal
        # or chosen medicine stem. Its resident star is the context anchor.
        resident=(cell["heaven_stars"][0]["star"] if cell["heaven_stars"]
                  else None)
        raw["gender"]=(cell,"star" if resident else "stem",
                       resident or cell["earth_stem"])

    # Strict user-specified illness scope: no generic actor.extra_cells.
    # All nine raw chart cells remain cast and available for inspection,
    # but only source-selected roles and 乾/坤 auxiliaries get scored.

    inspected={}
    one_cache={}
    physical_inspections=set()
    for key,(cell,kind,symbol) in raw.items():
        index=cell["palace"]
        cachekey=(index,kind,symbol)
        if cachekey not in one_cache:
            legacy_record=inspect_palace(
                chart=chart,cell=cell,role=ROLE_TITLES.get(key,"原书辅助宫"+str(index)),
                month_branch=month,star=symbol if kind=="star" else None,
                stem=symbol if kind=="stem" else None)
            record=normalize_new_door_relation(
                record=legacy_record,cell=cell,month_branch=month)
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
        if key=="chief":
            # 值符 is the ACTUAL eight-deity signifier. Its power is taken
            # from the user's five deity/palace relationships WITHOUT a
            # month status. Do not silently use the resident star as the
            # chief god when comparing protection vs illness.
            from .health_intrinsic_scoring_vnext import GOD_RELATIONS
            dg=view["complete_palace"]["deity"]
            if dg["name"]!="值符" or dg["nominal_relation"] not in GOD_RELATIONS:
                raise ValueError("Real chief deity lacks palace relationship")
            value_strength={
                **energy,
                "kind":"deity","symbol":"值符",
                "symbol_element":dg["symbol_element"],
                "symbol_month_stage":None,
                "strength_label":GOD_RELATIONS[dg["nominal_relation"]],
                "fact_id":"chief_deity:值符:"+str(index)+":"+month,
                "table_version":"user_eight_deity_palace_five_relations_20261024",
                "god_relation_no_month_stage":dg["nominal_relation"],
                "source_200_cell_deity_without_month":True}
            view["resident_star_strength_for_context_only"]=energy
            view["primary_strength_25"]=value_strength
            view["complete_palace"]["primary_strength"]=value_strength
        inspected[key]=view

    # User's latest instruction: ALWAYS observe the real 乾、坤 palaces
    # as secondary context and compare their nominal palace relationship
    # with Tianrui for internal factual research only, never automatic scoring.
    # gender, or duplicate votes if one is already the primary patient.
    auxiliary_palaces={}
    for alias,pid in (("qian",6),("kun",2)):
        palace_cell=_cell(chart,pid)
        if palace_cell is None:raise ValueError("Real Qian/Kun palace missing")
        resident=palace_cell["heaven_stars"]
        selected_star=resident[0]["star"] if resident else None
        legacy_observed=inspect_palace(
            chart=chart,cell=palace_cell,
            role=("乾六宫辅助观察" if pid==6 else "坤二宫辅助观察"),
            month_branch=month,star=selected_star,
            stem=palace_cell["earth_stem"] if selected_star is None else None)
        observed=normalize_new_door_relation(
            record=legacy_observed,cell=palace_cell,month_branch=month)
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
        "void_rule_version":"user_20261025_void_horse_same_palace_fake_v3",
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
        first_stage_macro=macro_facts,xun_shou=chart["xun_shou"],
        selected_gender_palace=gender_palace,directed_edges=edges)
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
    """V4 public prose from live scored real palaces, with no repeated evidence.

    Previous original books, source 81 rows and full 200-cell audits are untouched.
    Elders only: male -> Qian, female -> Kun; other actors -> neither.
    """
    from .health_five_level_quant_vnext import label as score_label

    roles=result["selected_roles"]
    edges=result["full_health_role_strength_network"]["directed_edges"]
    quant=result["candidate_five_grade_quantization"]
    sections=[]
    seen={}
    def grade(score):
        if score is None:return "吉凶待核"
        if score==0:return "中平"
        return score_label(score).replace("中等吉","中吉").replace("中等凶","中凶")
    def push(code,title,text):
        # Punctuation is sanitized ONLY after rendering immutable book quotes.
        # "文书不行。；古诀" => "文书不行；古诀", never mutate TSV.
        for old,new in (("。；","；"),("；；","；"),
                        ("。。","。"),("，；","；"),("。。，","。")):
            while old in text:text=text.replace(old,new)
        sections.append({"id":code,"title":title,"text":text.strip()})

    # This is the display of EXISTING exact table-one (month x 5 relations)
    # and table-two (attacker x target) results. No power is invented here.
    def role_power_note(key,row):
        power=row["primary_strength_25"]
        kind=power["kind"]
        strength=str(power.get("strength_label") or "待核")
        if kind=="deity":
            god=row["complete_palace"]["deity"]
            return ("值符按神宫"+god["relation"]+"，用神力量为"+strength+"。")
        if kind=="star":
            rel={"宫生符号":"被宫生","宫克符号":"被宫克",
                 "符号克宫":"克宫","符号生宫":"生宫","比和":"比和"}
            col=power.get("user_cell_col") or power.get("nominal_relation_from_symbol")
            return (power["symbol"]+"月令"+str(power.get("symbol_month_stage") or "待核")+
                    "、"+rel.get(col,str(col))+"，用神力量为"+strength+"。")
        if kind=="stem":
            col=power.get("user_cell_col") or "月令关系待核"
            row_name=power.get("user_cell_row") or "长生分支待核"
            return (power["symbol"]+"天干十二长生"+str(row_name)+
                    "、"+str(col)+"，用神力量为"+strength+"。")
        return "用神力量为"+strength+"。"

    def role_control_note(key,row):
        gate=quant["role_effectiveness_gates"][key]
        rel=gate["relation"]
        name={"doctor":"天心医生","medicine":"乙奇医药",
              "patient":"患者用神","hour":"时干事体",
              "chief":"值符大吉神","gender":"性别辅助宫",
              "natal":"患者年命"}.get(key,key)
        strength=role_power_note(key,row)
        outcome=gate["control_result"]
        if key=="medicine" and rel=="同宫":
            return (strength+"乙奇与天芮病宫同宫，表示正在接受治疗，"
                    "医药与病象同宫发挥作用。")
        if key=="chief" and rel=="同宫":
            return (strength+"值符大吉神与天芮病宫同宫，"
                    "表示大吉神在同宫护持，能够发挥作用。")
        if key=="chief" and gate["void"]!="not_void":
            return (strength+"因值符空亡，护持力明显减弱，尚存少许余气。"
                    "")
        if rel=="克":
            bonus=quant["summary"]["control_bonus_palaces"]
            if str(gate["palace"]) in bonus:
                void=roles["illness"]["complete_palace"]["void"]["classification"]
                meaning=("病宫逢空，病气减弱，更易受到"+name+"的克制。"
                         if void!="not_void" else "病象受到"+name+"的克制。")
            else:
                meaning=name+"虽克病宫，但护持之力难以发挥。"
            return strength+name+"宫克天芮病宫，"+meaning
        if rel=="生":
            meaning=name+"宫生天芮病宫，意思为：疾病得不到"+name+"的压制，反受其生扶。"
        elif rel=="被克":
            meaning=name+"宫受天芮病宫克，意思为："+name+"受病宫压制，无法制病。"
        elif rel=="被生":
            meaning=name+"宫受天芮病宫生，意思为：本宫受病宫生扶，未形成对病宫的克制。"
        elif rel=="比和":
            meaning=name+"宫与天芮病宫比和，意思为：双方同气，未形成对病宫的克制。"
        elif rel=="同宫":
            meaning=name+"与天芮病宫同宫，意思为：双方同宫，不另论跨宫克制。"
        else:
            meaning=name+"与病宫的五行关系待核。"
        return strength+meaning

    power_seen={}
    push("01_macro",template_title("macro"),
         render_slot("macro",macro_text=render_first_stage_macro(
             result["first_stage_macro"])))
    for key,serial,title_key in (
        ("illness","02","illness"),("doctor","03","doctor"),
        ("medicine","04","medicine"),("patient","05","patient"),
        ("hour","06","hour"),("chief","07","chief"),
        ("natal","08","natal"),("gender","09","gender")):
        if key not in roles:
            continue
        role=roles[key]
        qitem=quant["roles"][key]
        pid=role["palace"]
        strength=grade(qitem["palace_score"]["score"])
        if pid in seen:
            detail=("与前述"+seen[pid]+"同在"+
                    role["complete_palace"]["palace_name"]+
                    "。全部因素推断后，此宫为"+strength+"。")
        else:
            detail=render_complete_selected_palace(
                role["complete_palace"],quantified=qitem)
            seen[pid]=template_title(title_key)
        extra=""
        if key=="illness":
            t25=result["interactions"]["天芮星月令×星宫五行25格"]
            extra=render_slot("illness",name=t25["traditional_title"],
                              explanation=t25["why"])
        if key=="illness":
            relation=""
        else:
            power=role["primary_strength_25"]
            marker=(pid,power["kind"],power["symbol"])
            if marker in power_seen and key!="chief":
                relation=""
            else:
                relation=render_slot("role_relation",
                                     relation_text=role_control_note(key,role))
                power_seen[marker]=key
        title=template_title(title_key)
        if key=="gender":
            title=("坤宫辅助（女）" if pid==2 else
                   "乾宫辅助（男）" if pid==6 else title)
        push(serial,title,render_slot("role",palace_detail=detail,
            palace_score="",extra_illness=extra,role_relation=relation,
            gender_note=""))

    # Qian/Kun audit records remain retained for internal investigations.
    # Elder-only sex palace was shown/scored as 'gender' if eligible;
    # never infer either palace from the sex of a non-elder.

    q=quant["summary"]
    preface=""
    if q["drain_bonus_palaces"]:
        palace_names=[]
        for pid in sorted(int(k) for k in q["drain_bonus_palaces"]):
            source=next(row for row in roles.values() if row["palace"]==pid)
            palace_names.append(source["complete_palace"]["palace_name"])
        preface="病星本已极弱，反去生助"+"、".join(palace_names)+"，自身气力进一步耗散，有病势受损之象。"
    preface+="".join(q["auspice_bonus_notes"])
    conclusion=(render_slot("overall_pending",post_void_sum=q["post_void_known_sum"])
                if q["score"] is None else
                render_slot("overall_resolved",grade=("不凶不吉" if q["score"]==0 else grade(q["score"])),
                    palace_count=q["unique_palace_count"],
                    post_void_sum=q["post_void_known_sum"],score=q["score"]))
    push("90_review",template_title("verdict"),
         render_slot("verdict",conclusion=preface+conclusion))
    push("91_timing",template_title("timing"),
         render_slot("timing",horse=HORSE[chart["hour_ganzhi"][1]]))
    return sections
