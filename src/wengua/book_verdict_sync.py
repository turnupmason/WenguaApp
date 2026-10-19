"""Retroactively assign user-specified default book verdict to prior health events.

Only a source-EXPLICIT author correction may change a success label to
author_book_error_explicit. The operation never edits the actual old case
or replaces a verdict that already exists. No external accuracy claim.
"""
from __future__ import annotations
import json
from pathlib import Path
from .database import ROOT,connect,initialize

HEALTH_INDEX=ROOT/"data/knowledge/shenqi/health_prediction_ch01/case_index.json"

def sync_health_book_outcomes(db_path):
    rows=json.loads(Path(HEALTH_INDEX).read_text(encoding="utf-8"))["cases"]
    if len(rows)!=6:
        raise ValueError("Expected all six old health families")
    initialize(db_path)
    count=0
    with connect(db_path) as db:
        for item in rows:
            family=item["event_family_id"]
            if item.get("book_outcome_label")!="author_book_success_default":
                raise ValueError("Health source policy changed: review explicit corrections")
            if not db.execute("SELECT 1 FROM cases WHERE case_id=?",(family,)).fetchone():
                raise ValueError("Health case must already be in private SQLite before labeling")
            feedback=list(item.get("feedback_lines",[]))
            for x in item.get("progressive_disclosures",[])+item.get("disclosure",{}).get("line_events",[]):
                feedback+=list(range(x["lines"][0],x["lines"][1]+1))
            feedback=sorted(set(feedback))
            old=db.execute("SELECT verdict FROM historical_case_book_verdicts WHERE event_family_id=?",
                           (family,)).fetchone()
            if old:
                if old[0]=="author_book_error_explicit":
                    continue # safeguard explicit author-corrected records
                if old[0]!="author_book_success_default":
                    raise ValueError("Prior author verdict requires review")
                continue
            db.execute("""INSERT INTO historical_case_book_verdicts
                (event_family_id,primary_case_id,verdict,explicit_source_correction,
                source_correction_lines_json,feedback_source_lines_json,
                independent_external_verification,app_output_protocol,evidence_review_status,note)
                VALUES (?,?,'author_book_success_default',0,'[]',?,
                 'not_verified','single_answer_for_one_cast','book_source_only',?)""",
                 (family,family,json.dumps(feedback),
                  "User policy: book author success by default; progressive disclosures validate same event"))
            count+=1
        total=db.execute("""SELECT count(*) FROM historical_case_book_verdicts
                   WHERE event_family_id LIKE 'shenqi.health.%'""").fetchone()[0]
    return {"health_families_found":len(rows),"new_labels":count,
            "health_book_outcome_labels":total,
            "external_proof_added":0}
