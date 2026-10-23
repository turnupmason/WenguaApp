"""Palace-by-palace traditional illness-severity reasoning, review-only.

Macro (伏反吟) FIRST. Then: 天芮 → 天心 → 乙奇 → 患者/年命 →
时干/辅助. Each palace is inspected independently for monthly strength,
star/door/god, real life stages, void/tomb/punishment/door pressure.
Directed five-element relations are assessed AGAINST QUALITATIVE strengths:
a very weak source cannot automatically restrain a strong target.

Verdict is a comparison of distinct, eligible favorable/adverse *facts*,
not a V4.2 scalar health score, probability, biomedical prediction, or a
validated claim that true emptiness determines death/cure.
"""
from __future__ import annotations

from .marriage_runtime import (
    ELEMENTS,PALACE_BRANCHES,CONTROLS,PRODUCES,
    element_relation,hourly_void_branches)
from .semantic_lookup import nine_star_month_status,door_palace_relation,STAR_ELEMENT
from .health_severity_template import MONTH_ELEMENTS,STEM_ELEMENTS
from .health_severity_v28 import yi_month_stage
from .health_severity_v25 import fuyin_fanyin_facts
from .health_severity_v22 import _find_star,_find_heaven_stem,_palace
from .health_severity_v34 import HORSE
from .symbol_relations import door_season
from .health_lifecycle_v391 import source_full12,stage_for_stem_at_actual_palace
from .health_tianrui_25_matrix import inspect_tianrui_25

from .qualitative_month_palace import (
    STRONG,WEAK,VALID_STAGES,effect_of_relation,compare_vigor_before_control)
SEASONS={"寅":"春","卯":"春","辰":"四季月","巳":"夏","午":"夏",
         "未":"四季月","申":"秋","酉":"秋","戌":"四季月",
         "亥":"冬","子":"冬","丑":"四季月"}
OUTCOME={"favorable":"古籍象意偏吉","adverse":"古籍象意偏不利",
         "unresolved":"吉凶暂不能定"}


def element_month_stage(element,month_element):
    """Ordinary five-element 旺相休囚死, NOT nine-star 旺相休囚废."""
    if element==month_element:return "旺"
    if PRODUCES[month_element]==element:return "相"
    if PRODUCES[element]==month_element:return "休"
    if CONTROLS[element]==month_element:return "囚"
    if CONTROLS[month_element]==element:return "死"
    raise ValueError("Unrecognized month versus element")


def _month_status_for_star(name,month_el):
    return nine_star_month_status(name,month_el)["value"]


def inspect_palace(*,chart,cell,role,month_branch,star=None,stem=None):
    """Per-role palace record; never manufacture centre-five ordinary symbols."""
    idx=cell["palace"]
    if idx==5:
        raise ValueError("Centre five needs its own original-book method")
    month_el=MONTH_ELEMENTS[month_branch]
    branches=PALACE_BRANCHES[idx]
    empty=hourly_void_branches(chart["hour_ganzhi"])
    occupied=[b for b in branches if b in empty["xun_kong_branches"]]
    seasonal=SEASONS[month_branch]
    door=cell["door"]
    door_month=door_season(door,seasonal)["stage"] if door else None
    press=door_palace_relation(door,idx)["kind"]=="迫" if door else False
    table=source_full12()
    sky=[]
    for entry in cell["heaven_stars"]:
        stage=stage_for_stem_at_actual_palace(entry["carried_stem"],idx,table=table)
        sky.append({"star":entry["star"],"stem":entry["carried_stem"],
                    "life":stage["actual_stage_facts"],
                    "tombs":[x["branch"] for x in stage["actual_stage_facts"]
                             if x["stage"]=="墓"]})
    earth=stage_for_stem_at_actual_palace(cell["earth_stem"],idx,table=table)
    try:
        from .health_severity_v28 import STRIKING_PALACE
        striking=[x["stem"] for x in sky if STRIKING_PALACE.get(x["stem"])==idx]
    except ImportError:
        striking=[]
    stage_month=(_month_status_for_star(star,month_el) if star else
                 element_month_stage(STEM_ELEMENTS[stem],month_el) if stem else None)
    # True/false void is NOT implied by a branch intersecting xun-kong.
    return {
        "role":role,"palace":idx,"name":_palace(cell),
        "element":ELEMENTS[idx],"branches":list(branches),"month_stage":stage_month,
        "palace_month_stage":element_month_stage(ELEMENTS[idx],month_el),
        "star":star,"stem":stem,"deity":cell["deity"],"door":door,
        "door_month_stage":door_month,"door_pressure":press,
        "earth_stem":cell["earth_stem"],"heaven":sky,
        "earth_life":earth["actual_stage_facts"],
        "void_branches":occupied,
        "void_classification":"needs_original_source_true_false_conditions" if occupied else "not_void",
        "sky_tombs":[{"stem":v["stem"],"branch":b} for v in sky for b in v["tombs"]],
        "earth_tombs":[x["branch"] for x in earth["actual_stage_facts"]
                       if x["stage"]=="墓"],
        "striking_stems":striking,
    }


def inspect_pair(actor,target,*,actor_stage=None,target_stage=None):
    """Directed PALACE interaction; intrinsic star relationship is separate."""
    rel=element_relation(actor["element"],target["element"])
    blocked=bool(actor["void_branches"] or actor["striking_stems"] or
                 actor["sky_tombs"] or actor["door_pressure"])
    actor_month=actor_stage or actor["month_stage"] or actor["palace_month_stage"]
    target_month=target_stage or target["month_stage"] or target["palace_month_stage"]
    return {
        "from":actor["role"],"to":target["role"],"relationship":rel,
        "actor_month":actor_month,"target_month":target_month,
        "actor_palace_month":actor["palace_month_stage"],
        "target_palace_month":target["palace_month_stage"],
        **compare_vigor_before_control(
            rel,actor_symbol_month=actor_month,target_symbol_month=target_month,
            actor_palace_month=actor["palace_month_stage"],
            target_palace_month=target["palace_month_stage"],blocked=blocked),
    }


def collect_sequence(*,chart,calendar,actor,inquiry,matched_pairs=()):
    """Return full ordered palace inspections and an evidence ledger.

    Ledger counts at most one decision-bearing fact per physical event id,
    even where both Tianxin and Yi share one physical relationship or palace.
    Unverified ancient gates / true-false void stay pending, not 'negative'.
    """
    month=calendar["month_branch"]
    if month not in SEASONS:raise ValueError("A genuine month branch is required")
    ill_cell,ill_star=_find_star(chart,"天芮星")
    doc_cell,doc_star=_find_star(chart,"天心星")
    yi_cell=_find_heaven_stem(chart,"乙")
    hour_cell=_find_heaven_stem(chart,chart["hour_ganzhi"][0])
    person=actor["main_cell"]
    if any(c is None for c in (ill_cell,doc_cell,yi_cell,hour_cell,person)):
        raise ValueError("Actual patient, illness, doctor, medicine and hour palaces required")
    macro=fuyin_fanyin_facts(chart)
    ill=inspect_palace(chart=chart,cell=ill_cell,role="天芮病宫",month_branch=month,star="天芮星")
    doc=inspect_palace(chart=chart,cell=doc_cell,role="天心医生",month_branch=month,star="天心星")
    yi=inspect_palace(chart=chart,cell=yi_cell,role="乙奇医药",month_branch=month,stem="乙")
    patient=inspect_palace(chart=chart,cell=person,role="患者用神",month_branch=month,stem=actor["stem"])
    hour=inspect_palace(chart=chart,cell=hour_cell,role="时干事体",
                        month_branch=month,stem=chart["hour_ganzhi"][0])
    natal=None
    if actor.get("birth_cell"):
        birth=(inquiry.get("patient_birth_ganzhi") or inquiry.get("subject_year_ganzhi"))
        if not birth:raise ValueError("No actual natal stem supplied")
        natal=inspect_palace(chart=chart,cell=actor["birth_cell"],role="患者年命",
                             month_branch=month,stem=birth[0])
    # Existing source role-bound auxiliaries (including 乾坤 if applicable).
    extras=[]
    for c in actor.get("extra_cells",()):
        if c and c["palace"] not in {patient["palace"],natal["palace"] if natal else 0}:
            extras.append(inspect_palace(chart=chart,cell=c,role="辅助宫"+str(c["palace"]),
                                         month_branch=month,stem=c["earth_stem"]))
    interactions={
        "病宫五行对天芮本体":{
            "relationship":element_relation(ill["element"],STAR_ELEMENT["天芮星"]),
            **effect_of_relation(
                element_relation(ill["element"],STAR_ELEMENT["天芮星"]),
                ill["palace_month_stage"],ill["month_stage"],
                blocked=bool(ill["void_branches"] or ill["sky_tombs"] or ill["striking_stems"]))
        },
        "天心宫对病宫":inspect_pair(doc,ill),
        "乙奇宫对病宫":inspect_pair(yi,ill),
        "患者宫对病宫":inspect_pair(patient,ill),
        "时干宫对病宫":inspect_pair(hour,ill),
    }
    tianrui_25=inspect_tianrui_25(
        star_month=ill["month_stage"],
        star_element=STAR_ELEMENT["天芮星"],
        palace_element=ill["element"],
        palace_month=ill["palace_month_stage"],
        void_branches=ill["void_branches"],
        sky_tombs=ill["sky_tombs"],
        earth_tombs=ill["earth_tombs"],
        striking_stems=ill["striking_stems"],
        door_pressure=ill["door_pressure"])
    interactions["天芮星月令×星宫五行25格"]=tianrui_25
    if natal:interactions["年命宫对病宫"]=inspect_pair(natal,ill)
    for i,p in enumerate(extras,1):interactions["辅助宫"+str(i)+"对病宫"]=inspect_pair(p,ill)
    evidence={}
    def add(key,direction,text,source,role):
        if direction not in ("favorable","adverse","neutral","pending"):
            raise ValueError("Invalid traditional evidence direction")
        if key not in evidence:
            evidence[key]={"id":key,"direction":direction,"text":text,
                           "source":source,"roles":[role]}
        elif role not in evidence[key]["roles"]:
            evidence[key]["roles"].append(role)
        # Contradictory reused facts must never be counted both ways.
        if evidence[key]["direction"]!=direction:
            evidence[key]["direction"]="pending"
            evidence[key]["text"]+="；同一事实用于不同角色，含义相反，保留待辨"
    # The macro governs tempo, NEVER silently gives a favorable/adverse vote.
    add("macro:star_and_door", "neutral",
        "九星"+macro["star"]+"、八门"+macro["door"]+"；"+macro["pace"],
        macro["basis"],"宏观伏反吟")
    for cell in (ill,doc,yi,patient,*([natal] if natal else []),hour,*extras):
        role=cell["role"]; p=cell["palace"]
        # Strength describes a role's capacity; it has no default direction
        # for time/event or unbound auxiliary roles. Avoid treating every 旺 as
        # an independent auspicious sign and every 废 as a malicious omen.
        meaningful=role in ("天芮病宫","天心医生","乙奇医药",
                            "患者用神","患者年命")
        if cell["month_stage"] in STRONG:
            direction=("neutral" if role=="天芮病宫" else
                       "favorable" if meaningful else "neutral")
            add("monthly:"+role+":"+str(p),direction,
                role+"月令"+cell["month_stage"]+
                ("；仅说明事体旺弱，须联系病宫判断" if not meaningful else ""),
                "nine_star_month_status or original ordinary-stem month law",role)
        elif cell["month_stage"] in WEAK:
            direction=("neutral" if role=="天芮病宫" else
                       "adverse" if meaningful else "neutral")
            add("monthly:"+role+":"+str(p),direction,
                role+"月令"+cell["month_stage"]+"，作用弱但不代表完全没有作用",
                "nine_star_month_status or original ordinary-stem month law",role)
        if cell["void_branches"]:
            add("void:"+str(p),"pending",role+"旬空"+"/".join(cell["void_branches"])+
                "；真空/假空尚缺原书可执行判据，不假定必愈、必死或固定减半",
                "actual Xun emptiness; true/false unverified",role)
        if cell["sky_tombs"] or cell["earth_tombs"]:
            for t in cell["sky_tombs"]:
                add("tomb:sky:%s:%s:%s"%(p,t["stem"],t["branch"]),
                    "favorable" if role=="天芮病宫" else "adverse",
                    role+"天盘"+t["stem"]+"在"+t["branch"]+"入墓",
                    "source_full12/actual-palace-branch",role)
            for branch in cell["earth_tombs"]:
                add("tomb:earth:%s:%s:%s"%(p,cell["earth_stem"],branch),
                    "favorable" if role=="天芮病宫" else "adverse",
                    role+"地盘"+cell["earth_stem"]+"在"+branch+"入墓",
                    "source_full12/actual-palace-branch",role)
        for stem in cell["striking_stems"]:
            add("punishment:"+str(p)+":"+stem,
                "favorable" if role=="天芮病宫" else "adverse",
                role+"天盘"+stem+"六仪击刑","health_v28.STRIKING_PALACE",role)
        if cell["door_pressure"]:
            add("door_pressure:"+str(p),
                "pending" if role=="天芮病宫" else "adverse",
                role+cell["door"]+"门迫；病宫门迫究竟制病还是助病须按原书条件辨",
                "original door over palace five elements",role)
        if role=="天芮病宫" and cell["door"]=="死门":
            add("illness:death_door:"+str(p),"adverse",
                "天芮病宫临死门，但仍须结合死门旺衰及其他宫",
                "illness-local death-door symbol",role)
        if role=="天芮病宫" and cell["deity"]=="白虎":
            add("illness:white_tiger:"+str(p),"adverse",
                "天芮病宫临白虎，按原书伤病象候选","illness deity source",role)
    # The five monthly stages x five directed STAR→PALACE relationships are
    # ONE compound interpretation. Do NOT separately tally bare Tianrui month
    # and its element relationship, or assume a weak palace can restrain it.
    add("illness:tianrui_25:"+str(ill["palace"]),
        tianrui_25["eligible_evidence_direction"],
        "天芮月令"+tianrui_25["star_month"]+"，"+tianrui_25["category"]+
        "「"+tianrui_25["traditional_title"]+"」；落宫月令"+
        tianrui_25["palace_month"]+"；"+tianrui_25["why"],
        "source-verified month+element; user-proposed traditional 25-case interpretation",
        "天芮病宫")
    # These are the only role relationships for which both month-of-star
    # AND month-of-landing-palace must gate nominal doctor/medicine control.
    # 反侮/反克 describe candidates, not guaranteed reverse attack or cure.
    for marker,key in (("天心","天心宫对病宫"),("乙奇","乙奇宫对病宫")):
        contrast=interactions[key]
        if contrast["power_class"]=="反侮候选":
            add("strength_contrast:"+key,"adverse",
                marker+"名义克病宫，但星弱宫弱而病星旺宫旺，传统反侮候选；不能记作医药制病已成",
                "star month + real palace month + directional five elements",marker)
        elif contrast["power_class"]=="反克候选":
            add("strength_contrast:"+key,"favorable",
                marker+"名义受病宫克，但星旺宫旺而病星弱宫弱，传统反克候选；保留医药防御象，不等于痊愈",
                "star month + real palace month + directional five elements",marker)
    # Co-location is an opportunity even when doctor/medicine are weak.
    if doc["palace"]==ill["palace"] or yi["palace"]==ill["palace"]:
        aid=sorted([z for z in (doc,yi) if z["palace"]==ill["palace"]],
                   key=lambda z:z["role"])
        add("treatment:co_located:"+str(ill["palace"]),"favorable",
            "、".join(z["role"] for z in aid)+"与病宫同宫，传统有就医/用药之象；"+
            "即使月废或死也仍有微弱作用，不等于治疗有效",
            "actual same-palace role binding","天心与乙奇")
    for role,key in (("天心医生","天心宫对病宫"),("乙奇医药","乙奇宫对病宫"),
                     ("患者用神","患者宫对病宫"),("时干事体","时干宫对病宫"),
                     ("患者年命","年命宫对病宫")):
        if key not in interactions:continue
        rel=interactions[key]
        if rel["relationship"]=="比和":continue
        polarity=("favorable" if rel["relationship"]=="克" else
                  "adverse" if rel["relationship"]=="生" else
                  "adverse" if rel["relationship"]=="受克" else
                  "favorable" if rel["relationship"]=="受生" else "neutral")
        identity=("relation:%d:%d:%s"%(next(
            c["palace"] for c in (doc,yi,patient,hour,*([natal] if natal else []))
            if c["role"]==role),ill["palace"],rel["relationship"]))
        if rel["effect"] in ("limited","obstructed","unknown","resists_weak_attack"):
            add(identity,"pending",key+rel["relationship"]+"，但"+rel["why"],
                "palace mutual relation with qualitative strength",role)
        else:
            add(identity,polarity,key+rel["relationship"]+"；"+rel["why"],
                "palace mutual relation with qualitative strength",role)
    # Validated textual signifiers not included in independent evidence tally:
    # one unknown keyword-based source formation is not a verified vote.
    for item in matched_pairs:
        if item["source_state"]!="fully_verified_original_predicate":
            add("book:"+item["fact_id"],"pending",
                item["book_title"]+"：干配已命中，但完整原书判据未核实",
                item.get("source_sha256_internal"),"天地干格局")
    for item in extras:
        key="辅助宫"+str(extras.index(item)+1)+"对病宫"
        cmp=interactions[key]
        add("auxiliary:%s:%s"%(item["palace"],ill["palace"]),
            "pending" if cmp["effect"] in ("obstructed","limited","unknown") else
            "favorable" if cmp["relationship"] in ("克","受生") else
            "adverse" if cmp["relationship"] in ("生","受克") else "neutral",
            item["role"]+"与病宫"+cmp["relationship"]+"，"+cmp["why"],
            "role-bound actually supplied auxiliary",item["role"])
    good=[x for x in evidence.values() if x["direction"]=="favorable"]
    bad=[x for x in evidence.values() if x["direction"]=="adverse"]
    pending=[x for x in evidence.values() if x["direction"]=="pending"]
    is_confident=actor["confidence"] in (
         "source_case_specific","user_explicit_direction_verified_by_actual_chart")
    if not is_confident:
        state="unresolved";why="患者本人取用尚待原书条件核定，即使其他宫吉凶较多也不能直接下结论"
    elif not good and not bad:
        state="unresolved";why="尚无足够独立已核证据"
    elif len(good)>len(bad):
        state="favorable";why="列出并去重后的有效吉证多于凶证，作为传统象意倾向"
    elif len(bad)>len(good):
        state="adverse";why="列出并去重后的有效凶证多于吉证，作为传统象意倾向"
    else:
        state="unresolved";why="有效吉凶依据数量相持，暂不强断"
    verdict={"state":state,"label":OUTCOME[state],"reason":why,
             "decisive_chain":"independent_evidence_majority" if state!="unresolved" else None,
             "no_numeric_health_score":True}
    return {"schema":"health_palace_sequence_review_1","macro":macro,
            "ordered_roles":[ill,doc,yi,patient,*([natal] if natal else []),hour,*extras],
            "interactions":interactions,"verdict":verdict,
            "evidence":{"favorable":good,"adverse":bad,"pending":pending,
                        "neutral":[x for x in evidence.values() if x["direction"]=="neutral"]},
            "counts":{"qualified_favorable":len(good),"qualified_adverse":len(bad),
                      "pending_conditions":len(pending)},
            "not_medical_outcome":True}


def format_sequence_sections(result,*,actor,chart):
    """Human Chinese explanation in explicit requested reasoning order."""
    roles=result["ordered_roles"]
    name=lambda r:r["role"]+"落"+r["name"]
    def facts(r):
        stars="、".join(x["star"]+"携"+x["stem"] for x in r["heaven"])
        tombs=(["天盘"+x["stem"]+x["branch"]+"墓" for x in r["sky_tombs"]]+
               ["地盘"+r["earth_stem"]+b+"墓" for b in r["earth_tombs"]])
        return ("，宫五行"+r["element"]+"，"+(stars+"，" if stars else "")+
                "八神"+str(r["deity"])+"，八门"+str(r["door"])+
                "（月令"+str(r["door_month_stage"] or "待核")+"），"+
                "宫位月令"+r["palace_month_stage"]+
                ("，本符号月令"+r["month_stage"] if r["month_stage"] else "")+
                "，天地盘长生："+ "；".join(
                    x["stem"]+":"+"/".join(z["branch"]+z["stage"] for z in x["life"])
                    for x in r["heaven"])+
                "；地盘"+r["earth_stem"]+":"+
                "/".join(z["branch"]+z["stage"] for z in r["earth_life"])+
                "；空亡"+("/".join(r["void_branches"]) if r["void_branches"] else "无")+
                "；"+("、".join(tombs) if tombs else "无入墓")+
                ("；六仪击刑"+"/".join(r["striking_stems"]) if r["striking_stems"] else "")+
                ("；门迫" if r["door_pressure"] else "；非门迫"))
    sections=[]
    def push(k,title,txt):sections.append({"id":k,"title":title,"text":txt})
    m=result["macro"]
    push("01_macro","先看伏吟反吟",
         "九星"+m["star"]+"、八门"+m["door"]+"；"+m["pace"]+
         "。先定全盘宏观动静，不直接据此判断病人康复或恶化。")
    ill,doc,yi,patient=roles[:4]
    t25=result["interactions"]["天芮星月令×星宫五行25格"]
    push("02_illness","天芮病宫",name(ill)+facts(ill)+
         "。以天芮星为起点，第"+str(t25["case_number"])+"格："+t25["category"]+
         "、天芮月令"+t25["star_month"]+"，传统象意「"+
         t25["traditional_title"]+"」；落宫月令"+t25["palace_month"]+
         "，作用条件："+t25["why"]+
         "。星宫关系是名义五行事实，此条不等于临床治疗或预后。")
    for number,title,record,k in (
        ("03","天心医生",doc,"天心宫对病宫"),
        ("04","乙奇医药",yi,"乙奇宫对病宫"),
        ("05","患者用神",patient,"患者宫对病宫"),
    ):
        comparison=result["interactions"][k]
        co=record["palace"]==ill["palace"]
        push(number+"_"+record["role"],title,name(record)+facts(record)+
             "。对天芮病宫："+comparison["relationship"]+
             "；"+comparison["why"]+"。"+
             ("与病宫同宫，代表存在干预/接触候选；弱象并非零作用。"
              if co and record["role"] in ("天心医生","乙奇医药") else ""))
    for i,record in enumerate(roles[4:],6):
        code="年命宫对病宫" if record["role"]=="患者年命" else (
             "时干宫对病宫" if record["role"]=="时干事体" else
             "辅助宫"+str(i-6 if "患者年命" not in [z["role"] for z in roles] else i-7)+"对病宫")
        cmp=result["interactions"].get(code)
        push(str(i).zfill(2)+"_"+record["role"],record["role"],
             name(record)+facts(record)+
             ("。对病宫："+cmp["relationship"]+"；"+cmp["why"] if cmp else "")+"。")
    counts=result["counts"]; v=result["verdict"]
    push("90_review","全部证据合断",
         v["label"]+"。"+v["reason"]+"。"+
         "逐宫列出、去重且条件合格的有利依据"+str(counts["qualified_favorable"])+
         "条、不利依据"+str(counts["qualified_adverse"])+
         "条，尚待原书条件核实"+str(counts["pending_conditions"])+"条。"+
         "不能把这些条目看作医疗健康分数或临床概率。")
    push("91_timing","时空及应期",
         "时支驿马"+HORSE[chart["hour_ganzhi"][1]]+
         "；空亡、伏反吟及可能冲墓须按实际地支六冲、填实和原书真/假空条件另验，"+
         "不能仅凭两宫相对或同一支就断有效冲墓、痊愈或病亡；不虚构应期。")
    return sections
