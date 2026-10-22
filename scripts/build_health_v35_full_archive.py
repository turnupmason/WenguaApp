"""V3.5 immutable 194 case complete SQLite archive, no earlier seals touched."""
from __future__ import annotations
import argparse,hashlib,json,lzma,sqlite3
from pathlib import Path
from scripts.build_health_v21_archive import preserve
from scripts.replay_all_historical_health_v35 import evaluate,PARENT_SHA
ROOT=Path(__file__).resolve().parents[1]
MIG=ROOT/"schema/migrations/063_health_patient_first_priority_v35.sql"

def sha(x):return hashlib.sha256(Path(x).read_bytes()).hexdigest()

def build(parent,output,seal,manifest):
    parent,output,seal,manifest=map(Path,(parent,output,seal,manifest))
    xz=Path(str(output)+".xz")
    if any(q.exists() for q in (output,seal,manifest,xz)):
        raise ValueError("No preexisting immutable artifact can be rewritten")
    if sha(parent)!=PARENT_SHA:raise ValueError("Exact V3.4 full source parent required")
    r=evaluate(db_path=parent)
    if r["counts"]!={"rendered":12,"blocked":0}:
        raise ValueError("All twelve actual source cases must be rendered or archive is blocked")
    output.parent.mkdir(parents=True,exist_ok=True)
    with sqlite3.connect(parent.resolve().as_uri()+"?mode=ro",uri=True) as old,sqlite3.connect(output) as db:
        old.backup(db);db.executescript(MIG.read_text("utf8"))
        db.execute("PRAGMA foreign_keys=ON")
        with db:
            for tab,num in [("cases",194),("sections",43),
                            ("health_v33_all_historical_health_replay",12),
                            ("health_v34_role_and_condition_replay",12),
                            ("health_v32_pre_disclosure_history",2),
                            ("health_v30_stem_pair_rules",42),
                            ("health_v30_composite_rule_index",17)]:
                actual=db.execute('SELECT count(*) FROM "'+tab+'"').fetchone()[0]
                if actual!=num:raise ValueError("Prior source rows missing: "+tab)
            if db.execute("SELECT count(*) FROM marriage_v16_post_inference_labels WHERE matches_initial_book_retrospective_result=0").fetchone()[0]!=2:
                raise ValueError("Old failed development readings deleted")
            for row in r["samples"]:
                decision=row["patient_priority"]
                db.execute("""INSERT INTO health_v35_patient_first_replay (
                    event_family_id,actual_source_day,actual_source_hour,original_author_outcome_was_used,
                    readout_sha256,prior_v34_traditional_verdict,revised_v35_traditional_verdict,
                    real_double_control,patient_void_limits_control,natal_year_qualified_by_source,
                    medical_co_palace_not_vetoed_by_weakness,user_review)
                    VALUES (?,?,?,0,?,?,?,?,?,?,1,'pending')""",
                    (row["family_id"],row["source_day"],row["source_hour"],row["sha256"],
                     row["previous_v34_severity"],row["traditional_severity"],
                     int(decision["double_suppression"]),int(decision["patient_void"]),
                     int(row.get("supplied_natal_reference_palace") is not None and row["family_id"]=="kaiwu.final.recovery")))
            db.execute("""INSERT INTO health_v35_complete_parent_archive
                  VALUES ('v3.5',?,194,43,2,1,42,17,1,1,'pending')""",(PARENT_SHA,))
        preserve(old,db)
        if db.execute("PRAGMA integrity_check").fetchone()[0]!="ok":raise ValueError("SQLite integrity invalid")
        if db.execute("PRAGMA foreign_key_check").fetchall():raise ValueError("Foreign key invalid")
        db.execute("VACUUM");db.commit()
    seal.parent.mkdir(parents=True,exist_ok=True)
    seal.write_text(json.dumps(r,ensure_ascii=False,indent=2)+"\n","utf8")
    xz.write_bytes(lzma.compress(output.read_bytes(),preset=6))
    meta={"schema":"wengua_v35_194_source_12_patients_priority_complete_archive",
      "sqlite_sha256":sha(output),"sqlite_bytes":output.stat().st_size,
      "xz_sha256":sha(xz),"exact_v34_parent_sha256":sha(parent),
      "sealed_12_case_sha256":sha(seal),"book_case_families":194,"source_sections":43,
      "historical_illness_cases":12,"cases_rendered":r["counts"]["rendered"],
      "cases_blocked":r["counts"]["blocked"],
      "previous_failed_developer_forecasts_preserved":2,
      "previous_v31_v33_v34_sealed_readouts_unchanged":True,
      "all_42_pairs_and_17_composites_audited_tristate":True,
      "incomplete_source_rules_not_falsely_claimed_complete":True,
      "author_book_outcomes_not_used":True,"medical_forecast_validated":False,
      "other_four_health_intents_unapproved":True,"user_review":"pending",
      "ui_not_yet_built":True}
    manifest.parent.mkdir(parents=True,exist_ok=True)
    manifest.write_text(json.dumps(meta,ensure_ascii=False,indent=2)+"\n","utf8")
    return meta

if __name__=="__main__":
    p=argparse.ArgumentParser()
    for arg in ("parent","output","seal","manifest"):p.add_argument("--"+arg,required=True)
    a=p.parse_args()
    print(json.dumps(build(a.parent,a.output,a.seal,a.manifest),ensure_ascii=False,indent=2))
