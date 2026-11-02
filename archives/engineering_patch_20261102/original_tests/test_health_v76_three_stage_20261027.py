import unittest
from scripts.ios_vnext_manual_colleague_natal_yi_20261027 import produce as colleague
from scripts.ios_vnext_manual_1920_female_20261027 import produce as elder
from src.wengua.health_five_level_quant_vnext import saturate
class V76ThreeStage(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.c=colleague()["cases"][0];cls.e=elder()["cases"][0]
 def audit(self,record):
  q=record["summary"];roles=q["effective_role_scores"]
  self.assertEqual(set(roles),set(record["roles"]))
  self.assertEqual(q["role_count"],len(roles))
  self.assertEqual(q["pending_roles"],[])
  self.assertEqual(q["post_void_known_sum"],sum(roles.values()))
  self.assertEqual(q["five_not_global_penalty"],2*len(roles) if record["firstStage"] else 0)
  self.assertEqual(q["raw_final_before_saturation"],sum(roles.values())+q["relationship_bonus_score"]-q["five_not_global_penalty"])
  self.assertEqual(q["score"],saturate(q["raw_final_before_saturation"]))
  self.assertEqual(q["final_scoring_policy"],"V7.6_ROLE_BASE_ENVIRONMENT_THEN_CONTROL")
 def test_colleague(self):
  self.audit(self.c)
  self.assertEqual(self.c["summary"]["role_count"],7)
  self.assertIn("各参与用神落宫分别扣两分",next(x["text"] for x in self.c["source_sections"] if x["id"]=="90_review"))
 def test_1920_same_yi_twice(self):
  self.audit(self.e)
  self.assertEqual(self.e["summary"]["role_count"],8)
  self.assertEqual(self.e["roles"]["medicine"]["palace"],self.e["roles"]["hour"]["palace"])
  grades=self.e["summary"]["effective_role_scores"]
  self.assertIn("medicine",grades);self.assertIn("hour",grades)
  self.assertEqual(grades["medicine"],grades["hour"])
