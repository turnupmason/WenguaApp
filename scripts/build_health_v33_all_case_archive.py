"""New immutable full SQLite research archive of every indexed historical illness event.

Append-only on V3.2 exact SHA. Retains all 194 historical families and all
former V2.x/V3.x sealed errors; only V3.1 unaltered interpreter evaluated.
"""
from __future__ import annotations
import argparse, hashlib, json, lzma, sqlite3
from pathlib import Path
from scripts.build_health_v21_archive import preserve
from scripts.replay_all_historical_health_v31_v33 import evaluate, PARENT_SHA
ROOT=Path(__file__).resolve().parents[1]
MIG=ROOT/"schema/migrations/061_health_all_original_case_replay_v33.sql"
COVERAGE=ROOT/"data/knowledge/phrase_library/health_v33/user_disease_supplement_template_coverage.json"

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def build(*,parent,output,seal,manifest):
    parent,output,seal,manifest=map(Path,(parent,output,seal,manifest))
    xz=Path(str(output)+".xz")
    if any(p.exists() for p in (output,seal,manifest,xz)):
        raise ValueError("Never rewrite or reuse an already archived V3.3 file")
    if sha(parent)!=PARENT_SHA:
        raise ValueError("Only exact latest full V3.2 source archive accepted")
    coverage=json.loads(COVERAGE.read_text("utf8"))
    if len(coverage["template_slots"])!=11:
        raise ValueError("Missing user's eleven-section source coverage")
    outcome=evaluate(db_path=parent)
    if len(outcome["records"])!=12 or outcome["counts"]["rendered_v31"]+outcome["counts"]["blocked"]!=12:
        raise ValueError("Incomplete historical health domain research batch")
    output.parent.mkdir(parents=True,exist_ok=True)
    with sqlite3.connect(parent.resolve().as_uri()+"?mode=ro",uri=True) as old, sqlite3.connect(output) as db:
        old.backup(db)
        db.executescript(MIG.read_text("utf8"))
        db.execute("PRAGMA foreign_keys=ON")
        with db:
            for table,count in (("cases",194),("sections",43),
                                ("health_v30_stem_pair_rules",42),
                                ("health_v30_composite_rule_index",17),
                                ("health_v32_pre_disclosure_history",2),
                                ("health_v31_correction_archive",2)):
                if db.execute('SELECT count(*) FROM "'+table+'"').fetchone()[0]!=count:
                    raise ValueError("Missing inherited source rows: "+table)
            if db.execute("SELECT count(*) FROM marriage_v16_post_inference_labels WHERE matches_initial_book_retrospective_result=0").fetchone()[0]!=2:
                raise ValueError("Lost previous two wrong research predictions")
            for row in outcome["records"]:
                db.execute("""INSERT INTO health_v33_all_historical_health_replay (
                    event_family_id,source_book,source_date,source_day,source_hour,
                    source_question_intent,actual_template_intent,
                    original_author_answer_loaded,original_feedback_loaded,
                    cast_or_role_status,failure_reason,reading_sha256,
                    traditional_book_method_verdict,user_review_status)
                    VALUES (?,?,?,?,?,?,?,0,0,?,?,?,?, 'pending')""",
                    (row["family_id"],row["source"],row["source_date"],row["source_day"],row["source_hour"],
                     row["source_question_intent"],"severity",row["status"],row.get("reason",""),
                     row.get("readout_sha256"),row.get("traditional_verdict")))
            db.execute("""INSERT INTO health_v33_user_disease_curriculum_appendix
              VALUES('health_20261022_followup','direct_user_message',
                     'partially_executable_not_full_rule_approval',?,42,17,11,1,4,1)""",
                     ("data/knowledge/phrase_library/health_v33/user_disease_supplement_template_coverage.json",))
        preserve(old,db)
        if db.execute("PRAGMA integrity_check").fetchone()[0]!="ok":
            raise ValueError("SQLite integrity not ok")
        if db.execute("PRAGMA foreign_key_check").fetchall():
            raise ValueError("Foreign keys broken")
        db.execute("VACUUM");db.commit()
    seal.parent.mkdir(parents=True,exist_ok=True)
    seal.write_text(json.dumps(outcome,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    xz.write_bytes(lzma.compress(output.read_bytes(),preset=6))
    meta={
      "schema":"wengua_v33_full_194_12_health_indexed_family_replays",
      "complete_sqlite_sha256":sha(output),"complete_size_bytes":output.stat().st_size,
      "compressed_xz_sha256":sha(xz),"source_parent_v32_sha256":sha(parent),
      "historical_readouts_sha256":sha(seal),"supplement_coverage_sha256":sha(COVERAGE),
      "cases_original":194,"sections_original":43,"indexed_health_unique_events":12,
      "rendered":outcome["counts"]["rendered_v31"],"blocked":outcome["counts"]["blocked"],
      "earlier_two_failed_dev_readings_preserved":True,
      "author_answers_not_used":True,"scientific_medical_validation":False,
      "v31_renderer_unchanged":True,
      "user_approval":"pending","ui":"not_yet_approved",
      "other_four_health_intents":"unapproved"}
    manifest.parent.mkdir(parents=True,exist_ok=True)
    manifest.write_text(json.dumps(meta,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    return meta

if __name__=="__main__":
    p=argparse.ArgumentParser()
    for name in ("parent","output","seal","manifest"):
        p.add_argument("--"+name,required=True)
    a=p.parse_args()
    print(json.dumps(build(parent=a.parent,output=a.output,seal=a.seal,manifest=a.manifest),ensure_ascii=False,indent=2))
