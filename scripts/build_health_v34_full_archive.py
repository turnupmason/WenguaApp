"""Append-only V3.4 complete 194-book-case SQLite with new true hour replays.

Never overwrite V3.1 through V3.3 binaries or earlier inaccurate readings.
Never use any original-book later results as forecast inputs.
"""
from __future__ import annotations
import argparse,hashlib,json,lzma,sqlite3
from pathlib import Path
from scripts.build_health_v21_archive import preserve
from scripts.replay_all_historical_health_v34 import evaluate,PARENT_SHA
ROOT=Path(__file__).resolve().parents[1]
MIG=ROOT/"schema/migrations/062_health_full_actor_and_source_predicates_v34.sql"

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def build(parent,output,seal,manifest):
    parent,output,seal,manifest=map(Path,(parent,output,seal,manifest))
    xz=Path(str(output)+".xz")
    if any(p.exists() for p in (output,seal,manifest,xz)):
        raise ValueError("Do not overwrite existing full SQL, compressed data or original readings")
    if sha(parent)!=PARENT_SHA:raise ValueError("V3.4 requires exact latest V3.3 entire research DB")
    evaluations=evaluate(db_path=parent)
    if len(evaluations["samples"])!=12 or sum(evaluations["counts"].values())!=12:
        raise ValueError("Missing original source illness family")
    output.parent.mkdir(parents=True,exist_ok=True)
    with sqlite3.connect(parent.resolve().as_uri()+"?mode=ro",uri=True) as old,sqlite3.connect(output) as db:
        old.backup(db)
        db.executescript(MIG.read_text("utf8"))
        db.execute("PRAGMA foreign_keys=ON")
        with db:
            for name,n in [("cases",194),("sections",43),
                           ("health_v30_stem_pair_rules",42),
                           ("health_v30_composite_rule_index",17),
                           ("health_v32_pre_disclosure_history",2),
                           ("health_v33_all_historical_health_replay",12)]:
                got=db.execute('SELECT count(*) FROM "'+name+'"').fetchone()[0]
                if got!=n:raise ValueError("Lost old rows in "+name+" "+str(got))
            wrong=db.execute("SELECT count(*) FROM marriage_v16_post_inference_labels WHERE matches_initial_book_retrospective_result=0").fetchone()[0]
            if wrong!=2:raise ValueError("Lost two previous wrong forecasts")
            for x in evaluations["samples"]:
                ok=x["result"]=="rendered"
                db.execute("""INSERT INTO health_v34_role_and_condition_replay
                 (event_family_id,source_original_intent,template_intent,actual_source_day,
                  actual_source_hour,patient_relation,result_status,blockade_reason,
                  sealed_reading_sha256,traditional_research_verdict,
                  all_42_pairs_tristate_checked,all_17_composite_tristate_checked,
                  user_acceptance,original_book_result_loaded,medical_accuracy_proven)
                 VALUES (?,?,'severity',?,?,?,?,?,?,?,?,?,'pending',0,0)""",
                 (x["family_id"],x["source_intent"],x["source_day"],x["source_hour"],
                  next(c["relation"] for c in __import__("scripts.replay_all_historical_health_v31_v33",fromlist=["CASES"]).CASES if c["id"]==x["family_id"]),
                  x["result"],x.get("reason",""),x.get("sha256"),x.get("traditional_severity"),
                  int(ok and len(x["ordered_pairs"])==42),
                  int(ok and len(x["composites"])==17)))
            db.execute("""INSERT INTO health_v34_source_rule_audit VALUES
                 ('health_v34_user_supplied',?,
                  'data/knowledge/phrase_library/health_v20/actor_profiles.json',
                  'src/wengua/health_severity_v34.py',1,42,17,1,194,43,2,1,1)""",
                       (PARENT_SHA,))
        preserve(old,db)
        if db.execute("PRAGMA integrity_check").fetchone()[0]!="ok":
            raise ValueError("New sqlite integrity failed")
        if db.execute("PRAGMA foreign_key_check").fetchall():
            raise ValueError("Foreign keys invalid")
        db.execute("VACUUM");db.commit()
    seal.parent.mkdir(parents=True,exist_ok=True)
    seal.write_text(json.dumps(evaluations,ensure_ascii=False,indent=2)+"\n","utf8")
    xz.write_bytes(lzma.compress(output.read_bytes(),preset=6))
    details={
      "schema":"wengua_v34_full_book_source_role_disease_replay",
      "full_db_sha256":sha(output),"full_db_bytes":output.stat().st_size,
      "xz_sha256":sha(xz),"full_parent_v33_sha256":sha(parent),
      "sealed_readout_sha256":sha(seal),"book_cases":194,"book_sections":43,
      "health_unique_source_families":12,
      "rendered":evaluations["counts"]["rendered"],"blocked":evaluations["counts"]["blocked"],
      "ordered_pairs_indexed_and_condition_checked":42,
      "composite_patterns_indexed_and_condition_checked":17,
      "unsupported_condition_predicates_are_explicit_unknown_not_claimed_complete":True,
      "original_source_outcome_loaded":False,"medical_validation":False,
      "prior_seals_and_failure_records_immutable":True,
      "no_runtime_llm_or_network":True,"user_review":"pending",
      "other_four_health_intents":"unapproved","ui":"user_design_needed"
    }
    manifest.parent.mkdir(parents=True,exist_ok=True)
    manifest.write_text(json.dumps(details,ensure_ascii=False,indent=2)+"\n","utf8")
    return details

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    for key in ("parent","output","seal","manifest"):parser.add_argument("--"+key,required=True)
    a=parser.parse_args()
    print(json.dumps(build(a.parent,a.output,a.seal,a.manifest),ensure_ascii=False,indent=2))
