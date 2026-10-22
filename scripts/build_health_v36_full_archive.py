"""V3.6 immutable full SQLite from exact V3.5, preserving every older failed seal."""
from __future__ import annotations
import argparse,hashlib,json,lzma,sqlite3
from pathlib import Path
from scripts.build_health_v21_archive import preserve
from scripts.replay_all_historical_health_v36 import evaluate,PARENT_SHA
ROOT=Path(__file__).resolve().parents[1]
MIG=ROOT/"schema/migrations/064_health_hour_horse_value_door_v36.sql"
def sha(f):return hashlib.sha256(Path(f).read_bytes()).hexdigest()
def build(parent,output,seal,manifest):
    parent,output,seal,manifest=map(Path,(parent,output,seal,manifest))
    xz=Path(str(output)+".xz")
    if any(p.exists() for p in (output,seal,manifest,xz)):
        raise ValueError("Immutable previous archive present; never overwrite")
    if sha(parent)!=PARENT_SHA:raise ValueError("Only verified V3.5 full parent accepted")
    r=evaluate(db_path=parent)
    if r["counts"]!={"rendered":12,"blocked":0} or len(r["samples"])!=12:
        raise ValueError("Expected all twelve original book cases to render")
    output.parent.mkdir(parents=True,exist_ok=True)
    with sqlite3.connect(parent.resolve().as_uri()+"?mode=ro",uri=True) as old,sqlite3.connect(output) as new:
        old.backup(new)
        new.executescript(MIG.read_text("utf8"))
        new.execute("PRAGMA foreign_keys=ON")
        with new:
            for tab,n in (("cases",194),("sections",43),("health_v33_all_historical_health_replay",12),
                          ("health_v34_role_and_condition_replay",12),("health_v35_patient_first_replay",12),
                          ("health_v30_stem_pair_rules",42),("health_v30_composite_rule_index",17)):
                if new.execute('SELECT count(*) FROM "'+tab+'"').fetchone()[0]!=n:raise ValueError("Lost previous rows "+tab)
            if new.execute("SELECT count(*) FROM marriage_v16_post_inference_labels WHERE matches_initial_book_retrospective_result=0").fetchone()[0]!=2:
                raise ValueError("Two prior failed developer predictions must remain")
            for x in r["samples"]:
                items={q["id"]:q for q in x["corrected_17_composite_predicates"]}
                horse=items["health_composite_12"]["evidence"][0]
                new.execute("""INSERT INTO health_v36_source_horse_and_value_door VALUES(?,?,?,0,1,?,?,1,?,'pending')""",
                    (x["family_id"],x["source_hour"],horse["horse_branch"],
                     int(items["health_composite_07"]["state"]=="triggered"),
                     int(items["health_composite_08"]["state"]=="triggered"),x["sha256"]))
            new.execute("""INSERT INTO health_v36_full_archive_audit VALUES
                     ('v3.6',?,194,43,2,12,42,17,1,'pending')""",(PARENT_SHA,))
        preserve(old,new)
        if new.execute("PRAGMA integrity_check").fetchone()[0]!="ok":raise ValueError("Bad sqlite integrity")
        if new.execute("PRAGMA foreign_key_check").fetchall():raise ValueError("Invalid foreign keys")
        new.execute("VACUUM");new.commit()
    seal.parent.mkdir(parents=True,exist_ok=True)
    seal.write_text(json.dumps(r,ensure_ascii=False,indent=2)+"\n","utf8")
    xz.write_bytes(lzma.compress(output.read_bytes(),preset=6))
    receipt={"schema":"wengua_health_v36_complete_book_source_four_symbols",
        "full_sqlite_sha256":sha(output),"full_sqlite_bytes":output.stat().st_size,
        "full_sqlite_xz_sha256":sha(xz),
        "exact_parent_v35_sha256":sha(parent),"twelve_readouts_sha256":sha(seal),
        "book_source_families":194,"source_chapters":43,
        "historical_health_source_families":12,"all_twelve_rendered":True,
        "42_ordered_pairs_in_each_case":True,"17_composite_audits_in_each_case":True,
        "three_wonders_and_jade_woman_actual_value_door_checked":True,
        "horse_uses_source_actual_hour_branch":True,
        "unsupported_source_conditions_remain_explicit_unknown":True,
        "previous_all_readouts_and_failures_unchanged":True,
        "not_an_independent_secret_blind_test":True,"real_medical_predictiveness":False,
        "user_approval":"pending","ui_status":"not_started"}
    manifest.parent.mkdir(parents=True,exist_ok=True)
    manifest.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n","utf8")
    return receipt

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    for k in ("parent","output","seal","manifest"):parser.add_argument("--"+k,required=True)
    a=parser.parse_args()
    print(json.dumps(build(a.parent,a.output,a.seal,a.manifest),ensure_ascii=False,indent=2))
