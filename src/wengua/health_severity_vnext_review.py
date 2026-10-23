"""Independent REVIEW branch of the illness-severity reading. Never replace V3.9.1.

The unchanged V3.9.1 result and its historical hashes remain the baseline.
This module adds an auditable, conditional book-evidence gate, physical-fact
deduplication and a three-way decision (including abstain/conflict), and
reorders ONLY the new preview prose. No weights, numeric scores or outcomes.
Clinical validity is not claimed.
"""
from __future__ import annotations

from collections import defaultdict
from .health_severity_v391_active import analyze_health_severity_v391
from .health_severity_v39 import analyze_health_severity_v39
from .health_dynamic_v21 import bind_patient
from .health_severity_v22 import _find_star, _find_heaven_stem, _palace
from .marriage_runtime import ELEMENTS, element_relation

# Original book annotations are keyword/index metadata, NOT executable proofs.
# These flags make a pair conditional; without a source-authored predicate
# evaluated on the actual palace it must NOT influence verdict precedence.
UNPROVEN_SOURCE_GATES = frozenset(
    ("如果", "但", "门迫", "入墓", "击刑", "月令", "吉门", "凶门", "为主", "为客")
)
SOURCE_HEALTH_POLARITIES = frozenset(
    ("book_health_adverse", "book_health_favorable")
)
BOOK_BAD_PATIENT = frozenset(
    ("book_adverse_formation", "book_health_adverse")
)
APPROVED_PERSON_ROLE_CONFIDENCE = frozenset(
    ("source_case_specific", "user_explicit_direction_verified_by_actual_chart")
)


def review_ordered_pairs(pairs, inquiry):
    """An ordered sky/earth hit is not necessarily a qualified illness rule.

    Never count a book title or keyword as proof of its conditions, and never
    treat an alternate name (42 supplements) as a separate occurrence.
    """
    by_key = {}
    for item in pairs:
        key=(item["palace"],item["star"],item["top"],item["bottom"])
        if key in by_key:
            by_key[key]["roles"] = sorted(set(by_key[key]["roles"] + item["roles"]))
            continue
        flags=item.get("source_conditions") or {}
        missing=[k for k in sorted(UNPROVEN_SOURCE_GATES) if flags.get(k)]
        kind=item["applicability"]
        if kind=="book_conflicted":
            state="source_disagreement"
            why="原书记述与疾病补充存在冲突，须保留双轨"
        elif kind=="book_duration_qualified" and inquiry.get("illness_duration") not in ("new","chronic"):
            state="missing_duration"
            why="必须有真实的新病／久病信息"
        elif missing:
            state="needs_complete_source_predicate"
            why="原书存在条件语句或特殊限制，尚无逐项核实的可执行判据："+ "、".join(missing)
        elif kind in SOURCE_HEALTH_POLARITIES:
            state="source_health_phrase_no_extra_gate"
            why="原书含测病专述；本条无已标注的条件缺口，仍须结合宫位主证"
        else:
            state="context_only"
            why="天地干名称命中，但未证明此处能作疾病轻重的独立吉凶证据"
        by_key[key]={
            "fact_id":"pair:%d:%s:%s:%s"%(item["palace"],item["star"],item["top"],item["bottom"]),
            "palace":item["palace"],"roles":list(item["roles"]),
            "star":item["star"],"heaven":item["top"],"earth":item["bottom"],
            "book_title":item["title"],"source_state":state,
            "applicability":kind,"source_gate_flags":missing,
            "explanation":why,
            "source_line_internal":item["source_line"],
            "source_sha256_internal":item["source_sha256"],
            "supplement_id_internal":item.get("user_health_supplement"),
        }
    return list(by_key.values())


def dedup_lifecycle_facts(evidence):
    """One fact ID per physical stem/branch/palace/stage, irrespective of role.

    Repeated mention of 墓 in V3.9 and full twelve-cycle text is ONE stage
    fact, not two separately weighted adverse events. Heaven and earth planes
    remain distinct. Include both branches where the real palace has two.
    """
    roles={
        "patient":evidence["patient"],
        "illness_tianrui_heaven":evidence["illness_tianrui_heaven"],
        "doctor_tianxin_heaven":evidence["doctor_tianxin_heaven"],
        "medicine_yi":evidence["medicine_yi"],
        "hour_event":evidence["hour_event"],
    }
    collected={}
    for role, data in roles.items():
        stem=data.get("stem")
        palace=data.get("palace")
        # The returned source verifier stores per-branch stage entries.
        for row in data.get("actual_stage_facts",[]):
            token=(stem,palace,row["branch"],row["stage"])
            if token not in collected:
                collected[token]={
                    "fact_id":"life:%s:%s:%s:%s"%(stem,palace,row["branch"],row["stage"]),
                    "stem":stem,"palace":palace,"branch":row["branch"],
                    "stage":row["stage"],"roles":[role],
                    "one_fact_even_if_referenced_twice":True}
            elif role not in collected[token]["roles"]:
                collected[token]["roles"].append(role)
    return list(collected.values())


def decide_review(*,role_confidence,patient_void,patient_hazards,
                  patient_to_illness,illness_to_star,medicine_controls,
                  eligible_bad_patient_pair,unverified_bad_patient_pair):
    """Only fully grounded high-priority chains may settle a symbolic verdict.

    No numeric weighting, no forced binary fallback to old verdict. Actual
    unknown person-signifier blocks a strong conclusion.
    """
    if role_confidence not in APPROVED_PERSON_ROLE_CONFIDENCE:
        return {"state":"unresolved","label":"取用待核",
                "reason":"当前人物用神属类推或条件候选，须先核定人物用神及其适用情境",
                "decisive_chain":None}
    hazard = patient_void or any(v in ("六仪击刑","入墓地") for v in patient_hazards)
    double_control=(patient_to_illness=="克" and illness_to_star=="克")
    ill_attacks=(patient_to_illness=="受克")
    ill_grows=(illness_to_star in ("生","比和"))
    patient_feeds=(patient_to_illness=="生" and illness_to_star=="生")
    confirmed_adverse=(ill_attacks and ill_grows) or patient_feeds or (
        ill_attacks and eligible_bad_patient_pair)
    uncertain_adverse=ill_attacks and unverified_bad_patient_pair and not confirmed_adverse
    if double_control and not hazard:
        return {"state":"favorable","label":"古籍象意偏吉",
                "reason":"患者宫克病宫，且病宫克天芮；患者用神无已核空墓刑阻碍",
                "decisive_chain":"patient_controls_illness_and_illness_controls_tianrui"}
    if confirmed_adverse and medicine_controls:
        return {"state":"conflicted","label":"强证据相持",
                "reason":"不利主链成立，但医药宫出现独立制病反证，不能简单抵消任何一侧",
                "decisive_chain":"adverse_vs_independent_medicine"}
    if confirmed_adverse:
        return {"state":"adverse","label":"古籍象意偏不利",
                "reason":"病宫克患者且扶助病星，或患者生病宫再生病星，或已核的患者凶格并发",
                "decisive_chain":"verified_distinct_adverse_chain"}
    if double_control and hazard:
        return {"state":"conflicted","label":"制病证据受阻",
                "reason":"存在双重制病，但患者宫空亡或已核刑墓限制此主证",
                "decisive_chain":"double_control_blocked"}
    if uncertain_adverse:
        return {"state":"unresolved","label":"吉凶暂不能定",
                "reason":"患者宫受克，但相关天地干凶格的原书条件尚未逐项核定",
                "decisive_chain":None}
    return {"state":"unresolved","label":"吉凶暂不能定",
            "reason":"无符合高优先级完整主链的证据；不能从旧版二元结果机械继承结论",
            "decisive_chain":None}


def _section(title,content,key):
    return {"id":key,"title":title,"text":content.strip()}


def analyze_health_severity_review(*,chart,inquiry,calendar,db_path):
    """Standalone review API; V3.9.1 remains byte-for-byte and callable."""
    if inquiry.get("intent")!="severity":
        raise ValueError("Only disease-severity domain-specific review is implemented")
    v391=analyze_health_severity_v391(
        chart=chart,inquiry=inquiry,calendar=calendar,db_path=db_path)
    legacy=analyze_health_severity_v39(
        chart=chart,inquiry=inquiry,calendar=calendar,db_path=db_path)
    actor=bind_patient(chart,inquiry,calendar)
    if actor["main_cell"] is None:
        raise ValueError("No confirmed actual chart palace for this person")
    person=actor["main_cell"]
    ill,_=_find_star(chart,"天芮星")
    doctor,_=_find_star(chart,"天心星")
    yi=_find_heaven_stem(chart,"乙")
    hour=_find_heaven_stem(chart,chart["hour_ganzhi"][0])
    pairs=review_ordered_pairs(legacy["audit"]["v37_81_ordered_full_book_pairs"],inquiry)
    source_patient=[x for x in pairs if "患者宫" in x["roles"]]
    confirmed_bad=any(x["applicability"] in BOOK_BAD_PATIENT
                      and x["source_state"]=="source_health_phrase_no_extra_gate"
                      for x in source_patient)
    uncertain_bad=any(x["applicability"] in BOOK_BAD_PATIENT
                      and x["source_state"]!="source_health_phrase_no_extra_gate"
                      for x in source_patient)
    relation=element_relation(ELEMENTS[person["palace"]],ELEMENTS[ill["palace"]])
    star_relation=element_relation(ELEMENTS[ill["palace"]],"土")
    medicine_controlled=any(
        element_relation(ELEMENTS[c["palace"]],ELEMENTS[ill["palace"]])=="克"
        for c in (doctor,yi))
    original_hazards=legacy["audit"]["actual_tomb_punishment_v28"]
    patient_hazards=[x["kind"] for x in original_hazards if x["role"]=="patient"]
    void=legacy["audit"]["v37_2_sided_double_evidence"]["patient_void"]
    result=decide_review(
        role_confidence=actor["confidence"],patient_void=void,
        patient_hazards=patient_hazards,patient_to_illness=relation,
        illness_to_star=star_relation,medicine_controls=medicine_controlled,
        eligible_bad_patient_pair=confirmed_bad,
        unverified_bad_patient_pair=uncertain_bad)
    sections={s["id"]:s["text"] for s in v391["sections"]}
    def has(key):return sections.get(key,"")
    q=list(x for x in pairs if x["source_state"]=="source_health_phrase_no_extra_gate")
    pending=list(x for x in pairs if x["source_state"] in
       ("needs_complete_source_predicate","source_disagreement","missing_duration"))
    life=dedup_lifecycle_facts(v391["source_chart_evidence"])
    # A useful *presentation* order, not a new claim or post hoc answer fit.
    lead=(result["label"]+"。"+result["reason"]+"。"
          "这是依原书条件分析的传统象意，并非医学诊断或治疗预后。")
    main=(has("01_role")+" "+has("05_patient")+" "+has("03_illness"))
    counter=(has("04_season")+" "+has("07_medicine"))
    risks=has("09_hazards")
    if pending:
        risks+=("；"+str(len(pending))+"处天地干存在原书未完成核实的适用条件，"
                "已保留为待核依据，不凭名称推翻主判断。")
    pace=has("08_hour")+" "+has("10_pace")
    notes=has("02_far")+" "+has("06_gender")
    result_sections=[
        _section("主判断",lead,"01_conclusion"),
        _section("患者与疾病主证",main,"02_main"),
        _section("医药及相反证据",counter,"03_counter"),
        _section("格局限制与冲突",risks,"04_limits"),
        _section("病势与应期条件",pace,"05_time"),
        _section("值符值使与辅助参考",notes,"06_extra"),
    ]
    public="\n\n".join(x["title"]+"：\n"+x["text"] for x in result_sections)
    if any(x in public for x in ("健康指数","吉凶概率","100分","原书第","SHA256","数据库")):
        raise ValueError("Review prose leaked an internal marker, score or source line")
    return {
        "schema":"wengua_health_severity_vnext_conditional_preview_v1",
        "status":"independent_review_not_public_release",
        "domain":"health","intent":"severity",
        "verdict":result,
        "sections":result_sections,"reading_text":public,
        "no_scores":True,"medical_validity_claimed":False,
        "baseline_v391_unchanged":True,
        "audit":{
            "legacy_v39_symbolic_verdict":legacy["audit"]["v37_actual_health_priority_verdict"],
            "legacy_v391_reading_text":v391["reading_text"],
            "role_confidence":actor["confidence"],
            "role_via":actor["role_via"],
            "primary_role_palace":person["palace"],
            "illness_palace":ill["palace"],
            "patient_to_illness":relation,"illness_to_star":star_relation,
            "medicine_controls":medicine_controlled,
            "conditional_source_pairs":pairs,
            "book_81_catalog_complete":len(pairs)==9,
            "supplement_rules_preserved":len(legacy["audit"]["v34_42_directional_pairs"]),
            "composites_preserved":len(legacy["audit"]["v36_17_source_rechecked_composites"]),
            "actual_stage_facts_unique":life,
            "patient_hazards":patient_hazards,
            "missing_source_predicates":len(pending),
            "actual_original_author_outcomes_not_used":True,
            "legacy_score":None
        }
    }
