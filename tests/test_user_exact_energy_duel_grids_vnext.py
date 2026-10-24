"""User-authored 2026-10-23 two grids: pin all 25+25 literal cells.

No screenshot/OCR, interpolation, numeric score, coarse win/lose remapping,
or retrospective tuning. Verifies that selective real reading uses the table.
"""
import unittest

from src.wengua.factor_energy_25_rules import (
    USER_STAR_RELATIONS, USER_STAR_25, STAR_STAGES, lookup_25, inspect_strength_25)
from src.wengua.selected_duel_table_vnext import (
    USER_DUEL_5X5, DUEL_COLUMN_TIERS, user_duel_lookup,
    matchup, VERSION, USER_DUEL_TABLE_VERSION)
from src.wengua.health_text_pipeline_vnext_review import auto_cast_health_review_text
from src.wengua.user_domain_matrices_20261023 import CONTROL_NORMAL, raw_cell, CONTROL_GRID_VERSION


USER_STAR_ROWS={
    "旺":("极大","中等","大","大","极大"),
    "相":("极大","小","中等","中等","大"),
    "休":("大","极小","小","小","中等"),
    "囚":("中等","极小","极小","极小","小"),
    "废":("小","极小","极小","极小","极小"),
}
USER_DUEL_ROWS={
    "极小":("干得过","干得过","勉强干得过","干不过","硬干反而受伤"),
    "小":("轻松干得过","干得过","干得过","勉强干得过","干不过"),
    "中等":("非常简单干得过","轻松干得过","干得过","干得过","勉强干得过"),
    "大":("碾压式干得过","非常简单干得过","轻松干得过","干得过","干得过"),
    "极大":("世界级压制干得过","碾压式干得过","非常简单干得过","轻松干得过","干得过"),
}


class UserAuthoredCells(unittest.TestCase):
    def test_nine_star_exact_25_unreordered_user_columns(self):
        self.assertEqual(USER_STAR_RELATIONS,
                         ("宫生符号","宫克符号","符号克宫","符号生宫","比和"))
        self.assertEqual(set(USER_STAR_25),set(STAR_STAGES))
        for stage,row in USER_STAR_ROWS.items():
            self.assertEqual(USER_STAR_25[stage],row)
            for relation,expected in zip(USER_STAR_RELATIONS,row):
                with self.subTest(stage=stage,relation=relation):
                    fact=lookup_25("star",stage,relation)
                    self.assertEqual(fact["strength"],expected)
                    self.assertTrue(fact["user_exact_star_table"])
                    self.assertEqual(fact["table_version"],
                                     "user_exact_nine_star_5x5_20261023")
                    self.assertFalse(fact["status"]=="source_case_author_verified")
        self.assertEqual(len(USER_STAR_25)*len(USER_STAR_RELATIONS),25)

    def test_duel_exact_25_literal_labels_even_unusual_cases(self):
        self.assertEqual(DUEL_COLUMN_TIERS,("极小","小","中等","大","极大"))
        self.assertEqual(set(USER_DUEL_5X5),set(USER_DUEL_ROWS))
        for actor,row in USER_DUEL_ROWS.items():
            self.assertEqual(USER_DUEL_5X5[actor],row)
            for target,expected in zip(DUEL_COLUMN_TIERS,row):
                with self.subTest(actor=actor,target=target):
                    self.assertEqual(user_duel_lookup(actor,target),expected)
        self.assertEqual(user_duel_lookup("极小","小"),"干得过")
        self.assertEqual(user_duel_lookup("极小","极大"),"硬干反而受伤")
        self.assertEqual(user_duel_lookup("小","极小"),"轻松干得过")
        self.assertEqual(user_duel_lookup("极大","极小"),"世界级压制干得过")
        with self.assertRaises(ValueError):
            user_duel_lookup("弱","大")

    def test_all_25_pair_labels_survive_ONE_lookup_per_pair(self):
        # Use real inspected signifiers and every synthetic power-cell pair,
        # deliberately reverse palace context to prove it is NOT a rival.
        doctor=inspect_strength_25("star","天心星","申",6)
        illness=inspect_strength_25("star","天冲星","申",3)
        for a in DUEL_COLUMN_TIERS:
            for j,b in enumerate(DUEL_COLUMN_TIERS):
                x={**doctor,"strength_label":a,"palace_strength_label":b}
                y={**illness,"strength_label":b,"palace_strength_label":a}
                with self.subTest(from_power=a,to_power=b):
                    edge=matchup(x,y,actor_role="doctor",target_role="illness")
                    self.assertEqual(edge["duel_result"],CONTROL_NORMAL[a][j])
                    self.assertEqual(edge["control_result"],CONTROL_NORMAL[a][j])
                    self.assertNotIn("palace_duel_result",edge)
                    self.assertEqual(edge["table_two_lookups_for_pair"],1)
                    self.assertTrue(edge["palace_strength_is_context_only"])
                    self.assertEqual(edge["relation"],"克")
                    self.assertEqual(edge["version"],VERSION)
                    self.assertTrue(edge["raw_user_duel_cells_preserved"])

    def test_palace_context_is_not_a_second_strength_fight(self):
        doctor=inspect_strength_25("star","天心星","申",6)
        illness=inspect_strength_25("star","天冲星","申",3)
        low={**doctor,"strength_label":"极小","palace_strength_label":"极大"}
        high={**illness,"strength_label":"极大","palace_strength_label":"极小"}
        edge=matchup(low,high,actor_role="doctor",target_role="illness")
        self.assertEqual(edge["duel_result"],"反侮受损")
        self.assertTrue(edge["backfire_risk_symbolic"])
        self.assertEqual(edge["ability"],"不能")
        self.assertEqual(edge["table_two_lookups_for_pair"],1)
        # Swapping PALACE context cannot reverse or override table-two result.
        mixed={**doctor,"strength_label":"极大","palace_strength_label":"极小"}
        inverted={**illness,"strength_label":"极小","palace_strength_label":"极大"}
        edge=matchup(mixed,inverted,actor_role="doctor",target_role="illness")
        self.assertEqual(edge["duel_result"],"极限压制")
        self.assertEqual(edge["ability"],"能")
        self.assertNotIn("palace_duel_result",edge)
        obstructed={**doctor,"restrictions":["门迫待核"]}
        blocked=matchup(obstructed,illness,actor_role="a",target_role="b")
        self.assertEqual(blocked["ability"],"条件待核")
        self.assertEqual(blocked["duel_result"],
                         raw_cell(CONTROL_NORMAL,doctor["strength_label"],
                                  illness["strength_label"]))

    def test_raw_user_labels_flow_into_real_selected_health_reading(self):
        result=auto_cast_health_review_text(
            iso="2026-10-22T12:00:00-04:00",
            timezone_name="America/New_York",
            inquiry={"intent":"severity","relationship":"self",
                     "consultation_context":"direct_self"})
        net=result["full_health_role_strength_network"]
        self.assertEqual(net["mode"],"selective")
        self.assertEqual(net["factor_two_duel_table"],CONTROL_GRID_VERSION)
        self.assertEqual(net["factor_one_nine_star_table"],
                         "user_exact_nine_star_5x5_20261023")
        self.assertLessEqual(net["table_two_queries"],10)
        for edge in net["directed_edges"].values():
            if edge["relation"]=="克" and edge["control_status"]=="matched":
                self.assertEqual(edge["control_result"],raw_cell(
                    CONTROL_NORMAL,edge["actor_strength"],edge["target_strength"]))
                self.assertEqual(edge["table_two_lookups_for_pair"],1)
            else:
                self.assertIsNone(edge["control_result"])
                self.assertIn(edge["control_status"],(
                    "void_type_pending","factor_power_pending",
                    "not_control_relation","duplicate_attacker_label_pending"))
            self.assertTrue(edge["palace_strength_is_context_only"])
            self.assertNotIn("palace_duel_result",edge)
        # Revised complete-palace narrative only cites a control matrix when
        # an actually selected role has a real eligible 克 direction; the
        # fixed live chart can have no such usable edge.
        self.assertIn("对天芮病宫",result["reading_text"])
        self.assertIn("八神",result["reading_text"])
        self.assertIn("八门",result["reading_text"])
        self.assertNotIn("宫位对抗「",result["reading_text"])
        self.assertTrue(result["no_scoring"])
        self.assertFalse(result["medical_validity_claimed"])


if __name__=="__main__":
    unittest.main()
