"""V3.9 condensed auditable reader rendering of V3.8 real source facts.

No mutation of prior V3.1-V3.8 sealed outputs. Provenance and family-case
outcomes never appear in customer text. Only actual source-specific stages,
roles, stem combinations and contrary evidence become prose.
"""
from __future__ import annotations
import json,re
from pathlib import Path
from .health_severity_v38 import analyze_health_severity_v38,_customer_clean
from .health_severity_v22 import _find_star,_find_heaven_stem,_palace,_yes_void
from .health_dynamic_v21 import bind_patient
from .marriage_runtime import ELEMENTS,element_relation
from .health_severity_v27 import five_not_encounter

ROOT=Path(__file__).resolve().parents[2]
TEMPLATE=ROOT/"data/knowledge/phrase_library/health_v39/severity_customer_template.json"

def _names(pairs):
    return "、".join(z["top"]+"加"+z["bottom"]+"「"+z["title"]+"」" for z in pairs)

def _short_role(inquiry,profile):
    r=inquiry["relationship"]
    if r=="self":return "本人","日干"
    if r in ("father","mother"):return ("父亲" if r=="father" else "母亲"),"年干"
    if r in ("younger_sibling","brother","sister"):
        sex=inquiry.get("patient_sex")
        name="弟弟" if r=="younger_sibling" and sex=="male" else "妹妹" if r=="younger_sibling" and sex=="female" else "兄弟姐妹"
        return name,"月干"
    if r in ("son","daughter","child","nephew","son_in_law"):
        return {"son":"儿子","daughter":"女儿","child":"子女","nephew":"侄辈","son_in_law":"女婿"}[r],"时干"
    if r.startswith("animal"):return "动物","时干"
    if r in ("spouse","wife","husband"):
        return "妻子" if profile["stem"]=="乙" else "丈夫",("乙奇" if profile["stem"]=="乙" else "庚金")
    return profile["label"],profile["role_name"]

def analyze_health_severity_v39(*,chart,inquiry,calendar=None,db_path=None):
    base=analyze_health_severity_v38(chart=chart,inquiry=inquiry,calendar=calendar,db_path=db_path)
    template=json.loads(TEMPLATE.read_text("utf8"))
    patient_role=bind_patient(chart,inquiry,calendar)
    p=patient_role["main_cell"]
    ill,star=_find_star(chart,"天芮星")
    doctor,_=_find_star(chart,"天心星")
    yi=_find_heaven_stem(chart,"乙")
    hour=_find_heaven_stem(chart,chart["hour_ganzhi"][0])
    if not all((p,ill,doctor,yi,hour)):raise ValueError("Missing real actor/star/time chart palace")
    facts=base["audit"]["v38_actual_illness_derived_tomb_extinct_void"]
    pairs=base["audit"]["v37_81_ordered_full_book_pairs"]
    pair_by_role=lambda label:[x for x in pairs if label in x["roles"]]
    who,which=_short_role(inquiry,patient_role)
    role_text=(who+"以"+which+"为主要用神，落"+_palace(p)+"；"+
        "天芮星是疾病用神，落"+_palace(ill)+"。")
    birth=inquiry.get("patient_birth_ganzhi")
    natal=base["audit"].get("v35_patient_birth_reference")
    if birth and natal:role_text+="已知年命"+birth+"另参"+_palace({"palace":natal})+"。"
    if inquiry.get("patient_sex") in ("male","female") and inquiry["relationship"] in ("father","mother"):
        role_text+="并参"+("乾六宫" if inquiry["patient_sex"]=="male" else "坤二宫")+"。"
    value_star=chart["palaces"][str(chart["value_star_palace"])]
    value_door=chart["palaces"][str(chart["value_door_palace"])]
    value_text=("值符"+chart["value_star"]+"落"+_palace(value_star)+"，值使"+
          chart["value_door"]+"落"+_palace(value_door)+"。")
    if value_star["palace"]==p["palace"]:value_text+="值符与患者用神同宫，权重需提高。"
    if value_star["palace"]==ill["palace"]:value_text+="值符与病星同宫，病势需要重点核对。"
    if value_door["palace"]==p["palace"]:value_text+="值使与患者宫同宫。"
    if value_door["palace"]==ill["palace"]:value_text+="值使与病宫同宫。"
    illness_parts=[
        "天芮"+("与天禽同宫，" if len(ill["heaven_stars"])>1 else "星")+
        "临"+ill["door"]+"、"+ill["deity"]+"。"+
        "所携天盘"+star["carried_stem"]+"加地盘"+ill["earth_stem"]+
        "，"+_names(pair_by_role("病宫"))+"。"]
    direction=element_relation(ELEMENTS[ill["palace"]],"土")
    if direction=="受生":illness_parts.append("天芮土生病宫"+ELEMENTS[ill["palace"]]+"，病星有泄气之象。")
    elif direction=="克":illness_parts.append("病宫"+ELEMENTS[ill["palace"]]+"克天芮土，病星受制。")
    elif direction=="生":illness_parts.append("病宫"+ELEMENTS[ill["palace"]]+"生天芮土，病星受生。")
    elif direction=="比和":illness_parts.append("病宫与天芮同为土，病星有根。")
    else:illness_parts.append("天芮土克病宫"+ELEMENTS[ill["palace"]]+"，仍须辨强弱。")
    present=[]
    if facts["tomb_branch_in_illness_palace"]:
        present.append("天盘"+star["carried_stem"]+"在"+facts["stage_tomb_branch"]+"入墓")
    if facts["extinct_branch_in_illness_palace"]:
        present.append("在"+facts["stage_extinct_branch"]+"临绝")
    if facts["void_in_illness_palace"]:
        present.append("占时"+facts["hour_ganzhi"]+"属"+facts["hour_xun_head"]+
                       "旬，"+"/".join(facts["void_branches"])+"空，"+_palace(ill)+"旬空")
    if present:
        illness_parts.append("；".join(present)+"。")
        if facts["compound_tomb_extinct_void_same_palace"]:
            illness_parts.append("三象同宫，病星所携干的作用受到牵制；空亡还须区分新病久病，"
                   "不可把入墓、绝地、空亡直接等同于疾病结局。")
    # No negative stage sentence if only void or neither condition is present.
    season=calendar["month_branch"]
    month_text=_customer_clean(next(x["text"] for x in base["sections"] if x["id"]=="04_season"))
    pat_pair=pair_by_role("患者宫")
    pr=element_relation(ELEMENTS[p["palace"]],ELEMENTS[ill["palace"]])
    pr_text={"克":"患者宫克病宫，具有制病方向","受克":"病宫克患者宫，用神受克",
             "生":"患者宫生病宫，有助病之象","受生":"病宫生患者宫，患者得生扶",
             "比和":"患者宫与病宫比和，须辨强弱"}[pr]
    patient_text=(who+"宫见"+p["door"]+"、"+p["deity"]+
        "，天地干"+_names(pat_pair)+"。"+pr_text+"。"+
        ("患者宫旬空，力量需打折。" if _yes_void(chart,p) else "患者宫未逢旬空。"))
    if r:=base["audit"].get("v37_2_sided_double_evidence"):
        if r["double_control"]:patient_text+="患者宫制病、病宫又制天芮，两重有利条件相合。"
        if r["double_adverse_types"]:patient_text+="本盘不利关系相互叠加："+"/".join(r["double_adverse_types"])+"。"
    gender_original=next((x["text"] for x in base["sections"] if x["id"]=="06_gender"),"")
    med_base=base["audit"]["medical_timing_v28"]
    med_text=("天心落"+_palace(doctor)+"，"+_names(pair_by_role("天心宫"))+
         "；乙奇落"+_palace(yi)+"，"+_names(pair_by_role("乙奇宫"))+"。"+
         "天心月"+med_base["doc_month"]+"，乙奇月"+med_base["yi_month"]+"。")
    if med_base["matches"]:
        med_text+="时干或病星与医药同宫，有及时得到医治的传统有利象；医药力量弱仍不抵消同宫事实。"
    rel=element_relation(ELEMENTS[yi["palace"]],ELEMENTS[ill["palace"]])
    if rel=="受克":med_text+="病宫克乙奇宫，药象受制。"
    elif rel=="克":med_text+="乙奇宫克病宫，药象能制病。"
    med_text+="这些都不能直接推出药物疗效。"
    tim_rel=element_relation(ELEMENTS[hour["palace"]],ELEMENTS[p["palace"]])
    time_text=("时干"+chart["hour_ganzhi"][0]+"落"+_palace(hour)+"，"+
      _names(pair_by_role("时干宫"))+"。时干代表病情现状，"+
      {"克":"时干宫克患者宫","受克":"患者宫克时干宫","生":"时干宫生患者宫",
       "受生":"患者宫生时干宫","比和":"时干宫与患者宫比和"}[tim_rel]+
      "，需与病宫共同推断发展方向。")
    five=five_not_encounter(calendar["day_ganzhi"],chart["hour_ganzhi"])
    specials=base["audit"]["actual_tomb_punishment_v28"]
    hazard=("本时辰"+("出现五不遇时" if five["triggered"] else "不属五不遇时")+"。")
    pats=[z for z in specials if z["role"]=="patient"]
    if pats:hazard+="患者宫另见"+"、".join(z["kind"] for z in pats)+"。"
    illother=[z for z in specials if z["role"]=="illness" and z["stem"]!=star["carried_stem"]]
    if illother:hazard+="病宫其他携干见"+"、".join(z["stem"]+z["kind"] for z in illother)+"。"
    chief=[z for z in pairs if "值符宫" in z["roles"] or "值使宫" in z["roles"]]
    if chief:hazard+="值符值使宫见"+_names(chief)+"，须合本事取义。"
    gates=base["audit"]["v36_17_source_rechecked_composites"]
    if any(z["id"]=="health_composite_07" and z["state"]=="triggered" for z in gates):
        hazard+="值使宫满足三奇得使。"
    if any(z["id"]=="health_composite_08" and z["state"]=="triggered" for z in gates):
        hazard+="值使宫满足玉女守门。"
    pace=_customer_clean(next(x["text"] for x in base["sections"] if x["id"]=="10_pace"))
    # V3.7 fixed text already has credible source pace/horse but don't
    # repeat stage evidence in hazards or final as an entire paragraph.
    e=base["audit"]["v37_2_sided_double_evidence"]
    old_verdict=base["audit"]["v37_actual_health_priority_verdict"]
    indicative="偏凶" if old_verdict=="病凶" else "偏吉"
    balancing=[]
    if e["illness_palace_vs_tianrui_earth"]=="受生":
        balancing.append("天芮土生病宫"+ELEMENTS[ill["palace"]]+"，病星泄气")
    elif e["illness_palace_vs_tianrui_earth"]=="克":
        balancing.append("病宫克天芮，病星受制")
    illness_favorable=[x for x in pair_by_role("病宫") if x["applicability"] in ("book_health_favorable","book_favorable_formation")]
    if illness_favorable:balancing.append("病宫亦见"+_names(illness_favorable))
    if facts["void_in_illness_palace"]:
        balancing.append("病宫旬空，需辨新病与久病")
    # Distinct branch evidence limits the positive heavenly Bing formation.
    if facts["tomb_branch_in_illness_palace"] or facts["extinct_branch_in_illness_palace"]:
        balancing.append("病星所携"+star["carried_stem"]+"临墓或绝，其相关吉格难以全力发挥")
    if med_base["matches"]:balancing.append("医药同宫仍有医治机会")
    verdict=("综合看，本盘古籍取象"+indicative+"。"+
      pr_text+"；"+
      ("/".join(e["double_adverse_types"])+"。" if e["double_adverse_types"] else
       "双重制病形成有利主证。" if e["double_control"] else
       "其余关系需合看。")+
      "同时还有"+("；".join(balancing) if balancing else "医药和门星的相反作用")+"。"+
      "这是传统象意的分析，不能当作现实疾病诊断、预后或治疗依据。")
    sections=[]
    texts={"01_role":role_text,"02_far":value_text,"03_illness":"".join(illness_parts),
         "04_season":month_text,"05_patient":patient_text,
         "06_gender":_customer_clean(gender_original) if gender_original else None,
         "07_medicine":med_text,"08_hour":time_text,"09_hazards":hazard,
         "10_pace":pace,"11_final":verdict}
    formats={x["id"]:x["format"] for x in template["sections"]}
    if len(formats)!=11:raise ValueError("Complete eleven-slot customer template required")
    for original in base["sections"]:
        id=original["id"]
        raw=texts[id]
        if raw is None:continue
        rendered=_customer_clean(formats[id].format_map({"content":raw}))
        sections.append({**original,"text":rendered})
    if len(sections)!=len(base["sections"]):
        raise ValueError("Do not drop any fixed user section")
    reading="\n\n".join(s["title"]+"："+s["text"] for s in sections)
    _customer_clean(reading)
    return {**base,"schema":"wengua_health_v39_customer_concise_real_stages_no_duplicate",
        "sections":sections,"reading_text":reading,
        "audit":{**base["audit"],"v39_client_stem_stage_selected_only_if_true":True,
            "v39_source_line_only_internal":True,"v39_patient_role_specific":who,
            "v39_earlier_v38_seal_untouched":True,
            "v39_user_content_approved":False,"runtime_gpt_calls":0},
        "user_accepted":False}
