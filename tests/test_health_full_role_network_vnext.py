"""All health factors, including true Qian/Kun and optional birth life."""
import unittest

from src.wengua.health_text_pipeline_vnext_review import auto_cast_health_review_text

WHEN="2026-10-22T12:00:00-04:00"
ZONE="America/New_York"
BASE={"intent":"severity","relationship":"self",
      "consultation_context":"direct_self"}


class FullIllnessRoleNetwork(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.no_birth=auto_cast_health_review_text(
            iso=WHEN,timezone_name=ZONE,inquiry=BASE)
        cls.male_birth=auto_cast_health_review_text(
            iso=WHEN,timezone_name=ZONE,
            inquiry={**BASE,"patient_sex":"male","patient_birth_ganzhi":"乙丑"})
        cls.female=auto_cast_health_review_text(
            iso=WHEN,timezone_name=ZONE,
            inquiry={**BASE,"patient_sex":"female"})

    def test_real_qian_and_kun_always_both_present_even_when_sex_unknown(self):
        graph=self.no_birth["full_health_role_strength_network"]
        self.assertTrue(graph["qian_and_kun_always_observed"])
        self.assertEqual(graph["nodes"]["qian"]["palace"],6)
        self.assertEqual(graph["nodes"]["kun"]["palace"],2)
        self.assertEqual(graph["nodes"]["qian"]["role_status"],
                         "physical_palace_observation_only")
        self.assertEqual(graph["nodes"]["kun"]["role_status"],
                         "physical_palace_observation_only")
        for key in ("qian","kun"):
            node=graph["nodes"][key]
            kinds={x["kind"] for x in node["all_factors"]}
            self.assertEqual(kinds,{"deity","door","star","stem"})
            self.assertTrue(node["life_stage_earth"])
            self.assertTrue(node["life_stage_sky"])
            self.assertTrue(node["symbol_strength"])
            self.assertTrue(node["palace_strength"])
            self.assertFalse(node["eligible_as_independent_verdict_vote"])
        self.assertIn("乾六宫",self.no_birth["reading_text"])
        self.assertIn("坤二宫",self.no_birth["reading_text"])
        self.assertIn("年命、时干与乾坤全宫力量",
                      [s["title"] for s in self.no_birth["sections"]])

    def test_year_missing_is_explicit_and_never_fabricated(self):
        graph=self.no_birth["full_health_role_strength_network"]
        self.assertTrue(graph["missing_natal_not_fabricated"])
        self.assertFalse(graph["nodes"]["natal"]["present"])
        self.assertNotIn("natal->illness",graph["directed_edges"])
        self.assertIn("患者年命未提供",self.no_birth["reading_text"])
        present={k for k,v in graph["nodes"].items() if v["present"]}
        self.assertEqual(graph["role_pair_count"],len(present)*(len(present)-1))

    def test_supplied_real_birth_is_separate_stem_and_full_crosses(self):
        graph=self.male_birth["full_health_role_strength_network"]
        self.assertTrue(graph["nodes"]["natal"]["present"])
        self.assertEqual(graph["nodes"]["natal"]["source_birth_ganzhi"],"乙丑")
        self.assertEqual(graph["nodes"]["natal"]["symbol"],"乙")
        self.assertEqual(graph["nodes"]["natal"]["symbol_kind"],"stem")
        self.assertIn("natal->illness",graph["directed_edges"])
        self.assertIn("natal->patient",graph["directed_edges"])
        self.assertIn("natal",graph["focus_against_disease_and_patient"])
        self.assertEqual(graph["nodes"]["qian"]["role_status"],
                         "sex_correspondence_candidate_unverified")
        self.assertEqual(graph["nodes"]["kun"]["role_status"],
                         "physical_palace_observation_only")

    def test_gender_reference_not_promoted_to_certainty(self):
        graph=self.female["full_health_role_strength_network"]
        self.assertEqual(graph["nodes"]["kun"]["role_status"],
                         "sex_correspondence_candidate_unverified")
        self.assertEqual(graph["nodes"]["qian"]["role_status"],
                         "physical_palace_observation_only")
        self.assertFalse(graph["nodes"]["kun"]["eligible_as_independent_verdict_vote"])

    def test_full_directed_graph_covers_each_role_to_disease_and_patient(self):
        for result in (self.no_birth,self.male_birth):
            graph=result["full_health_role_strength_network"]
            present={k for k,v in graph["nodes"].items() if v["present"]}
            for a in present:
                for b in present-{a}:
                    edge=graph["directed_edges"][a+"->"+b]
                    self.assertTrue(edge["exhaustive_physical_pair_covered"])
                    self.assertFalse(edge["verdict_vote_added"])
                    self.assertFalse(edge["additional_evidence_vote"])
                    self.assertTrue(edge["actor_fact_id"])
                    self.assertTrue(edge["target_fact_id"])
                    self.assertIn(edge["relation"],
                                  ("克","被克","生","被生","比和","同宫"))
                    self.assertIn(edge["ability_to_control"],
                                  ("能","不能","艰难","条件待核","不适用"))
            for key in ("doctor","medicine","patient","hour","qian","kun"):
                self.assertIn(key+"->illness",graph["directed_edges"])
            self.assertIn("qian->patient",graph["directed_edges"])
            self.assertIn("kun->patient",graph["directed_edges"])
            self.assertEqual(graph["added_independent_verdict_votes"],0)
            self.assertFalse(graph["clinical_prediction"])

    def test_every_deity_door_star_and_both_stem_planes_crossed(self):
        graph=self.male_birth["full_health_role_strength_network"]
        total=0
        for source, targets in graph["focus_against_disease_and_patient"].items():
            for target, edge in targets.items():
                a=graph["nodes"][source]["all_factors"]
                b=graph["nodes"][target]["all_factors"]
                count=len(a)*len(b)
                self.assertEqual(edge["factor_pair_count"],count)
                cross=edge["all_cross_layer_factor_pairs"]
                self.assertEqual(len(cross),count)
                kinds={(x["actor_kind"],x["target_kind"]) for x in cross}
                self.assertEqual({x["kind"] for x in a},
                                 {k for k,_ in kinds})
                self.assertEqual({x["kind"] for x in b},
                                 {k for _,k in kinds})
                self.assertTrue(all(x["full_physical_25x25_precomputed"] for x in cross))
                self.assertFalse(any(x["eligible_as_independent_verdict_vote"] for x in cross))
                self.assertEqual(len({(x["actor_fact_id"],x["target_fact_id"])
                                     for x in cross}),count)
                total+=count
        self.assertEqual(total,graph["focused_cross_layer_factor_pairs"])
        self.assertGreater(total,50)

    def test_colocation_kept_without_double_counting_physical_relation(self):
        graph=self.male_birth["full_health_role_strength_network"]
        edges=graph["directed_edges"]
        pairs={}
        for edge in edges.values():
            pairs.setdefault(edge["physical_pair_id"],[]).append(edge)
            if edge["same_physical_palace"]:
                self.assertEqual(edge["relation"],"同宫")
                self.assertEqual(edge["ability_to_control"],"不适用")
        self.assertEqual(graph["physical_palace_pair_count"],len(pairs))
        for grouping in pairs.values():
            self.assertEqual(sum(not x["same_physical_pair_already_seen"]
                                 for x in grouping),1)
        self.assertTrue(self.no_birth["no_scoring"])
        self.assertFalse(self.no_birth["medical_validity_claimed"])

    def test_preserve_old_health_order_and_new_network_review_only(self):
        for result in (self.no_birth,self.male_birth,self.female):
            titles=[s["title"] for s in result["sections"]]
            self.assertEqual(titles[:5],
                             ["先看伏吟反吟","天芮病宫","天心医生",
                              "乙奇医药","患者用神"])
            self.assertEqual(titles[-1],"时空及应期")
            self.assertLess(titles.index("年命、时干与乾坤全宫力量"),
                            titles.index("全部证据合断"))
            self.assertEqual(result["status"],"review_not_public")


if __name__=="__main__":
    unittest.main()
