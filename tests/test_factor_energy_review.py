"""Universal symbolic energy contract: no star/door/god/stem conflation."""
import unittest

from src.wengua.factor_energy_review import (
    DEITY_ELEMENTS, inspect_symbol_energy, illustrate_user_tianrui_scores,
)


class CrossDomainSymbolEnergyFacts(unittest.TestCase):
    def test_all_eight_deities_and_earth_value(self):
        self.assertEqual(DEITY_ELEMENTS["值符"], "土")
        self.assertEqual(len({x for x in DEITY_ELEMENTS if x != "腾蛇"}), 8)
        for deity in ("值符", "腾蛇", "太阴", "六合", "白虎", "玄武", "九地", "九天"):
            fact = inspect_symbol_energy("deity", deity, "申", 3)
            self.assertIsNone(fact["symbol_month_stage"])
            self.assertEqual(fact["palace_month_stage"], "死")
            self.assertFalse(fact["usable_as_final_verdict"])

    def test_star_and_palace_have_independent_month_strength(self):
        for branch, star_stage, palace_stage in (("申", "旺", "死"), ("亥", "休", "相")):
            fact = inspect_symbol_energy("九星", "天芮星", branch, 3)
            self.assertEqual(fact["symbol_month_stage"], star_stage)
            self.assertEqual(fact["palace_month_stage"], palace_stage)
            self.assertEqual(fact["nominal_relation_from_symbol"], "宫克符号")
            self.assertIsNone(fact["numeric_score"])
            self.assertNotEqual(fact["effective_control"], "supported")

    def test_door_keeps_ordinary_and_original_season_views(self):
        fact = inspect_symbol_energy("八门", "生门", "申", 3)
        self.assertEqual(fact["symbol_month_stage"], "休")
        self.assertIn(fact["book_door_month_stage"], ("旺", "相", "休", "囚", "死", None))
        self.assertEqual(fact["book_door_season"], "秋")
        self.assertTrue(fact["month_views_must_remain_distinct"])

    def test_stem_keeps_actual_palace_twelve_life(self):
        fact = inspect_symbol_energy("天干", "乙", "亥", 3)
        self.assertEqual(fact["symbol_month_stage"], "相")
        self.assertEqual(fact["palace_month_stage"], "相")
        self.assertTrue(fact["palace_twelve_life_facts"])
        self.assertTrue(fact["twelve_life_independent_of_month"])
        self.assertTrue(all("branch" in x and "stage" in x for x in fact["palace_twelve_life_facts"]))

    def test_user_arithmetic_examples_are_not_verdicts(self):
        a = illustrate_user_tianrui_scores("申")
        b = illustrate_user_tianrui_scores("亥")
        self.assertEqual((a["proposed_star_base"], a["proposed_nominal_palace_adjustment"], a["arithmetic_only_total"]), (10, -4, 6))
        self.assertEqual((b["proposed_star_base"], b["proposed_nominal_palace_adjustment"], b["arithmetic_only_total"]), (3, -4, -1))
        self.assertNotEqual(a["palace_month_stage"], b["palace_month_stage"])
        self.assertFalse(a["usable_as_verdict"] or b["usable_as_verdict"])
        self.assertFalse(a["usable_for_medical_guidance"] or b["usable_for_medical_guidance"])
        with self.assertRaises(ValueError):
            illustrate_user_tianrui_scores("酉")

    def test_reject_unknown_and_middle_palace(self):
        with self.assertRaises(ValueError):
            inspect_symbol_energy("star", "天芮星", "亥", 5)
        with self.assertRaises(ValueError):
            inspect_symbol_energy("star", "天芮星", "不存在", 3)
        with self.assertRaises(ValueError):
            inspect_symbol_energy("deity", "不知道", "亥", 3)


if __name__ == "__main__":
    unittest.main()
