"""V1.1 preserves V1 and blocks 'maybe later' readings without real timing."""
import hashlib,sqlite3,tempfile,unittest
from pathlib import Path
from scripts.upgrade_marriage_phrase_timing_v11 import ROOT,OLD,NEW,BASE_SHA,run
from src.wengua.timing_engine import derive_timing_candidates,finalize_traditional_decision
OLD_FILE=ROOT/"archives/sqlite"/OLD
class MarriageV11(unittest.TestCase):
 def test_upgraded_194_and_old_four_draft_phrases_unchanged(self):
  self.assertEqual(hashlib.sha256(OLD_FILE.read_bytes()).hexdigest(),BASE_SHA)
  with tempfile.TemporaryDirectory() as d:
   new=Path(d)/NEW
   m=run(OLD_FILE,new,Path(d)/"i")
   self.assertEqual(m["historical_events"],194)
   self.assertTrue(m["original_source_rows_and_v1_phrases_unchanged"])
   with sqlite3.connect(new) as db:
    self.assertEqual(db.execute("SELECT count(*) FROM cases").fetchone()[0],194)
    self.assertEqual(db.execute("SELECT count(*) FROM phrase_template_drafts").fetchone()[0],4)
    self.assertEqual(db.execute("SELECT count(*) FROM phrase_outcome_timing_contracts").fetchone()[0],4)
    self.assertEqual(db.execute("SELECT count(*) FROM phrase_instance_timing_windows").fetchone()[0],0)
    self.assertEqual(db.execute("SELECT count(*) FROM phrase_context_instances").fetchone()[0],0)
    self.assertEqual(db.execute("SELECT prompt_version FROM phrase_version_progress").fetchone()[0],"marriage_reading_v1.1")
    self.assertEqual(db.execute("PRAGMA integrity_check").fetchone()[0],"ok")
    self.assertEqual(db.execute("PRAGMA foreign_key_check").fetchall(),[])
    pid=db.execute("SELECT phrase_id FROM phrase_template_drafts LIMIT 1").fetchone()[0]
    db.execute("SAVEPOINT test_untrusted_reading")
    db.execute("""INSERT INTO phrase_context_instances
     (instance_id,phrase_id,domain_id,state_id,birth_year_ganzhi,age_band,
      sex,relationship,question_type,cast_engine_version,full_board_sha256,
      facts_sha256,complete_input_json,matched_rule_evidence_json,
      generated_text,generated_text_sha256,status,created_utc)
     VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
     ("TEST_ONLY",pid,"marriage","yang-01-00","甲子","adult",
      "female","self","courtship_to_marriage","UNVERIFIED_FIXTURE",
      "0"*64,"1"*64,"{}","{}","DRAFT_NOT_REAL","2"*64,"draft",
      "2026-10-21"))
    with self.assertRaises(sqlite3.IntegrityError):
     db.execute("UPDATE phrase_context_instances SET status='approved' WHERE instance_id='TEST_ONLY'")
    db.execute("ROLLBACK TO test_untrusted_reading")
    db.execute("RELEASE test_untrusted_reading")
 def test_actual_calendar_rows_mandatory_for_timing(self):
  arg=dict(empty_branches=["午","未"],periods=[],granularity="month",
      method="clash_empty",reference_iso="2026-11-01T00:00:00-05:00",
      calendar_method_version="real_required",calendar_receipt="fixture",
      source_method_ref="kaiwu.marriage.case01.line43")
  with self.assertRaises(ValueError):derive_timing_candidates(**arg)
  with self.assertRaises(ValueError):
   finalize_traditional_decision(outcome="success",reasoned_support=["有驿马"],
    reasoned_counter=[],chosen_timing=None,known_timing_candidates=[],
    timing_choice_rule_ref="空亡填实",confidence_boundary="traditional_only")
if __name__=="__main__":unittest.main()
