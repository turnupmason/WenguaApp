"""Full 255-entry source inventory for traditional health.discomfort reading.

Never uses V8 severity scores; text labels are historical analogies, not
clinical illness localization. A/B/C/D/E remain separate, unverified variants
and disclosed case outcomes never contribute to the customer prediction.
"""
from __future__ import annotations
from functools import lru_cache
from pathlib import Path
import json
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[2]
RULES = ROOT / "data/knowledge/health_discomfort/complete_255_rules_v15_20261101.json"
STEMS = ROOT / "data/knowledge/health_discomfort/three_source_stem_variants_v14_20261101.json"
PALACE = {1:"坎一",2:"坤二",3:"震三",4:"巽四",6:"乾六",7:"兑七",8:"艮八",9:"离九"}
LABEL = {"inner":("内","体内"),"outer":("外","体表")}
SOURCE_FAMILY = {"秘笈疾病象":"qimen_secret_vol13",
                 "三命通会脏腑":"sanming_viscera",
                 "三命通会体表":"sanming_body_surface"}

@lru_cache(maxsize=1)
def full_rules() -> dict[str,Any]:
    doc=json.loads(RULES.read_text(encoding="utf8"))
    rows=doc.get("rules",[])
    expected={f"HLT-{n:04d}" for n in range(1,256)}
    if len(rows)!=255 or {r.get("ID") for r in rows}!=expected or len(doc.get("cases",[]))!=12 or len(doc.get("conflicts",[]))!=20:
        raise ValueError("Full 255-rule provenance and historical counterexamples required")
    if any(r.get("上下干方向") for r in rows):
        raise ValueError("The original workbook's unverified sky/earth order has changed")
    return doc

@lru_cache(maxsize=1)
def stem_variants() -> dict[str,Any]:
    doc=json.loads(STEMS.read_text(encoding="utf8"))
    if len(doc.get("mapping",{}))!=10 or set(doc["mapping"])!=set("甲乙丙丁戊己庚辛壬癸"):
        raise ValueError("Three stem families incomplete")
    return doc

def match_location_inventory(*,illness_palace:int,sector:str,sky_stem:str,door:str,deity:str) -> dict[str,Any]:
    """Match only source predicates actually known from a real Tianrui palace.

    All 255 source entries are accounted for; unsafe or underspecified rules
    stay traceable but cannot narrow the person's actual body site.
    """
    if illness_palace not in PALACE or sector not in LABEL or sky_stem not in stem_variants()["mapping"]:
        raise ValueError("Need real physical Tianrui, actual dun and carried stem")
    if door not in ("开门","休门","生门","伤门","杜门","景门","死门","惊门"):
        raise ValueError("Need actual illness door")
    if deity not in ("值符","螣蛇","太阴","六合","白虎","玄武","九地","九天"):
        raise ValueError("Need actual illness deity")
    doc=full_rules()
    matched=[]
    separated=[]
    ignored=[]
    for rule in doc["rules"]:
        rid=rule["ID"]
        cat=rule["类别"]
        tier=rule["证据级别"][0]
        combo=rule["符号组合"]
        subtype=rule["子类"]
        ok=False
        if cat=="九宫定位":
            if subtype in ("秘笈大全-外","秘笈大全-内","神奇之门-体表","神奇之门-体内"):
                expected=("外" if sector=="outer" else "内")
                side_ok=(subtype.endswith(expected) or
                         (sector=="inner" and subtype.endswith("体内")) or
                         (sector=="outer" and subtype.endswith("体表")))
                ok=combo.startswith(PALACE[illness_palace]+"·") and side_ok
            elif subtype=="八卦取象":
                ok=combo==PALACE[illness_palace]
        elif cat=="十干定位":
            ok=(combo==sky_stem and subtype in SOURCE_FAMILY)
        elif cat=="八门病象" and tier=="A":
            ok=combo==door
        elif cat=="八神病象" and tier=="A":
            ok=deity in combo.split("／")
        elif cat=="九宫病象" and tier=="A":
            # Context only, NOT a candidate organ and NEVER a central role.
            ok=combo==PALACE[illness_palace]
        elif cat=="宫门组合" and tier=="A":
            # Simple physical palace+door allowed only when no unverified
            # month or 五行 strength predicate is required.
            ok=(combo.startswith(PALACE[illness_palace]+"宫＋"+door)
                and "旺" not in combo and "衰" not in combo)
        if ok and tier=="A":
            matched.append({"id":rid,"category":cat,"source":rule["来源"],"note":rule["古籍象意或候选"],
                            "status":"historic_source_context_not_medical"})
        elif ok and tier=="D":
            separated.append({"id":rid,"source":rule["来源"],"note":rule["古籍象意或候选"],
                              "status":"cross_system_comparison_not_confirmation"})
        else:
            ignored.append(rid)
    if len(matched)+len(separated)+len(ignored)!=255:
        raise AssertionError("Must account for all 255 unique rules")
    return {"total":255,"matched_qimen_text":matched,"cross_system_comparisons":separated,
            "inapplicable_or_unverified_ids":ignored,
            "matched_ids":[x["id"] for x in matched+separated],
            "three_stem_families":stem_variants()["mapping"][sky_stem],
            "historical_cases_kept_separate":len(doc["cases"]),
            "conflicts_preserved":len(doc["conflicts"]),
            "clinical_diagnosis":None,"severity_score":None}

def source_comparison_phrase(evidence:Mapping[str,Any],*,sky_stem:str)->str:
    """Full provenance is in audit; patient text avoids claiming an organ."""
    variants=evidence["three_stem_families"]
    q="、".join(variants["qimen_secret_vol13"])
    v="、".join(variants["sanming_viscera"])
    s="、".join(variants["sanming_body_surface"])
    return (f"天芮携{sky_stem}，另查不同原书的传统象意：《奇门遁甲秘笈大全》作{q}；"
            f"《三命通会》脏腑歌作{v}、体表歌作{s}。"
            "后二者属同一命理文本家族，只作异说对照，不当作两条独立证据，也不能凭此确定器官。")
