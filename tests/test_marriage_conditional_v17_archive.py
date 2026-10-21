"""V1.7 append-only source book citations + genuine absent-data holdout gates."""
from __future__ import annotations
import hashlib,sqlite3,tempfile,unittest
from pathlib import Path
from scripts.build_marriage_conditional_v17 import ROOT,PARENT_NAME,NEW_NAME,PARENT_SHA,build
PARENT=ROOT/"archives/sqlite"/PARENT_NAME
class MarriageOriginalConditionalFullArchive(unittest.TestCase):
 def test_source_sha_27_rules_two_other_families_old_194_cases_and_two_misses_kept(self):
  self.assertEqual(hashlib.sha256(PARENT.read_bytes()).hexdigest(),PARENT_SHA)
  with tempfile.TemporaryDirectory() as d:
   out=Path(d)/NEW_NAME
   report=build(PARENT,out,Path(d)/"rule_evidence")
   self.assertTrue(report["all_previous_rows_identical"])
   self.assertEqual(report["exact_new_original_conditional_rules"],27)
   self.assertEqual(report["81_ordered_kaiwu_stem_pairs_read_with_source"],81)
   self.assertEqual(report["prior_dev_retained_matches"],1)
   self.assertEqual(report["prior_dev_retained_misses"],2)
   self.assertFalse(report["24_factor_full_inference_approved"])
   with sqlite3.connect(out) as conn:
    for tbl,count in report["counts"].items():
     self.assertEqual(conn.execute('SELECT COUNT(*) FROM "'+tbl+'"').fetchone()[0],count,tbl)
    self.assertEqual(conn.execute("SELECT COUNT(*) FROM cases").fetchone()[0],194)
    self.assertEqual(conn.execute("SELECT COUNT(*) FROM marriage_v16_post_inference_labels WHERE matches_initial_book_retrospective_result=0").fetchone()[0],2)
    self.assertEqual(conn.execute("SELECT COUNT(*) FROM marriage_v17_new_event_family_replays WHERE initial_traditional_verdict='unresolved' AND retrospective_future_outcome_score IS NULL").fetchone()[0],2)
    self.assertEqual(conn.execute("SELECT COUNT(*) FROM marriage_v17_book_conditional_rules WHERE length(source_sha256)=64 AND length(exact_excerpt_sha256)=64").fetchone()[0],27)
    self.assertEqual(conn.execute("SELECT COUNT(*) FROM marriage_v17_rule_change_and_error_audit WHERE previous_dev_wrong_kept=2 AND new_other_family_scoreable_future_results=0").fetchone()[0],1)
    self.assertEqual(conn.execute("PRAGMA integrity_check").fetchone()[0],"ok")
    self.assertEqual(conn.execute("PRAGMA foreign_key_check").fetchall(),[])
 def test_versioned_full_database_must_not_be_rewritten(self):
  with tempfile.TemporaryDirectory() as d:
   out=Path(d)/NEW_NAME;out.write_text("already archived")
   with self.assertRaisesRegex(ValueError,"Cannot overwrite"):
    build(PARENT,out,Path(d)/"rule_evidence")
if __name__=="__main__":unittest.main()
