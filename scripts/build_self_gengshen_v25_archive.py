"""Append-only complete V2.5 194-case source SQLite, immutable parent V2.4."""
from __future__ import annotations
import argparse, hashlib,json,sqlite3
from pathlib import Path
from scripts.build_health_v21_archive import preserve
ROOT=Path(__file__).resolve().parents[1]
PARENT_SHA="9b5e574543bf7fc298412ac98ededf09445dc3c555312ad7b525f92f22aa41e0"
TPL=ROOT/"data/knowledge/phrase_library/health_v25/severity_11_concise_template.json"
MIG=ROOT/"schema/migrations/053_health_severity_11_fuyin_verdict_v25.sql"
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
            oldwrong=db.execute("SELECT COUNT(*) FROM marriage_v16_post_inference_labels WHERE matches_initial_book_retrospective_result=0").fetchone()[0]
            if oldwrong!=2:raise ValueError("Prior 2 failed dev cases were lost")
            for i,s in enumerate(template["sections"],1):
                db.execute("""INSERT INTO health_v25_concise_sections
                    (section_order,section_id,title,template_text,optional_context,deterministic_python_only)
                    VALUES(?,?,?,?,?,1)""",
                    (i,s["id"],s["title"],s["format"],s.get("optional")))
            db.execute("""INSERT INTO health_v25_evidence_acceptance
                (version,exact_parent_sha256,original_book_case_families,original_book_sections,
                original_v16_wrong_development_predictions,original_21_health_source_facts,
                source_section_count,actual_user_preview_sections,four_other_unapproved_intents,
                fuyin_fanyin_strict_separate_computation,verdict_traditional_only,
                no_llm_runtime,medical_outcome_validated,previous_all_rows_unchanged,user_review_status)
                VALUES ('v2.5',?,194,43,2,21,11,10,4,1,1,1,0,1,'pending')""",(PARENT_SHA,))
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
        "schema":"wengua_v25_11_source_sections_self_gengshen_full_194_case",
        "exact_parent_sha256":PARENT_SHA,"new_sqlite_sha256":sha(output),
        "original_book_cases":194,"original_book_sections":43,"old_dev_failures":2,
        "source_21_facets_preserved":True,
        "template_total_sections":11,"visible_self_sections":10,
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
