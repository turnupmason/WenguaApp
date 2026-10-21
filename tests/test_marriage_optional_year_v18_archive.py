"""V1.8 complete SQLite append-only regression with optional 年命 book methods."""
from __future__ import annotations
from pathlib import Path
import hashlib,sqlite3,tempfile,unittest
from scripts.build_marriage_optional_year_v18 import ROOT,PARENT_NAME,OUTPUT_NAME,PARENT_SHA,build
PARENT=ROOT/"archives/sqlite"/PARENT_NAME
class OptionalYearCompleteArchive(unittest.TestCase):
 def test_exact_parent_preservation_22_routes_10_sources_two_historical_errors(self):
  self.assertEqual(hashlib.sha256(PARENT.read_bytes()).hexdigest(),PARENT_SHA)
  with tempfile.TemporaryDirectory() as d:
   output=Path(d)/OUTPUT_NAME
   result=build(PARENT,output,Path(d)/"index")
   self.assertEqual(result["all_book_events_preserved"],194)
   self.assertTrue(result["original_all_prior_database_rows_unchanged"])
   self.assertEqual(result["previous_v16_wrong_dev_predictions_preserved"],2)
   self.assertTrue(result["all_22_marriage_scenes_accept_absent_year"])
   self.assertEqual(result["exact_original_method_line_hashes"],10)
   self.assertEqual(result["other_two_historical_families_no_year_comparison"],2)
   self.assertEqual(result["new_independently_verified_real_world_predictions"],0)
   self.assertEqual(sorted(x["year_mode"] for x in result["first_results"]),
                    ["no_year_optional","one_year_optional"])
   with sqlite3.connect(output) as db:
    for table,count in result["counts"].items():
     self.assertEqual(db.execute('SELECT COUNT(*) FROM "'+table+'"').fetchone()[0],count,table)
    self.assertEqual(db.execute("""SELECT COUNT(*) FROM marriage_v16_post_inference_labels
         WHERE matches_initial_book_retrospective_result=0""").fetchone()[0],2)
    self.assertEqual(db.execute("""SELECT COUNT(*) FROM marriage_v18_optional_year_scene_methods
         WHERE no_year_route_available=1 AND one_year_route_available=1 AND both_years_route_available=1""").fetchone()[0],22)
    self.assertEqual(db.execute("""SELECT COUNT(*) FROM marriage_v18_missing_year_dev_studies
         WHERE history_family_feedback_as_initial_input=1 OR
         missing_year_not_fabricated=0 OR reading_publication_ready=1""").fetchone()[0],0)
    self.assertEqual(db.execute("PRAGMA integrity_check").fetchone()[0],"ok")
    self.assertEqual(db.execute("PRAGMA foreign_key_check").fetchall(),[])
 def test_old_archives_refuse_overwrite(self):
  with tempfile.TemporaryDirectory() as d:
   out=Path(d)/OUTPUT_NAME
   out.write_bytes(b"immutable")
   with self.assertRaisesRegex(ValueError,"Refuse to overwrite"):
    build(PARENT,out,Path(d)/"index")
if __name__=="__main__":unittest.main()
