"""Export the complete source-computed five-by-five Tianrui research matrix.

One actual palace for each directional relation, five REAL original month-law
states; deterministic, excludes made-up cancer/drug/medical predictions.
Run: python -m scripts.preview_health_tianrui_25 artifacts/tianrui_25.json
"""
from __future__ import annotations
import json
import sys
from pathlib import Path
from src.wengua.health_tianrui_25_matrix import (
    RELATION_KEYS,MONTH_STAGES,inspect_tianrui_25,validate_matrix)
from src.wengua.health_severity_template import MONTH_ELEMENTS
from src.wengua.health_palace_sequence_vnext import element_month_stage
from src.wengua.semantic_lookup import STAR_ELEMENT,nine_star_month_status
from src.wengua.marriage_runtime import ELEMENTS

BRANCH_FOR_STAGE={"旺":"酉","相":"辰","休":"子","囚":"卯","废":"午"}
PALACE_FOR_RELATION={"宫克星":3,"星生宫":6,"星克宫":1,
                     "宫生星":9,"宫星比和":2}

def generate():
    validate_matrix()
    result=[]
    for relation in RELATION_KEYS:
        for month in MONTH_STAGES:
            branch=BRANCH_FOR_STAGE[month]
            palace=PALACE_FOR_RELATION[relation]
            month_element=MONTH_ELEMENTS[branch]
            source_stage=nine_star_month_status("天芮星",month_element)["value"]
            assert source_stage==month
            info=inspect_tianrui_25(
                star_month=source_stage,
                star_element=STAR_ELEMENT["天芮星"],
                palace_element=ELEMENTS[palace],
                palace_month=element_month_stage(ELEMENTS[palace],month_element))
            assert info["category"]==relation
            result.append({"source_actual_lunar_month_branch":branch,
                           "month_element":month_element,
                           "actual_nine_palace_number":palace,
                           **info})
    assert len(result)==len(set(x["case_id"] for x in result))==25
    return {"schema":"tianrui_25_original_month_and_palace_calculations",
            "source":"user_proposed_25_analogies_review_not_book_verified",
            "not_a_real_calendar_cast":True,
            "not_a_medical_prediction":True,
            "cases":result}

def main():
    report=generate()
    dest=Path(sys.argv[1]) if len(sys.argv)>1 else Path("/tmp/tianrui_25.json")
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    for t in report["cases"]:
        print(f'{t["case_number"]:02d} | {t["category"]:4} | 天芮月令{t["star_month"]} | '
              f'落宫{t["actual_nine_palace_number"]}宫月令{t["palace_month"]} | '
              f'{t["traditional_title"]} | {t["effectiveness"]} | '
              f'{t["eligible_evidence_direction"]}')
    print("PASS 25/25 REAL MONTH-LAW x ACTUAL PALACE ELEMENT combinations",flush=True)
    print("WRITTEN",dest,flush=True)

if __name__=="__main__":main()
