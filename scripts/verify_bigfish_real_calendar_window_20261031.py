"""Real BigFish TypeScript × actual calendar 2026 Nov–2027 Mar, V8/V10.2.

Strictly exercises original TS; does not claim the whole 121-day window is
already generated, or imply a 12-slot sample substitutes for any phone clock.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from scripts.verify_bigfish_actor_natal_real_20261029 import load_adapter

def main(compiled:Path):
    script=load_adapter(compiled)
    script.RELATIONSHIP="father"
    script.PATIENT_BIRTH_GANZHI=None
    slots=list(script.real_calendar_slots())
    assert len(slots)==1452,len(slots)
    positions=(0,11,120,528,1440,1451)
    worker=script.BigFishWorker(script.base.OUTPUT)
    count=0
    inquiry={"intent":"severity","relationship":"father",
             "consultation_context":"direct_proxy"}
    try:
        for idx in positions:
            slot=slots[idx]
            result=script.real_case_from_slot(worker,slot,inquiry)
            if not result["status"].startswith("原始断词"):
                raise AssertionError("Real BigFish TS / source calendar / V8 fail: "+
                                     json.dumps({"instant":slot["instant"],
                                      "error":result["error"]},ensure_ascii=False))
            calendar=result["calendar_receipt"]
            lock=result["source_fact_lock"]
            binding=lock["person_binding"]
            assert calendar["active_solar_term"]==result["term"]
            assert lock["exact_real_instant"]==slot["instant"]
            assert binding["role_via"]=="casting_year_stem"
            assert binding["stem"]==calendar["four_pillars"]["year"][0]
            assert binding["natal_active"] is False
            assert lock["selected_roles"]["gender"]["palace"]==6
            assert -5<=result["score"]<=5
            assert result["sections"] and result["original_text_sha256"]
            print("TRUE_BIGFISH_CALENDAR_V8_V102_PASS "+json.dumps({
                "instant":slot["instant"],"term":result["term"],
                "pillars":calendar["four_pillars"],
                "bureau":result["bureau"],"physical":result["base_id"],
                "stem":binding["stem"],"palace":binding["palace"],
                "score_internal":result["score"],
                "text_sha256":result["original_text_sha256"],
            },ensure_ascii=False),flush=True)
            count+=1
    finally:
        worker.close()
    assert count==len(positions)
    print("TOTAL_TRUE_CALENDAR_BIGFISH_PASS "+str(count)+"/"+str(count),flush=True)

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--compiled",type=Path,required=True)
    a=p.parse_args()
    main(a.compiled)
