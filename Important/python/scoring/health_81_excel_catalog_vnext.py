"""User-supplied Excel 81 ordered (heaven, earth) patterns: current authority.

Editable live source:
data/knowledge/health_81_excel_20261025/81_pairs.tsv

The two other archival catalogs remain untouched. This user Excel table gives
the outcome of EVERY real 9x9 pair. An excerpt mentioning a door or a remedy
is not an additional, silently unsatisfied condition on whether the entry
exists or whether its declared 吉/凶 is known.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/"data/knowledge/health_81_excel_20261025/81_pairs.tsv"
HEADERS=("天盘干","地盘干","格局名称","吉凶","古文（摘句）","古诀大意","天地盘取象")
STEMS="戊乙丙丁己庚辛壬癸"
VERSION="health_81_excel_20261025_authoritative_v1"


@lru_cache(maxsize=1)
def catalog():
    """Strict 81/81 coverage, fail closed if manual TSV edits break a cell."""
    text=SOURCE.read_text(encoding="utf-8-sig").splitlines()
    if not text or tuple(text[0].split("|"))!=HEADERS:
        raise ValueError("Latest Excel 81 source headers invalid")
    rows={}
    for line_index,line in enumerate(text[1:],start=2):
        if not line.strip():continue
        values=line.split("|")
        if len(values)!=7 or any(not v.strip() for v in values):
            raise ValueError("Incomplete Excel source at line "+str(line_index))
        h,e,name,polarity,old,meaning,imagery=values
        if h not in STEMS or e not in STEMS or polarity not in ("吉","凶"):
            raise ValueError("Bad pair/polarity at line "+str(line_index))
        key=h+"/"+e
        if key in rows:raise ValueError("Duplicate Excel pair "+key)
        rows[key]={
            "key":key,"heaven":h,"earth":e,"name":name,
            "polarity":polarity,"classical_text":old,
            "classical_meaning":meaning,"imagery":imagery,
            "source_excel_row":line_index+3,
            "source":"奇门遁甲_天地盘81格_古文吉凶化解取象.xlsx",
            "source_sheet":"81格完整表",
            "version":VERSION,
        }
    if len(rows)!=81 or set(rows)!={a+"/"+b for a in STEMS for b in STEMS}:
        raise ValueError("Latest Excel source must cover 81 unique pairs")
    return rows


def lookup_pair(heaven,earth):
    """Exact directed actual sky/earth pair, never fuzzy matched by title."""
    key=heaven+"/"+earth
    try:return dict(catalog()[key])
    except KeyError as exc:raise ValueError("No original 81 stem pair "+key) from exc


def for_real_palace(cell):
    """Centre earth permanently hosted at Kun-2; never invent a sky star."""
    earth=cell.get("earth_stem")
    if not earth or cell["palace"]==5:return []
    stars=[s for s in cell["heaven_stars"] if s.get("carried_stem") in STEMS]
    if not stars:return []
    if cell["palace"]==2:
        centre=cell.get("hosted_centre_earth_stem")
        if not isinstance(centre,str) or centre not in STEMS:
            raise ValueError("Kun 2 lacks real centre-earth host")
        if len(stars)==1:
            real=[(stars[0],earth),(stars[0],centre)]
        elif len(stars)==2 and {s["star"] for s in stars}=={"天芮星","天禽星"}:
            real=[(s,centre if s["star"]=="天禽星" else earth) for s in stars]
        else:raise ValueError("Unverified Kun sky carriers")
    else:
        real=[(s,earth) for s in stars]
    return [dict(lookup_pair(s["carried_stem"],bottom),
                 star=s["star"],palace=cell["palace"],can_vote=True,
                 source_state="user_excel_explicit_81",
                 applicability="user_excel_heaven_earth_pair",source_conditions=(),
                 explanation="真实天盘干与固定宫地盘干对应原81格",
                 fact_id="user_excel81:"+str(cell["palace"])+":"+s["carried_stem"]+"/"+bottom)
            for s,bottom in real]


def authoritative_score_source(heaven,earth):
    """Small compatibility adapter for active signed current palace model.

    Generic catalog records always declare polarity. Do not call older
    unresolved book phrase gates to obtain the user's known 81 classifications.
    """
    x=lookup_pair(heaven,earth)
    return {
        "key":x["key"],"top":heaven,"bottom":earth,
        "user_rows":[{"title":x["name"],"polarity":x["polarity"],
                      "classical_text":x["classical_text"],
                      "classical_meaning":x["classical_meaning"],
                      "imagery":x["imagery"]}],
        "status":"user_excel_exact_81",
        "polarity":x["polarity"],
        "baseline":3 if x["polarity"]=="吉" else -3,
        "conditional":False,
        "reason":"用户Excel81格明确吉凶及四项解释，实际天地干吻合即查出原表",
        "source_version":VERSION,"excel_original":x,
        "historical_extra_gates_not_used":True,
        "not_clinical":True,
    }
