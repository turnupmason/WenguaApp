"""Three reproducible random local hours, live Python V-next truth fixtures.
No auspice/outcome filtering. Rejected technical candidate instants kept.
These are software test casts, not historical cases or medical claims.
"""
from __future__ import annotations
import argparse
from datetime import datetime
from pathlib import Path
import json
import random
from zoneinfo import ZoneInfo
from src.wengua.health_text_pipeline_vnext_review import auto_cast_health_review_text

SEED=202610263311
RELATIONS=(("self","本人","direct_self",None),
           ("father","父亲","direct_proxy",None),
           ("wife","妻子","direct_proxy","female"))

def produce(seed=SEED,count=3,wife_only=False):
    if not 2 <= count <= 24:
        raise ValueError('batch count must be 2..24')
    rng=random.Random(seed)
    cases=[]
    rejected=[]
    accepted_instants=set()
    for draw in range(1,max(81,count*40)+1):
        if len(cases)==count:break
        instant=datetime(rng.randint(2020,2025),rng.randint(1,12),
            rng.randint(1,28),rng.choice([1,3,5,7,9,11,13,15,17,19,21]),
            tzinfo=ZoneInfo("America/New_York")).isoformat()
        rel,label,context,sex=RELATIONS[2 if wife_only else len(cases)%len(RELATIONS)]
        if instant in accepted_instants:
            rejected.append({"draw":draw,"instant":instant,"relationship":label,
                             "reason":"duplicate previously accepted clock"})
            continue
        inquiry={"intent":"severity","relationship":rel,
                 "consultation_context":context}
        if sex:inquiry["patient_sex"]=sex
        try:
            r=auto_cast_health_review_text(
                iso=instant,timezone_name="America/New_York",inquiry=inquiry)
        except (ValueError,LookupError,KeyError) as e:
            rejected.append({"draw":draw,"instant":instant,
                             "relationship":label,"reason":str(e)})
            continue
        accepted_instants.add(instant)
        q=r["full_health_role_strength_network"]["candidate_five_grade_quantization"]
        roles={
            k:{"palace":v["palace"],"components":{
                   "star":v["star"]["score"],"door":v["door"]["score"],
                   "deity":v["deity"]["score"],"pattern":v["pattern"]["score"]},
               "raw":v["palace_score"]["raw_sum"],
               "score":v["palace_score"]["score"],
               "void":v["palace_score"]["void_state"]}
            for k,v in q["roles"].items()
        }
        aux={k:{"palace":v["palace"],"score":v["palace_score"]["score"]}
             for k,v in q["auxiliary_qian_kun"].items()}
        controls={k:{"direction":v["relation"],
                 "cell":v.get("control_result"),
                 "scenario":v.get("control_scenario")}
              for k,v in r["full_health_role_strength_network"]["role_group_reviews"].items()}
        cases.append({
            "draw":draw,"instant":instant,"relationship":label,
            "patient_sex":sex,"context":context,
            "four_pillars":r["four_pillars"],
            "solar_term":r["solar_term"],"bureau":r["bureau"],
            "firstStage":r["first_stage_macro"]["five_not_encounter_triggered"],
            "summary":q["summary"],"roles":roles,"auxiliaries":aux,
            "controls":controls,"evidenceDirection":r["verdict"]["state"],
            "source_sections":r["sections"],
            "python_reading_text":r["reading_text"],
            "tianrui25":r["qualitative_palace_relationships"]["天芮星月令×星宫五行25格"],
            "macro":r["first_stage_macro"]
        })
    assert len(cases)==count, f"Insufficient accepted technical casts: {len(cases)}/{count}"
    return {"schema":"wengua_ios_random_batch_vnext_20261026_v2",
            "seed":seed,"timezone":"America/New_York",
            "selection":f"first {count} technically valid instants in seeded random order; " + ("wife direct_proxy female for all" if wife_only else "profiles cycle self father wife") + "; no selection by score/verdict",
            "rejected":rejected,"cases":cases}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output",required=True)
    ap.add_argument("--seed",type=int,default=SEED)
    ap.add_argument("--count",type=int,default=3)
    ap.add_argument("--wife-only",action="store_true",help="Use wife/direct_proxy/female for every sampled chart")
    args=ap.parse_args()
    obj=produce(seed=args.seed,count=args.count,wife_only=args.wife_only)
    p=Path(args.output)
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print("VNEXT_RANDOM_PYTHON_TIMES="+json.dumps({
        "seed":obj["seed"],"count":len(obj["cases"]),"rejected":obj["rejected"],
        "accepted":[{"instant":c["instant"],"draw":c["draw"],"relation":c["relationship"]}
                    for c in obj["cases"]]},ensure_ascii=False))
if __name__=="__main__":main()
