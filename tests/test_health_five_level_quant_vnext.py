"""Exact five-level user-scored arithmetic, no unstated weighted gates."""
import unittest
from src.wengua.health_five_level_quant_vnext import (
    points,label,downgrade_strength,pattern_grade,adverse_shift,
    palace_tally,multi_palace_tally,void_shift_three)

class QuantizedCases(unittest.TestCase):
    def test_user_explicit_example_equals_plus_one_small_good(self):
        # star +4, door -5, deity -3 => -4 大凶
        assert points("大","吉")==4
        assert points("极大","凶")==-5
        assert points("中等","凶")==-3
        pattern=pattern_grade(polarity="吉",heaven_stage="长生",
                              source_gate_verified=True)
        self.assertEqual((pattern["base_tier"],pattern["score"]),("极大",5))
        self.assertEqual(sum((4,-5,-3)),-4)
        result=palace_tally(factors={"star":4,"door":-5,"deity":-3,
                                     "pattern":pattern["score"]})
        self.assertEqual(result["components"],
                         {"star":4,"door":-5,"deity":-3,"pattern":5})
        self.assertEqual(result["raw_sum"],1)
        self.assertEqual((result["score"],result["grade"]),(1,"极小吉"))

    def test_pattern_12_life_groups_and_tomb_punishment_each_one(self):
        for stage,tier in (
            ("长生","极大"),("冠带","极大"),("临官","极大"),
            ("帝旺","极大"),("沐浴","极大"),("胎","大"),
            ("养","大"),("衰","中等"),("死","中等"),
            ("墓","中等"),("绝","中等")):
            result=pattern_grade(
                polarity="凶",heaven_stage=stage,source_gate_verified=True)
            self.assertEqual(result["base_tier"],tier)
        self.assertEqual(pattern_grade(
            polarity="吉",heaven_stage="长生",earth_tomb=True,
            source_gate_verified=True)["score"],4)
        self.assertEqual(pattern_grade(
            polarity="吉",heaven_stage="长生",earth_tomb=True,
            earth_punishment=True,source_gate_verified=True)["score"],3)
        self.assertEqual(pattern_grade(
            polarity="吉",heaven_stage="胎",heaven_tomb=True,
            heaven_punishment=True,source_gate_verified=True)["score"],2)
        self.assertEqual(pattern_grade(
            polarity="凶",heaven_stage="死",earth_tomb=True,
            earth_punishment=True,source_gate_verified=True)["score"],-1)
        self.assertEqual(pattern_grade(
            polarity="吉",heaven_stage="长生",
            heaven_tomb=True,earth_tomb=True,
            heaven_punishment=True,earth_punishment=True,
            source_gate_verified=True)["score"],1)
        p=pattern_grade(polarity="吉",heaven_stage=["长生","绝"],
                        source_gate_verified=True)
        self.assertIsNone(p["score"])
        self.assertEqual(p["status"],"heaven_two_life_groups_pending")
        p=pattern_grade(polarity="吉",heaven_stage="长生",
                        source_gate_verified=False)
        self.assertIsNone(p["score"])
        self.assertEqual(p["candidate_score"],5)

    def test_five_not_or_doorbreak_two_tier_shift(self):
        tests=((3,1),(2,1),(1,1),(5,3),
               (-1,-3),(-2,-4),(-3,-5),(-5,-5),(0,0))
        for score,expected in tests:
            self.assertEqual(adverse_shift(score,2),expected)
        base={"star":4,"door":-5,"deity":-3,"pattern":5} # 1
        self.assertEqual(palace_tally(
            factors=base,five_not_encounter=True)["score"],1)
        self.assertEqual(palace_tally(
            factors={"star":5,"door":1,"deity":-3,"pattern":1},
            door_break=True)["score"],2)
        self.assertEqual(palace_tally(
            factors={"star":5,"door":1,"deity":-3,"pattern":1},
            door_break=True,five_not_encounter=True)["score"],1)

    def test_user_exact_void_signed_three_for_fake_and_true(self):
        for void in ("fake_void","true_void"):
            for current,expected in ((2,-1),(3,0),(-2,1),(-3,0),
                                     (0,0),(1,-2),(-1,2),(5,2),(-5,-2)):
                with self.subTest(kind=void,before=current):
                    self.assertEqual(void_shift_three(current,void_state=void),expected)
            self.assertEqual(void_shift_three(3,void_state="not_void"),3)
            base={"star":3,"door":0,"deity":0,"pattern":0}
            out=palace_tally(factors=base,void_state=void)
            self.assertEqual((out["score_before_void"],out["score"]),(3,0))
            self.assertEqual(out["status"],"void_signed_three_shift")
            self.assertEqual(out["void_adjustment"],-3)
            self.assertNotEqual(out["score"],-5)
        self.assertTrue(palace_tally(
            factors={"star":3,"door":0,"deity":0,"pattern":0},
            void_state="fake_void")["timing_can_refill_or_clash"])
        self.assertFalse(palace_tally(
            factors={"star":3,"door":0,"deity":0,"pattern":0},
            void_state="true_void")["timing_can_refill_or_clash"])
        with self.assertRaises(ValueError):
            palace_tally(factors={"star":3,"door":0,"deity":0,"pattern":0},
                         void_state="fake_void",horse_cleared_void=True)


    def test_missing_door_second_case_and_god_tier_do_not_auto_fill(self):
        result=palace_tally(
            factors={"star":4,"door":None,"deity":None,"pattern":None})
        self.assertIsNone(result["score"])
        self.assertEqual(result["known_subtotal"],4)
        self.assertEqual(set(result["unresolved_categories"]),
                         {"door","deity","pattern"})

    def test_sum_greater_than_five_is_explicitly_saturated_and_raw_preserved(self):
        result=palace_tally(
            factors={"star":5,"door":5,"deity":5,"pattern":5})
        self.assertEqual(result["raw_sum"],20)
        self.assertEqual(result["status"],"saturated_five_grade")
        self.assertEqual((result["score"],result["grade"]),(5,"极大吉"))
        self.assertEqual(result["saturated_from_raw"],20)
        self.assertEqual(label(-4),"大凶")

    def test_multi_palace_dedup_and_pending_bands(self):
        def row(p,score):
            return {"palace":p,"score":score}
        result=multi_palace_tally(palaces={
            "doctor":row(6,2),"medicine":row(6,2),
            "patient":row(3,-1),"illness":row(8,1)})
        self.assertEqual(result["raw_known_sum"],2)
        self.assertEqual(result["grade"],"小吉")
        self.assertEqual(result["unique_palace_count"],3)
        self.assertEqual(len(result["duplicate_physical_roles"]),1)
        self.assertEqual(multi_palace_tally(palaces={
            "doctor":row(6,5),"illness":row(8,5)})["status"],
                         "saturated_five_grade")
        self.assertEqual(multi_palace_tally(palaces={
            "doctor":row(6,None),"illness":row(8,-3)})["status"],
                         "unresolved_palaces")

if __name__=="__main__": unittest.main()
