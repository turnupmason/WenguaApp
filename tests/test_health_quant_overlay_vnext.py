"""Guard current real-chart numeric candidate, never invent missing auspices."""
import unittest
from src.wengua.health_text_pipeline_vnext_review import auto_cast_health_review_text
from src.wengua.health_quant_overlay_vnext import render_quant_review


class CurrentQuantReview(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report=auto_cast_health_review_text(
            iso="2026-10-22T12:00:00-04:00",
            timezone_name="America/New_York",
            inquiry={"intent":"severity","relationship":"self",
                     "consultation_context":"direct_self"})

    def test_selected_roles_real_tier_not_imaginary_god_door_case(self):
        r=self.report
        net=r["full_health_role_strength_network"]
        q=net["candidate_five_grade_quantization"]
        self.assertIn(q["summary"]["status"],("unresolved_palaces","saturated_five_grade","calculated"))
        self.assertEqual(q["summary"]["score"],None if q["summary"]["pending_palaces"] else q["summary"]["score"])
        self.assertEqual(q["roles"]["illness"]["star"]["polarity"],"凶")
        self.assertEqual(q["roles"]["doctor"]["star"]["polarity"],"吉")
        for role in ("illness","doctor","patient","medicine","hour"):
            row=q["roles"][role]
            self.assertIn(row["door"]["status"],("calculated","neutral"))
            self.assertIsNotNone(row["door"]["score"])
            self.assertIn(row["door"]["applied_door_break_shift"],(0,2))
            self.assertTrue(row["door"]["strength_lookup_unchanged"])
            self.assertEqual(row["deity"]["status"],"calculated")
            self.assertIn(row["deity"]["score"],range(-5,6))
            self.assertIn(row["pattern"]["status"],
                             ("calculated","nontriggered_patterns_excluded_from_current_score"))
            self.assertIn(row["palace_score"]["status"],(
                "incomplete_components","void_signed_three_shift",
                "calculated","saturated_five_grade"))
        self.assertEqual(q["auxiliary_qian_kun"]["qian"]["selected_if_patient_gender_known"], q["selected_gender_palace"]==6)
        self.assertIn("qian",q["auxiliary_qian_kun"])
        self.assertIn("kun",q["auxiliary_qian_kun"])
        self.assertNotIn("宫位五级吉凶净分合断",r["reading_text"])
        self.assertIn("±5",render_quant_review(q))

    def test_selected_role_real_void_always_matches_new_priority(self):
        q=self.report["full_health_role_strength_network"][
            "candidate_five_grade_quantization"]
        details=self.report["full_health_role_strength_network"][
            "complete_selected_palace_audits"]
        for role,item in q["roles"].items():
            d=details[role]["void"]
            self.assertEqual(item["palace_score"]["void_state"],d["classification"])
            if d["classification"] in ("fake_void","true_void"):
                pal=item["palace_score"]
                if pal["score_before_void"] is not None:
                    before=pal["score_before_void"]
                    want=before-3 if before>0 else before+3 if before<0 else 0
                    self.assertEqual(pal["score"],want)
                    self.assertEqual(pal["status"],"void_signed_three_shift")
                    self.assertNotEqual(pal["score"],-5)
            if d.get("horse_cleared_void"):
                self.assertEqual(item["palace_score"]["void_state"],"not_void")

if __name__=="__main__": unittest.main()
