"""User 2026-10-24: 生门坎 / 景门乾 门破 remain normal (NO -2).

The user did NOT authorize turning door-break into an automatic 凶 door,
nor replacing its 200-cell monthly/palace energy cell.
"""
import unittest
from src.wengua.health_five_level_quant_vnext import (
    door_break_penalty_policy,palace_tally)
from src.wengua.health_quant_overlay_vnext import _quantize_one
from src.wengua.selected_duel_table_vnext import table_one
from src.wengua.health_palace_detailed_vnext import normalize_new_door_relation

MONTH="戌"
BASE={"star":5,"door":1,"deity":-3,"pattern":1}  # +4


def detail(door, palace):
    energy=table_one("door",door,MONTH,palace)
    return {"palace":palace,"stars":[],
            "door":energy,"deity":{"name":"九天","polarity":"更吉","relation":"比和"},
            "ordered_book_81_pairs":[],"heaven_stems":[],"earth_stem":{},
            "void":{"classification":"not_void","horse_cleared_void":False}}


class DoorBreakNoExtraPenalty(unittest.TestCase):
    def test_exact_two_are_still_door_break_but_skip_shift(self):
        for name,palace in (("生门",1),("景门",6)):
            with self.subTest(door=name,palace=palace):
                x=detail(name,palace)
                self.assertEqual(x["door"]["user_cell_col"],"门破")
                strength=x["door"]["strength_label"]
                policy=door_break_penalty_policy(
                    door_name=name,palace=palace,
                    door_relation=x["door"]["user_cell_col"])
                self.assertTrue(policy["has_door_break"])
                self.assertTrue(policy["no_extra_two_level_shift"])
                self.assertFalse(policy["apply_extra_two_level_shift"])
                self.assertEqual(policy["two_level_shift"],0)
                self.assertEqual(x["door"]["strength_label"],strength)
                audited=_quantize_one("medicine",x,five_not_encounter=False)
                self.assertEqual(audited["door"]["strength"],strength)
                self.assertEqual(audited["door"]["status"],"door_polarity_rule_pending")
                self.assertFalse(audited["palace_score"]["door_break"])
                self.assertEqual(audited["door"]["applied_door_break_shift"],0)

    def test_actual_other_door_break_uses_two_level_shift(self):
        for name,palace in (("景门",7),("死门",1),("休门",9),("开门",3)):
            with self.subTest(door=name,palace=palace):
                d=detail(name,palace)
                self.assertEqual(d["door"]["user_cell_col"],"门破")
                p=door_break_penalty_policy(
                    door_name=name,palace=palace,door_relation="门破")
                self.assertTrue(p["apply_extra_two_level_shift"])
                self.assertEqual(p["two_level_shift"],2)
                self.assertTrue(_quantize_one(
                    "medicine",d,five_not_encounter=False)[
                        "palace_score"]["door_break"])

    def test_no_confusion_between_gong_po_and_men_po(self):
        d=detail("开门",9)  # 宫火克门金 -> 宫迫
        self.assertEqual(d["door"]["user_cell_col"],"宫迫")
        p=door_break_penalty_policy(
            door_name="开门",palace=9,door_relation="宫迫")
        self.assertFalse(p["has_door_break"])
        self.assertFalse(p["apply_extra_two_level_shift"])

    def test_legacy_迫_is_preserved_but_does_not_double_block_new_门破(self):
        # Historical semantic_lookup originally called 门克宫 '迫'.
        # The latest user distinguishes 宫迫=宫克门 and 门破=门克宫.
        for name,palace in (("生门",1),("景门",6),("景门",7)):
            updated=normalize_new_door_relation(
                record={"door_pressure":True},
                cell={"door":name,"palace":palace},month_branch=MONTH)
            self.assertTrue(updated["legacy_door_pressure"])
            self.assertTrue(updated["door_break"])
            self.assertFalse(updated["door_pressure"])
            self.assertEqual(updated["door_relation_user_200_cells"],"门破")
            twice=normalize_new_door_relation(
                record=updated,cell={"door":name,"palace":palace},
                month_branch=MONTH)
            self.assertTrue(twice["legacy_door_pressure"])
            self.assertFalse(twice["door_pressure"])
        gong=normalize_new_door_relation(
            record={"door_pressure":False},
            cell={"door":"开门","palace":9},month_branch=MONTH)
        self.assertTrue(gong["door_pressure"])
        self.assertFalse(gong["door_break"])
        self.assertFalse(gong["legacy_door_pressure"])
        self.assertEqual(gong["door_relation_user_200_cells"],"宫迫")

    def test_signed_results_when_all_four_factors_are_verified(self):
        # +4 with no void; the only difference here is user-specified -2.
        ordinary=palace_tally(factors=BASE,door_break=False)
        other_break=palace_tally(factors=BASE,door_break=True)
        self.assertEqual((ordinary["score"],ordinary["grade"]),(4,"大吉"))
        self.assertEqual((other_break["score"],other_break["grade"]),(2,"小吉"))
        # Five-not-encounter still applies *once* to the two exempted doors.
        self.assertEqual(palace_tally(
            factors=BASE,five_not_encounter=True,door_break=False)["score"],2)
        self.assertEqual(palace_tally(
            factors=BASE,five_not_encounter=True,door_break=True)["score"],1)
        # Fake/true void overrides known energy, regardless of exception.
        self.assertEqual(palace_tally(
            factors=BASE,void_state="fake_void")["score"],0)
        self.assertEqual(palace_tally(
            factors=BASE,void_state="true_void")["score"],-5)

    def test_unverified_door_polarity_is_still_pending(self):
        x=_quantize_one("illness",detail("生门",1),five_not_encounter=False)
        self.assertIsNone(x["palace_score"]["score"])
        self.assertIsNone(x["door"]["score"])
        self.assertIn("door",x["palace_score"]["unresolved_categories"])


if __name__=="__main__":
    unittest.main()
