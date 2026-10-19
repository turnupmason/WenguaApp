"""Per-palace review of Shenqi source-derived, NOT-APPROVED formation variants."""
from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
DEFAULT_VARIANTS=ROOT/"data/knowledge/shenqi/shijia_judgments_ch05/formation_variants_draft.json"
FIELDS=frozenset(("heaven_stem","earth_stem","door","deity","palace"))

def _test(condition,row):
    if not isinstance(condition,dict) or set(condition) - {"field","op","value","values"}:
        raise ValueError("Malformed formation condition")
    field=condition.get("field")
    if field not in FIELDS or field not in row:
        return False
    if condition.get("op")=="eq" and set(condition)=={"field","op","value"}:
        return row[field]==condition["value"]
    if condition.get("op")=="in" and set(condition)=={"field","op","values"}:
        vs=condition["values"]
        if not isinstance(vs,list) or not vs or any(not isinstance(x,(str,int)) for x in vs):
            raise ValueError("Invalid OR membership")
        return row[field] in vs
    raise ValueError("Unknown condition operation")

def _matched(ast,row):
    if not isinstance(ast,list):
        raise ValueError("All-of must be an array")
    return all(_test(c,row) for c in ast)

def evaluate_candidates(chart,definitions=DEFAULT_VARIANTS):
    """Never infer fields from other palaces or match unknown-layer relationships.

    These are draft evidence candidates; their matching is NOT professional
    applicability or proven prediction. A human must review conflicts,
    negative evidence, timing, method variants and source chapter before use.
    """
    if (not isinstance(chart,dict) or chart.get("school_id")!="shijia_zhuanpan"
            or chart.get("status") not in ("source_text_consistency_only","engine_verified")):
        raise ValueError("No independently sourced chart facts")
    obj=json.loads(Path(definitions).read_text(encoding="utf-8"))
    if obj.get("schema")!="wengua_conditional_formation_primitive_v1":
        raise ValueError("Unknown formation-rule schema")
    candidates=[]
    for k,cell in (chart.get("palaces") or {}).items():
        palace=int(k)
        if palace<1 or palace>9 or cell.get("palace")!=palace:
            raise ValueError("Palace label mismatch")
        if palace==5:continue
        for star in cell.get("heaven_stars",()):
            row={"palace":palace,"heaven_stem":star["carried_stem"],
                 "earth_stem":cell.get("earth_stem"),
                 "door":(cell.get("door") or "").removesuffix("门"),
                 "deity":cell.get("deity")}
            for rule in obj.get("variants",()):
                if rule.get("review_status")!="draft" or rule.get("auto_approved") is not False:
                    raise ValueError("Rule release status requires explicit human review")
                all_of=rule.get("preconditions",[])
                or_of=rule.get("alternatives",[])
                if _matched(all_of,row) and (not or_of or any(_matched(group,row) for group in or_of)):
                    candidates.append({
                        "palace":palace,"star":star["star"],"variant_id":rule["variant_id"],
                        "formation_name":rule["formation_name"],
                        "source":{"book":"神奇之门","chapter":5,"line":rule["source_line"]},
                        "matched_per_palace_facts":row,
                        "review_status":"candidate_match_only_not_approved",
                        "applicable_prediction":"blocked_until_source_and_counterevidence_review",
                        "important_note":rule.get("notes","")})
    return {"status":"draft_review_candidates_only","matches":candidates,
            "do_not_publish_as_prediction":True,"needs_professional_review":True}
