"""Deterministic strength tables must cover every symbol without false certainty."""
import unittest

from src.wengua.factor_energy_25_rules import (
    RELATIONS,STAR_STAGES,EARTH_STAGES,TIERS,lookup_25,
    inspect_strength_25,compare_role_strength,
    format_strength_template,format_duel_template)
from src.wengua.factor_energy_review import DEITY_ELEMENTS
from src.wengua.semantic_lookup import STAR_ELEMENT,DOORS
from src.wengua.health_severity_template import STEM_ELEMENTS


class UniversalTwentyFive(unittest.TestCase):
    def test_25_explicit_entries_for_every_class(self):
        for kind,stages in (("star",STAR_STAGES),("stem",EARTH_STAGES),
                            ("door",EARTH_STAGES),("deity",EARTH_STAGES)):
            seen=set()
            for month in stages:
                for rel in RELATIONS:
                    row=lookup_25(kind,month,rel)
                    self.assertIn(row["strength"],TIERS)
                    self.assertEqual(row["status"],"uncalibrated_review_heuristic")
                    seen.add(row["case_number"])
            self.assertEqual(seen,set(range(1,26)))

    def test_every_actual_symbol_reaches_all_25_theoretical_cases(self):
        kinds={
          "star":list(STAR_ELEMENT),
          "door":[name+"门" for name in DOORS],
          "stem":list(STEM_ELEMENTS),
          "deity":[name for name in DEITY_ELEMENTS if name!="腾蛇"],
        }
        for kind,names in kinds.items():
            for name in names:
                used=set()
                for branch in ("寅","巳","申","亥","辰"):
                    for palace in (3,9,6,1,2):
                        v=inspect_strength_25(kind,name,branch,palace)
                        used.add(v["case_number"])
                        self.assertIn(v["strength_label"],TIERS)
                        self.assertFalse(v["usable_as_final_verdict"])
                        self.assertTrue(v["one_compound_fact"])
                        self.assertIsNone(v["numeric_score"])
                        if kind=="deity":
                            self.assertIsNone(v["symbol_month_stage"])
                self.assertEqual(len(used),25,(kind,name,sorted(used)))

    def test_star_and_palace_season_are_independent(self):
        a=inspect_strength_25("star","天芮星","申",3)
        b=inspect_strength_25("star","天芮星","亥",3)
        self.assertEqual((a["symbol_month_stage"],a["palace_month_stage"]),("旺","死"))
        self.assertEqual((b["symbol_month_stage"],b["palace_month_stage"]),("休","相"))
        self.assertEqual((a["relation"],b["relation"]),("宫克符号","宫克符号"))
        self.assertNotEqual(a["strength_label"],b["strength_label"])
        self.assertIn("天芮星月令旺",format_strength_template(a))

    def test_gods_are_not_assigned_own_month_strength(self):
        a=inspect_strength_25("deity","值符","申",3)
        self.assertEqual(a["symbol_element"],"土")
        self.assertIsNone(a["symbol_month_stage"])
        self.assertIn("宫内承载",format_strength_template(a))

    def test_door_source_and_stem_both_planes_survive(self):
        door=inspect_strength_25("door","生门","申",3)
        self.assertTrue(door["month_views_must_remain_distinct"])
        self.assertIn("book_door_month_stage",door)
        heaven=inspect_strength_25("stem","乙","亥",3,plane="heaven")
        earth=inspect_strength_25("stem","乙","亥",3,plane="earth")
        self.assertEqual(heaven["palace_twelve_life_facts"],earth["palace_twelve_life_facts"])
        self.assertNotEqual(heaven["fact_id"],earth["fact_id"])

    def test_actual_control_vs_inverse_vs_blocker(self):
        actor=inspect_strength_25("star","天心星","申",6)
        target=inspect_strength_25("star","天冲星","申",3)
        result=compare_role_strength(actor,target,actor_name="天心",target_name="天冲")
        self.assertEqual(result["relation"],"克")
        self.assertEqual(result["ability_to_control"],"能")
        self.assertFalse(result["additional_evidence_vote"])
        self.assertIn("符号力量",format_duel_template(result))
        inverse=compare_role_strength(target,actor)
        self.assertEqual((inverse["relation"],inverse["ability_to_control"]),("被克","不适用"))
        blocked=inspect_strength_25("star","天心星","申",6,restrictions=("空亡待辨",))
        self.assertEqual(compare_role_strength(blocked,target)["ability_to_control"],"条件待核")
        same=inspect_strength_25("star","天心星","申",3)
        self.assertEqual(compare_role_strength(same,target)["relation"],"同宫")

    def test_synthetic_weak_attack_is_not_effective(self):
        # Synthetic comparison fixture validates comparator only; NOT a real chart.
        actor=inspect_strength_25("star","天心星","申",6)
        target=inspect_strength_25("star","天冲星","申",3)
        actor["strength_label"]=actor["palace_strength_label"]="极小"
        target["strength_label"]=target["palace_strength_label"]="极大"
        self.assertEqual(compare_role_strength(actor,target)["ability_to_control"],"不能")
        actor["strength_label"]="中等"
        self.assertEqual(compare_role_strength(actor,target)["ability_to_control"],"艰难")

    def test_invalid_stages_and_middle_blocked(self):
        with self.assertRaises(ValueError):lookup_25("star","死","比和")
        with self.assertRaises(ValueError):lookup_25("door","废","比和")
        with self.assertRaises(ValueError):lookup_25("star","旺","unknown")
        with self.assertRaises(ValueError):inspect_strength_25("star","天芮星","申",5)
        with self.assertRaises(ValueError):inspect_strength_25("star","天芮星","申",3,plane="false")

    def test_existing_health_vnext_integration(self):
        import inspect
        from src.wengua import health_palace_sequence_vnext
        code=inspect.getsource(health_palace_sequence_vnext.collect_sequence)
        # After factoring the audited role strengths into a reusable module,
        # ensure collect_sequence calls the helper and the helper still records
        # every real sky/earth/deity/door/star factor.
        self.assertIn("attach_all_factor_strengths",code)
        from src.wengua import health_full_role_network_vnext as network_module
        self.assertIn("all_symbol_strength_25",
                      inspect.getsource(network_module.attach_all_factor_strengths))
        self.assertIn("天心对天芮25格力量推演",code)
        self.assertIn("inspect_tianrui_25",code)


if __name__=="__main__":
    unittest.main()
