"""Book-original complete-family dev holdout: output labels never enter engine."""
from __future__ import annotations
import json,unittest
from scripts.evaluate_marriage_family_holdout_v16 import evaluate,QUESTIONS
class MarriageFamiliesNoLeak(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.report=evaluate()
 def test_real_book_dev_questions_exact_three_nonduplicated_inquiry_events(self):
  self.assertEqual(len(QUESTIONS),3)
  self.assertEqual(self.report["candidate_questions"],3)
  self.assertEqual(self.report["number_of_distinct_heldout_book_families"],2)
  self.assertTrue(self.report["author_judgment_and_feedback_never_initial_inference_inputs"])
  self.assertTrue(self.report["not_claimed_to_be_untouched_blind_test"])
 def test_source_chart_alignment_and_feedback_differentiation(self):
  for i,row in enumerate(self.report["results"]):
   self.assertIn("original_book_chart_alignment",row)
   self.assertIn("initial_inference_without_author_label_or_feedback",row)
   self.assertIn("validation_only_later",row)
   self.assertEqual(row["validation_only_later"]["book_reported_event_outcome"],"failure")
   view=row["initial_inference_without_author_label_or_feedback"]
   if view is not None:
    self.assertNotIn(row["heldout_event_family_id"],view["book_witness_families_used"])
    self.assertFalse(view["publication_ready"])
    self.assertNotIn("book_reported_event_outcome",view)
    self.assertNotIn("later_source_feedback_lines",view)
    self.assertIn(view["outcome"],("success","failure","mixed","unresolved"))
  self.assertGreaterEqual(self.report["printed_original_chart_alignment_count"],0)
  self.assertLessEqual(self.report["printed_original_chart_alignment_count"],3)
  self.assertLessEqual(self.report["matched_book_reported_outcomes"],
                       self.report["scored_decisive_cases"])
 def test_all_original_inputs_are_yongshen_and_four_pillar_specific(self):
  self.assertNotEqual(QUESTIONS[1][10],QUESTIONS[2][10])
  self.assertEqual(QUESTIONS[1][0],QUESTIONS[2][0])
  self.assertNotEqual(QUESTIONS[1][11],QUESTIONS[2][11])
if __name__=="__main__":unittest.main()
