"""25 genuine month x palace families; no fabricated nine-palace labels.

Uses ORIGINAL nine-star season method and five-element palace month law to
cover five month states against all five ACTUAL Tianrui landing relations.
Regression makes sure this is one integrated symbol relation, not 25 votes.
"""
from __future__ import annotations

import unittest
from itertools import product

from src.wengua.health_tianrui_25_matrix import (
    inspect_tianrui_25,validate_matrix,MONTH_STAGES,RELATION_KEYS,TITLES)
from src.wengua.health_palace_sequence_vnext import element_month_stage
from src.wengua.health_severity_template import MONTH_ELEMENTS
from src.wengua.semantic_lookup import nine_star_month_status,STAR_ELEMENT
from src.wengua.marriage_runtime import ELEMENTS,element_relation

# Actual reachable star-palace relations, not artificial five-element text.
PALACES={"宫克星":3,"星生宫":6,"星克宫":1,"宫生星":9,"宫星比和":2}
BRANCH_FOR_STAGE={"旺":"酉","相":"辰","休":"子","囚":"卯","废":"午"}


class TwentyFiveRealMonthPalaceCases(unittest.TestCase):
    def actual(self,category,stage,**kwargs):
        palace=PALACES[category]
        branch=BRANCH_FOR_STAGE[stage]
        month_el=MONTH_ELEMENTS[branch]
        self.assertEqual(nine_star_month_status("天芮星",month_el)["value"],stage)
        return inspect_tianrui_25(
            star_month=nine_star_month_status("天芮星",month_el)["value"],
            star_element=STAR_ELEMENT["天芮星"],
            palace_element=ELEMENTS[palace],
            palace_month=element_month_stage(ELEMENTS[palace],month_el),
            **kwargs)

    def test_all_25_exactly_once_from_actual_month_palace_facts(self):
        self.assertEqual(validate_matrix(),25)
        visited=set()
        for category,stage in product(RELATION_KEYS,MONTH_STAGES):
            with self.subTest(category=category,stage=stage):
                got=self.actual(category,stage)
                self.assertEqual(got["category"],category)
                self.assertEqual(got["star_month"],stage)
                self.assertEqual(got["traditional_title"],
                                 TITLES[category][MONTH_STAGES.index(stage)])
                self.assertEqual(got["source_type"],
                                 "user_proposed_symbolic_hypothesis_not_original_author_verified")
                self.assertEqual(got["case_number"],
                                 RELATION_KEYS.index(category)*5+MONTH_STAGES.index(stage)+1)
                self.assertEqual(got["relation_from_star"],
                                 element_relation("土",ELEMENTS[PALACES[category]]))
                self.assertEqual(got["one_matrix_case_only"],True)
                self.assertEqual(got["medical_diagnosis_or_prognosis"],False)
                self.assertIn(got["eligible_evidence_direction"],
                              ("pending","favorable","adverse"))
                visited.add(got["case_id"])
        self.assertEqual(len(visited),25)

    def test_real_weak_palace_cannot_simply_eliminate_strong_tianrui(self):
        # 天芮月旺 = metal month; 巽/震 wood is month-weak -> 旺病被宫克
        # is a nominal relation, NOT qualified success.
        fact=self.actual("宫克星","旺")
        self.assertEqual(fact["palace_month"],"死")
        self.assertEqual(fact["effectiveness"],"limited")
        self.assertEqual(fact["eligible_evidence_direction"],"pending")

    def test_real_weak_star_with_actual_strong_controlling_palace(self):
        fact=self.actual("宫克星","囚") # wood month wood palace旺
        self.assertEqual(fact["palace_month"],"旺")
        self.assertEqual(fact["effectiveness"],"supported")
        self.assertEqual(fact["eligible_evidence_direction"],"favorable")

    def test_star_attacks_palace_must_compare_actual_month_strength(self):
        strong=self.actual("星克宫","旺") # 土月旺? star 旺 in 金month, 水宫 休
        weak=self.actual("星克宫","囚") 
        self.assertNotEqual(strong["case_id"],weak["case_id"])
        self.assertEqual(strong["relation_from_star"],"克")
        self.assertEqual(weak["relation_from_star"],"克")
        self.assertIn(weak["effectiveness"],("limited","conditional","obstructed"))

    def test_void_tomb_door_pressure_block_not_auto_cure(self):
        for blocked in (
            {"void_branches":["戌"]},
            {"sky_tombs":[{"stem":"己","branch":"丑"}]},
            {"earth_tombs":["丑"]},
            {"striking_stems":["庚"]},
            {"door_pressure":True},
        ):
            with self.subTest(blocked=blocked):
                got=self.actual("宫克星","囚",**blocked)
                self.assertEqual(got["effectiveness"],"obstructed")
                self.assertEqual(got["eligible_evidence_direction"],"pending")
                self.assertTrue(got["restrictions"])

    def test_nine_star_five_state_excludes_ordinary_stem_dead(self):
        with self.assertRaisesRegex(ValueError,"旺相休囚废"):
            inspect_tianrui_25(star_month="死",star_element="土",
                               palace_element="木",palace_month="旺")
        with self.assertRaisesRegex(ValueError,"Tianrui"):
            inspect_tianrui_25(star_month="旺",star_element="木",
                               palace_element="木",palace_month="旺")

    def test_physical_case_is_unique_not_two_tallies(self):
        from src.wengua.health_text_pipeline_vnext_review import auto_cast_health_review_text
        actual=auto_cast_health_review_text(
            iso="2026-11-01T05:00:00-05:00",
            timezone_name="America/New_York",
            inquiry={"intent":"severity","relationship":"self",
                     "consultation_context":"direct_self"})
        reality=actual["qualitative_palace_relationships"]["天芮星月令×星宫五行25格"]
        disease_votes=[
            x for direction in actual["evidence_ledger"].values()
            for x in direction if x["id"].startswith("illness:tianrui_25:")
        ]
        old_votes=[
            x for direction in actual["evidence_ledger"].values()
            for x in direction if x["id"].startswith("illness_star:")
        ]
        self.assertEqual(len(disease_votes),1)
        self.assertEqual(len(old_votes),0)
        self.assertIn(reality["traditional_title"],actual["reading_text"])
        self.assertEqual(reality["one_matrix_case_only"],True)
        self.assertTrue(actual["no_scoring"])
        self.assertTrue(actual["audit"]["legacy_v391_reading_text"])
        self.assertNotIn("癌细胞",actual["reading_text"])

if __name__=="__main__":
    unittest.main()
