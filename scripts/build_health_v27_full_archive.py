"""Append-only V2.7 full SQLite with two sealed historical case readings.

No original author conclusion is opened during candidate selection, model
inference or recording. All 194 original event families remain untouched.
"""
from __future__ import annotations
import argparse,hashlib,json,sqlite3
from pathlib import Path
from scripts.build_health_v21_archive import preserve
from scripts.run_two_historical_health_v27 import evaluate,SEED
ROOT=Path(__file__).resolve().parents[1]
PARENT_SHA="e6dff53d3c1f403650581877b8563db00b49958d75b0a3e8a459d6c7bb4cfa17"
TEMPLATE=ROOT/"data/knowledge/phrase_library/health_v27/severity_fixed_template.json"
MIG=ROOT/"schema/migrations/055_health_severity_five_not_encounter_v27.sql"
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def build(parent,output,index_dir,predictions_out):
    parent,output,index_dir,predictions_out=map(Path,(parent,output,index_dir,predictions_out))
    if output.exists() or predictions_out.exists():
        raise ValueError("Never overwrite immutable original archive or sealed prediction")
    if sha(parent)!=PARENT_SHA:
        raise ValueError("V2.7 must derive from exact complete V2.6 source SHA")
    template=json.loads(TEMPLATE.read_text("utf8"))
    if len(template["sections"])!=11:raise ValueError("Exactly 11 fixed sections")
    # Run independent prospective STYLE forecasts before opening author results.
    report=evaluate(db_path=parent)
    if len(report["predictions"])!=2:raise ValueError("Exactly two distinct historical cases")
    output.parent.mkdir(parents=True,exist_ok=True)
    with sqlite3.connect(parent.resolve().as_uri()+"?mode=ro",uri=True) as old,sqlite3.connect(output) as db:
        old.backup(db)
        db.executescript(MIG.read_text("utf8"))
        db.execute("PRAGMA foreign_keys=ON")
        with db:
            for table,n in {
                 "cases":194,"sections":43,
                 "health_v20_actor_role_profiles":14,
                 "health_v20_intent_templates":5,
                 "health_v20_intent_steps":66,
                 "health_v22_customer_severity_sections":21,
                 "health_v23_display_groups":1,
                 "health_v24_corrected_father_prose":4,
                 "health_v25_concise_sections":11,
                 "health_v26_strict_customer_template":11}.items():
                got=db.execute('SELECT COUNT(*) FROM "'+table+'"').fetchone()[0]
                if got!=n:raise ValueError("Previous version rows missing "+table+" "+str(got))
            wrong=db.execute(
             "SELECT COUNT(*) FROM marriage_v16_post_inference_labels WHERE matches_initial_book_retrospective_result=0").fetchone()[0]
            if wrong!=2:raise ValueError("Previous failed developer examples must remain")
            for i,section in enumerate(template["sections"],1):
                db.execute("""INSERT INTO health_v27_fixed_customer_sections
                    (ordinal,section_id,title,static_format,optional_context,
                     no_model_rewrite,no_outcome_leakage) VALUES(?,?,?,?,?,1,1)""",
                    (i,section["id"],section["title"],section["format"],section.get("optional")))
            rules=[
                ("health:five_not_encounter","kaiwu","analysis_judgment_ch04",
                 "580-590; also shenqi/health_prediction_ch01 case4",
                 "hour_stem_controls_day_stem AND parity_matches",
                 "凶时，传统测病不利；不凭此一项断生死",
                 "癸日庚时不触发;庚日丁时虽火克金但阴阳不同",
                 "author_source_conditions_indexed"),
                ("health:male_qian","shenqi","health_prediction_ch01",
                 "source father predictive method around lines 100-106",
                 "patient_sex=male; Qian6 auxiliary to main yongshen",
                 "乾6为男性参考宫，主辅合断，不重复计数",
                 "患者性别未知不得推断男人",
                 "user_requested_and_source_gender_symbol"),
                ("health:female_kun","shenqi","health_prediction_ch01",
                 "source older relative method around lines 190-195",
                 "patient_sex=female; Kun2 auxiliary to main yongshen",
                 "坤2为女性参考宫，主辅合断，不替代年干或日干",
                 "患者性别未知不得推断女人",
                 "user_requested_and_source_gender_symbol"),
            ]
            for row in rules:
                db.execute("""INSERT INTO health_v27_conditional_rule_registry
                 (rule_id,source_book,source_chapter,source_lines,truth_conditions,
                 meaning,counterexamples,proof_status,no_single_factor_clinical_prediction)
                 VALUES(?,?,?,?,?,?,?,?,1)""",row)
            for pred in report["predictions"]:
                db.execute("""INSERT INTO health_v27_sealed_historical_predictions
                     (event_family_id,user_selected_clock,selection_seed,
                      full_readout_sha256,provisional_traditional_verdict,
                      author_outcome_used_for_generation,later_feedback_still_sealed,user_review_status)
                     VALUES(?,?,?,?,?,0,1,'pending')""",
                     (pred["case_id"],pred["civil_clock_anchor"],SEED,
                      pred["readout_sha256"],pred["traditional_verdict"]))
            db.execute("""INSERT INTO health_v27_acceptance_history
                  (version,parent_full_sha256,original_event_families,
                   original_source_sections,old_wrong_development_predictions,
                   original_21_health_fact_sections,source_template_sections,
                   other_four_unreviewed_health_intents,no_runtime_gpt,
                   real_world_clinical_outcomes_verified,all_previous_rows_unchanged,user_review_status)
                  VALUES('v2.7',?,194,43,2,21,11,4,1,0,1,'pending')""",(PARENT_SHA,))
        preserve(old,db)
        if db.execute("PRAGMA integrity_check").fetchone()[0]!="ok":
            raise ValueError("New full SQLite integrity failure")
        if db.execute("PRAGMA foreign_key_check").fetchall():
            raise ValueError("New full SQLite FK failure")
        db.execute("VACUUM")
        db.commit()
        counts={table:db.execute('SELECT COUNT(*) FROM "'+table+'"').fetchone()[0]
            for table in ("cases","sections","health_v22_customer_severity_sections",
                "health_v26_strict_customer_template","health_v27_fixed_customer_sections",
                "health_v27_conditional_rule_registry",
                "health_v27_sealed_historical_predictions","health_v27_acceptance_history")}
    predictions_out.parent.mkdir(parents=True,exist_ok=True)
    predictions_out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n","utf8")
    index_dir.mkdir(parents=True,exist_ok=True)
    manifest={
        "schema":"wengua_v27_194_case_11_section_five_not_gender_2_sealed_trials",
        "parent_full_sha256":PARENT_SHA,
        "new_full_sha256":sha(output),
        "original_194_events":194,"original_43_chapters":43,
        "original_failed_case_examples":2,
        "old21_health_source_sections_kept":True,
        "previous_all_rows_bytewise":True,
        "gender_qian_kun_added":True,"five_not_encounter_added":True,
        "predictions_sealed_before_book_outcome_comparison":True,
        "actual_truly_unseen_blind_test":False,
        "traditional_verdict_not_medical_prognosis":True,
        "runtime_GPT_or_network_calls":0,
        "other_four_health_subdomains":"unapproved",
        "user_acceptance":"pending",
        "prediction_readout_sha256s":{p["case_id"]:p["readout_sha256"] for p in report["predictions"]},
        "counts":counts
    }
    (index_dir/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n","utf8")
    return manifest

if __name__=="__main__":
    p=argparse.ArgumentParser()
    for arg in ("base","output","index-dir","sealed-predictions"):
        p.add_argument("--"+arg,required=True)
    a=p.parse_args()
    print(json.dumps(build(a.base,a.output,a.index_dir,a.sealed_predictions),ensure_ascii=False))
