"""V3.6 actual hour-stem horse, source chapter value gate conditions, clean main/natal separation."""
from __future__ import annotations
import hashlib,unittest
from scripts.replay_all_historical_health_v36 import evaluate,PARENT,PARENT_SHA
from src.wengua.health_severity_v36 import _rechecked_composites
from src.wengua.casting_shenqi import layout_from_explicit_bureau
from src.wengua.health_severity_v34 import HORSE

class HealthV36(unittest.TestCase):
 def test_parent_and_12_real_hour_corpus(self):
    self.assertEqual(hashlib.sha256(PARENT.read_bytes()).hexdigest(),PARENT_SHA)
    q=evaluate()
    self.assertEqual(q["counts"],{"rendered":12,"blocked":0})
    self.assertEqual(len(q["samples"]),12)
    for z in q["samples"]:
       self.assertFalse(z["author_answer_used"] or z["later_feedback_used"])
       self.assertEqual(len(z["corrected_17_composite_predicates"]),17)
       self.assertEqual(len(z["ordered_pairs"]),42)
       self.assertEqual(hashlib.sha256(z["reading"].encode()).hexdigest(),z["sha256"])
 def test_horse_from_actual_hour_not_day(self):
    for v in evaluate()["samples"]:
       h=v["source_hour"][1]
       horse=next(z for z in v["corrected_17_composite_predicates"] if z["id"]=="health_composite_12")["evidence"][0]
       self.assertEqual(horse["hour_branch"],h)
       self.assertEqual(horse["horse_branch"],HORSE[h])
       self.assertIn("依据占时"+h+"支，驿马在"+HORSE[h],v["reading"])
 def test_door_matching_attested_three_wonders_and_jade(self):
    for v in evaluate()["samples"]:
       q={z["id"]:z for z in v["corrected_17_composite_predicates"]}
       for x in ("health_composite_07","health_composite_08"):
          self.assertIn(q[x]["state"],("triggered","not_triggered"))
          self.assertNotIn("unknown",q[x]["state"])
          if q[x]["state"]=="triggered":
              self.assertTrue(q[x]["evidence"])
       self.assertEqual(q["health_composite_07"]["source"],"kaiwu_ch04_section_三奇得使")
 def test_main_role_and_natal_year_not_confused(self):
    q={s["family_id"]:s for s in evaluate()["samples"]}
    brother=q["kaiwu.health.19950219.brother_paralysis"]
    self.assertIn("月干戊落离九宫为主用神",brother["sections"][0]["text"])
    self.assertIn("出生年命癸丑另参坤二宫",brother["sections"][0]["text"])
    self.assertNotIn("年命癸丑落离九宫",brother["sections"][0]["text"])
    daughter=q["kaiwu.final.recovery"]
    self.assertIn("出生年命甲辰",daughter["sections"][0]["text"])
    self.assertIsNotNone(daughter["supplied_natal_reference_palace"])
 def test_no_leaking_unapproved_methods_into_instant_medical_assertion(self):
    for v in evaluate()["samples"]:
       final=v["sections"][-1]["text"]
       self.assertIn("依据古籍",final)
       self.assertNotIn("必死",final)
       self.assertNotIn("确诊癌症",final)
       self.assertNotIn("停止治疗",final)

if __name__=="__main__":unittest.main()
