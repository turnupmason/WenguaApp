"""Real source-book casting example to 22 marriage-issue engine bridge.

No actual marriage event or privately known outcome is invented: both complete
nine-palace examples are from the *casting chapter*, not marriage. Tests make
sure all intents can retrieve actual book sources without using later feedback
as first-judgment evidence.
"""
import unittest
from pathlib import Path
from src.wengua.marriage_runtime import (
    SOURCE_EXAMPLES,inspect_marriage_study_cast,inspect_marriage_chart_json,
    compute_source_chart_factors,hourly_void_branches,ELEMENTS,DOOR_ELEMENTS,element_relation)
from src.wengua.casting_shenqi import layout_from_explicit_bureau
from src.wengua.phrase_pipeline import FACTOR_IDS
ROOT=Path(__file__).resolve().parents[1]
FULL_DB=ROOT/"archives/sqlite/WenguaApp_双书194案例_婚姻22场景六层流程V1_3_完整研究库.sqlite3"
EXAMPLES={
 "shenqi_casting_example_1995_06_11":{
  "day_ganzhi":"癸酉","solar_term":"芒种","hour_ganzhi":"丁巳"},
 "shenqi_casting_example_1995_08_13":{
  "day_ganzhi":"丙子","solar_term":"立秋","hour_ganzhi":"戊戌"}}
class SourceChartBridgeTests(unittest.TestCase):
 def test_original_example_hour_xun_and_palace_role_candidates(self):
  a=inspect_marriage_study_cast(db_path=FULL_DB,scene_id="marriage.scene.02",
   example_key="shenqi_casting_example_1995_06_11",**EXAMPLES["shenqi_casting_example_1995_06_11"])
  self.assertEqual(a["bureau_from_explicit_term"]["ju"],3)
  self.assertEqual(a["bureau_from_explicit_term"]["dun"],"yang")
  self.assertEqual(a["factor_checked_count"],24)
  self.assertEqual(len(a["source_chart"]["palaces"]),9)
  self.assertEqual(a["role_candidates_not_final_yongshen"]["day_stem_palaces"][0]["palace"],9)
  self.assertEqual(a["role_candidates_not_final_yongshen"]["hour_stem_palaces"][0]["palace"],6)
  self.assertEqual(a["role_candidates_not_final_yongshen"]["liuhe"][0]["palace"],6)
  self.assertEqual(a["role_candidates_not_final_yongshen"]["yi_traditional_candidate"][0]["palace"],1)
  self.assertEqual(a["role_candidates_not_final_yongshen"]["geng_traditional_candidate"][0]["palace"],1)
  self.assertEqual(a["factor_audit"]["xun_kong"]["evidence"]["xun_kong_branches"],["子","丑"])
  self.assertEqual(set(x["palace"] for x in a["factor_audit"]["door_press_palace"]["evidence"]["exact_mechanical_door_press_palaces"]),{3,4,9})
  self.assertTrue(a["author_first_and_method_source_links"])
  self.assertEqual(a["traditional_forecast_result"],None)
  self.assertEqual(a["calculated_primary_timing"],None)
  self.assertEqual(a["human_natural_phrase"],None)
  self.assertIn("no_independently_verified_event_timing_calendar",a["missing_to_publish"])
 def test_yin_source_example_no_book_feedback_leakage(self):
  a=inspect_marriage_study_cast(db_path=FULL_DB,scene_id="marriage.scene.22",
   example_key="shenqi_casting_example_1995_08_13",**EXAMPLES["shenqi_casting_example_1995_08_13"])
  self.assertEqual((a["bureau_from_explicit_term"]["dun"],a["bureau_from_explicit_term"]["ju"]),("yin",8))
  self.assertEqual(a["factor_audit"]["xun_kong"]["evidence"]["xun_kong_branches"],["辰","巳"])
  self.assertEqual(a["role_candidates_not_final_yongshen"]["day_stem_palaces"][0]["palace"],9)
  self.assertEqual(a["role_candidates_not_final_yongshen"]["hour_stem_palaces"][0]["palace"],2)
  self.assertEqual(set(v["palace"] for v in a["factor_audit"]["door_press_palace"]["evidence"]["exact_mechanical_door_press_palaces"]),{1,2,3,6})
  self.assertTrue(a["author_first_and_method_source_links"])
  self.assertIsNone(a["human_natural_phrase"])
 def test_all_22_marriage_methods_retrieve_actual_book_lines_without_real_case_claims(self):
  for i in range(1,23):
   with self.subTest(scene=i):
    a=inspect_marriage_study_cast(db_path=FULL_DB,
     scene_id=f"marriage.scene.{i:02d}",
     example_key="shenqi_casting_example_1995_06_11",
     **EXAMPLES["shenqi_casting_example_1995_06_11"])
    self.assertEqual(len(a["factor_audit"]),len(FACTOR_IDS))
    self.assertEqual(len(a["source_chart"]["palaces"]),9)
    self.assertTrue(a["author_first_and_method_source_links"])
    for ref in a["author_first_and_method_source_links"]:
     self.assertEqual(len(ref["original_source_sha256"]),64)
     self.assertTrue(ref["source_line_numbers"])
    self.assertEqual(a["six_layer_execution_status"]["gpt_human_language"],"not_called_missing_structured_outcome")
 def test_source_scope_cannot_be_faked_or_palace_5_invented(self):
  with self.assertRaises(ValueError):
   inspect_marriage_study_cast(db_path=FULL_DB,scene_id="marriage.scene.02",
    example_key="shenqi_casting_example_1995_06_11",
    day_ganzhi="癸酉",solar_term="立秋",hour_ganzhi="丁巳")
  with self.assertRaises(ValueError):
   inspect_marriage_study_cast(db_path=FULL_DB,scene_id="marriage.scene.99",
    example_key="shenqi_casting_example_1995_06_11",**EXAMPLES["shenqi_casting_example_1995_06_11"])
  for key,v in EXAMPLES.items():
   c=SOURCE_EXAMPLES[key]
   chart=layout_from_explicit_bureau(dun=c["dun"],ju=c["ju"],hour_ganzhi=c["hour_ganzhi"])
   self.assertEqual(chart["palaces"]["5"]["door"],None)
   self.assertEqual(chart["palaces"]["5"]["deity"],None)
   factors=compute_source_chart_factors(chart)
   self.assertEqual(len(factors),24)
   self.assertEqual(factors["hidden_stems"]["status"],"unknown")
  self.assertEqual(element_relation("木","木"),"比和")
  self.assertEqual(element_relation("金","木"),"克")
  self.assertNotIn("杜门",DOOR_ELEMENTS.get("景门"))

 def test_external_chart_json_is_recomputed_and_actor_year_palaces_bound(self):
  import copy
  chart=layout_from_explicit_bureau(dun="yang",ju=3,hour_ganzhi="丁巳")
  payload={"chart":chart,"calendar_inputs":{
   "day_ganzhi":"癸酉","solar_term":"芒种","hour_ganzhi":"丁巳"},
   "original_casting_book_example_key":"shenqi_casting_example_1995_06_11",
   "inquiry":{"domain":"marriage","scene_id":"marriage.scene.02",
    "question_text":"我们两个人能否交往？",
    "relationship":"self",
    "querent":{"year_ganzhi":"癸酉"},
    "subject":{"year_ganzhi":"乙酉"},
    "partner":{"year_ganzhi":"庚寅"}}}
  data=inspect_marriage_chart_json(db_path=FULL_DB,payload=payload)
  self.assertEqual(data["status"],"actual_chart_json_source_consistent_pending_author_decision_and_timing")
  self.assertTrue(data["source_cast_replayed_from_json_and_consistent"])
  self.assertEqual(data["factor_checked_count"],24)
  self.assertEqual(data["actual_year_stem_candidate_binding"]["subject"]["candidate_palace_cells"][0]["palace"],1)
  self.assertEqual(data["actual_year_stem_candidate_binding"]["partner"]["candidate_palace_cells"][0]["palace"],1)
  self.assertEqual(data["factor_audit"]["palace_interactions"]["evidence"]["subject_to_partner"],"比和")
  self.assertEqual(data["factor_mechanically_resolved_count"],6)
  self.assertFalse(data["calendar_independently_verified"])
  self.assertIsNone(data["traditional_forecast_result"])
  self.assertIsNone(data["human_natural_phrase"])
  mutated=copy.deepcopy(payload)
  mutated["chart"]["palaces"]["3"]["door"]="杜门"
  with self.assertRaisesRegex(ValueError,"Nine-palace JSON altered"):
   inspect_marriage_chart_json(db_path=FULL_DB,payload=mutated)
  fake=copy.deepcopy(payload)
  fake["chart"]["status"]="engine_verified"
  with self.assertRaisesRegex(ValueError,"not independent source proof"):
   inspect_marriage_chart_json(db_path=FULL_DB,payload=fake)
  incomplete=copy.deepcopy(payload)
  del incomplete["inquiry"]["partner"]["year_ganzhi"]
  m=inspect_marriage_chart_json(db_path=FULL_DB,payload=incomplete)
  self.assertIn("person_year_ganzhi_missing:partner",m["missing_to_publish"])
  self.assertEqual(m["factor_audit"]["palace_interactions"]["status"],"unknown")

if __name__=="__main__":unittest.main()
