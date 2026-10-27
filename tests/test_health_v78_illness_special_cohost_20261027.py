"""V7.8: only one physical palace base, special illness bonuses distinct.

No original books/cases altered. These are user clocks, not blind tests.
"""
import unittest
from scripts.ios_vnext_manual_colleague_natal_yi_20261027 import produce as colleague
from scripts.ios_vnext_manual_1920_female_20261027 import produce as elder
from src.wengua.health_five_level_quant_vnext import saturate
from src.wengua.health_quant_overlay_vnext import (
    special_disease_control_points,special_cohost_total)

class V78SpecialConditionalHealth(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.both=(colleague()["cases"][0],elder()["cases"][0])

    def test_cross_palace_control_triage_with_weak_attacker_precedence(self):
        cases=[(0,False,False,False,0),
               (1,False,False,True,0),
               (-1,False,False,False,0),
               (2,False,False,False,3),
               (3,False,False,True,5),
               (5,True,False,True,1),
               (3,False,True,True,1),
               (-5,True,False,False,1)]
        for power,av,controlled,dv,expected in cases:
            with self.subTest(power=power,av=av,controlled=controlled,dv=dv):
                self.assertEqual(special_disease_control_points(
                    attacker_score=power,attacker_void=av,
                    attacker_controlled=controlled,illness_void=dv),expected)

    def test_chief_earth_yi_ding_plus_separately_and_whole_palace_void(self):
        for c,e,expected in ((3,3,6),(2,3,5),(3,1,4),(2,1,3)):
            self.assertEqual(special_cohost_total(c,e),expected)
            self.assertEqual(special_cohost_total(c,e,void=True),expected//2)
        self.assertEqual(special_cohost_total(0,3,void=True),1)
        self.assertEqual(special_cohost_total(3,0,void=True),1)

    def test_both_original_user_clocks_include_cohost_once_not_extra_palace(self):
        for case,expected_n,expected_five in ((self.both[0],5,True),
                                                (self.both[1],4,False)):
            with self.subTest(clock=case["instant"]):
                s=case["summary"]
                physical=s["unique_palace_score_details"]
                self.assertEqual(s["unique_palace_count"],expected_n)
                self.assertEqual(len(physical),expected_n)
                self.assertEqual(s["post_void_known_sum"],
                                 sum(x["score"] for x in physical.values()))
                self.assertEqual(s["auspice_applied_extra_score"],
                                 s["auspice_bonus_score"])
                self.assertFalse(s["auspice_merged_into_physical_palace"])
                self.assertEqual(s["relationship_bonus_score"],
                                 s["control_bonus_score"]+
                                 s["weak_illness_drain_bonus_score"]+
                                 s["auspice_applied_extra_score"])
                self.assertEqual(s["five_not_global_penalty"],
                                 2*expected_n if expected_five else 0)
                raw=s["post_void_known_sum"]+s["relationship_bonus_score"]-s["five_not_global_penalty"]
                self.assertEqual(s["raw_final_before_saturation"],raw)
                self.assertEqual(s["score"],saturate(raw))
                self.assertEqual(s["final_scoring_policy"],
                    "V7.8_UNIQUE_PHYSICAL_PALACE_PLUS_CONDITIONAL_ILLNESS_AUSPICE")
                for pid,record in s["auspice_cohost_audit"].items():
                    self.assertEqual(record["after_void"],
                         special_cohost_total(record["chief"],record["stem_family"],
                                              void=record["empty"]))
                self.assertIn("伏吟",case["python_reading_text"])
                self.assertIn("五不遇时",case["python_reading_text"])
                summary=next(x["text"] for x in case["source_sections"] if x["id"]=="90_review")
                self.assertEqual(len(summary.split("\n\n")),2)
                self.assertIn("不能据此判断真实病情",summary)

    def test_colleague_yi_natal_still_not_new_palace_or_duplicated_symbol(self):
        case=self.both[0]
        self.assertEqual([case["four_pillars"][k] for k in
            ("year","month","day","hour")],["己丑","戊辰","辛卯","丁酉"])
        self.assertEqual(case["patient_birth_stem"],"乙")
        self.assertEqual(set(case["summary"]["unique_palace_score_details"]["3"]["unique_stem_scores"]),{"乙"})
        self.assertNotIn("gender",case["roles"])

    def test_elder_yi_hour_and_medicine_remain_one_actual_earth_sky_family(self):
        case=self.both[1]
        self.assertEqual([case["four_pillars"][k] for k in
            ("year","month","day","hour")],["己丑","庚午","丁亥","乙巳"])
        self.assertEqual(case["roles"]["medicine"]["palace"],case["roles"]["hour"]["palace"])
        self.assertEqual(set(case["summary"]["unique_palace_score_details"]["9"]["unique_stem_scores"]),{"乙","庚"})
        self.assertEqual(case["roles"]["chief"]["palace"],case["roles"]["gender"]["palace"])

if __name__=="__main__":
    unittest.main()
