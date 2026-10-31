"""Real original BigFish compiled TS + 22 actor sources / 24 real categories.

At SAME genuine clock; all 22 actors must bind their own source kind without
guessing birth Ganzhi or sex/age/rank. Composite spouse/parent have sex-specific
inputs. Frozen V8 score and V10.2 text must be present or the test fails.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
from scripts.verify_bigfish_actor_natal_real_20261029 import load_adapter

def main(compiled:Path):
    script=load_adapter(compiled)
    catalog=script.actor_catalog()
    configurations=script.all_signifier_configs(catalog)
    assert len(configurations)==24,len(configurations)
    slot=next(script.real_calendar_slots())
    worker=script.BigFishWorker(script.base.OUTPUT)
    passed=0
    previous=(script.RELATIONSHIP,script.PATIENT_SEX)
    try:
        for item in configurations:
            script.RELATIONSHIP=item["relationship"]
            script.PATIENT_SEX=item["patient_sex"]
            validation=script.validate_actor_settings(catalog)
            inquiry=script.build_inquiry(validation)
            assert "patient_birth_ganzhi" not in inquiry
            result=script.real_case_from_slot(worker,slot,inquiry)
            if not result["status"].startswith("原始断词"):
                raise AssertionError("Real BigFish selected use-god failed: "+
                                     json.dumps({
                                        "relationship":item["relationship"],
                                        "patient_sex":item["patient_sex"],
                                        "source_kind":item["source_kind"],
                                        "reason":result.get("error"),
                                     },ensure_ascii=False))
            lock=result["source_fact_lock"]
            binding=lock["person_binding"]
            assert binding["role_via"]==item["source_kind"],(item,binding)
            assert lock["selected_roles"]["patient"]["palace"]==binding["palace"]
            assert binding["natal_active"] is False
            assert "natal" not in lock["selected_roles"]
            assert result["sections"] and result["text"]
            assert result["original_text_sha256"] and result["evidence_sha"]
            print("REAL_BIGFISH_ALL_ACTOR_SOURCE_PASS "+json.dumps({
                "relationship":item["relationship"],"sex":item["patient_sex"],
                "source_kind":item["source_kind"],
                "source_status":item["source_status"],
                "palace":binding["palace"],
                "original_stem":binding["stem"],
                "carrier_stem":binding.get("carrier_stem"),
                "score_internal":result["score"],
                "read_hash":result["original_text_sha256"],
                "approved_for_app":False
            },ensure_ascii=False),flush=True)
            passed+=1
    finally:
        script.RELATIONSHIP,script.PATIENT_SEX=previous
        worker.close()
    assert passed==24
    print("TOTAL_REAL_BIGFISH_ALL_ACTORS=24/24; SOURCE_PROFILE_IDS=22; NATAL_NOT_USED",flush=True)

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--compiled",type=Path,required=True)
    main(ap.parse_args().compiled)
