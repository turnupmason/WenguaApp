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
              # The selected factor is the ONLY table-one factor queried.
              "all_symbol_strength_25":[energy]}
        inspected[key]=view

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
            actor_role=a,target_role=b)
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
    macro=fuyin_fanyin_facts(chart)
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
    # Candidate win/loss is still research-only, not an author-verified vote.
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
        "candidate_duels_plus_one_illness_compound"
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
    } for k,r in inspected.items()}
    network={
        "schema":"selected_domain_signifier_network_vnext_1",
        "mode":"selective","domain":"health","subtopic":"severity",
        "factor_one_nine_star_table":"user_exact_nine_star_5x5_20261023",
        "factor_two_duel_table":"user_5x5_control_with_void_20261023_v1",
        "factor_one_stem_table":"user_stem_life_stage_x_month_relation_20261023_v1",
        "factor_one_door_table":"user_door_month_x_palace_relation_20261023_v1",
        "nodes":nodes,"directed_edges":edges,
        "year_role_status":missing_natal or "bound_from_supplied_real_year",
        "selected_gender_palace":gender_palace,
        "unselected_gender_palace":(2 if gender_palace==6 else
                                    6 if gender_palace==2 else None),
        "table_one_queries":len(one_cache),"table_two_queries":len(edges),
        "inspected_palace_ids":sorted(physical_inspections),
        "precomputed_cartesian_pairs_materialized":False,
        "domain_template_version":"health_severity_minimal_vnext_1",
        "physical_evidence_pairs_counted_once":sorted(unique_pair),
        "independent_candidate_favorable":favor,
        "independent_candidate_adverse":against,
        "conditional_candidate_unresolved":len(candidate["pending"]),
        "clinical_prediction":False}
    interactions={
        "天芮星月令×星宫五行25格":t25,
        "table_two_selected_edges":edges,
    }
    result={
        "schema":"health_selective_two_table_review_vnext_1",
        "selected_energy_pipeline":True,
        "macro":macro,"selected_roles":inspected,
        "ordered_roles":[inspected[k] for k in inspected],
        "interactions":interactions,
        "full_health_role_strength_network":network,
        "verdict":verdict,
        "evidence":candidate,
        "counts":counts,
        "missing_natal":missing_natal,
        "gender_palace":gender_palace,
        "book_pair_source_hits":len(matched_pairs),
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
    push("01_macro","先看伏吟反吟",
         "九星"+macro["star"]+"、八门"+macro["door"]+"；"+macro["pace"]+
         "。宏观节奏与吉凶独立判断。")
    key_order=(("illness","02","天芮病宫"),
               ("doctor","03","天心医生"),
               ("medicine","04","乙奇医药"),
               ("patient","05","患者用神"),
               ("natal","06","患者年命"),
               ("hour","07","时干事体"),
               ("gender","08","乾坤辅助宫"))
    for key,serial,title in key_order:
        if key=="natal" and key not in roles:
            push(serial,title,"患者未提供可核的真实生年干支或落宫，本次不使用年命。")
            continue
        if key not in roles:continue
        r=roles[key];energy=r["primary_strength_25"]
        if energy.get("table_version")=="user_stem_life_stage_x_month_relation_20261023_v1":
            if energy.get("stem_life_strength_pending"):
                strength_desc=(
                    "十天干按真实宫支十二长生查表；候选"+
                    "、".join(x["row"]+"为"+x["strength"]
                              for x in energy["stem_life_candidate_cells"])+
                    "，尚缺该宫两支择用原书条件，本次不造唯一强度。")
            else:
                strength_desc=("十天干十二长生归组"+str(energy["user_cell_row"])+
                               "，与月令"+str(energy["user_cell_col"])+
                               "，力量"+str(energy["strength_label"])+"。")
            text=r["role"]+"落"+r["name"]+"。"+strength_desc
        else:
            text=r["role"]+"落"+r["name"]+"。"+format_strength_template(energy)
        if key=="illness":
            t25=result["interactions"]["天芮星月令×星宫五行25格"]
            text+="传统病星格局候选「"+t25["traditional_title"]+"」，其独立条件："+t25["why"]+"。"
        details=[]
        for a,b in (("doctor","illness"),("doctor","patient"),
                    ("medicine","illness"),("medicine","patient"),
                    ("patient","illness"),("illness","patient"),
                    ("natal","illness"),("natal","patient"),
                    ("hour","illness"),("hour","patient"),
                    ("gender","illness"),("gender","patient")):
            if a!=key:continue
            x=edges.get(a+"->"+b)
            if not x:continue
            goal="病宫" if b=="illness" else "患者宫"
            if x["control_status"]=="matched":
                explanation=("克制表「"+x["control_result"]+"」"+
                             "（"+str(x["control_scenario"])+"）")
            elif x["control_status"]=="duplicate_attacker_label_pending":
                explanation="施力方假空有两张同名不同值的原表，等用户确认分支"
            elif x["control_status"]=="factor_power_pending":
                explanation="十干长生分支取用未定，不能生成对抗胜负"
            elif x["control_status"]=="void_type_pending":
                explanation="空亡真假未核，暂不套假空表"
            else:
                explanation="此关系不适用克制表"
            details.append("对"+goal+x["relation"]+"；"+explanation+
                           "，作用条件"+x["ability"])
        if details:text+="；"+"；".join(details)+"。"
        if key=="gender":
            text+="仅为实际性别辅助宫，不自动作为患者主要用神。"
        push(serial,title,text)
    for key in roles:
        if not key.startswith("extra_"):continue
        x=roles[key]
        push("08_"+key,"源书辅助宫",
             x["role"]+"落"+x["name"]+"，"+format_strength_template(
                 x["primary_strength_25"])+
             "按来源取用，不能仅因旺就判吉。")
    v=result["verdict"];n=result["counts"]
    push("90_review","全部证据合断",
         v["label"]+"。候选力量对抗去重后，有利"+
         str(n["qualified_favorable"])+"条、不利"+
         str(n["qualified_adverse"])+"条、条件未定"+
         str(n["pending_conditions"])+"条。"+
         "本次只计算专题选中的用神，不按所有九宫穷举；候选强度尚未古籍独立校准，"+
         "不用于临床病情或治疗判断。")
    push("91_timing","时空及应期",
         "驿马参考"+HORSE[chart["hour_ganzhi"][1]]+
         "；应期还需原书空墓、冲合、填实和具体问事条件共同触发，"+
         "证据不足时不虚构具体日期。")
    return sections
