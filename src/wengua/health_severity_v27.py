"""Source-grounded deterministic health-severity V2.7 (no generative runtime).

All customer prose comes from fixed JSON str.format_map slots and local source
facts. Traditional cultural verdict only, NEVER an actual clinical assessment.
Original cases/outcomes are not read by this evaluator (testing isolation).
"""
from __future__ import annotations
import json
from pathlib import Path

from .health_dynamic_v21 import bind_patient, _checked_calendar, _meaning_deity, _meaning_door
from .health_severity_v22 import (
    analyze_health_severity_v22, _find_star, _find_heaven_stem, _palace,
    _body, _read, SHENQI, _yes_void, _phase_from_chart, FORBIDDEN_CUSTOMER
)
from .health_severity_v26 import (
    _direction, _star_relation, _source_pair_prose, _fuyin_text, _pace,
    _inside, _meaning_singular
)
from .health_severity_v25 import fuyin_fanyin_facts, _traditional_choice
from .marriage_runtime import ELEMENTS, element_relation, CONTROLS
from .core import STEMS

ROOT=Path(__file__).resolve().parents[2]
TEMPLATE=ROOT/"data/knowledge/phrase_library/health_v27/severity_fixed_template.json"
STEM_EL={"甲":"木","乙":"木","丙":"火","丁":"火","戊":"土","己":"土",
         "庚":"金","辛":"金","壬":"水","癸":"水"}
YANG_STEMS=set("甲丙戊庚壬")
YIN_STEMS=set("乙丁己辛癸")

def five_not_encounter(day_ganzhi:str,hour_ganzhi:str)->dict:
    """五不遇时：HOUR heavenly stem overcomes DAY stem AND same polarity.

    Important: no "same-sex characters" or palace position substitution.
    The source distinguishes elective action times from inquiry times and
    explicitly says a single bad time is not sufficient for an outcome.
    """
    if not isinstance(day_ganzhi,str) or not isinstance(hour_ganzhi,str):
        raise ValueError("Need historical DAY and HOUR full pillars")
    day,hour=day_ganzhi[:1],hour_ganzhi[:1]
    if day not in STEM_EL or hour not in STEM_EL:
        raise ValueError("Valid day and hour stems required")
    same=(day in YANG_STEMS and hour in YANG_STEMS) or (day in YIN_STEMS and hour in YIN_STEMS)
    controls=CONTROLS[STEM_EL[hour]]==STEM_EL[day]
    triggered=bool(controls and same)
    return {
        "triggered":triggered,"hour_stem":hour,"day_stem":day,
        "hour_element":STEM_EL[hour],"day_element":STEM_EL[day],
        "same_yin_yang":bool(same),"hour_controls_day":bool(controls),
        "rule":"hour_controls_day_same_polarity",
        "source":{"book":"kaiwu","chapter":"analysis_judgment_ch04","lines":[580,590]},
        "effect":"凶时信号，但不单条断生死" if triggered else "不成五不遇时"
    }


def _clinical_role_sign(role_from:str, relation:str)->str:
    """Meaning of directional five elements for a HEALTH target, not all-life fortune."""
    if role_from=="patient":
        return {"克":"偏吉，患者制病","受克":"偏凶，病宫克身",
                "生":"偏凶，患者生扶病宫",
                "受生":"偏吉，患者得病宫生扶，不能据此单断痊愈",
                "比和":"同气相持，须合参其他证据"}[relation]
    if role_from in ("doctor","medicine"):
        return {"克":"偏吉，制病","受克":"偏凶，医药受病宫克制",
                "生":"偏凶，医药宫生扶病宫","受生":"受生但未制病，不能单定疗效",
                "比和":"同气但未制病，须兼看门神"}[relation]
    if role_from=="gender":
        return {"克":"辅助宫制病，偏吉","受克":"辅助宫受病宫克，偏凶",
                "生":"辅助宫生扶病宫，偏凶","受生":"辅助宫得生扶，偏吉",
                "比和":"辅助宫与病宫同气，吉凶未定"}[relation]
    if role_from=="hour":
        return {"克":"事体宫克病宫，偏吉","受克":"事体宫受病宫克，偏凶",
                "生":"事体宫生扶病宫，偏凶",
                "受生":"事体宫受病宫生，需合参，非单凭此断愈",
                "比和":"时干宫与病宫比和，未单定吉凶"}[relation]
    if role_from=="value":
        return {"克":"值符宫克病宫，偏吉","受克":"值符宫受病宫克，偏不利",
                "生":"值符宫生病宫，病象得助，偏不利",
                "受生":"值符宫受病宫生，不能单据此断愈",
                "比和":"值符宫与病宫比和，吉凶需合参"}[relation]
    raise ValueError("Unknown health-significance role")


def _directed(a,b,what):
    return _direction(a,b,{"patient":"患者宫","doctor":"天心宫","medicine":"乙奇宫",
                           "gender":"辅助宫","hour":"时干宫","value":"值符宫"}[what],"病宫") +\
           "，"+_clinical_role_sign(what,element_relation(ELEMENTS[a["palace"]],ELEMENTS[b["palace"]]))


def _star_good_bad(ill):
    p=ELEMENTS[ill["palace"]]
    if p=="土":return "与天芮土比和，病星有根，偏不利"
    if CONTROLS[p]=="土":return p+"克天芮土，病星受制，偏吉"
    if CONTROLS["土"]==p:return "天芮土克落宫"+p+"，病星克宫，偏凶"
    if {"木":"火","火":"土","土":"金","金":"水","水":"木"}[p]=="土":
        return p+"生天芮土，病星受生，偏凶"
    return "天芮土生落宫"+p+"，兼看病星旺衰"


def _sex_from_context(inquiry):
    sex=inquiry.get("patient_sex")
    if sex is None:
        sex={"father":"male","son":"male","mother":"female","daughter":"female"}.get(inquiry.get("relationship"))
    if sex not in (None,"male","female"):
        raise ValueError("Patient sex must be explicit male/female or unknown")
    return sex


def _evidence_and_verdict(ill,person,doctor,medicine,aux,month,stage,five,press,chart):
    """Fixed evidence precedence; preserve all contrary evidence independently."""
    bad=[];good=[]
    if stage in ("旺","相"):
        bad.append("天芮在"+month+"月为"+stage+"，病星有气")
    if ill["door"]=="死门":bad.append("病宫临死门")
    if ill["palace"] in press:bad.append(_palace(ill)+"的"+ill["door"]+"门迫")
    if person["palace"] in press and person["palace"]!=ill["palace"]:
        bad.append(_palace(person)+"的"+person["door"]+"门迫")
    if _yes_void(chart,person):bad.append("患者宫旬空")
    if ill["deity"]=="白虎":bad.append("病星乘白虎")
    if five["triggered"]:bad.append("五不遇时，时干克日干且阴阳同性")
    star_rel=element_relation(ELEMENTS[ill["palace"]],"土")
    if star_rel=="克":good.append("病宫五行克天芮，病星受制")
    if element_relation(ELEMENTS[doctor["palace"]],ELEMENTS[ill["palace"]])=="克":
        good.append("天心宫克病宫")
    if element_relation(ELEMENTS[medicine["palace"]],ELEMENTS[ill["palace"]])=="克":
        good.append("乙奇宫克病宫")
    if person["door"] in ("开门","休门","生门"):
        good.append("患者临"+person["door"])
    if not _yes_void(chart,person):good.append("患者宫不空")
    if aux and aux["palace"]!=person["palace"]:
        rel=element_relation(ELEMENTS[aux["palace"]],ELEMENTS[ill["palace"]])
        if rel in ("克","受生"):good.append("乾坤辅助宫有生扶或制病象")
        elif rel in ("生","受克"):bad.append("乾坤辅助宫生病或受克")
    # Five-not-encounter is an adverse factor, NOT automatic death or sole determinant.
    # Preserve original disease/medical precedence, adding actual focus-door-press
    # and patient-void qualifiers; do not mechanically count every palace equally.
    base=_traditional_choice(
        ill,person,doctor,medicine,stage,star_rel,_yes_void(chart,person))
    decisive_bad=bool(stage in ("旺","相") and ill["door"]=="死门")
    focus_pressure=ill["palace"] in press or person["palace"] in press
    strong_resistance=(star_rel=="克" and
      (element_relation(ELEMENTS[doctor["palace"]],ELEMENTS[ill["palace"]])=="克"
       or element_relation(ELEMENTS[medicine["palace"]],ELEMENTS[ill["palace"]])=="克")
      and not _yes_void(chart,person))
    if decisive_bad and (five["triggered"] or focus_pressure or _yes_void(chart,person)) and not strong_resistance:
        verdict="病凶";reason="病星有气临死门，另遇"+("五不遇时" if five["triggered"] else "宫位阻滞象")
    else:
        verdict=base["verdict"]
        reason=("病宫和患者、医药的传统生克合断偏吉" if verdict=="病吉"
                else "病星及患者宫的不利条件在本盘占主导")
    main=("；".join(bad[:4]) if verdict=="病凶" else "；".join(good[:4])) or reason
    counter=("；".join(good[:3]) if verdict=="病凶" else "；".join(bad[:3]))
    return {"verdict":verdict,"main":main,"counter":counter,
            "adverse":bad,"favorable":good,"priority":reason,
            "book_symbolic_only":True,"clinical_validation":False}


def analyze_health_severity_v27(*,chart,inquiry,calendar=None,db_path=None):
    if not isinstance(inquiry,dict) or inquiry.get("intent")!="severity":
        raise ValueError("Four unapproved health intents remain blocked")
    calendar=_checked_calendar(calendar,chart)
    base=analyze_health_severity_v22(chart=chart,inquiry=inquiry,calendar=calendar,db_path=db_path)
    profile=bind_patient(chart,inquiry,calendar)
    person=profile["main_cell"]
    if not person:raise ValueError("Patient signifier unresolved; do not force birth-year")
    pack=json.loads(TEMPLATE.read_text("utf8"))
    ill,carried=_find_star(chart,"天芮星")
    doctor,_=_find_star(chart,"天心星")
    medicine=_find_heaven_stem(chart,"乙")
    event=_find_heaven_stem(chart,chart["hour_ganzhi"][0])
    if not (medicine and event):raise ValueError("Missing necessary original chart symbol")
    five=five_not_encounter(calendar["day_ganzhi"],chart["hour_ganzhi"])
    sex=_sex_from_context(inquiry)
    aux=chart["palaces"][str(6 if sex=="male" else 2)] if sex else None
    press=base["audit"]["actual_door_press_palaces"]
    stage=_phase_from_chart(ill,calendar["month_branch"])
    fy=fuyin_fanyin_facts(chart)
    evidence=_evidence_and_verdict(ill,person,doctor,medicine,aux,
               calendar["month_branch"],stage,five,press,chart)
    pair=base["audit"]["stem_pair_source"]
    if pair["id"]!="heaven_over_earth:"+carried["carried_stem"]+":"+ill["earth_stem"]:
        raise ValueError("Source pair not the original illness palace")
    if sex:
        gender_rel=_directed(aux,ill,"gender")
        if aux["palace"]==person["palace"]:
            gender_symbol="与主用神同宫，不重复计入吉凶"
        else:
            gender_symbol="临"+_meaning_singular(aux,chart)
        gender_label="男性患者" if sex=="male" else "女性患者"
        if aux["palace"] in press:
            gender_rel+="；辅助宫"+aux["door"]+"门迫，偏凶"
        if _yes_void(chart,aux):
            gender_rel+="；辅助宫逢空，吉象受虚"
    else:gender_rel=gender_symbol=gender_label=""
    if five["triggered"]:
        five_phrase=("五不遇时：时干"+five["hour_stem"]+five["hour_element"]+
         "克日干"+five["day_stem"]+five["day_element"]+
         "，"+("阳克阳" if five["hour_stem"] in YANG_STEMS else "阴克阴")+
         "，测病为传统凶时，但不可仅凭此断生死")
    else:
        five_phrase=("时干"+five["hour_stem"]+"未对日干"+five["day_stem"]+
                     "构成同性相克，不属五不遇时")
    focal=[]
    for p,role_label in ((ill["palace"],"病宫"),(person["palace"],"患者宫")):
        if p in press and not any(p==q for q,_ in focal):
            focal.append((p,role_label))
    focal_txt="；".join(role_label+_palace(chart["palaces"][str(p)])+
             "的"+chart["palaces"][str(p)]["door"]+"门迫，偏凶" for p,role_label in focal)
    if not focal_txt:focal_txt="病宫和患者宫没有门迫"
    p_void="患者宫逢旬空，偏凶" if _yes_void(chart,person) else "患者宫不空，有利于用神发挥"
    with_extra=[x["star"] for x in ill["heaven_stars"] if x["star"]!="天芮星"]
    with_extra=("与"+"、".join(with_extra)+"同") if with_extra else ""
    surface,internal=_body(_read(SHENQI),ill["palace"])
    vstar=chart["palaces"][str(chart["value_star_palace"])]
    vdoor=chart["palaces"][str(chart["value_door_palace"])]
    gender_palette="乾六宫" if sex=="male" else "坤二宫" if sex else ""
    role_name=("本人以日干"+profile["stem"]+"为用神" if inquiry["relationship"]=="self"
       else "以"+profile["role_name"].replace("（长辈候选）","")+"为患者用神")
    if inquiry.get("patient_birth_ganzhi"):
        role_name+="，另参年命"+inquiry["patient_birth_ganzhi"]
    pace=_pace(fy,ill,person,chart["dun"])
    inner_ill=_inside(ill,chart["dun"]);inner_p=_inside(person,chart["dun"])
    inner_fact=(("阴遁" if chart["dun"]=="yin" else "阳遁")+
                "病宫在"+inner_ill+"、患者宫在"+inner_p)
    ill_door_sign=("偏凶" if ill["door"]=="死门" else
        "吉象需合看" if ill["door"] in ("生门","开门","休门") else "结合用神")
    ill_deity_sign=("偏凶" if ill["deity"]=="白虎" else
       "主牵连、协调" if ill["deity"]=="六合" else "作辅助判断")
    doctor_effect=_directed(doctor,ill,"doctor")
    medicine_effect=_directed(medicine,ill,"medicine")
    age=inquiry.get("illness_duration")
    timing="不强断具体应期"
    if "反吟" in (fy["star"],fy["door"]) and age in ("new","chronic"):
        timing+="，新病反吟另有趋愈之象" if age=="new" else "，久病反吟另有不利之象"
    fields={
      "person_label":profile["label"],"subject_method":role_name,
      "person_palace":_palace(person),
      "value_star":chart["value_star"],"value_door":chart["value_door"],
      "value_star_palace":_palace(vstar),"value_door_palace":_palace(vdoor),
      "value_relation":_directed(vstar,ill,"value"),
      "with_extra_stars":with_extra,"ill_palace":_palace(ill),
      "ill_door":ill["door"],"ill_deity":ill["deity"],
      "ill_heaven":carried["carried_stem"],"ill_earth":ill["earth_stem"],
      "star_palace_meaning":_star_good_bad(ill),
      "door_deity_meaning":ill["door"]+"主"+_meaning_door(ill["door"])+"，"+ill_door_sign+
                           "；"+ill["deity"]+"主"+_meaning_deity(ill["deity"])+"，"+ill_deity_sign,
      "pair_domain_meaning":_source_pair_prose(pair,carried["carried_stem"],ill["earth_stem"],chart,ill),
      "body_image":"、".join([surface,internal]),
      "month_branch":calendar["month_branch"],"stage":stage,
      "stage_meaning":("病星有气，偏不利" if stage in ("旺","相") else
                       "病星气弱，偏有利但仍看患者宫"),
      "person_star_door_deity":_meaning_singular(person,chart),
      "person_vs_ill_relation":_directed(person,ill,"patient"),
      "patient_void_or_factor":p_void,
      "sex_label":gender_label,"gender_palace":gender_palette,
      "gender_symbol_sentence":gender_symbol,"gender_vs_ill_relation":gender_rel,
      "doctor_palace":_palace(doctor),"medicine_palace":_palace(medicine),
      "doctor_effect":doctor_effect,"medicine_effect":medicine_effect,
      "hour_stem":chart["hour_ganzhi"][0],"event_palace":_palace(event),
      "event_relation":_directed(event,ill,"hour"),
      "five_not_encounter_sentence":five_phrase,
      "targeted_press_sentence":focal_txt,
      "fuyin_fanyin_statement":_fuyin_text(fy),
      "inner_outer_statement":inner_fact,"pace_statement":pace,
      "timing_statement":timing,
      "final_verdict":evidence["verdict"],
      "major_evidence_sentence":"主因："+evidence["main"],
      "counter_evidence_sentence":("反证："+evidence["counter"] if evidence["counter"] else
                                   "其他宫位证据不足以改变主判"),
      "final_tempo_sentence":("传统缓急偏慢" if "慢" in pace else
                              "传统缓急偏快" if "快" in pace else
                              "传统缓急尚难单定"),
    }
    visible=[]
    for section in pack["sections"]:
        if section.get("optional")=="patient_sex" and not sex:continue
        text=section["format"].format_map(fields)
        forbidden=tuple(FORBIDDEN_CUSTOMER)+tuple(pack["validation"]["no_tokens"])
        hits=[x for x in forbidden if x in text]
        if hits:
            raise ValueError("Invalid V2.7 template render at "+section["id"]+": "+repr(hits)+"; output="+text)
        if any(x in text for x in ("{","}","（未提供","门门迫","与与")):
            raise ValueError("Invalid static template output")
        visible.append({"id":section["id"],"title":section["title"],"text":text})
    if len(visible)!=(11 if sex else 10):
        raise ValueError("Gender subsection selection mismatch")
    audit={
        **base["audit"],
        "source_21_facts_retained":21,"real_patient_sex":sex,
        "five_not_encounter":five,
        "gender_auxiliary_palace":aux["palace"] if aux else None,
        "gender_auxiliary_role":"Qian6" if sex=="male" else "Kun2" if sex=="female" else None,
        "fuyin_fanyin":fy,
        "full_board_door_press":press,
        "focus_press":focal,
        "traditional_verdict":evidence,
        "opposite_evidence_retained":True,
        "runtime_gpt_calls":0,"runtime_network_calls":0,
        "user_review_status":"pending",
        "clinical_prognosis":False,
        "original_case_outcomes_read":False,
        "renderer":"pure_python_static_template_11_slots"}
    return {
        "schema":pack["schema"],"domain":"health","intent":"severity",
        "sections":visible,"reading_text":"\n\n".join(x["title"]+"："+x["text"] for x in visible),
        "audit":audit,"source_provenance":base["source_provenance"],
        "user_accepted":False
    }
