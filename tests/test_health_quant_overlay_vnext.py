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
        self.assertEqual(q["summary"]["status"],"unresolved_palaces")
        self.assertIsNone(q["summary"]["score"])
        self.assertEqual(q["roles"]["illness"]["star"]["polarity"],"凶")
        self.assertEqual(q["roles"]["doctor"]["star"]["polarity"],"吉")
        for role in ("illness","doctor","patient","medicine","hour"):
            row=q["roles"][role]
            self.assertEqual(row["door"]["status"],"door_polarity_rule_pending")
            self.assertIn(row["door"]["applied_door_break_shift"],(0,2))
            self.assertTrue(row["door"]["strength_lookup_unchanged"])
            self.assertEqual(row["deity"]["status"],
                             "deity_five_tier_conversion_missing")
            self.assertEqual(row["pattern"]["status"],
                             "pattern_full_source_gate_and_polarity_pending")
            self.assertIn(row["palace_score"]["status"],(
                "incomplete_components","fake_void_zero",
                "true_void_extreme_adverse"))
        self.assertTrue(q["auxiliary_qian_kun"]["qian"][
            "auxiliary_only_not_auto_counted"])
        self.assertIn("五级能量量化合断",r["reading_text"])
        self.assertIn("暂不生成虚构的极大吉",render_quant_review(q))

    def test_selected_role_real_void_always_matches_new_priority(self):
        q=self.report["full_health_role_strength_network"][
            "candidate_five_grade_quantization"]
        details=self.report["full_health_role_strength_network"][
            "complete_selected_palace_audits"]
        for role,item in q["roles"].items():
            d=details[role]["void"]
            self.assertEqual(item["palace_score"]["void_state"],d["classification"])
            if d["classification"]=="fake_void":
                self.assertEqual(item["palace_score"]["score"],0)
            elif d["classification"]=="true_void":
                self.assertEqual(item["palace_score"]["score"],-5)
            if d.get("horse_cleared_void"):
                self.assertEqual(item["palace_score"]["void_state"],"not_void")

if __name__=="__main__": unittest.main()
