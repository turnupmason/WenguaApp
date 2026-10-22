"""Immutable V2.3 full-book archive; merge disease palace and father aux only."""
from __future__ import annotations
import argparse,hashlib,json,sqlite3
from pathlib import Path
from scripts.build_health_v21_archive import preserve
ROOT=Path(__file__).resolve().parents[1]
PARENT_SHA="db993ba9f5ff6511f2fb4104d881a3e9008f1f4cc19df7e68cbbe788f24a15f6"
PARENT_NAME="WenguaApp_双书194案例_疾病轻重纯离线21段断词V2_2_完整研究库.sqlite3"
NEW_NAME="WenguaApp_双书194案例_父亲测病与病宫合并断词V2_3_完整研究库.sqlite3"
MIG=ROOT/"schema/migrations/051_health_severity_father_grouped_v23.sql"
TEMPLATE=ROOT/"data/knowledge/phrase_library/health_v23/severity_grouped_template.json"

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def build(parent,output,index_dir):
    parent,output,index_dir=map(Path,(parent,output,index_dir))
    if output.exists():
        raise ValueError("Never overwrite an immutable SQLite archive")
    if sha(parent)!=PARENT_SHA:
        raise ValueError("Exact complete V2.2 194-event archive is required")
    p=json.loads(TEMPLATE.read_text(encoding="utf8"))
    if len(p["group"]["source_ids"])!=6 or p["display_sections"]!=16:
        raise ValueError("Unexpected six-to-one group rule")
    output.parent.mkdir(parents=True,exist_ok=True)
    with sqlite3.connect(parent.resolve().as_uri()+"?mode=ro",uri=True) as old, sqlite3.connect(output) as db:
        old.backup(db)
        db.executescript(MIG.read_text(encoding="utf8"))
        db.execute("PRAGMA foreign_keys=ON")
        with db:
            expected={
                "cases":194,"sections":43,
                "health_v20_actor_role_profiles":14,
                "health_v20_intent_templates":5,
                "health_v20_intent_steps":66,
                "health_v21_directed_palace_relations":5,
                "health_v22_customer_severity_sections":21
            }
            for table,n in expected.items():
                if db.execute('SELECT COUNT(*) FROM "'+table+'"').fetchone()[0]!=n:
                    raise ValueError("Parent historical content lost: "+table)
            wrong=db.execute(
                "SELECT COUNT(*) FROM marriage_v16_post_inference_labels "
                "WHERE matches_initial_book_retrospective_result=0").fetchone()[0]
            if wrong!=2:
                raise ValueError("Prior two failed dev predictions must remain")
            group=p["group"]
            db.execute("""INSERT INTO health_v23_display_groups
                         (group_id,title,source_sections_json,group_format,
                          merge_without_dropping_source,deterministic_no_llm,
                          user_review_status)
                         VALUES (?,?,?,?,1,1,'pending')""",
                       (group["id"],group["title"],
                        json.dumps(group["source_ids"],ensure_ascii=False),
                        group["format"]))
            db.execute("""INSERT INTO health_v23_role_auxiliary
                         (role_id,auxiliary_palace,detailed_text,evidence_text,
                          summary_text,requires_patient_birth_year)
                         VALUES ('father',6,?,?,?,0)""",
                       (p["father_aux"]["full"],p["father_aux"]["evidence"],
                        p["father_aux"]["summary"]))
            db.execute("""INSERT INTO health_v23_acceptance_audit
                       (audit_id,parent_exact_sha256,historical_cases,
                        historical_sections,old_wrong_development_cases,
                        parent_customer_sections,merged_source_sections,
                        presented_sections,other_four_intents_still_unapproved,
                        real_patient_birth_year_inferred,old_tables_preserved,
                        actual_medical_accuracy_verified,user_acceptance)
                       VALUES ('v2.3',?,194,43,2,21,6,16,4,0,1,0,'pending')""",
                       (PARENT_SHA,))
        preserve(old,db)
        if db.execute("PRAGMA integrity_check").fetchone()[0]!="ok":
            raise ValueError("DB corruption")
        if db.execute("PRAGMA foreign_key_check").fetchall():
            raise ValueError("Broken foreign keys")
        db.execute("VACUUM")
        db.commit()
        counts={name:db.execute('SELECT COUNT(*) FROM "'+name+'"').fetchone()[0] for name in
            ("cases","sections","health_v20_actor_role_profiles",
             "health_v20_intent_steps","health_v22_customer_severity_sections",
             "health_v23_display_groups","health_v23_role_auxiliary",
             "health_v23_acceptance_audit")}
    if counts["health_v23_display_groups"]!=1 or counts["health_v23_role_auxiliary"]!=1:
        raise ValueError("Missing grouping or father role")
    manifest={
        "schema":"wengua_v23_full_194_case_father_health_grouped",
        "exact_parent_v22_sha256":PARENT_SHA,
        "new_full_v23_sha256":sha(output),
        "source_cases_unchanged":194,"source_sections_unchanged":43,
        "failed_development_examples_preserved":2,
        "all_v22_21_source_sections_preserved":True,
        "six_same_palace_sections_combined_into_one":True,
        "display_paragraphs":16,
        "new_year_stem_father_and_qian6_aux":True,
        "four_other_health_intents_approved":False,
        "runtime_llm_calls":0,
        "actual_illness_outcome_validation":0,
        "user_review_status":"pending",
        "all_prior_rows_identical":True,
        "counts":counts
    }
    index_dir.mkdir(parents=True,exist_ok=True)
    (index_dir/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    return manifest

if __name__=="__main__":
    p=argparse.ArgumentParser()
    for option in ("base","output","index-dir"):
        p.add_argument("--"+option,required=True)
    a=p.parse_args()
    print(json.dumps(build(a.base,a.output,a.index_dir),ensure_ascii=False))
