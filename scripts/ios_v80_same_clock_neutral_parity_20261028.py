"""Exact 2026-10-28 13:44 NYC same-instant self/colleague parity.

Produce ONE relationship per run, because the Swift test harness intentionally
rejects duplicate instants inside a single random batch. These are two actual
same-minute readings, not randomized or a valid clinical comparison.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
from src.wengua.health_text_pipeline_vnext_review import auto_cast_health_review_text

ISO="2026-10-28T13:44:00-04:00"
ZONE="America/New_York"
ROLES={"self":("self","本人","direct_self"),
       "colleague":("colleague","同事","direct_proxy"),
       "grandfather":("grandfather","爷爷","direct_proxy"),
       "grandmother":("grandmother","奶奶","direct_proxy")}

def produce(role):
    relation,label,context=ROLES[role]
    r=auto_cast_health_review_text(
        iso=ISO,timezone_name=ZONE,inquiry={
            "intent":"severity","relationship":relation,
            "consultation_context":context})
    assert r["four_pillars"]=={
        "year":"丙午","month":"戊戌","day":"乙亥","hour":"癸未"}
    q=r["full_health_role_strength_network"]["candidate_five_grade_quantization"]
    s=q["summary"]
    # Historical first version was 0 for both. The independently approved
    # Tianqin centre-earth 81-pair correction now gives +3 for both.
    # Grandparents may have OTHER totals because real gender palaces differ.
    if role in ("self","colleague"):
        assert s["raw_final_before_saturation"]==3
        assert s["score"]==3
        # Current user-authorized 81 pairing replaces the old zero result.
        last=next(section["text"] for section in r["sections"]
                  if section["id"]=="90_review")
        assert "此病为中吉" in last
        assert "暂不强断吉凶" not in last
    else:
        patient=q["summary"]["actual_role_strengths"]["patient"]
        gender=q["summary"]["actual_role_strengths"]["gender"]
        assert patient["symbol"]==r["four_pillars"]["year"][0]
        assert gender["palace"]==(6 if role=="grandfather" else 2)
        assert "natal" not in q["roles"]
        assert r["audit"]["role_confidence"]=="conditional_older_generation_analogy_not_exact_case"
    roles={k:{"palace":v["palace"],
              "components":{"star":v["star"]["score"],
                            "door":v["door"]["score"],
                            "deity":v["deity"]["score"],
                            "pattern":v["pattern"]["score"]},
              "raw":v["palace_score"]["raw_sum"],
              "score":v["palace_score"]["score"],
              "void":v["palace_score"]["void_state"]}
           for k,v in q["roles"].items()}
    auxiliaries={k:{"palace":v["palace"],"score":v["palace_score"]["score"]}
                 for k,v in q["auxiliary_qian_kun"].items()}
    controls={k:{"direction":v["relation"],
                 "cell":v.get("control_result"),
                 "scenario":v.get("control_scenario")}
              for k,v in r["full_health_role_strength_network"][
                  "role_group_reviews"].items()}
    case={"draw":1,"instant":ISO,"relationship":label,
          "patient_sex":None,"context":context,
          "four_pillars":r["four_pillars"],"solar_term":r["solar_term"],
          "bureau":r["bureau"],
          "firstStage":r["first_stage_macro"]["five_not_encounter_triggered"],
          "summary":s,"roles":roles,"auxiliaries":auxiliaries,
          "controls":controls,"evidenceDirection":r["verdict"]["state"],
          "source_sections":r["sections"],
          "python_reading_text":r["reading_text"],
          "tianrui25":r["qualitative_palace_relationships"][
              "天芮星月令×星宫五行25格"],
          "macro":r["first_stage_macro"]}
    return {"schema":"wengua_ios_random_batch_vnext_20261026_v2",
            "seed":202610281344,
            "timezone":ZONE,
            "selection":"exact user screenshot 13:44 same physical clock; "+
                role+" is a source-specific role; no choice by grade",
            "rejected":[],"cases":[case]}

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--role",required=True,choices=tuple(ROLES))
    ap.add_argument("--output",required=True)
    args=ap.parse_args()
    payload=produce(args.role)
    path=Path(args.output)
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n")
    print("EXACT_CLOCK_1344="+json.dumps({
        "role":args.role,"pillars":payload["cases"][0]["four_pillars"],
        "score":payload["cases"][0]["summary"]["score"],
        "raw":payload["cases"][0]["summary"]["raw_final_before_saturation"]
    },ensure_ascii=False))
