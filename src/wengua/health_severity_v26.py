"""V2.6: corrected offline 11-slot Chinese reading, six disease facets combined.

One runtime route: source-checked calendar/chart -> actual actor roles -> local
book-pair SQLite -> classical fact criteria -> fixed Python phrase slots.
No GPT, API, network, freehand polishing, guessed conditions, prognosis dates.
Earlier 194 cases and all previous model errors are input-independent.
"""
from __future__ import annotations
from pathlib import Path
import json, re
from .casting_shenqi import STARS, DOORS
from .health_severity_v22 import (
    analyze_health_severity_v22, _find_star, _find_heaven_stem,
    _p, _palace, _qualified, _body, _read, SHENQI,
    _yes_void, _meaning_deity, _meaning_door, _meaning_star,
    _meaning_stem, _relation, _phase_from_chart, FORBIDDEN_CUSTOMER)
from .health_dynamic_v21 import bind_patient, _checked_calendar
from .marriage_runtime import ELEMENTS, element_relation
from .semantic_lookup import door_palace_relation
from .health_severity_template import STEM_ELEMENTS

TEMPLATE=Path(__file__).resolve().parents[2]/"data/knowledge/phrase_library/health_v26/severity_11_concise_template.json"
OPPOSITE={1:9,9:1,2:8,8:2,3:7,7:3,4:6,6:4}
INNER={"yin":{9,2,7,6},"yang":{1,8,3,4}}

def fuyin_fanyin_facts(chart):
    """Eight actual exterior stars & eight doors checked separately, exact home/opposite.

    Source: 开悟 第四章 伏吟/反吟 paragraphs and source-v1 concept tracks.
    Center-5 Tianqin excluded; never fake its door, star or deity.
    """
    home_stars={name:palace for palace,name in STARS.items() if palace!=5}
    home_doors={name:palace for palace,name in DOORS.items()}
    star_at={s["star"]:int(key) for key,c in chart["palaces"].items()
             for s in c["heaven_stars"] if s["star"] in home_stars}
    door_at={c["door"]:int(key) for key,c in chart["palaces"].items()
             if c["door"] in home_doors}
    if set(star_at)!=set(home_stars) or set(door_at)!=set(home_doors):
        raise ValueError("Incomplete nine-star/eight-door external positions")
    if len(set(star_at.values()))!=8 or len(set(door_at.values()))!=8:
        raise ValueError("Repeated exterior symbol position")
    sf=sum(star_at[s]==h for s,h in home_stars.items())
    sr=sum(star_at[s]==OPPOSITE[h] for s,h in home_stars.items())
    df=sum(door_at[d]==h for d,h in home_doors.items())
    dr=sum(door_at[d]==OPPOSITE[h] for d,h in home_doors.items())
    def state(home,reverse):
        return "伏吟" if home==8 else "反吟" if reverse==8 else "非伏吟反吟"
    star=state(sf,sr); door=state(df,dr)
    pace=("主迟滞、较慢" if "伏吟" in (star,door) else
          "主变化、较快" if "反吟" in (star,door) else
          "不凭伏吟反吟断缓急")
    return {"star":star,"door":door,"star_home":sf,"star_opposite":sr,
            "door_home":df,"door_opposite":dr,"pace":pace,
            "both_fuyin":star=="伏吟" and door=="伏吟",
            "both_fanyin":star=="反吟" and door=="反吟",
            "basis":"kaiwu_ch04_lines_556_580", "not_medical_timing":True}

def _inside(cell,dun):
    return "内盘" if cell["palace"] in INNER[dun] else "外盘"

def _stem_mean(stem,chart,cell):
    return _meaning_stem(stem,chart,cell)

def _short_cell(cell, include_stem=True):
    if not cell: return ""
    stars="、".join(s["star"] for s in cell["heaven_stars"])
    parts=stars+"、"+cell["door"]+"、"+cell["deity"]
    if include_stem:
        top="、".join(s["carried_stem"] for s in cell["heaven_stars"])
        parts+="，天盘"+top+"、地盘"+cell["earth_stem"]
    return parts

def _relation_mean(a,b,label_a,label_b):
    return _relation(a,b,label_a,label_b)

def _pure_relation(a,b):
    return element_relation(ELEMENTS[a["palace"]],ELEMENTS[b["palace"]])

def _traditional_choice(ill,person,doc,yi,stage,ill_star_relation,person_void,ill_press=False,person_press=False):
    strong=stage in ("旺","相")
    death=ill["door"]=="死门"
    medicine_controls=_pure_relation(doc,ill)=="克" or _pure_relation(yi,ill)=="克"
    star_controlled=ill_star_relation=="克"
    life=person["door"] in ("生门","休门","开门")
    adverse=[]
    if strong:adverse.append("天芮临月令"+stage+"，病象有气")
    if death:adverse.append("天芮临死门，主闭塞病困")
    if person_void:adverse.append("患者用神宫逢空")
    if ill_press:adverse.append("病宫门迫，病象受阻")
    if person_press:adverse.append("患者宫门迫，人物门象受阻")
    if ill["deity"]=="白虎":adverse.append("病星乘白虎，有伤损象")
    beneficial=[]
    if star_controlled:beneficial.append("病星受落宫克制")
    if medicine_controls:beneficial.append("天心或乙奇宫能克病宫")
    if life:beneficial.append("患者临"+person["door"]+"，有生机象"+("，但此门受迫" if person_press else ""))
    if not person_void:beneficial.append("患者宫不逢旬空")
    if strong and death and not (medicine_controls and star_controlled and life and not person_void):
        choice="病凶"
        why="；".join(adverse[:4])+"；虽有"+("、".join(beneficial[:2]) if beneficial else "其他宫位辅助象")+"，本盘仍以病困为主。"
    elif medicine_controls and life and not person_void:
        choice="病吉"
        why="；".join(beneficial[:3])+"，传统病象有制有扶。"
    elif star_controlled and life and not person_void and not (strong and death):
        choice="病吉"
        why="；".join(beneficial[:3])+"，传统病象趋缓。"
    elif strong and death:
        choice="病凶"
        why="；".join(adverse[:3])+"，暂以病困为主。"
    elif life and not person_void and not (strong and ill["deity"]=="白虎"):
        choice="病吉"
        why="；".join(beneficial[:3])+"，偏向可调养之象。"
    else:
        choice="病凶"
        why="；".join(adverse[:3])+"，暂以不利象为主。"
    return {"verdict":choice,"rationale":why,"unfavorable":adverse,
            "favorable":beneficial,"binary_is_traditional_only":True,
            "not_a_real_medical_risk_grade":True,
            "rule_branch":("sick_door_strong" if strong and death else
                           "controlled_and_beneficial" if choice=="病吉" else
                           "other_evidence_conflict"),
            "source_judgement_requires_user_review":True}

def analyze_health_severity_v26(*,chart,inquiry,calendar=None,db_path=None):
    if not isinstance(inquiry,dict) or inquiry.get("intent")!="severity":
        raise ValueError("Four other unreviewed health intents cannot render")
    calendar=_checked_calendar(calendar,chart)
    base=analyze_health_severity_v22(chart=chart,inquiry=inquiry,calendar=calendar,db_path=db_path)
    role=bind_patient(chart,inquiry,calendar)
    person=role["main_cell"]
    if not person:raise ValueError("No source-supported patient stem/palace; cannot force binary reading")
    pack=_read(TEMPLATE)
    if len(pack["sections"])!=11:raise ValueError("Exactly 11 chapter templates required")
    ill,carrier=_find_star(chart,"天芮星")
    doc,_=_find_star(chart,"天心星")
    yi=_find_heaven_stem(chart,"乙")
    if not yi: raise ValueError("乙奇宫缺失")
    event=_find_heaven_stem(chart,chart["hour_ganzhi"][0])
    if event is None:raise ValueError("Hour stem needs a real carrier")
    fy=fuyin_fanyin_facts(chart)
    month=calendar.get("month_branch")
    stage=_phase_from_chart(ill,month)
    pair=base["audit"]["stem_pair_source"]
    star_rel=element_relation(ELEMENTS[ill["palace"]],"土")
    pressed=base["audit"]["actual_door_press_palaces"]
    verdict=_traditional_choice(ill,person,doc,yi,stage,star_rel,_yes_void(chart,person),
                                ill["palace"] in pressed,person["palace"] in pressed)
    other_stars=[s["star"] for s in ill["heaven_stars"] if s["star"]!="天芮星"]
    disease_name="与"+"、".join(other_stars)+"同" if other_stars else ""
    body_a,body_b=_body(_read(SHENQI),ill["palace"])
    symbols=(ill["door"]+"主"+_meaning_door(ill["door"])+"，"+
             ill["deity"]+"主"+_meaning_deity(ill["deity"]))
    pair_label=pair["name"] if pair["category"]=="source_named_obstruction" else (
        carrier["carried_stem"]+"加"+ill["earth_stem"])
    if pair["category"]=="source_named_obstruction":
        symbols+="；"+pair["short"]
    elif STEM_ELEMENTS[carrier["carried_stem"]]==STEM_ELEMENTS[ill["earth_stem"]]:
        symbols+="；两干同属"+STEM_ELEMENTS[carrier["carried_stem"]]+"，"+
                 _stem_mean(carrier["carried_stem"],chart,ill)+"之象重见"
    if star_rel=="克":star_line="宫"+ELEMENTS[ill["palace"]]+"克天芮土，病星受制"
    elif star_rel=="比和":star_line="宫星同属土，病象有根"
    elif star_rel=="生":star_line="落宫生扶病星"
    elif star_rel=="受克":star_line="天芮土克落宫"+ELEMENTS[ill["palace"]]+"，病星克宫"
    elif star_rel=="受生":star_line="天芮土生扶落宫"+ELEMENTS[ill["palace"]]
    else:star_line="病星与落宫五行相互作用"
    role_line={"self":"本人以日干"+calendar["day_ganzhi"][0]+"为用神",
               "father":"父亲参起局年干"+calendar["year_ganzhi"][0]+"为用神"}.get(
               inquiry["relationship"],"以"+role["role_name"]+"为患者用神")
    aux=role["extra_cells"]
    aux=next((c for c in aux if c and c["palace"]!=person["palace"]),None)
    if inquiry["relationship"]=="father":
        aux=chart["palaces"]["6"]
    p_void=_yes_void(chart,person)
    press=base["audit"]["actual_door_press_palaces"]
    pointed_press=[chart["palaces"][str(i)] for i in press]
    relevant_press=[c for c in pointed_press if c["palace"] in {person["palace"],ill["palace"]}]
    if relevant_press:
        pdetail="；".join(("病宫" if c["palace"]==ill["palace"] else "患者宫")+
                           _palace(c)+c["door"]+"受门迫" for c in relevant_press)
    else:
        pdetail="病宫与患者宫均无门迫"
    pdetail+="；患者宫"+("逢旬空" if p_void else "不逢旬空")
    focus=pdetail
    inner_ill=_inside(ill,chart["dun"])
    inner_p=_inside(person,chart["dun"])
    inner_line=("阴遁" if chart["dun"]=="yin" else "阳遁")+\
        "病宫在"+inner_ill+"、患者宫在"+inner_p
    if inner_ill==inner_p:
        inner_line+="；"+("内盘主近快" if inner_ill=="内盘" else "外盘主远慢")
    else:inner_line+="；内外分居，缓急并参"
    # Physical fuyin/fanyin may oppose the inside/outside speed cue.
    if "伏吟" in (fy["star"],fy["door"]):
        timely="伏吟主慢，不据此强定应期"
    elif "反吟" in (fy["star"],fy["door"]):
        timely="反吟主快，不据此强定应期"
    else:timely="未见星门整盘伏吟反吟，不以此定应期"
    if "反吟" in (fy["star"],fy["door"]):
        known=inquiry.get("illness_duration")
        duration="新病反吟有转愈之象" if known=="new" else \
                 "久病反吟有不利之象" if known=="chronic" else \
                 "病程未注明，新病与久病不混断"
    else:
        duration="病程长短还须结合患者用神"
    if "伏吟" in (fy["star"],fy["door"]):
        speed="伏吟主迟，传统进展偏慢"
    elif "反吟" in (fy["star"],fy["door"]):
        speed="反吟主速，传统进展偏快"
    elif inner_ill==inner_p=="外盘":
        speed="病宫和患者宫均在外盘，传统进展偏慢"
    elif inner_ill==inner_p=="内盘":
        speed="病宫和患者宫均在内盘，传统进展偏快"
    else:
        speed="病宫在"+inner_ill+"，传统缓急尚须合看内外盘"
    clock_status=speed+"；不据此推算实际康复日期"
    # The front-end does not repeat any palace's full symbol set in
    # multiple paragraphs; doctor/person same-palace shown as shared place.
    doctor_line="天心落"+_palace(doc)
    if doc["palace"]==person["palace"]:doctor_line+="，与患者同宫"
    yi_line="乙奇落"+_palace(yi)
    if yi["palace"]==doc["palace"]:yi_line+="，与天心同宫"
    med_line=_relation_mean(doc,ill,"天心宫","病宫")+"；"+_relation_mean(yi,ill,"乙奇宫","病宫")
    role_support=("另参"+_palace(aux)+"，临"+aux["door"]+"、"+aux["deity"]+
                  "；"+_relation_mean(aux,ill,"亲属辅助宫","病宫")) if aux else ""
    phrase={
        "who":role["label"],"role":role_line,"person":_palace(person),
        "birth":("年命"+inquiry["patient_birth_ganzhi"] if inquiry.get("patient_birth_ganzhi") else ""),
        "value_star":chart["value_star"],"value_star_palace":_palace(chart["palaces"][str(chart["value_star_palace"])]),
        "value_star_image":_meaning_star(chart["value_star"]),
        "value_door":chart["value_door"],"value_door_palace":_palace(chart["palaces"][str(chart["value_door_palace"])]),
        "value_door_image":_meaning_door(chart["value_door"]),
        "far_relation":_relation_mean(chart["palaces"][str(chart["value_star_palace"])],ill,"值符宫","病宫"),
        "ill_p":_palace(ill),"other_star":disease_name,"ill_door":ill["door"],"ill_deity":ill["deity"],
        "ill_heaven":carrier["carried_stem"],"ill_earth":ill["earth_stem"],
        "pair":pair_label,"symbols":symbols,"star_line":star_line,
        "parts":body_a+"；"+body_b,
        "palace_special":("本宫门迫" if ill["palace"] in press else ""),
        "month":month,"stage":stage,
        "strength":("有气，须留意疾病阻滞象" if stage in ("旺","相") else "气势转弱，仍需看用神宫"),
        "person_contents":_short_cell(person),
        "person_relation":_relation_mean(person,ill,"患者宫","病宫"),
        "person_factors":("逢旬空，吉象受虚" if p_void else "不逢旬空"),
        "family_extra":role_support,
        "doc":doctor_line,"yi":yi_line,"med_relation":med_line,
        "hour":chart["hour_ganzhi"][0],"event_palace":_palace(event),
        "event_relation":_relation_mean(event,ill,"时干事体宫","病宫"),
        "factors":focus,
        "star_pattern":"九星"+fy["star"],"door_pattern":"八门"+fy["door"],
        "inner_outer":inner_line,"duration":duration,"timing":timely,
        "verdict":verdict["verdict"],"rationale":verdict["rationale"],
        "rhythm":clock_status,
    }
    # Data template enumerates only fixed phrases; optional factual sentences
    # are skipped, not filled with "unimplemented/unreviewed".
    display=[]
    for it in pack["sections"]:
        if it.get("optional")=="family_aux" and not aux: continue
        if it["id"]=="01_role":
            val="依据古籍，本次为"+phrase["who"]+"测病情轻重。"+phrase["role"]+"，落"+phrase["person"]+"。"
            if phrase["birth"]:val+="另参"+phrase["birth"]+"。"
        elif it["id"]=="02_far":
            val=("值符"+phrase["value_star"]+"落"+phrase["value_star_palace"]+"，主"+
                 phrase["value_star_image"]+"；值使"+phrase["value_door"]+"落"+
                 phrase["value_door_palace"]+"，主"+phrase["value_door_image"]+"。"+
                 phrase["far_relation"]+"。")
        elif it["id"]=="03_ill":
            val=("天芮"+(phrase["other_star"] if phrase["other_star"] else "")+"落"+
                 phrase["ill_p"]+"，临"+phrase["ill_door"]+"、乘"+phrase["ill_deity"]+
                 "，天盘"+phrase["ill_heaven"]+"加地盘"+phrase["ill_earth"]+"，为"+
                 phrase["pair"]+"。"+phrase["symbols"]+"；"+phrase["star_line"]+
                 "。人体类象涉及"+phrase["parts"]+"。")
        elif it["id"]=="04_strength":
            val=phrase["month"]+"月天芮为"+phrase["stage"]+"，"+phrase["strength"]+"。"
        elif it["id"]=="05_person":
            val=(phrase["role"]+"落"+phrase["person"]+"，"+phrase["person_contents"]+"。"+
                 phrase["person_relation"]+"；"+phrase["person_factors"]+"。")
        elif it["id"]=="06_family":
            val=phrase["family_extra"]+"。"
        elif it["id"]=="07_med":
            val=phrase["doc"]+"，"+phrase["yi"]+"；"+phrase["med_relation"]+"。"
        elif it["id"]=="08_event":
            val="时干"+phrase["hour"]+"落"+phrase["event_palace"]+"；"+phrase["event_relation"]+"。"
        elif it["id"]=="09_factors":
            val=phrase["factors"]+"。"
        elif it["id"]=="10_rhythm":
            val=(phrase["star_pattern"]+"、"+phrase["door_pattern"]+"，"+fy["pace"]+"。"+
                 phrase["inner_outer"]+"；"+phrase["duration"]+"。"+phrase["timing"]+"。")
        elif it["id"]=="11_final":
            val=("依据古籍，传统主判："+phrase["verdict"]+"。"+phrase["rationale"]+
                 phrase["rhythm"]+"。")
        else:raise ValueError("Unexpected display section")
        if any(s in val for s in FORBIDDEN_CUSTOMER) or "{" in val or "}" in val:
            raise ValueError("Customer output contained implementation text or unexpanded data")
        display.append({"id":it["id"],"title":it["title"],"text":val})
    if len(display)!=11-(1 if not aux else 0):
        raise AssertionError("Visible conditional section count")
    audit={**base["audit"],
           "source_facts_retained":21,
           "visible_sections":len(display),
           "fuyin_fanyin":fy,
           "yin_inner_palaces":sorted(INNER[chart["dun"]]),
           "illness_inner_outer":inner_ill,
           "patient_inner_outer":inner_p,
           "binary_traditional_conclusion":verdict,
        "filtered_context_unrelated_stem_pair_name":pair["name"] if pair_label!=pair["name"] else None,
        "actual_timing_speed_sentence":speed,
           "user_accepted":False,
           "render_mode":"local_python_static_strings_no_llm",
           "runtime_llm_calls":0,
           "runtime_web_calls":0,
           "clinical_severity_diagnosis":None}
    return {"domain":"health","intent":"severity","schema":pack["schema"],
            "status":"offline_user_acceptance_pending",
            "sections":display,
            "reading_text":"\n\n".join(x["title"]+"："+x["text"] for x in display),
            "audit":audit,"source_provenance":base["source_provenance"]}
