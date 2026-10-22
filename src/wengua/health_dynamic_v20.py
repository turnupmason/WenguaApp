"""V2.0 source-based health readings: role routing + full-length intent templates.

Separate which patient, how the question is asked, illness, physician,
medicine, event, and timing before rendering. Historical results are not inputs.
All health readings are traditional literature analysis, NOT medical guidance.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from .casting_shenqi import layout_from_explicit_bureau
from .core import cycle60
from .health_severity_template import (
    render_health_severity, _find_heaven_stem, _find_star,
    _p, _contents, _direction, MONTH_ELEMENTS, STEM_ELEMENTS,
)
from .marriage_runtime import ELEMENTS, element_relation, PALACE_BRANCHES, hourly_void_branches
from .semantic_lookup import GUAS
from .formation_candidates import evaluate_candidates
from .phrase_pipeline import FACTOR_IDS

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data/knowledge/phrase_library/health_v20"
SEVERITY = DATA / "severity_template.json"
OTHER = DATA / "other_intent_templates.json"
PROFILES = DATA / "actor_profiles.json"

STAR_MEANINGS = {
    "天蓬星":"流动、水道、险阻", "天芮星":"疾病、病患",
    "天冲星":"急动、冲发", "天辅星":"辅佐、知识、调理",
    "天禽星":"居中统合", "天心星":"医生、医药、治理",
    "天柱星":"阻隔、口舌、惊恐", "天任星":"稳定、担当、厚重",
    "天英星":"火热、光明、显露",
}
DOOR_MEANINGS = {
    "休门":"休养、休息、调养", "生门":"生机、恢复、发展",
    "伤门":"伤损、伤病、损耗", "杜门":"闭塞、阻碍、隐藏",
    "景门":"光热、外显、影像", "死门":"闭塞、病困、停滞",
    "惊门":"惊恐、惊扰、变动", "开门":"开启、医治通路、手术辅助象",
}
DEITY_MEANINGS = {
    "值符":"主导、核心、有所护持", "螣蛇":"反复、缠绕、虚幻",
    "太阴":"隐蔽、安静、潜藏", "六合":"结合、协调、牵连",
    "白虎":"伤损、疼痛、血光", "玄武":"隐情、反复、暗昧",
    "九地":"沉滞、缓慢、稳定", "九天":"高远、行动、变化",
}
STEM_MEANINGS = {
    "甲":"统领、头部、筋骨", "乙":"肝胆、筋脉、经络",
    "丙":"光热、炎热、火气", "丁":"火热、血液、血脉",
    "戊":"肌肉、胃土、阻滞", "己":"脾胃、消化、郁结",
    "庚":"筋骨、坚硬、阻隔", "辛":"筋骨、细微、损伤",
    "壬":"水道、津液、流动", "癸":"水道、泌尿、津液",
}
FACTOR_LABELS = {
    "six_yi_striking_punishment":"六仪击刑", "branch_opposition":"地支冲",
    "branch_punishment":"地支刑", "branch_harm":"地支害",
    "month_day_break":"月日破", "door_press_palace":"门迫",
    "heaven_stem_tomb":"天干入墓", "stem_storage":"墓库",
    "travel_horse":"驿马", "xun_kong":"旬空",
    "kong_near_far":"远近空亡", "kong_fill":"填实",
    "kong_clash":"冲空", "hidden_stems":"暗干",
    "seasonal_prosperity":"月令旺衰", "palace_five_elements":"宫五行",
    "heaven_earth_stem_structure":"天地盘干", "star_door_deity_structure":"星门神",
    "fuyin_fanyin":"伏吟反吟", "palace_interactions":"宫位生克",
    "auspicious_inauspicious_formations":"格局", "primary_secondary_yongshen":"主辅用神",
    "conflicting_evidence":"冲突证据", "timing_qualification":"应期条件",
}
PARENTAL_PALACES = {"father":[6], "mother":[2]}
ORDER_PALACES = {
    ("male","eldest"):3, ("male","middle"):1, ("male","youngest"):8,
    ("female","eldest"):4, ("female","middle"):9, ("female","youngest"):7,
}
INTENTS = {"severity","treatment","discharge","surgery","travel_for_treatment"}


def _read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def _cell(chart, palace):
    return chart["palaces"].get(str(palace)) if palace else None


def _stem_cell(chart, stem):
    if not stem or stem == "甲":
        return None
    return _find_heaven_stem(chart, stem)


def _source_text(x):
    """Book names are never rendered to end users; internal provenance stays."""
    text = str(x or "")
    for word in ("《神奇之门》","《开悟之门》","神奇之门","开悟之门"):
        text = text.replace(word,"依据古籍")
    text = text.replace("unknown","尚无可核条件").replace("draft","研究记录")
    return text


def _relation_kind(chart, person, ill):
    return _direction(person, ill) if person and ill else "未核定"


def _context(inquiry):
    mode = inquiry.get("consultation_context")
    if mode not in ("direct_self", "direct_proxy", "event_news"):
        raise ValueError("consultation_context must be explicitly selected")
    if inquiry.get("relationship") == "self" and mode != "direct_self":
        raise ValueError("Self inquiry requires direct_self; no proxy role switching")
    if inquiry.get("relationship") != "self" and mode == "direct_self":
        raise ValueError("A proxy patient cannot be routed as direct_self")
    return mode


def bind_patient(chart, inquiry, calendar):
    """Produce DIFFERENT audit trails for self, father/mother, peer, and child.

    Role sources with only analogous ancient cases remain research candidates.
    They are never silently treated as authoritative universal patient stems.
    """
    profiles = _read(PROFILES)
    by_id = {x["id"]: x for x in profiles["profiles"]}
    relation = inquiry.get("relationship")
    if relation not in by_id:
        raise ValueError("Patient relationship not in source profile")
    mode = _context(inquiry)
    profile = by_id[relation]
    label = profile["label"]
    role = profile["references"][0] if profile["references"] else None
    via = None
    if mode == "event_news" and relation in profiles["event_news_override"]["eligible"]:
        role = profiles["event_news_override"]
        via = role["role_kind"]
        source_rule = role["source"]
        confidence = "source_case_specific_event_time"
    elif role:
        via = role["kind"]
        source_rule = role["source"]
        confidence = role["status"]
    else:
        source_rule = "no fixed personal signifier in indexed chapter"
        confidence = "unknown"
    if via in ("day_stem", "casting_day_stem"):
        ganzhi = calendar.get("day_ganzhi")
    elif via == "casting_year_stem":
        ganzhi = calendar.get("year_ganzhi")
    elif via == "casting_month_stem":
        ganzhi = calendar.get("month_ganzhi")
    elif via == "casting_hour_stem":
        ganzhi = chart["hour_ganzhi"]
    else:
        ganzhi = None
    if ganzhi is not None and (ganzhi not in cycle60()):
        raise ValueError("Reference ganzhi must be an actual sexagenary pillar")
    stem = ganzhi[:1] if ganzhi else None
    primary = _stem_cell(chart, stem)
    fixed_palaces = list(profile["palaces"])
    is_child = relation in ("child","son","daughter","nephew")
    if is_child:
        sex = inquiry.get("patient_sex")
        birth_order = inquiry.get("birth_order")
        candidate = ORDER_PALACES.get((sex,birth_order))
        if candidate and candidate not in fixed_palaces:
            fixed_palaces.append(candidate)
    if relation == "parent":
        if inquiry.get("patient_sex") == "male":
            fixed_palaces.append(6)
        elif inquiry.get("patient_sex") == "female":
            fixed_palaces.append(2)
    if relation == "older_relative" and inquiry.get("relative_specific") == "aunt":
        fixed_palaces.append(2)
    if relation == "younger_sibling" and inquiry.get("patient_age_band") == "young" and inquiry.get("patient_sex") == "male":
        fixed_palaces.append(8)
    extra_cells = [_cell(chart, p) for p in sorted(set(fixed_palaces))]
    birth = inquiry.get("patient_birth_ganzhi") or inquiry.get("subject_year_ganzhi")
    if birth and birth not in cycle60():
        raise ValueError("Patient birth year Ganzhi must be a full valid 60-cycle pillar")
    birth_cell = _stem_cell(chart, birth[:1]) if birth else None
    # If birth is Jia, hidden stem must be resolved from the actual Jia-xun,
    # NEVER pretend a visible '甲' exists in a nine-ritual chart.
    extras = ["{p}参考宫主{m}".format(
        p=_p(c), m=("父辈/乾" if c["palace"]==6 and relation in ("father","parent")
                    else "母辈/坤" if c["palace"]==2 and relation in ("mother","parent")
                    else "年龄排行辅助象")) for c in extra_cells if c]
    role_name = ("闻讯事件日干" if mode == "event_news" and via == "day_stem" else
                 "日干" if via in ("day_stem","casting_day_stem") else
                 "年干（长辈候选）" if via=="casting_year_stem" else
                 "月干（同辈候选）" if via=="casting_month_stem" else
                 "时干（晚辈候选）" if via=="casting_hour_stem" else "未核定的患者个人用神")
    if stem:
        role_name += stem
    elif via:
        role_name += "（对应年月日时柱未提供，个人用神尚未绑定）"
    if primary is None and stem:
        role_name += "（实际落宫尚未绑定）"
    birth_note = (("患者生年" + birth + "已提供，作为额外参考；落" + _p(birth_cell)
                   if birth_cell else "患者生年" + birth + "已提供，但年命干落宫未核定，不强行填充")
                  if birth else "患者年命未提供，本次不使用年命")
    status = "matched_source_condition" if primary and confidence.startswith("source_") else (
        "conditional_candidate" if primary else "no_personal_palace_verified")
    return {
        "relationship": relation,"label":label,"context":mode,
        "consultation_label":profiles["contexts"][mode],
        "role_name":role_name,"role_via":via,"stem":stem,
        "main_cell":primary,"extra_cells":extra_cells,
        "birth_cell":birth_cell,"birth_note":birth_note,
        "source_rule":source_rule,"confidence":confidence,"status":status,
        "note":profile["note"],"extra_meaning":"；".join(extras) or "无额外固定人物宫",
    }


def _meaning_star(name):
    return STAR_MEANINGS.get(name, "该星本问事象意未核实")


def _meaning_door(name):
    return DOOR_MEANINGS.get(name, "该门本问事象意未核实")


def _meaning_deity(name):
    return DEITY_MEANINGS.get(name, "该神本问事象意未核实")


def _door(cell):
    return cell.get("door") if cell else None


def _deity(cell):
    return cell.get("deity") if cell else None


def _meaning_stem(stem, chart=None, ill=None, inquiry=None):
    basic = STEM_MEANINGS.get(stem, "未收录该干病象")
    if chart and ill and ill["palace"] == 2:
        if stem == "庚":
            basic = ("筋骨、肌肤等外部象" if chart["dun"] == "yang"
                     else "坚硬、阻结、水道相关的内部组合象")
        if stem == "癸":
            basic = ("神经、水道等外部象" if chart["dun"] == "yang"
                     else "水道、消化与体内水液象")
    return basic


def _palace_star_relation(ill):
    palace_el = ELEMENTS[ill["palace"]]
    rel = element_relation(palace_el, "土")
    desc = {"生":"宫生病星，传统病星有气", "克":"宫克病星，传统病星受制",
            "受生":"病星生宫，病星气有外泄", "受克":"病星克宫，病星受耗",
            "比和":"宫星比和，传统病象同气"}[rel]
    return "宫" + rel + "星", desc


def _factor_chinese(factors, keys):
    zh = {"present":"存在", "absent":"未触发", "unknown":"未核实",
          "not_applicable":"不适用"}
    return "；".join(FACTOR_LABELS[k] + "：" + zh.get(factors[k]["status"], "未核实")
                    for k in keys)


def _open_door(chart):
    cells = [c for c in chart["palaces"].values() if c.get("door") == "开门"]
    if len(cells) != 1:
        raise ValueError("Exactly one opening door required in a complete chart")
    return cells[0]


def _void_for(chart, c):
    if not c:
        return "患者宫未核定"
    void = hourly_void_branches(chart["hour_ganzhi"])["xun_kong_branches"]
    return "宫支与旬空重合" if set(PALACE_BRANCHES[c["palace"]]) & set(void) else "宫支不在旬空"


def _edge(x):
    return "本宫克病宫，传统制病之象" if x.endswith("克") else (
        "本宫受病宫所克，传统制病力量受限" if x.endswith("受克") else
        "与病宫比和，未形成克病关系" if x.endswith("比和") else
        "对病宫有生扶象，未形成克病关系" if x.endswith("生") else
        "与病宫有五行联系，须结合格局")


def _build_slots(chart, inquiry, calendar, base, roles):
    b = dict(base["slots"])
    ill, carrier = _find_star(chart, "天芮星")
    doctor, _ = _find_star(chart, "天心星")
    yi = _stem_cell(chart,"乙")
    event = _stem_cell(chart,chart["hour_ganzhi"][0])
    far_star = _cell(chart,chart["value_star_palace"])
    far_door = _cell(chart,chart["value_door_palace"])
    open_cell = _open_door(chart)
    person = roles["main_cell"]
    fac = base["audit"]["factor_statuses"]
    open_relation = _direction(open_cell,ill)
    ill_pair = carrier["carried_stem"]+"加"+ill["earth_stem"]
    old_pair = _source_text(b["stem_pair_meaning"])
    if "本地原文释义尚未读取" in old_pair:
        if ill_pair in ("乙加壬","癸加辛"):
            old_pair = "依据古籍，" + ill_pair + "在疾病案例中为不利克应"
        else:
            old_pair = "本地格局解释未收录，该项不参与吉凶合断"
    figures = evaluate_candidates(chart)["matches"]
    matched = [f for f in figures if f["palace"] == ill["palace"]]
    cluster = base["traditional_cautions"]
    positives = base["traditional_support"]
    star_stage = b["illness_star_stage"]
    strong = "旺相" if star_stage in ("旺","相") else "衰弱" if star_stage in ("囚","休","废") else "未知"
    star_relation, star_relation_desc = _palace_star_relation(ill)
    ill_door = ill["door"]
    if ill_door == "死门":
        door_effect = "病困闭塞象偏重（传统）"
    elif ill_door in ("生门","休门","开门"):
        door_effect = "出现调养与生机的门象，但仍看病星和格局"
    else:
        door_effect = "有本门相应病象，仍须配合全宫判断"
    patient_relation = _direction(person,ill)
    patient_meaning = ("已计算实际人物宫；" + patient_relation if person
                       else "人物宫未核实，仅列条件性取用，不冒充真实患者落宫")
    patient_void = _void_for(chart,person)
    doctor_rel, yi_rel = _direction(doctor,ill), _direction(yi,ill)
    support = list(positives)
    bad = list(cluster)
    if ill_door=="死门" and not cluster:
        bad.append("天芮临死门：传统闭塞病困象")
    if star_stage=="旺":
        bad.append("天芮星月令旺：传统病星有气")
    if person and patient_void=="宫支与旬空重合":
        bad.append("患者宫逢旬空：人物用神虚象")
    if person and patient_relation.endswith("克"):
        support.append("患者用神宫克病宫（仍核空墓强弱）")
    seen = lambda seq: "；".join(dict.fromkeys(seq)) if seq else "无已成立的相关证据"
    if bad and support:
        summary="传统病象与相反的医药/患者制病象并存"
    elif bad:
        summary="传统病象不利条件较集中"
    elif support:
        summary="传统医药或患者制病象较明显"
    else:
        summary="尚未形成可辨的传统轻重结论"
    hard_keys = ("six_yi_striking_punishment","branch_opposition","branch_punishment",
                 "branch_harm","month_day_break","door_press_palace",
                 "heaven_stem_tomb","stem_storage")
    motion_keys = ("fuyin_fanyin","travel_horse","xun_kong","kong_near_far",
                   "kong_fill","kong_clash","hidden_stems","palace_interactions")
    missing = [FACTOR_LABELS[x] for x in FACTOR_IDS if fac[x]["status"]=="unknown"]
    b.update({
        "relationship_label":roles["label"],"consultation_label":roles["consultation_label"],
        "hour_ganzhi":chart["hour_ganzhi"],
        "patient_role_name":roles["role_name"],"patient_role_meaning":patient_meaning,
        "patient_role_note":roles["note"],"patient_birth_note":roles["birth_note"],
        "patient_palace":_p(person),"patient_contents":_contents(person),
        "patient_void":patient_void,
        "patient_illness_relation":patient_relation,
        "patient_extra_palace_note":roles["extra_meaning"],
        "patient_door_deity_meaning":_meaning_door(_door(person))+"；"+_meaning_deity(_deity(person)),
        "patient_condition_signal":("有实际人物宫，" + patient_relation+"；"+patient_void
                                    if person else "该关系个人用神未核定，不对患者个人状态作断言"),
        "value_star_meaning":_meaning_star(chart["value_star"]),
        "value_star_element":ELEMENTS[far_star["palace"]],
        "value_star_door_meaning":_meaning_door(far_star["door"]),
        "value_star_deity_meaning":_meaning_deity(far_star["deity"]),
        "value_star_illness_relation":_direction(far_star,ill),
        "far_star_decision":"参考宫位五行与病星的有向生克，不代替疾病主用神",
        "value_door_meaning":_meaning_door(chart["value_door"]),
        "value_door_relation_meaning":("门克宫，门迫受制" if b["value_door_relation"]=="迫"
                                     else "门宫状态由实际五行生克确定"),
        "far_door_decision":"作为整体门象参考，与值符星及疾病宫分开取证",
        "illness_palace_star_relation":star_relation,
        "illness_palace_star_meaning":star_relation_desc,
        "illness_anchor_signal":("临死门，病困象偏重" if ill_door=="死门"
                                 else "需结合旺衰与星门神格局"),
        "body_focus_meaning":"其象意从体表和体内两路观察，不是同时发生的多个实际疾病",
        "inner_outer_meaning":_source_text(b["inner_outer"]),
        "body_priority":"天芮所携带干与内外盘条件共同确认的部位象",
        "illness_stem_element":STEM_ELEMENTS.get(carrier["carried_stem"],"未知"),
        "illness_heaven_stem_meaning":_meaning_stem(carrier["carried_stem"],chart,ill),
        "illness_earth_stem_meaning":_meaning_stem(ill["earth_stem"],chart,ill),
        "illness_stem_combined_meaning":("在"+ill["gua"]+"宫以"+_meaning_stem(carrier["carried_stem"],chart,ill)
                                         +"与"+_meaning_stem(ill["earth_stem"],chart,ill)+"联合取象"),
        "event_stem_meaning":_meaning_stem(chart["hour_ganzhi"][0]),
        "event_stem_element":STEM_ELEMENTS.get(chart["hour_ganzhi"][0],"未知"),
        "event_contents":_contents(event),
        "event_relation_meaning":_edge(b["event_relation"]) if event else "事体落宫未核定",
        "star_stage_meaning":("传统病星有气" if strong=="旺相" else
                              "传统病星偏衰" if strong=="衰弱" else "缺月令不能定旺衰"),
        "illness_strength_conclusion":strong,
        "season_label":"当前月令" if calendar.get("month_branch") else "未给实际节令",
        "stem_pair_short":ill_pair,
        "stem_pair_meaning_short":old_pair,
        "illness_pair_health_meaning":("本盘已记录的疾病问事格局象" if "未收录" not in old_pair
                                     else "无足够原书格局释义"),
        "stem_pair_orientation":("不利" if ill_pair in ("乙加壬","癸加辛") else "须与全宫合判"),
        "formation_matches_short":"、".join(f["formation_name"] for f in matched) or "没有触发已编码的复合格局",
        "formation_interpretation":"；".join(f["formation_name"]+"：按完整条件匹配"
                                   for f in matched) or "没有额外格局可解释",
        "formation_effect":"格局条件在本宫成立，仍需与门、神及病星一起研判" if matched else "不额外添吉凶",
        "deity_short_meaning":_meaning_deity(ill["deity"]),
        "deity_health_effect":"与"+_meaning_door(ill_door)+"及天芮疾病象合参",
        "deity_orientation":"须按同宫条件判定，未固定加减分",
        "illness_door_meaning":_meaning_door(ill_door),
        "illness_door_element":("土" if ill_door in ("生门","死门") else
                               "木" if ill_door in ("伤门","杜门") else
                               "金" if ill_door in ("开门","惊门") else
                               "火" if ill_door=="景门" else "水"),
        "illness_door_relation_meaning":("门克宫，为门迫" if b["illness_door_relation"]=="迫"
                                        else "不构成门迫，另按门宫作用判断"),
        "door_health_effect":door_effect,
        "month_break_short":"尚未得到可核的独立月破结果",
        "void_trigger_short":"未具可核实的具体填实、逢冲时间触发",
        "hard_factor_summary_zh":_factor_chinese(fac,hard_keys),
        "movement_factor_summary_zh":_factor_chinese(fac,motion_keys),
        "hard_target_effect":"先核病宫、患者宫的确切命中，其余宫不自动带入",
        "motion_conflict_meaning":"关键用神为主、动静证据分别记录",
        "positive_evidence_zh":seen(support),
        "adverse_evidence_zh":seen(bad),
        "counter_evidence_zh":"与病星格局方向相反的患者和医药关系需独立保留",
        "evidence_status":summary,
        "missing_factors_zh":"、".join(missing) if missing else "无遗漏的强制审计项目",
        "timing_conditions_zh":"空亡"+b["void_branches"]+"；患者宫"+patient_void+"；内外盘"+_source_text(b["inner_outer"]),
        "timing_result_zh":"缺少符合本次事件的完整时间触发与核验历法，本次不输出日历日期",
        "traditional_summary_v20":summary,
        "body_summary_short":b["body_surface"],
        "doctor_relation_meaning":_edge(doctor_rel),
        "doctor_door_meaning":_meaning_door(_door(doctor)),
        "doctor_deity_meaning":_meaning_deity(_deity(doctor)),
        "doctor_signal":_edge(doctor_rel),
        "yi_relation_meaning":_edge(yi_rel) if yi else "乙奇落宫尚未核定",
        "yi_door_meaning":_meaning_door(_door(yi)),
        "yi_deity_meaning":_meaning_deity(_deity(yi)),
        "yi_signal":_edge(yi_rel) if yi else "乙奇落宫尚未核定",
        "open_door_palace":_p(open_cell),
        "open_door_contents":_contents(open_cell),
        "open_door_relation":open_relation,
        "open_door_signal":_edge(open_relation),
        "treatment_result":summary+"；医药宫有向生克已列，不能当临床疗效",
        "discharge_result":"只有人物宫、病宫和出院目标条件都明确时才能择古籍应期；现阶段不指定出院日",
        "surgery_result":"开门与病宫"+open_relation+"，只说明传统手术象，不判断手术必要性",
        "travel_direction_status":"未输入可靠目标地点与方向，本次不填写出行方向",
        "travel_result":"按出行、病宫、患者宫和医药宫条件联合阅读，不能由盘面代替实际转诊决定",
    })
    return {k:_source_text(v) for k,v in b.items()}


def analyze_health_v20(*,chart,inquiry,calendar=None,db_path=None):
    """All user-facing slots derive from chart and the selected role+intent.

    No author-book answer/feedback enters decision slots. Unlike V1.9,
    generic phrase fragments are replaced by full interpreted 21-section prose.
    """
    calendar = calendar or {}
    if not isinstance(inquiry,dict) or inquiry.get("intent") not in INTENTS:
        raise ValueError("Choose the specific health intent first")
    role = bind_patient(chart,inquiry,calendar)
    # Existing 24-factor source facts are shared, but each health intent has
    # an independent sequence and different use of facts/actor evidence.
    source_inquiry = dict(inquiry)
    source_inquiry["intent"] = "severity"
    if source_inquiry["relationship"] not in ("self","father","mother","son","daughter","nephew","spouse","older_relative","brother","sister","other"):
        source_inquiry["relationship"] = "other"
    base = render_health_severity(chart,source_inquiry,calendar=calendar,db_path=db_path)
    slot = _build_slots(chart,inquiry,calendar,base,role)
    if inquiry["intent"]=="severity":
        pack = _read(SEVERITY)
        sections=pack["sections"]
    else:
        pack = _read(OTHER)
        sections=pack["descriptions"][inquiry["intent"]]["sections"]
    texts=[]
    for section in sections:
        try:
            content=section["format"].format_map(slot)
        except KeyError as exc:
            raise ValueError("Undeclared slot: "+str(exc)) from exc
        if re.search(r"(?<!{){[A-Za-z_][A-Za-z_0-9]*}",content):
            raise ValueError("Unexpanded symbolic placeholder")
        if "《神奇之门》" in content or "《开悟之门》" in content:
            raise ValueError("Source book title leaked into user-facing text")
        texts.append({"id":section["id"],"title":section["title"],"text":content})
    factor_states=base["audit"]["factor_statuses"]
    if len(factor_states)!=24 or set(factor_states)!=set(FACTOR_IDS):
        raise ValueError("24 mandatory factors dropped")
    return {
        "schema":"wengua_health_intent_dynamic_v20",
        "domain":"health","intent":inquiry["intent"],
        "status":"traditional_source_research_not_clinical",
        "role_binding":{
            k:v for k,v in role.items()
            if k not in ("main_cell","extra_cells","birth_cell")},
        "sections":texts,
        "reading_text":"\n\n".join(x["title"]+"："+x["text"] for x in texts),
        "audit":{
            "twenty_four_factors":factor_states,
            "unknown_factors":base["audit"]["unknown_factors"],
            "source_book_names_user_facing":False,
            "patient_birth_year_optional":True,
            "historical_feedback_used_as_input":False,
            "medical_severity_grade":None,
            "specific_disease_diagnosis":None,
            "recovery_date_as_clinical_claim":None,
            "source_chart_recast_only":True,
        },
        "source_provenance":_read(SEVERITY)["provenance"],
    }
