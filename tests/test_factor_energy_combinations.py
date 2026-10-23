"""Fixed combinatorics: no fifth actual relation ever silently disappears."""
import unittest

from src.wengua.factor_energy_combinations import (
    PRIMARY_RELATIONS,EXTRA_RELATION,PALACE_INTERACTIONS,
    LAYER20,LAYER5_EXCEPTION,GOD4,GOD_EXCEPTION,PAIR20X20,
    STEM_STAR_4X20,STEM_STAR_4X20X20,GOD4X20,PHYSICAL25,PAIR_PHYSICAL_25X25,
    single_case,compare_full_factors,format_full_pair)
from src.wengua.factor_energy_25_rules import inspect_strength_25


class FullSymbolCombinations(unittest.TestCase):
    def test_primary_four_five_is_20_per_kind(self):
        self.assertEqual(len(PRIMARY_RELATIONS),4)
        self.assertEqual(len(PALACE_INTERACTIONS),4)
        self.assertEqual(len(LAYER20),3)
        for kind in ("star","door","stem"):
            self.assertEqual(len(LAYER20[kind]),20)
            self.assertEqual(len(LAYER5_EXCEPTION[kind]),5)
            self.assertFalse(any(x[1]==EXTRA_RELATION for x in LAYER20[kind]))
            self.assertTrue(all(v["status"]=="uncalibrated_review_heuristic"
                                for v in LAYER20[kind].values()))
        self.assertEqual(len(GOD4),4)
        self.assertIsNone(next(iter(GOD4.values()))["god_month_stage"])

    def test_precomputed_full_star_star_400_and_all_seasonal_pairs(self):
        self.assertEqual(len(PAIR20X20),9)
        for kinds,pairs in PAIR20X20.items():
            self.assertEqual(len(pairs),400,kinds)
            self.assertTrue(all(p["comparison_only"] in
                         ("actor_stronger","target_stronger","equal_tier")
                         for p in pairs.values()))

    def test_stem_star_four_by_twenty_and_full_stem_states(self):
        self.assertEqual(len(STEM_STAR_4X20),80)
        self.assertEqual(len(STEM_STAR_4X20X20),1600)
        for direction in PALACE_INTERACTIONS:
            entries=[x for (rel,_),x in STEM_STAR_4X20.items()
                     if rel==direction]
            self.assertEqual(len(entries),20)
            self.assertTrue(all(x["needs_actual_stem20_and_both_palace_months"]
                                for x in entries))
        self.assertEqual(len(GOD4X20["star"]),80)
        self.assertEqual(len(GOD4X20["stem"]),80)
        self.assertEqual(len(GOD4X20["door"]),80)

    def test_real_tianxin_tianrui_pair_both_factors_independent(self):
        xin=inspect_strength_25("star","天心星","申",6)
        rui=inspect_strength_25("star","天芮星","申",3)
        pair=compare_full_factors(xin,rui,actor_name="天心星",target_name="天芮星")
        self.assertEqual(pair["relation"],"克")
        self.assertEqual(pair["actor_case"]["path"],"main_4x5_20")
        self.assertEqual(pair["target_case"]["path"],"main_4x5_20")
        self.assertIsNotNone(pair["precomputed_20x20_pair"])
        self.assertIn(pair["ability_to_control"],
                      ("能","不能","艰难","条件待核"))
        self.assertFalse(pair["additional_evidence_vote"])
        txt=format_full_pair(pair)
        self.assertIn("天心星",txt)
        self.assertIn("两宫克",txt)

    def test_stem_and_star_get_both_twenty_states_and_real_palace(self):
        stem=inspect_strength_25("stem","戊","亥",2)
        star=inspect_strength_25("star","天心星","亥",6)
        pair=compare_full_factors(stem,star,actor_name="戊干",target_name="天心星")
        self.assertEqual(pair["relation"],"生")
        self.assertIsNotNone(pair["precomputed_20x20_pair"])
        self.assertTrue(pair["needs_domain_yongshen_and_original_book_conditions"])
        self.assertNotEqual(pair["actor_fact_id"],pair["target_fact_id"])

    def test_four_case_default_preserves_fifth_real_case(self):
        # 土天芮星落坎水宫: 星克宫，不在用户主模板四关系内。
        overflow=inspect_strength_25("star","天芮星","亥",1)
        self.assertEqual(overflow["nominal_relation_from_symbol"],"符号克宫")
        self.assertEqual(single_case(overflow)["path"],"required_fifth_physical")
        normal=inspect_strength_25("star","天心星","亥",6)
        pair=compare_full_factors(overflow,normal)
        self.assertIsNone(pair["precomputed_20x20_pair"])
        self.assertIn("第五种",pair["fallback_reason"])
        # 别把神的落宫月令错当神自己的月令。
        deity=inspect_strength_25("deity","值符","亥",1)
        self.assertIsNone(deity["symbol_month_stage"])
        self.assertIn(single_case(deity)["path"],("deity_four","deity_fifth_physical"))
        mix=compare_full_factors(deity,normal)
        self.assertEqual(mix["actor_case"]["path"],single_case(deity)["path"])
        self.assertIsNone(mix["precomputed_20x20_pair"])

    def test_complete_physical_25x25_across_all_16_layer_pairs(self):
        self.assertEqual(set(PHYSICAL25),{"star","door","stem","deity"})
        self.assertEqual(len(PAIR_PHYSICAL_25X25),16)
        for kinds,catalog in PAIR_PHYSICAL_25X25.items():
            self.assertEqual(len(catalog),625,kinds)
            self.assertTrue(all(x["requires_actual_two_palace_conditions"]
                                for x in catalog.values()))
        overflow=inspect_strength_25("star","天芮星","亥",1)
        normal=inspect_strength_25("star","天心星","亥",6)
        combined=compare_full_factors(overflow,normal)
        self.assertTrue(combined["exhaustive_physical_pair_covered"])
        self.assertIsNotNone(combined["precomputed_physical_25x25_pair"])
        self.assertIsNone(combined["precomputed_20x20_pair"])
        deity=inspect_strength_25("deity","值符","亥",1)
        with_deity=compare_full_factors(deity,normal)
        self.assertTrue(with_deity["precomputed_physical_25x25_pair"][
            "deity_stage_is_only_palace_environment"])

    def test_blocked_and_same_palace_remain_indeterminate(self):
        xin=inspect_strength_25("star","天心星","申",6,
                                restrictions=("入墓条件需核",))
        rui=inspect_strength_25("star","天芮星","申",3)
        self.assertEqual(compare_full_factors(xin,rui)["ability_to_control"],"条件待核")
        same=inspect_strength_25("star","天心星","申",3)
        self.assertEqual(compare_full_factors(same,rui)["relation"],"同宫")
        self.assertEqual(compare_full_factors(same,rui)["ability_to_control"],"不适用")

    def test_existing_health_vnext_uses_cross_grid_without_new_vote(self):
        import inspect
        from src.wengua import health_palace_sequence_vnext
        src=inspect.getsource(health_palace_sequence_vnext.collect_sequence)
        self.assertIn("all_symbol_strength_25",src)
        self.assertIn("compare_full_factors",src)
        self.assertIn("天心对天芮25格力量推演",src)
        self.assertIn("inspect_tianrui_25",src)


if __name__=="__main__":
    unittest.main()
