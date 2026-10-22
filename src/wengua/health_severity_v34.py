"""V3.4: source-conditioned complete role and disease evidence, offline only.

Old V3.1/3.3 sealed results remain byte-identical and immutable.
This version consumes every catalog row with explicit true/false/unknown
condition state. Unknown predicate is NOT silently taken as true/false.
Traditional medicine and severity symbolism is not clinical prediction.
"""
from __future__ import annotations
import json
from pathlib import Path
from .health_severity_v31 import analyze_health_severity_v31
from .health_severity_v22 import _find_star, _find_heaven_stem, _yes_void, FORBIDDEN_CUSTOMER
from .health_dynamic_v21 import bind_patient
from .health_severity_v25 import fuyin_fanyin_facts
from .marriage_runtime import ELEMENTS,element_relation,PALACE_BRANCHES
from .symbol_relations import stem_stage
from .health_severity_v26 import _direction

ROOT=Path(__file__).resolve().parents[2]
CATALOG=ROOT/"data/knowledge/phrase_library/health_v30/user_20261022_pair_catalog.json"
SLOTS=ROOT/"data/knowledge/phrase_library/health_v33/severity_fixed_template.json"
DOORS_FAVORABLE=("开门","休门","生门")
DEATH_WORDS=("必死","死亡","癌症","确诊","停药","放弃治疗")
HORSE={"申":"寅","子":"寅","辰":"寅",
       "寅":"申","午":"申","戌":"申",
       "巳":"亥","酉":"亥","丑":"亥",
       "亥":"巳","卯":"巳","未":"巳"}

def _cell_stems(cell):
    return tuple(s["carried_stem"] for s in cell.get("heaven_stars",()))

def _palace_label(cell):
    p=cell["palace"]
    return {1:"坎",2:"坤",3:"震",4:"巽",6:"乾",7:"兑",8:"艮",9:"离"}[p]+str(p)+"宫"

def _pair_catalog(chart,ill,person,duration):
    catalog=json.loads(CATALOG.read_text("utf8"))
    observations=[]
    # Pair catalog order is directional: heaven OVER earth, not an unordered set.
    for p in catalog["pairs"]:
        appearances=[]
        for role,cell in (("病宫",ill),("患者宫",person)):
            top=_cell_stems(cell)
            if p["heaven"] in top and cell["earth_stem"]==p["earth"]:
                appearances.append({"role":role,"palace":cell["palace"],
                    "literal":p["heaven"]+"加"+p["earth"]})
        if not appearances:
            state="not_triggered";detail=""
        elif p["mode"]=="needs_source":
            state="unknown_exact_condition"
            detail="双干已匹配；古籍对应完整复合条件未核定"
        elif p["mode"]=="duration" and duration not in ("new","chronic"):
            state="unknown_missing_duration"
            detail="真实配对已匹配但未给新病或久病"
        elif p["mode"]=="conditional" and not any(
            chart["palaces"][str(a["palace"])]["door"]=="死门" and
            chart["palaces"][str(a["palace"])]["deity"]=="太阴" for a in appearances
        ):
            state="not_triggered_full_conditional";detail="缺同宫死门和太阴"
        else:
            state="triggered";detail=p["meaning"]
            if p["mode"]=="duration":
                detail=("新病古籍有转缓候选" if duration=="new" else "久病古籍有不利候选")
            if p["mode"]=="conflict":
                detail="原诀与实践判断冲突，必须两轨保留、不能一格单定吉凶"
            if p["mode"]=="role_dependent":
                detail="病宫与患者宫方向相反，按实际角色分别判断"
        observations.append({"id":p["id"],"name":p["name"],
                             "pattern":[p["heaven"],p["earth"]],
                             "state":state,"matched":appearances,"meaning":detail,
                             "provenance":"user_supplied_2026_10_22"})
    if len(observations)!=42:raise ValueError("Original 42 pair records incomplete")
    return observations

def _composite_catalog(chart,ill,person,event,inquiry,calendar,base):
    specs=json.loads(CATALOG.read_text("utf8"))["composites"]
    roles={"病宫":ill,"患者宫":person}
    computed=[]
    duration=inquiry.get("illness_duration")
    fy=fuyin_fanyin_facts(chart)
    matches=lambda c,stem:stem in _cell_stems(c)
    for x in specs:
        i=int(x["id"][-2:])
        evidence=[]
        status="not_triggered"
        reason=""
        if i in (1,2,3,4,5):
            for role,c in roles.items():
                if i==1: hit=c["door"] in DOORS_FAVORABLE and matches(c,"乙") and c["earth_stem"]=="己"
                elif i==2:hit=c["door"] in ("杜门","开门") and matches(c,"丁") and c["deity"]=="九地"
                elif i==3:hit=c["door"]=="休门" and matches(c,"丁") and c["deity"]=="太阴"
                elif i==4:hit=c["door"]=="死门" and c["deity"]=="九地" and any(matches(c,s) for s in ("丁","己","癸"))
                else:hit=c["door"]=="惊门" and matches(c,"壬") and c["deity"]=="九天"
                if hit:evidence.append({"role":role,"palace":c["palace"]})
            status="triggered" if evidence else "not_triggered"
        elif i in (6,7,8,10,11):
            # Catalog gives a name rather than a machine-complete predicate:
            # never equate an arbitrary gate/symbol with verified 三诈/得使/守门.
            status="unknown_definition"
            reason="书源未给出这一组全部可判定的机械条件，不得强套单一星门"
        elif i==9:
            birth=inquiry.get("patient_birth_ganzhi") or inquiry.get("subject_year_ganzhi")
            yr=calendar.get("year_ganzhi")
            if not birth or not yr:
                status="unknown_missing_birth_year"
            else:
                from .core import BRANCHES
                # 太岁前后二辰，出生支与两候选逐一比对；不作死生之断。
                tai=BRANCHES.index(yr[1])
                peers=(BRANCHES[(tai+2)%12],BRANCHES[(tai-2)%12])
                status="triggered" if birth[1] in peers else "not_triggered"
                evidence=[{"birth_branch":birth[1],"year_branch":yr[1],"candidate_branches":peers}]
        elif i==12:
            b=calendar.get("day_ganzhi","")
            if len(b)!=2:status="unknown_missing_day_branch"
            else:
                horse=HORSE[b[1]]
                related=[role for role,c in roles.items() if horse in PALACE_BRANCHES[c["palace"]]]
                evidence=[{"day_branch":b[1],"horse_branch":horse,"roles":related}]
                # Presence of a horse branch is not the same as actual
                # opposing/filling calendar activation and an expected date.
                status="triggered" if related else "not_triggered"
        elif i==13:
            age=inquiry.get("patient_age_band")
            primary=inquiry.get("patient_birth_ganzhi") or inquiry.get("subject_year_ganzhi")
            if age not in ("young","middle","old") or not primary:
                status="unknown_missing_age_or_birth"
            else:
                danger=("绝",) if age=="young" else ("帝旺",) if age=="old" else ("死","绝","墓")
                values=[{"stage":v,"branch":stem_stage(primary[0],v)["branch"]} for v in danger]
                evidence=[{"age_band":age,"stages":values}]
                status="triggered" if any(e["branch"] in PALACE_BRANCHES[person["palace"]] for e in values) else "not_triggered"
        elif i==14:
            if duration not in ("new","chronic"):status="unknown_missing_duration"
            else:
                hit=_yes_void(chart,person)
                evidence=[{"duration":duration,"person_void":bool(hit)}]
                status="triggered" if hit else "not_triggered"
        elif i==15:
            evidence=[{"star":fy["star"],"door":fy["door"]}]
            status="triggered" if ("反吟" in (fy["star"],fy["door"]) or "伏吟" in (fy["star"],fy["door"])) else "not_triggered"
        elif i==16:
            patterns=(("癸","辛"),("癸","癸"),("癸","庚"))
            for role,c in roles.items():
                for h,e in patterns:
                    if h in _cell_stems(c) and c["earth_stem"]==e:
                        evidence.append({"role":role,"palace":c["palace"],"heaven":h,"earth":e})
            status="triggered" if evidence else "not_triggered"
        elif i==17:
            relation=element_relation(ELEMENTS[person["palace"]],ELEMENTS[event["palace"]])
            evidence=[{"patient_palace":person["palace"],"event_palace":event["palace"],
                       "patient_vs_hour_relation":relation}]
            status="triggered"
        else:raise ValueError("Unsupported indexed composite")
        computed.append({"id":x["id"],"name":x["name"],"state":status,
            "evidence":evidence,"reason":reason,"source":"user_supplied_2026_10_22"})
    if len(computed)!=17:raise ValueError("All 17 composite audits required")
    return computed

def _append(text,extension):
    if not extension:return text
    return text.rstrip("。")+"；"+extension.rstrip("。")+"。"

def analyze_health_severity_v34(*,chart,inquiry,calendar=None,db_path=None):
    if inquiry.get("intent")!="severity":raise ValueError("Only health severity currently authorized")
    if calendar is None:raise ValueError("Actual source four pillars required")
    base=analyze_health_severity_v31(chart=chart,inquiry=inquiry,calendar=calendar,db_path=db_path)
    bind=bind_patient(chart,inquiry,calendar)
    person=bind["main_cell"]
    if person is None:raise ValueError("No factual patient palace; do not force a chart")
    ill,_=_find_star(chart,"天芮星")
    doc,_=_find_star(chart,"天心星")
    yi=_find_heaven_stem(chart,"乙")
    event=_find_heaven_stem(chart,chart["hour_ganzhi"][0])
    if not (yi and event):raise ValueError("Cannot locate actual medicine/hour event")
    direct=element_relation(ELEMENTS[person["palace"]],ELEMENTS[ill["palace"]])
    star=element_relation(ELEMENTS[ill["palace"]],"土")
    # Both are distinct relations: patient -> illness palace -> Tianrui earth.
    double_control=(direct=="克" and star=="克")
    patient_control=(direct=="克")
    # Two immediate attention triggers, always positive as an opportunity
    # EVEN IF doctor/medicine month strength is weak or palace obstructed.
    same=[]
    for pivot,cell in (("时干",event),("病宫",ill)):
        for practitioner,mc in (("天心",doc),("乙奇",yi)):
            if cell["palace"]==mc["palace"]:
                same.append({"source":pivot,"symbol":practitioner,"palace":cell["palace"]})
    med_base=base["audit"]["medical_timing_v28"]
    if sorted((a["source"],a["symbol"],a["palace"]) for a in same)!=sorted(
        (a["trigger"],a["medicine_symbol"],a["palace"]) for a in med_base["matches"]):
        raise ValueError("Real hour/medicine same-palace audit conflicts with V3.1")
    weak_med=[x for x in med_base["limits"] if x]
    duration=inquiry.get("illness_duration")
    pairs=_pair_catalog(chart,ill,person,duration)
    composites=_composite_catalog(chart,ill,person,event,inquiry,calendar,base)
    full_template=json.loads(SLOTS.read_text("utf8"))
    if len(full_template["sections"])!=11:raise ValueError("Static eleven-slot template missing")
    extra={}
    if double_control:
        extra["05_patient"]="患者宫"+ELEMENTS[person["palace"]]+"克病宫"+ELEMENTS[ill["palace"]]+"，而病宫"+ELEMENTS[ill["palace"]]+"又克天芮土，构成双重制病象，病星受制更重，作为重要有利反证"
    elif patient_control:
        extra["05_patient"]="患者宫克病宫，属于患者制病；但病星本体是否同时受克须另看病宫对天芮土的关系"
    else:
        extra["05_patient"]="患者用神、病宫对天芮土分别取关系；不把日干与病宫五行混为病星本体"
    if same:
        labels="、".join(x["source"]+"与"+x["symbol"]+"同"+_palace_label(chart["palaces"][str(x["palace"])]) for x in same)
        sentence=labels+"，传统有及时获得医治之机会"
        if weak_med:sentence+="；即使医药象有"+("、".join(weak_med[:2]))+"，同宫机会仍独立成立，医治作用和疗效另议"
        extra["07_medicine"]=sentence
    p_name=bind["role_name"]
    if bind.get("harmony_stem"):
        h=bind["harmony_stem"]
        q=bind.get("harmony_palace")
        extra["01_role"]="按妻乙夫庚与日干五合分别取用；五合"+h+("另在"+_palace_label(chart["palaces"][str(q)])+"参证" if q else "无可见天盘宫，不凭空借位")
    if inquiry["relationship"].startswith("animal") or inquiry["relationship"]=="animal":
        extra["01_role"]="动物无明确其它用神，以实际时干所落宫作动物用神，不取问者日干"
    if inquiry["relationship"]=="son_in_law":
        extra["01_role"]="岳父代问女婿，按本书案例时干作女婿用神"
    vstar=chart["palaces"][str(chart["value_star_palace"])]
    vdoor=chart["palaces"][str(chart["value_door_palace"])]
    role_link=[]
    for label,c in (("值符",vstar),("值使",vdoor)):
        if c["palace"]==person["palace"]:role_link.append(label+"与患者用神同宫")
        elif c["palace"]==ill["palace"]:role_link.append(label+"与病宫同宫")
    if role_link:
        extra["02_far"]="；".join(role_link)+"，牵领此事的重要纲领；仍须按患者宫与病星实际证据综合判断"
    visible_pairs=[x for x in pairs if x["state"]=="triggered"]
    if visible_pairs:
        # Avoid injecting diagnostic or mortality absolutes from ancient notes.
        names="、".join(x["name"]+"（"+"/".join(a["role"] for a in x["matched"])+"）" for x in visible_pairs)
        extra["09_hazards"]="本盘实际有序天地干命中："+names+"；须结合人物宫、病宫及新旧病区别解释"
    obvious=[x for x in composites if x["state"]=="triggered"]
    if obvious:
        extra["10_pace"]="已满足可实算复合条件："+("、".join(x["name"] for x in obvious))+"；需按不同条件确定性质与传统应期，不能自行推出具体日期"
    old_verdict=base["audit"]["traditional_verdict"]["verdict"]
    # Patient controls illness AND illness star controlled merits a stronger
    # independent favorable evidence, but must not erase contrary evidence.
    # The final traditional verdict remains conservative until a separately
    # approved precedence reweighting validation; never tune to known ending.
    final=("患者制病"+"且病星又受落宫制，双重制病为重要有利证据"
           if double_control else "患者制病为有利证据" if patient_control
           else "患者宫与病星并非双重制病，需合看用神旺衰")
    if same:final+="；时干或病宫与医药同宫有及时医治机会，医药力量弱不取消同宫之象"
    extra["11_final"]=final+"；原传统主判"+old_verdict+"，有利与不利证据并列保存，不按单一格局断生死"
    sections=[]
    for x in base["sections"]:
        y=x["text"]
        if x["id"]=="11_final" and base["audit"]["real_patient_sex"]:
            gender="乾六宫" if base["audit"]["real_patient_sex"]=="male" else "坤二宫"
            y=y.replace("乾坤辅助宫",gender+"辅助宫")
        new=_append(y,extra.get(x["id"],""))
        if any(z in new for z in FORBIDDEN_CUSTOMER) or "{" in new or "}" in new or "。。" in new:
            raise ValueError("Invalid literal source-backed V3.4 customer phrase")
        # Ancient severe diagnostic or fatal labels never become claims.
        if any(w in new for w in DEATH_WORDS):
            raise ValueError("Unsafe medical diagnostic/mortality claims in customer text")
        sections.append({**x,"text":new})
    audit={**base["audit"],"v34_patient_binding":{k:v for k,v in bind.items() if k not in ("main_cell","birth_cell","extra_cells")},
       "v34_double_control":{"patient_controls_illness_palace":patient_control,
         "illness_palace_controls_tianrui_earth":star=="克",
         "both":double_control,"patient_vs_illness":direct,"illness_palace_vs_star":star},
       "v34_treatment_co_palace":{"independent_opportunities":same,"weaknesses_kept":weak_med,
                                "no_strength_veto_on_co_palace":True},
       "v34_42_directional_pairs":pairs,"v34_17_composite_conditions":composites,
       "v34_false_and_unknown_predicates_are_not_asserted":True,
       "v34_retains_old_v31_verdict_for_neutral_comparison":old_verdict,
       "historical_author_feedback_loaded":False,
       "runtime_gpt_calls":0,"runtime_network_calls":0,
       "user_acceptance":"pending"}
    return {**base,"schema":"wengua_health_severity_v34_role_priority_co_palace_and_42_17_conditions",
       "sections":sections,"reading_text":"\n\n".join(z["title"]+"："+z["text"] for z in sections),
       "audit":audit,"user_accepted":False}
