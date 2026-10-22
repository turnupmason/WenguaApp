"""V4.2: a single REAL chart drives the unchanged V3.9 11-slot reading and
a separate, six-budget balanced, SOURCE-GATED symbolic scoring explanation.

This never changes V3.9's words. It computes ALL chart-derived facts before
scoring, 120 full life-stage mappings from five original anchor stages, and
exact role/combination/horse/tomb evidence. Optional new/chronic, birth year
or unknown person's sex are context, not hidden chart facts: compute both
scenario scores rather than declaring chart facts insufficient.

Not medicine, probability, diagnosis, care advice or evidence of mortality.
"""
from __future__ import annotations
from collections import defaultdict
import json
from pathlib import Path
from .health_severity_v39 import analyze_health_severity_v39
from .health_symbolic_score_v41 import calculate_health_symbolic_score_v41
from .health_dynamic_v21 import bind_patient
from .health_severity_v22 import _find_star,_find_heaven_stem,_palace
from .health_severity_v25 import fuyin_fanyin_facts
from .marriage_runtime import PALACE_BRANCHES,ELEMENTS,element_relation,hourly_void_branches
from .symbol_relations import stem_stage

ROOT=Path(__file__).resolve().parents[2]
STAGE=ROOT/"data/knowledge/score_models/health_severity_v42/twelve_life_stages_source_anchor_full.json"
POLICY=ROOT/"data/knowledge/score_models/health_severity_v42/integrated_budget_policy.json"
BOOK_5_ANCHORS=("长生","帝旺","死","墓","绝")
MODULES=("主体与天芮及其月令","时干事体","医药相互作用",
         "刑冲破墓空与马星","原书有序天地盘格局","复合格局与节奏")

def source_full12():
    p=json.loads(STAGE.read_text("utf8"))
    if p.get("schema")!="wengua_stem_full12_source_anchor_derived_v42":
        raise ValueError("Full12 original-source status changed")
    rows={x["stem"]:x for x in p["stem_tables"]}
    if len(rows)!=10 or len(p["order"])!=12:
        raise ValueError("Ten stems times 12 stages are required")
    for stem,row in rows.items():
        stages=row["stage_to_branch"];reverse=row["branch_to_stage"]
        if len(stages)!=12 or len(reverse)!=12:
            raise ValueError("Twelve stages missing for "+stem)
        for stage in BOOK_5_ANCHORS:
            ref=stem_stage(stem,stage)
            if stages[stage]!=ref["branch"] or stages[stage]!=row["source_existing_5_anchor_branches"][stage]:
                raise ValueError("Ancient book source anchor disagrees "+stem+" "+stage)
        for name,branch in stages.items():
            if reverse[branch]!=name:raise ValueError("Non-bijective full12 "+stem)
    return rows

def full_lifecycle_at_palace(stem,palace,full12=None):
    rows=full12 or source_full12()
    if stem not in rows or palace not in PALACE_BRANCHES or palace==5:
        raise ValueError("Real outer palace and visible stem required")
    branches=PALACE_BRANCHES[palace]
    stages=[{"branch":b,"stage":rows[stem]["branch_to_stage"][b]} for b in branches]
    return {"stem":stem,"palace":palace,"palace_branches":list(branches),
            "all_actual_branch_stages":stages,
            "is_tomb":any(x["stage"]=="墓" for x in stages),
            "is_extinct":any(x["stage"]=="绝" for x in stages),
            "is_strong_stage":any(x["stage"] in ("长生","临官","帝旺") for x in stages),
            "full12_computed":True,
            "origin":"5 book anchors + exact cycle parity and steps",
            "not_a_clinical_statement":True}

def full_board_facts(chart,calendar,inquiry):
    full12=source_full12()
    if calendar["hour_ganzhi"]!=chart["hour_ganzhi"]:
        raise ValueError("Calendar/chart hour mismatch; no invented board")
    p=bind_patient(chart,inquiry,calendar)
    ill,carrier=_find_star(chart,"天芮星")
    doctor,_=_find_star(chart,"天心星")
    medicine=_find_heaven_stem(chart,"乙")
    hour=_find_heaven_stem(chart,chart["hour_ganzhi"][0])
    if not p["main_cell"] or not all((ill,carrier,doctor,medicine,hour)):
        raise ValueError("Unknown relationship is not a defect in palace casting")
    patient=p["main_cell"]
    real=[]
    for k in range(1,10):
        c=chart["palaces"][str(k)]
        if k==5:
            if c["heaven_stars"] or c["door"] or c["deity"]:
                raise ValueError("Centre five must not fabricate the eight ordinary structures")
        else:
            real.append({"palace":k,"element":ELEMENTS[k],
              "branches":list(PALACE_BRANCHES[k]),
              "earth_stem":c["earth_stem"],
              "heaven":[{"star":t["star"],"stem":t["carried_stem"],
                         "lifecycle":full_lifecycle_at_palace(t["carried_stem"],k,full12)}
                        for t in c["heaven_stars"]],
              "door":c["door"],"deity":c["deity"]})
    void=hourly_void_branches(chart["hour_ganzhi"])
    known={"patient":full_lifecycle_at_palace(p["stem"],patient["palace"],full12),
           "tianrui_heaven":full_lifecycle_at_palace(carrier["carried_stem"],ill["palace"],full12)}
    return {"four_pillars":{key:calendar[key+"_ganzhi"]
                 for key in ("year","month","day","hour")},
       "month_branch":calendar["month_branch"],
       "patient_role":p["label"],"patient_stem":p["stem"],
       "patient_palace":patient["palace"],"illness_palace":ill["palace"],
       "illness_carried_stem":carrier["carried_stem"],
       "doctor_palace":doctor["palace"],"yi_medicine_palace":medicine["palace"],
       "hour_event_palace":hour["palace"],"void_from_hour":void,
       "actual_full_8_palace_inventory":real,
       "source12_stage_for_actors":known,
       "source12_all_ten_stems_checked":len(full12)==10,
       "source12_total_stage_facts_checked":sum(len(x["stage_to_branch"]) for x in full12.values()),
       "fuyin_fanyin":fuyin_fanyin_facts(chart),
       "chart_relevant_facts_calculated":True}

def _route_weight(rule):
    label=rule.get("id",rule.get("rule_id",""))
    if rule.get("family")=="original_81_book_pair":return MODULES[4]
    if label.startswith("same_palace_event_or_illness_medicine") or (
        label.startswith(("physician_","illness_controls_all_available_medicine",
         "doctor_and_yi_","qian_kun_gender"))):
        return MODULES[2]
    if label.startswith("double_") or "fuyin" in label or "fanyin" in label:
        return MODULES[5]
    if label.startswith("patient_") and ("void" in label or "tomb" in label
         or "striking" in label or "month_break" in label or "deity" in label
         or "three_wonders" in label or "door_press" in label):
        return MODULES[3]
    if label in ("patient_bad_deity","patient_good_deity","patient_three_wonders",
                 "patient_door_press","illness_door_press",
                 "death_door_co_palace_patient","death_door_controls_patient",
                 "tianrui_geng_same_palace"):
        return MODULES[3]
    if label.startswith("illness_") and ("door_press" in label or "geng" in label):
        return MODULES[3]
    return MODULES[0]

def budgeted_score_from_source(evidence,board,cfg):
    budget=cfg["module_budgets"]
    denom=cfg["module_raw_denominator"]
    if sum(budget.values())!=50 or set(budget)!=set(MODULES):
        raise ValueError("All six module budgets must sum 50 for neutral50 0–100")
    dedup=set();parts=defaultdict(list)
    for row in evidence["evidence_ledger"]:
        id=row.get("id",row.get("rule_id"))
        if not id:raise ValueError("Every score needs stable source evidence id")
        physical=(row.get("family"),id,row.get("palace"),row.get("source_pair_key"))
        if physical in dedup:raise ValueError("Repeated same source evidence")
        dedup.add(physical)
        target=_route_weight(row)
        parts[target].append({"evidence_id":id,"points":row["points"],
              "family":row.get("family"),"original_source_role":row.get("role")})
    # Time module is a true physical relation V3.9 already computed as prose
    # but omitted in the earlier numerical V4.0/V4.1 prototype.
    r=element_relation(ELEMENTS[board["hour_event_palace"]],ELEMENTS[board["patient_palace"]])
    score=cfg["time_relation_candidate"][r]
    parts[MODULES[1]].append({"evidence_id":"real_hour_vs_real_patient",
         "points":score,"family":"directed_hour_person_5element",
         "actual_relation":r,"hour":board["hour_event_palace"],
         "patient":board["patient_palace"]})
    # Full12 is a pure chart fact; don't score tomb a second time here.
    stages=board["source12_stage_for_actors"]["patient"]["all_actual_branch_stages"]
    requested=cfg["stage_mapping"]["patient_stage_illustrative_delta"]
    stage_score=int(round(sum(requested[z["stage"]] for z in stages)/len(stages)))
    if stage_score:
        parts[MODULES[0]].append({"evidence_id":"patient_twelve_stage_at_actual_palace",
            "points":stage_score,"family":"book_anchored_full12_patient",
            "actual_stages":stages})
    # The Tianrui-carried stem may be 墓戌/绝亥, but this does not logically
    # identify medical virus activity or cancel the source book's 丙辛福象.
    module_out=[]
    for name in MODULES:
        raw=sum(x["points"] for x in parts[name])
        limited=max(-budget[name],min(budget[name],
                    int(round(raw*budget[name]/denom[name]))))
        module_out.append({"name":name,"budget":budget[name],
            "raw_rule_sum":raw,"applied_signed_score":limited,
            "all_scored_facts":parts[name],
            "unclamped_candidate":raw*budget[name]/denom[name]})
    if len(module_out)!=6:raise ValueError("Missing module")
    total=cfg["baseline"]+sum(x["applied_signed_score"] for x in module_out)
    if not 0<=total<=100:raise ValueError("Budget overflow is mathematically impossible")
    return {"baseline":cfg["baseline"],"score":total,"six_modules":module_out,
            "legacy_v41_raw":evidence["revised_raw_score"],
            "sub_scores_sum":sum(x["applied_signed_score"] for x in module_out),
            "no_implicit_good_when_rule_not_applicable":True,
            "no_modern_medical_probability":True}

def score_with_context_scenarios(chart,inquiry,calendar,board,cfg):
    duration=inquiry.get("illness_duration")
    if duration not in (None,"new","chronic"):
        raise ValueError("Illness duration must be new/chronic/unknown")
    runs={}
    options=[duration] if duration else [None,"new","chronic"]
    for option in options:
        q=dict(inquiry)
        if option is None:q.pop("illness_duration",None)
        else:q["illness_duration"]=option
        ev=calculate_health_symbolic_score_v41(chart=chart,inquiry=q,calendar=calendar)
        runs[option or "unprovided"]=budgeted_score_from_source(ev,board,cfg)
        runs[option or "unprovided"]["source_context"]=option or "unprovided"
        if option is None:runs["unprovided"]["known_chart_not_missing"]=True
    nominal=runs[duration or "unprovided"]
    return {"observed_or_unspecified_nominal":nominal,
      "conditional_scenarios":{k:v["score"] for k,v in runs.items()},
      "scenario_range":[min(x["score"] for x in runs.values()),
                        max(x["score"] for x in runs.values())],
      "duration_provided":duration is not None,
      "duration_not_invented":True,
      "unknown_personal_context_not_chart_missing":duration is None}

def analyze_health_severity_v42(*,chart,inquiry,calendar,db_path):
    cfg=json.loads(POLICY.read_text("utf8"))
    if cfg.get("version")!="V4.2":
        raise ValueError("Original six-budget research policy required")
    original=analyze_health_severity_v39(
         chart=chart,inquiry=inquiry,calendar=calendar,db_path=db_path)
    board=full_board_facts(chart,calendar,inquiry)
    scores=score_with_context_scenarios(chart,inquiry,calendar,board,cfg)
    nominal=scores["observed_or_unspecified_nominal"]
    display="、".join(x["name"]+("+" if x["applied_signed_score"]>=0 else "")
                      +str(x["applied_signed_score"])
                      for x in nominal["six_modules"])
    extra=("古籍病势象意实验分："+str(nominal["score"])+"/100。"+
           "以50分为中性起点，各模块已设置独立分值预算："+display+"。")
    if not scores["duration_provided"]:
        d=scores["conditional_scenarios"]
        extra+=("占盘内所有星门神与干支已计算；病程未说明，分别计算新病"+
                str(d["new"])+"分、久病"+str(d["chronic"])+
                "分，两种条件取向不冒充真实病史。")
    patient=board["source12_stage_for_actors"]["patient"]
    illness=board["source12_stage_for_actors"]["tianrui_heaven"]
    def stage_text(x):
        return "、".join(e["branch"]+e["stage"] for e in x["all_actual_branch_stages"])
    extra+=(board["patient_stem"]+"在患者宫："+stage_text(patient)+"；"+
           "天芮携"+board["illness_carried_stem"]+"在病宫："+stage_text(illness)+"。"+
           "本分数表示古籍规则下的象意比较，不是现实健康概率、病情评估或用药建议。")
    original_sections=original["sections"]
    if not 10<=len(original_sections)<=11:
        raise ValueError("Source V3.9 customer template must remain unchanged")
    # Append ONLY an additional verified scoring section, never replace
    # any of the stage-accepted V3.9 text or reword it to fit a numeric score.
    sections=[*original_sections,{"id":"12_symbolic_score","title":"传统病势象意分","text":extra}]
    reading=original["reading_text"]+"\n\n"+"传统病势象意分："+extra
    if "原书第" in extra or "SHA" in extra or "数据库" in extra:
        raise ValueError("Technical source metadata must not leak to reader")
    return {"schema":"wengua_health_v42_v39_integrated_source_facts_six_budget_score",
       "version":"V4.2","status":"source_tested_user_review_pending",
       "exact_original_v39_reading":original["reading_text"],
       "legacy_v39_sections":original_sections,
       "sections":sections,"reading_text":reading,
       "traditional_v39_qualitative_verdict":original["audit"]["v37_actual_health_priority_verdict"],
       "chart_evidence":board,"scoring":scores,
       "source_v41_book_81_42_17_trace_preserved":True,
       "clinical_risk":None,"statistical_probability":None,
       "original_historical_author_outcome_used":False,
       "user_approved":False}
