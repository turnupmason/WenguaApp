"""User 2026-10-25: only relevant palaces, same palace = one score,
fake/true void signed +/-3 (not -5 or 0) and horse+void same palace fake.
One REAL 2024 historical learning cast is fixed as a reproducible regression.
"""
import unittest

from src.wengua.health_five_level_quant_vnext import (
    void_shift_three,palace_tally,multi_palace_tally)
from src.wengua.health_palace_detailed_vnext import inspect_role_void
from src.wengua.health_text_pipeline_vnext_review import auto_cast_health_review_text

DATE="2024-05-28T13:00:00-04:00"
QUERY={"intent":"severity","relationship":"self",
       "consultation_context":"direct_self","patient_sex":"male"}


class VoidScoreTests(unittest.TestCase):
    def test_18_signed_void_examples_and_same_current_result(self):
        for before,after in ((2,-1),(3,0),(-2,1),(-3,0),(0,0),
                             (1,-2),(-1,2),(5,2),(-5,-2)):
            for state in ("fake_void","true_void"):
                with self.subTest(before=before,state=state):
                    self.assertEqual(void_shift_three(before,void_state=state),after)
        self.assertEqual(void_shift_three(3,void_state="not_void"),3)
        self.assertEqual(palace_tally(
            factors={"star":3,"door":0,"deity":0,"pattern":0},
            void_state="fake_void")["score"],0)
        self.assertEqual(palace_tally(
            factors={"star":3,"door":0,"deity":0,"pattern":0},
            void_state="true_void")["score"],0)

    def test_void_in_actual_horse_palace_is_fake_even_without_month_help(self):
        # 午未时马=巳，真正落巽四；申月金不生、不比和巽木.
        v=inspect_role_void(
            palace=4,occupied_void_branches=("巳",),
            month_branch="申",hour_ganzhi="丁未")
        self.assertEqual(v["horse_branch"],"巳")
        self.assertEqual(v["horse_palace"],4)
        self.assertFalse(v["month_support"])
        self.assertTrue(v["horse_same_palace_void"])
        self.assertEqual(v["classification"],"fake_void")
        # Same branch becomes true void if no matching horse/moon support.
        w=inspect_role_void(
            palace=4,occupied_void_branches=("巳",),
            month_branch="申",hour_ganzhi="戊申")
        self.assertEqual(w["classification"],"true_void")

    def test_no_unrelated_place_and_no_prevoid_sum_can_overwrite_final(self):
        e=multi_palace_tally(palaces={
            "illness":{"palace":1,"score":-1,"raw_sum":4},
            "hour":{"palace":1,"score":-1,"raw_sum":4},
            "medicine":{"palace":3,"score":2,"raw_sum":-1},
            "aux":{"palace":6,"score":-2,"raw_sum":12}})
        self.assertEqual(e["unique_palace_count"],3)
        self.assertEqual(e["post_void_known_sum"],-1)
        self.assertEqual(e["score"],-1)
        self.assertEqual(e["raw_known_sum"],15)
        self.assertEqual(len(e["duplicate_physical_roles"]),1)


class Real2024SelectedChart(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report=auto_cast_health_review_text(
            iso=DATE,timezone_name="America/New_York",inquiry=QUERY)

    def test_real_2024_chart_and_only_selected_relevance_closure(self):
        r=self.report
        self.assertEqual(r["instant"],DATE)
        self.assertEqual(r["four_pillars"],{
            "year":"甲辰","month":"己巳","day":"壬辰","hour":"丁未"})
        self.assertEqual(len(r["nine_palaces"]),9)
        selected=set(r["scored_relevant_palaces"])
        net=r["full_health_role_strength_network"]
        self.assertEqual(selected,
                         {x["palace"] for x in net["nodes"].values()}|{2,6})
        self.assertEqual({int(x) for x in r["nine_palace_condition_facts"]},selected)
        self.assertTrue(set(net["nodes"]).issubset(
            {"illness","doctor","medicine","patient","hour",
             "chief","natal","gender"}))
        self.assertNotIn("extra_3",net["nodes"])
        self.assertEqual(selected,{1,2,3,6,8})

    def test_same_palace_same_current_score_even_if_different_roles(self):
        net=self.report["full_health_role_strength_network"]
        scored=net["candidate_five_grade_quantization"]
        pairs=(("illness","hour"),("patient","chief"))
        for a,b in pairs:
            self.assertEqual(scored["roles"][a]["palace"],
                             scored["roles"][b]["palace"])
            self.assertEqual(scored["roles"][a]["palace_score"]["score"],
                             scored["roles"][b]["palace_score"]["score"])
        self.assertEqual(scored["auxiliary_qian_kun"]["kun"]["palace_score"]["score"],
                         scored["roles"]["patient"]["palace_score"]["score"])
        self.assertEqual(scored["summary"]["unique_palace_count"],5)
        self.assertEqual(scored["summary"]["post_void_known_sum"],-4)
        self.assertEqual(scored["summary"]["score"],-4)
        self.assertEqual(scored["summary"]["grade"],"大凶")
        self.assertEqual(scored["summary"]["effective_palace_scores"],
                         {"1":-1,"3":-2,"8":-2,"2":5,"6":-4})
        self.assertEqual(scored["summary"]["pending_palaces"],[])
        self.assertIn("乾宫辅助（男）",self.report["reading_text"])
        self.assertNotIn("坤宫辅助（女）",self.report["reading_text"])


if __name__=="__main__":unittest.main()
