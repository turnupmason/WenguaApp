"""Latest user's hand-corrected eight 5x5 tables, exactly 200 literal cells.

The fourth/fifth void tables are now definitively separated by whether
the SOURCE or TARGET is 真空, rather than guessed A/B aliases. Older
versions and failed experiments remain in repository history.
"""
import unittest
from src.wengua.user_domain_matrices_20261023 import (
    STAR_POWER,DOOR_POWER,STEM_POWER,POWER_RELATIONS,STEM_COLUMNS,
    DOOR_COLUMNS,STEM_STAGE_ROWS,CONTROL_GRID_BY_ID,
    CONTROL_NORMAL,CONTROL_FAKE_VOID_ATTACKER,CONTROL_FAKE_VOID_TARGET,
    CONTROL_TRUE_VOID_ATTACKER,CONTROL_TRUE_VOID_TARGET,CONTROL_GRID_VERSION,
    raw_cell,lookup_selected_factor,inspect_control,stem_month_relation)
from src.wengua.selected_duel_table_vnext import matchup

LEVELS=("极小","小","中等","大","极大")
STAR={
    "旺":("极大","中等","大","大","极大"),
    "相":("极大","小","中等","中等","大"),
    "休":("大","极小","小","小","中等"),
    "囚":("中等","极小","极小","极小","小"),
    "废":("小","极小","极小","极小","极小"),
}
NORMAL={
    "极小":("有效克制","有效克制","微弱克制","克制失效","反侮受损"),
    "小":("高效克制","有效克制","有效克制","微弱克制","克制失效"),
    "中等":("强力主克","高效克制","有效克制","有效克制","微弱克制"),
    "大":("绝对主克","强力主克","高效克制","有效克制","有效克制"),
    "极大":("极限压制","绝对主克","强力主克","高效克制","有效克制"),
}
FAKE_SOURCE={
    "极小":("减力克制","微弱克制","克制失效","反侮受损","完全失控"),
    "小":("有效克制","减力克制","反侮受损","完全失控","完全失控"),
    "中等":("高效克制","有效克制","减力克制","微弱克制","完全失控"),
    "大":("强力主克","高效克制","有效克制","减力克制","微弱克制"),
    "极大":("绝对主克","强力主克","高效克制","有效克制","减力克制"),
}
FAKE_TARGET={
    "极小":("高效克制","有效克制","完全失控","完全失控","完全失控"),
    "小":("强力主克","高效克制","减力克制","完全失控","完全失控"),
    "中等":("强力主克","有效主克","微弱克制","效力递减","克制失效"),
    "大":("绝对主克","强力主克","有效主克","微弱克制","效力递减"),
    "极大":("完全清除","完全清除","绝对主克","强力主克","微弱克制"),
}
TRUE_SOURCE={
    "极小":("完全失控","完全失控","完全失控","完全失控","完全失控"),
    "小":("完全失控","完全失控","完全失控","完全失控","完全失控"),
    "中等":("完全失控","完全失控","完全失控","完全失控","完全失控"),
    "大":("微弱克制","微弱克制","完全失控","完全失控","完全失控"),
    "极大":("减力克制","微弱克制","完全失控","完全失控","完全失控"),
}
TRUE_TARGET={
    "极小":("完全失控","完全失控","完全失控","完全失控","完全失控"),
    "小":("完全失控","完全失控","完全失控","完全失控","完全失控"),
    "中等":("完全失控","完全失控","完全失控","完全失控","完全失控"),
    "大":("完全失控","完全失控","完全失控","微弱克制","完全失控"),
    "极大":("完全失控","完全失控","完全失控","减力克制","微弱克制"),
}
STEM={
    "长生/冠带/临官/帝旺/沐浴":STAR["旺"],
    "胎 / 养":STAR["相"],"衰 / 病":STAR["休"],
    "囚":STAR["囚"],"死 / 墓 / 绝":STAR["废"],
}


class UserLiteralMatrixTests(unittest.TestCase):
    def test_all_eight_grids_are_exact_25_each(self):
        expected_door={
            "旺":STAR["旺"],"相":STAR["相"],"休":STAR["休"],
            "囚":STAR["囚"],"死":STAR["废"]}
        for name,real,expected in (
            ("star",STAR_POWER,STAR),
            ("stem",STEM_POWER,STEM),
            ("door",DOOR_POWER,expected_door),
            ("normal",CONTROL_NORMAL,NORMAL),
            ("fake_source",CONTROL_FAKE_VOID_ATTACKER,FAKE_SOURCE),
            ("fake_target",CONTROL_FAKE_VOID_TARGET,FAKE_TARGET),
            ("true_source",CONTROL_TRUE_VOID_ATTACKER,TRUE_SOURCE),
            ("true_target",CONTROL_TRUE_VOID_TARGET,TRUE_TARGET),
        ):
            self.assertEqual(real,expected,name)
            self.assertEqual(len(real),5,name)
            for row in real.values():self.assertEqual(len(row),5,name)
        self.assertEqual(DOOR_COLUMNS,("被宫生","宫迫","门破","生宫","比和"))
        self.assertEqual(STEM_COLUMNS,("被月令生","被月令克","克月令","生月令","比和"))
        self.assertEqual(len(set(STEM_STAGE_ROWS)-{"囚"}),12)
        self.assertEqual(CONTROL_GRID_VERSION,
                         "user_5x5_control_with_void_20261023_v3_corrected_roles")
        self.assertEqual(len(CONTROL_GRID_BY_ID),5)

    def test_life_group_vs_month_direction_no_substituting_star_rule(self):
        # 申为金; 乙木: 被月令克. 乙 stem uses actual-palace lifecycle.
        stem=lookup_selected_factor("stem","乙","申",3)
        self.assertEqual(stem["user_cell_col"],"被月令克")
        self.assertEqual(stem_month_relation("木","金"),"被月令克")
        self.assertEqual(stem["table_version"],
                         "user_stem_life_stage_x_month_relation_20261023_v1")
        for item in stem["stem_life_candidate_cells"]:
            self.assertEqual(item["strength"],raw_cell(
                STEM_POWER,item["row"],"被月令克",col_order=STEM_COLUMNS))
        self.assertEqual(
            set(x["stage"] for x in stem["stem_life_source_facts"]),
            set(x["stage"] for x in stem["palace_twelve_life_facts"]))
        star=lookup_selected_factor("star","天芮星","申",3)
        self.assertEqual(star["user_cell_row"],"旺")
        self.assertNotIn("stem_life_strength_pending",star)
        door=lookup_selected_factor("door","生门","申",3)
        self.assertIn(door["user_cell_row"],("旺","相","休","囚","死"))
        self.assertIn(door["user_cell_col"],DOOR_COLUMNS)
        self.assertTrue(door["user_original_door_label_preserved"])

    def test_twelve_life_two_palace_branches_are_not_guess_one(self):
        from src.wengua.user_domain_matrices_20261023 import STEM_STAGE_ROWS
        # Mock only the two independently verified lifecycle source branches;
        # produce genuinely distinct row powers, so fail closed.
        from unittest.mock import patch
        from src.wengua import user_domain_matrices_20261023 as module
        from src.wengua.factor_energy_25_rules import inspect_strength_25
        real=inspect_strength_25("stem","乙","申",6)
        fake={**real,"palace_twelve_life_facts":[
            {"branch":"戌","stage":"帝旺"},{"branch":"亥","stage":"绝"}]}
        with patch("src.wengua.factor_energy_25_rules.inspect_strength_25",
                   return_value=fake):
            output=lookup_selected_factor("stem","乙","申",6)
        self.assertIsNone(output["strength_label"])
        self.assertTrue(output["stem_life_strength_pending"])
        self.assertEqual(len(output["stem_life_candidate_cells"]),2)

    def test_control_normal_all_25_direct(self):
        for a,row in NORMAL.items():
            for b,value in zip(LEVELS,row):
                out=inspect_control(actor_power=a,target_power=b,
                                    palace_relation="克")
                self.assertEqual((out["status"],out["result"]),("matched",value))
                self.assertEqual(out["scenario"],"normal")

    def test_all_four_correct_void_cases_each_25_cells(self):
        self.assertEqual(set(CONTROL_GRID_BY_ID),{
            "normal","fake_void_attacker","fake_void_target",
            "true_void_attacker","true_void_target"})
        for a in LEVELS:
            for b in LEVELS:
                with self.subTest(actor=a,target=b):
                    for kwargs,key,expected in (
                        ({"attacker_fake_void":True},
                         "fake_void_attacker",FAKE_SOURCE),
                        ({"target_fake_void":True},
                         "fake_void_target",FAKE_TARGET),
                        ({"attacker_true_void":True},
                         "true_void_attacker",TRUE_SOURCE),
                        ({"target_true_void":True},
                         "true_void_target",TRUE_TARGET),
                    ):
                        out=inspect_control(
                            actor_power=a,target_power=b,
                            palace_relation="克",**kwargs)
                        self.assertEqual(out["status"],"matched")
                        self.assertEqual(out["scenario"],key)
                        self.assertEqual(out["result"],raw_cell(expected,a,b))
        self.assertEqual(inspect_control(
            actor_power="极小",target_power="极大",palace_relation="克",
            attacker_void_unknown=True)["status"],"void_type_pending")
        self.assertEqual(inspect_control(
            actor_power="极小",target_power="极大",palace_relation="克",
            attacker_true_void=True,target_fake_void=True)["status"],
                         "both_void_unspecified")
        self.assertEqual(inspect_control(
            actor_power="极小",target_power="极大",palace_relation="生")["status"],
                         "not_control_relation")
        with self.assertRaises(ValueError):
            inspect_control(actor_power="大",target_power="小",
                            palace_relation="克",attacker_true_void=True,
                            attacker_true_void_variant="A")
        with self.assertRaises(ValueError):
            inspect_control(actor_power="大",target_power="小",
                            palace_relation="克",attacker_fake_void=True,
                            attacker_fake_void_variant="B")

    def test_true_void_source_target_do_not_get_conflated(self):
        # Same strength pair yields different readings because the void
        # side is an explicit factual branch, not a second power duel.
        actor=inspect_control(actor_power="大",target_power="大",
                              palace_relation="克",attacker_true_void=True)
        target=inspect_control(actor_power="大",target_power="大",
                               palace_relation="克",target_true_void=True)
        self.assertEqual(actor["result"],"完全失控")
        self.assertEqual(target["result"],"微弱克制")
        self.assertNotEqual(actor["result"],target["result"])
        self.assertEqual(inspect_control(
            actor_power="极小",target_power="极小",palace_relation="克",
            target_fake_void=True)["result"],"高效克制")
        self.assertEqual(inspect_control(
            actor_power="极小",target_power="极小",palace_relation="克")["result"],
                         "有效克制")

    def test_matchup_can_choose_both_corrected_true_void_sides(self):
        actor=lookup_selected_factor("star","天心星","申",6)
        target=lookup_selected_factor("star","天冲星","申",3)
        self.assertEqual(matchup(actor,target,actor_role="a",target_role="b",
            attacker_true_void=True)["control_scenario"],"true_void_attacker")
        self.assertEqual(matchup(actor,target,actor_role="a",target_role="b",
            target_true_void=True)["control_scenario"],"true_void_target")

    def test_selected_matchup_no_second_palace_duel(self):
        a=lookup_selected_factor("star","天心星","申",6)
        b=lookup_selected_factor("star","天冲星","申",3)
        edge=matchup(a,b,actor_role="doctor",target_role="patient")
        self.assertEqual(edge["relation"],"克")
        self.assertEqual(edge["duel_result"],raw_cell(
            NORMAL,a["strength_label"],b["strength_label"]))
        self.assertEqual(edge["table_two_lookups_for_pair"],1)
        self.assertNotIn("palace_duel_result",edge)
        self.assertTrue(edge["palace_strength_is_context_only"])
        # Contradictory PALACE power metadata should not add a duel.
        changed=matchup({**a,"palace_strength_label":"极小"},
                        {**b,"palace_strength_label":"极大"},
                        actor_role="doctor",target_role="patient")
        self.assertEqual(edge["duel_result"],changed["duel_result"])


if __name__=="__main__":
    unittest.main()
