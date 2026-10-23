"""Generate non-blind four-clock before/after V3.9.1 vs V-next review.

Outputs into the CI artifact folder. This DOES NOT use book-case endings as
inputs or tune verdicts, and does NOT alter the sealed V3.9.1 files.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path
from src.wengua.health_text_pipeline import auto_cast_health_v39_text
from src.wengua.health_text_pipeline_vnext_review import auto_cast_health_review_text

ROOT=Path(__file__).resolve().parents[1]
SAMPLES=ROOT/"data/evaluation/health_v391/four_fixed_random_real_hour_charts_SOURCE_AUDIT.json"
INQUIRY={"intent":"severity","relationship":"self","consultation_context":"direct_self"}

def make_report():
    old=json.loads(SAMPLES.read_text("utf8"))["samples"]
    result=[]
    for sample in old:
        opts={"iso":sample["local_datetime"],"timezone_name":sample["timezone"],
              "inquiry":dict(INQUIRY)}
        before=auto_cast_health_v39_text(**opts)
        after=auto_cast_health_review_text(**opts)
        result.append({
            "instant":sample["local_datetime"],
            "four_pillars":sample["four_pillars"],
            "original_v391_reading_text":before["reading_text"],
            "original_v391_reading_sha256":sample["v391_customer_reading_sha256"],
            "new_review_conclusion":after["sections"][0]["text"],
            "new_review_state":after["verdict"]["state"],
            "new_review_full_reading":after["reading_text"],
            "new_review_sections":after["sections"],
            "source_pairs_require_full_predicate":after["audit"]["missing_source_predicates"],
            "deduplicated_life_facts":len(after["audit"]["actual_stage_facts_unique"]),
            "old_v39_verdict_internal_only":after["audit"]["legacy_v39_symbolic_verdict"],
            "not_blind_historical_or_clinical_accuracy_test":True,
        })
    return {
        "version":"vnext_preview_not_public","baseline_unchanged":True,
        "abstention_supported":True,"scores_disabled":True,
        "tested_four_fixed_development_charts_not_new_blind_cases":True,
        "original_book_outcomes_not_loaded":True,
        "cases":result
    }

def main():
    dst=Path(sys.argv[1]) if len(sys.argv)>1 else Path("health_vnext_preview.json")
    dst.parent.mkdir(parents=True,exist_ok=True)
    report=make_report()
    dst.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    for x in report["cases"]:
        print("时刻:",x["instant"])
        print("旧版古籍主判:",x["old_v39_verdict_internal_only"])
        print("新版判断:",x["new_review_conclusion"])
        print("原书仍待完整条件核定的天地干:",x["source_pairs_require_full_predicate"])
        print("去重后的重点人物十二长生事实:",x["deduplicated_life_facts"])
        print("---")
    print("WROTE",dst,flush=True)

if __name__=="__main__":main()
