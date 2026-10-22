"""V2.4 full SQLite exact V2.3 copy with corrected father prose templates."""
from __future__ import annotations
import argparse,hashlib,json,sqlite3
from pathlib import Path
from scripts.build_health_v21_archive import preserve

ROOT=Path(__file__).resolve().parents[1]
PARENT_SHA="2634ffff6f6033861a333cc0ee3007a261d76fb97bac3a597fa70f06a16569ad"
MIG=ROOT/"schema/migrations/052_health_severity_father_corrected_v24.sql"
TEMPLATE=ROOT/"data/knowledge/phrase_library/health_v24/severity_father_corrected_template.json"

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def build(parent,output,index_dir):
    parent,output,index_dir=map(Path,(parent,output,index_dir))
    if output.exists():
        raise ValueError("Immutable archive exists, refusing replacement")
    if sha(parent)!=PARENT_SHA:
        raise ValueError("Exact last complete V2.3 194-case SQLite required")
    pack=json.loads(TEMPLATE.read_text(encoding="utf8"))
    if pack["display_sections"]!=16 or len(pack["group"]["source_ids"])!=6:
        raise ValueError("Wrong 6-in-1 grouping")
    output.parent.mkdir(parents=True,exist_ok=True)
    with sqlite3.connect(parent.resolve().as_uri()+"?mode=ro",uri=True) as old, sqlite3.connect(output) as db:
        old.backup(db)
        db.executescript(MIG.read_text(encoding="utf8"))
        db.execute("PRAGMA foreign_keys=ON")
        with db:
            counts_required={"cases":194,"sections":43,
                "health_v20_actor_role_profiles":14,
                "health_v20_intent_templates":5,
                "health_v20_intent_steps":66,
                "health_v22_customer_severity_sections":21,
                "health_v23_display_groups":1,
                "health_v23_role_auxiliary":1}
            for table,need in counts_required.items():
                if db.execute('SELECT COUNT(*) FROM "'+table+'"').fetchone()[0]!=need:
                    raise ValueError("Lost old rows: "+table)
            bad=db.execute(
                "SELECT COUNT(*) FROM marriage_v16_post_inference_labels "
                "WHERE matches_initial_book_retrospective_result=0").fetchone()[0]
            if bad!=2: raise ValueError("Failed old training case records changed")
            for name,txt in [
                ("father_intro",pack["father_intro"]),
                ("father_patient",pack["father_patient"]),
                ("father_summary",pack["father_summary"]),
                ("illness_palace_six_in_one",pack["group"]["format"])]:
                db.execute("""INSERT INTO health_v24_corrected_father_prose
                    (template_key,template_text,deterministic_no_llm,
                     role_source_is_actual_year_stem,qian6_auxiliary_required)
                    VALUES(?,?,1,1,1)""",(name,txt))
            db.execute("""INSERT INTO health_v24_acceptance_audit
                 (version,parent_full_sha256,historical_cases,historical_sections,
                  old_wrong_development_cases,old_source_facets,merged_user_paragraphs,
                  old_other_unreviewed_intents,no_gpt_or_network,
                  real_medical_accuracy_verified,previous_rows_unchanged,user_acceptance)
                 VALUES('v2.4',?,194,43,2,21,16,4,1,0,1,'pending')""",(PARENT_SHA,))
        preserve(old,db)
        if db.execute("PRAGMA integrity_check").fetchone()[0]!="ok":
            raise ValueError("SQLite integrity failure")
        if db.execute("PRAGMA foreign_key_check").fetchall():
            raise ValueError("Foreign key violation")
        db.execute("VACUUM")
        db.commit()
        counts={table:db.execute('SELECT COUNT(*) FROM "'+table+'"').fetchone()[0]
                for table in ("cases","sections","health_v20_actor_role_profiles",
                             "health_v22_customer_severity_sections",
                             "health_v23_display_groups","health_v23_role_auxiliary",
                             "health_v24_corrected_father_prose","health_v24_acceptance_audit")}
    index_dir.mkdir(parents=True,exist_ok=True)
    data={"schema":"wengua_v24_fixed_father_case_194_original_book_full",
          "parent_full_sqlite_sha256":PARENT_SHA,
          "new_full_sqlite_sha256":sha(output),
          "original_cases_unchanged":194,"original_sections_unchanged":43,
          "earlier_two_failed_development_predictions_preserved":2,
          "original_21_facets_preserved":21,"visible_merged_paragraphs":16,
          "corrected_father_templates":4,
          "all_other_health_intents_unapproved":True,
          "pure_offline_no_llm":True,
          "patient_birth_year_not_inferred":True,
          "medical_accuracy_verified":False,
          "old_rows_identical":True,
          "user_approval":"pending",
          "counts":counts}
    (index_dir/"manifest.json").write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    return data

if __name__=="__main__":
    p=argparse.ArgumentParser()
    for name in ("base","output","index-dir"):p.add_argument("--"+name,required=True)
    a=p.parse_args()
    print(json.dumps(build(a.base,a.output,a.index_dir),ensure_ascii=False))
