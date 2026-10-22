"""V3.0: user-confirmed illness-method curriculum, no text generation or network.

Extends V2.9 *without* rewriting previously sealed v27/v28/v29 predictions.
Only proven actual palace conditions may add content. Indexed but unsupported
book rules remain searchable curriculum, not invented outcomes.
"""
from __future__ import annotations
from pathlib import Path
import json
from .health_severity_v29 import analyze_health_severity_v29
from .health_severity_v27 import _directed
from .health_severity_v26 import _direction
from .health_severity_v22 import _find_star, _find_heaven_stem, _palace, _yes_void, FORBIDDEN_CUSTOMER
from .health_dynamic_v21 import bind_patient
from .health_severity_v28 import related_special_facts
from .marriage_runtime import ELEMENTS,element_relation

ROOT=Path(__file__).resolve().parents[2]
TEMPLATE=ROOT/"data/knowledge/phrase_library/health_v30/severity_fixed_template.json"
CURRICULUM=ROOT/"data/knowledge/phrase_library/health_v30/user_20261022_disease_curriculum.json"
PAIRS=ROOT/"data/knowledge/phrase_library/health_v30/user_20261022_pair_catalog.json"
FORMAT_EXTENSIONS=("03_illness","05_patient","08_hour","09_hazards","10_pace","11_final")

def _load(path):
    return json.loads(path.read_text("utf8"))

def _exact_stems(cell):
    return [s["carried_stem"] for s in cell["heaven_stars"]]

def _pair_matches(chart,cell,role,catalog):
    """Match ONLY literal heaven-over-earth two-stem conditions.

    The book can interpret the same formation differently for illness and
    patient. Contradictory source readings are NOT resolved to suit a label.
    """
    stem=cell["earth_stem"]
    matches=[]
    for h in ([next(x["carried_stem"] for x in cell["heaven_stars"] if x["star"]=="天芮星")] if role=="illness" else _exact_stems(cell)[:1]):
        for pattern in catalog["pairs"]:
            if pattern["heaven"]!=h or pattern["earth"]!=stem:
                continue
            mode=pattern["mode"]
            if mode=="needs_source":
                continue
            if role=="illness":
                if mode=="ill_adverse":
                    phrase="此宫"+pattern["name"]+"，传统病象偏不利"
                elif mode=="ill_favorable":
                    phrase="此宫"+pattern["name"]+"，传统病象有转缓之意"
                elif mode=="duration":
                    phrase="此宫"+pattern["name"]+"，新病与久病须分别判断"
                elif mode=="role_dependent":
                    phrase="此宫"+pattern["name"]+"，病象与患者用神取意不同"
                elif mode=="conflict":
                    phrase="此宫"+pattern["name"]+"，吉凶须结合患者及门迫刑墓同断"
                else:
                    continue
            elif role=="patient":
                if mode=="role_dependent":
                    phrase="患者宫"+pattern["name"]+"，应按人物宫而非病宫取断"
                elif mode=="duration":
                    phrase="患者宫"+pattern["name"]+"，需结合已知新旧病程"
                elif mode in ("ill_adverse","ill_favorable"):
                    phrase="患者宫临"+pattern["name"]+"，仍以患者宫旺衰及生克为主"
                else:
                    continue
            else:
                continue
            matches.append({"heaven":h,"earth":stem,"name":pattern["name"],
                            "meaning":phrase,"source_id":pattern["id"],
                            "role":role,"source_status":"user_supplied_rule"})
    # do not repeat original stem formation prose already rendered
    return matches

def _composites(ill,person):
    """Only fully matched actual chart facts; never infer another palace."""
    known=[]
    for who,cell in (("病宫",ill),("患者宫",person)):
        top=_exact_stems(cell)
        if cell["door"] in ("开门","休门","生门") and "乙" in top and cell["earth_stem"]=="己":
            known.append({"role":who,"name":"地遁",
                          "text":who+"见地遁，按"+("病象深藏" if who=="病宫" else "患者宫偏不利")+"取象"})
        if cell["door"]=="死门" and cell["deity"]=="九地" and ({"丁","己","癸"} & set(top)):
            known.append({"role":who,"name":"鬼假","text":who+"临鬼假，传统不利象加重"})
        if cell["door"]=="休门" and cell["deity"]=="太阴" and "丁" in top:
            known.append({"role":who,"name":"人遁",
                          "text":who+"临人遁，测病不能只按吉门取吉"})
        if cell["door"]=="惊门" and cell["deity"]=="九天" and "壬" in top:
            known.append({"role":who,"name":"人假","text":who+"临人假，传统不利象加重"})
    return known

def _duration_condition(chart,person,ill,duration,fy,actual_factors):
    """New/chronic claims ONLY if provided, never infer from a life-stage label."""
    if duration not in (None,"new","chronic"):
        raise ValueError("Illness duration must be new/chronic or unknown")
    if duration is None:return ""
    notes=[]
    state="新病" if duration=="new" else "久病"
    if _yes_void(chart,person):
        notes.append(state+"用神逢空，传统"+("有病象转缓之意" if duration=="new" else "偏不利"))
    if "反吟" in (fy["star"],fy["door"]):
        notes.append(state+"遇反吟，传统"+("有转愈之象" if duration=="new" else "偏不利"))
    if "伏吟" in (fy["star"],fy["door"]):
        notes.append("伏吟主慢，传统病程易拖延")
    return "；".join(notes)

def _timing_candidates(chart,fy,special):
    notes=[]
    if "伏吟" in (fy["star"],fy["door"]):
        notes.append("伏吟逢冲为传统应期候选")
    if "反吟" in (fy["star"],fy["door"]):
        notes.append("反吟逢合为传统应期候选")
    if any(f["kind"]=="入墓地" for f in special):
        notes.append("已见入墓地，出墓冲墓为候选，仍须分墓库")
    if any(f["kind"]=="六仪击刑" for f in special):
        notes.append("已见六仪击刑，逢冲后合为候选")
    return "；".join(notes)

def analyze_health_severity_v30(*,chart,inquiry,calendar=None,db_path=None):
    """Pure Python fixed template+checked palace data, not clinical advice."""
    if not isinstance(inquiry,dict) or inquiry.get("intent")!="severity":
        raise ValueError("Other four health intents still unreviewed")
    base=analyze_health_severity_v29(chart=chart,inquiry=inquiry,calendar=calendar,db_path=db_path)
    template=_load(TEMPLATE)
    curriculum=_load(CURRICULUM)
    pair_catalog=_load(PAIRS)
    if len(template["sections"])!=11 or len(pair_catalog["pairs"])<35:
        raise ValueError("Missing full user-supplied disease curriculum")
    ill,_=_find_star(chart,"天芮星")
    person=bind_patient(chart,inquiry,calendar)["main_cell"]
    if person is None:
        raise ValueError("Patient role not verified, cannot fabricate individual prognosis")
    event=_find_heaven_stem(chart,chart["hour_ganzhi"][0])
    if event is None:
        raise ValueError("Hour stem not present on source chart")
    from .health_severity_v25 import fuyin_fanyin_facts
    symptoms=_pair_matches(chart,ill,"illness",pair_catalog)
    # Avoid reasserting the same named pair already reported in the V2.9 illness palace.
    illness_earlier=next(x["text"] for x in base["sections"] if x["id"]=="03_illness")
    symptoms=[x for x in symptoms if x["name"] not in illness_earlier]
    patient_combos=_pair_matches(chart,person,"patient",pair_catalog)
    composites=_composites(ill,person)
    actual=base["audit"]["actual_tomb_punishment_v28"]
    special={name:[f for f in actual if f["kind"]==name] for name in ("六仪击刑","入墓地")}
    fy=fuyin_fanyin_facts(chart)
    duration=inquiry.get("illness_duration")
    duration_phrase=_duration_condition(chart,person,ill,duration,fy,actual)
    # Ground-palace Tianrui is the stable home association, never a fabricated
    # extra Tianrui star on the earth plate.
    home=chart["palaces"]["2"]
    kun_reference="" if ill["palace"]==2 else "present"
    if kun_reference:
        rel=element_relation(ELEMENTS[home["palace"]],ELEMENTS[ill["palace"]])
        rel_words={"克":"本位宫制病宫","受克":"本位宫受病宫克",
                   "生":"本位宫生扶病宫","受生":"本位宫得病宫生扶",
                   "比和":"本位宫与病宫同气"}[rel]
        kun_reference=("另参坤二宫天芮本位，临"+home["door"]+"、"+home["deity"]+
                       "，地盘"+home["earth_stem"]+"；"+rel_words+"。")
    extras={
       "03_illness":{
           "kun2_reference":kun_reference,
           "illness_pair_extension":("；".join(x["meaning"] for x in symptoms)+"。") if symptoms else "",
           "verified_composite":("；".join(x["text"] for x in composites if x["role"]=="病宫")+"。")
                                 if any(x["role"]=="病宫" for x in composites) else ""},
       "05_patient":{
           "patient_pair_extension":("；".join(x["meaning"] for x in patient_combos)+"。") if patient_combos else "",
           "patient_evidence_priority":"患者宫是病情传统吉凶的重要依据，须与病星、医药及年命共同取断。"
       },
       "08_hour":{
           "hour_vs_person":"时干主病情现状与发展；"+_directed(event,person,"hour").replace("病宫","患者宫")+"。"
       },
       "09_hazards":{
           "more_verified_hazards":("；".join(x["text"] for x in composites if x["role"]=="患者宫")+"。")
                                   if any(x["role"]=="患者宫" for x in composites) else ""
       },
       "10_pace":{
           "duration_and_timing_condition":("；".join(x for x in (
             duration_phrase,_timing_candidates(chart,fy,actual)) if x)+"。")
             if duration_phrase or _timing_candidates(chart,fy,actual) else ""
       },
       "11_final":{
           "patient_first_balance":"患者用神"+_palace(person)+"，"+_direction(person,ill,"患者宫","病宫")+"；以患者状态权衡病星。"
       }
    }
    originals={x["id"]:x for x in base["sections"]}
    rendered=[]
    for s in template["sections"]:
        if s["id"] not in originals:continue
        if s["id"] in FORMAT_EXTENSIONS:
            slots={"legacy":originals[s["id"]]["text"].rstrip("。")+"。"}
            slots.update(extras[s["id"]])
            text=s["format"].format_map(slots)
        else:text=originals[s["id"]]["text"]
        # preserve legacy no-GPT customer constraints.
        forbidden=tuple(FORBIDDEN_CUSTOMER)+tuple(template["validation"]["no_tokens"])
        if any(x in text for x in forbidden):
            raise ValueError("Forbidden user-facing phrase in "+s["id"])
        if "{" in text or "}" in text or "门门迫" in text or "与与" in text:
            raise ValueError("Duplicate or unresolved customer phrase "+s["id"])
        rendered.append({**originals[s["id"]],"text":text})
    if len(rendered)!=len(base["sections"]):
        raise ValueError("Optional patient sex rendering missing/duplicated")
    audit={**base["audit"],"v30_user_curriculum_source":"user_message_2026-10-22",
        "v30_rules":{ "illness_pair_matches":symptoms,"patient_pair_matches":patient_combos,
                     "composites":composites,"actual_special_conditions":actual,
                     "course":"new/chronic" if duration else "unknown",
                     "ground_kun_referenced":bool(kun_reference),
                     "timing_candidates_only":True},
        "curriculum_completeness":{
           "pair_rules_indexed":len(pair_catalog["pairs"]),
           "composites_indexed":len(pair_catalog["composites"]),
           "remaining_staged_rules":curriculum["statuses"]["indexed_not_executable"]},
        "historical_v27_v28_v29_sealed_readouts_unchanged":True,
        "runtime_gpt_calls":0,"runtime_network_calls":0,
        "user_review_status":"pending","actual_medical_severity":None}
    return {**base,"schema":template["schema"],
       "reading_text":"\n\n".join(x["title"]+"："+x["text"] for x in rendered),
       "sections":rendered,"audit":audit,"user_accepted":False}
