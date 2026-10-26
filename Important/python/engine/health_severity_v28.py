"""V2.8 fixed, offline extension: timely treatment, doctor/medicine strength,
original source tomb and 六仪击刑 facts. Never rewrite V2.7 sealed readings.
V2.8 only replaces the five new JSON phrase slots in the eleven-section
original deterministic template; unmodified sections remain byte-identical.
"""
from __future__ import annotations
import json
from pathlib import Path
from .health_severity_v27 import analyze_health_severity_v27, _directed
from .health_severity_v22 import _find_star, _find_heaven_stem, _palace, _yes_void, FORBIDDEN_CUSTOMER
from .health_severity_template import MONTH_ELEMENTS
from .marriage_runtime import PALACE_BRANCHES,CONTROLS
from .semantic_lookup import nine_star_month_status
from .symbol_relations import stem_stage

ROOT=Path(__file__).resolve().parents[2]
TEMPLATE=ROOT/"data/knowledge/phrase_library/health_v28/severity_fixed_template.json"
GENERATES={"木":"火","火":"土","土":"金","金":"水","水":"木"}
STEM_ELEMENTS={"甲":"木","乙":"木","丙":"火","丁":"火","戊":"土","己":"土",
               "庚":"金","辛":"金","壬":"水","癸":"水"}
STRIKING_PALACE={"戊":3,"己":2,"庚":8,"辛":9,"壬":4,"癸":4}
RELEVANT={"illness":"病宫","patient":"患者宫","event":"时干宫",
          "doctor":"天心宫","medicine":"乙奇宫","gender":"乾坤辅助宫"}

def yi_month_stage(month_branch):
    """乙奇取普通木五行旺相休囚死，不套九星『废』的月令公式。"""
    month=MONTH_ELEMENTS[month_branch]
    elem="木"
    if month==elem:stage="旺"
    elif GENERATES[month]==elem:stage="相"
    elif GENERATES[elem]==month:stage="休"
    elif CONTROLS[elem]==month:stage="囚"
    elif CONTROLS[month]==elem:stage="死"
    else:raise ValueError("Unverified month element")
    return stage

def related_special_facts(chart, selected):
    """源：开悟第四章506-544；每一条与实际天盘仪、落宫严配。

    天干入墓地与时干「墓/库」是两个级别；月令未充分支持时不
    把墓地泛称墓凶或计算一个虚构的出墓日期。
    """
    results=[]
    for role,cell,stems in selected:
        if cell is None:continue
        stems=stems if stems is not None else [s["carried_stem"] for s in cell["heaven_stars"]]
        for stem in sorted(set(stems)):
            if stem not in STEM_ELEMENTS:continue
            candidate=[]
            if STRIKING_PALACE.get(stem)==cell["palace"]:
                candidate.append(("六仪击刑","偏凶，主阻滞伤病","kaiwu:506-528"))
            branch=stem_stage(stem,"墓")["branch"]
            if branch in PALACE_BRANCHES[cell["palace"]]:
                candidate.append(("入墓地","受困，作用减弱；仍须按月令辨墓与库",
                                  "shenqi_symbols:253-259;kaiwu:530-544"))
            for kind,effect,source in candidate:
                item={"palace":cell["palace"],"stem":stem,"kind":kind,
                      "effect":effect,"role":role,"source":source}
                if not any((q["palace"],q["stem"],q["kind"])==
                           (item["palace"],item["stem"],item["kind"]) for q in results):
                    results.append(item)
    return results

def treatment_evidence(chart,month_branch,doctor,medicine,ill,event,press):
    """Both independent same-palace triggers; therapy opportunity != efficacy."""
    doc_phase=nine_star_month_status("天心星",MONTH_ELEMENTS[month_branch])["value"]
    yi_phase=yi_month_stage(month_branch)
    matched=[]
    for anchor,cell in (("时干",event),("病宫",ill)):
        for role,medicine_cell in (("天心",doctor),("乙奇",medicine)):
            if cell["palace"]==medicine_cell["palace"]:
                matched.append((anchor,role,cell["palace"]))
    problems=[]
    if doc_phase in ("废","囚"):problems.append("天心月"+doc_phase+"，医生象偏弱")
    if yi_phase in ("囚","死"):problems.append("乙奇月"+yi_phase+"，医药象偏弱")
    for name,cell in (("天心",doctor),("乙奇",medicine)):
        if _yes_void(chart,cell):problems.append(name+"宫旬空，吉象受虚")
        if cell["palace"] in press:problems.append(name+"宫"+cell["door"]+"构成门迫，偏不利")
    if matched:
        statement="、".join(anchor+"与"+name+"同在"+_palace(chart["palaces"][str(p)])
                          for anchor,name,p in matched)+"，传统主有及时得到医治的机会"
        statement+=("；但"+"、".join(problems[:3])+"，不能直接断治疗见效"
                    if problems else "；实际疗效仍须结合医药克病和患者宫")
    else:statement=""
    event_statement="、".join("时干与"+name+"同宫" for anchor,name,p in matched if anchor=="时干")
    return {"matches":[{"trigger":a,"medicine_symbol":b,"palace":p} for a,b,p in matched],
            "triggered":bool(matched),
            "doc_month":doc_phase,"yi_month":yi_phase,
            "doctor_meaning":"较有力" if doc_phase in ("旺","相") else "偏弱",
            "yi_meaning":"较有力" if yi_phase in ("旺","相") else "偏弱",
            "limits":problems,"timing":statement,
            "event":event_statement,
            "not_treatment_success_or_medical_forecast":True}

def analyze_health_severity_v28(*,chart,inquiry,calendar=None,db_path=None):
    """Old historical predictions stay frozen. All changed prose: fixed JSON."""
    previous=analyze_health_severity_v27(
        chart=chart,inquiry=inquiry,calendar=calendar,db_path=db_path)
    month_branch=calendar["month_branch"]
    ill,_=_find_star(chart,"天芮星")
    doctor,_=_find_star(chart,"天心星")
    medicine=_find_heaven_stem(chart,"乙")
    event=_find_heaven_stem(chart,chart["hour_ganzhi"][0])
    if not medicine or not event:raise ValueError("Missing visible medicine or hour stem")
    press=previous["audit"]["full_board_door_press"]
    treatment=treatment_evidence(chart,month_branch,doctor,medicine,ill,event,press)
    from .health_dynamic_v21 import bind_patient
    patient=bind_patient(chart,inquiry,calendar)["main_cell"]
    roles=[("illness",ill,None),("patient",patient,None),
           ("doctor",doctor,None),("medicine",medicine,["乙"]),
           ("event",event,[chart["hidden_stem"] if chart["hour_ganzhi"][0]=="甲"
                                   else chart["hour_ganzhi"][0]])]
    sex=previous["audit"]["real_patient_sex"]
    if sex:
        aux=chart["palaces"]["6" if sex=="male" else "2"]
        roles.append(("gender",aux,None))
    special=related_special_facts(chart,roles)
    def evidence_phrase(f):
        return (_palace(chart["palaces"][str(f["palace"])])+
                "天盘"+f["stem"]+f["kind"]+"，"+f["effect"])
    special_text=("；"+"；".join(map(evidence_phrase,special))) if special else ""
    medical_limit=("；"+"；".join(treatment["limits"][:4])) if treatment["limits"] else ""
    old_by_id={x["id"]:x for x in previous["sections"]}
    def parts(section,n):
        p=old_by_id[section]["text"].rstrip("。").split("。")
        if len(p)!=n:raise ValueError("Earlier fixed template source format unexpectedly changed "+section+" "+str(len(p)))
        return p
    special_old=parts("09_hazards",2)
    rhythm_old=parts("10_pace",4)
    final_old=parts("11_final",4)
    event_old=parts("08_hour",2)
    fields={
      "doctor_palace":_palace(doctor),"medicine_palace":_palace(medicine),
      "doctor_month_stage":treatment["doc_month"],"medicine_month_stage":treatment["yi_month"],
      "doctor_strength_judgement":"医生象"+treatment["doctor_meaning"],
      "medicine_strength_judgement":"医药象"+treatment["yi_meaning"],
      "doctor_effect":_directed(doctor,ill,"doctor"),
      "medicine_effect":_directed(medicine,ill,"medicine"),
      "medical_obstacles":medical_limit,
      "hour_stem":chart["hour_ganzhi"][0],"event_palace":_palace(event),
      "event_relation":event_old[1],
      "timely_treatment_event":("；"+treatment["event"] if treatment["event"] else ""),
      "five_not_encounter_sentence":special_old[0],
      "targeted_press_sentence":special_old[1],
      "tomb_punishment_sentence":special_text,
      "fuyin_fanyin_statement":rhythm_old[0],
      "inner_outer_statement":rhythm_old[1],
      "pace_statement":rhythm_old[2],
      "timing_statement":rhythm_old[3],
      "timely_treatment_timing":("；"+treatment["timing"] if treatment["timing"] else ""),
      "final_verdict":previous["audit"]["traditional_verdict"]["verdict"],
      "major_evidence_sentence":final_old[1],
      "counter_evidence_sentence":final_old[2],
      "timely_treatment_verdict":(
          "；有及时医治之象，但不能仅凭同宫推断康复"
          if treatment["triggered"] else ""),
      "final_tempo_sentence":final_old[3]
    }
    doc=json.loads(TEMPLATE.read_text("utf8"))
    if len(doc["sections"])!=11:raise ValueError("11 fixed sections required")
    edited_ids=set(("07_medicine","08_hour","09_hazards","10_pace","11_final"))
    result=[]
    for original in previous["sections"]:
        section=next(x for x in doc["sections"] if x["id"]==original["id"])
        if original["id"] in edited_ids:
            rendered=section["format"].format_map(fields)
            if any(x in rendered for x in tuple(FORBIDDEN_CUSTOMER)+tuple(doc["validation"]["no_tokens"])):
                raise ValueError("Bad customer phrase in "+original["id"])
            if "{" in rendered or "}" in rendered:
                raise ValueError("Template slot missing")
            result.append({**original,"text":rendered})
        else: result.append(original)
    new_audit={**previous["audit"],
        "medical_timing_v28":treatment,
        "actual_tomb_punishment_v28":special,
        "medicine_phase_method":"ordinary_wuxing_wang_xiang_xiu_qiu_si",
        "doctor_phase_method":"nine_star_wang_xiang_xiu_qiu_fei",
        "runtime_gpt_calls":0,"runtime_network_calls":0,
        "historical_sealed_v27_unmodified":True,"user_review_status":"pending"}
    return {**previous,"schema":doc["schema"],"sections":result,
            "reading_text":"\n\n".join(x["title"]+"："+x["text"] for x in result),
            "audit":new_audit,"user_accepted":False}
