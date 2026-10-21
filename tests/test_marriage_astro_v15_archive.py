"""Source-hash checked all 20 timing methods, actual astronomy and immutable full DB."""
import hashlib,sqlite3,tempfile,unittest
from pathlib import Path
from scripts.build_marriage_astro_v15 import ROOT,PARENT_NAME,OUTPUT_NAME,PARENT_SHA,build
from src.wengua.book_timing_runtime import book_case01_marriage_timing_study
PARENT=ROOT/"archives/sqlite"/PARENT_NAME
class BookAstronomyFullDatabaseV15(unittest.TestCase):
 def test_all_source_cases_preserved_and_real_jie_windows_are_not_feedback_leakage(self):
  self.assertEqual(hashlib.sha256(PARENT.read_bytes()).hexdigest(),PARENT_SHA)
  with tempfile.TemporaryDirectory() as d:
   output=Path(d)/OUTPUT_NAME
   result=build(PARENT,output,Path(d)/"audit")
   self.assertEqual(result["original_book_timing_methods"],20)
   self.assertEqual(result["astronomically_computed_original_marriage_month_windows"],2)
   self.assertEqual(result["posterior_feedback_checks_strictly_separated"],2)
   self.assertEqual(result["new_actual_unseen_real_marriage_predictions"],0)
   self.assertEqual(result["calendar_method"],"wen-gua-local-meeus-solar-longitude-v1")
   with sqlite3.connect(output) as db:
    for table,expected in result["counts"].items():
     self.assertEqual(db.execute('SELECT COUNT(*) FROM "'+table+'"').fetchone()[0],expected,table)
    self.assertEqual(db.execute("SELECT COUNT(*) FROM cases").fetchone()[0],194)
    self.assertEqual(db.execute("SELECT COUNT(*) FROM marriage_runtime_scenario_study").fetchone()[0],44)
    self.assertEqual(db.execute("SELECT COUNT(*) FROM marriage22_scenario_protocol").fetchone()[0],22)
    months=db.execute("""SELECT trigger_branch,window_start_iso,window_end_iso
      FROM marriage_author_timing_month_windows ORDER BY ordinal""").fetchall()
    self.assertEqual([m[0] for m in months],["子","丑"])
    self.assertLess(months[0][1],"1998-12-16T12:00:00+08:00")
    self.assertGreater(months[0][2],"1998-12-16T12:00:00+08:00")
    self.assertLess(months[1][1],"1999-01-17T12:00:00+08:00")
    self.assertGreater(months[1][2],"1999-01-17T12:00:00+08:00")
    self.assertEqual(db.execute("""SELECT COUNT(*) FROM marriage_author_time_feedback_validation
        WHERE later_book_feedback_not_initial_input=1 AND observed_day_inside_candidate_month=1""").fetchone()[0],2)
    self.assertEqual(db.execute("SELECT COUNT(*) FROM marriage_v15_astro_method_audit WHERE verified_unseen_marriage_forecasts=0").fetchone()[0],1)
    self.assertEqual(db.execute("PRAGMA integrity_check").fetchone()[0],"ok")
    self.assertEqual(db.execute("PRAGMA foreign_key_check").fetchall(),[])
 def test_history_is_immutable_reject_attempt_to_overwrite_completed_version(self):
  with tempfile.TemporaryDirectory() as d:
   output=Path(d)/OUTPUT_NAME
   output.write_bytes(b"do not overwrite")
   with self.assertRaisesRegex(ValueError,"not be overwritten"):
    build(PARENT,output,Path(d)/"audit")
if __name__=="__main__":unittest.main()
