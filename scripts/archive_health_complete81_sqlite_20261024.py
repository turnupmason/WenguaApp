"""Append-only FULL 194-case SQLite archive for user's 81 unique ordered pairs.

Source is the ALREADY archived current complete SQLite, never the original
legacy partial cases. Do not replace prior binary, table, failed CI or text.
"""
from __future__ import annotations
import hashlib
import json
import lzma
import shutil
import sqlite3
from pathlib import Path
from src.wengua.health_intrinsic_scoring_vnext import (
    CATALOG,USER_PATTERN_ROWS,PAIR_ROWS,VERSION,catalog_validation)

ROOT=Path(__file__).resolve().parents[1]
ARCH=ROOT/"archives/sqlite"
OLD=ARCH/"WenguaApp_双书194案例_用户星门神81格吉凶定位20261024_Vnext_完整研究库.sqlite3"
NAME="WenguaApp_双书194案例_新增四格_81组合完整断案20261024_VnextV3_完整研究库.sqlite3"
DEST=ARCH/NAME
MANIFEST=ARCH/"wengua_health_complete81_user_20261024_v3_manifest.json"
SOURCE_KEY="user_81_completed_20261024_v3_original_book_names_preserved"

def counts(conn):
    names=[x[0] for x in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")]
    return {name:conn.execute(
        'SELECT COUNT(*) FROM "'+name.replace('"','""')+'"').fetchone()[0] for name in names}

def build():
    if not OLD.is_file():raise FileNotFoundError("Historical complete archived 194-case SQL required")
    if any(x.exists() for x in (DEST,Path(str(DEST)+".xz"),MANIFEST)):
        raise FileExistsError("Never overwrite any already archived snapshot")
    if len(PAIR_ROWS)!=81 or len(USER_PATTERN_ROWS)!=82:raise AssertionError("Wrong 81/82 coverage")
    if catalog_validation()["missing_pair_keys"]:raise AssertionError("Missing pair")
    shutil.copy2(OLD,DEST)
    try:
        conn=sqlite3.connect(DEST)
        previous=counts(conn)
        conn.executescript("""
CREATE TABLE health_ordered_pair_current_v3_20261024(
 declaration_id INTEGER PRIMARY KEY,
 ordered_pair TEXT NOT NULL,
 top_stem TEXT NOT NULL,
 earth_stem TEXT NOT NULL,
 user_title TEXT NOT NULL,
 user_explanation TEXT NOT NULL,
 signed_default INTEGER,
 polarity TEXT NOT NULL,
 gate TEXT NOT NULL,
 ancient_book_original_excerpt TEXT,
 ancient_book_source_line INTEGER,
 ancient_book_excerpt_sha256 TEXT,
 name_differs_from_ancient INTEGER NOT NULL,
 source_version TEXT NOT NULL
);
CREATE INDEX health_pair_current81_idx_v3_20261024
 ON health_ordered_pair_current_v3_20261024(ordered_pair);
CREATE TABLE health_ordered_pair_coverage_v3_20261024(
 ordered_pair TEXT PRIMARY KEY,
 declarations INTEGER NOT NULL,
 completeness TEXT NOT NULL
);
CREATE TABLE health_user_book_name_conflict_v3_20261024(
 ordered_pair TEXT PRIMARY KEY,
 user_title TEXT NOT NULL,
 book_excerpt TEXT NOT NULL,
 book_line INTEGER NOT NULL,
 book_hash TEXT NOT NULL,
 preserve_both_versions INTEGER NOT NULL
);
CREATE TABLE health_runtime_rule_metadata_v3_20261024(
 rule TEXT PRIMARY KEY, datum TEXT NOT NULL
);
""")
        for i,row in enumerate(USER_PATTERN_ROWS,1):
            t,b=row["key"].split("/")
            val=row.get("baseline")
            if val is None and row.get("gate")=="unconditional":
                val=3 if row["polarity"]=="吉" else -3
            conn.execute(
                "INSERT INTO health_ordered_pair_current_v3_20261024 VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (i,row["key"],t,b,row["title"],row["explain"],val,
                 row["polarity"],row["gate"],
                 row.get("book_original_title_from_source"),
                 row.get("book_source_line"),
                 row.get("book_excerpt_sha256"),
                 int(bool(row.get("book_title_mismatch"))),
                 SOURCE_KEY))
        keys=[a+"/"+b for a in CATALOG["stems"] for b in CATALOG["stems"]]
        for pair in keys:
            amount=len(PAIR_ROWS.get(pair,()))
            status="two_original_variants_retained" if amount>1 else (
                "completed_unique_user_entry" if amount==1 else "still_missing")
            if not amount:raise AssertionError("Missing declared "+pair)
            conn.execute(
                "INSERT INTO health_ordered_pair_coverage_v3_20261024 VALUES(?,?,?)",
                (pair,amount,status))
        for row in CATALOG["user_20261024_new_four"]:
            conn.execute(
                "INSERT INTO health_user_book_name_conflict_v3_20261024 VALUES(?,?,?,?,?,1)",
                (row["key"],row["user"],row["original_excerpt"],
                 row["book_line"],row["book_excerpt_sha256"]))
        for k,v in {
            "current_score_model":VERSION,
            "new_4_signed_defaults":{"乙/壬":-3,"乙/癸":-3,"丙/癸":-3,"戊/乙":3},
            "current_user_distinct_ordered_combinations":81,
            "physical_declaration_rows_including_duplicated_庚己":82,
            "historical_78_old_user_declarations_retained":True,
            "new_relationship_language":"physician_chief_medicine_patient_hour_outcome_phrase_v1",
            "casting_user_chai_bu":"audit_with_24_solar_terms_and_middle_tianqin_kun2",
            "still_pending_source_conditions_are_not_invented":True,
            "contains_same_194_original_cases":True,
            "clinical_prediction":False,
        }.items():
            conn.execute(
                "INSERT INTO health_runtime_rule_metadata_v3_20261024 VALUES(?,?)",
                (k,json.dumps(v,ensure_ascii=False,sort_keys=True)))
        conn.commit()
        after=counts(conn)
        if {k:after[k] for k in previous}!=previous:
            raise AssertionError("Existing 194-case archive tables changed")
        assert after["health_ordered_pair_current_v3_20261024"]==82
        assert after["health_ordered_pair_coverage_v3_20261024"]==81
        assert after["health_user_book_name_conflict_v3_20261024"]==4
        assert conn.execute("PRAGMA integrity_check").fetchone()[0]=="ok"
        conn.close()
        raw=DEST.read_bytes()
        compressed=lzma.compress(raw,preset=6)
        Path(str(DEST)+".xz").write_bytes(compressed)
        sha=hashlib.sha256(raw).hexdigest()
        data={"version":SOURCE_KEY,"file":NAME,"bytes":len(raw),
              "sha256":sha,"compressed_bytes":len(compressed),
              "base_historical_file":OLD.name,
              "existing_old_table_counts_preserved":True,
              "old_table_count":len(previous),
              "new_tables":{
                 "health_ordered_pair_current_v3_20261024":82,
                 "health_ordered_pair_coverage_v3_20261024":81,
                 "health_user_book_name_conflict_v3_20261024":4,
                 "health_runtime_rule_metadata_v3_20261024":8},
              "integrity_check":"ok","never_replace_source":True,
              "not_clinical":True}
        MANIFEST.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        print(json.dumps(data,ensure_ascii=False,indent=2))
        return data
    except Exception:
        try:conn.close()
        except Exception:pass
        DEST.unlink(missing_ok=True)
        Path(str(DEST)+".xz").unlink(missing_ok=True)
        MANIFEST.unlink(missing_ok=True)
        raise

if __name__=="__main__":build()
