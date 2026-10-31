"""V9 selected friend sex x relative_age creates four distinct PEER trigrams."""
import json
import unittest
from pathlib import Path
from src.wengua.casting_shenqi import layout_from_explicit_bureau
from src.wengua.health_dynamic_v21 import bind_patient
from src.wengua.domain_selected_energy_vnext import selected_health_sequence

ROOT=Path(__file__).resolve().parents[1]
P=json.loads((ROOT/"data/knowledge/phrase_library/health_v20/actor_profiles.json").read_text("utf8"))

class FriendV90(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.chart=layout_from_explicit_bureau(dun="yin",ju=2,hour_ganzhi="己卯")
  cls.cal={"year_ganzhi":"丙午","month_ganzhi":"戊戌",
           "day_ganzhi":"乙亥","hour_ganzhi":"己卯","month_branch":"戌"}

 def inquiry(self,sex=None,age=None):
  x={"intent":"severity","relationship":"friend","consultation_context":"direct_proxy"}
  if sex is not None:x["patient_sex"]=sex
  if age is not None:x["relative_age"]=age
  return x

 def test_friend_all_four_month_real_auxiliary(self):
  expected={("male","older"):3,("female","older"):4,
            ("male","younger"):8,("female","younger"):7}
  self.assertEqual(P["profiles"][6]["id"],"friend")
  self.assertEqual(P["profiles"][6]["references"][0]["kind"],"casting_month_stem")
  for (sex,age),palace in expected.items():
   with self.subTest(sex=sex,age=age):
    actor=bind_patient(self.chart,self.inquiry(sex,age),self.cal)
    self.assertEqual(actor["role_via"],"casting_month_stem")
    self.assertEqual(actor["stem"],"戊")
    self.assertEqual(actor["resolved_sex"],sex)
    self.assertEqual(actor["resolved_relative_age"],age)
    self.assertEqual(actor["sibling_auxiliary_candidate"]["palace"],palace)
    self.assertTrue(actor["sibling_auxiliary_selected"])
    self.assertEqual([x["palace"] for x in actor["extra_cells"]],[palace])
    self.assertEqual(actor["confidence"],"user_explicit_direction_verified_by_actual_chart")
    out=selected_health_sequence(chart=self.chart,calendar=self.cal,actor=actor,
                                 inquiry=self.inquiry(sex,age))
    self.assertEqual(out["selected_roles"]["sibling"]["palace"],palace)
    self.assertEqual(out["selected_roles"]["patient"]["palace"],actor["main_cell"]["palace"])
    q=out["candidate_five_grade_quantization"]
    self.assertIn("sibling",q["roles"])
    self.assertEqual(q["summary"]["unique_palace_count"],
                     len(q["summary"]["unique_palace_score_details"]))
    self.assertEqual(q["summary"]["final_scoring_policy"],
                     "V9.0_SOURCE_CONDITIONED_SIBLING_AUXILIARY")

 def test_both_conditions_required_and_unrelated_relation_rejects_age(self):
  for q in (self.inquiry(),self.inquiry("male"),self.inquiry(age="older"),
            self.inquiry("unknown","older"),self.inquiry("male","same")):
   with self.subTest(q=q),self.assertRaises(ValueError):
    bind_patient(self.chart,q,self.cal)
  b={"intent":"severity","relationship":"father",
     "consultation_context":"direct_proxy","relative_age":"older"}
  with self.assertRaises(ValueError):bind_patient(self.chart,b,self.cal)

if __name__=="__main__":unittest.main()
