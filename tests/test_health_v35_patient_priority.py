"""V3.5 12 real source cases: patient-first decision, double suppression, doctor same-palace even weak, natal Jia."""
from __future__ import annotations
import hashlib,unittest
from scripts.replay_all_historical_health_v35 import evaluate,PARENT,PARENT_SHA
from src.wengua.health_severity_v35 import patient_first_decision
class HealthV35Priority(unittest.TestCase):
 def test_parent_and_all_twelve_no_feedback(self):
    self.assertEqual(hashlib.sha256(PARENT.read_bytes()).hexdigest(),PARENT_SHA)
    r=evaluate()
    self.assertEqual(len(r["samples"]),12)
    self.assertEqual(r["counts"]["rendered"],12)
    self.assertEqual(r["counts"]["blocked"],0)
    for x in r["samples"]:
        self.assertFalse(x["author_answer_used"])
        self.assertFalse(x["later_feedback_used"])
        self.assertEqual(hashlib.sha256(x["reading"].encode()).hexdigest(),x["sha256"])
        self.assertEqual(len(x["ordered_pairs"]),42)
        self.assertEqual(len(x["composites"]),17)
        self.assertEqual(x["traditional_severity"],x["patient_priority"]["verdict"])
 def test_double_suppression_stronger_than_lone_tianrui_weakness(self):
    # Fully explicit mechanical precedence independent of known case ending.
    chart={"hour_ganzhi":"丙申"}
    ill={"palace":3}
    person={"palace":6}
    from unittest.mock import patch
    with patch("src.wengua.health_severity_v35._yes_void",return_value=False):
        result=patient_first_decision(chart=chart,person=person,ill=ill,
          prior={"verdict":"病凶","adverse":["病宫临死门","月令天芮旺"],"favorable":[]},
          evidence={"actual_tomb_punishment_v28":[]})
    self.assertTrue(result["double_suppression"])
    self.assertEqual(result["verdict"],"病吉")
    self.assertIn("双重制病",result["priority"])
 def test_patient_void_limits_control_but_does_not_erase_double_facts(self):
    from unittest.mock import patch
    with patch("src.wengua.health_severity_v35._yes_void",return_value=True):
        result=patient_first_decision(chart={},person={"palace":6},ill={"palace":3},
          prior={"verdict":"病凶","adverse":[]},evidence={})
    self.assertTrue(result["double_suppression"])
    self.assertTrue(result["patient_void"])
    self.assertEqual(result["verdict"],"病凶")
 def test_spouse_animal_son_in_law_readings_no_malformed_role(self):
    v={x["family_id"]:x for x in evaluate()["samples"]}
    wife=v["shenqi.health.19971227.spouse_travel_for_treatment"]
    self.assertIn("日干五合戊",wife["reading"])
    self.assertNotIn("五合戊乙",wife["reading"])
    self.assertIn("妻子以乙奇为主",wife["reading"])
    for f in ("kaiwu.health.19980616.hen_illness","kaiwu.health.19980621.rooster_illness"):
        self.assertIn("以时干",v[f]["sections"][0]["text"])
        self.assertNotIn("晚辈候选",v[f]["sections"][0]["text"])
    son=v["kaiwu.final.recovery"]
    self.assertIn("女婿",son["reading"])
    self.assertIn("甲辰",son["sections"][0]["text"])
    self.assertIsNotNone(son["supplied_natal_reference_palace"])
 def test_medical_opportunity_survives_doctor_weakness(self):
    cases=evaluate()["samples"]
    match=[x for x in cases if x["medicine_copalace"]["independent_opportunities"] and
                            x["medicine_copalace"]["weaknesses_kept"]]
    self.assertTrue(match)
    for x in match:
        final=next(p["text"] for p in x["sections"] if p["id"]=="11_final")
        self.assertIn("不取消这一同宫象",final)
 def test_old_v34_parent_book_predictions_not_mutated(self):
    import json
    old=json.loads((PARENT.parent.parent.parent/"data/evaluation/health_v34/all_12_original_source_conditions_V34_SEALED.json").read_text("utf8"))
    self.assertEqual(old["counts"],{"rendered":12,"blocked":0})

if __name__=="__main__":unittest.main()
