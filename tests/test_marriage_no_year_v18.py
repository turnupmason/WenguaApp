"""V1.8 no birth year DOES NOT block marriage author inquiry.

No historical answer used as inference input. Historical examples 04/05
have already been consulted as development and are NOT sealed blinds.
When only one year is known, that one may inform an overlay; missing years
must not be fabricated.  All source citations include book,line,whole SHA.
"""
from __future__ import annotations
import copy,json,unittest
from pathlib import Path
from src.wengua.casting_shenqi import layout_from_explicit_bureau
from src.wengua.marriage_no_year_v18 import analyze_marriage_v18,_original_rules
from scripts.evaluate_marriage_other_families_v17 import CASES,_compare_printed_chart
ROOT=Path(__file__).resolve().parents[1]
DB=ROOT/"archives/sqlite/WenguaApp_双书194案例_婚姻多证据条件与新增家族验证V1_7_完整研究库.sqlite3"
def packet(original,*,no_year=True):
 chart=layout_from_explicit_bureau(
  dun=original["dun"],ju=original["ju"],hour_ganzhi=original["hour"])
 return {"chart":chart,
  "calendar_inputs":{"day_ganzhi":original["day"],"hour_ganzhi":original["hour"],
   "year_ganzhi":original["year"],"month_ganzhi":original["month"],
   "solar_term":original["solar_term"],"local_time_iso":original["date"],
   "iana_timezone":"Asia/Shanghai"},
  "inquiry":{"domain":"marriage","scene_id":original["scene"],
   "question_text":original["question"],"relationship":"self",
   "subject":{} if no_year else {"year_ganzhi":original["year_subject"]},
   "partner":{}}}
class OptionalYearBookAuthor(unittest.TestCase):
 def test_22_scenes_real_author_method_without_birth_year(self):
  for i in range(1,23):
   with self.subTest(scene=i):
    original=copy.deepcopy(CASES[1])
    original["scene"]=f"marriage.scene.{i:02d}"
    result=analyze_marriage_v18(db_path=DB,payload=packet(original),
       held_out_family_id="kaiwu.marriage.case05")
    self.assertEqual(result["status"],"v18_source_author_initial_decision_no_year_optional")
    self.assertEqual(result["year_role_binding"]["strategy"],"no_year_optional")
    self.assertTrue(result["missing_year_no_year_value_invented"])
    self.assertFalse(result["no_year_caused_block"])
    self.assertNotEqual(result["traditional_initial_outcome"],"unresolved")
    self.assertIn(result["traditional_initial_outcome"],("success","failure","mixed"))
    self.assertIsNone(result["year_role_binding"]["subject_year_palace"])
    self.assertIsNone(result["year_role_binding"]["partner_year_palace"])
    self.assertIsNone(result["primary_timing_if_justified"] if
       result["traditional_initial_outcome"]=="mixed" else None)
    self.assertFalse(result["publication_ready"])
    self.assertFalse(result["author_future_feedback_used_in_initial_decision"])
 def test_one_available_year_is_optional_overlay_not_a_dependent_required_pair(self):
  first=CASES[0]
  result=analyze_marriage_v18(db_path=DB,payload=packet(first,no_year=False),
      held_out_family_id=first["family"])
  self.assertEqual(result["year_role_binding"]["strategy"],"one_year_optional")
  self.assertIsNotNone(result["year_role_binding"]["subject_year_palace"])
  self.assertIsNone(result["year_role_binding"]["partner_year_palace"])
  self.assertNotEqual(result["traditional_initial_outcome"],"unresolved")
  self.assertEqual(result["source_multi_factor_conditions"]["source_rule_catalog_count"],27)
  self.assertEqual(len(result["source_rule_refs"]),10)
  self.assertEqual(result["year_role_binding"]["birth_year_supplement_used_only_when_supplied"],True)
  self.assertNotIn(first["family"],
     [x["event_family_id"] for x in result["prior_method_witness_holdout"]["pre_event_method_witnesses"]])
 def test_no_year_entire_family_holdout_keeps_later_feedback_out(self):
  for original in CASES:
   with self.subTest(family=original["family"]):
    payload=packet(original)
    chart=payload["chart"]
    source=_compare_printed_chart(chart,original["family"])
    self.assertTrue(source["agrees_with_original_book"])
    result=analyze_marriage_v18(db_path=DB,payload=payload,
             held_out_family_id=original["family"])
    witness=result["prior_method_witness_holdout"]
    self.assertTrue(all(x["event_family_id"]!=original["family"]
       for x in witness["pre_event_method_witnesses"]))
    self.assertFalse(result["author_future_feedback_used_in_initial_decision"])
    self.assertEqual(result["source_multi_factor_conditions"]["directional_stem_pair_count"],81)
    self.assertFalse(result["gpt_full_200_character_phrase_enabled"])
 def test_no_user_assigned_partner_gender_and_medical_accusation(self):
  result=analyze_marriage_v18(db_path=DB,payload=packet(CASES[1]),
       held_out_family_id="kaiwu.marriage.case05")
  self.assertTrue(result["cannot_make_specific_person_attitude_claim_without_identification"])
  self.assertTrue(result["year_role_binding"]["sexual_orientation_and_actual_gender_never_inferred"])
  self.assertTrue(result["source_multi_factor_conditions"]["traditional_symbolic_conditions_only"])
  self.assertEqual(result["source_rule_refs"]["kaiwu.line281"]["line"],281)
  self.assertEqual(result["source_rule_refs"]["kaiwu.line285"]["line"],285)
  for key,item in result["source_rule_refs"].items():
   self.assertEqual(len(item["whole_chapter_sha256"]),64)
   self.assertEqual(len(item["original_line_sha256"]),64)
if __name__=="__main__":unittest.main()
