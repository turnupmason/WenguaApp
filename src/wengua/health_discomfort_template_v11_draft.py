"""Independent V11-style *research* template for health.discomfort.

Reads actual chart positions and V11 relationship selection but never calls
V8 severity scoring. The source book's two body maps are alternatives, while
non-book stem/door/deity hints are visibly unapproved candidates. No diagnosis,
release or iOS lock is authorized by this module.
"""
from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
from string import Formatter
from typing import Any, Mapping

from .health_discomfort_location_draft import (
    inspect_traditional_body_clues, load_traditional_location_candidates,
)
from .health_dynamic_v21 import bind_patient, _stem_cell
from .health_81_excel_catalog_vnext import for_real_palace
from .health_discomfort_inner_outer_v12_draft import inspect_priority
from .health_discomfort_detail_v13_draft import inspect_detail
from .health_discomfort_cross_text_v14_draft import inspect_cross_text_candidates
from .health_discomfort_255_v15 import match_location_inventory

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "data/templates/health_discomfort_v11/reading_template.json"
SCHEMA = "wengua_health_discomfort_v11_candidate_template_20261031"
SECTION_IDS = ("01_location", "02_tianrui", "03_comparison", "04_person",
               "05_review", "06_conclusion")
SLOTS = ("opening", "illness", "companion_found", "companion_absent",
         "secondary", "injury_same", "injury_other", "hour_known",
         "hour_missing", "patient", "auxiliary_none", "auxiliary_found",
         "review", "ending", "source_comparison")
PALACE_NAMES = {1:"坎一宫", 2:"坤二宫", 3:"震三宫", 4:"巽四宫",
                6:"乾六宫", 7:"兑七宫", 8:"艮八宫", 9:"离九宫"}
UNSAFE_HINTS = ("癌", "肿瘤", "炎症", "恶性", "死亡", "死症", "手术",
                "化疗", "病变", "增生", "囊肿", "出血", "压迫")
FEMALE_ONLY = ("输卵管","阴道","子宫","卵巢","女性")
MALE_ONLY = ("输精管","前列腺","睾丸","阴茎","男性")


def _sex_compatible(word: str, sex: str | None) -> bool:
    return (sex == "female" or not any(x in word for x in FEMALE_ONLY)) and (
            sex == "male" or not any(x in word for x in MALE_ONLY))


def _symbol_note(note: str) -> str:
    """Only symbolic, non-diagnostic short clues; preserve raw notes in source."""
    phrases = note.split("；",1)[0].replace("，","、").split("、")
    safe = [p.replace("候选","").strip() for p in phrases
            if p and not any(bad in p for bad in UNSAFE_HINTS)]
    return ("、".join(safe[:2]) if safe else "一般变化") + "之象"



@lru_cache(maxsize=1)
def template() -> dict[str, Any]:
    raw = json.loads(SOURCE.read_text(encoding="utf-8"))
    if (raw.get("schema") != SCHEMA or raw.get("topic_id") != "health.discomfort"
            or raw.get("status") != "research_draft_not_customer_approved"
            or tuple(raw.get("sections", ())) != SECTION_IDS
            or set(raw.get("titles", {})) != set(SECTION_IDS)
            or set(raw.get("macros", {})) != set(SLOTS)
            or any(v is not True for v in raw.get("guards", {}).values())):
        raise ValueError("Unapproved or incomplete discomfort template")
    for slot, phrase in raw["macros"].items():
        if not isinstance(phrase, str) or not phrase.strip():
            raise ValueError("Missing discomfort template phrase: " + slot)
        if any(field is not None and (not field or "." in field or "[" in field)
               for _, field, _, _ in Formatter().parse(phrase)):
            raise ValueError("Unsafe format placeholder: " + slot)
    return raw


def _say(slot: str, **facts: str) -> str:
    line = template()["macros"][slot]
    required = {field for _, field, _, _ in Formatter().parse(line) if field}
    if set(facts) != required:
        raise ValueError("Missing/extra discomfort source facts in " + slot)
    if any(not isinstance(facts[key], str) or not facts[key] for key in facts):
        raise ValueError("Unverified or empty discomfort source fact: " + slot)
    return line.format_map(facts)


def _readable(items: list[str], count: int = 3) -> str:
    return "、".join(items[:count])


def _stem_hint(chart_evidence: Mapping[str, Any], sex: str | None,
               sector: str) -> str:
    """Only align source-uncertain sky-stem hints with the chosen body side.

    A generic surface feature of a stem must not displace a source-backed
    internal branch (or vice versa), nor invent a diagnosis or patient sex.
    """
    if sector not in ("inner","outer"):
        raise ValueError("An actual selected traditional sector is required")
    candidates=chart_evidence["tianrui_stem_main_clues"]
    palace=str(chart_evidence["tianrui_palace"])
    body=(chart_evidence["internal_symbol_candidates"] if sector=="inner"
          else chart_evidence["surface_symbol_candidates"])
    raw=candidates.get("by_palace",{}).get(palace,[])
    filtered=[s for s in raw if _sex_compatible(s,sex)
              and not any(bad in s for bad in UNSAFE_HINTS)]
    # Literal overlap avoids importing unverified aliases, hidden anatomy,
    # or a generic organ/surface unrelated to this physical palace branch.
    matching=[s for s in filtered if any(s in x or x in s for x in body)]
    if matching:
        return _readable(matching,2)+"等与本宫表里对应的待核细部象"
    return "尚无与本宫所取表里位置一致的已核干宫细部象"


def compose_draft(*, chart: Mapping[str, Any], inquiry: Mapping[str, Any],
                  calendar: Mapping[str, Any]) -> dict[str, Any]:
    """Candidate prose only. No scoring, medical conclusion or public release.

    Explicitly reuse the V11 actor binder on the REAL nine-palace source chart,
    not V8 severity's post-void grade or a fictional patient/natal stem.
    """
    if not isinstance(inquiry, Mapping) or not isinstance(calendar, Mapping):
        raise ValueError("Actual inquiry and four-pillar context required")
    if inquiry.get("intent") != "discomfort":
        raise ValueError("Discomfort cannot masquerade as severity")
    evidence = inspect_traditional_body_clues(chart)
    actor = bind_patient(chart, dict(inquiry), dict(calendar))
    patient = actor["main_cell"]
    if patient is None or patient["palace"] not in PALACE_NAMES:
        raise ValueError("Actual selected V11 patient palace is mandatory")
    actual = chart["palaces"]
    ill_id = evidence["tianrui_palace"]
    ill = actual[str(ill_id)]
    injury_id = evidence["injury_door_palace_for_secondary_review"]
    injury = actual[str(injury_id)]
    if injury["door"] != "伤门":
        raise ValueError("Independent true injury-door palace was altered")
    hour_stem = chart["hour_ganzhi"][0]
    hour = _stem_cell(chart, hour_stem, source_ganzhi=chart["hour_ganzhi"])
    if hour is None or hour["palace"] not in PALACE_NAMES:
        raise ValueError("Actual hour-stem carrier palace is mandatory")
    location = inspect_priority(chart=chart,body=evidence,
                                patient_palace=patient["palace"],
                                hour_palace=hour["palace"],injury_palace=injury_id)
    details = inspect_detail(chart=chart,illness_palace=ill_id,
                             patient_cell=patient,location=location,
                             patient_sex=actor.get('resolved_sex'),
                             patient_age_group=inquiry.get('patient_age_group'))
    cross_text = inspect_cross_text_candidates(chart=chart,location=location)
    notes = load_traditional_location_candidates()
    inventory = match_location_inventory(illness_palace=ill_id, sector=location["sector"],
        sky_stem=evidence["tianrui_carried_stem"], door=ill["door"], deity=ill["deity"])
    surface, internal = (evidence["surface_symbol_candidates"],
                         evidence["internal_symbol_candidates"])
    if not surface or not internal:
        raise ValueError("Both real book body groups are required")
    chosen=location["focus_candidates"]
    other=location["alternative_candidates"]
    label=location["label"]
    conflicts=location["counterevidence"]
    counter_note=("同宫另见"+ "、".join(x["symbol"] for x in conflicts)
                  +"等不同表里倾向，属于待核反证，不能推翻首层内外盘。"
                  if conflicts else "本宫未见相反的门神携干表里候选。")
    palace_name = PALACE_NAMES[ill_id]
    stars = ill["heaven_stars"]
    actual_companion = next((s["carried_stem"] for s in stars
                             if s["star"] == "天禽星"), None)
    companion = (_say("companion_found", stem=actual_companion)
                 if actual_companion else _say("companion_absent"))
    formation_cell = ({**ill, "hosted_centre_earth_stem": actual["5"]["earth_stem"]}
                      if ill_id == 2 else ill)
    patterns = for_real_palace(formation_cell)
    if not patterns:
        raise ValueError("Missing real 81 formation for illness palace")
    names = "、".join(p["name"] for p in patterns)
    door, deity = ill["door"], ill["deity"]
    door_clue = _symbol_note(notes["doors"][door]["illness"])
    deity_clue = _symbol_note(notes["deities"][deity]["illness"])
    extra = sorted({c["palace"] for c in actor.get("extra_cells", [])
                    if c and c["palace"] in PALACE_NAMES
                    and c["palace"] != patient["palace"]})
    aux = (_say("auxiliary_found", palaces="、".join(PALACE_NAMES[p] for p in extra))
           if extra else _say("auxiliary_none"))
    sections = [
        {"id":"01_location", "title":template()["titles"]["01_location"],
         "text":_say("opening", illness_palace=palace_name,
                     chosen=_readable(chosen),other=_readable(other),sector=label,
                     region=details['anatomical_region_zh'],
                     opposite=location["opposite"])},
        {"id":"02_tianrui", "title":template()["titles"]["02_tianrui"],
         "text":_say("illness",door=door,deity=deity,door_clue=door_clue,
                     deity_clue=deity_clue,sky=evidence["tianrui_carried_stem"],
                     stem_clues=_stem_hint(evidence, actor.get('resolved_sex'),
                                            location["sector"]),companion=companion,
                     earth=location["actual_earth_stem"],
                     patterns=names)},
        {"id":"03_comparison", "title":template()["titles"]["03_comparison"],
         "text":_say("secondary",injury_palace=PALACE_NAMES[injury_id],
                     injury_note=_say("injury_same" if injury_id == ill_id else "injury_other"),
                     hour_stem=hour_stem,
                     hour_note=_say("hour_known",palace=PALACE_NAMES[hour["palace"]]))},
        {"id":"04_person", "title":template()["titles"]["04_person"],
         "text":_say("patient",person=actor["label"],role=actor["role_name"],
                     patient_palace=PALACE_NAMES[patient["palace"]],
                     patient_door=patient["door"],auxiliary=aux,
                     patient_door_note=_symbol_note(details['patient_door_meaning']))},
        {"id":"05_review", "title":template()["titles"]["05_review"],
         "text":_say("review",sector=label,counter_note=counter_note)},
        {"id":"06_conclusion", "title":template()["titles"]["06_conclusion"],
         "text":_say("ending",illness_palace=palace_name,
                     sector=label,focus_short=chosen[0],
                     caveat=("门神提示另有方向，仍不作为实病判断"
                             if conflicts else "本宫仍有多个部位类象，不能认定唯一器官"))},
    ]
    families = inventory["three_stem_families"]
    sections[1]["text"] += " " + _say("source_comparison",
        sky=evidence["tianrui_carried_stem"],
        qimen="、".join(families["qimen_secret_vol13"]),
        viscera="、".join(families["sanming_viscera"]),
        surface="、".join(families["sanming_body_surface"]))
    return {
        "schema":SCHEMA,"topic_id":"health.discomfort",
        "status":"research_draft_not_customer_approved",
        "sections":sections,
        "reading_text":"\n\n".join(s["title"]+"：\n"+s["text"] for s in sections),
        "audit":{
            "source_book":"shenqi",
            "source_lines":evidence["source_lines"],
            "tianrui_palace":ill_id,
            "surface_all":surface,"internal_all":internal,
            "external_stem_clues_status":evidence["external_notes_status"],
            "external_stem_raw":evidence["tianrui_stem_main_clues"],
            "81_pairs":patterns,"patient_role":actor["role_via"],
            "patient_palace":patient["palace"],
            "hour_palace":hour["palace"],"injury_palace":injury_id,
            "same_physical_injury_palace":injury_id==ill_id,
            "birth_year_used_only_if_provided":bool(inquiry.get("patient_birth_ganzhi") or
                                                    inquiry.get("subject_year_ganzhi") or
                                                    inquiry.get("patient_birth_stem")),
            "body_v13_detail":details,
            "v14_cross_text_research":cross_text,
            "v15_full_255_rule_inventory":inventory,
            "location_priority":location,
            "selected_body_candidates":chosen,
            "other_body_candidates":other,
            "inner_outer_selected":True,
            "symbolic_not_clinical":True,
            "v80_severity_score":None,"grade":None,"timing":None,
            "medical_diagnosis":None},
        "released":False,"ios_enabled":False,"locks_15_days":False,
    }
