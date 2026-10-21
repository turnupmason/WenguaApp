"""V1.7 two further event-family development studies, with missing birth data abstention."""
from __future__ import annotations
import unittest
from scripts.evaluate_marriage_other_families_v17 import evaluate
class UnseenBookFamiliesNoFakePrediction(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.result=evaluate()
 def test_other_family_ids_and_full_source_chart_alignment(self):
  r=self.result
  self.assertEqual(r["new_historical_event_families"],
                   ["kaiwu.marriage.case04","kaiwu.marriage.case05"])
  self.assertEqual(len(r["before_feedback_initial_study"]),2)
  self.assertTrue(r["not_untouched_sealed"])
  self.assertEqual(r["actual_new_forecast_correctness_scores"],0)
  self.assertTrue(r["case06_explicit_first_author_failure_kept_out_of_positive_training"])
  for row in r["before_feedback_initial_study"]:
   self.assertTrue(row["source_chart_alignment"]["agrees_with_original_book"])
   self.assertTrue(row["source_chart_alignment"]["center_five_not_fabricated"])
   self.assertEqual(row["source_chart_alignment"]["eight_printed_outer_palaces_checked"],8)
   self.assertEqual(row["initial_source_judgment"]["outcome"],"unresolved")
   self.assertIsNone(row["initial_source_judgment"]["future_window"])
   self.assertFalse(row["initial_source_judgment"]["publication_ready"])
   self.assertEqual(row["initial_source_judgment"]["real_81_ordered_pairs"],81)
 def test_no_author_outcome_label_was_allowed_into_inference(self):
  for item in self.result["after_initial_author_comments"]:
   self.assertTrue(item["author_outcome_vs_unobserved_future_not_scorable"])
   self.assertTrue(item["initial_author_verdict_was_not_a_model_input"])
   self.assertGreater(len(item["original_first_lines"]),0)
if __name__=="__main__":unittest.main()
