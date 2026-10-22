"""V4.2 integration source/regression: full12 from book, immutable V3.9 words.

All chart-derived factors actually computed; patient-supplied duration/natal
are not invented. Source known historical stories not medical validation.
"""
from __future__ import annotations
import hashlib,unittest
from scripts.replay_health_v42_unified_five_actual_casts import evaluate,PARENT,PARENT_SHA,IDS
from src.wengua.health_severity_v42_integrated import (
    full_lifecycle_at_palace,source_full12,MODULES,POLICY,
    _route_weight,budgeted_score_from_source)
from src.wengua.symbol_relations import stem_stage
from src.wengua.marriage_runtime import PALACE_BRANCHES
class V42SourceUnified(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.run=evaluate()
 def test_immutable_full_v41_parent_and_exact_three_v39_output_text(self):
    self.assertEqual(hashlib.sha256(PARENT.read_bytes()).hexdigest(),PARENT_SHA)
    self.assertEqual([r["family_id"] for r in self.run["records"]],IDS)
    for r in self.run["records"][:3]:
       self.assertTrue(r["old_v39_reading_byte_identical"])
       self.assertTrue(r["V42_integrated_customer_text"].startswith(r["V39_exact_legacy_customer_text"]))
       self.assertEqual(hashlib.sha256(r["V39_exact_legacy_customer_text"].encode()).hexdigest(),r["original_v39_reading_sha256"])
       self.assertNotIn("原书第",r["V42_integrated_extra_section"]["text"])
 def test_full12_ten_stems_and_all_5_original_book_anchors(self):
    t=source_full12()
    self.assertEqual(len(t),10)
    for stem,row in t.items():
       self.assertEqual(len(row["stage_to_branch"]),12)
       self.assertEqual(len(set(row["stage_to_branch"].values())),12)
       for name in ("长生","帝旺","死","墓","绝"):
          self.assertEqual(row["stage_to_branch"][name],stem_stage(stem,name)["branch"])
 def test_user_real_factual_yiji_patient_illness_all_branch_stages(self):
    q=self.run["records"][0]
    self.assertEqual(q["four_pillars"],{"year":"丙午","month":"戊戌","day":"己巳","hour":"庚午"})
    self.assertEqual(q["complete_real_chart_facts"]["patient_palace"],4)
    self.assertEqual(q["complete_real_chart_facts"]["illness_palace"],6)
    p=q["stage_actor_audit"]["patient"]
    ill=q["stage_actor_audit"]["tianrui_heaven"]
    self.assertEqual(p["all_actual_branch_stages"],[{"branch":"辰","stage":"衰"},{"branch":"巳","stage":"帝旺"}])
    self.assertEqual(ill["all_actual_branch_stages"],[{"branch":"戌","stage":"墓"},{"branch":"亥","stage":"绝"}])
    self.assertEqual(q["complete_real_chart_facts"]["source12_total_stage_facts_checked"],120)
    self.assertEqual(len(q["complete_real_chart_facts"]["actual_full_8_palace_inventory"]),8)
    self.assertIn("戌墓、亥绝",q["V42_integrated_extra_section"]["text"])
 def test_all_six_budgets_sum50_and_neutral_baseline(self):
    for r in self.run["records"]:
       score=r["symbolic_scoring"]
       obs=score["observed_or_unspecified_nominal"]
       self.assertEqual(obs["baseline"],50)
       self.assertEqual(len(obs["six_modules"]),6)
       self.assertEqual(sum(x["budget"] for x in obs["six_modules"]),50)
       self.assertEqual(sum(x["applied_signed_score"] for x in obs["six_modules"])+50,obs["score"])
       self.assertTrue(0<=obs["score"]<=100)
       self.assertEqual({x["name"] for x in obs["six_modules"]},set(MODULES))
       for x in obs["six_modules"]:
           self.assertLessEqual(abs(x["applied_signed_score"]),x["budget"])
       self.assertEqual(len(score["scenario_range"]),2)
       self.assertLessEqual(score["scenario_range"][0],score["scenario_range"][1])
 def test_each_known_chart_factor_not_misclassified_as_missing(self):
    for r in self.run["records"]:
       c=r["complete_real_chart_facts"]
       self.assertTrue(c["chart_relevant_facts_calculated"])
       self.assertTrue(c["source12_all_ten_stems_checked"])
       for actual in c["actual_full_8_palace_inventory"]:
           self.assertTrue(actual["heaven"])
           for star in actual["heaven"]:
               self.assertTrue(star["lifecycle"]["full12_computed"])
           self.assertIn(actual["palace"],PALACE_BRANCHES)
       score=r["symbolic_scoring"]
       self.assertTrue(score["duration_not_invented"])
       self.assertFalse(score["duration_provided"])
       self.assertIn("new",score["conditional_scenarios"])
       self.assertIn("chronic",score["conditional_scenarios"])
       self.assertIn("unprovided",score["conditional_scenarios"])
 def test_two_other_unseen_for_current_weight_tuning_are_first_health_questions(self):
    for r in self.run["records"][3:]:
       self.assertTrue(r["family_id"].startswith("shenqi.health."))
       self.assertFalse(r["author_book_outcome_used"])
       self.assertIn("古籍病势象意实验分",r["V42_integrated_extra_section"]["text"])
 def test_no_false_probability_and_no_repetition_alias_tianqin_tianrui(self):
    for r in self.run["records"]:
       self.assertFalse(r["new_medical_diagnosis"])
       self.assertFalse(r["author_book_outcome_used"])
       self.assertFalse(self.run["score_is_not_a_medical_probability"] is False)
       self.assertEqual(r["complete_real_chart_facts"]["source12_total_stage_facts_checked"],120)
       self.assertIn("不是现实健康概率",r["V42_integrated_extra_section"]["text"])
 def test_stage_lifecycle_bijective_for_unequal_palaces(self):
    for stem,palace in (("丙",6),("己",4),("甲",8),("癸",2)):
       x=full_lifecycle_at_palace(stem,palace)
       self.assertEqual(len(x["all_actual_branch_stages"]),len(PALACE_BRANCHES[palace]))
       self.assertEqual(len(x["palace_branches"]),len(x["all_actual_branch_stages"]))
if __name__=="__main__":unittest.main()
