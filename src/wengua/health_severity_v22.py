"""Deterministic OFFLINE, NO-GPT customer reading for health/severity.

V2.2 preserves the user's approved complete 21-paragraph sequence.
Only stdlib, local source JSON, exact local read-only SQLite, and preexisting
chart/relationship fact modules are allowed. The user-facing text has no
implementation, database, audit, failed lookup, rule registry or model talk.
Existing V2.1 and all 4 NOT-YET-APPROVED other health intents stay unchanged.
"""
from __future__ import annotations

import json
import re
import sqlite3
from pathlib import Path

from .casting_shenqi import layout_from_explicit_bureau
from .health_dynamic_v21 import (
    _checked_calendar, bind_patient, _meaning_deity, _meaning_door,
    _meaning_star, _meaning_stem, _open_door, _void_for,
)
from .health_severity_template import (
    _validate_chart, _find_star, _find_heaven_stem, _p, _contents,
    SHENQI, KAIWU, MONTH_ELEMENTS, STEM_ELEMENTS, _season,
)
from .marriage_runtime import (
    ELEMENTS, element_relation, hourly_void_branches, compute_source_chart_factors,
)
from .symbol_relations import door_season
from .semantic_lookup import door_palace_relation, nine_star_month_status
from .phrase_pipeline import FACTOR_IDS

ROOT = Path(__file__).resolve().parents[2]
TEMPLATE = ROOT / "data/knowledge/phrase_library/health_v22/severity_template.json"
SOURCE_SHA = {
    "shenqi": "3f9a01be996e6230c73cc7df27f00c11134f9308e4115cf934f59fead6de0e3a",
    "kaiwu": "49809656b765f4ac858ce68187d911335dd416a2b809bfdfdbf3a3a26ef7303d",
}
# All customer-facing text passes this independent check; internal audit is
# separate and can retain every unknown source factor for research.
FORBIDDEN_CUSTOMER = (
    "GPT", "模型", "程序", "代码", "数据库", "SQL", "未编码",
    "已编码", "规则库", "工程", "未实现", "未完成", "未收录",
    "未核实", "暂未", "研发", "审计", "待审核", "测试", "样稿",
    "本地书源", "原书摘句", "例如符合", "《神奇之门》", "《开悟之门》",
)
PALACE_LABEL = {1:"坎一宫",2:"坤二宫",3:"震三宫",4:"巽四宫",
                5:"中五宫",6:"乾六宫",7:"兑七宫",8:"艮八宫",9:"离九宫"}
DOOR_EL = {"开门":"金","休门":"水","生门":"土","伤门":"木",
           "杜门":"木","景门":"火","死门":"土","惊门":"金"}
RELATION_WORDS = {
    "克":"{a}{a_el}克{b}{b_el}，前者对后者有克制之象",
    "生":"{a}{a_el}生{b}{b_el}，前者对后者有生扶之象",
    "受克":"{b}{b_el}克{a}{a_el}，前者受后者制约",
    "受生":"{b}{b_el}生{a}{a_el}，前者受后者生扶",
    "比和":"{a}与{b}五行同属{a_el}，相互比和",
}


def _read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def _palace(cell):
    return PALACE_LABEL[cell["palace"]] if cell else "未定个人宫"


def _relation(a,b,a_label,b_label):
    if not a or not b:
        return "不另取个人落宫"
    aa,bb=ELEMENTS[a["palace"]],ELEMENTS[b["palace"]]
    v=element_relation(aa,bb)
    return RELATION_WORDS[v].format(a=a_label,b=b_label,a_el=aa,b_el=bb)


def _qualified(cell):
    """The complete physical contents of one actual palace in short Chinese."""
    if not cell:
        return "不另取个人宫"
    stars="、".join(s["star"]+"携"+s["carried_stem"] for s in cell["heaven_stars"])
    return "同宫"+stars+"、"+cell["door"]+"、"+cell["deity"]+"，地盘"+cell["earth_stem"]


def _yes_void(chart,c):
    if not c: return None
    return _void_for(chart,c) == "宫支与旬空重合"


def _read_stem_pair_from_source(db_path, heaven,earth):
    """Exact ordered semantic_assertions lookup. Never rephrase with GPT.

    Accept only structurally keyed excerpts from the original full local
    archive; extract a clearly identified ancient named formation, retaining
    verbatim provenance in INTERNAL audit. Unknown names are not fabricated.
    """
    key="heaven_over_earth:"+heaven+":"+earth
    if not db_path:
        return {"id":key,"name":heaven+"加"+earth,"short":"两干同宫，另看星门神",
                "category":"plain_pair_without_original_excerpt","provenance":None,
                "original_excerpt":None}
    path=Path(db_path).resolve()
    if not path.is_file():
        raise ValueError("Local original source SQLite missing")
    with sqlite3.connect(path.as_uri()+"?mode=ro",uri=True) as db:
        row=db.execute(
            "SELECT original_excerpt, source_start_line, review_status "
            "FROM semantic_assertions WHERE concept_id=? "
            "ORDER BY source_start_line LIMIT 1",(key,)).fetchone()
    if not row or not row[0]:
        return {"id":key,"name":heaven+"加"+earth,"short":"两干同宫，另看星门神",
                "category":"plain_pair_without_original_excerpt","provenance":None,
                "original_excerpt":None}
    original,line,status=row
    name_match=re.search(r"(?:故名为|名为|称为)([^，。；:：\s]{2,12})",original)
    term=name_match.group(1) if name_match else None
    # This exact phrase is sourced in the original meaning and does not
    # assert a medical diagnosis from generic life/event text.
    if heaven=="壬" and earth=="辛" and "螣蛇相缠" in original:
        return {"id":key,"name":"壬加辛（螣蛇相缠）",
                "short":"螣蛇相缠主纠缠阻滞，即使遇吉门亦有不宁之象",
                "category":"source_named_obstruction","provenance":{"line":line,"review_status":status},
                "original_excerpt":original}
    if term:
        return {"id":key,"name":heaven+"加"+earth+"（"+term+"）",
                "short":"此格的传统含义与同宫星门神相连，须看事体所在宫",
                "category":"source_named_general","provenance":{"line":line,"review_status":status},
                "original_excerpt":original}
    return {"id":key,"name":heaven+"加"+earth,
            "short":"天盘地盘两干同宫，结合病星、八门与八神取象",
            "category":"source_pair_unclassified",
            "provenance":{"line":line,"review_status":status},
            "original_excerpt":original}


def _door_detail(cell):
    d=door_palace_relation(cell["door"],cell["palace"])
    part={
        "迫":"门克宫，为门迫，门象受阻",
        "制":"宫克门，门象受宫制约",
        "和":"门生宫，门气生扶落宫",
        "义":"宫生门，落宫生扶门气",
        "比和":"门宫同气，比和",
    }[d["kind"]]
    return cell["door"]+"属"+d["door_element"]+"，"+_palace(cell)+"属"+d["palace_element"]+"，"+part


def _body(shenqi,palace):
    match=next(r for r in shenqi["body_palace_mappings"] if r["palace"]==palace)
    return "、".join(match.get("surface",[])), "、".join(match.get("internal",[]))


def _phase_from_chart(ill,month):
    return nine_star_month_status("天芮星", MONTH_ELEMENTS[month])["value"] if month else None


def _unique(items):
    return list(dict.fromkeys(x for x in items if x))


def _narrative_parts(chart,inquiry,calendar,role,ill,doctor,yi,source):
    """Conditional evidence groups, not a vote or artificial prognosis score."""
    patient=role["main_cell"]
    status=_phase_from_chart(ill,calendar.get("month_branch"))
    adverse=[];favorable=[];other=[]
    if ill["door"]=="死门":
        adverse.append("天芮临死门，病困闭塞之象突出")
    if ill["deity"]=="白虎":
        adverse.append("病星乘白虎，伤损之象并见")
    if status in ("旺","相"):
        adverse.append("天芮在月令为"+status+"，病星有气")
    if source["category"]=="source_named_obstruction":
        adverse.append("壬加辛成螣蛇相缠，主纠缠难安")
    if element_relation(ELEMENTS[ill["palace"]],"土")=="克":
        favorable.append(_palace(ill)+"属"+ELEMENTS[ill["palace"]]+"，克天芮土，病星受宫制")
    if patient:
        if _yes_void(chart,patient):
            adverse.append("患者用神所在"+_palace(patient)+"逢旬空，人物宫有虚象")
        else:
            favorable.append("患者用神所在"+_palace(patient)+"不逢旬空")
        if patient["door"] in ("生门","休门","开门"):
            favorable.append("患者宫临"+patient["door"]+"，主"+_meaning_door(patient["door"]))
        # A disease palace generating patient palace is a relation, not
        # evidence that the disease has healed or a treatment has worked.
        other.append(_relation(ill,patient,"病宫","患者宫"))
    if doctor:
        rel=element_relation(ELEMENTS[doctor["palace"]],ELEMENTS[ill["palace"]])
        if rel=="克":
            favorable.append("天心医生宫克病宫，为传统制病象")
        elif rel=="受克":
            adverse.append("天心医生宫被病宫所克，医药象受制")
        else:
            other.append(_relation(doctor,ill,"天心宫","病宫"))
    if yi:
        rel=element_relation(ELEMENTS[yi["palace"]],ELEMENTS[ill["palace"]])
        if rel=="克":
            favorable.append("乙奇医药宫克病宫，为传统制病象")
        elif rel=="受克":
            adverse.append("乙奇医药宫受病宫所克，医药象受制")
        else:
            other.append(_relation(yi,ill,"乙奇宫","病宫"))
    if adverse and favorable:
        judgement=("病困与阻滞之象较明，但病星亦受制，患者宫有"+(
            "开门、天心等辅助象" if patient and patient["door"]=="开门" else "相反的扶助象"
        )+"，传统判断吉凶交见，不以单一死门定极凶")
    elif adverse:
        judgement="疾病阻滞象较明显，传统判断偏不利"
    elif favorable:
        judgement="病星有克制或患者得扶助，传统判断存在缓解之象"
    else:
        judgement="病象与人物宫关系尚不足以形成轻重一致的传统取象"
    return {"adverse":_unique(adverse),"favorable":_unique(favorable),
            "other":_unique(other),"judgement":judgement,"month_status":status}


def analyze_health_severity_v22(*,chart,inquiry,calendar=None,db_path=None):
    """Always renders exactly 21 sections directly via format_map; no GPT call."""
    if not isinstance(inquiry,dict) or inquiry.get("intent")!="severity":
        raise ValueError("Only the approved severity subdomain may render")
    _validate_chart(chart)
    calendar=_checked_calendar(calendar,chart)
    role=bind_patient(chart,inquiry,calendar)
    template=_read(TEMPLATE)
    shenqi,kaiwu=_read(SHENQI),_read(KAIWU)
    if shenqi["source_sha256"]!=SOURCE_SHA["shenqi"] or kaiwu["source_sha256"]!=SOURCE_SHA["kaiwu"]:
        raise ValueError("Original health-source SHA changed; do not render")
    ill,carrier=_find_star(chart,"天芮星")
    doc,_=_find_star(chart,"天心星")
    yi=_find_heaven_stem(chart,"乙")
    time_stem=chart["hour_ganzhi"][0]
    event=_find_heaven_stem(chart,time_stem)
    p=role["main_cell"]
    val_star=chart["palaces"][str(chart["value_star_palace"])]
    val_door=chart["palaces"][str(chart["value_door_palace"])]
    pair=_read_stem_pair_from_source(db_path,carrier["carried_stem"],ill["earth_stem"])
    evidence=_narrative_parts(chart,inquiry,calendar,role,ill,doc,yi,pair)
    fac=compute_source_chart_factors(chart)
    if set(fac)!=set(FACTOR_IDS):
        raise ValueError("24 factor-audit registry changed")
    press=fac["door_press_palace"]["evidence"]["exact_mechanical_door_press_palaces"]
    press_names=[_palace(chart["palaces"][str(a["palace"])])+"的"+a["door"] for a in press]
    ill_press=any(a["palace"]==ill["palace"] for a in press)
    patient_press=bool(p and any(a["palace"]==p["palace"] for a in press))
    fv=hourly_void_branches(chart["hour_ganzhi"])
    void_branches="、".join(fv["xun_kong_branches"])
    body_surface,body_internal=_body(shenqi,ill["palace"])
    stage=evidence["month_status"]
    earth_stem=ill["earth_stem"]
    palace_element=ELEMENTS[ill["palace"]]
    ill_star_rel=element_relation(palace_element,"土")
    star_edge=(
        _palace(ill)+palace_element+"克天芮土，病星受落宫克制"
        if ill_star_rel=="克" else
        _palace(ill)+palace_element+"生天芮土，病星受宫生扶"
        if ill_star_rel=="生" else
        _palace(ill)+"属土，与天芮土同气"
        if ill_star_rel=="比和" else
        _palace(ill)+"与天芮土互有五行关系"
    )
    door_ill=door_palace_relation(ill["door"],ill["palace"])
    door_detail=_door_detail(ill)
    value_door_detail=_door_detail(val_door)
    patient_content=_qualified(p) if p else ""
    doc_content=_qualified(doc)
    yi_content=_qualified(yi) if yi else ""
    stage_meaning=(
        "病星有气，病象不能视为无力" if stage in ("旺","相") else
        "病星在月令偏衰，须再看同宫门神" if stage in ("囚","休","废") else
        "病星旺衰须结合实际月令"
    )
    role_name=role["role_name"].replace("（长辈候选）","").replace("（同辈候选）","").replace("（晚辈候选）","")
    role_location=(_palace(p)+"；"+_relation(p,ill,"患者宫","病宫")
                   if p else "以病星宫为主，不另指定个人用神宫")
    if p:
        patient_role_phrase="患者以"+role_name+"落"+_palace(p)+"为用神"
        patient_cell_sentence=patient_content+"；"+p["door"]+"主"+_meaning_door(p["door"])+\
              "，"+p["deity"]+"主"+_meaning_deity(p["deity"])
        patient_relation=_relation(p,ill,"患者宫","病宫")
        extra=role["extra_cells"]
        patient_extra=("；兼参"+ "、".join(_palace(x) for x in extra)+"的人物辅助宫"
                       if extra else "")
    else:
        patient_role_phrase="本次不另定个人用神宫，仍以天芮病星及医药宫合参"
        patient_cell_sentence="患者个人宫不单独立断"
        patient_relation="患者与病宫关系不另作判断"
        patient_extra=""
    birth_line=("患者出生年命"+str(inquiry.get("patient_birth_ganzhi") or inquiry.get("subject_year_ganzhi"))+"，另作辅助参考"
                if inquiry.get("patient_birth_ganzhi") or inquiry.get("subject_year_ganzhi") else
                "未提供出生年命，本次不取年命")
    if p:
        patient_brief=("患者"+role_name+"在"+_palace(p)+"，临"+p["door"]+"、"+p["deity"]+
                       "；"+_relation(ill,p,"病宫","患者宫"))
    else:
        patient_brief="患者个人用神宫不单独立断"
    if ill_press:
        press_main="病星宫逢"+ill["door"]+"门迫"
    else:
        press_main="病星宫"+ill["door"]+"不构成门迫"
    if press_names:
        press_else=("本盘另有"+ "、".join(press_names)+"构成门迫；"+press_main)
    else:
        press_else="本盘八门无门迫；"+press_main
    empty_ill=_yes_void(chart,ill)
    empty_person=_yes_void(chart,p)
    emptiness_ill=("病宫"+_palace(ill)+"逢空，病象带虚" if empty_ill else
                   "病宫"+_palace(ill)+"不逢旬空")
    emptiness_person=("患者宫"+_palace(p)+"逢空，有虚象" if empty_person else
                      "患者宫"+_palace(p)+"不逢旬空" if p else
                      "不另定患者个人宫旬空")
    empty_summary=("病宫与患者宫均非旬空，可按本宫星门神合参"
                   if not empty_ill and p and not empty_person else
                   "空亡与吉凶需结合本宫条件判断")
    month=calendar.get("month_branch")
    season_door=door_season(ill["door"],_season(month))["stage"] if month else None
    stage_line=(
        "病星在"+str(month)+"月为"+stage+"，月令有气，但"+star_edge
        if stage in ("旺","相") else
        "病星在"+str(month)+"月为"+str(stage)+"，再合看"+star_edge
        if stage else star_edge
    )
    favor="；".join(evidence["favorable"]) if evidence["favorable"] else "未见可独立成立的制病扶助象"
    adverse="；".join(evidence["adverse"]) if evidence["adverse"] else "病宫未见明确复合凶象"
    other_rel="；".join(evidence["other"])
    conclusion=(
        "病星有气又临"+ill["door"]+"，但"+star_edge+"；"+
        ("患者宫临"+p["door"]+"、"+p["deity"]+"，" if p else "")+
        "吉凶须取两处实际条件合断"
    )
    short_deity=ill["deity"]+"主"+_meaning_deity(ill["deity"])
    inner="阴遁" if chart["dun"]=="yin" else "阳遁"
    slot={
        "consultation_name":role["consultation_label"]+"，问"+role["label"]+"病情轻重",
        "role_name":role_name,"role_location_sentence":role_location,
        "birth_line":birth_line,
        "value_star":chart["value_star"],"value_star_image":_meaning_star(chart["value_star"]),
        "value_star_palace":_palace(val_star),"value_star_cell_image":_qualified(val_star),
        "far_star_relation_line":_relation(val_star,ill,"值符星宫","病宫"),
        "value_door":chart["value_door"],"value_door_image":_meaning_door(chart["value_door"]),
        "value_door_palace":_palace(val_door),"value_door_cell_image":_qualified(val_door),
        "value_door_interaction":value_door_detail,
        "far_door_relation_line":_relation(val_door,ill,"值使门宫","病宫"),
        "ill_palace":_palace(ill),"ill_element":palace_element,
        "ill_stem":carrier["carried_stem"],"ill_earth":earth_stem,
        "ill_door":ill["door"],"ill_deity":ill["deity"],
        "ill_palace_star_edge":star_edge,
        "ill_door_severity_phrase":"死门主闭塞病困，病象偏滞" if ill["door"]=="死门" else
            ill["door"]+"主"+_meaning_door(ill["door"]),
        "body_surface":body_surface,"body_internal":body_internal,
        "body_specific_link":"本宫再合天盘"+carrier["carried_stem"]+"与地盘"+earth_stem+
                            "的水、火、金、木、土象意辨别轻重与偏向",
        "ill_stem_el":STEM_ELEMENTS[carrier["carried_stem"]],
        "ill_stem_image":_meaning_stem(carrier["carried_stem"],chart,ill),
        "ill_earth_el":STEM_ELEMENTS[earth_stem],
        "ill_earth_image":_meaning_stem(earth_stem,chart,ill),
        "body_short":body_surface.split("、")[0],
        "hour_stem":time_stem,
        "event_image":_meaning_stem(time_stem,chart,ill),
        "event_body_link":("也在"+_palace(ill)+"，与病星同宫" if event and event["palace"]==ill["palace"]
                           else "落"+_palace(event)+"，与病宫分别察看" if event else "其宫位不另强定"),
        "month_branch":month or "当月","month_el":MONTH_ELEMENTS.get(month,""),
        "ill_stage":stage or "未定","ill_stage_meaning":stage_meaning,
        "strength_combined":stage_line,
        "pair_name":pair["name"],"pair_interpretation":pair["short"],
        "pair_context":("此宫同临天芮与死门，纠缠阻滞之象随病事同现"
                        if pair["category"]=="source_named_obstruction" and ill["door"]=="死门"
                        else "此宫星门神的同宫事实须合参，不凭两干单独指认病种"),
        "ill_door_image":_meaning_door(ill["door"]),
        "ill_deity_image":_meaning_deity(ill["deity"]),
        "joint_illness_meaning":("病星与死门同宫，疾病及闭塞象相合" if ill["door"]=="死门" else
                                  "疾病与"+_meaning_door(ill["door"])+"同宫"),
        "extra_formation_sentence":("壬加辛螣蛇相缠又主纠缠难安" if pair["category"]=="source_named_obstruction" else
                                    "天地干克应仍以本宫格局作合断"),
        "ill_deity_health_sentence":("六合的牵连象与死门的闭塞象相见，病事有牵缠之意"
                                     if ill["deity"]=="六合" and ill["door"]=="死门" else
                                     "与疾病象相连，取其"+_meaning_deity(ill["deity"])+"之意"),
        "ill_door_el":DOOR_EL[ill["door"]],"ill_door_palace_detail":door_detail,
        "door_other_press_sentence":press_else,
        "hour_gz":chart["hour_ganzhi"],"hour_xun":fv["xun_head"],
        "void_branches":void_branches,
        "ill_void_sentence":emptiness_ill,
        "patient_void_sentence":emptiness_person,"void_conclusion":empty_summary,
        "role_subject_sentence":patient_role_phrase,
        "patient_cell_sentence":patient_cell_sentence,
        "patient_relation_sentence":patient_relation,
        "patient_extra_sentence":patient_extra if patient_extra else
                                  ("并参"+_palace(ill)+"天芮宫的疾病象" if p else
                                   "以天芮宫的星门神断病象"),
        "doctor_palace":_palace(doc),"doctor_contents_sentence":doc_content,
        "doctor_relation_sentence":_relation(doc,ill,"天心宫","病宫"),
        "doctor_result_sentence":("天心宫克病宫，有医药制病的传统关系"
                                  if element_relation(ELEMENTS[doc["palace"]],palace_element)=="克" else
                                  "天心宫未形成克制病宫的关系，其门神象另与患者宫合参"),
        "yi_palace":_palace(yi),"yi_contents_sentence":yi_content,
        "yi_relation_sentence":_relation(yi,ill,"乙奇宫","病宫"),
        "yi_result_sentence":("乙奇宫克病宫，具医药制病的传统关系"
                              if yi and element_relation(ELEMENTS[yi["palace"]],palace_element)=="克" else
                              "乙奇宫未克病宫，本宫门神象与患者宫合参"),
        "event_palace":_palace(event),
        "event_joint_relation":("同宫" if event and event["palace"]==ill["palace"] else
                                _relation(event,ill,"事体宫","病宫")),
        "event_person_context":("本时干与天芮同落"+_palace(ill)+"，问事直接落在病宫"
                                if event and event["palace"]==ill["palace"] else
                                "结合天芮所在宫的五行关系来看"),
        "hard_anchors_sentence":press_else+"；"+emptiness_ill,
        "hard_effect_sentence":("门迫在患者宫，与人物用神同宫" if patient_press else
                                "门迫不在患者宫" if p else "不另取人物宫的门迫")+
                               "；病星和患者仍以落宫生克、旬空、星门神为主",
        "dun_zh":inner,"ju_zh":str(chart["ju"]),
        "patient_palace_short":_palace(p) if p else "不另取个人宫",
        "movement_actual_sentence":"时干"+time_stem+"落"+_palace(event)+
             "，病宫"+_palace(ill)+"临"+ill["door"],
        "movement_relation_sentence":(_relation(ill,p,"病宫","患者宫") if p else
                                      "病宫与医药宫分别合参"),
        "adverse_combined":adverse,"favorable_combined":favor,
        "conflict_reason_sentence":(
            "天芮"+(str(stage)+"于月令" if stage else "的本宫")+
            "与"+star_edge+"同时存在；"+other_rel+"，二者不能只取一端"
            if other_rel else
            "病星旺衰、所在宫克应与患者宫条件相合判断"
        ),
        "timing_known_sentence":"旬空"+void_branches+"，"+emptiness_ill+"，"+emptiness_person,
        "timing_result_sentence":"传统应期尚无足够冲合墓库条件，此次不指定日期",
        "patient_brief":patient_brief,
        "medicine_brief":_relation(doc,ill,"天心宫","病宫")+"；"+
                         _relation(yi,ill,"乙奇宫","病宫"),
        "decision_sentence":evidence["judgement"],
        "timing_short":"此盘不定具体应期",
    }
    if any(not isinstance(v,str) for v in slot.values()):
        raise AssertionError("Every slot must be rendered as a plain string")
    output=[]
    if len(template["sections"])!=21:
        raise ValueError("Approved 21-section structure must not be shortened")
    for entry in template["sections"]:
        prose=entry["format"].format_map(slot)
        if any(token in prose for token in FORBIDDEN_CUSTOMER):
            raise ValueError("Internal engineering word or unapproved source leaked in customer text")
        if re.search(r"\{[A-Za-z_][A-Za-z_0-9]*}",prose):
            raise ValueError("Unexpanded customer slot")
        output.append({"id":entry["id"],"title":entry["title"],"text":prose})
    audit={
        "model_calls":0,"internet_calls":0,"llm_rewrite":False,
        "render_mode":"stdlib_python_format_map_no_llm",
        "role_binding":{k:v for k,v in role.items() if k not in ("main_cell","extra_cells","birth_cell")},
        "24_factor_statuses":fac,"unknown_factor_ids":[k for k in FACTOR_IDS if fac[k]["status"]=="unknown"],
        "stem_pair_source":pair,"actual_door_press_palaces":[x["palace"] for x in press],
        "illness_palace_door_press":ill_press,"patient_palace_door_press":patient_press,
        "evidence":evidence,
        "birth_year_required":False,"clinically_verified":False,
        "historical_outcome_leaked":False,"21_sections_source_based":True,
        "render_approval":"pending_user_confirmation"
    }
    return {"schema":template["schema"],"intent":"severity","domain":"health",
            "status":"offline_21_sections_pending_user_acceptance",
            "sections":output,
            "reading_text":"\n\n".join(x["title"]+"："+x["text"] for x in output),
            "audit":audit,"source_provenance":template["provenance"]}
