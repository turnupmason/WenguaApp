"""V2.0 immutable SQLite: 14 conditional patient roles + 5 distinct health intents."""
from __future__ import annotations
import argparse
import hashlib
import json
import sqlite3
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PARENT="WenguaApp_双书194案例_疾病严重程度动态断词V1_9_完整研究库.sqlite3"
OUTPUT="WenguaApp_双书194案例_疾病五问事动态断词与人物关系V2_0_完整研究库.sqlite3"
PARENT_SHA="b0b2aeaf9bfbb94be3f435391e8fb2b066b9c9da7a5a6675e3d22cf50c6ce55f"
DATA=ROOT/"data/knowledge/phrase_library/health_v20"
MIGRATION=ROOT/"schema/migrations/048_health_five_intents_actor_roles_v20.sql"
SOURCES={
 "roles":DATA/"actor_profiles.json",
 "severity":DATA/"severity_template.json",
 "other":DATA/"other_intent_templates.json",
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _preserve(old,new):
    for (table,) in old.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"):
        cols=[x[1] for x in old.execute('PRAGMA table_info("'+table+'")')]
        clause=",".join('"'+c+'"' for c in cols)
        prior=list(old.execute('SELECT '+clause+' FROM "'+table+'"'))
        current=set(new.execute('SELECT '+clause+' FROM "'+table+'"'))
        if any(x not in current for x in prior):
            raise ValueError("Old database source / wrong outcome row changed: "+table)


def build(parent,output,manifest_dir):
    parent,output,manifest_dir=map(Path,(parent,output,manifest_dir))
    if output.exists():
        raise ValueError("Existing immutable SQLite must not be overwritten")
    if sha(parent)!=PARENT_SHA:
        raise ValueError("Parent is not exact V1.9 complete 194-case full SQLite")
    profiles=json.loads(SOURCES["roles"].read_text(encoding="utf-8"))
    severe=json.loads(SOURCES["severity"].read_text(encoding="utf-8"))
    other=json.loads(SOURCES["other"].read_text(encoding="utf-8"))
    all_intents={"severity":severe}
    for key,item in other["descriptions"].items():
        all_intents[key]={
          "schema":other["schema"],"domain":"health","intent":key,
          "sections":item["sections"],"method":item["special_method"],
          "source":item["source"]}
    expected={"severity":21,"treatment":12,"discharge":12,
              "surgery":10,"travel_for_treatment":11}
    if len(profiles["profiles"])!=14 or {k:len(v["sections"]) for k,v in all_intents.items()}!=expected:
        raise ValueError("Unexpected role or sub-intent coverage")
    output.parent.mkdir(parents=True,exist_ok=True)
    with sqlite3.connect("file:"+str(parent.resolve())+"?mode=ro",
                         uri=True) as old,sqlite3.connect(output) as new:
        old.backup(new)
        new.executescript(MIGRATION.read_text(encoding="utf-8"))
        new.execute("PRAGMA foreign_keys=ON")
        with new:
            retained={
                "cases":194,"sections":43,"marriage_v17_book_conditional_rules":27,
                "marriage_v18_optional_year_scene_methods":22,
                "health_severity_v19_template_sections":21,
            }
            for table,expect in retained.items():
                if new.execute('SELECT COUNT(*) FROM "'+table+'"').fetchone()[0]!=expect:
                    raise ValueError("Old domain content lost: "+table)
            wrong=new.execute(
                "SELECT COUNT(*) FROM marriage_v16_post_inference_labels "
                "WHERE matches_initial_book_retrospective_result=0").fetchone()[0]
            if wrong!=2:
                raise ValueError("Old failed predictions cannot disappear")
            for profile in profiles["profiles"]:
                new.execute("""INSERT INTO health_v20_actor_role_profiles
                 (profile_id,label,profile_json,reference_count)
                 VALUES(?,?,?,?)""",
                 (profile["id"],profile["label"],
                  json.dumps(profile,ensure_ascii=False),
                  len(profile["references"])))
            for intent,definition in all_intents.items():
                raw=json.dumps(definition,ensure_ascii=False,sort_keys=True)
                new.execute("""INSERT INTO health_v20_intent_templates
                 (intent,title,template_hash_sha256,template_json,
                  sections_count,author_method_different_from_severity)
                 VALUES(?,?,?,?,?,?)""",
                 (intent,other["descriptions"][intent]["title"] if intent!="severity" else "病情严重程度",
                  hashlib.sha256(raw.encode("utf-8")).hexdigest(),raw,
                  len(definition["sections"]),int(intent!="severity")))
                for n,s in enumerate(definition["sections"],1):
                    new.execute("""INSERT INTO health_v20_intent_steps
                     (intent,ordinal,section_id,title,template_text)
                     VALUES(?,?,?,?,?)""",
                     (intent,n,s["id"],s["title"],s["format"]))
            new.execute("""INSERT INTO health_v20_archive_audit
             (audit_id,parent_full_archive_sha256,source_event_families,
              source_sections,previous_dev_misses,previous_conditional_rules,
              older_health_v19_template_rows,source_old_rows_unchanged,
              independent_clinical_accuracy_estimate)
             VALUES ('v20',?,194,43,2,27,21,1,0)""",(PARENT_SHA,))
        _preserve(old,new)
        if new.execute("PRAGMA integrity_check").fetchone()[0]!="ok":
            raise ValueError("SQLite integrity failed")
        if new.execute("PRAGMA foreign_key_check").fetchall():
            raise ValueError("SQLite FK references failed")
        new.execute("VACUUM")
        new.commit()
        counts={k:new.execute('SELECT COUNT(*) FROM "'+k+'"').fetchone()[0]
                for k in ("cases","sections","marriage_v16_post_inference_labels",
                          "marriage_v17_book_conditional_rules",
                          "health_severity_v19_template_sections",
                          "health_v20_actor_role_profiles",
                          "health_v20_intent_templates",
                          "health_v20_intent_steps","health_v20_archive_audit")}
    if counts["health_v20_intent_steps"]!=66 or counts["health_v20_actor_role_profiles"]!=14:
        raise ValueError("New role and template text rows incomplete")
    result={
      "schema":"wengua_health_v20_five_distinct_intent_194_case_append_only",
      "parent_full_sqlite_sha256":PARENT_SHA,
      "new_full_sqlite_sha256":sha(output),
      "original_historical_case_families_unchanged":194,
      "original_source_sections_unchanged":43,
      "previous_two_dev_errors_preserved":2,
      "previous_27_author_combinator_rules_preserved":27,
      "prior_health_21_sections_preserved":21,
      "patient_role_profiles":14,
      "separate_health_intents":expected,
      "total_dynamic_template_sections":66,
      "new_independently_verified_clinical_predictions":0,
      "all_old_tables_and_rows_identical":True,
      "source_files_sha256":{name:sha(path) for name,path in SOURCES.items()},
      "counts":counts
    }
    manifest_dir.mkdir(parents=True,exist_ok=True)
    (manifest_dir/"manifest.json").write_text(
       json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return result


def main():
    ap=argparse.ArgumentParser()
    for x in ("base","output","index-dir"):
        ap.add_argument("--"+x,required=True)
    opts=ap.parse_args()
    print(json.dumps(build(opts.base,opts.output,opts.index_dir),
                     ensure_ascii=False,sort_keys=True))


if __name__=="__main__":
    main()
