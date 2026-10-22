"""V3.0 versioned full 194-original-case SQLite with user disease curriculum.

Append-only from exact immutable V2.9 SHA; original old rows remain
bitwise identical and old V2.7/V2.8/V2.9 prediction seals are untouched.
"""
from __future__ import annotations
import argparse,hashlib,json,sqlite3
from pathlib import Path
from scripts.build_health_v21_archive import preserve
from scripts.run_two_historical_health_v30 import evaluate
ROOT=Path(__file__).resolve().parents[1]
PARENT_SHA="511f3b18404d72d185d1e01c79258ac53d5f3aab66235092d9fd7c2e03c27f19"
MIG=ROOT/"schema/migrations/058_health_user_disease_supplement_v30.sql"
CUR=ROOT/"data/knowledge/phrase_library/health_v30/user_20261022_disease_curriculum.json"
BANK=ROOT/"data/knowledge/phrase_library/health_v30/user_20261022_pair_catalog.json"
TEMPLATE=ROOT/"data/knowledge/phrase_library/health_v30/severity_fixed_template.json"
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def build(parent,out,sealed,manifest):
    parent,out,sealed,manifest=map(Path,(parent,out,sealed,manifest))
    if out.exists() or sealed.exists():raise ValueError("Never overwrite previous full SQLite or archived evaluation")
    if sha(parent)!=PARENT_SHA:raise ValueError("Must use exact V2.9 complete full original source archive")
    curriculum=json.loads(CUR.read_text("utf8"))
    catalog=json.loads(BANK.read_text("utf8"))
    template=json.loads(TEMPLATE.read_text("utf8"))
    report=evaluate(db_path=parent)
    assert len(report["samples"])==2
    assert len(catalog["pairs"])>=35 and len(template["sections"])==11
    out.parent.mkdir(parents=True,exist_ok=True)
    with sqlite3.connect(parent.resolve().as_uri()+"?mode=ro",uri=True) as old,sqlite3.connect(out) as db:
        old.backup(db)
        db.executescript(MIG.read_text("utf8"))
        db.execute("PRAGMA foreign_keys=ON")
        with db:
            expected={
                "cases":194,"sections":43,
                "health_v22_customer_severity_sections":21,
                "health_v27_fixed_customer_sections":11,
                "health_v27_sealed_historical_predictions":2,
                "health_v28_historical_review":2,
                "health_v29_no_duplicate_medical_template":11,
                "health_v29_archival_readouts":2
            }
            for table,count in expected.items():
                n=db.execute('SELECT COUNT(*) FROM "'+table+'"').fetchone()[0]
                if n!=count:raise ValueError("Previously archived source rows changed "+table+":"+str(n))
            bad=db.execute("SELECT COUNT(*) FROM marriage_v16_post_inference_labels WHERE matches_initial_book_retrospective_result=0").fetchone()[0]
            if bad!=2:raise ValueError("Both old failed dev predictions must be preserved")
            for key,value in curriculum.items():
                db.execute("""INSERT INTO health_v30_method_curriculum
                     (method_key,content,origin,verification_state)
                     VALUES(?,?,'user_supplied_2026_10_22',?)""",
                    (key,json.dumps(value,ensure_ascii=False),
                     "indexed_not_all_executable" if key!="statuses" else "status_ledger"))
            for p in catalog["pairs"]:
                db.execute("""INSERT INTO health_v30_stem_pair_rules
                     (rule_id,heaven_stem,earth_stem,traditional_name,role_mode,
                      traditional_reading,source_status) VALUES(?,?,?,?,?,?,?)""",
                    (p["id"],p["heaven"],p["earth"],p["name"],p["mode"],p["meaning"],p["source"]))
            for x in catalog["composites"]:
                db.execute("""INSERT INTO health_v30_composite_rule_index
                     (composite_rule_id,name,required_conditions,traditional_reading,executable_status)
                     VALUES(?,?,?,?,?)""",
                    (x["id"],x["name"],x["conditions"],x["traditional_meaning"],x["calculation_status"]))
            for i,x in enumerate(template["sections"],1):
                db.execute("""INSERT INTO health_v30_fixed_template
                     (section_id,ordinal,title,format_text,no_gpt_runtime)
                     VALUES(?,?,?,?,1)""",(x["id"],i,x["title"],x["format"]))
            for pred in report["samples"]:
                db.execute("""INSERT INTO health_v30_historical_readout_seals
                     (case_id,readout_sha256,old_v27_sha256,author_outcome_used,
                      previously_approved_only_v27_case_2,v30_user_approved)
                     VALUES(?,?,?,0,?,0)""",
                   (pred["case_id"],pred["sha256"],pred["previous_v27_sha"],
                    int("19960523" in pred["case_id"])))
            db.execute("""INSERT INTO health_v30_version_receipt
                 (version,parent_full_sha256,event_families,old_source_sections,old_failed_dev_cases,
                  unreviewed_other_health_domains,imported_pairs,
                  no_real_medical_outcome_proof,old_rows_preserved,user_acceptance)
                 VALUES ('v3.0',?,194,43,2,4,?,1,1,'pending')""",
                 (PARENT_SHA,len(catalog["pairs"])))
        preserve(old,db)
        if db.execute("PRAGMA integrity_check").fetchone()[0]!="ok":
            raise ValueError("New full database integrity failure")
        if db.execute("PRAGMA foreign_key_check").fetchall():raise ValueError("New foreign keys broken")
        db.execute("VACUUM");db.commit()
    sealed.parent.mkdir(parents=True,exist_ok=True)
    sealed.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n","utf8")
    audit={
        "version":"V3.0","parent_sha256":PARENT_SHA,
        "new_full_sha256":sha(out),"sealed_sha256":sha(sealed),
        "cases":194,"source_sections":43,"prior_wrong_dev_cases":2,
        "source_type":"user_supplied_2026_10_22",
        "pair_rules":len(catalog["pairs"]),"composite_rules":len(catalog["composites"]),
        "template_slots":11,"previous_v27_v28_v29_seals_preserved":True,
        "other_four_health_intents_user_review":"not_approved",
        "user_approval":"pending",
        "no_gpt_or_network_runtime":True,"clinical_accuracy_verified":False}
    manifest.parent.mkdir(parents=True,exist_ok=True)
    manifest.write_text(json.dumps(audit,ensure_ascii=False,indent=2)+"\n","utf8")
    return audit
if __name__=="__main__":
    p=argparse.ArgumentParser()
    for key in ("parent","output","sealed","manifest"):p.add_argument("--"+key,required=True)
    a=p.parse_args()
    print(json.dumps(build(a.parent,a.output,a.sealed,a.manifest),ensure_ascii=False))
