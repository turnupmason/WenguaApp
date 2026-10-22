"""Create immutable V2.6 full SQLite, append-only from exact V2.5 194-case source."""
from __future__ import annotations
import argparse,hashlib,json,sqlite3
from pathlib import Path
from scripts.build_health_v21_archive import preserve

ROOT=Path(__file__).resolve().parents[1]
PARENT_SHA="6b4dd75729d76f99bfd089c09606ddf39b316a12b80a96949373d884fd098bdf"
TPL=ROOT/"data/knowledge/phrase_library/health_v26/severity_customer_template.json"
MIG=ROOT/"schema/migrations/054_health_severity_strict_customer_template_v26.sql"

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def build(parent,output,index_dir):
    parent,output,index_dir=map(Path,(parent,output,index_dir))
    if output.exists():raise ValueError("Never overwrite immutable older SQLite")
    if sha(parent)!=PARENT_SHA:raise ValueError("V2.6 must derive from exact V2.5 complete SHA")
    template=json.loads(TPL.read_text("utf8"))
    if len(template["sections"])!=11:raise ValueError("Missing fixed 11-part template")
    output.parent.mkdir(parents=True,exist_ok=True)
    with sqlite3.connect(parent.resolve().as_uri()+"?mode=ro",uri=True) as old,sqlite3.connect(output) as db:
        old.backup(db)
        db.executescript(MIG.read_text("utf8"))
        db.execute("PRAGMA foreign_keys=ON")
        with db:
            counts={
               "cases":194,"sections":43,"health_v20_actor_role_profiles":14,
               "health_v20_intent_templates":5,"health_v20_intent_steps":66,
               "health_v22_customer_severity_sections":21,
               "health_v23_display_groups":1,
               "health_v24_corrected_father_prose":4,
               "health_v25_concise_sections":11}
            for table,n in counts.items():
                count=db.execute('SELECT COUNT(*) FROM "'+table+'"').fetchone()[0]
                if count!=n:raise AssertionError((table,count,n))
            failures=db.execute(
              "SELECT COUNT(*) FROM marriage_v16_post_inference_labels "
              "WHERE matches_initial_book_retrospective_result=0").fetchone()[0]
            if failures!=2:raise ValueError("Historic unsuccessful cases cannot disappear")
            for i,s in enumerate(template["sections"],1):
                db.execute("""INSERT INTO health_v26_strict_customer_template
                        (section_order,section_id,title,format_text,optional_context,
                        no_llm_or_rewrite,no_duplicate_palaces)
                        VALUES (?,?,?,?,?,1,1)""",
                       (i,s["id"],s["title"],s["format"],s.get("optional")))
            db.execute("""INSERT INTO health_v26_acceptance_receipt
               (receipt_id,v25_exact_parent_sha256,cases_unchanged,source_sections_unchanged,
               prior_wrong_predictions_unchanged,old_health_21_facets_unchanged,
               customer_section_count,user_self_section_count,previous_health_subtypes_unapproved,
               medically_validated,external_model_calls,previous_rows_kept,user_review_status)
               VALUES ('v2.6',?,194,43,2,21,11,10,4,0,0,1,'pending')""",(PARENT_SHA,))
        preserve(old,db)
        if db.execute("PRAGMA integrity_check").fetchone()[0]!="ok":raise ValueError("SQLite corrupt")
        if db.execute("PRAGMA foreign_key_check").fetchall():raise ValueError("Foreign key constraints failed")
        db.execute("VACUUM")
        db.commit()
        counts={t:db.execute('SELECT COUNT(*) FROM "'+t+'"').fetchone()[0] for t in
               ("cases","sections","health_v22_customer_severity_sections",
                "health_v25_concise_sections","health_v26_strict_customer_template",
                "health_v26_acceptance_receipt")}
    index_dir.mkdir(parents=True,exist_ok=True)
    receipt={
      "schema":"full_194_book_case_11_strict_customer_template_v26",
      "parent_sha256":PARENT_SHA,"new_sha256":sha(output),
      "original_book_case_families":194,"original_book_sections":43,
      "prior_failed_dev_examples":2,"previous_all_rows_unchanged":True,
      "previous_source_21_disease_facets_preserved":True,
      "runtime_model_calls":0,"medical_efficacy_proven":False,
      "four_unapproved_health_templates_still_blocked":True,
      "v26_section_templates":11,"user_self_real_output_sections":10,
      "user_approval":"pending","counts":counts}
    (index_dir/"manifest.json").write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n","utf8")
    return receipt

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    for flag in ("base","output","index-dir"):ap.add_argument("--"+flag,required=True)
    opts=ap.parse_args()
    print(json.dumps(build(opts.base,opts.output,opts.index_dir),ensure_ascii=False))
