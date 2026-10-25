"""Verification of current caster against user-stated 拆补 step contract.

Original 1995 book diagrams MUST retain all nine cells; intentionally do
not try to place a value DOOR in middle five for unresolved nonzero steps.
"""
import unittest
from datetime import datetime
from src.wengua.casting_chai_bu_audit_vnext import (
    verify_original_cast_steps,exact_within_offline_model_term_receipt)
from src.wengua.casting_shenqi import (
    bureau_for_term,layout_from_explicit_bureau,earth_plate)

class CastingUserFlow(unittest.TestCase):
    def test_original_books_yang_yin_nine_palaces_and_source_value(self):
        for dun,ju,hour in (("yang",3,"丁巳"),("yin",8,"戊戌"),
                            ("yang",2,"壬戌")):
            chart=layout_from_explicit_bureau(
                dun=dun,ju=ju,hour_ganzhi=hour)
            a=verify_original_cast_steps(chart=chart)
            self.assertTrue(a["verified"])
            self.assertTrue(a["earth_plate_luoshu_yang_forward_yin_reverse"])
            self.assertTrue(a["centre_tianqin_and_heaven_stem_travel_with_kun_two"])
            self.assertTrue(a["eight_deities_follows_value_star_yin_reverse_yang_forward"])
            self.assertEqual(a["chief_star_follows_hour_stem_to_palace"],
                             chart["value_star_palace"])
            self.assertEqual(a["chief_door_follows_hour_palace"],
                             chart["value_door_palace"])

    def test_solar_model_term_transitions_date_not_civil_month(self):
        for clock,zone in (
            ("1995-06-11T12:00:00+08:00","Asia/Shanghai"),
            ("1995-08-13T12:00:00+08:00","Asia/Shanghai"),
            ("2025-10-21T03:00:00-04:00","America/New_York"),
        ):
            a=exact_within_offline_model_term_receipt(
                iso=clock,timezone_name=zone)
            self.assertLess(
                datetime.fromisoformat(a["model_crossing_utc"]),
                datetime.fromisoformat(a["observed_at_utc"]))
            self.assertGreater(
                datetime.fromisoformat(a["next_model_crossing_utc"]),
                datetime.fromisoformat(a["observed_at_utc"]))
            self.assertEqual(len(a["clock_receipt_sha256"]),64)
            self.assertFalse(a["astronomical_externally_verified"])
            self.assertEqual(a["near_term_guard_degrees"],0.05)

    def test_near_solar_term_guard_remains_not_invented(self):
        a=exact_within_offline_model_term_receipt(
            iso="1995-06-11T12:00:00+08:00",
            timezone_name="Asia/Shanghai")
        # Even model bisection to seconds is NOT external astronomical
        # precision; the old source tester intentionally rejects uncertain
        # timestamps around the boundary.
        self.assertEqual(a["solar_term"],"芒种")
        self.assertEqual(bureau_for_term("癸酉",a["solar_term"])["ju"],3)
        with self.assertRaisesRegex(ValueError,"Astronomical solar-term boundary"):
            exact_within_offline_model_term_receipt(
                iso=a["model_crossing_utc"],
                timezone_name="UTC")

    def test_centre_door_zero_step_only_original_confirmed(self):
        with self.assertRaisesRegex(ValueError,"centre 5"):
            layout_from_explicit_bureau(dun="yang",ju=1,hour_ganzhi="戊辰")

if __name__=="__main__":
    unittest.main()
