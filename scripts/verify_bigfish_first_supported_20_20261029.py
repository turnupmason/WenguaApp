"""Full REAL original BigFish TS -> frozen Wengua V8/V10.2 20x2 smoke.

Only tests accepted independently source-bound non-Jia father scenarios.
Does NOT claim years with source Jia are supported, nor Gregorian time validity.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
from scripts.verify_bigfish_actor_natal_real_20261029 import load_adapter

def main(compiled):
    script=load_adapter(compiled)
    script.RELATIONSHIP="father"
    script.PATIENT_BIRTH_GANZHI=None
    validation=script.validate_actor_settings(script.actor_catalog())
    inquiry=script.build_inquiry(validation)
    # Now verify the exact formerly failed father 甲子 first20, as well as
    # the pre-existing second-year 乙丑 success regression. No natal.
    worker=script.BigFishWorker(script.base.OUTPUT)
    total=0
    try:
        for start in (0,8640):
          for idx in range(start,start+20):
            pillars=script.scenario(idx)
            assert pillars["year"]==("甲子" if start==0 else "乙丑"),(idx,pillars)
            assert not script.DEFER_UNRESOLVED_JIA
            for term in script.TERM_BY_MONTH[pillars["month"][1]]:
                result=script.compute_variant(worker,pillars,term,inquiry)
                if not result["status"].startswith("原始断词") or not result["text"]:
                    raise AssertionError(f"REAL BigFish first20 source failed: idx={idx+1} term={term} "
                                         f"pillars={pillars} error={result.get('error')}")
                binding=result["source_fact_lock"]["person_binding"]
                roles=result["source_fact_lock"]["selected_roles"]
                assert binding["role_via"]=="casting_year_stem",binding
                assert binding["stem"]==pillars["year"][0],binding
                if start==0:
                    assert binding["source_ganzhi"]=="甲子",binding
                    assert binding["carrier_stem"]=="戊",binding
                assert binding["natal_active"] is False
                assert binding["auxiliary_palaces"]==[6],binding
                assert "natal" not in roles
                assert roles["patient"]["palace"]==binding["palace"]
                assert roles["gender"]["palace"]==6
                assert isinstance(result["score"],int) and -5<=result["score"]<=5
                assert result["sections"] and result["original_text_sha256"]
                print("REAL_BIGFISH_20_FATHER_NO_NATAL_PASS "+json.dumps({
                    "index":idx+1,"term":term,"pillars":pillars,
                    "bureau":result["bureau"],"physical":result["base_id"],
                    "stem":binding["stem"],"patient_palace":binding["palace"],
                    "score_internal":result["score"],"text_sha256":result["original_text_sha256"]
                },ensure_ascii=False),flush=True)
                total+=1
    finally:
        worker.close()
    assert total==80,total
    print("TOTAL_REAL_BIGFISH_FIRST_20_JIA_FIXED=40 PLUS_YICHOU_40; NO_NATAL",
          flush=True)

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--compiled",type=Path,required=True)
    main(ap.parse_args().compiled)
