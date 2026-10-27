"""2026-10-26 V5 source-truth regression: real role control gates and no Tianqin carrier.
Never change frozen V3.9.1 or claim clinical diagnosis.
"""
import unittest
from src.wengua.health_text_pipeline_vnext_review import auto_cast_health_review_text
from src.wengua.user_domain_matrices_20261023 import (
    STAR_POWER,STEM_POWER,DOOR_POWER,CONTROL_NORMAL)
from src.wengua.factor_energy_25_rules import USER_STAR_25

CITY="America/New_York"
WIFE={"intent":"severity","relationship":"wife","consultation_context":"direct_proxy","patient_sex":"female"}

def review(instant, inquiry):
    return auto_cast_health_review_text(iso=instant,timezone_name=CITY,inquiry=inquiry)


class ExactRoleMatrixGate(unittest.TestCase):
    def test_source_25_cells_are_user_exact(self):
        self.assertEqual(STAR_POWER,USER_STAR_25)
        self.assertEqual(STEM_POWER["衰 / 病"],("大","极小","小","小","中等"))
        self.assertEqual(DOOR_POWER["旺"],("极大","中等","大","大","极大"))
        self.assertEqual(CONTROL_NORMAL["极小"],(
            "有效克制","有效克制","微弱克制","克制失效","反侮受损"))
        self.assertEqual(CONTROL_NORMAL["极大"],(
            "极限压制","绝对主克","强力主克","高效克制","有效克制"))

    def test_same_two_actual_wife_clocks_use_current_role_strength_and_control(self):
        for instant in ("2021-10-03T03:00:00-04:00",
                        "2023-04-24T21:00:00-04:00"):
            with self.subTest(instant=instant):
                r=review(instant,WIFE)
                graph=r["full_health_role_strength_network"]
                q=graph["candidate_five_grade_quantization"]
                gates=q["role_effectiveness_gates"]
                self.assertEqual(set(gates),set(q["roles"]))
                self.assertNotIn("天禽星",r["reading_text"])
                self.assertNotIn("天禽星长生",r["reading_text"])
                self.assertNotIn("。；",r["reading_text"])
                self.assertNotIn("坤宫辅助（女）",r["reading_text"])
                self.assertNotIn("gender",q["roles"])  # spouse is not an elder
                self.assertNotIn("乾宫辅助（男）",r["reading_text"])
                self.assertIn("用神力量为",r["reading_text"])
                self.assertIn("综上所述，此病为",r["reading_text"])
                for role,gate in gates.items():
                    if role=="illness":continue
                    self.assertIn(gate["actor_strength"],
                                  ("极小","小","中等","大","极大",None))
                    if gate["relation"]=="克":
                        edge=graph["directed_edges"][role+"->illness"]
                        self.assertEqual(gate["control_result"],
                                         edge["control_result"])
                        self.assertEqual(gate["control_ability"],edge["ability"])
                    else:
                        self.assertIsNone(gate["control_result"])
                selected={g["palace"] for g in gates.values() if g["score_eligible"]}
                self.assertEqual(q["summary"]["unique_palace_count"],len(selected))
                chief=gates["chief"]
                if chief["relation"]!="同宫" and (chief["void"]!="not_void" or chief["relation"]!="克"):
                    self.assertFalse(chief["score_eligible"])
                    self.assertTrue(chief["chief_zero_score"])

    def test_real_chief_under_illness_control_and_void_do_not_vote(self):
        cases=(("2022-07-19T11:00:00-04:00",
                 {"intent":"severity","relationship":"self","consultation_context":"direct_self"},
                 "被克"),
               ("2026-11-16T21:00:00-05:00",
                 {"intent":"severity","relationship":"father","consultation_context":"direct_proxy"},
                 "同宫"))
        for instant,inquiry,relation in cases:
            with self.subTest(instant=instant):
                r=review(instant,inquiry)
                q=r["full_health_role_strength_network"]["candidate_five_grade_quantization"]
                chief=q["role_effectiveness_gates"]["chief"]
                self.assertEqual(chief["relation"],relation)
                if relation=="同宫":
                    self.assertTrue(chief["score_eligible"])
                    self.assertFalse(chief["chief_zero_score"])
                    self.assertIn("值符大吉神与天芮病宫同宫",r["reading_text"])
                else:
                    self.assertFalse(chief["score_eligible"])
                    self.assertTrue(chief["chief_zero_score"])
                    self.assertNotIn("值符护持不参与最终合断。",r["reading_text"])
                if relation!="同宫" and chief["void"]!="not_void":
                    self.assertIn("因值符空亡，护持力明显减弱，尚存少许余气",r["reading_text"])

    def test_very_weak_illness_generates_two_roles_in_one_physical_palace(self):
        r=review("2021-07-03T01:00:00-04:00",
                 {"intent":"severity","relationship":"self",
                  "consultation_context":"direct_self"})
        q=r["full_health_role_strength_network"]["candidate_five_grade_quantization"]
        self.assertTrue(q["summary"]["weak_illness_drain_eligible"])
        illness=r["full_health_role_strength_network"]["nodes"]["illness"]
        self.assertEqual(illness["strength"],"极小")
        recipients=q["summary"]["drain_bonus_palaces"]
        self.assertTrue(recipients)
        self.assertEqual(len(recipients),len(set(recipients)))
        self.assertEqual(q["summary"]["weak_illness_drain_bonus_score"],3*len(recipients))
        self.assertIn("病星本已极弱，反去生助",r["reading_text"])
        base=q["summary"]["post_void_known_sum"]
        bonuses=q["summary"]["relationship_bonus_score"]
        self.assertEqual(q["summary"]["score"],max(-5,min(5,base+bonuses)))

    def test_v61_customer_prose_keeps_source_score_but_hides_internal_formulae(self):
        r=review("2024-03-25T05:00:00-04:00",WIFE)
        graph=r["full_health_role_strength_network"]
        audit=graph["candidate_five_grade_quantization"]["summary"]
        self.assertEqual(audit["control_bonus_score"],
                         sum(audit["control_bonus_points"].values()))
        self.assertEqual(audit["auspice_bonus_score"],
                         sum(x["points"] for x in audit["auspice_bonus_details"].values()))
        self.assertEqual(audit["relationship_bonus_score"],
                         audit["control_bonus_score"]+audit["auspice_bonus_score"]+
                         audit["weak_illness_drain_bonus_score"])
        public=r["reading_text"]
        for forbidden in ("克制力量表为","完全失控","按新规则加3分",
                          "不同实宫形成五行克病共","同一实宫仅计一次",
                          "长生分支待核（","每宫加3分","值符护持不参与最终合断",
                          "此处不再重复","不计独立克病加分"):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden,public)
        self.assertIn("天心医生宫克天芮病宫",public)
        self.assertIn("值符大吉神与天芮病宫同宫",public)
        self.assertIn("综上所述，此病为",public)
        self.assertEqual(public,"\n\n".join(
            x["title"]+"：\n"+x["text"] for x in r["sections"]))

    def test_control_bonus_only_distinct_real_palaces(self):
        r=review("2023-04-24T21:00:00-04:00",WIFE)
        q=r["full_health_role_strength_network"]["candidate_five_grade_quantization"]
        bonuses=q["summary"]["control_bonus_palaces"]
        self.assertEqual(q["summary"]["control_bonus_score"],
                         sum(q["summary"]["control_bonus_points"].values()))
        for palace,roles in bonuses.items():
            self.assertTrue(roles)
            for role in roles:
                self.assertEqual(q["role_effectiveness_gates"][role]["relation"],"克")
                self.assertEqual(str(q["role_effectiveness_gates"][role]["palace"]),palace)

    def test_v7_same_hour_male_friend_has_no_gender_auxiliary_or_natal(self):
        r=review("2010-02-02T07:00:00-05:00",
                 {"intent":"severity","relationship":"friend",
                  "consultation_context":"direct_proxy","patient_sex":"male"})
        q=r["full_health_role_strength_network"]["candidate_five_grade_quantization"]
        self.assertNotIn("gender",q["roles"])
        self.assertNotIn("natal",q["roles"])
        self.assertNotIn("乾宫辅助（男）",r["reading_text"])
        self.assertNotIn("坤宫辅助（女）",r["reading_text"])
        self.assertEqual(r["four_pillars"],
                         {"year":"己丑","month":"丁丑","day":"癸未","hour":"丙辰"})
        self.assertIn("患者用神",r["reading_text"])
        self.assertEqual(q["summary"]["relationship_bonus_score"],
                         q["summary"]["control_bonus_score"]+
                         q["summary"]["weak_illness_drain_bonus_score"]+
                         q["summary"]["auspice_bonus_score"])
        for points in q["summary"]["control_bonus_points"].values():
            self.assertIn(points,(1,3,5))
        for lucky in q["summary"]["auspice_bonus_details"].values():
            self.assertIn(lucky["points"],(1,2,3))

    def test_v7_elder_father_mother_get_exclusive_qian_kun(self):
        for relationship,sex,want,other in (
            ("father","male",6,2),("mother","female",2,6),
            ("older_relative","male",6,2),("older_relative","female",2,6)):
            with self.subTest(relationship=relationship,sex=sex):
                r=review("2010-02-02T07:00:00-05:00",{
                    "intent":"severity","relationship":relationship,
                    "consultation_context":"direct_proxy","patient_sex":sex})
                q=r["full_health_role_strength_network"]["candidate_five_grade_quantization"]
                self.assertEqual(q["roles"]["gender"]["palace"],want)
                text=r["reading_text"]
                self.assertIn("坤宫辅助（女）" if want==2 else "乾宫辅助（男）",text)
                self.assertNotIn("乾宫辅助（男）" if want==2 else "坤宫辅助（女）",text)

if __name__=="__main__":
    unittest.main()
