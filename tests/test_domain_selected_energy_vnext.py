"""Selection first -> hard-coded TABLE ONE -> hard-coded TABLE TWO -> topic verdict.

Verifies the default route does NOT perform the old all-palace Cartesian graph.
The old path remains separately tested through _research_full_graph opt-in.
"""
import unittest
from src.wengua.selected_duel_table_vnext import (
    table_one, matchup, USER_DUEL_5X5, user_duel_lookup, VERSION)
from src.wengua.domain_selected_energy_vnext import (
    DOMAIN_CASE_TEMPLATES, HEALTH_EDGES, selected_health_sequence)
from src.wengua.health_text_pipeline_vnext_review import auto_cast_health_review_text
from src.wengua.user_domain_matrices_20261023 import CONTROL_NORMAL, raw_cell, CONTROL_GRID_VERSION

WHEN="2026-10-22T12:00:00-04:00"
ZONE="America/New_York"
BASE={"intent":"severity","relationship":"self",
      "consultation_context":"direct_self"}


class CompactTables(unittest.TestCase):
    def test_two_separate_hardcoded_tables_and_25_case_exception(self):
        self.assertEqual(len(USER_DUEL_5X5),5)
        self.assertEqual(sum(len(row) for row in USER_DUEL_5X5.values()),25)
        a=table_one("star","天心星","申",6)
        b=table_one("star","天冲星","申",3)
        comparison=matchup(a,b,actor_role="doctor",target_role="illness")
        self.assertEqual(comparison["relation"],"克")
        self.assertIn(comparison["ability"],("能","不能","艰难","条件待核"))
        self.assertEqual(comparison["version"],VERSION)
        self.assertEqual(comparison["control_result"],raw_cell(
            CONTROL_NORMAL,a["strength_label"],b["strength_label"]))
        self.assertEqual(comparison["table_two_lookups_for_pair"],1)
        self.assertTrue(comparison["palace_strength_is_context_only"])
        self.assertNotIn("palace_duel_result",comparison)
        overflow=table_one("star","天芮星","亥",1)
        self.assertEqual(overflow["relation"],"符号克宫")
        self.assertTrue(overflow["one_compound_fact"])
        self.assertIsNone(table_one("deity","值符","亥",1)["symbol_month_stage"])

    def test_one_user_control_matrix_and_palace_context_only(self):
        a=table_one("star","天心星","申",6)
        b=table_one("star","天冲星","申",3)
        strong=matchup(a,b,actor_role="doctor",target_role="illness")
        self.assertEqual(strong["ability"],"能")
        weak_a={**a,"strength_label":"极小","palace_strength_label":"极小"}
        high_b={**b,"strength_label":"极大","palace_strength_label":"极大"}
        self.assertEqual(matchup(weak_a,high_b,actor_role="a",target_role="b")["ability"],"不能")
        # The factor's final strength is already fixed by TABLE ONE. Palace
        # strength remains context and must NOT start a second duel.
        mixed={**a,"strength_label":"极大","palace_strength_label":"极小"}
        high_palace={**b,"strength_label":"极小","palace_strength_label":"极大"}
        mixed_result=matchup(mixed,high_palace,actor_role="a",target_role="b")
        self.assertEqual(mixed_result["duel_result"],"极限压制")
        self.assertEqual(mixed_result["ability"],"能")
        self.assertFalse(mixed_result["backfire_risk_symbolic"])
        self.assertEqual(mixed_result["table_two_lookups_for_pair"],1)
        blocked={**a,"restrictions":["旬空待核"]}
        self.assertEqual(matchup(blocked,b,actor_role="a",target_role="b")["ability"],"条件待核")
        same=table_one("star","天心星","申",3)
        self.assertEqual(matchup(same,b,actor_role="a",target_role="b")["ability"],"不适用")

    def test_only_registered_subtype_is_eligible(self):
        self.assertEqual(set(DOMAIN_CASE_TEMPLATES),{("health","severity")})
        self.assertEqual(len(HEALTH_EDGES),14)  # includes verified real 值符->病宫/患者宫


class SelectedRealCases(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.unspecified=auto_cast_health_review_text(
            iso=WHEN,timezone_name=ZONE,inquiry=BASE)
        cls.male=auto_cast_health_review_text(
            iso=WHEN,timezone_name=ZONE,
            inquiry={**BASE,"patient_sex":"male"})
        cls.female=auto_cast_health_review_text(
            iso=WHEN,timezone_name=ZONE,
            inquiry={**BASE,"patient_sex":"female"})
        cls.birth=auto_cast_health_review_text(
            iso=WHEN,timezone_name=ZONE,
            inquiry={**BASE,"patient_sex":"male","patient_birth_ganzhi":"乙丑"})

    def test_default_unknown_sex_does_not_inspect_both_qian_kun(self):
        net=self.unspecified["full_health_role_strength_network"]
        self.assertEqual(net["mode"],"selective")
        self.assertIsNone(net["selected_gender_palace"])
        self.assertNotIn("gender",net["nodes"])
        self.assertNotIn("natal",net["nodes"])
        self.assertEqual(net["year_role_status"],"not_provided")
        self.assertFalse(net["precomputed_cartesian_pairs_materialized"])
        self.assertLessEqual(net["table_one_queries"],6)
        self.assertLessEqual(net["table_two_queries"],10)
        self.assertNotIn("乾六宫观察",self.unspecified["reading_text"])
        self.assertNotIn("坤二宫观察",self.unspecified["reading_text"])

    def test_gender_selection_male_qian_female_kun(self):
        male=self.male["full_health_role_strength_network"]
        female=self.female["full_health_role_strength_network"]
        self.assertEqual(male["selected_gender_palace"],6)
        self.assertEqual(male["unselected_gender_palace"],2)
        self.assertEqual(female["selected_gender_palace"],2)
        self.assertEqual(female["unselected_gender_palace"],6)
        self.assertEqual(male["nodes"]["gender"]["palace"],6)
        self.assertEqual(female["nodes"]["gender"]["palace"],2)
        self.assertNotIn(2,male["inspected_palace_ids"]
                         if 2 not in {x["palace"] for k,x in male["nodes"].items() if k!="gender"}
                         else [])
        self.assertTrue(all("all_cross_layer_factor_pairs" not in value
                            for value in male["directed_edges"].values()))

    def test_natal_only_if_real_birth_ganzhi(self):
        graph=self.birth["full_health_role_strength_network"]
        self.assertEqual(graph["year_role_status"],"bound_from_supplied_real_year")
        self.assertEqual(graph["nodes"]["natal"]["symbol"],"乙")
        self.assertIn("natal->illness",graph["directed_edges"])
        self.assertNotIn("natal",self.male["full_health_role_strength_network"]["nodes"])
        self.assertFalse(graph["precomputed_cartesian_pairs_materialized"])

    def test_no_cartesian_and_edges_are_domain_selected_only(self):
        for out in (self.unspecified,self.male,self.female,self.birth):
            net=out["full_health_role_strength_network"]
            self.assertEqual(net["mode"],"selective")
            self.assertLessEqual(len(net["nodes"]),8)
            self.assertLessEqual(len(net["directed_edges"]),14)
            self.assertEqual(len(net["directed_edges"]),net["table_two_queries"])
            self.assertEqual(len({key for key in net["nodes"]}),len(net["nodes"]))
            self.assertIn("doctor->illness",net["directed_edges"])
            self.assertIn("medicine->illness",net["directed_edges"])
            self.assertIn("patient->illness",net["directed_edges"])
            self.assertIn("hour->illness",net["directed_edges"])
            self.assertTrue(out["no_scoring"])
            self.assertFalse(out["medical_validity_claimed"])

    def test_template_order_and_one_disease_matrix_evidence(self):
        for out in (self.unspecified,self.male,self.birth):
            names=[s["title"] for s in out["sections"]]
            self.assertEqual(names[:5],[
                "起盘总纲：五不遇时、伏吟、反吟","天芮病宫","天心医生","乙奇医药","患者用神"])
            self.assertEqual(names[-1],"时空及应期")
            self.assertEqual(names[-2],"全部证据合断")
            evidence=[x for v in out["evidence_ledger"].values() for x in v]
            self.assertEqual(sum(x["id"].startswith("illness:tianrui_25:")
                                 for x in evidence),1)
            self.assertEqual(out["evidence_counts"]["qualified_favorable"],
                             len(out["evidence_ledger"]["favorable"]))
            self.assertEqual(out["evidence_counts"]["qualified_adverse"],
                             len(out["evidence_ledger"]["adverse"]))
            self.assertIn("候选",out["reading_text"])
            self.assertNotIn("加大药量",out["reading_text"])
            self.assertNotIn("康复保证",out["reading_text"])

if __name__=="__main__":
    unittest.main()
