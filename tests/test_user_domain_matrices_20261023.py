"""Regress eight exact handwritten 25-cell user grids = 200 cells.

The latest source correction fixes the former fake-attacker-B label as
true-attacker-A, adds another same-heading true-attacker-B, and forbids
guessing which one applies. Historical changes and failures are in git.
"""
import unittest
from src.wengua.user_domain_matrices_20261023 import (
    STAR_POWER,DOOR_POWER,STEM_POWER,POWER_RELATIONS,STEM_COLUMNS,
    DOOR_COLUMNS,STEM_STAGE_ROWS,CONTROL_GRID_BY_ID,
    CONTROL_NORMAL,CONTROL_FAKE_VOID_ATTACKER_A,
    CONTROL_FAKE_VOID_TARGET,CONTROL_TRUE_VOID_ATTACKER_A,
    CONTROL_TRUE_VOID_ATTACKER_B,CONTROL_GRID_VERSION,
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
ATT_A={
    "极小":("减力克制","微弱克制","克制失效","反侮受损","系统性失控"),
    "小":("有效克制","减力克制","反侮受损","系统性失控","系统性失控"),
    "中等":("高效克制","有效克制","减力克制","微弱克制","克制失效"),
    "大":("强力主克","高效克制","有效克制","减力克制","微弱克制"),
    "极大":("绝对主克","强力主克","高效克制","有效克制","减力克制"),
}
TARGET={
    "极小":("微弱克制","效力递减","克制失效","完全失控","完全失控"),
    "小":("有效主克","微弱克制","效力递减","克制失效","完全失控"),
    "中等":("强力主克","有效主克","微弱克制","效力递减","克制失效"),
    "大":("绝对主克","强力主克","有效主克","微弱克制","效力递减"),
    "极大":("完全清除","绝对主克","强力主克","有效主克","微弱克制"),
}
TRUE_A={
    "极小":("有效克制","减力克制","效力递减","克制失效","完全失控"),
    "小":("减力克制","效力递减","效力递减","克制失效","完全失控"),
    "中等":("断续克制","效力递减","克制失效","完全失控","完全失控"),
    "大":("克制失效","克制失效","完全失控","完全失控","完全失控"),
    "极大":("完全失控","完全失控","完全失控","完全失控","完全失控"),
}
TRUE_B={
    "极小":("终极解体","终极解体","终极解体","终极解体","终极解体"),
    "小":("丧失能力","丧失能力","完全失控","完全失控","完全失控"),
    "中等":("克制失效","克制失效","完全失控","完全失控","完全失控"),
    "大":("断续克制","效力递减","效力递减","克制失效","完全失控"),
    "极大":("微弱克制","断续克制","效力递减","克制失效","完全失控"),
}
STEM={
    "长生/冠带/临官/帝旺/沐浴":STAR["旺"],
    "胎 / 养":STAR["相"],"衰 / 病":STAR["休"],
    "囚":STAR["囚"],"死 / 墓 / 绝":STAR["废"],
}


class UserLiteralMatrixTests(unittest.TestCase):
    def test_all_eight_grids_are_exact_25_each(self):
        for name,real,expected in (
            ("star",STAR_POWER,STAR),("door",DOOR_POWER,
             {"旺":STAR["旺"],"相":STAR["相"],"休":STAR["休"],
              "囚":STAR["囚"],"死":STAR["废"]}),
            ("stem",STEM_POWER,STEM),
            ("normal",CONTROL_NORMAL,NORMAL),
            ("fake_attacker_A",CONTROL_FAKE_VOID_ATTACKER_A,ATT_A),
            ("fake_target",CONTROL_FAKE_VOID_TARGET,TARGET),
            ("true_attacker_A",CONTROL_TRUE_VOID_ATTACKER_A,TRUE_A),
            ("true_attacker_B",CONTROL_TRUE_VOID_ATTACKER_B,TRUE_B),
        ):
            self.assertEqual(real,expected,name)
            self.assertEqual(len(real)*len(next(iter(real.values()))),25,name)
        self.assertEqual(DOOR_COLUMNS,("被宫生","被宫克","门破","生宫","比和"))
        self.assertEqual(STEM_COLUMNS,("被月令生","被月令克","克月令","生月令","比和"))
        self.assertEqual(len(set(STEM_STAGE_ROWS)-{"囚"}),12)

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

    def test_corrected_fake_and_both_true_void_matrices_all_25_cells(self):
        self.assertEqual(set(CONTROL_GRID_BY_ID),{
            "normal","fake_void_attacker_A","fake_void_target",
            "true_void_attacker_A","true_void_attacker_B"})
        self.assertEqual(CONTROL_GRID_VERSION,
                         "user_5x5_control_with_void_20261023_v2_true_void")
        for a in LEVELS:
            for b in LEVELS:
                with self.subTest(a=a,b=b):
                    fake=inspect_control(actor_power=a,target_power=b,
                                         palace_relation="克",
                                         attacker_fake_void=True)
                    self.assertEqual(fake["scenario"],"fake_void_attacker_A")
                    self.assertEqual(fake["result"],raw_cell(ATT_A,a,b))
                    target=inspect_control(actor_power=a,target_power=b,
                                           palace_relation="克",
                                           target_fake_void=True)
                    self.assertEqual(target["result"],raw_cell(TARGET,a,b))
                    pending=inspect_control(actor_power=a,target_power=b,
                                             palace_relation="克",
                                             attacker_true_void=True)
                    self.assertEqual(pending["status"],
                                     "duplicate_true_attacker_label_pending")
                    self.assertIsNone(pending["result"])
                    self.assertEqual(
                        tuple(v["result"] for v in pending["candidate_tables"]),
                        (raw_cell(TRUE_A,a,b),raw_cell(TRUE_B,a,b)))
                    for variant,expected in (("A",TRUE_A),("B",TRUE_B)):
                        resolved=inspect_control(
                            actor_power=a,target_power=b,palace_relation="克",
                            attacker_true_void=True,
                            attacker_true_void_variant=variant)
                        self.assertEqual(resolved["result"],
                                         raw_cell(expected,a,b))
                        self.assertEqual(resolved["scenario"],
                                         "true_void_attacker_"+variant)
        self.assertEqual(inspect_control(
            actor_power="极小",target_power="极大",palace_relation="克",
            attacker_void_unknown=True)["status"],"void_type_pending")
        self.assertEqual(inspect_control(
            actor_power="极小",target_power="极大",palace_relation="克",
            attacker_true_void=True,target_fake_void=True)["status"],
                         "both_void_unspecified")
        self.assertEqual(inspect_control(
            actor_power="极小",target_power="极大",palace_relation="克",
            target_true_void=True)["status"],"target_true_void_unspecified")
        with self.assertRaises(ValueError):
            inspect_control(actor_power="大",target_power="小",
                            palace_relation="克",attacker_fake_void=True,
                            attacker_fake_void_variant="B")
        self.assertEqual(inspect_control(
            actor_power="极小",target_power="极大",palace_relation="生")["status"],
                         "not_control_relation")

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
