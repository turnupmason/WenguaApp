"""Fixed ten/eleven-section offline Chinese severity renderer.

NO generated prose after filling the approved literal V2.6 JSON template;
no web/network/LLM. All decisions are ancient textual symbolism only,
not a real patient's clinical severity or treatment recommendation.
"""
from __future__ import annotations
import json
from pathlib import Path
from .casting_shenqi import STARS, DOORS
from .health_dynamic_v21 import bind_patient, _checked_calendar, _meaning_door, _meaning_deity, _meaning_star, _meaning_stem
from .health_severity_v22 import (
    analyze_health_severity_v22,_find_star,_find_heaven_stem,_palace,_body,_read,
    SHENQI,_yes_void,_phase_from_chart,FORBIDDEN_CUSTOMER
)
from .health_severity_v25 import fuyin_fanyin_facts, _traditional_choice, INNER
from .marriage_runtime import ELEMENTS, element_relation
from .health_severity_template import STEM_ELEMENTS

ROOT=Path(__file__).resolve().parents[2]
TEMPLATE=ROOT/"data/knowledge/phrase_library/health_v26/severity_customer_template.json"
EL_PRODUCES={"木":"火","火":"土","土":"金","金":"水","水":"木"}
EL_CONTROLS={"木":"土","土":"水","水":"火","火":"金","金":"木"}


def _direction(left,right,left_label,right_label):
    """Explicit subject, object and direction for every ordered 五行 relation."""
    el=ELEMENTS[left["palace"]]
    er=ELEMENTS[right["palace"]]
    if el==er:
        return left_label+"与"+right_label+"同属"+el+"，比和"
    if EL_PRODUCES[el]==er:
        return left_label+el+"生"+right_label+er+"，"+right_label+"受生"
    if EL_CONTROLS[el]==er:
        return left_label+el+"克"+right_label+er+"，"+right_label+"受制"
    if EL_PRODUCES[er]==el:
        return right_label+er+"生"+left_label+el+"，"+left_label+"受生"
    if EL_CONTROLS[er]==el:
        return right_label+er+"克"+left_label+el+"，"+left_label+"受制"
    raise ValueError("Invalid directional element relation")


def _star_relation(ill):
    palace=ELEMENTS[ill["palace"]]
    if palace=="土":return "病宫与天芮土比和，病星宫星同气"
    if EL_CONTROLS[palace]=="土":
        return "病宫"+palace+"克天芮土，病星受宫制"
    if EL_CONTROLS["土"]==palace:
        return "天芮土克病宫"+palace+"，病星克宫"
    if EL_PRODUCES[palace]=="土":
        return "病宫"+palace+"生天芮土，病星受宫生"
    if EL_PRODUCES["土"]==palace:
        return "天芮土生病宫"+palace+"，病星生宫"
    raise ValueError("Incomplete five elements")


def _source_pair_prose(pair,stem_heaven,stem_earth,chart,ill):
    """Only domain-relevant book semantics may appear in user text.

    The original excerpt/name/hash still stay in internal audit. A salacious
    unrelated original title is NOT a health outcome or a patient's trait.
    """
    key=pair["id"]
    if key=="heaven_over_earth:壬:辛" and "螣蛇相缠" in pair["name"]:
        return "壬加辛为螣蛇相缠，主纠缠阻滞"
    if key=="heaven_over_earth:壬:壬" and "蛇入地罗" in pair["name"]:
        return "壬加壬为蛇入地罗，主事体反复牵缠"
    if stem_heaven==stem_earth:
        return stem_heaven+"加"+stem_earth+"，同一五行之象重见"
    el1,el2=STEM_ELEMENTS[stem_heaven],STEM_ELEMENTS[stem_earth]
    if el1==el2:
        return stem_heaven+"加"+stem_earth+"，两干同属"+el1+"，"+_meaning_stem(stem_heaven,chart,ill)+"之象重叠"
    if EL_PRODUCES[el1]==el2:
        return stem_heaven+"加"+stem_earth+"，天盘"+el1+"生地盘"+el2
    if EL_CONTROLS[el1]==el2:
        return stem_heaven+"加"+stem_earth+"，天盘"+el1+"克地盘"+el2
    if EL_PRODUCES[el2]==el1:
        return stem_heaven+"加"+stem_earth+"，地盘"+el2+"生天盘"+el1
    return stem_heaven+"加"+stem_earth+"，地盘"+el2+"克天盘"+el1


def _fuyin_text(fy):
    st,dt=fy["star"],fy["door"]
    if st=="伏吟" and dt=="伏吟":
        return "九星、八门俱伏吟，主慢、主迟滞"
    if st=="反吟" and dt=="反吟":
        return "九星、八门俱反吟，主快、主变化反复"
    if st=="伏吟" or dt=="伏吟":
        return ("九星伏吟" if st=="伏吟" else "八门伏吟")+"，主慢；另一项非伏吟"
    if st=="反吟" or dt=="反吟":
        return ("九星反吟" if st=="反吟" else "八门反吟")+"，主快；另一项非反吟"
    return "九星、八门均非伏吟或反吟"


def _inside(cell,dun):
    return "内盘" if cell["palace"] in INNER[dun] else "外盘"


def _pace(fy,ill,person,dun):
    illness=_inside(ill,dun);patient=_inside(person,dun)
    if fy["star"]=="伏吟" or fy["door"]=="伏吟":
        return "伏吟主慢，进展偏迟"
    if fy["star"]=="反吟" or fy["door"]=="反吟":
        return "反吟主快，变化较急"
    if illness==patient=="外盘":
        return "外盘主慢"
    if illness==patient=="内盘":
        return "内盘主快"
    return "病患分居内外盘，缓急并见"


def _evidence_summary(*,verdict,stage,ill,person,doctor,medicine,press,
                      person_empty,month):
    """Traditional evidence priority with palace-specific facts. No guessed weights."""
    adverse=[]
    favorable=[]
    if stage in ("旺","相"):
        adverse.append("天芮于"+month+"月为"+stage)
    if ill["door"]=="死门":
        adverse.append("病宫临死门")
    if ill["palace"] in press:
        adverse.append(_palace(ill)+"的"+ill["door"]+"门迫")
    if person["palace"] in press and person["palace"]!=ill["palace"]:
        adverse.append(_palace(person)+"的"+person["door"]+"门迫")
    if person_empty:
        adverse.append("患者宫逢旬空")
    if _star_relation(ill).endswith("病星受宫制"):
        favorable.append("病星受落宫克制")
    if element_relation(ELEMENTS[doctor["palace"]],ELEMENTS[ill["palace"]])=="克":
        favorable.append("天心"+_palace(doctor)+"克病宫")
    if element_relation(ELEMENTS[medicine["palace"]],ELEMENTS[ill["palace"]])=="克":
        favorable.append("乙奇"+_palace(medicine)+"克病宫")
    if person["door"] in ("开门","生门","休门"):
        favorable.append("患者临"+person["door"])
    if not person_empty:
        favorable.append("患者宫不空")
    if verdict["verdict"]=="病凶":
        adverse_text="、".join(adverse[:4]) if adverse else "病宫仍有传统不利象"
        counter="；虽"+"、".join(favorable[:2])+"，仍以病宫不利象为主" if favorable else ""
        return adverse_text+counter
    main="、".join(favorable[:3]) if favorable else "用神有传统扶助象"
    counter="；虽"+"、".join(adverse[:2])+"，主判仍以制病扶助为重" if adverse else ""
    return main+counter


def _meaning_singular(cell,chart):
    stars="、".join(s["star"] for s in cell["heaven_stars"] if s["star"]!="天禽星")
    return stars+"、"+cell["door"]+"、"+cell["deity"]


def analyze_health_severity_v26(*,chart,inquiry,calendar=None,db_path=None):
    if not isinstance(inquiry,dict) or inquiry.get("intent")!="severity":
        raise ValueError("Unreviewed four other health intents cannot run")
    calendar=_checked_calendar(calendar,chart)
    source=analyze_health_severity_v22(chart=chart,inquiry=inquiry,calendar=calendar,db_path=db_path)
    user=bind_patient(chart,inquiry,calendar)
    person=user["main_cell"]
    if not person:
        raise ValueError("Patient role missing; cannot assert a traditional verdict")
    pack=json.loads(TEMPLATE.read_text("utf8"))
    if len(pack["sections"])!=11:
        raise ValueError("Unexpected template section count")
    ill,carrier=_find_star(chart,"天芮星")
    doctor,_=_find_star(chart,"天心星")
    medicine=_find_heaven_stem(chart,"乙")
    event=_find_heaven_stem(chart,chart["hour_ganzhi"][0])
    if not medicine or not event: raise ValueError("Missing source chart role")
    stage=_phase_from_chart(ill,calendar.get("month_branch"))
    fy=fuyin_fanyin_facts(chart)
    bad_press=source["audit"]["actual_door_press_palaces"]
    pair=source["audit"]["stem_pair_source"]
    if pair["id"]!="heaven_over_earth:"+carrier["carried_stem"]+":"+ill["earth_stem"]:
        raise ValueError("Paired source must agree with actual 天/地")
    verdict=_traditional_choice(ill,person,doctor,medicine,stage,
                                element_relation(ELEMENTS[ill["palace"]],"土"),
                                _yes_void(chart,person))
    extras=[c for c in user.get("extra_cells",[]) if c and c["palace"]!=person["palace"]]
    aux=extras[0] if extras else None
    if inquiry["relationship"]=="father":
        aux=chart["palaces"]["6"] if person["palace"]!=6 else None
    # One palace display per section, no duplicate star-door-deity descriptions.
    starred=[s["star"] for s in ill["heaven_stars"] if s["star"]!="天芮星"]
    star_suffix=("与"+"、".join(starred)+"同") if starred else ""
    surface,internal=_body(_read(SHENQI),ill["palace"])
    if ill["door"]=="死门":
        door_image="死门主闭塞、病困"
    else:
        door_image=ill["door"]+"主"+_meaning_door(ill["door"])
    person_void=_yes_void(chart,person)
    void_mean="患者宫逢旬空，吉象受虚" if person_void else "患者宫不逢旬空"
    press_targets=[
        chart["palaces"][str(p)] for p in bad_press
        if p in {ill["palace"],person["palace"]}
    ]
    specific_press="；".join(_palace(c)+"的"+c["door"]+"构成门迫" for c in press_targets)
    special="；".join(x for x in (specific_press,void_mean) if x)
    if not special:special="病宫与患者宫均未见门迫或旬空"
    pace=_pace(fy,ill,person,chart["dun"])
    inner_ill=_inside(ill,chart["dun"])
    inner_person=_inside(person,chart["dun"])
    inner_facts="阴遁" if chart["dun"]=="yin" else "阳遁"
    inner_facts+="病宫在"+inner_ill+"、患者宫在"+inner_person
    if fy["star"] in ("伏吟","反吟") or fy["door"] in ("伏吟","反吟"):
        qualifier="以伏吟反吟定快慢，再参内外盘"
    else:
        qualifier="星门无整盘伏吟反吟，按内外盘断缓急"
    disease_duration=inquiry.get("illness_duration")
    if (fy["star"]=="反吟" or fy["door"]=="反吟") and inquiry.get("illness_duration") in ("new","chronic"):
        specific="；新病反吟传统有趋愈之象" if inquiry["illness_duration"]=="new" else "；久病反吟传统偏不利"
    else:
        specific=""
    timing="不强定实际应期日期"+specific
    if person["palace"]==doctor["palace"]:
        doc_loc=_palace(doctor)+"（与患者同宫）"
    else:
        doc_loc=_palace(doctor)
    if doctor["palace"]==medicine["palace"]:
        medicine_loc=_palace(medicine)+"（与天心同宫）"
    else:medicine_loc=_palace(medicine)
    value_star=chart["palaces"][str(chart["value_star_palace"])]
    value_door=chart["palaces"][str(chart["value_door_palace"])]
    if value_star["palace"]==value_door["palace"]:
        value_loc=_palace(value_star)
    else:
        value_loc=_palace(value_star)+"、"+_palace(value_door)
    role_stem=user["stem"]
    method=("以日干"+role_stem+"为本人用神" if inquiry["relationship"]=="self" else
            "以"+user["role_name"].replace("（长辈候选）","")+"为"+user["label"]+"用神")
    born=inquiry.get("patient_birth_ganzhi")
    reason=_evidence_summary(verdict=verdict,stage=stage,ill=ill,person=person,
                 doctor=doctor,medicine=medicine,press=bad_press,
                 person_empty=person_void,month=calendar["month_branch"])
    body_image="、".join(x for x in (surface,internal) if x)
    fields={
        "patient_label":user["label"],"patient_method":method,
        "patient_palace":_palace(person),
        "value_star":chart["value_star"],"value_door":chart["value_door"],
        "value_palace_sentence":value_loc,
        "value_star_meaning":_meaning_star(chart["value_star"]),
        "value_door_meaning":_meaning_door(chart["value_door"]),
        "value_disease_relation":_direction(value_star,ill,"值符宫","病宫"),
        "extra_stars":star_suffix,"ill_palace":_palace(ill),
        "ill_door":ill["door"],"ill_deity":ill["deity"],
        "ill_heaven":carrier["carried_stem"],"ill_earth":ill["earth_stem"],
        "palace_star_relation":_star_relation(ill),
        "ill_door_image":door_image,
        "ill_deity_image":ill["deity"]+"主"+_meaning_deity(ill["deity"]),
        "pair_domain_meaning":_source_pair_prose(pair,carrier["carried_stem"],ill["earth_stem"],chart,ill),
        "body_image":body_image,
        "month_branch":calendar["month_branch"],"ill_strength":stage,
        "strength_significance":("病星有气，不宜单取吉门判断" if stage in ("旺","相") else
                                  "病星气弱，仍须看人物与医药宫"),
        "patient_symbols":_meaning_singular(person,chart),
        "person_relation":_direction(person,ill,"患者宫","病宫"),
        "person_void_meaning":void_mean,
        "aux_palace":_palace(aux) if aux else "",
        "aux_symbols":_meaning_singular(aux,chart) if aux else "",
        "aux_relation":_direction(aux,ill,"辅助宫","病宫") if aux else "",
        "doctor_palace":doc_loc,"medicine_palace":medicine_loc,
        "doctor_relation":_direction(doctor,ill,"天心宫","病宫"),
        "medicine_relation":_direction(medicine,ill,"乙奇宫","病宫"),
        "hour_stem":chart["hour_ganzhi"][0],"event_palace":_palace(event),
        "event_relation":_direction(event,ill,"时干宫","病宫"),
        "targeted_special_facts":special,
        "star_door_pattern":_fuyin_text(fy),
        "inner_outer_fact":inner_facts,"pace_judgement":pace,
        "duration_qualifier":"","timing_qualifier":timing,
        "traditional_verdict":verdict["verdict"],
        "evidence_reason":reason,"final_pace":("传统缓急：偏慢" if "慢" in pace else "传统缓急：偏快" if "快" in pace else "缓急仍须合参"),
    }
    if born:
        fields["patient_method"]+="，另参出生年命"+born
    visible=[]
    for section in pack["sections"]:
        if section.get("optional")=="auxiliary" and not aux:
            continue
        paragraph=section["format"].format_map(fields)
        if any(forbid in paragraph for forbid in FORBIDDEN_CUSTOMER):
            raise ValueError("Internal engineering language cannot reach patient")
        if any(word in paragraph for word in pack["pair_domain_policy"]["banned_rendered_name_substrings"]):
            raise ValueError("Irrelevant ancient pair-name leaked")
        if "{" in paragraph or "}" in paragraph:
            raise ValueError("Unexpanded template slots")
        if "门门迫" in paragraph or "与与" in paragraph or "同同" in paragraph:
            raise ValueError("Duplicated template words")
        visible.append({"id":section["id"],"title":section["title"],"text":paragraph})
    if len(visible)!=11-(0 if aux else 1):
        raise ValueError("Actual visible template count mismatch")
    audit={**source["audit"],
        "fuyin_fanyin":fy,
        "illness_inner_outer":inner_ill,"patient_inner_outer":inner_person,
        "tradition_binary_verdict":verdict,
        "customer_sections":len(visible),
        "source_facts_retained":21,
        "pair_original_still_auditable":pair,
        "render_mode":"strict_static_format_map_offline_no_GPT",
        "runtime_model_calls":0,"runtime_network_calls":0,
        "medical_severity_verified":False,"user_content_accepted":False}
    return {
        "schema":pack["schema"],"domain":"health","intent":"severity",
        "status":"software_test_not_user_content_acceptance",
        "sections":visible,
        "reading_text":"\n\n".join(x["title"]+"："+x["text"] for x in visible),
        "audit":audit,"source_provenance":source["source_provenance"]
    }
