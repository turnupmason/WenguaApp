"""Cross-chapter *research* retrieval: symbols, stem pairs and grounded formulas.

No knowledge here is approved prediction or published interpretation.
Door+door / door+instrument layer binding remains unresolved and MUST NOT
silently match one visible door to a second imaginary door or stem.
"""
from __future__ import annotations
import json
import sqlite3

GUAS={1:("坎","水"),2:("坤","土"),3:("震","木"),4:("巽","木"),
      5:("中","土"),6:("乾","金"),7:("兑","金"),8:("艮","土"),9:("离","火")}
DOORS={"开":"金","休":"水","生":"土","伤":"木",
       "杜":"木","景":"火","死":"土","惊":"金"}
STAR_ELEMENT={"天蓬星":"水","天芮星":"土","天冲星":"木","天辅星":"木",
             "天禽星":"土","天心星":"金","天柱星":"金","天任星":"土","天英星":"火"}
GENERATES={"木":"火","火":"土","土":"金","金":"水","水":"木"}
CONTROLS={"木":"土","土":"水","水":"火","火":"金","金":"木"}

def door_palace_relation(door,palace):
    d=door[:-1] if isinstance(door,str) and door.endswith("门") else door
    if d not in DOORS or palace not in GUAS:raise ValueError("Invalid palace or door")
    if palace==5:
        return {"status":"blocked_middle_palace","reason":"五宫寄宫约定未审核"}
    de,pe=DOORS[d],GUAS[palace][1]
    if de==pe:kind="比和"
    elif CONTROLS[de]==pe:kind="迫"
    elif CONTROLS[pe]==de:kind="制"
    elif GENERATES[de]==pe:kind="和"
    elif GENERATES[pe]==de:kind="义"
    else:raise AssertionError("Five-element relation inconsistent")
    return {"status":"calculated_from_source_draft","kind":kind,
            "door_element":de,"palace_element":pe,
            "source_concept_id":"principle:door_palace_elements"}

def nine_star_month_status(star,month_element):
    """九星旺相休囚废 ≠ earthly 五行旺相休囚死; requires known month element."""
    if star not in STAR_ELEMENT or month_element not in GENERATES:
        raise ValueError("Known star and season's wuxing required")
    el=STAR_ELEMENT[star]
    if GENERATES[el]==month_element:status="旺"
    elif el==month_element:status="相"
    elif GENERATES[month_element]==el:status="废"
    elif CONTROLS[el]==month_element:status="休"
    elif CONTROLS[month_element]==el:status="囚"
    else:raise AssertionError("Five element relation invalid")
    return {"status":"calculated_from_source_draft","value":status,
            "source_concept_id":"principle:star_month_formula"}

def chart_concepts(chart):
    if (not isinstance(chart,dict) or chart.get("school_id")!="shijia_zhuanpan"
            or chart.get("status") not in ("source_text_consistency_only","engine_verified")):
        raise ValueError("Source-limited chart required; never invent a chart")
    result=[]
    for palace,cell in (chart.get("palaces") or {}).items():
        p=int(palace)
        if p not in GUAS or cell.get("palace")!=p or cell.get("gua")!=GUAS[p][0]:
            raise ValueError("Inconsistent palace+trigram")
        if not cell.get("earth_stem"):raise ValueError("Missing ground stem")
        ids=[f'trigram:{cell["gua"]}',f'stem:{cell["earth_stem"]}']
        if cell.get("door"):
            ids.append(f'door:{cell["door"][:-1]}')
            result.append({"palace":p,"kind":"door_palace",
                           "fact":door_palace_relation(cell["door"],p)})
        if cell.get("deity"):ids.append(f'deity:{cell["deity"]}')
        for hs in cell.get("heaven_stars",()):
            if not hs.get("star") or not hs.get("carried_stem"):
                raise ValueError("Incomplete heaven star entry")
            ids.extend([f'star:{hs["star"]}',f'stem:{hs["carried_stem"]}',
                        f'heaven_over_earth:{hs["carried_stem"]}:{cell["earth_stem"]}'])
        result.extend({"palace":p,"kind":"source_concept","concept_id":k} for k in ids)
    return result

def lookup_concept(db_path,concept_id,*,include_original=False):
    if not isinstance(concept_id,str) or not concept_id or len(concept_id)>128:
        raise ValueError("Invalid concept id")
    with sqlite3.connect(db_path) as db:
        rows=db.execute("""SELECT chapter_key,kind,relation,source_start_line,
            source_end_line,metadata_json,original_excerpt,review_status
            FROM semantic_assertions WHERE concept_id=? ORDER BY chapter_key,source_start_line""",
            (concept_id,)).fetchall()
    return [{"chapter_key":a,"kind":b,"relation":c,"source_lines":[d,e],
             "metadata":json.loads(f),"local_source_text":g if include_original else None,
             "review_status":h} for a,b,c,d,e,f,g,h in rows]

def gather_chart_research_context(db_path,chart):
    """Connect old Chapter-1 casting result to Chapter-4/5 interpreted identities.

    Returns individual *draft* evidence and source pointers, no unconditional
    ancient divination conclusion; requiring a source-verified calendar remains.
    """
    facts=chart_concepts(chart)
    indexed={}
    for concept in set(x["concept_id"] for x in facts if "concept_id" in x):
        indexed[concept]=lookup_concept(db_path,concept)
    return {"status":"draft_source_context_not_approved_divination",
            "school_id":chart["school_id"],
            "matches":[{**x,"evidence":indexed[x["concept_id"]]}
                       for x in facts if "concept_id" in x],
            "door_palace_facts":[x for x in facts if x["kind"]=="door_palace"],
            "missing_ids":[k for k,v in sorted(indexed.items()) if not v],
            "limitations":["source_text_consistency_only is not engine_verified",
              "door-over-door and door-over-stem require independently defined layers",
              "complex 吉凶格 require individually vetted conditions and conflict management",
              "all current semantic records remain draft and cannot be published as readings"]}
