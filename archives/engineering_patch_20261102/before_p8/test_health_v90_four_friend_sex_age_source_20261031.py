"""Current V11 friend month-stem-only regression; V9 four friend trigrams in Git history."""
import json
import unittest
from pathlib import Path
from src.wengua.casting_shenqi import layout_from_explicit_bureau
from src.wengua.health_dynamic_v21 import bind_patient
from src.wengua.domain_selected_energy_vnext import selected_health_sequence

ROOT=Path(__file__).resolve().parents[1]
P=json.loads((ROOT/"data/knowledge/phrase_library/health_v20/actor_profiles.json").read_text("utf8"))

class FriendV11(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.chart=layout_from_explicit_bureau(dun="yin",ju=2,hour_ganzhi="己卯")
  cls.cal={"year_ganzhi":"丙午","month_ganzhi":"戊戌",
           "day_ganzhi":"乙亥","hour_ganzhi":"己卯","month_branch":"戌"}

 def inquiry(self,sex=None,age=None):
  q={"intent":"severity","relationship":"friend","consultation_context":"direct_proxy"}
  if sex is not None:q["patient_sex"]=sex
  if age is not None:q["relative_age"]=age
  return q

 def test_friend_month_only_identical_across_old_four_demographics(self):
  self.assertEqual(P["profiles"][6]["id"],"friend")
  self.assertEqual(P["profiles"][6]["references"][0]["kind"],"casting_month_stem")
  fingerprints=set()
  for sex,age in ((None,None),("male","older"),("female","older"),
                  ("male","younger"),("female","younger")):
   with self.subTest(sex=sex,age=age):
    q=self.inquiry(sex,age)
    actor=bind_patient(self.chart,q,self.cal)
    self.assertEqual(actor["role_via"],"casting_month_stem")
    self.assertEqual(actor["stem"],"戊")
    self.assertIsNone(actor.get("resolved_relative_age"))
    self.assertFalse(actor.get("sibling_auxiliary_selected"))
    self.assertFalse(actor.get("sibling_auxiliary_candidate"))
    self.assertFalse(actor["extra_cells"])
    out=selected_health_sequence(chart=self.chart,calendar=self.cal,
                                 actor=actor,inquiry=q)
    self.assertNotIn("sibling",out["selected_roles"])
    self.assertNotIn("gender",out["selected_roles"])
    self.assertEqual(out["selected_roles"]["patient"]["palace"],
                     actor["main_cell"]["palace"])
    quant=out["candidate_five_grade_quantization"]
    self.assertNotIn("sibling",quant["roles"])
    self.assertEqual(quant["summary"]["unique_palace_count"],
                     len(quant["summary"]["unique_palace_score_details"]))
    fingerprints.add((out["selected_roles"]["patient"]["palace"],
                     quant["summary"]["score"]))
  self.assertEqual(len(fingerprints),1)

 def test_friend_no_demographics_required_but_family_age_must_not_override(self):
  a=bind_patient(self.chart,self.inquiry(),self.cal)
  self.assertEqual(a["stem"],"戊")
  b={"intent":"severity","relationship":"father",
     "consultation_context":"direct_proxy","relative_age":"older"}
  with self.assertRaises(ValueError):bind_patient(self.chart,b,self.cal)

if __name__=="__main__":unittest.main()
