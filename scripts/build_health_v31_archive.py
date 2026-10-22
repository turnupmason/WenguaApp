"""Immutable V3.1 SQLite repair audit, from exact already-archived V3.0 full source."""
from __future__ import annotations
import argparse,hashlib,json,sqlite3
from pathlib import Path
from scripts.build_health_v21_archive import preserve
from scripts.run_two_historical_health_v31 import evaluate
ROOT=Path(__file__).resolve().parents[1]
PARENT_SHA="713081aed68bb38172ae506d78c1cf59a1853f64daf14be360507e6670baf27b"
TEMPLATE=ROOT/"data/knowledge/phrase_library/health_v31/severity_fixed_template.json"
MIG=ROOT/"schema/migrations/059_health_patient_hour_direction_v31.sql"
def sha(x):return hashlib.sha256(Path(x).read_bytes()).hexdigest()
def build(parent,out,sealed,manifest):
    parent,out,sealed,manifest=map(Path,(parent,out,sealed,manifest))
    if out.exists() or sealed.exists():raise ValueError("Never overwrite past archive/seal")
    if sha(parent)!=PARENT_SHA:raise ValueError("Exact V3.0 full source required")
    pack=json.loads(TEMPLATE.read_text("utf8"))
    updated=evaluate(db_path=parent)
    assert len(pack["sections"])==11 and len(updated["samples"])==2
    fmt=next(x["format"] for x in pack["sections"] if x["id"]=="08_hour")
    out.parent.mkdir(parents=True,exist_ok=True)
    with sqlite3.connect(parent.resolve().as_uri()+"?mode=ro",uri=True) as old,sqlite3.connect(out) as db:
        old.backup(db)
        db.executescript(MIG.read_text("utf8"))
        db.execute("PRAGMA foreign_keys=ON")
        with db:
            for table,count in (("cases",194),("sections",43),
               ("health_v30_stem_pair_rules",42),
               ("health_v30_composite_rule_index",17),
               ("health_v30_historical_readout_seals",2)):
                n=db.execute('SELECT COUNT(*) FROM "'+table+'"').fetchone()[0]
                if n!=count:raise ValueError("Older archived table changed: "+table)
            wrong=db.execute("SELECT COUNT(*) FROM marriage_v16_post_inference_labels WHERE matches_initial_book_retrospective_result=0").fetchone()[0]
            if wrong!=2:raise ValueError("Prior historical prediction failures lost")
            db.execute("""INSERT INTO health_v31_hour_patient_fixed_templates
                 (section_id,exact_format,interpret_from_person_to_hour,no_post_gpt_rewrite)
                 VALUES('08_hour',?,1,1)""",(fmt,))
            for x in updated["samples"]:
                db.execute("""INSERT INTO health_v31_correction_archive
                     (case_id,v30_original_sha256,new_v31_sha256,
                      never_overwrite_original,original_book_answer_used,content_user_approved)
                     VALUES(?,?,?,1,0,0)""",
                     (x["case_id"],x["v30_original_sha256"],x["sha256"]))
            db.execute("""INSERT INTO health_v31_version_receipt
                 (version,exact_parent_v30_sha256,book_cases,source_sections,
                  original_two_failed_dev_cases,imported_ordered_pairs,
                  indexed_composite_patterns,remaining_other_health_subtypes_unapproved,
                  original_rows_unchanged,user_review_status)
                 VALUES('v3.1',?,194,43,2,42,17,4,1,'pending')""",(PARENT_SHA,))
        preserve(old,db)
        if db.execute("PRAGMA integrity_check").fetchone()[0]!="ok":raise ValueError("corrupt new archive")
        if db.execute("PRAGMA foreign_key_check").fetchall():raise ValueError("broken foreign keys")
        db.execute("VACUUM");db.commit()
    sealed.parent.mkdir(parents=True,exist_ok=True)
    sealed.write_text(json.dumps(updated,ensure_ascii=False,indent=2)+"\n","utf8")
    meta={"version":"V3.1","full_sqlite_sha256":sha(out),
       "exact_parent_v30_sha256":PARENT_SHA,
       "sealed_readouts_sha256":sha(sealed),
       "full_original_cases":194,"original_chapters":43,
       "prior_two_failed_dev_cases":2,"v30_bad_hour_verdict_retained_as_failure":True,
       "v31_changed_only_hour_patient_role_semantics":True,
       "pair_catalog_count":42,"composite_catalog_count":17,
       "patient_severity_content_user_review":"pending",
       "four_other_health_intents_approved":False,
       "no_gpt_or_network_rewrite":True,"clinical_validation":False}
    manifest.parent.mkdir(parents=True,exist_ok=True)
    manifest.write_text(json.dumps(meta,ensure_ascii=False,indent=2)+"\n","utf8")
    return meta
if __name__=="__main__":
    p=argparse.ArgumentParser()
    for name in ("parent","output","sealed","manifest"):p.add_argument("--"+name,required=True)
    a=p.parse_args()
    print(json.dumps(build(a.parent,a.output,a.sealed,a.manifest),ensure_ascii=False))
