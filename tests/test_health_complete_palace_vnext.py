"""User's full palace-by-palace illness severity template, on real charts.

No new casting method and no invented medical prognosis. Explicitly verifies
deity element/polarity, fake/true void by month/horse, real 81-pair provenance,
and one role-to-Tianrui majority without per-symbol double votes.
"""
import unittest
from src.wengua.health_palace_detailed_vnext import (
    GOOD_GODS,BAD_GODS,inspect_god,inspect_role_void,
    render_complete_selected_palace,void_kwargs)
from src.wengua.health_text_pipeline_vnext_review import auto_cast_health_review_text

WHEN="2026-10-22T12:00:00-04:00"
ZONE="America/New_York"
BASE={"intent":"severity","relationship":"self",
      "consultation_context":"direct_self"}


class UserVoidDefinition(unittest.TestCase):
    def test_month_generates_or_same_palace_means_fake_void(self):
        # 乾六宫为金, 申/酉金 month 比和 or 戌土 month 生金.
        for m in ("申","酉","戌"):
            x=inspect_role_void(palace=6,occupied_void_branches=["亥"],
                                month_branch=m,hour_ganzhi="庚子")
            self.assertEqual(x["classification"],"fake_void",m)
            self.assertTrue(x["month_support"])

    def test_horse_opposite_branch_clash_cancels_void_before_month(self):
        # 旬空在艮八宫寅，寅午戌时马在申，申冲寅，对角巽/乾
        # here 艮/坤 are the actual diagonally opposite palaces.
        x=inspect_role_void(palace=8,occupied_void_branches=["寅"],
                            month_branch="卯",hour_ganzhi="甲寅")
        self.assertEqual(x["classification"],"not_void")
        self.assertTrue(x["horse_cleared_void"])
        self.assertTrue(x["had_xun_void"])
        self.assertFalse(x["month_support"])
        self.assertTrue(x["horse_clashes_void"])
        self.assertEqual(x["horse_palace"],2)
        no=inspect_role_void(palace=8,occupied_void_branches=["寅"],
                             month_branch="卯",hour_ganzhi="己卯")
        self.assertEqual(no["classification"],"true_void")
        self.assertFalse(no["horse_clashes_void"])
        self.assertEqual(inspect_role_void(
            palace=8,occupied_void_branches=[],
            month_branch="卯",hour_ganzhi="甲寅")["classification"],
                         "not_void")


class EightDeityWithoutMonth(unittest.TestCase):
    def test_eight_names_and_actual_element_relation(self):
        self.assertEqual(GOOD_GODS,{"值符","六合","太阴","九天"})
        for deity in ("白虎","玄武","螣蛇","九地"):
            self.assertIn(deity,BAD_GODS)
        for name,element,relation,polarity in (
            ("值符","土","比和","更吉"),
            ("值符","金","生宫","微吉"),
            ("六合","木","比和","更吉"),
            ("白虎","金","比和","更凶"),
            ("白虎","火","被宫克","微凶"),
            ("九地","土","比和","更凶"),
        ):
            x=inspect_god(deity=name,palace_element=element)
            self.assertEqual((x["relation"],x["polarity"]),(relation,polarity))
            self.assertIsNone(x["month_stage"])
            self.assertTrue(x["not_independent_outcome_vote"])


class RealSelectedPalacePipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.self_reading=auto_cast_health_review_text(
            iso=WHEN,timezone_name=ZONE,inquiry=BASE)
        cls.male=auto_cast_health_review_text(
            iso=WHEN,timezone_name=ZONE,
            inquiry={**BASE,"patient_sex":"male"})

    def test_every_chosen_role_has_all_local_areas(self):
        graph=self.self_reading["full_health_role_strength_network"]
        self.assertEqual(graph["mode"],"selective")
        self.assertEqual(graph["void_rule_version"],
                         "user_20261024_void_horse_cancels_first_v2")
        for role in ("illness","doctor","medicine","patient","hour"):
            d=graph["complete_selected_palace_audits"][role]
            self.assertTrue(d["stars"])
            self.assertIsNotNone(d["door"])
            self.assertIsNotNone(d["deity"])
            self.assertTrue(d["heaven_stems"])
            self.assertIsNotNone(d["earth_stem"])
            self.assertIn(d["void"]["classification"],
                          ("not_void","fake_void","true_void"))
            self.assertIsInstance(d["ordered_book_81_pairs"],list)
            self.assertIn("九星",render_complete_selected_palace(d))
            self.assertIn("天地格",render_complete_selected_palace(d))
            self.assertFalse(d["medical_diagnosis"])
        self.assertIn("八神",self.self_reading["reading_text"])
        self.assertIn("八门",self.self_reading["reading_text"])
        self.assertIn("天盘干",self.self_reading["reading_text"])
        self.assertIn("地盘干",self.self_reading["reading_text"])

    def test_role_bindings_no_fabricated_year_or_both_gender_palaces(self):
        graph=self.self_reading["full_health_role_strength_network"]
        self.assertNotIn("natal",graph["complete_selected_palace_audits"])
        self.assertNotIn("gender",graph["complete_selected_palace_audits"])
        g=self.male["full_health_role_strength_network"]
        self.assertEqual(g["selected_gender_palace"],6)
        self.assertEqual(g["complete_selected_palace_audits"]["gender"]["palace"],6)
        self.assertEqual(g["role_group_reviews"]["gender"]["role_key"],"gender")
        self.assertNotIn("natal",g["role_group_reviews"])

    def test_qian_and_kun_are_always_real_auxiliaries_not_two_patients(self):
        for report in (self.self_reading,self.male):
            graph=report["full_health_role_strength_network"]
            qk=graph["qian_kun_auxiliary_observations"]
            self.assertEqual({qk["qian"]["palace"],qk["kun"]["palace"]},{6,2})
            for name in ("qian","kun"):
                ob=qk[name]
                self.assertTrue(ob["used_only_as_auxiliary"])
                self.assertTrue(ob["patient_identity_not_implied"])
                self.assertTrue(ob["cannot_vote_without_role_source"])
                self.assertTrue(ob["complete_palace"]["stars"])
                self.assertIsNotNone(ob["complete_palace"]["door"])
                self.assertIn(ob["relation_to_illness"],
                              ("生","克","受生","受克","比和"))
            self.assertIn("乾坤宫辅助观察",report["reading_text"])
        unknown=self.self_reading["full_health_role_strength_network"]
        self.assertIsNone(unknown["selected_gender_palace"])
        self.assertNotIn("gender",unknown["nodes"])

    def test_avoids_double_voting_multiple_symbols_of_same_palace(self):
        net=self.self_reading["full_health_role_strength_network"]
        reviews=net["role_group_reviews"]
        # Exactly one role->illness review for each requested fact group.
        for r in ("doctor","medicine","patient","hour"):
            self.assertIn(r,reviews)
            self.assertIn(reviews[r]["direction"],
                          ("favorable","adverse","pending"))
        receipts=[v for v in reviews.values() if v["counted_in_majority"]]
        self.assertEqual(len({v["physical_relation_id"] for v in receipts}),
                         len(receipts))
        for v in reviews.values():
            self.assertFalse(v["not_clinically_valid"]==False)
        counted=self.self_reading["evidence_counts"]
        ledger=self.self_reading["evidence_ledger"]
        self.assertEqual(counted["qualified_favorable"],len(ledger["favorable"]))
        self.assertEqual(counted["qualified_adverse"],len(ledger["adverse"]))
        self.assertIn("全部证据合断",self.self_reading["reading_text"])


if __name__=="__main__":
    unittest.main()
