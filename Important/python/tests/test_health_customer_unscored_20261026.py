"""Customer speech never exposes internal scoring; researcher DTO stays available."""
import unittest
from src.wengua.health_text_pipeline_vnext_review import auto_cast_health_review_text
from src.wengua.health_reading_template_vnext import template

class CustomerOnlyUnscored(unittest.TestCase):
    def test_template_has_no_visible_score_words(self):
        t=template()
        self.assertEqual(t["schema"],"health_severity_user_editable_template_v20261026_customer_v3_explicit_signed_grades")
        user_slots=("role","auxiliary","overall_resolved","overall_pending","verdict","timing")
        for slot in user_slots:
            text=t["macros"][slot]
            self.assertNotIn("{palace_score}",text)
            self.assertNotIn("{score}",text)
            self.assertNotIn("{post_void_sum}",text)
            self.assertNotIn("净分",text)
        self.assertEqual(t["macros"]["role_score"],"")
        self.assertIn("native_customer",t)

    def test_two_actual_casts_keep_private_quant_but_customer_unscored(self):
        for iso in ("2025-07-18T03:00:00-04:00","2022-07-19T11:00:00-04:00"):
            report=auto_cast_health_review_text(
                iso=iso,timezone_name="America/New_York",
                inquiry={"intent":"severity","relationship":"self",
                         "consultation_context":"direct_self"})
            text=report["reading_text"]
            self.assertIn("天芮",text)
            self.assertIn("全部证据合断",text)
            self.assertNotIn("宫内吉凶能量：",text)
            self.assertNotIn("五级吉凶净分",text)
            self.assertNotIn("原始净分",text)
            self.assertIn("天干仅列强弱",text)
            self.assertNotIn("合计-7分",text)
            self.assertNotIn("最后按±5",text)
            self.assertFalse(any(s["id"]=="89_quant" for s in report["sections"]))
            self.assertIsNotNone(report["full_health_role_strength_network"]
                                  ["candidate_five_grade_quantization"]["summary"])

if __name__=="__main__":unittest.main()
