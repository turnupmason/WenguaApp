"""Append-only full 194-case V2.2 with 21 strict offline customer sections."""
from __future__ import annotations
import argparse,hashlib,json,sqlite3
from pathlib import Path
from scripts.build_health_v21_archive import preserve

ROOT=Path(__file__).resolve().parents[1]
PARENT_SHA="25d95ed8df42ed0739d82cc930fcd5127ba187740c0b871fc3ae488d69bc81f3"
PARENT_NAME="WenguaApp_双书194案例_疾病有向生克修正与历法校验V2_1_完整研究库.sqlite3"
NEW_NAME="WenguaApp_双书194案例_疾病轻重纯离线21段断词V2_2_完整研究库.sqlite3"
TEMPLATE=ROOT/"data/knowledge/phrase_library/health_v22/severity_template.json"
MIG=ROOT/"schema/migrations/050_health_severity_offline_customer_language_v22.sql"


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def build(parent,output,index_dir):
    parent,output,index_dir=map(Path,(parent,output,index_dir))
    if output.exists():
        raise ValueError("Refuse to overwrite immutable V2.2 SQLite")
    if digest(parent)!=PARENT_SHA:
        raise ValueError("Must use exact V2.1 latest full 194 case SQLite parent")
    meta=json.loads(TEMPLATE.read_text(encoding="utf8"))
    if meta.get("intent")!="severity" or len(meta["sections"])!=21:
        raise ValueError("Exactly one approved 21 section health intent")
    output.parent.mkdir(parents=True,exist_ok=True)
    with sqlite3.connect(parent.as_uri()+"?mode=ro",uri=True) as old, sqlite3.connect(output) as db:
        old.backup(db)
        db.executescript(MIG.read_text(encoding="utf8"))
        db.execute("PRAGMA foreign_keys=ON")
        with db:
            for name,cnt in {"cases":194,"sections":43,
                "health_v20_actor_role_profiles":14,
                "health_v20_intent_templates":5,
                "health_v20_intent_steps":66,
                "health_v21_directed_palace_relations":5}.items():
                actual=db.execute('SELECT COUNT(*) FROM "'+name+'"').fetchone()[0]
                if actual!=cnt:raise AssertionError((name,actual,cnt))
            misses=db.execute(
              "SELECT COUNT(*) FROM marriage_v16_post_inference_labels "
              "WHERE matches_initial_book_retrospective_result=0").fetchone()[0]
            if misses!=2:raise AssertionError("Must preserve both historical dev mistakes")
            for i,s in enumerate(meta["sections"],1):
                db.execute("""INSERT INTO health_v22_customer_severity_sections
                            (ordinal,section_id,heading,template_text,
                             deterministic_python_only,
                             customer_language_no_engine_explanation,
                             distinct_from_internal_audit)
                            VALUES (?,?,?,?,1,1,1)""",
                         (i,s["id"],s["title"],s["format"]))
            result=db.execute(
                "SELECT original_excerpt,source_start_line FROM semantic_assertions "
                "WHERE concept_id='heaven_over_earth:壬:辛' "
                "ORDER BY source_start_line LIMIT 1").fetchone()
            if not result or "螣蛇相缠" not in result[0] or result[1]!=661:
                raise ValueError("Missing exact original source of 壬加辛")
            db.execute("""INSERT INTO health_v22_source_pair_explanations
                        (source_pair_id,source_line,original_excerpt,
                         traditional_formation_name,context,is_clinical_diagnosis)
                        VALUES (?,?,?,?,?,0)""",
                       ("heaven_over_earth:壬:辛",result[1],result[0],
                        "螣蛇相缠","疾病主用神宫天地干同宫时的传统阻滞辅助象"))
            db.execute("""INSERT INTO health_v22_acceptance_receipt
                        (receipt_id,parent_sha256,previous_original_case_count,
                         previous_original_section_count,
                         previous_v16_dev_wrong_count,
                         previous_health_v20_patient_roles,
                         previous_unapproved_other_health_templates,
                         previous_v20_draft_template_sections,
                         new_user_approved_sections,current_user_acceptance,
                         no_llm_customer_rewrite,all_previous_rows_kept)
                        VALUES ('v2.2',?,194,43,2,14,4,66,21,'pending',1,1)""",(PARENT_SHA,))
        preserve(old,db)
        if db.execute("PRAGMA integrity_check").fetchone()[0]!="ok":
            raise ValueError("SQLite integrity failure")
        if db.execute("PRAGMA foreign_key_check").fetchall():
            raise ValueError("SQLite foreign key failure")
        db.execute("VACUUM")
        db.commit()
        counts={t:db.execute('SELECT COUNT(*) FROM "'+t+'"').fetchone()[0]
         for t in ("cases","sections","health_v20_actor_role_profiles",
                  "health_v20_intent_steps","health_v21_directed_palace_relations",
                  "health_v22_customer_severity_sections",
                  "health_v22_source_pair_explanations",
                  "health_v22_acceptance_receipt")}
    manifest={
        "schema":"health_severity_pure_offline_v22_full_194_case_parent",
        "parent_sha256":PARENT_SHA,"full_new_sha256":digest(output),
        "original_event_families":194,"original_sections":43,
        "old_v16_wrong_case_count":2,
        "14_prior_patient_roles_unchanged":True,
        "4_unapproved_health_intents_frozen":True,
        "21_customer_facing_sections":21,
        "no_ai_generation_or_llm_polish":True,
        "actual_user_acceptance":"pending",
        "source_original_pair":"heaven_over_earth:壬:辛",
        "original_pair_source_line":661,
        "unchanged_all_old_rows":True,
        "counts":counts,
    }
    index_dir.mkdir(parents=True,exist_ok=True)
    (index_dir/"manifest.json").write_text(
       json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    return manifest


if __name__=="__main__":
    ap=argparse.ArgumentParser()
    for key in ("base","output","index-dir"):
        ap.add_argument("--"+key,required=True)
    a=ap.parse_args()
    print(json.dumps(build(a.base,a.output,a.index_dir),ensure_ascii=False))
