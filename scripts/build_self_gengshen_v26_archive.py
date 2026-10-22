"""Append-only corrected V2.6 full 194-case archive from exact V2.5."""
from __future__ import annotations
import argparse, hashlib,json,sqlite3
from pathlib import Path
from scripts.build_health_v21_archive import preserve
ROOT=Path(__file__).resolve().parents[1]
PARENT_SHA="6b4dd75729d76f99bfd089c09606ddf39b316a12b80a96949373d884fd098bdf"
TPL=ROOT/"data/knowledge/phrase_library/health_v26/severity_11_concise_template.json"
MIG=ROOT/"schema/migrations/054_health_severity_gengshen_corrected_v26.sql"
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def build(parent,output,index_dir):
    parent,output,index_dir=map(Path,(parent,output,index_dir))
    if output.exists():raise ValueError("Immutable version cannot be replaced")
    if sha(parent)!=PARENT_SHA:raise ValueError("Exact immutable complete V2.4 full 194-case parent required")
    template=json.loads(TPL.read_text(encoding="utf8"))
    assert len(template["sections"])==11
    output.parent.mkdir(parents=True,exist_ok=True)
    with sqlite3.connect(parent.resolve().as_uri()+"?mode=ro",uri=True) as old, sqlite3.connect(output) as db:
        old.backup(db)
        db.executescript(MIG.read_text(encoding="utf8"))
        db.execute("PRAGMA foreign_keys=ON")
        with db:
            for table,count in {
                "cases":194,"sections":43,
                "health_v20_actor_role_profiles":14,
                "health_v20_intent_templates":5,
                "health_v20_intent_steps":66,
                "health_v22_customer_severity_sections":21,
                "health_v23_display_groups":1,
                "health_v24_corrected_father_prose":4}.items():
                actual=db.execute('SELECT COUNT(*) FROM "'+table+'"').fetchone()[0]
                if actual!=count:raise ValueError("Parent rows incorrect "+table+" "+str(actual))
            assert db.execute("SELECT COUNT(*) FROM health_v25_concise_sections").fetchone()[0]==11
            oldwrong=db.execute("SELECT COUNT(*) FROM marriage_v16_post_inference_labels WHERE matches_initial_book_retrospective_result=0").fetchone()[0]
            if oldwrong!=2:raise ValueError("Prior 2 failed dev cases were lost")
            for i,s in enumerate(template["sections"],1):
                db.execute("""INSERT INTO health_v26_source_grounded_language
                    (section_order,section_id,title,template_text,optional_context,no_llm_after_cast)
                    VALUES(?,?,?,?,?,1)""",
                    (i,s["id"],s["title"],s["format"],s.get("optional")))
            db.execute("""INSERT INTO health_v26_acceptance_audit
                (version,exact_parent_v25_sha256,original_case_count,original_section_count,
                 old_wrong_prediction_count,old_21_health_facts,visible_self_paragraphs,
                 source_template_sections,user_has_not_approved_four_other_intents,
                 false_stem_pair_illness_name_suppressed,directional_five_elements_corrected,
                 illness_and_patient_door_pressure_distinct,yin_outer_palace_slowness_in_final,
                 all_previous_rows_preserved,actual_medical_prognosis_validated,user_status)
                 VALUES ('v2.6',?,194,43,2,21,10,11,1,1,1,1,1,1,0,'pending')""",(PARENT_SHA,))
        preserve(old,db)
        if db.execute("PRAGMA integrity_check").fetchone()[0]!="ok":raise ValueError("SQLite corruption")
        if db.execute("PRAGMA foreign_key_check").fetchall():raise ValueError("Foreign-key error")
        db.execute("VACUUM");db.commit()
        counts={t:db.execute('SELECT COUNT(*) FROM "'+t+'"').fetchone()[0] for t in
               ("cases","sections","health_v22_customer_severity_sections",
                "health_v24_corrected_father_prose","health_v25_concise_sections",
                "health_v25_evidence_acceptance")}
    index_dir.mkdir(parents=True,exist_ok=True)
    rec={
        "schema":"wengua_v26_corrected_self_gengshen_full_194_case",
        "exact_parent_sha256":PARENT_SHA,"new_sqlite_sha256":sha(output),"previous_v25_failed_output_retained":True,
        "original_book_cases":194,"original_book_sections":43,"old_dev_failures":2,
        "source_21_facets_preserved":True,
        "template_total_sections":11,"visible_self_sections":10,
        "unrelated_sexual_formation_name_suppressed":True,
        "five_element_direction_and_targeted_door_pressure_fixed":True,
        "yin_outer_slow_in_final":True,
        "optional_family_section_skipped_for_self":True,
        "other_four_health_templates_unapproved":True,
        "source_fuyin_fanyin":True,
        "traditional_binary_verdict_not_clinical":True,
        "offline_no_gpt":True,"user_content_approved":False,
        "all_previous_rows_preserved":True,"counts":counts}
    (index_dir/"manifest.json").write_text(json.dumps(rec,ensure_ascii=False,indent=2)+"\n","utf8")
    return rec
if __name__=="__main__":
    a=argparse.ArgumentParser()
    for flag in ("base","output","index-dir"):a.add_argument("--"+flag,required=True)
    p=a.parse_args()
    print(json.dumps(build(p.base,p.output,p.index_dir),ensure_ascii=False))
