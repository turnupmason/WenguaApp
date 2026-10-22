"""V3.7 health reading: all 81 ORIGINAL ordered heaven/earth name records,
balanced true double-control vs two kinds of double-adverse evidence.

Uses only original source predicates + already verified V3.6 exact chart.
Never uses outcome to tune a historical verdict, and never claims medical
diagnosis, mortality, efficacy, or recovery date. Pure Python offline.
"""
from __future__ import annotations
import json,re
from pathlib import Path
from .health_severity_v36 import analyze_health_severity_v36
from .health_severity_v22 import _find_star,_find_heaven_stem,_yes_void,_palace
from .health_dynamic_v21 import bind_patient
from .health_severity_v34 import _cell_stems
from .marriage_runtime import ELEMENTS,element_relation
from .health_severity_v26 import _star_relation

ROOT=Path(__file__).resolve().parents[2]
ALL_BOOK_PAIRS=ROOT/"data/knowledge/kaiwu/analysis_judgment_ch04/ordered_stem_pairs.json"
HEALTH_PAIRS=ROOT/"data/knowledge/phrase_library/health_v30/user_20261022_pair_catalog.json"
TEMPLATE=ROOT/"data/knowledge/phrase_library/health_v37/severity_fixed_template.json"
PALETTES={1:"坎",2:"坤",3:"震",4:"巽",5:"中",6:"乾",7:"兑",8:"艮",9:"离"}

def _title_from_source(text,top,bottom):
    # Source text takes priority over a newly guessed label.
    for pat in (r'(?:名曰|名谓|名为|叫作|故曰|故名|古人名|称为|叫做)[^。]{0,9}[“"]([^”"]{1,22})[”"]',
                r'[“"]([^”"]{2,18})[”"](?:凶格|吉格|格)'):
        m=re.search(pat,text)
        if m:return m.group(1)
    return top+"加"+bottom+"（原书未明确另名）"

def load_81_book_pairs():
    o=json.loads(ALL_BOOK_PAIRS.read_text("utf8"))
    if o.get("ordered_not_symmetric") is not True or len(o["pairs"])!=81:
        raise ValueError("Only 81 source-attested ordered heaven/earth pairs permitted")
    out={}
    for item in o["pairs"]:
        key=item["pair_key"]
        if key!=item["top"]+"/"+item["bottom"] or key in out:
            raise ValueError("Invalid or duplicated ordered book combination")
        if not item.get("source_original") or len(item.get("excerpt_sha256",""))!=64:
            raise ValueError("Missing original line and SHA evidence")
        out[key]=item
    if len(out)!=81:raise ValueError("Original nine-times-nine source must be complete")
    return out

def _role_pair_polarity(text,mode,roles):
    # Polarity is not a modern clinical claim, and depends on actual role.
    # Disease-specific original text overrides generic "lucky formation."
    if "病宫" in roles:
        if "测人疾病也不凶" in text or "测病" in text and "不凶" in text:
            return "book_health_favorable"
        if ("测病也主凶" in text or "测疾病，遇此格，不仅不吉" in text
            or "如测疾病，遇此格，不仅显示病重" in text):
            return "book_health_adverse"
    if mode=="conflict":return "book_conflicted"
    if mode=="duration":return "book_duration_qualified"
    # Explicit traditional adverse formation is evidence in a person's own
    # palace even if the book didn't discuss illness specifically.
    if re.search(r'(?<!不)(?:大凶之格|大凶|凶格|主凶|皆不利|病.*垂危)',text):
        return "book_adverse_formation"
    if re.search(r'(?:吉格|第一吉格|第二吉格|测人疾病也不凶)',text):
        if any(v in text for v in ("门凶","遇上门迫","如果","但是","同样","但如果","凶格")):
            return "book_conditional_auspicious"
        return "book_favorable_formation"
    return "book_context_required"

def actual_81_pair_context(chart,patient,ill,doctor,yi,hour):
    source=load_81_book_pairs()
    supplement=json.loads(HEALTH_PAIRS.read_text("utf8"))
    extra={(x["heaven"],x["earth"]):x for x in supplement["pairs"]}
    expected=42
    if len(extra)!=expected:raise ValueError("User's 42 supplemental conditional rows were dropped")
    vp=chart["value_star_palace"];vd=chart["value_door_palace"]
    roles_by_palace={}
    for role,cell in [("患者宫",patient),("病宫",ill),("时干宫",hour),
                      ("天心宫",doctor),("乙奇宫",yi),
                      ("值符宫",chart["palaces"][str(vp)]),
                      ("值使宫",chart["palaces"][str(vd)]),
                      ("天芮地盘坤本位",chart["palaces"]["2"])]:
        roles_by_palace.setdefault(cell["palace"],[]).append(role)
    matches=[]
    for p in range(1,10):
        c=chart["palaces"][str(p)]
        if p==5:
            if c["heaven_stars"] or c["door"] or c["deity"]:
                raise ValueError("Centre five cannot hold invented regular star/door/deity")
            continue
        for star in c["heaven_stars"]:
            top=star["carried_stem"];bottom=c["earth_stem"]
            key=top+"/"+bottom
            if key not in source:raise ValueError("Unmatched original full 81 catalog: "+key)
            record=source[key]
            addon=extra.get((top,bottom))
            roles=roles_by_palace.get(p,[])
            effect=_role_pair_polarity(record["source_original"],addon["mode"] if addon else None,roles)
            title=_title_from_source(record["source_original"],top,bottom)
            if addon and addon["name"] and addon["name"]!=title:
                # Different book names are source-alternative labels, never
                # overwrite original author name or turn into 2 independent signs.
                aliases=[addon["name"]]
            else:aliases=[]
            matches.append({
                "palace":p,"star":star["star"],"roles":roles,
                "top":top,"bottom":bottom,"pair_key":key,"title":title,
                "alternate_user_health_name":aliases,
                "source_line":record["source_line"],
                "source_sha256":record["excerpt_sha256"],
                "source_original":record["source_original"],
                "source_conditions":record["source_conditions_present"],
                "applicability":effect,
                "user_health_supplement":addon["id"] if addon else None,
                "interpretation_policy":"book_role_and_gate_conditions_not_a_medical_diagnosis"
            })
    if len(matches)!=9:raise ValueError("Expected precisely nine actual stars with sky stems")
    return matches

def two_sided_evidence(*,patient,ill,patient_void,patient_hazards,patient_pairs,
                       month_phase, doctor_controls, yi_controls):
    """No pair may count twice as evidence. Strict directions and vetoes."""
    p_el=ELEMENTS[patient["palace"]];i_el=ELEMENTS[ill["palace"]]
    rel=element_relation(p_el,i_el)
    star_rel=element_relation(i_el,"土")
    controls_person=rel=="受克"                  # illness controls patient
    controls_illness=rel=="克"                 # patient controls illness
    illness_grows_star=star_rel in ("生","比和") # illness palace gives to Tianrui OR earth sustains earth
    illness_gives_to_patient=rel=="受生"       # ill generates patient, not adverse
    feeds_illness=rel=="生"                    # patient generates illness palace
    direct_star_control=star_rel=="克"         # illness controls Tianrui
    adverse_person_pair=[r for r in patient_pairs
        if r["applicability"] in ("book_adverse_formation","book_health_adverse")]
    # Identical palace or two Tianqin-carried variants are not two independent
    # palaces and may not inflate a "double" score.
    distinct=patient["palace"]!=ill["palace"]
    double_control=distinct and controls_illness and direct_star_control
    double_adverse_growth=distinct and controls_person and illness_grows_star
    double_adverse_chain=distinct and feeds_illness and star_rel=="生"
    double_adverse_person_combo=distinct and controls_person and bool(adverse_person_pair)
    adverse_types=[]
    if double_adverse_growth:adverse_types.append("病宫克患者、病宫又生扶或同气助病星")
    if double_adverse_chain:adverse_types.append("患者宫生病宫、病宫再生病星")
    if double_adverse_person_combo:
        adverse_types.append("病宫克患者、患者宫又临原书凶格")
    positive_types=[]
    if double_control:positive_types.append("患者宫克病宫、病宫又克天芮土")
    # Present supporting evidence but do not pretend neutral/weak means safety.
    i_to_star={
       "克":"病宫克天芮土，病星受宫制",
       "生":"病宫生天芮土，病星得宫生扶",
       "比和":"病宫与天芮同属土，病星有根",
       "受生":"天芮土生病宫五行，病星泄气，需结合月令",
       "受克":"天芮土克病宫五行，不能误称病宫制病"
    }[star_rel]
    hazard=any(x in ("六仪击刑","入墓地") for x in patient_hazards)
    # A double adverse from geometry is different from a compounded symbolic
    # adverse of disease attack plus bad patient palace. Preserve both.
    active_double_bad=bool(adverse_types)
    medical_counter=doctor_controls or yi_controls
    if double_control and not patient_void and not hazard:
        choice="病吉";priority="双重制病成立、病人用神不空且无已核刑墓，传统倾向有利"
    elif active_double_bad and not medical_counter:
        choice="病凶";priority="两项不同的传统凶证相互加强，患者宫受制；不能以单个吉格推翻主证"
    elif active_double_bad and medical_counter:
        choice="病凶";priority="双重凶证存在，但医药有克病反证，传统偏不利且需保持条件判断"
    else:
        choice=None;priority="未形成无阻双重制病或双重不利，沿用综合主判并保留冲突证据"
    if patient_void or hazard:
        priority+="；患者用神空亡/刑墓使制病力量受阻" if double_control else "；患者宫空亡或刑墓需加强谨慎"
    return {
       "patient_element":p_el,"illness_element":i_el,
       "patient_vs_illness":rel,"illness_palace_vs_tianrui_earth":star_rel,
       "illness_star_relation_prose":i_to_star,
       "double_control":bool(double_control),
       "double_adverse_disease_growth":bool(double_adverse_growth),
       "double_adverse_patient_nourishes":bool(double_adverse_chain),
       "double_adverse_patient_formation":bool(double_adverse_person_combo),
       "double_adverse_types":adverse_types,"double_favorable_types":positive_types,
       "actual_patient_adverse_formation":[
           {"name":x["title"],"pair":x["pair_key"],"source_line":x["source_line"]}
           for x in adverse_person_pair],
       "patient_void":bool(patient_void),"patient_hazards":patient_hazards,
       "medicine_controlling_palace_counter":bool(medical_counter),
       "decision_override":choice,"priority":priority,
       "scope":"traditional_cultural_judgment_only"
    }

def _pairs_for(pairs,role):
    return [p for p in pairs if role in p["roles"]]

def _describe(pair):
    name=pair["title"]
    aliases=pair["alternate_user_health_name"]
    if aliases:name+="（另有"+"/".join(aliases)+"之名）"
    polarity={
       "book_health_favorable":"原书测病有利象",
       "book_health_adverse":"原书测病不利象",
       "book_adverse_formation":"原书凶格，须结合本宫",
       "book_conditional_auspicious":"原书吉格但受条件限制",
       "book_favorable_formation":"原书吉格，不能直接代替问病判断",
       "book_conflicted":"不同书法存在取义冲突",
       "book_duration_qualified":"须辨新病久病",
       "book_context_required":"须合宫、门、用神判断"
    }[pair["applicability"]]
    return (PALETTES[pair["palace"]]+str(pair["palace"])+"宫"+
        "天盘"+pair["top"]+"加地盘"+pair["bottom"]+
        "，"+name+"，"+polarity+"（原书第"+str(pair["source_line"])+"行）")

def analyze_health_severity_v37(*,chart,inquiry,calendar=None,db_path=None):
    if inquiry.get("intent")!="severity":
        raise ValueError("Other four disease intentions not yet professionally approved")
    base=analyze_health_severity_v36(chart=chart,inquiry=inquiry,calendar=calendar,db_path=db_path)
    patient=bind_patient(chart,inquiry,calendar)["main_cell"]
    if not patient:raise ValueError("No actual patient role")
    ill,_=_find_star(chart,"天芮星")
    doctor,_=_find_star(chart,"天心星")
    yi=_find_heaven_stem(chart,"乙")
    hour=_find_heaven_stem(chart,chart["hour_ganzhi"][0])
    if not yi or not hour:raise ValueError("Missing actual source star/stem palace")
    pairings=actual_81_pair_context(chart,patient,ill,doctor,yi,hour)
    patient_pairs=_pairs_for(pairings,"患者宫")
    illness_pairs=_pairs_for(pairings,"病宫")
    main_pair_next=next((p for p in illness_pairs if p["star"]=="天芮星"),None)
    if main_pair_next is None:raise ValueError("Tianrui's specific heavenly stem must be attributed")
    doctor_controls=element_relation(ELEMENTS[doctor["palace"]],ELEMENTS[ill["palace"]])=="克"
    yi_controls=element_relation(ELEMENTS[yi["palace"]],ELEMENTS[ill["palace"]])=="克"
    original_adverse=base["audit"]["actual_tomb_punishment_v28"]
    patient_hazards=[f["kind"] for f in original_adverse if f["role"]=="patient"]
    priority=two_sided_evidence(patient=patient,ill=ill,
        patient_void=_yes_void(chart,patient),patient_hazards=patient_hazards,
        patient_pairs=patient_pairs,month_phase=None,
        doctor_controls=doctor_controls,yi_controls=yi_controls)
    previous=base["audit"]["v35_patient_first_decision"]["verdict"]
    verdict=priority["decision_override"] or previous
    med=base["audit"]["v34_treatment_co_palace"]
    same=len(med["independent_opportunities"])
    template=json.loads(TEMPLATE.read_text("utf8"))
    expected_ids=[x["id"] for x in template["sections"]]
    if len(expected_ids)!=11 or len(set(expected_ids))!=11:raise ValueError("V3.7 needs 11 distinct slots")
    old={x["id"]:x for x in base["sections"]}
    extensions={
        "illness_details":"；".join(_describe(p) for p in illness_pairs),
        "patient_details":("患者宫"+PALETTES[patient["palace"]]+str(patient["palace"])+"，"+
             ("；".join(_describe(p) for p in patient_pairs))+
             "；患者宫对病宫为"+priority["patient_vs_illness"]+
             "；"+priority["illness_star_relation_prose"]),
        "doctor_details":("；".join(_describe(p) for p in pairings
             if "天心宫" in p["roles"] or "乙奇宫" in p["roles"])+
            ("；已见时干/病宫与医药同宫，保留及时医治机会；是否有力另看医药宫"
              if same else "；无已核时干/病宫与医药同宫，不等于没有治疗方法")),
        "hour_details":"；".join(_describe(p) for p in _pairs_for(pairings,"时干宫")),
        "chief_details":"；".join(_describe(p) for p in pairings
            if "值符宫" in p["roles"] or "值使宫" in p["roles"]),
    }
    if priority["double_control"]:
        typename="、".join(priority["double_favorable_types"])
    elif priority["double_adverse_types"]:
        typename="、".join(priority["double_adverse_types"])
    else:
        typename="未构成完整双重制病或双重不利链"
    positives=[_describe(p) for p in illness_pairs if p["applicability"]=="book_health_favorable"]
    counters="；".join(positives[:2]) or "病宫吉门、病星耗泄、医药或时干其他实际证据仍独立保留"
    summary=("依据古籍，传统病势主判："+verdict+"。"+
             "真实用神：日干或关系对应的患者宫落"+_palace(patient)+"，病宫落"+_palace(ill)+"。"+
             "双向证据："+typename+"。"+
             "病星五行："+priority["illness_star_relation_prose"]+"。"+
             "主次："+priority["priority"]+"。"+
             "反证："+counters+"。"+
             ("时干或病宫与医药同宫的及时救治机会独立成立，即使医药象偏弱也不能取消；"
               if same else "天心/乙奇是否制病须另核，不因不同宫断无医可治；")+
             "这只是古籍符号研究，不是实际疾病诊断、治疗有效性或生命风险结论。")
    extensions["final_text"]=summary
    sections=[]
    for orig in base["sections"]:
        segment=next(x for x in template["sections"] if x["id"]==orig["id"])
        fmt=segment["format"]
        fields={"old":orig["text"],**extensions}
        new=fmt.format_map(fields)
        if "{" in new or "}" in new or "。。" in new:
            raise ValueError("Unexpanded fixed V3.7 slot or malformed paragraph")
        sections.append({**orig,"text":new})
    aud={**base["audit"],
      "v37_81_ordered_full_book_pairs":pairings,
      "v37_source_book_pair_count":81,"v37_source_book_matched_actual_nine_stars":len(pairings),
      "v37_42_supplement_pairs_also_preserved":True,
      "v37_17_composites_preserved":True,
      "v37_2_sided_double_evidence":priority,
      "v37_actual_health_priority_verdict":verdict,
      "v37_previous_v36_verdict":previous,
      "v37_not_all_book_conditions_universally_approved":True,
      "runtime_gpt_calls":0,"runtime_network_calls":0,
      "user_approval_status":"pending",
      "medical_validation":False}
    return {**base,"schema":"wengua_health_v37_real_81_ordered_pairs_double_adverse_and_double_control",
      "sections":sections,
      "reading_text":"\n\n".join(x["title"]+"："+x["text"] for x in sections),
      "audit":aud,"user_accepted":False}
