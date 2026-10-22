"""V3.1 exact patient/hour directed illness test and preserved historical seals."""
import unittest
from unittest.mock import patch
from scripts.run_two_historical_health_v31 import evaluate
from src.wengua.health_severity_v31 import patient_vs_disease_hour_relation
from src.wengua.casting_shenqi import layout_from_explicit_bureau
from src.wengua.health_dynamic_v21 import bind_patient

class V31ExplicitHourDiseasePatient(unittest.TestCase):
 def test_both_historical_patient_vs_hour_disease_directions(self):
    a,b=evaluate()["samples"]
    self.assertEqual(a["hour_patient_evidence"]["relation"],"受克")
    self.assertIn("患者宫受制",a["hour_patient_evidence"]["text"])
    self.assertIn("偏凶",a["sections"][6 if len(a["sections"])==10 else 7]["text"])
    self.assertNotIn("事体宫克患者宫，偏吉",a["readout"])
    self.assertEqual(b["hour_patient_evidence"]["relation"],"比和")
    self.assertIn("同气相持",b["readout"])
    self.assertNotIn("时干宫与患者宫比和，未单定吉凶",b["readout"])
 def test_real_source_outcomes_not_used_and_old_failure_seal_retained(self):
    report=evaluate()
    self.assertTrue(report["prior_v27_v28_v29_v30_seals_preserved"])
    self.assertTrue(report["original_book_author_answers_not_used"])
    for x in report["samples"]:
        self.assertEqual(len(x["v30_original_sha256"]),64)
        self.assertNotEqual(x["sha256"],x["v30_original_sha256"])
        self.assertFalse("GPT" in x["readout"])
        self.assertNotIn("必死",x["readout"])
        self.assertEqual(x["traditional_verdict"],"病凶")
 def test_end_user_text_generated_offline_deterministically(self):
    with patch("socket.socket",side_effect=AssertionError("Network used")):
        a=evaluate();b=evaluate()
    self.assertEqual([x["readout"].encode() for x in a["samples"]],
                     [x["readout"].encode() for x in b["samples"]])
 def test_print_all_changed_hour_prose(self):
    for x in evaluate()["samples"]:
        print("V31_HOUR_"+x["case_id"]+"="+next(s["text"] for s in x["sections"] if s["id"]=="08_hour"))
        print("V31_SHA_"+x["case_id"]+"="+x["sha256"])
if __name__=="__main__":unittest.main()
