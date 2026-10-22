"""USER REQUESTED STOP-GATE: 2026 丙午 戊戌 戊辰 壬戌 health/severity.

This is a new independent real-calendar input, NOT a sealed outcome blind:
the user hasn't supplied patient relationship or outcome. We run SELF only
as an explicitly conditional development fixture and do not approve other
health intents. This file NEVER hardcodes a divination chart, layout or verdict.
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

from src.wengua.astro_calendar import solar_chart_clock
from src.wengua.casting_shenqi import bureau_for_term, layout_from_explicit_bureau
from src.wengua.health_dynamic_v21 import analyze_health_v21


EXPECTED = {"year": "丙午", "month": "戊戌", "day": "戊辰", "hour": "壬戌"}
WALL_TIME = "2026-10-21T19:30:00-04:00"
TIMEZONE = "America/New_York"
AUDIT_MARKER = "USER_REQUEST_20261021_HEALTH_SEVERITY_TEST"


def run_case():
    """Live project code ONLY: calendar -> bureau -> real nine-palace -> 21 fields."""
    calendar = solar_chart_clock(WALL_TIME, TIMEZONE)
    if calendar["four_pillars"] != EXPECTED:
        raise AssertionError(
            "Input four pillars did not match actual offline calendar: "
            + json.dumps(calendar["four_pillars"], ensure_ascii=False))
    if calendar["active_solar_term"] != "寒露":
        raise AssertionError("Expected active term 寒露; never guess 霜降 from 戌月")
    method = bureau_for_term(EXPECTED["day"], calendar["active_solar_term"])
    chart = layout_from_explicit_bureau(
        dun=method["dun"], ju=method["ju"], hour_ganzhi=EXPECTED["hour"])
    inquire = {
        "domain": "health", "intent": "severity", "relationship": "self",
        "consultation_context": "direct_self",
        "asker_label": "自测者（仅为未确认身份的测试假设）"
    }
    pillars = calendar["four_pillars"]
    actual_calendar = {
        "year_ganzhi": pillars["year"],
        "month_ganzhi": pillars["month"],
        "day_ganzhi": pillars["day"],
        "hour_ganzhi": pillars["hour"],
        "month_branch": pillars["month"][1],
    }
    response = analyze_health_v21(
        chart=chart, inquiry=inquire, calendar=actual_calendar)
    return calendar, method, chart, inquire, response


class UserInputHealthSeverityGate(unittest.TestCase):
    def test_actual_four_pillar_calendar_and_bureau(self):
        calendar, method, chart, inquiry, result = run_case()
        self.assertEqual(calendar["four_pillars"],EXPECTED)
        self.assertEqual(calendar["active_solar_term"],"寒露")
        self.assertEqual(method["dun"],"yin")
        self.assertEqual(method["ju"],6)
        self.assertEqual(method["yuan"],"upper")
        self.assertEqual(chart["hour_ganzhi"],"壬戌")
        self.assertEqual(chart["xun_shou"],"甲寅")
        self.assertEqual(chart["value_star"],"天蓬星")
        self.assertEqual(chart["value_door"],"休门")
    def test_real_full_twenty_one_section_reading_no_invented_data(self):
        calendar, method, chart, inquiry, result = run_case()
        self.assertEqual(len(result["sections"]),21)
        self.assertEqual(result["intent"],"severity")
        self.assertEqual(result["role_binding"]["relationship"],"self")
        self.assertEqual(result["role_binding"]["role_via"],"day_stem")
        self.assertEqual(result["role_binding"]["stem"],"戊")
        self.assertTrue(result["audit"]["patient_birth_year_optional"])
        self.assertIsNone(result["audit"]["medical_severity_grade"])
        self.assertIsNone(result["audit"]["specific_disease_diagnosis"])
        self.assertIsNone(result["audit"]["recovery_date_as_clinical_claim"])
        self.assertEqual(len(result["audit"]["twenty_four_factors"]),24)
        self.assertNotIn("《神奇之门》",result["reading_text"])
        self.assertNotIn("《开悟之门》",result["reading_text"])
        self.assertNotIn("例如",result["reading_text"])
        self.assertNotIn("{patient_",result["reading_text"])
        self.assertGreater(len(result["reading_text"]),2300)
    def test_print_exact_full_unedited_runtime_output(self):
        calendar, method, chart, inquiry, result = run_case()
        print("\n" + AUDIT_MARKER + "_BEGIN")
        print("CALENDAR="+json.dumps(calendar,ensure_ascii=False,sort_keys=True))
        print("BUREAU="+json.dumps(method,ensure_ascii=False,sort_keys=True))
        print("CHART="+json.dumps(chart,ensure_ascii=False,sort_keys=True))
        print("INQUIRY="+json.dumps(inquiry,ensure_ascii=False,sort_keys=True))
        print("ROLE_BINDING="+json.dumps(result["role_binding"],ensure_ascii=False,sort_keys=True))
        print("CONCLUSION="+json.dumps({
            "status":result["status"],
            "intent":result["intent"],
            "sections":len(result["sections"]),
            "audit":result["audit"]
        },ensure_ascii=False,sort_keys=True))
        for i,section in enumerate(result["sections"],1):
            print("SECTION_%02d "%i+section["title"]+"："+section["text"])
        print(AUDIT_MARKER+"_END\n")


if __name__=="__main__":
    unittest.main()
