"""V3.8 disease fixed-template revision: source tomb, 绝地, Xun-kong included.

V3.7 original predictions and full 194-source SQLite are immutable. Source
line numbers, SHA and method-state remain INTERNAL audit only; user receives
natural Chinese. Only genuine astrological-symbolic chart facts are output,
never medical diagnosis, cancer, dying or actual medication advice.
"""
from __future__ import annotations
import json,re
from pathlib import Path
from .health_severity_v37 import analyze_health_severity_v37
from .health_severity_v22 import _find_star,_yes_void,_palace
from .health_dynamic_v21 import bind_patient
from .symbol_relations import stem_stage
from .marriage_runtime import PALACE_BRANCHES,hourly_void_branches,ELEMENTS,element_relation

ROOT=Path(__file__).resolve().parents[2]
TEMPLATE=ROOT/"data/knowledge/phrase_library/health_v38/severity_customer_template.json"
FORBIDDEN=(r"原书第[0-9０-９]+行",r"(?i)sha(?:256)?",r"(?i)sqlite",
           r"(?i)GPT",r"(?i)数据库",r"(?i)回归测试",r"(?i)规则库",
           r"(?i)代码",r"(?i)模型版本")
PROVENANCE=re.compile(r"[（(]\s*(?:原书|书中|来源|见)?第\s*[0-9０-９]+\s*行\s*[)）]")
INLINE_LINE=re.compile(r"原书第\s*[0-9０-９]+\s*行")

def _customer_clean(phrase):
    # Sources must remain in the immutable JSON audit fields, never in prose.
    text=PROVENANCE.sub("",phrase)
    text=INLINE_LINE.sub("",text)
    text=text.replace("。。","。").replace("；。","。").strip()
    if any(re.search(p,text) for p in FORBIDDEN):
        raise ValueError("Internal-only source metadata leaked into customer reading")
    if not text:
        raise ValueError("Customer sentence unexpectedly empty")
    return text

def illness_stem_tomb_extinction_void(chart,ill,carrier):
    """Separate actual heaven Tianrui-carried stem's 墓,绝 & hour-Xun void.

    A palace having 2 associated branches can host both 墓/绝 branches.
    This is NOT two separate observed time events, a diagnosis, or a
    proof of mortality; it is two symbolic conditions for one stem/palace.
    """
    carried=carrier["carried_stem"]
    palace=ill["palace"]
    branches=tuple(PALACE_BRANCHES[palace])
    tomb_src=stem_stage(carried,"墓")
    extinct_src=stem_stage(carried,"绝")
    tomb_branch=tomb_src["branch"]
    extinction_branch=extinct_src["branch"]
    tomb=tomb_branch in branches
    extinction=extinction_branch in branches
    h=hourly_void_branches(chart["hour_ganzhi"])
    void_branches=tuple(h["xun_kong_branches"])
    void_in_palace=[b for b in branches if b in void_branches]
    void=bool(void_in_palace)
    if not carried or palace==5:
        raise ValueError("Heavenly illness-carried stem must have an actual exterior palace")
    if tomb and tomb_branch in void_branches:
        tomb_is_void=True
    else:tomb_is_void=False
    # This deliberately differs from _yes_void(patient): these are
    # illness-palace conditions and must not be assigned to patient.
    return {
       "illness_tianrui_star":"天芮星",
       "actual_heaven_carried_stem":carried,
       "illness_palace":palace,
       "illness_palace_branches":branches,
       "stage_tomb_branch":tomb_branch,"tomb_branch_in_illness_palace":tomb,
       "stage_extinct_branch":extinction_branch,
       "extinct_branch_in_illness_palace":extinction,
       "hour_ganzhi":chart["hour_ganzhi"],
       "hour_xun_head":h["xun_head"],"void_branches":void_branches,
       "void_in_illness_palace":void,"void_palace_branches":void_in_palace,
       "tomb_branch_also_void":tomb_is_void,
       "compound_tomb_extinct_void_same_palace":bool(tomb and extinction and void),
       "separate_stages_not_separate_deaths":True,
       "source_stem_tomb":tomb_src,
       "source_stem_extinct":extinct_src,
       "interpretation_not_a_medical_prediction":True
    }

def _tomb_lifecycle_sentence(facts,month_branch):
    p=_palace({"palace":facts["illness_palace"]})
    carried=facts["actual_heaven_carried_stem"]
    fragments=[]
    if facts["tomb_branch_in_illness_palace"]:
        fragments.append(carried+"火" if carried=="丙" else "天盘"+carried)
        fragments[-1]+="在"+facts["stage_tomb_branch"]+"为墓，随病星同临"+p+"，呈入墓受困之象"
    if facts["extinct_branch_in_illness_palace"]:
        fragments.append(carried+"在"+facts["stage_extinct_branch"]+"为绝，"+p+"也涵此支，见绝地气弱之象")
    if facts["void_in_illness_palace"]:
        a="、".join(facts["void_branches"])
        fragments.append(facts["hour_ganzhi"]+"时属"+facts["hour_xun_head"]+"旬，"+a+
            "空，病星宫"+p+"逢旬空")
    if not fragments:
        return ("天芮星所携天盘"+carried+"在"+p+
                "未同时出现相应入墓、绝地与宫位旬空，仍须合看其它旺衰。")
    caveat=("墓、绝与旬空是同宫的不同层次，不可机械相加为绝症或生命危险；"
            "病星本体旺衰、患者受克与医药扶助仍要分别权衡")
    if facts["compound_tomb_extinct_void_same_palace"]:
        caveat=("丙奇吉象同时受墓、绝、空的多重限制，不能见丙辛吉格就断顺利；"
                "但旬空亦有病象虚转的可能，需辨新病久病，不凭空断具体吉凶、应期"
                if carried=="丙" else
                "墓、绝、空三种不同象同时存在，仍须按各自角色与新旧病判断")
    return "；".join(fragments)+"。"+caveat+"。"

def _source_book_name(p):
    labels=p["title"]
    alt=p.get("alternate_user_health_name") or []
    if alt and alt[0]!=labels:labels+="（又称"+alt[0]+"）"
    return p["top"]+"加"+p["bottom"]+"「"+labels+"」"

def _evidence_comparison(audit,ill,patient,facts):
    p=audit["v37_2_sided_double_evidence"]
    disease=audit["v37_actual_health_priority_verdict"]
    pairs=audit["v37_81_ordered_full_book_pairs"]
    main_patient=[q for q in pairs if "患者宫" in q["roles"]]
    main_ill=[q for q in pairs if "病宫" in q["roles"]]
    illness_good=[q for q in main_ill if q["applicability"] in ("book_health_favorable","book_favorable_formation")]
    patient_bad=[q for q in main_patient if q["applicability"] in ("book_adverse_formation","book_health_adverse")]
    sign=element_relation(ELEMENTS[patient["palace"]],ELEMENTS[ill["palace"]])
    if sign=="受克":
        main="病宫"+ELEMENTS[ill["palace"]]+"克患者宫"+ELEMENTS[patient["palace"]]+"，患者用神承受病宫之克"
    elif sign=="克":main="患者宫克病宫，具有制病的有利方向"
    elif sign=="生":main="患者宫生病宫，患者反而助长病象"
    elif sign=="受生":main="病宫生患者宫，患者得生扶"
    else:main="患者与病宫比和，需看各自旺弱"
    clauses=[main]
    if patient_bad:
        clauses.append("患者宫又有"+ "、".join(_source_book_name(q) for q in patient_bad)+"等不利格局")
    if p["double_control"]:
        clauses.append("患者宫制病与病宫制天芮同时成立，形成双重制病")
    if p["double_adverse_types"]:
        clauses.append("相互加强的不利象为"+"/".join(p["double_adverse_types"]))
    counters=[]
    if p["illness_palace_vs_tianrui_earth"]=="受生":
        counters.append("天芮土生落宫"+ELEMENTS[ill["palace"]]+"，病星有泄气之象")
    if illness_good:
        counters.append("病宫"+ "、".join(_source_book_name(q) for q in illness_good)+"含吉格")
    if facts["void_in_illness_palace"]:
        counters.append("病宫旬空，病势有虚实转化之象，不等于患者宫一定得益")
    if facts["tomb_branch_in_illness_palace"] or facts["extinct_branch_in_illness_palace"]:
        counters.append("病宫所携天盘"+facts["actual_heaven_carried_stem"]+"入墓、绝地，格局吉象发挥受限")
    if not counters:counters.append("病星旺衰与医药力量仍须另看")
    return disease,"；".join(clauses),"；".join(counters)

def analyze_health_severity_v38(*,chart,inquiry,calendar=None,db_path=None):
    if inquiry.get("intent")!="severity":
        raise ValueError("Only traditional severity intent is eligible for this template")
    if not calendar or not calendar.get("month_branch"):
        raise ValueError("Actual source calendar month branch required")
    base=analyze_health_severity_v37(chart=chart,inquiry=inquiry,calendar=calendar,db_path=db_path)
    illness,carrier=_find_star(chart,"天芮星")
    patient=bind_patient(chart,inquiry,calendar)["main_cell"]
    if patient is None:raise ValueError("Cannot invent the person's actual palace")
    facts=illness_stem_tomb_extinction_void(chart,illness,carrier)
    month=calendar["month_branch"]
    lifetext=_tomb_lifecycle_sentence(facts,month)
    verdict,main,counter=_evidence_comparison(base["audit"],illness,patient,facts)
    med=base["audit"]["v34_treatment_co_palace"]
    doc,_=_find_star(chart,"天心星")
    yi=next(c for c in chart["palaces"].values()
            if any(x["carried_stem"]=="乙" for x in c["heaven_stars"]))
    medicine_detail=(
      "天心落"+_palace(doc)+"，乙奇落"+_palace(yi)+"；"+
      ("病宫或时干与医药同宫，传统有及时得到医治的机会，"
       "即使医药宫虚弱也不取消同宫之象；"
       if med["independent_opportunities"] else
       "此盘未见病宫、时干与医药直接同宫，但不能据此断没有医治机会；")
    )
    if element_relation(ELEMENTS[yi["palace"]],ELEMENTS[illness["palace"]])=="受克":
        medicine_detail+="病宫克乙奇宫，药象受制，需要与吉格相互参看。"
    else:medicine_detail+="疗效不能只凭相生相克一条决定。"
    phrase_verdict=("偏凶，病宫克患者、患者宫不利格局形成双重凶证"
         if base["audit"]["v37_2_sided_double_evidence"]["double_adverse_patient_formation"]
         else "偏吉，双重制病是重要的有利证据"
         if base["audit"]["v37_2_sided_double_evidence"]["double_control"]
         else ("偏凶" if verdict=="病凶" else "偏吉")+",综合证据仍需兼看")
    outcome=("按此盘传统取象，"+phrase_verdict+"。"+
      "主证："+main+"。"+
      "病星与格局的反证："+counter+"。"+
      "特别注意："+lifetext+
      "医药方面，"+medicine_detail+
      "断的是古籍象意，并不代表真实疾病的诊断、发展或治疗结果。")
    template=json.loads(TEMPLATE.read_text("utf8"))
    formats={z["id"]:z["format"] for z in template["sections"]}
    if len(formats)!=11 or "03_illness" not in formats or "11_final" not in formats:
        raise ValueError("Missing V3.8 source intact static eleven-slot customer template")
    changed=[]
    for section in base["sections"]:
        key=section["id"]
        clean=_customer_clean(section["text"])
        if key=="03_illness":
            fields={"clean_original":clean,
                "actual_stem_tomb_extinction_void":lifetext}
        elif key=="09_hazards":
            fields={"clean_original":clean,
                "combination_and_limitations":(
                    "本盘病宫"+_palace(illness)+"，"+lifetext+
                    "入墓、绝地与旬空需要结合病宫所属干及新旧病，不能用单独一个象下结论")}
        elif key=="11_final":fields={"revised_final":outcome}
        else:fields={"clean_original":clean}
        updated=_customer_clean(formats[key].format_map(fields))
        changed.append({**section,"text":updated})
    if len(changed)!=len(base["sections"]):
        raise ValueError("All original sections must be preserved")
    reading="\n\n".join(s["title"]+"："+s["text"] for s in changed)
    _customer_clean(reading)
    return {**base,
        "schema":"wengua_health_v38_user_ready_source_provenance_hidden_tomb_extinct_void",
        "sections":changed,"reading_text":reading,
        "audit":{**base["audit"],
            "v38_actual_illness_derived_tomb_extinct_void":facts,
            "v38_actual_illness_user_phrase":lifetext,
            "v38_source_provenance_internal_only":True,
            "v38_illness_and_patient_void_not_merged":True,
            "v38_ancient_patient_risk_not_clinical_assessment":True,
            "v38_previous_v37_exact_readouts_unchanged":True,
            "v38_known_source_conditions_coverage_not_falsely_inflated":True,
            "v38_final_user_acceptance":"pending",
            "runtime_gpt_calls":0,
            "runtime_network_calls":0},
        "user_accepted":False}
