"""Create NEW full SQLite snapshot; never overwrite the old 194-case archive."""
from __future__ import annotations
from pathlib import Path
import hashlib,json,lzma,shutil,sqlite3

from src.wengua.health_intrinsic_scoring_vnext import (
    CATALOG,STARS,DOORS,GODS,GOD_RELATIONS,
    USER_PATTERN_ROWS,catalog_validation)

ROOT=Path(__file__).resolve().parents[1]
ARCH=ROOT/"archives/sqlite"
BASE=ARCH/"WenguaApp_双书194案例_81原书病情格局校核V4_1_完整研究库.sqlite3"
NAME="WenguaApp_双书194案例_用户星门神81格吉凶定位20261024_Vnext_完整研究库.sqlite3"
DEST=ARCH/NAME
SOURCE_VERSION="user_intrinsic_200_grid_20261024_v1"

def table_counts(con):
    names=[r[0] for r in con.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")]
    return {name:con.execute('SELECT COUNT(*) FROM "'+name.replace('"','""')+'"').fetchone()[0]
            for name in names}

def create_db():
    if not BASE.is_file():raise FileNotFoundError("Need existing complete 194-case SQLite, do not fabricate its tables")
    if DEST.exists():raise FileExistsError("Do not overwrite archive: "+str(DEST))
    shutil.copy2(BASE,DEST)
    try:
        con=sqlite3.connect(DEST)
        original=table_counts(con)
        con.execute("PRAGMA foreign_keys=ON")
        con.executescript("""
CREATE TABLE health_signifier_baselines_vnext_20261024 (
 symbol_kind TEXT NOT NULL, symbol TEXT NOT NULL,
 default_signed INTEGER NOT NULL, source_version TEXT NOT NULL,
 independent_month_stage INTEGER NOT NULL,
 PRIMARY KEY(symbol_kind,symbol)
);
CREATE TABLE health_god_palace_strength_vnext_20261024 (
 physical_relation TEXT PRIMARY KEY,
 strength_label TEXT NOT NULL, source_version TEXT NOT NULL
);
CREATE TABLE health_ordered_pair_polarity_vnext_20261024 (
 declaration_id INTEGER PRIMARY KEY,
 ordered_pair TEXT NOT NULL, top_stem TEXT NOT NULL,
 earth_stem TEXT NOT NULL, user_title TEXT NOT NULL,
 original_user_meaning TEXT NOT NULL, category TEXT NOT NULL,
 explicit_polarity TEXT NOT NULL,
 gate TEXT NOT NULL, source_version TEXT NOT NULL
);
CREATE INDEX idx_health_user_pair_vnext ON
 health_ordered_pair_polarity_vnext_20261024(ordered_pair);
CREATE TABLE health_ordered_pair_coverage_vnext_20261024 (
 ordered_pair TEXT PRIMARY KEY, top_stem TEXT NOT NULL,
 earth_stem TEXT NOT NULL, declarations INTEGER NOT NULL,
 status TEXT NOT NULL, never_replace_old_81_source INTEGER NOT NULL DEFAULT 1
);
CREATE TABLE health_score_rule_metadata_vnext_20261024 (
 rule_name TEXT PRIMARY KEY, rule_value_json TEXT NOT NULL,
 source_version TEXT NOT NULL
);
""")
        for typ,items in (("star",STARS),("door",DOORS),("deity",GODS)):
            con.executemany(
                "INSERT INTO health_signifier_baselines_vnext_20261024 VALUES(?,?,?,?,?)",
                [(typ,name,value,SOURCE_VERSION,1 if typ=="deity" else 0)
                 for name,value in items.items()])
        con.executemany(
            "INSERT INTO health_god_palace_strength_vnext_20261024 VALUES(?,?,?)",
            [(rel,tier,SOURCE_VERSION) for rel,tier in GOD_RELATIONS.items()])
        con.executemany(
            "INSERT INTO health_ordered_pair_polarity_vnext_20261024 VALUES(?,?,?,?,?,?,?,?,?,?)",
            [(i,r["key"],*r["key"].split("/"),r["title"],r["explain"],
              r["group"],r["polarity"],r["gate"],SOURCE_VERSION)
             for i,r in enumerate(USER_PATTERN_ROWS,1)])
        keys=[a+"/"+b for a in CATALOG["stems"] for b in CATALOG["stems"]]
        for k in keys:
            n=sum(1 for item in USER_PATTERN_ROWS if item["key"]==k)
            status=("missing_new_user_classification" if n==0 else
                    "duplicate_conditional_tracks" if n>1 else "one_user_entry")
            con.execute(
                "INSERT INTO health_ordered_pair_coverage_vnext_20261024 VALUES(?,?,?,?,?,1)",
                (k,*k.split("/"),n,status))
        for k,v in {
            "scope":"symbolic_health_severity_vnext_only",
            "user_star_baselines":STARS,
            "user_door_baselines":DOORS,
            "user_god_baselines":GODS,
            "god_month_stage":"none",
            "200_grid_still_applies":"monthly_physical_star_and_door_strength",
            "user_ordered81_coverage":catalog_validation(),
            "old_book_health_exceptions":["戊/丙","丙/戊","丁/壬","丙/辛"],
            "existing_cases_unchanged":True,
            "unknown_final_sum_gt_five":"defer_no_clamp",
            "no_clinical_claims":True,
        }.items():
            con.execute(
                "INSERT INTO health_score_rule_metadata_vnext_20261024 VALUES(?,?,?)",
                (k,json.dumps(v,ensure_ascii=False,sort_keys=True),SOURCE_VERSION))
        con.commit()
        after=table_counts(con)
        if {k:after.get(k) for k in original}!=original:
            raise AssertionError("Original historical SQLite records changed")
        assert after["health_signifier_baselines_vnext_20261024"]==25
        assert after["health_god_palace_strength_vnext_20261024"]==5
        assert after["health_ordered_pair_polarity_vnext_20261024"]==78
        assert after["health_ordered_pair_coverage_vnext_20261024"]==81
        assert con.execute("PRAGMA integrity_check").fetchone()[0]=="ok"
        con.close()
        raw=DEST.read_bytes()
        compressed=lzma.compress(raw,preset=6)
        compressed_path=Path(str(DEST)+".xz")
        compressed_path.write_bytes(compressed)
        manifest={
            "status":"append_only_complete_SQLite_snap_vnext",
            "source_sqlite":BASE.name,"new_sqlite":DEST.name,
            "size_bytes":len(raw),"xz_bytes":len(compressed),
            "sha256":hashlib.sha256(raw).hexdigest(),
            "xz_sha256":hashlib.sha256(compressed).hexdigest(),
            "original_sqlite_table_rows_unchanged":len(original),
            "catalog_table_rows":{"intrinsic_baselines":25,
                "god_physical_relations":5,"user_pattern_rows":78,
                "ordered_pair_positions":81,"unique_user_pairs":77},
            "unclassified_user_pairs":catalog_validation()["missing_pair_keys"],
            "ambiguous_user_pairs":catalog_validation()["duplicate"],
            "not_a_medical_assessment":True}
        manifest_path=ARCH/"wengua_health_intrinsic_20261024_manifest.json"
        if manifest_path.exists():raise FileExistsError("Do not overwrite existing manifest")
        manifest_path.write_text(
            json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",
            encoding="utf-8")
        print("WENGUA_NEW_SQLITE "+json.dumps(
            manifest,ensure_ascii=False,separators=(",",":")))
        return manifest
    except BaseException:
        try:con.close()
        except Exception:pass
        # Only remove the newly generated incomplete output; leave historical
        # V4.1, previous versions and failed run logs untouched.
        if DEST.exists():DEST.unlink()
        raise

def main():
    create_db()
if __name__=="__main__":main()
