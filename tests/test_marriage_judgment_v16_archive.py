"""Strict SHA/row preservation and error-retention V1.6 entire-family dev corpus."""
from __future__ import annotations
import hashlib,sqlite3,tempfile,unittest
from pathlib import Path
from scripts.build_marriage_judgment_v16 import ROOT,OLD,NEW,PARENT_SHA,build
PARENT=ROOT/"archives/sqlite"/OLD
class BookFirstBlindStudyV16(unittest.TestCase):
 def test_complete_full_194_case_sqlite_unchanged_two_errors_preserved(self):
  self.assertEqual(hashlib.sha256(PARENT.read_bytes()).hexdigest(),PARENT_SHA)
  with tempfile.TemporaryDirectory() as d:
   out=Path(d)/NEW
   a=build(PARENT,out,Path(d)/"index")
   self.assertTrue(a["all_parent_rows_unchanged"])
   self.assertEqual(a["new_executable_author_initial_decisions"],3)
   self.assertEqual(a["two_complete_event_families_heldout"],2)
   self.assertEqual(a["matched_book_reported_feedback_in_dev"],1)
   self.assertEqual(a["mismatched_book_reported_feedback_in_dev"],2)
   self.assertEqual(a["printed_original_eight_deity_doors_aligned"],24)
   self.assertEqual(a["external_unseen_real_predictions"],0)
   with sqlite3.connect(out) as db:
    for table,n in a["counts"].items():
     self.assertEqual(db.execute('SELECT COUNT(*) FROM "'+table+'"').fetchone()[0],n,table)
    self.assertEqual(db.execute("SELECT COUNT(*) FROM cases").fetchone()[0],194)
    self.assertEqual(db.execute("SELECT COUNT(*) FROM marriage_v16_historical_initial_verdicts WHERE original_author_label_visible_before_initial=1").fetchone()[0],0)
    self.assertEqual(db.execute("SELECT COUNT(*) FROM marriage_v16_post_inference_labels WHERE available_to_initial_judger=1").fetchone()[0],0)
    self.assertEqual(db.execute("SELECT COUNT(*) FROM marriage_v16_post_inference_labels WHERE matches_initial_book_retrospective_result=0").fetchone()[0],2)
    self.assertEqual(db.execute("SELECT COUNT(*) FROM marriage_v16_historical_holdout_inputs WHERE original_case_chart_deity_door_align=1").fetchone()[0],3)
    self.assertEqual(db.execute("PRAGMA integrity_check").fetchone()[0],"ok")
    self.assertEqual(db.execute("PRAGMA foreign_key_check").fetchall(),[])
 def test_no_rewrite_previous_full_database(self):
  with tempfile.TemporaryDirectory() as d:
   out=Path(d)/NEW;out.write_bytes(b"already archived")
   with self.assertRaisesRegex(ValueError,"No overwrite"):
    build(PARENT,out,Path(d)/"audit")
if __name__=="__main__":unittest.main()
