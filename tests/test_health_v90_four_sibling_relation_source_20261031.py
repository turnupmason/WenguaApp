"""V9.0 relationship-based sibling yongshen and real palace source; no age guessing.

User-approved: older/younger is known from 哥/姐/弟/妹 alone.
This establishes a V9 secondary trigram *policy*, not original-book validation
of the whole 5x5 matrix and not a biomedical prediction.
"""
import json
import unittest
from pathlib import Path
from src.wengua.casting_shenqi import layout_from_explicit_bureau
from src.wengua.health_dynamic_v21 import bind_patient
from src.wengua.domain_selected_energy_vnext import selected_health_sequence
from src.wengua.health_reading_template_vnext import template

ROOT=Path(__file__).resolve().parents[1]
PROFILES=json.loads((ROOT/"data/knowledge/phrase_library/health_v20/actor_profiles.json").read_text("utf8"))
ROLES={"older_brother":(3,"male"),"older_sister":(4,"female"),
       "younger_brother":(8,"male"),"younger_sister":(7,"female")}

class V90SiblingRoles(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.chart=layout_from_explicit_bureau(dun="yin",ju=2,hour_ganzhi="己卯")
        cls.calendar={"year_ganzhi":"丙午","month_ganzhi":"戊戌",
                      "day_ganzhi":"乙亥","hour_ganzhi":"己卯","month_branch":"戌"}

    def query(self,role,**opts):
        return {"intent":"severity","relationship":role,
                "consultation_context":"direct_proxy",**opts}

    def test_24_distinct_profiles_old_composites_retained_only_for_replay(self):
        self.assertEqual(len(PROFILES["profiles"]),24)
        ids={x["id"] for x in PROFILES["profiles"]}
        self.assertTrue(ROLES.keys() <= ids)
        self.assertNotIn("older_sibling",ids)
        self.assertNotIn("younger_sibling",ids)
        self.assertEqual({x["id"] for x in PROFILES["legacy_composite_profiles"]},
                         {"older_sibling","younger_sibling"})
        self.assertEqual(template()["version"],"V9.0_source_conditioned_sibling_20261031")

    def test_all_four_main_month_and_distinct_aux_without_extra_user_input(self):
        for role,(palace,sex) in ROLES.items():
            with self.subTest(role=role):
                query=self.query(role)
                actor=bind_patient(self.chart,query,self.calendar)
                self.assertEqual(actor["role_via"],"casting_month_stem")
                self.assertEqual(actor["stem"],"戊")
                self.assertEqual(actor["resolved_sex"],sex)
                self.assertEqual(actor["sibling_auxiliary_candidate"]["palace"],palace)
                self.assertTrue(actor["sibling_auxiliary_selected"])
                self.assertIn(palace,[x["palace"] for x in actor["extra_cells"]])
                self.assertNotIn(6,[x["palace"] for x in actor["extra_cells"]] if palace!=6 else [])
                self.assertNotIn(2,[x["palace"] for x in actor["extra_cells"]] if palace!=2 else [])
                self.assertFalse(actor["birth_cell"])
                self.assertEqual(actor["confidence"],"user_explicit_direction_verified_by_actual_chart")
                report=selected_health_sequence(chart=self.chart,calendar=self.calendar,
                    actor=actor,inquiry=query)
                aux=report["v90_sibling_auxiliary"]
                self.assertEqual(aux["palace"],palace)
                self.assertEqual(report["selected_roles"]["patient"]["palace"],actor["main_cell"]["palace"])
                self.assertEqual(report["selected_roles"]["sibling"]["palace"],palace)
                roles=report["candidate_five_grade_quantization"]["roles"]
                self.assertIn("sibling",roles)
                assert report["candidate_five_grade_quantization"]["summary"]["score"] is not None
                self.assertEqual(
                    len(report["candidate_five_grade_quantization"]["summary"]["unique_palace_score_details"]),
                    report["candidate_five_grade_quantization"]["summary"]["unique_palace_count"])

    def test_opposite_gender_rejected_and_no_fabricated_birth_rank(self):
        for role,(palace,sex) in ROLES.items():
            wrong="female" if sex=="male" else "male"
            with self.subTest(role=role):
                with self.assertRaises(ValueError):
                    bind_patient(self.chart,self.query(role,patient_sex=wrong),self.calendar)
                actor=bind_patient(self.chart,self.query(role),self.calendar)
                self.assertEqual(actor["resolved_sex"],sex)
                self.assertNotIn("natal",actor)
                self.assertIn(palace,[x["palace"] for x in actor["extra_cells"]])

    def test_v80_unaffected_self_father_mother_with_old_200_81(self):
        for role in ("self","father","mother","grandfather","grandmother"):
            req={"intent":"severity","relationship":role,
                 "consultation_context":"direct_self" if role=="self" else "direct_proxy"}
            actor=bind_patient(self.chart,req,self.calendar)
            self.assertFalse(actor.get("sibling_auxiliary_selected"))
            out=selected_health_sequence(chart=self.chart,calendar=self.calendar,
                                         actor=actor,inquiry=req)
            self.assertNotIn("sibling",out["selected_roles"])
            self.assertEqual(out["candidate_five_grade_quantization"]["summary"]["final_scoring_policy"],
                             "V8.0_SELECTED_SIGNIFIER_STRENGTH_ALL_INTERPALACE")

if __name__=="__main__":unittest.main()
