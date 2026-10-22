"""V3.2 archival snapshot: 194 original events + two new V3.1-engine predictions.

Append-only on exact latest immutable V3.1 database. Never changes past case
text, patient information, old failed tests, source catalogs or model artifacts.
"""
from __future__ import annotations
import argparse,hashlib,json,sqlite3
from pathlib import Path
from scripts.build_health_v21_archive import preserve
from scripts.replay_two_new_historical_health_v32 import evaluate, PARENT_SHA

ROOT=Path(__file__).resolve().parents[1]
MIG=ROOT/"schema/migrations/060_health_v31_real_cases_ui_handoff_v32.sql"

def sha(file):return hashlib.sha256(Path(file).read_bytes()).hexdigest()

def build(parent,output,sealed,manifest):
    parent,output,sealed,manifest=map(Path,(parent,output,sealed,manifest))
    if output.exists() or sealed.exists():
        raise ValueError("Cannot replace an earlier full SQLite or prediction artifact")
    if sha(parent)!=PARENT_SHA:raise ValueError("Exact latest V3.1 complete DB required")
    # Reading made from time/role/casting facts before author comments are inspected.
    result=evaluate(db_path=parent)
    if len(result["samples"])!=2 or not result["pure_python_no_gpt"]:
        raise ValueError("Two distinct deterministic source-case predictions required")
    if len({x["family_id"] for x in result["samples"]})!=2:
        raise ValueError("Same original event cannot be tested twice")
    output.parent.mkdir(parents=True,exist_ok=True)
    with sqlite3.connect(parent.resolve().as_uri()+"?mode=ro",uri=True) as old,sqlite3.connect(output) as db:
        old.backup(db)
        db.executescript(MIG.read_text("utf8"))
        db.execute("PRAGMA foreign_keys=ON")
        with db:
            for table,n in (
               ("cases",194),("sections",43),
               ("health_v30_stem_pair_rules",42),
               ("health_v30_composite_rule_index",17),
               ("health_v31_hour_patient_fixed_templates",1),
               ("health_v31_correction_archive",2)):
                m=db.execute('SELECT count(*) FROM "'+table+'"').fetchone()[0]
                if m!=n:raise ValueError("Prior source data lost: "+table+":"+str(m))
            bad=db.execute(
                "SELECT count(*) FROM marriage_v16_post_inference_labels "+
                "WHERE matches_initial_book_retrospective_result=0").fetchone()[0]
            if bad!=2:raise ValueError("Earlier two wrong prediction records lost")
            for x in result["samples"]:
                db.execute("""INSERT INTO health_v32_pre_disclosure_history
                  (source_family_id,exact_v31_parent_sha256,pre_disclosure_pillars,
                   book_casting_bureau,original_book_outcome_was_read,
                   original_book_feedback_was_read,reading_sha256,
                   provisional_traditional_verdict,older_known_family_not_new_blind,user_acceptance)
                   VALUES (?,?,?,?,0,0,?,?,1,'pending')""",
                (x["family_id"],PARENT_SHA,
                 json.dumps(x["four_pillars"],ensure_ascii=False),
                 json.dumps(x["original_given_bureau"],ensure_ascii=False),
                 x["text_sha256"],x["verdict"]))
            db.execute("""INSERT INTO health_v32_handoff_gate
               (version,parent_full_sha256,original_case_families,original_chapters,
                old_wrong_development_predictions,indexed_original_stem_pairs,
                indexed_composite_rules,old_four_health_intents_unapproved,
                app_ui_cannot_be_accepted_ahead_of_user,previous_all_rows_preserved,
                clinical_prediction_validated,user_review_status)
                VALUES('v3.2',?,194,43,2,42,17,4,1,1,0,'pending')""",(PARENT_SHA,))
        preserve(old,db)
        if db.execute("PRAGMA integrity_check").fetchone()[0]!="ok":
            raise ValueError("Original and newly copied DB fail integrity")
        if db.execute("PRAGMA foreign_key_check").fetchall():
            raise ValueError("Foreign keys broken in new SQLite")
        db.execute("VACUUM");db.commit()
    sealed.parent.mkdir(parents=True,exist_ok=True)
    sealed.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n","utf8")
    metadata={
     "schema":"wengua_v32_two_new_event_families_v31_engine_replay",
     "exact_previous_v31_full_sha256":PARENT_SHA,
     "new_full_archive_sha256":sha(output),
     "sealed_output_sha256":sha(sealed),
     "two_source_families":[x["family_id"] for x in result["samples"]],
     "readout_sha256s":{x["family_id"]:x["text_sha256"] for x in result["samples"]},
     "engine_version":"V3.1 unchanged",
     "source_cases":194,"original_sections":43,"old_failed_dev_cases":2,
     "indexed_ordered_pairs":42,"indexed_composites":17,
     "original_source_outcomes_used":False,
     "source_cases_were_in_book_library":True,
     "no_secret_blind_validation_claim":True,
     "prior_all_rows_preserved":True,
     "four_other_health_intents_approved":False,
     "medical_accuracy_validated":False,
     "ui_approval":"pending after user reviews predictions",
     "ios_submission_status":"not started"
    }
    manifest.parent.mkdir(parents=True,exist_ok=True)
    manifest.write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+"\n","utf8")
    return metadata

if __name__=="__main__":
    p=argparse.ArgumentParser()
    for field in ("parent","output","sealed","manifest"):
        p.add_argument("--"+field,required=True)
    a=p.parse_args()
    print(json.dumps(build(a.parent,a.output,a.sealed,a.manifest),ensure_ascii=False))
