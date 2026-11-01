"""V14 separately sourced location *candidate* combinations.

Matches only directly observed single Tianrui carrier and illness-palace door.
Two-stem expressions from workbook lack an ordered sky/earth column; they are
NOT executable until an individual source verifies the actual role/direction.
This layer supplies audit evidence only, never medical diagnosis or severity.
"""
from __future__ import annotations
from functools import lru_cache
from pathlib import Path
import json
from typing import Any, Mapping

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/"data/knowledge/health_discomfort/cross_text_16_location_candidates_v14_20261101.json"
SCHEMA="wengua_health_discomfort_v14_16_combinations_20261101"
EXPECTED={f"HLT-{i:04d}" for i in range(240,256)}
STEM_SOURCE=ROOT/"data/knowledge/health_discomfort/three_source_stem_variants_v14_20261101.json"

@lru_cache(maxsize=1)
def stem_source_variants() -> dict[str,Any]:
    """Retain parallel textual families; sharing a stem is NOT independent proof."""
    j=json.loads(STEM_SOURCE.read_text(encoding="utf8"))
    expected=set("甲乙丙丁戊己庚辛壬癸")
    families={"qimen_secret_vol13","sanming_viscera","sanming_body_surface"}
    if (j.get("schema")!="wengua_health_discomfort_stem_three_family_variants_v14_20261101"
        or j.get("status")!="research_only_not_public"
        or set(j.get("mapping",{}))!=expected
        or any(set(v)!=families for v in j["mapping"].values())
        or len(j.get("provenance",[]))!=3
        or not all(j.get("guard",{}).values())):
        raise ValueError("Source-specific ten-stem mapping is incomplete")
    return j


@lru_cache(maxsize=1)
def rules() -> dict[str,Any]:
    j=json.loads(SOURCE.read_text(encoding="utf8"))
    rows=j.get("rows",[])
    if (j.get("schema")!=SCHEMA or j.get("status")!="separate_cross_text_candidate_not_approved"
        or len(rows)!=16 or {x["id"] for x in rows}!=EXPECTED
        or any(x.get("status")!="candidate_not_authorized"
               or x.get("cannot_choose_unique_organ") is not True for x in rows)):
        raise ValueError("Unapproved or incomplete 16-site cross-text source")
    for x in rows:
        if x["palace"] not in (1,2,3,4,6,7,8,9):
            raise ValueError("Centre cannot be treated as a real illness-star palace")
        single=len(x["stem_tokens"])==1
        if (single!=(x["symbol_operator"]=="tianrui_carried_stem_only")
            or x["executable_research_only"]!=(
                single and len(x["door_symbols"])==1)):
            raise ValueError("Two-stem unknown order must never be auto matched")
    return j


def inspect_cross_text_candidates(*, chart:Mapping[str,Any],
                                  location:Mapping[str,Any],
                                  source_case_context:Mapping[str,Any]|None=None)->dict[str,Any]:
    """Return research matches, unresolved multi-stem rules and case leakage gate."""
    j=rules()
    ill=location.get("tianrui_palace")
    cells=chart.get("palaces")
    if (chart.get("school_id")!="shijia_zhuanpan"
        or chart.get("casting_variant")!="shenqi_book_explicit_bureau_v1"
        or type(ill)!=int or ill not in (1,2,3,4,6,7,8,9)
        or not isinstance(cells,dict)
        or set(cells)!={str(i) for i in range(1,10)}):
        raise ValueError("Actual nine-palace Tianrui board required")
    site=cells[str(ill)]
    tianrui=[x for x in site["heaven_stars"] if x["star"]=="天芮星"]
    if (len(tianrui)!=1
        or tianrui[0]["carried_stem"]!=location["actual_sky_stem"]
        or site["door"]!=location["illness_door"]
        or site["earth_stem"]!=location["actual_earth_stem"]):
        raise ValueError("Source-true ordered sky/earth facts mismatch")
    matched=[]
    unresolved=[]
    for row in j["rows"]:
        if row["palace"]!=ill:
            continue
        if not row["executable_research_only"]:
            unresolved.append({"id":row["id"],"reason":"ordered_stem_or_multiple_symbol_roles_not_verified"})
            continue
        if (row["stem_tokens"][0]==tianrui[0]["carried_stem"]
            and row["door_symbols"][0]==site["door"]):
            matched.append({"id":row["id"],"status":"research_only_cross_text",
                            "one_actual_palace":ill,
                            "one_symbol_identity":"tianrui:"+tianrui[0]["carried_stem"],
                            "body_candidates":row["body_candidates"],
                            "independent_confirmations":0,
                            "may_narrow_for_customer":False})
    if source_case_context is not None:
        if not isinstance(source_case_context,Mapping):
            raise ValueError("Known case context must be explicit")
        # No revealed outcome is consulted. Source case data must be held apart.
        if source_case_context.get("known_after_cast") is True:
            raise ValueError("Postcast answer must not be mixed into initial evidence")
    return {
        "schema":SCHEMA,"illness_palace":ill,"research_matches":matched,
        "unresolved_multi_stem_rules":unresolved,
        "primary_original_book_candidates":location["focus_candidates"],
        "physical_source_clusters":{
            "illness_location":f"tianrui:{ill}",
            "stem_role":f"tianrui_sky:{ill}:{tianrui[0]['carried_stem']}",
            "door_role":f"illness_door:{ill}:{site['door']}",
        },
        "source_scheme_variants_for_actual_sky_stem":
            stem_source_variants()["mapping"][tianrui[0]["carried_stem"]],
        "source_scheme_independent_counts":{
            "qimen_secret_vol13":0,"sanming_mingli_cross_system":0},
        "distinct_independent_confirmations":0,
        "directly_deduced_medical_organ":None,
        "historical_case_not_blind_test":True,
        "may_modify_frozen_v80":False,
        "released":False,
    }
