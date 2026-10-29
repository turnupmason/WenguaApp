"""Regression: uploaded father 20 rows obey Five-Rat hourly stems.

The 18 blank rows are NOT caused by an illegal 日干/时干 pair. They were
blocked downstream by independent patient-source identity binding.
This test intentionally does not modify V8 scoring or force missing roles.
"""
from __future__ import annotations

import unittest

from src.wengua.casting_shenqi import hour_ganzhi_from_day
from src.wengua.core import cycle60

STEMS = "甲乙丙丁戊己庚辛壬癸"
BRANCHES = "子丑寅卯辰巳午未申酉戌亥"
DAY_ZI_START = {
    "甲": "甲", "己": "甲", "乙": "丙", "庚": "丙",
    "丙": "戊", "辛": "戊", "丁": "庚", "壬": "庚",
    "戊": "壬", "癸": "壬",
}
EXPECTED_FATHER_FIRST_20 = (
    ("甲子", "甲子"), ("甲子", "乙丑"), ("甲子", "丙寅"),
    ("甲子", "丁卯"), ("甲子", "戊辰"), ("甲子", "己巳"),
    ("甲子", "庚午"), ("甲子", "辛未"), ("甲子", "壬申"),
    ("甲子", "癸酉"), ("甲子", "甲戌"), ("甲子", "乙亥"),
    ("乙丑", "丙子"), ("乙丑", "丁丑"), ("乙丑", "戊寅"),
    ("乙丑", "己卯"), ("乙丑", "庚辰"), ("乙丑", "辛巳"),
    ("乙丑", "壬午"), ("乙丑", "癸未"),
)


def independent_five_rat(day: str, branch: str) -> str:
    """Independent 5-rat oracle, not copied output or a BigFish cast."""
    first = STEMS.index(DAY_ZI_START[day[0]])
    return STEMS[(first + BRANCHES.index(branch)) % 10] + branch


def first_twenty_day_hour() -> tuple[tuple[str, str], ...]:
    days = cycle60()
    return tuple(
        (days[i // 12], independent_five_rat(days[i // 12], BRANCHES[i % 12]))
        for i in range(20)
    )


class UploadedFather20FiveRatRegression(unittest.TestCase):
    def test_all_60_day_stems_x_12_hour_branches_reproduce_oracle(self):
        legal = set(cycle60())
        cases = 0
        for day in cycle60():
            for branch in BRANCHES:
                expected = independent_five_rat(day, branch)
                actual = hour_ganzhi_from_day(day[0], branch)
                self.assertEqual(actual, expected, (day, branch))
                self.assertIn(actual, legal, (day, branch))
                cases += 1
        self.assertEqual(cases, 720)

    def test_first_twenty_upload_all_legal_not_18_bad_hours(self):
        self.assertEqual(first_twenty_day_hour(), EXPECTED_FATHER_FIRST_20)
        for day, hour in EXPECTED_FATHER_FIRST_20:
            self.assertEqual(hour_ganzhi_from_day(day[0], hour[1]), hour)

    def test_jiazi_day_last_hour_is_yihai_then_yichou_zi_is_bingzi(self):
        # 21:00–23:00 is still 甲子日的乙亥时. Boundary happens AFTER 亥时.
        self.assertEqual(hour_ganzhi_from_day("甲", "亥"), "乙亥")
        self.assertEqual(hour_ganzhi_from_day("乙", "子"), "丙子")
        self.assertEqual(cycle60()[:2], ("甲子", "乙丑"))

    def test_jiazi_hour_and_jiaxu_hour_do_not_prove_jia_year_patient(self):
        # This fact guards against confusing 甲时遁干 and 父亲问测年干甲.
        from src.wengua.casting_shenqi import SIX_JIA
        self.assertEqual(SIX_JIA["甲子"], "戊")
        self.assertEqual(SIX_JIA["甲戌"], "己")
        self.assertNotEqual(SIX_JIA["甲子"], SIX_JIA["甲戌"])


if __name__ == "__main__":
    unittest.main()
