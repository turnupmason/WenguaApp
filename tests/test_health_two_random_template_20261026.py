"""Two NEW unbiased times on current 2026-10-25 editable V-next health template.
These are software demonstrations, not book cases or real patients.
Fail on failed technical casting rather than silently cherry-picking auspices.
"""
import datetime as dt
import json
import random
import unittest
from zoneinfo import ZoneInfo

from src.wengua.health_text_pipeline_vnext_review import auto_cast_health_review_text

SEED = 20261026
ZONE = "America/New_York"
INQUIRY = {"intent":"severity","relationship":"self",
           "consultation_context":"direct_self"}

def random_two_new_charts():
    rng = random.Random(SEED)
    seen = set()
    outputs = []
    for draw in range(1,3):
        year = rng.choice([2022,2023,2024,2025])
        month = rng.randint(1,12)
        day = rng.randint(1,28)
        hour = rng.choice(list(range(1,23,2)))
        instant = dt.datetime(year,month,day,hour,tzinfo=ZoneInfo(ZONE)).isoformat()
        assert instant not in seen
        seen.add(instant)
        # Don't change dates to obtain a preferred verdict; if the engine
        # cannot resolve a drawn time, keep the failure as a regression.
        out = auto_cast_health_review_text(
            iso=instant,timezone_name=ZONE,inquiry=INQUIRY)
        outputs.append({"draw":draw,"instant":instant,"report":out})
    return outputs

class TwoUnbiasedLiveTemplateCases(unittest.TestCase):
    def test_two_new_real_hour_customer_readings(self):
        outputs = random_two_new_charts()
        self.assertEqual(len(outputs),2)
        for case in outputs:
            report=case["report"]
            self.assertEqual(len(report["nine_palaces"]),9)
            self.assertIn("天芮",report["reading_text"])
            self.assertIn("天心",report["reading_text"])
            self.assertIn("古文",report["reading_text"])
            self.assertTrue(report["sections"])
            self.assertFalse(report["medical_validity_claimed"])
            print("WENGUA_20261026_TWO_RANDOM="+json.dumps({
                "seed":SEED,"draw":case["draw"],"instant":case["instant"],
                "four_pillars":report["four_pillars"],
                "solar_term":report["solar_term"],
                "bureau":report["bureau"],
                "first_stage_macro":report["first_stage_macro"],
                "role_palaces":report["full_health_role_strength_network"].get("nodes"),
                "quant":report["full_health_role_strength_network"].get("candidate_five_grade_quantization"),
                "verdict":report["verdict"],
                "sections":report["sections"],
                "reading_text":report["reading_text"]
            },ensure_ascii=False,separators=(",",":"),default=str))
if __name__ == "__main__":
    unittest.main()
