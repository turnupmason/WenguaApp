"""194 historical cases unchanged; 22 marriage reading routes × 2 true original casting examples."""
from __future__ import annotations
import hashlib,sqlite3,tempfile,unittest
from pathlib import Path
from scripts.build_marriage_runtime_v14 import ROOT,PARENT_NAME,NEW_NAME,PARENT_SHA,build
from src.wengua.marriage_runtime import inspect_marriage_study_cast
OLD=ROOT/"archives/sqlite"/PARENT_NAME
class V14CastingRuntimeArchive(unittest.TestCase):
 def test_original_source_chart_fixtures_are_not_fake_divination_outcomes(self):
  self.assertEqual(hashlib.sha256(OLD.read_bytes()).hexdigest(),PARENT_SHA)
  with tempfile.TemporaryDirectory() as dirname:
   dbpath=Path(dirname)/NEW_NAME
   report=build(OLD,dbpath,Path(dirname)/"index")
   self.assertEqual(report["real_original_casting_book_examples_compared"],2)
   self.assertEqual(report["source_chart_palaces_compared"],18)
   self.assertEqual(report["all_scene_source_retrieval_checks"],44)
   self.assertEqual(report["genuinely_end_to_end_decisive_reading_instances"],0)
   self.assertTrue(report["all_previous_sqlite_rows_unmodified"])
   self.assertEqual(report["per_sample_analysis"]["shenqi_casting_example_1995_06_11"]["xun_void_branches"],["子","丑"])
   self.assertEqual(report["per_sample_analysis"]["shenqi_casting_example_1995_08_13"]["xun_void_branches"],["辰","巳"])
   with sqlite3.connect(dbpath) as db:
    for table,n in report["counts"].items():
     self.assertEqual(db.execute('SELECT COUNT(*) FROM "'+table+'"').fetchone()[0],n,table)
    self.assertEqual(db.execute("SELECT COUNT(*) FROM marriage_runtime_scenario_study").fetchone()[0],44)
    self.assertEqual(db.execute("SELECT COUNT(*) FROM marriage_runtime_source_cast_fixture WHERE human_forecast_text IS NOT NULL").fetchone()[0],0)
    self.assertEqual(db.execute("SELECT COUNT(*) FROM marriage_runtime_scenario_study WHERE explicit_result IS NOT NULL OR calculated_primary_timing IS NOT NULL OR final_phrase IS NOT NULL").fetchone()[0],0)
    self.assertEqual(db.execute("SELECT COUNT(*) FROM cases").fetchone()[0],194)
    self.assertEqual(db.execute("SELECT COUNT(*) FROM phrase_intent_workflows").fetchone()[0],9)
    self.assertEqual(db.execute("SELECT COUNT(*) FROM marriage22_scenario_protocol").fetchone()[0],22)
    self.assertEqual(db.execute("SELECT COUNT(*) FROM marriage_runtime_scenario_study WHERE book_original_method_ref_count>0").fetchone()[0],44)
    self.assertEqual(db.execute("SELECT COUNT(*) FROM marriage_runtime_study_audit WHERE full_previous_rows_unchanged=1").fetchone()[0],1)
    self.assertEqual(db.execute("PRAGMA integrity_check").fetchone()[0],"ok")
    self.assertEqual(db.execute("PRAGMA foreign_key_check").fetchall(),[])
 def test_actual_source_ingest_cannot_reinterpret_without_book_refs(self):
  with self.assertRaises(ValueError):
   inspect_marriage_study_cast(db_path=OLD,scene_id="marriage.scene.00",
    day_ganzhi="癸酉",solar_term="芒种",hour_ganzhi="丁巳")
if __name__=="__main__":unittest.main()
