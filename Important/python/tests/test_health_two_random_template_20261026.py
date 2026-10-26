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
    rejected = []
    # Technical acceptance only, never discard a chart for a negative verdict.
    # The very first 2022-04-22 draw exposed an existing centre-five
    # hosting guard, documented by failed CI run 40342643735 (preserved).
    for draw in range(1,31):
        year = rng.choice([2022,2023,2024,2025])
        month = rng.randint(1,12)
        day = rng.randint(1,28)
        hour = rng.choice(list(range(1,23,2)))
        instant = dt.datetime(year,month,day,hour,tzinfo=ZoneInfo(ZONE)).isoformat()
        assert instant not in seen
        seen.add(instant)
        try:
            out = auto_cast_health_review_text(
                iso=instant,timezone_name=ZONE,inquiry=INQUIRY)
        except ValueError as exc:
            why = str(exc)
            if not any(fragment in why for fragment in (
                "Timed value door falls into centre 5",
                "Patient signifier unresolved",
                "No confirmed actual chart palace for this person",
            )):
                raise
            rejected.append({"draw":draw,"instant":instant,"reason":why})
            print("WENGUA_20261026_TECH_REJECTION="+json.dumps(
                rejected[-1],ensure_ascii=False),flush=True)
            continue
        outputs.append({"draw":draw,"instant":instant,
                        "rejected_before":list(rejected),"report":out})
        if len(outputs)==2:
            return outputs
    raise AssertionError("Fewer than two technically calculable draws in first 30")

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
                "rejected_before":case["rejected_before"],
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
