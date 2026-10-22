"""Append V2.1 direction correction/calendar guards to exact complete V2.0."""
from __future__ import annotations
import argparse
import hashlib
import json
import sqlite3
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE_SHA="8c3914f47b3433d23ddf16b6ecf8fc2e2dc4380165646c010f49e87212fb913e"
BASE="WenguaApp_双书194案例_疾病五问事动态断词与人物关系V2_0_完整研究库.sqlite3"
OUT="WenguaApp_双书194案例_疾病有向生克修正与历法校验V2_1_完整研究库.sqlite3"
MIG=ROOT/"schema/migrations/049_health_v21_directed_palace_relations.sql"

RELATIONS={
 "克":"本宫克制病宫，传统制病之象",
 "受克":"本宫被病宫所克，传统医药或人物象受制",
 "生":"本宫生扶病宫，传统助病之象",
 "受生":"病宫生本宫，双方有生扶关系但不是本宫克病",
 "比和":"与病宫比和，未形成克病关系",
}

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def preserve(old,new):
    for (table,) in old.execute(
      "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"):
        cols=[c[1] for c in old.execute('PRAGMA table_info("'+table+'")')]
        keys=",".join('"'+k+'"' for k in cols)
        prior=list(old.execute('SELECT '+keys+' FROM "'+table+'"'))
        current=set(new.execute('SELECT '+keys+' FROM "'+table+'"'))
        if any(x not in current for x in prior):
            raise ValueError("Old book/source/previous error row mutated: "+table)

def build(parent,output,index_dir):
    parent,output,index_dir=map(Path,(parent,output,index_dir))
    if output.exists():
        raise ValueError("Refuse to overwrite versioned full SQLite")
    if sha(parent)!=BASE_SHA:
        raise ValueError("V2.1 requires EXACT latest complete V2.0 SHA")
    output.parent.mkdir(parents=True,exist_ok=True)
    with sqlite3.connect("file:"+str(parent.resolve())+"?mode=ro",uri=True) as old,sqlite3.connect(output) as db:
        old.backup(db)
        db.executescript(MIG.read_text(encoding="utf8"))
        db.execute("PRAGMA foreign_keys=ON")
        with db:
            counts={
              "cases":194,"sections":43,"marriage_v17_book_conditional_rules":27,
              "health_severity_v19_template_sections":21,
              "health_v20_actor_role_profiles":14,
              "health_v20_intent_templates":5,"health_v20_intent_steps":66,
            }
            for table,n in counts.items():
                if db.execute('SELECT COUNT(*) FROM "'+table+'"').fetchone()[0]!=n:
                    raise ValueError("Prior full historical database table lost: "+table)
            wrong=db.execute(
              "SELECT COUNT(*) FROM marriage_v16_post_inference_labels "
              "WHERE matches_initial_book_retrospective_result=0").fetchone()[0]
            if wrong!=2:raise ValueError("Original two wrong V1.6 dev answers erased")
            for rel,meaning in RELATIONS.items():
                db.execute("""INSERT INTO health_v21_directed_palace_relations
                           (relation_id,conditional_meaning,direction_is_strict)
                           VALUES (?,?,1)""",(rel,meaning))
            db.execute("""INSERT INTO health_v21_calendar_guard
                       (guard_id,valid_year_pillar_required_when_supplied,
                        valid_month_pillar_required_when_supplied,
                        month_branch_consistent_with_month_pillar,
                        hour_pillar_matches_actual_cast,no_invented_birth_year,
                        no_false_solar_term_certification)
                       VALUES ('health_v21',1,1,1,1,1,1)""")
            db.execute("""INSERT INTO health_v21_archive_audit
                      (version,parent_sqlite_sha256,old_source_events,
                       old_source_sections,old_v16_incorrect_development_answers,
                       old_health_role_profiles,old_health_intent_templates,
                       old_health_template_sections,old_rows_unchanged,
                       actual_clinical_predictive_validations)
                       VALUES ('v2.1',?,194,43,2,14,5,66,1,0)""",(BASE_SHA,))
        preserve(old,db)
        if db.execute("PRAGMA integrity_check").fetchone()[0]!="ok":
            raise ValueError("Failed sqlite integrity")
        if db.execute("PRAGMA foreign_key_check").fetchall():
            raise ValueError("Failed foreign key")
        db.execute("VACUUM")
        db.commit()
        totals={name:db.execute('SELECT COUNT(*) FROM "'+name+'"').fetchone()[0] for name in
          ("cases","sections","health_v20_actor_role_profiles",
           "health_v20_intent_templates","health_v20_intent_steps",
           "health_v21_directed_palace_relations","health_v21_calendar_guard",
           "health_v21_archive_audit")}
        if totals["health_v21_directed_palace_relations"]!=5 or totals["health_v21_calendar_guard"]!=1:
            raise ValueError("Versioned direction policies not complete")
    index_dir.mkdir(parents=True,exist_ok=True)
    info={
      "schema":"wengua_health_v21_directed_palace_and_calendar_guard",
      "parent_full_sqlite_sha256":BASE_SHA,
      "new_full_sqlite_sha256":sha(output),
      "previous_194_book_cases_unchanged":True,
      "previous_43_book_sections_unchanged":True,
      "previous_v16_two_wrong_development_cases_retained":2,
      "previous_health_v20_person_roles_retained":14,
      "previous_five_health_intents_retained":5,
      "previous_health_dynamic_templates_retained":66,
      "directional_relation_variants":5,
      "calendar_guard_protocols":1,
      "real_medical_prognoses_validated":0,
      "previous_rows_unchanged":True,
      "counts":totals,
    }
    (index_dir/"manifest.json").write_text(
       json.dumps(info,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return info

def main():
    p=argparse.ArgumentParser()
    for x in ("base","output","index-dir"):
        p.add_argument("--"+x,required=True)
    a=p.parse_args()
    print(json.dumps(build(a.base,a.output,a.index_dir),ensure_ascii=False))

if __name__=="__main__":
    main()
