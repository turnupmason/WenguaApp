"""V4 draft: source-grounded CULTURAL health-severity score ledger, never medical risk.

User's proposed 100 baseline is an arbitrary starting index, not a probability.
All old V3.9 user-reviewed texts, real source cases and SQLite immutable.
Every score delta belongs to one non-duplicated evidence family. Unprovided
illness-duration and sex are UNKNOWN/UNSCORED, never silently invented.
"""
from __future__ import annotations
import json
from pathlib import Path
from .health_dynamic_v21 import bind_patient
from .health_severity_v22 import _find_star,_find_heaven_stem,_yes_void
from .health_severity_v25 import fuyin_fanyin_facts,OPPOSITE
from .health_severity_v28 import related_special_facts,STEM_ELEMENTS
from .health_severity_v34 import HORSE,_cell_stems
from .health_severity_v37 import actual_81_pair_context
from .health_severity_template import MONTH_ELEMENTS
from .marriage_runtime import (PALACE_BRANCHES,ELEMENTS,CONTROLS,PRODUCES,
                               element_relation,hourly_void_branches)
from .symbol_relations import stem_stage
from .semantic_lookup import door_palace_relation,nine_star_month_status

ROOT=Path(__file__).resolve().parents[2]
POLICY=ROOT/"data/knowledge/score_models/health_severity_v40/weights_draft.json"
BRANCH_CLASH={"子":"午","午":"子","丑":"未","未":"丑","寅":"申","申":"寅",
              "卯":"酉","酉":"卯","辰":"戌","戌":"辰","巳":"亥","亥":"巳"}

def _policy():
    p=json.loads(POLICY.read_text("utf8"))
    if p["version"]!="V4.0-score-experiment-1" or p["score_policy"]["baseline"]!=100:
        raise ValueError("Draft policy or baseline changed without new version")
    return p

def _season(elem,month_elem):
    """Seasonal five-element stage; not the nine-star or 12-life stage."""
    if elem==month_elem:return "旺"
    if PRODUCES[month_elem]==elem:return "相"
    if PRODUCES[elem]==month_elem:return "休"
    if CONTROLS[elem]==month_elem:return "囚"
    if CONTROLS[month_elem]==elem:return "死"
    raise ValueError("Unresolvable five-element month relation")

def _tomb_and_horse(chart,person,stem,calendar,month_stage):
    """Separate literal 枝冲 from user's hypothesized 对宫/对角马星开墓.

    Nine-palace OPPOSITE includes diagonal and opposing sides across center:
    1<->9, 2<->8, 3<->7, 4<->6. A spatial horse opposite is
    not an exact six-branch clash; audit MUST keep them separate.
    """
    p=person["palace"]
    tomb=stem_stage(stem,"墓")["branch"]
    housed=tomb in PALACE_BRANCHES[p]
    hour=chart["hour_ganzhi"]
    horse=HORSE[hour[1]]
    horse_palace=next(k for k,bs in PALACE_BRANCHES.items() if horse in bs)
    spatial=housed and OPPOSITE.get(p)==horse_palace
    opposing=BRANCH_CLASH[tomb]
    explicit=[]
    for label,key in (("年支","year_ganzhi"),("月支","month_ganzhi"),
                      ("日支","day_ganzhi"),("时支","hour_ganzhi")):
        s=hour if key=="hour_ganzhi" else calendar.get(key)
        if s and len(s)==2 and s[1]==opposing:explicit.append(label)
    direct=housed and bool(explicit)
    status=("not_in_tomb" if not housed else
            "exact_branch_clash_candidate" if direct else
            "opposite_horse_palace_user_method" if spatial else
            "unopened_tomb_or_storage")
    # This stage classification is defined in the second book: strong stem
    # in the tomb position is 库, weak stem is 墓, not synonymous.
    is_storage=month_stage in ("旺","相")
    return {"stem":stem,"patient_palace":p,"tomb_branch":tomb,
       "palace_branches":list(PALACE_BRANCHES[p]),"in_tomb_palace":housed,
       "month_stage":month_stage,"name":"入库" if is_storage else "入墓",
       "horse_from_hour_branch":hour[1],"horse_branch":horse,
       "horse_palace":horse_palace,"opposite_palace":OPPOSITE.get(p),
       "horse_spatial_opposite":bool(spatial),
       "direct_clashing_branch":opposing,"direct_clash_in_pillars":bool(direct),
       "direct_clash_pillar_labels":explicit,
       "opening_mode":status,
       "source_texts":["开悟之门第二章墓库月令及冲库原文",
          "开悟之门第四章时支驿马及六甲旬空、马星动象"],
       "two_methods_not_silently_equated":True}

def calculate_health_symbolic_score_v40(*,chart,inquiry,calendar):
    """An experimental POINT LEDGER, not an actual patient forecast.

    Inputs from exactly the same real casting engine and context used by
    user-reviewed V3.9. Outputs weight ledger, unknown factors, and provenance
    separate from old binary verdict. No old author outcomes are read.
    """
    if inquiry.get("intent")!="severity" or not calendar or "month_branch" not in calendar:
        raise ValueError("Only original source severity with real month context")
    cfg=_policy()
    w=cfg["weights"]
    patient_profile=bind_patient(chart,inquiry,calendar)
    patient=patient_profile["main_cell"]
    if patient is None:raise ValueError("Actual patient and role required")
    patient_stem=patient_profile["stem"]
    if not patient_stem or patient_stem not in STEM_ELEMENTS:
        raise ValueError("Need a source-supported patient stem")
    ill,carrier=_find_star(chart,"天芮星")
    doctor,_=_find_star(chart,"天心星")
    yi=_find_heaven_stem(chart,"乙")
    hour=_find_heaven_stem(chart,chart["hour_ganzhi"][0])
    if not doctor or not yi or not hour:
        raise ValueError("Real doctor/medicine/hour symbols required")
    month=calendar["month_branch"]
    me=MONTH_ELEMENTS[month]
    duration=inquiry.get("illness_duration")
    if duration not in (None,"new","chronic"):
        raise ValueError("Duration may only be actual new/chronic or unknown")
    sex=inquiry.get("patient_sex")
    if sex is None:
        if inquiry["relationship"] in ("father","son","brother","husband"):sex="male"
        elif inquiry["relationship"] in ("mother","daughter","sister","wife"):sex="female"
    if sex not in (None,"male","female"):raise ValueError("Known sex must be explicit")
    ledger=[];unknown=[];used=set()
    def add(id,family,why,details=None,adjust=None):
        if id in used:raise ValueError("Duplicate exact score rule "+id)
        used.add(id)
        pts=int(w[id] if adjust is None else adjust)
        ledger.append({"id":id,"family":family,"points":pts,
            "why":why,"evidence":details or {},
            "calibration":"user_proposal_plus_explicit_draft_interactions",
            "clinical_interpretation":None})
    def miss(id,why):unknown.append({"id":id,"reason":why})
    pp=ELEMENTS[patient["palace"]];ip=ELEMENTS[ill["palace"]]
    rel=element_relation(pp,ip)
    # 1) Directed patient–illness has only ONE mutually exclusive edge.
    if rel=="克":add("patient_controls_illness","main_patient_illness_relation",
                     "患者宫克病宫",{"p":patient["palace"],"i":ill["palace"]})
    elif rel=="受克":add("illness_controls_patient","main_patient_illness_relation",
                        "病宫克患者宫",{"p":patient["palace"],"i":ill["palace"]})
    elif rel=="生":add("patient_generates_illness","main_patient_illness_relation",
                       "患者宫生病宫",{"p":patient["palace"],"i":ill["palace"]})
    # 2) Medicine: choose best independently by palace, do NOT stack two +15.
    med_cells={doctor["palace"]:doctor,yi["palace"]:yi}
    med_roles={doctor["palace"]:["天心"],yi["palace"]:["乙奇"]}
    if yi["palace"]==doctor["palace"]:med_roles[yi["palace"]]=["天心","乙奇"]
    def med_quality(c):
        relation=element_relation(ELEMENTS[c["palace"]],ip)
        return 3 if relation=="克" else 0 if relation=="受克" else 2
    selected=max(med_cells.values(),key=lambda c:(med_quality(c),
        0 if _yes_void(chart,c) else 1,-c["palace"]))
    selected_rel=element_relation(ELEMENTS[selected["palace"]],ip)
    roles=med_roles[selected["palace"]]
    if selected_rel=="克":add("physician_or_derived_medicine_controls_illness","medicine_main",
      "已选医药宫克病宫",{"selected_palace":selected["palace"],"roles":roles})
    elif all(element_relation(ELEMENTS[c["palace"]],ip)=="受克" for c in med_cells.values()):
        add("illness_controls_all_available_medicine","medicine_main",
            "天心和乙奇均被病宫克制",{"palaces":list(med_cells)})
    # Independent co-palace chance: no imaginary treatment efficacy.
    if any(c["palace"]==ill["palace"] or c["palace"]==hour["palace"]
            for c in med_cells.values()):
        add("same_palace_event_or_illness_medicine_opportunity","medical_access",
             "时干/病宫与医药宫同宫，古籍的医治机会辅助象",
             {"hour":hour["palace"],"illness":ill["palace"],"medicine":list(med_cells)})
    if _yes_void(chart,selected):
        add("doctor_and_yi_both_void_or_selected_void","medicine_void",
            "所选主医药宫旬空，药象受虚",{"selected_palace":selected["palace"]})
    # Death door is NOT vitality palace. Same-palace and opposed are mutually exclusive.
    dead=next((c for c in chart["palaces"].values() if c["door"]=="死门"),None)
    if dead is None:raise ValueError("Actual one death door required")
    if dead["palace"]==patient["palace"]:
        add("death_door_co_palace_patient","door_patient",
            "患者本宫临死门","palace" if False else {"palace":patient["palace"]})
    elif element_relation(ELEMENTS[dead["palace"]],pp)=="克":
        add("death_door_controls_patient","door_patient",
            "死门所落宫五行克患者宫",{"death_door_palace":dead["palace"],"patient":patient["palace"]})
    # 3) 20% seasonal bucket is indicative only; stem and palace distinct.
    p_stem_state=_season(STEM_ELEMENTS[patient_stem],me)
    p_pal_state=_season(pp,me)
    add("patient_stem_month_vigorous" if p_stem_state in ("旺","相") else "patient_stem_month_weak",
       "season_patient_stem","患者主用干在月令"+p_stem_state,
       {"stem":patient_stem,"state":p_stem_state,"month":month})
    add("patient_palace_month_vigorous" if p_pal_state in ("旺","相") else "patient_palace_month_weak",
       "season_patient_palace","患者宫五行在月令"+p_pal_state,
       {"palace":patient["palace"],"state":p_pal_state})
    star_state=nine_star_month_status("天芮星",me)["value"]
    if star_state in ("旺","相"):
        add("illness_tianrui_star_month_vigorous","season_tianrui","天芮月令"+star_state)
    elif star_state in ("休","囚","废"):
        add("illness_tianrui_star_month_weak","season_tianrui","天芮月令"+star_state)
    else:miss("illness_tianrui_star_month","未核实天芮九星月令阶段")
    # 4) True patient tomb, month distinguish 库 vs 墓 before any opening.
    tomb=_tomb_and_horse(chart,patient,patient_stem,calendar,p_stem_state)
    if tomb["in_tomb_palace"]:
        key="patient_strong_storage" if tomb["name"]=="入库" else "patient_weak_tomb"
        penalty=w[key]
        add(key,"patient_tomb","患者用干处于"+tomb["name"],tomb)
        if tomb["direct_clash_in_pillars"]:
            add("patient_exact_clash_opens_tomb_refund_fraction","patient_tomb_opening",
                "四柱明见冲墓支，按冲墓候选返还原暂计墓库扣分",
                tomb,adjust=abs(penalty))
        elif tomb["horse_spatial_opposite"]:
            add("patient_opposite_horse_opens_tomb_refund_fraction","patient_tomb_opening",
                "依用户提出的对宫/对角马星动墓规则，暂返还部分墓库扣分（与直接地支六冲不同）",
                tomb,adjust=int(round(abs(penalty)*float(w["patient_opposite_horse_opens_tomb_refund_fraction"]))))
    # 5) Patient void needs actual new/chronic type.
    if _yes_void(chart,patient):
        if duration=="new":
            add("patient_void_new","patient_void","新病患者宫旬空，传统候选转缓")
        elif duration=="chronic":
            add("patient_void_chronic","patient_void","久病患者宫旬空，传统候选受阻")
        else:miss("patient_void_duration","患者宫旬空，但未提供新病或久病，不给固定吉凶分")
    special=related_special_facts(chart,[("patient",patient,[patient_stem])])
    if any(x["kind"]=="六仪击刑" for x in special):
        add("patient_striking_punishment","patient_punishment",
            "患者宫实算六仪击刑",{"facts":special})
    deity=patient["deity"]
    if deity in ("白虎","玄武"):
        add("patient_bad_deity","deity_patient","患者宫乘"+deity)
    elif deity in ("值符","太阴","六合"):
        add("patient_good_deity","deity_patient","患者宫乘"+deity)
    if any(x in ("乙","丙","丁") for x in _cell_stems(patient)):
        add("patient_three_wonders","patient_three_wonders",
            "患者宫天盘三奇",{"stems":_cell_stems(patient)})
    fy=fuyin_fanyin_facts(chart)
    if "伏吟" in (fy["star"],fy["door"]):
        if duration=="chronic":
            add("star_door_fuyin_chronic","duration_global",
                "久病遇真实星/门伏吟")
        else:miss("fuyin_duration","伏吟主迟，但未确认为久病，不机械扣轻重分")
    if "反吟" in (fy["star"],fy["door"]):
        if duration=="new":
            add("star_door_fanyin_new","duration_global","新病遇实际反吟")
        elif duration=="chronic":
            add("star_door_fanyin_chronic","duration_global","久病遇实际反吟")
        else:miss("fanyin_duration","反吟新病久病取向不同，未输入病程，不评分")
    # 6) Literal 庚同宫; never infer from "Tianrui at palace nine".
    if "庚" in _cell_stems(ill) or ill["earth_stem"]=="庚":
        add("tianrui_geng_same_palace","illness_stem_geng","庚与天芮同宫",
            {"illness_palace":ill["palace"]})
    # 7) Actual door-press: once per affected unique role palace.
    for role,c,rid in (("patient",patient,"patient_door_press"),
                         ("illness",ill,"illness_door_press")):
        if role=="illness" and ill["palace"]==patient["palace"]:continue
        if door_palace_relation(c["door"],c["palace"])["kind"]=="迫":
            add(rid,"door_press_"+str(c["palace"]),role+"宫门迫",{"palace":c["palace"],"door":c["door"]})
    # 8) Month opposite branch (月破) affects the actual patient palace.
    if BRANCH_CLASH[month] in PALACE_BRANCHES[patient["palace"]]:
        add("patient_branch_month_break","patient_month_break",
            "月支冲患者宫所辖地支",{"month":month,"clash":BRANCH_CLASH[month],"patient":patient["palace"]})
    # 9) Qian/Kun is a DIFFERENT auxiliary palace; neither overwrites main.
    if sex:
        aux=chart["palaces"]["6" if sex=="male" else "2"]
        if aux["palace"]!=patient["palace"] and aux["palace"]!=ill["palace"]:
            x=element_relation(ELEMENTS[aux["palace"]],ip)
            if x=="克":
                add("qian_kun_gender_aux_controls_disease","gender_aux",
                    ("乾" if sex=="male" else "坤")+"辅助宫克病宫",
                    {"aux":aux["palace"],"ill":ill["palace"],"sex":sex})
            elif x=="受克":
                add("qian_kun_gender_aux_illness_controls","gender_aux",
                    "病宫克"+("乾" if sex=="male" else "坤")+"辅助宫",
                    {"aux":aux["palace"],"ill":ill["palace"],"sex":sex})
        else:miss("qian_kun_overlap","辅助乾坤与主用神或病宫重叠，只保留证据不重复计分")
    else:miss("qian_kun_missing_patient_sex","未提供患者性别，不猜乾坤辅助宫")
    # 10) A true interaction is an incremental candidate, capped at ONCE.
    hour_c=hour
    pairs=actual_81_pair_context(chart,patient,ill,doctor,yi,hour_c)
    patient_bad=any("患者宫" in r["roles"] and r["applicability"] in
                 ("book_adverse_formation","book_health_adverse") for r in pairs)
    star_rel=element_relation(ip,"土")
    strong_double=rel=="克" and star_rel=="克"
    bad_double=(rel=="受克" and (star_rel in ("生","比和") or patient_bad)) or (
                    rel=="生" and star_rel=="生")
    if strong_double:
        add("double_suppression_distinct_chain_bonus","interaction",
            "患者制病并且病宫制天芮的独立两段关系，只加一次协同项",
            {"patient_vs_illness":rel,"illness_vs_tianrui":star_rel})
    elif bad_double:
        add("double_adverse_distinct_chain_penalty","interaction",
            "疾病攻人或患者助病并见独立凶证，只扣一次协同项",
            {"patient_vs_illness":rel,"illness_vs_tianrui":star_rel,
             "patient_original_bad_formation":patient_bad})
    # Missing information stays visible rather than unconditional zero/veto.
    if duration is None:miss("illness_duration","未说明新病/久病，伏吟反吟/空亡条件评分不足")
    if not inquiry.get("patient_birth_ganzhi") and not inquiry.get("subject_year_ganzhi"):
        miss("natal_context","没有提供出生年命，年命只作为未取值辅助")
    # Some 81 stem pair semantics and 17 composites are not FULL condition-executable.
    miss("unverified_81_and_17_conditions","原书部分复合条件仍待逐条考证，未自动转成一票否决或加减分")
    points=sum(x["points"] for x in ledger)
    raw=cfg["score_policy"]["baseline"]+points
    result=max(0,min(100,raw))
    if sum(1 for x in ledger if x["family"]=="interaction")>1:
        raise ValueError("Conflicting double interactions")
    if sum(1 for x in ledger if x["family"]=="patient_tomb_opening")>1:
        raise ValueError("Multiple tomb opening refunds")
    return {
      "schema":"wengua_health_v40_experimental_traditional_symbolic_100_score",
      "policy_version":cfg["version"],"approval":"unreviewed_research_candidate",
      "score_label":"奇门病势象意分（实验）",
      "baseline":100,"signed_delta_sum":points,"raw_score":raw,
      "display_score_0_100":result,"score_is_probability":False,
      "medical_health_index":False,"clinical_accuracy_validated":False,
      "illness_duration":duration,"person":patient_profile["label"],
      "patient_palace":patient["palace"],"illness_palace":ill["palace"],
      "male_female_aux_reference":sex,"tomb_and_horse":tomb,
      "selected_medical_palace":selected["palace"],
      "month_stage":{"patient_stem":p_stem_state,
         "patient_palace":p_pal_state,"tianrui_star":star_state},
      "ledger":ledger,"unscored_unknowns":unknown,
      "unadjusted_original_v39_readout":True,
      "book_source_outcomes_used":False}
