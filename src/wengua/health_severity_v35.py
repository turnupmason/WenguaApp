"""V3.5 evidence-priority correction after seeing genuine 12-case V3.4 audit.

Do NOT modify sealed V3.1, V3.3 or V3.4 outputs. This is a separately
versioned deterministic template with explicit patient-first priorities.
No modern clinical diagnostic validity is asserted.
"""
from __future__ import annotations
from .health_severity_v34 import analyze_health_severity_v34
from .health_severity_v22 import _find_star,_find_heaven_stem,_yes_void,_palace
from .health_dynamic_v21 import bind_patient
from .marriage_runtime import ELEMENTS,element_relation
from .health_severity_v26 import _direction

def patient_first_decision(*,chart,person,ill,prior,evidence):
    """Resolve actual patient -> illness palace -> Tianrui, with counterfacts.

    Double suppression is causally stronger than a single favorable palace,
    but adverse conditions affecting the patient herself remain active.
    Avoid numerical vote-counting or arbitrary medical severity probabilities.
    """
    patient_vs_ill=element_relation(ELEMENTS[person["palace"]],ELEMENTS[ill["palace"]])
    ill_vs_star=element_relation(ELEMENTS[ill["palace"]],"土")
    double=patient_vs_ill=="克" and ill_vs_star=="克"
    void=bool(_yes_void(chart,person))
    risks=[x for x in evidence.get("actual_tomb_punishment_v28",[]) if x["role"]=="patient"]
    patient_hazard=[x["kind"] for x in risks]
    serious_patient_obstruction=any(x in ("六仪击刑","入墓地") for x in patient_hazard)
    strong_illness=prior.get("adverse",[])
    story=[]
    if double:
        story.append("患者宫克病宫，且病宫本身克制天芮土；双重制病使病星受制力量更大")
    elif patient_vs_ill=="克":
        story.append("患者宫克病宫，但病宫对天芮星本体未构成第二重克制")
    elif patient_vs_ill=="受克":
        story.append("病宫克患者宫，为患者受克的不利证据")
    else:
        story.append("患者与病宫的生比关系须结合双方旺衰及星门判断")
    if void:story.append("患者用神旬空，制病之力不可视作完全实得")
    if serious_patient_obstruction:story.append("患者本宫有实算入墓地或六仪击刑等受阻事实")
    # A strong double-control and non-void patient is the important missing
    # source priority. Do NOT let a strong Tianrui month + death door simply
    # erase two independent controls as the old V3.1 implementation did.
    if double and not void and not serious_patient_obstruction:
        verdict="病吉"
        priority="双重制病且患者本宫不空，优先作为传统有利主证；病宫凶门/月旺留为反证"
    elif double and (void or serious_patient_obstruction):
        verdict=prior["verdict"]
        priority="虽有双重制病，患者本宫旬空或刑墓限制制病之力，不能机械改断"
    else:
        verdict=prior["verdict"]
        priority="未具备无阻双重制病条件，保留原有综合主判并列出患者与病星相反证据"
    return {"verdict":verdict,"previous_provisional_verdict":prior["verdict"],
            "double_suppression":double,"patient_void":void,
            "patient_hazards":patient_hazard,"priority":priority,
            "patient_reasoning":story,"no_clinical_prediction":True}

def analyze_health_severity_v35(*,chart,inquiry,calendar=None,db_path=None):
    base=analyze_health_severity_v34(chart=chart,inquiry=inquiry,calendar=calendar,db_path=db_path)
    person_data=bind_patient(chart,inquiry,calendar)
    patient=person_data["main_cell"]
    ill,_=_find_star(chart,"天芮星")
    prior=base["audit"]["traditional_verdict"]
    calc=patient_first_decision(chart=chart,person=patient,ill=ill,prior=prior,evidence=base["audit"])
    attention=base["audit"]["v34_treatment_co_palace"]
    stages=base["audit"]["medical_timing_v28"]
    combined=[]
    # If the original question actually supplies a full 甲旬 birth year (e.g.
    # 1964 甲辰), the matching 六仪 is determinable from that natal pillar.
    # Never borrow the casting HOUR's xun for a different Jia year.
    from .casting_shenqi import SIX_JIA
    birth=inquiry.get("patient_birth_ganzhi") or inquiry.get("subject_year_ganzhi")
    natal=person_data["birth_cell"]
    if birth and birth[:1]=="甲" and birth in SIX_JIA:
        natal=_find_heaven_stem(chart,SIX_JIA[birth])
    # Context known sex and actual traditional gender reference, not generic 乾坤.
    if inquiry.get("relationship") in ("spouse","wife","husband"):
        complementary=person_data["harmony_stem"]
        place=person_data["harmony_palace"]
        person_text=("妻子以乙奇为主，" if person_data["stem"]=="乙" else "丈夫以庚金为主，")
        person_text+="另参日干五合"+complementary
        if place:
            person_text+="所落的"+str(place)+"宫"
        else:
            person_text+="；该合干无可验证天盘落宫，不擅造"
        combined.append(person_text)
    if inquiry.get("relationship") in ("animal","animal_hen","animal_rooster"):
        combined.append("动物无单独明确用神时，以实际时干宫为动物用神")
    if inquiry.get("relationship")=="son_in_law":
        combined.append("原书岳父代测女婿以时干为人物用神")
    if natal:
        combined.append("已给患者年命"+str(birth)+"，另参"+str(natal["palace"])+"宫，不取代本次时干或亲属主用神")
    sections=[]
    for s in base["sections"]:
        phrase=s["text"]
        if s["id"]=="01_role" and combined:
            # Completely replace old V3.4 malformed actor phrase in a NEW
            # version, never edit original sealed source readouts in-place.
            relation=inquiry["relationship"]
            if relation in ("spouse","wife","husband"):
                label="妻子" if person_data["stem"]=="乙" else "丈夫"
                phrase=("依据古籍，此次为"+label+"测病情轻重。"+
                    combined[0]+"；主用神落"+_palace(patient)+"，天芮主病。")
                if len(combined)>1:phrase+="；"+"；".join(combined[1:])+"。"
            elif relation in ("animal","animal_hen","animal_rooster"):
                label=person_data["label"]
                phrase=("依据古籍，此次为"+label+"测病情轻重。无其它明确用神，"
                     "以时干"+person_data["stem"]+"落"+_palace(patient)+
                     "为动物用神，天芮主病。")
            elif relation=="son_in_law":
                phrase=("依据古籍，此次为女婿测病情轻重。岳父代问女婿，"
                       "以时干"+person_data["stem"]+"落"+_palace(patient)+
                       "为用神，天芮主病。")
                if natal:phrase+="另参已知出生年命"+str(birth)+"，落"+_palace(natal)+"。"
        if s["id"]=="11_final":
            attention_text=("时干或病宫与天心/乙奇同宫，传统有及时医治机会；"
                 "医药力量弱或受迫空影响发挥，但不取消这一同宫象"
                 if attention["independent_opportunities"] else
                 "未见时干/病宫与天心乙奇同宫的及时医治象，仍须分别看医药克病")
            # Disclose any original adverse evidence rather than hiding it.
            adverse="、".join(prior.get("adverse",[])[:3]) or "其他宫门证据须合参"
            favorable="、".join(prior.get("favorable",[])[:3]) or "按实际患者宫重新分析"
            phrase=("依据古籍，病情传统综合主判："+calc["verdict"]+"。"
                 + "患者主证："+"；".join(calc["patient_reasoning"])+"。"
                 + "证据优先级："+calc["priority"]+"。"
                 + "医药："+attention_text+"。"
                 + "不利证据："+adverse+"；有利证据："+favorable+"。"
                 + "这只是古籍文化取象，不是现实医学诊断或疗效预告。")
        sections.append({**s,"text":phrase})
    if not sections or any("{" in s["text"] or "}" in s["text"] or "。。" in s["text"] for s in sections):
        raise ValueError("V3.5 fixed source sections invalid")
    return {**base,"schema":"wengua_health_v35_patient_first_true_decision_with_doctor_copalace",
        "sections":sections,"reading_text":"\n\n".join(s["title"]+"："+s["text"] for s in sections),
        "audit":{**base["audit"],"v35_patient_first_decision":calc,
                 "v35_patient_birth_reference":natal["palace"] if natal else None,
                 "v35_doctor_copalace_preserved_even_when_weak":True,
                 "author_book_feedback_used":False,"runtime_gpt_calls":0},
        "user_accepted":False}
