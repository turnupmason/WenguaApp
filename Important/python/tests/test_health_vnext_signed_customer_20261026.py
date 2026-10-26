"""New customer-facing signed five-band verdict from REAL selected palace scores.

No historical V3.9.1 changes, no made-up year-life and no medical prediction.
Strict cross-language section equality is independently hard-gated by iOS CI.
"""
import unittest

from src.wengua.health_five_level_quant_vnext import label
from src.wengua.health_text_pipeline_vnext_review import auto_cast_health_review_text
from src.wengua.health_reading_template_vnext import template

ZONE = "America/New_York"
WIFE = {"intent": "severity", "relationship": "wife",
        "consultation_context": "direct_proxy", "patient_sex": "female"}
NEW_CLOCKS = ("2021-10-03T03:00:00-04:00",
              "2023-04-24T21:00:00-04:00")


class SignedHealthCustomerVerbatim(unittest.TestCase):
    def test_five_band_grade_wording_and_no_veto_for_completed_total(self):
        self.assertIn("{grade}", template()["macros"]["overall_resolved"])
        for iso in NEW_CLOCKS:
            with self.subTest(instant=iso):
                r = auto_cast_health_review_text(
                    iso=iso, timezone_name=ZONE, inquiry=WIFE)
                full = r["reading_text"]
                q = r["full_health_role_strength_network"][
                    "candidate_five_grade_quantization"]
                self.assertIn("（天干仅列强弱）", full)
                self.assertIn("本宫综合", full)
                self.assertIn("未提供真实年命，不纳入本次计算。", full)
                self.assertIn("（同宫不另计病星）", full)
                # The source's own original score is decisive only if all
                # actually selected, de-duplicated real palaces are known.
                score = q["summary"]["score"]
                if score is None:
                    self.assertIn("当前不足以给出最终五档吉凶", full)
                else:
                    grade = "不凶不吉" if score == 0 else label(score)
                    self.assertIn("最终断为" + grade + "。", full)
                    self.assertNotIn("宫位本体与人物关系的判断尚有分歧", full)
                self.assertNotIn("健康指数", full)
                self.assertEqual(
                    full, "\n\n".join(
                        s["title"] + "：\n" + s["text"]
                        for s in r["sections"]))
                self.assertTrue(r["full_health_role_strength_network"][
                    "candidate_five_grade_quantization"]["summary"][
                        "duplicate_physical_roles"])


if __name__ == "__main__":
    unittest.main()
