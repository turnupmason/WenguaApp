"""Health severity V1: conditional 21-section deterministic fill, no prognosis."""
import copy
import unittest

from src.wengua.casting_shenqi import layout_from_explicit_bureau
from src.wengua.health_severity_template import render_health_severity, TEMPLATE
from src.wengua.phrase_pipeline import FACTOR_IDS


class HealthSeverityTemplateTest(unittest.TestCase):
    def setUp(self):
        # Actual historically regression-tested source casting method.
        self.chart = layout_from_explicit_bureau(
            dun="yang", ju=3, hour_ganzhi="丁巳")

    def run_case(self, inquiry=None, calendar=None):
        return render_health_severity(
            self.chart, inquiry or {"intent": "severity", "relationship": "self"},
            calendar=calendar or {"day_ganzhi": "癸酉", "month_branch": "午"})

    def test_exact_twenty_one_detailed_sections_and_all_factor_audits(self):
        report = self.run_case()
        self.assertEqual(len(report["sections"]), 21)
        self.assertEqual(report["audit"]["factors_expected"], 24)
        self.assertEqual(set(report["audit"]["factor_statuses"]), set(FACTOR_IDS))
        self.assertIn("天芮星落", report["reading_text"])
        self.assertIn("表面部位", report["reading_text"])
        self.assertIn("天盘", report["reading_text"])
        self.assertIn("天心星", report["reading_text"])
        self.assertIn("乙奇", report["reading_text"])
        self.assertIn("门迫", report["reading_text"])
        self.assertIsNone(report["audit"]["final_medical_severity"])
        self.assertIsNone(report["audit"]["medical_recovery_date"])
        self.assertNotIn("{", report["reading_text"])

    def test_no_birth_year_mandatory(self):
        report = self.run_case({"intent": "severity", "relationship": "father"},
                               {"month_branch": "寅"})
        self.assertIn("未提供出生年命", report["reading_text"])
        self.assertIn("个人用神", report["reading_text"])
        self.assertIn("personal_patient_yongshen", report["audit"]["unknown_factors"])
        self.assertEqual(report["status"], "draft_research_only_not_clinical_or_publishable")

    def test_relationship_not_guessed(self):
        mother = self.run_case({"intent": "severity", "relationship": "mother"})
        brother = self.run_case({"intent": "severity", "relationship": "brother"})
        self.assertIn("缺原书可执行的具体个人取用方法",
                      mother["slots"]["patient_binding"])
        self.assertIn("缺原书可执行的具体个人取用方法",
                      brother["slots"]["patient_binding"])
        with self.assertRaises(ValueError):
            self.run_case({"intent": "severity", "relationship": "not_in_book"})

    def test_tampered_palace_cannot_be_filled(self):
        wrong = copy.deepcopy(self.chart)
        wrong["palaces"]["1"]["earth_stem"] = "乙"
        with self.assertRaisesRegex(ValueError, "Cast recomputation mismatch"):
            render_health_severity(
                wrong, {"intent": "severity", "relationship": "self"})

    def test_no_false_month_break_or_timing_when_calendar_missing(self):
        report = self.run_case(calendar={"day_ganzhi": "癸酉"})
        self.assertEqual(report["slots"]["month_element"], "未知")
        self.assertIn("unknown", report["slots"]["month_break"])
        self.assertIn("不输出真实康复日期", report["slots"]["timing_result"])

    def test_door_press_only_door_controlling_palace(self):
        report = self.run_case()
        if report["slots"]["illness_door_relation"] == "迫":
            self.assertIn("已由门克宫确认", report["slots"]["door_press"])
        else:
            self.assertIn("不构成门迫", report["slots"]["door_press"])

    def test_wrong_intent_does_not_reuse_severity_template(self):
        with self.assertRaises(ValueError):
            render_health_severity(
                self.chart, {"intent": "treatment", "relationship": "father"})

    def test_no_independent_claim_of_cast_verification(self):
        report = self.run_case()
        self.assertEqual(report["chart_validation"],
                         "original_source_bureau_recast_only_not_calendar_verified")
        self.assertFalse(report["audit"]["historical_answers_used_as_inputs"])
        self.assertTrue(TEMPLATE.is_file())


if __name__ == "__main__":
    unittest.main()
