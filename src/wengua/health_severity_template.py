"""Deterministic, detailed HEALTH -> SEVERITY slot-filling research renderer.

Only the original chart/known domain methods supply facts. Every unimplemented
factor stays unknown. Source phrases are *traditional book symbolism*, not
clinical severity, disease identification, prognosis, treatment or cure.
Existing historical case outcomes are never loaded by this module.
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from .casting_shenqi import layout_from_explicit_bureau, SIX_JIA
from .semantic_lookup import GUAS, nine_star_month_status, door_palace_relation
from .symbol_relations import door_season
from .marriage_runtime import (
    ELEMENTS, element_relation, hourly_void_branches, PALACE_BRANCHES,
    compute_source_chart_factors,
)
from .phrase_pipeline import FACTOR_IDS
from .formation_candidates import evaluate_candidates

ROOT = Path(__file__).resolve().parents[2]
TEMPLATE = ROOT / "data/knowledge/phrase_library/health_severity_v1/template.json"
SHENQI = ROOT / "data/knowledge/shenqi/health_prediction_ch01/method_index.json"
KAIWU = ROOT / "data/knowledge/kaiwu/health_prediction_ch02_section01/method_index.json"
CONCEPTS = ROOT / "data/knowledge/shenqi/shijia_judgments_ch05/concept_index.json"
MONTH_ELEMENTS = {"寅": "木", "卯": "木", "辰": "土", "巳": "火",
                  "午": "火", "未": "土", "申": "金", "酉": "金",
                  "戌": "土", "亥": "水", "子": "水", "丑": "土"}
STEM_ELEMENTS = {"甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土",
                 "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水"}
RELATIONS = {
    "self": "本人", "father": "父亲", "mother": "母亲",
    "brother": "兄弟", "sister": "姐妹", "nephew": "侄儿",
    "older_relative": "长辈", "spouse": "配偶", "son": "儿子",
    "daughter": "女儿", "other": "他人",
}
# These are contextual examples from Kaiwu's disease chapter line 85.
# Not free-standing assignments of a disease to an individual stem.
STEM_IMAGES = {
    "癸": "原书第85行在不同内外盘的两例中分别参考水道、神经类象，不能脱离宫位、阴阳遁套用",
    "庚": "原书第85行在外盘案例关联筋骨，在内盘另一案例关联结节、肿块，不能单凭庚诊断",
    "辛": "原书第85行在伤门个案结合筋骨象；并非所有辛都主筋骨病",
    "壬": "原书第85行在伤门临壬个案提及水道象，须先满足该语境",
    "丁": "丁五行为火；原书可结合火热、血液等多宫组合谈象，不能见丁便断上火或血液病",
}


def _json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def _validate_chart(chart):
    if not isinstance(chart, dict) or chart.get("school_id") != "shijia_zhuanpan":
        raise ValueError("Only the existing verified-style Shijia Zhuanpan chart structure is accepted")
    if chart.get("status") not in ("source_text_consistency_only", "engine_verified"):
        raise ValueError("An untrusted candidate index is not a nine-palace chart")
    fresh = layout_from_explicit_bureau(
        dun=chart["dun"], ju=chart["ju"], hour_ganzhi=chart["hour_ganzhi"])
    for key in ("value_star", "value_door", "value_star_palace",
                "value_door_palace", "xun_shou", "palaces"):
        if chart.get(key) != fresh[key]:
            raise ValueError("Cast recomputation mismatch: " + key)
    # A source text consistency recast does not independently verify local
    # time, astronomical term, casting variant or a historical prediction.
    return fresh


def _find_star(chart, name):
    hits = []
    for c in chart["palaces"].values():
        for s in c["heaven_stars"]:
            if s["star"] == name:
                hits.append((c, s))
    if len(hits) != 1:
        raise ValueError("Expected one carrier of " + name)
    return hits[0]


def _find_heaven_stem(chart, stem):
    hits = [(c, s) for c in chart["palaces"].values()
            for s in c["heaven_stars"] if s["carried_stem"] == stem]
    return hits[0][0] if len(hits) == 1 else None


def _p(cell):
    return (str(cell["palace"]) + "宫（" + cell["gua"] + "）") if cell else "未核定"


def _contents(cell):
    if not cell:
        return "未核定"
    stars = "、".join(s["star"] + "携" + s["carried_stem"]
                    for s in cell["heaven_stars"]) or "未载星"
    return "星" + stars + "、" + str(cell["door"] or "中宫无普通八门") + "、" + str(
        cell["deity"] or "中宫无普通八神") + "、地盘" + cell["earth_stem"]


def _direction(a, b):
    if not a or not b:
        return "未核定（缺实际落宫）"
    return "此宫对病宫" + element_relation(ELEMENTS[a["palace"]], ELEMENTS[b["palace"]])


def _season(branch):
    return ("四季月" if branch in "辰未戌丑" else
            "春" if branch in "寅卯" else "夏" if branch in "巳午" else
            "秋" if branch in "申酉" else "冬")


def _role(chart, inquiry, calendar):
    relation = inquiry.get("relationship")
    if relation not in RELATIONS:
        raise ValueError("Specify a supported explicit patient relationship")
    year = inquiry.get("subject_year_ganzhi")
    optional = "已给出生年命，仅列作可选附加证据，不自动改变患者主用神" if year else (
        "未提供出生年命，照原书其他适用取用方法分析，不虚构年命")
    hour_stem = chart["hour_ganzhi"][0]
    day = calendar.get("day_ganzhi")
    year_of_cast = calendar.get("year_ganzhi")
    if relation == "self" and day and day[0] in STEM_ELEMENTS:
        stem, why = day[0], "本人以问测日干为候选（神奇健康章67行）"
    elif relation == "father" and year_of_cast and year_of_cast[0] in STEM_ELEMENTS:
        stem, why = year_of_cast[0], "问父病依原书案例兼年干、乾宫（神奇健康章105行）；不能单用年干"
    elif relation == "nephew":
        stem, why = hour_stem, "叔辈问侄子以时干为条件候选（神奇健康章145行）"
    elif relation == "older_relative" and year_of_cast and year_of_cast[0] in STEM_ELEMENTS:
        stem, why = year_of_cast[0], "长辈案例兼年干与坤宫（神奇健康章192行）；不可普适化"
    else:
        stem, why = None, "该关系缺原书可执行的具体个人取用方法，仍可分析天芮与医药"
    if stem == "甲":
        # Birth years must NOT be guessed. A calendrical Jia stem alone
        # does not identify its hidden Jia-xun instrument.
        return None, why + "；甲遁干未由完整甲子旬判定", optional
    return _find_heaven_stem(chart, stem) if stem else None, why, optional


def _semantic_pair(pair, db_path):
    records = _json(CONCEPTS)["records"]
    r = next((x for x in records if x["concept_id"] == pair), None)
    source = ("《神奇之门》第五章第" + str(r["line"]) + "行（候选）") if r else (
        "未匹配到有序干克应索引")
    meaning = "本地原文释义尚未读取；不得凭组合名猜病种"
    if db_path:
        db_uri = "file:" + Path(db_path).resolve().as_posix() + "?mode=ro"
        with sqlite3.connect(db_uri, uri=True) as db:
            found = db.execute(
                "SELECT original_excerpt,source_start_line,review_status "
                "FROM semantic_assertions WHERE concept_id=? "
                "ORDER BY source_start_line LIMIT 1", (pair,)).fetchone()
        if found and found[0].strip():
            meaning = "本地书源摘句（" + found[2] + "，需按全文适用条件审核）：" + found[0].strip()[:140]
            source += "；本地 semantic_assertions 第" + str(found[1]) + "行"
    return source, meaning


def _factor_text(facts, keys):
    out = []
    for k in keys:
        row = facts.get(k, {})
        status = row.get("status", "unknown")
        out.append(k + "=" + status + (("（" + str(row.get("rule_ref")) + "）")
                                       if status not in ("unknown", "not_applicable") else ""))
    return "；".join(out)


def render_health_severity(chart, inquiry, *, calendar=None, db_path=None):
    """Recast and fill 21 detailed source-anchored template sections.

    A clinical severity grade, disease identity, prognosis and recovery date
    are never inferred from cultural symbolism. Missing evidence stays unknown.
    The input already needs a real full chart from the existing casting layer.
    """
    calendar = calendar or {}
    if not isinstance(inquiry, dict) or inquiry.get("intent") != "severity":
        raise ValueError("Only health/severity is implemented; do not route other intents here")
    _validate_chart(chart)
    template, shenqi, kaiwu = _json(TEMPLATE), _json(SHENQI), _json(KAIWU)
    anchors = template["provenance"]
    if (shenqi["source_sha256"] != anchors[0]["sha256"] or
            kaiwu["source_sha256"] != anchors[1]["sha256"]):
        raise ValueError("Mismatch between current original-book health indices and template")
    if {x["id"] for x in template["sections"]} != {
        "01_question", "02_far_star", "03_far_door", "04_illness_star",
        "05_body_part", "06_stem_image", "07_strength", "08_stem_pair",
        "09_formations", "10_deity", "11_door", "12_void_break",
        "13_patient", "14_doctor", "15_medicine", "16_disease_interaction",
        "17_hard_factors", "18_movement", "19_counter", "20_timing",
        "21_summary",
    }:
        raise ValueError("Severity template sections have been altered")
    illness, ill_carrier = _find_star(chart, "天芮星")
    doctor, _ = _find_star(chart, "天心星")
    yi = _find_heaven_stem(chart, "乙")
    event = _find_heaven_stem(chart, chart["hour_ganzhi"][0])
    patient, binding, optional = _role(chart, inquiry, calendar)
    diseases = {row["palace"]: row for row in shenqi["body_palace_mappings"]}
    body = diseases.get(illness["palace"], {})
    branch = calendar.get("month_branch", "")
    if branch and branch not in MONTH_ELEMENTS:
        raise ValueError("Invalid month branch")
    month_el = MONTH_ELEMENTS.get(branch)
    star_stage = nine_star_month_status("天芮星", month_el)["value"] if month_el else "unknown（缺真实节气月支）"
    door = illness.get("door")
    door_relation = door_palace_relation(door, illness["palace"]) if door else {}
    door_stage = door_season(door, _season(branch))["stage"] if door and branch else None
    empty = hourly_void_branches(chart["hour_ganzhi"])
    void_on_palace = sorted(set(PALACE_BRANCHES[illness["palace"]]) &
                            set(empty["xun_kong_branches"]))
    pair = "heaven_over_earth:" + ill_carrier["carried_stem"] + ":" + illness["earth_stem"]
    pair_source, pair_meaning = _semantic_pair(pair, db_path)
    formations = [x for x in evaluate_candidates(chart) if x["palace"] == illness["palace"]]
    formations_text = ("；".join(x["formation_name"] + "（" + x["variant_id"] + "，draft）"
                              for x in formations) if formations else "未匹配到可核实的已编码复合候选；不是无格局")
    facts = compute_source_chart_factors(chart)
    if set(facts) != set(FACTOR_IDS):
        raise ValueError("Factor registry mismatch; never drop a mandatory factor")
    hard = ("six_yi_striking_punishment", "branch_opposition", "branch_punishment",
            "branch_harm", "month_day_break", "door_press_palace",
            "heaven_stem_tomb", "stem_storage")
    move = ("fuyin_fanyin", "travel_horse", "hidden_stems", "kong_fill",
            "kong_clash", "kong_near_far", "palace_interactions",
            "conflicting_evidence", "timing_qualification")
    image = STEM_IMAGES.get(ill_carrier["carried_stem"],
                            "原书仅确认天干五行；本病种特定类象未核实")
    deity = illness.get("deity")
    deity_image = ("《开悟之门》同领域第191行曾将螣蛇用作虚幻不实的辅助象，不是通用吉凶扣分"
                   if deity == "螣蛇" else
                   "《开悟之门》第25与39行疾病案例提及白虎与其他凶格合参，不可据此诊断癌症"
                   if deity == "白虎" else "未找到该神在本问事的独立通用结论，待条件化检索")
    if chart["dun"] == "yin" and illness["palace"] in (2, 9):
        inner = "原书疾病章个案曾按阴遁本宫为内盘解读；需对照具体起局变体"
    elif chart["dun"] == "yang" and illness["palace"] == 2:
        inner = "原书疾病章第85行阳遁坤宫案例作外盘解读；非不加限定的通用结论"
    else:
        inner = "内外盘尚未由完整古籍条件核定"
    value_star = chart["palaces"][str(chart["value_star_palace"])]
    value_door = chart["palaces"][str(chart["value_door_palace"])]
    # The strongest disease-symbol cluster here comes from Kaiwu health lines
    # 25/39. This is an author-contextual *traditional cautionary pattern*,
    # NOT an oncology diagnosis, an empirically validated severity score or
    # an assertion about an individual's health.
    severe_cluster = (door == "死门" and deity == "白虎"
                      and "庚" in (ill_carrier["carried_stem"], illness["earth_stem"]))
    doctor_controls = element_relation(
        ELEMENTS[doctor["palace"]], ELEMENTS[illness["palace"]]) == "克"
    yi_controls = (yi is not None and element_relation(
        ELEMENTS[yi["palace"]], ELEMENTS[illness["palace"]]) == "克")
    positive = []
    adverse = []
    if severe_cluster:
        adverse.append("《开悟之门》疾病章第39行天芮、死门、庚、白虎四符同宫传统重警示组合")
    if doctor_controls:
        positive.append("天心宫克病星宫（原书医药辅助关系候选）")
    if yi_controls:
        positive.append("乙奇宫克病星宫（原书第187行有类似条件化案例）")
    if adverse and positive:
        traditional_pattern = "传统警示组合与医药辅助制病象并存，须作冲突审计"
    elif adverse:
        traditional_pattern = "符合原书个案的传统重警示组合，但不代表医学严重程度"
    elif positive:
        traditional_pattern = "出现医药制病的传统辅助象，但不能单据此判断病情不重"
    else:
        traditional_pattern = "尚无足够已编码的原书条件形成传统轻重倾向"
    known = ("天芮位置、宫位身体类象、天地干配对、门宫关系、"
             "九星季节状态（若月令已给）、医药宫位关系；"
             "条件触发：" + ("；".join(adverse + positive) or "尚无已核复合结论"))
    missing = [k for k in FACTOR_IDS if facts[k]["status"] == "unknown"]
    missing += ([] if month_el else ["calendar.month_branch"])
    if patient is None:
        missing.append("personal_patient_yongshen")
    slots = {
        "asker": str(inquiry.get("asker_label") or "求测者"),
        "relationship": RELATIONS[inquiry["relationship"]],
        "patient_binding": binding,
        "birth_year_status": optional,
        "value_star": chart["value_star"], "value_door": chart["value_door"],
        "value_star_palace": _p(value_star), "value_door_palace": _p(value_door),
        "value_star_contents": _contents(value_star),
        "value_door_contents": _contents(value_door),
        "value_door_relation": door_palace_relation(chart["value_door"],
                                                   value_door["palace"]).get("kind", "未知"),
        "illness_palace": _p(illness), "illness_element": ELEMENTS[illness["palace"]],
        "illness_stem": ill_carrier["carried_stem"],
        "illness_earth_stem": illness["earth_stem"],
        "body_surface": "、".join(body.get("surface", [])) or "未载",
        "body_internal": "、".join(body.get("internal", [])) or "未载",
        "inner_outer": inner, "illness_stem_image": image,
        "earth_stem_element": STEM_ELEMENTS.get(illness["earth_stem"], "未知"),
        "month_branch": branch or "未提供",
        "month_element": month_el or "未知",
        "illness_star_stage": star_stage,
        "stem_pair_id": pair, "stem_pair_source": pair_source,
        "stem_pair_meaning": pair_meaning, "formation_matches": formations_text,
        "illness_deity": deity or "未载", "deity_image": deity_image,
        "illness_door": door or "未载", "illness_door_relation": door_relation.get("kind", "未知"),
        "door_press": "已由门克宫确认" if door_relation.get("kind") == "迫" else
                      "已核算，不构成门迫" if door_relation.get("kind") else "未知",
        "door_season_stage": door_stage or "未知（缺真实节令或原书定义）",
        "hour_xun": empty["xun_head"],
        "void_branches": "、".join(empty["xun_kong_branches"]),
        "illness_void": ("宫支" + "、".join(void_on_palace) + "与旬空支重合，仍需该宫判法"
                          if void_on_palace else "宫支不在本旬空支内"),
        "month_break": "unknown（尚无经核验的月破推断实现，不能以月支冲宫直接当月破）",
        "patient_palace": _p(patient),
        "patient_illness_relation": _direction(patient, illness),
        "doctor_palace": _p(doctor), "doctor_relation": _direction(doctor, illness),
        "doctor_contents": _contents(doctor),
        "yi_palace": _p(yi), "yi_relation": _direction(yi, illness),
        "yi_contents": _contents(yi),
        "event_stem": chart["hour_ganzhi"][0], "event_palace": _p(event),
        "event_relation": _direction(event, illness),
        "hard_factor_summary": _factor_text(facts, hard),
        "movement_factor_summary": _factor_text(facts, move),
        "known_evidence": known,
        "counter_evidence": ("已触发的相反来源：" + ("；".join(positive) if adverse else "未形成明确相反触发") + "；尚未核实：" + "、".join(missing)),
        "evidence_status": traditional_pattern + "；并非真实病情分级",
        "timing_result": "未满足医学预后与古籍适用条件门槛，不输出真实康复日期",
        "traditional_summary": traditional_pattern + "。综合分析保留未查条件和双方反证；不能据此推断真实病情是否严重。",
    }
    sections = [{"id": section["id"], "title": section["title"],
                 "text": section["format"].format_map(slots)}
                for section in template["sections"]]
    return {
        "traditional_signal": traditional_pattern,
        "traditional_support": positive,
        "traditional_cautions": adverse,
        "schema": template["schema"], "intent": "severity", "domain": "health",
        "status": "draft_research_only_not_clinical_or_publishable",
        "chart_validation": "original_source_bureau_recast_only_not_calendar_verified",
        "sections": sections,
        "reading_text": "\n\n".join(s["title"] + "：" + s["text"] for s in sections),
        "slots": slots,
        "audit": {"factors_expected": len(FACTOR_IDS),
                  "factors_checked": len(facts), "factor_statuses": facts,
                  "unknown_factors": missing, "historical_answers_used_as_inputs": False,
                  "final_medical_severity": None, "medical_recovery_date": None},
        "sources": anchors,
    }
