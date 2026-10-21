"""Append-only V1.9 archive: original 194 events + 21 health/severity slots."""
from __future__ import annotations
import argparse
import hashlib
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PARENT_SHA = "fbd2f6a5475e9f54cb9a98a42b1f96800cf8c1dd8d96f884951d900c7f287536"
PARENT_NAME = "WenguaApp_双书194案例_婚姻无年命作者取用方法V1_8_完整研究库.sqlite3"
NEW_NAME = "WenguaApp_双书194案例_疾病严重程度动态断词V1_9_完整研究库.sqlite3"
TEMPLATE = ROOT / "data/knowledge/phrase_library/health_severity_v1/template.json"
MIGRATION = ROOT / "schema/migrations/047_health_severity_dynamic_template_v19.sql"
PROTOCOL = "health.severity.dynamic_slots.v1.9"


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def preserve(old, new):
    """Prove old tables contain all old original and development-error rows."""
    for (name,) in old.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"):
        cols = [col[1] for col in old.execute('PRAGMA table_info("' + name + '")')]
        select = ",".join('"' + col + '"' for col in cols)
        prior = list(old.execute('SELECT ' + select + ' FROM "' + name + '"'))
        current = set(new.execute('SELECT ' + select + ' FROM "' + name + '"'))
        if any(row not in current for row in prior):
            raise ValueError("Parent database row mutated: " + name)


def build(parent, output, indexdir):
    parent, output, indexdir = map(Path, (parent, output, indexdir))
    if output.exists():
        raise ValueError("No replacing or rewriting a historical archive version")
    if digest(parent) != PARENT_SHA:
        raise ValueError("Expected SHA of current complete 194-case V1.8 parent")
    raw = TEMPLATE.read_bytes()
    template = json.loads(raw)
    sections = template["sections"]
    if (len(sections) != 21 or template["domain"] != "health" or
            template["intent"] != "severity"):
        raise ValueError("Expected exact health/severity 21-section template")
    output.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(
        "file:" + str(parent.resolve()) + "?mode=ro", uri=True
    ) as old, sqlite3.connect(output) as db:
        old.backup(db)
        db.executescript(MIGRATION.read_text(encoding="utf-8"))
        db.execute("PRAGMA foreign_keys=ON")
        with db:
            cases = db.execute("SELECT COUNT(*) FROM cases").fetchone()[0]
            sections_old = db.execute("SELECT COUNT(*) FROM sections").fetchone()[0]
            wrong = db.execute(
                "SELECT COUNT(*) FROM marriage_v16_post_inference_labels "
                "WHERE matches_initial_book_retrospective_result=0").fetchone()[0]
            rules = db.execute(
                "SELECT COUNT(*) FROM marriage_v17_book_conditional_rules").fetchone()[0]
            if (cases, sections_old, wrong, rules) != (194, 43, 2, 27):
                raise ValueError("194-case source data, previous misses or source rules missing")
            db.execute("""INSERT INTO health_severity_v19_protocol
                (protocol_id,domain,intent,version,parent_full_archive_sha256,
                 template_sha256,sections_count,medical_diagnosis_prohibited,status,note)
                VALUES (?, 'health','severity','v1.9',?,?,21,1,
                        'draft_research_not_clinical',?)""",
                (PROTOCOL, PARENT_SHA, hashlib.sha256(raw).hexdigest(),
                 "Dynamic book-source slots, no prewritten 1080x60 phrases."))
            for i, row in enumerate(sections, 1):
                db.execute("""INSERT INTO health_severity_v19_template_sections
                    (protocol_id,section_id,section_order,title,format_text,
                     source_links_json,no_historical_answers_in_initial_input)
                    VALUES (?,?,?,?,?,?,1)""",
                    (PROTOCOL, row["id"], i, row["title"], row["format"],
                     json.dumps(template["provenance"], ensure_ascii=False)))
            db.execute("""INSERT INTO health_severity_v19_archive_audit
                (version,parent_full_archive_sha256,historical_cases,
                 historical_sections,original_v16_misses,retained_v17_condition_rules,
                 detailed_severity_sections,all_old_rows_unchanged,
                 newly_validated_real_patient_prognoses)
                VALUES ('v1.9',?,194,43,2,27,21,1,0)""", (PARENT_SHA,))
        preserve(old, db)
        if (db.execute("PRAGMA integrity_check").fetchone()[0] != "ok" or
                db.execute("PRAGMA foreign_key_check").fetchall()):
            raise ValueError("New SQLite is not source-preserving and valid")
        db.execute("VACUUM")
        db.commit()
        counts = {tab: db.execute('SELECT COUNT(*) FROM "'+tab+'"').fetchone()[0]
                  for tab in ("cases", "sections", "marriage_v16_post_inference_labels",
                              "marriage_v17_book_conditional_rules",
                              "marriage_v18_optional_year_scene_methods",
                              "health_severity_v19_protocol",
                              "health_severity_v19_template_sections",
                              "health_severity_v19_archive_audit")}
        if (counts["cases"], counts["sections"],
                counts["health_severity_v19_template_sections"],
                counts["marriage_v18_optional_year_scene_methods"]) != (194, 43, 21, 22):
            raise ValueError("Expected parent and appended row counts not preserved")
    result = {
        "schema": "wengua_v19_health_severity_dynamic_template_complete_archive",
        "parent_sha256": PARENT_SHA,
        "new_sha256": digest(output),
        "original_194_cases_unchanged": True,
        "original_43_sections_unchanged": True,
        "earlier_misses_retained": 2,
        "prior_marriage_rules_retained": 27,
        "health_severity_template_sections": 21,
        "new_real_world_clinical_validation": 0,
        "source_template_sha256": hashlib.sha256(raw).hexdigest(),
        "counts": counts,
    }
    indexdir.mkdir(parents=True, exist_ok=True)
    (indexdir / "manifest.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def main():
    parser = argparse.ArgumentParser()
    for flag in ("base", "output", "index-dir"):
        parser.add_argument("--" + flag, required=True)
    args = parser.parse_args()
    print(json.dumps(build(args.base, args.output, args.index_dir), ensure_ascii=False))


if __name__ == "__main__":
    main()
