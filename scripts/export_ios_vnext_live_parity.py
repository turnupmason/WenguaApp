"""Run the *current live* Python V-next for five fixed technically valid clocks.
Never consult an outcome when choosing a timestamp, and never mark these
software dry runs as original historical book families or medical evidence.
The Swift CLI consumes this JSON in the SAME GitHub Actions job.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from src.wengua.health_text_pipeline_vnext_review import auto_cast_health_review_text

CASES=[
    ("2025-07-18T03:00:00-04:00","self","direct_self"),
    ("2022-07-19T11:00:00-04:00","self","direct_self"),
    ("2021-07-03T01:00:00-04:00","self","direct_self"),
    ("2024-05-28T13:00:00-04:00","self","direct_self"),
    ("2026-11-16T21:00:00-05:00","father","direct_proxy"),
]

def make_fixture():
    reports=[]
    for instant,relationship,context in CASES:
        r=auto_cast_health_review_text(
            iso=instant,timezone_name="America/New_York",
            inquiry={"intent":"severity","relationship":relationship,
                     "consultation_context":context})
        q=r["full_health_role_strength_network"]["candidate_five_grade_quantization"]
        print("PY_ROLE_EFFECTIVE_GATE",instant,json.dumps(q.get("role_effectiveness_gates"),ensure_ascii=False,sort_keys=True))
        roles={}
        for key,row in q["roles"].items():
            roles[key]={
                "palace":row["palace"],
                "components":{
                    "star":row["star"]["score"],
                    "door":row["door"]["score"],
                    "deity":row["deity"]["score"],
                    "pattern":row["pattern"]["score"]},
                "raw":row["palace_score"]["raw_sum"],
                "score":row["palace_score"]["score"],
                "void":row["palace_score"]["void_state"]}
        aux={
           key:{"palace":row["palace"],
                "score":row["palace_score"]["score"]}
           for key,row in q["auxiliary_qian_kun"].items()
        }
        role_checks=r["full_health_role_strength_network"]["role_group_reviews"]
        controls={
            key:{"direction":row["relation"],
                 "cell":row.get("control_result"),
                 "scenario":row.get("control_scenario")}
            for key,row in role_checks.items()
        }
        reports.append({
            "evidenceDirection":r["verdict"]["state"],
            "controls":controls,
            "instant":instant,
            "relationship":"父亲" if relationship=="father" else "本人",
            "summary":q["summary"],
            "roles":roles,
            "auxiliaries":aux,
            "firstStage":r["first_stage_macro"]["five_not_encounter_triggered"],
        })
    return {"schema":"wengua_native_vnext_live_five_current_python",
            "source":"src.wengua.health_text_pipeline_vnext_review.auto_cast_health_review_text",
            "cases":reports}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output",required=True)
    args=p.parse_args()
    obj=make_fixture()
    path=Path(args.output)
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print("CURRENT_LIVE_PYTHON_VNEXT_PARITY_READY cases=",len(obj["cases"]))
if __name__=="__main__":
    main()
