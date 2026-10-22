"""No duplicate doctor/medicine monthly state on two real source-family charts."""
import unittest
from unittest.mock import patch
from scripts.run_two_historical_health_v29 import evaluate
from src.wengua.health_severity_v28 import treatment_evidence,related_special_facts
class V29CleanMedicalMonthlyProse(unittest.TestCase):
    def test_real_two_historical_cases_keep_old_seals_and_verdicts(self):
        x=evaluate()
        self.assertEqual(len(x["samples"]),2)
        self.assertTrue(x["original_v27_and_v28_readings_preserved"])
        for p in x["samples"]:
            self.assertEqual(p["verdict"],"病凶")
            self.assertTrue(p["medical_timing"]["triggered"])
            self.assertNotIn("门门迫",p["readout"])
            self.assertIn("及时得到医治的机会",p["readout"])
            self.assertFalse(p["other_original_book_outcome_used"])
            self.assertEqual(len(p["sha256"]),64)
            med=next(s["text"] for s in p["sections"] if s["id"]=="07_medicine")
            self.assertLessEqual(med.count("天心月废"),1)
            self.assertLessEqual(med.count("天心月囚"),1)
            self.assertLessEqual(med.count("乙奇月囚"),1)
            self.assertLessEqual(med.count("乙奇月休"),1)
        self.assertIn("天心在离九宫，月令废",x["samples"][0]["readout"])
        self.assertIn("乙奇在坤二宫，月令休",x["samples"][1]["readout"])
    def test_no_gpt_no_network_idempotence(self):
        with patch("socket.socket",side_effect=AssertionError("network forbidden")):
            a=evaluate();b=evaluate()
        self.assertEqual([x["readout"].encode() for x in a["samples"]],
                         [x["readout"].encode() for x in b["samples"]])
    def test_actual_original_source_conditions_present(self):
        a,b=evaluate()["samples"]
        self.assertTrue(any(s["kind"]=="六仪击刑" for s in b["medical_timing"]["role_factors"]["illness"]) if "role_factors" in b["medical_timing"] else True)
        self.assertIn("离九宫天盘辛六仪击刑",b["readout"])
        self.assertNotIn("有病一定能治愈",a["readout"])
    def test_print_verbatim_timing_and_monthly_templates(self):
        for i,x in enumerate(evaluate()["samples"],1):
            print("V29_MEDICAL_CASE_%d_BEGIN"%i)
            for s in x["sections"]:
                if s["id"] in ("07_medicine","08_hour","09_hazards","10_pace","11_final"):
                    print(s["title"]+"："+s["text"])
            print("V29_CASE_SHA="+x["sha256"])
            print("V29_MEDICAL_CASE_%d_END"%i)
if __name__=="__main__": unittest.main()
