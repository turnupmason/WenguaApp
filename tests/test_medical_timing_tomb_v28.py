"""V2.8 fixed-template medical opportunity and actual tomb/striking regression."""
from __future__ import annotations
import json, unittest
from unittest.mock import patch
from src.wengua.health_severity_v28 import (
  yi_month_stage, related_special_facts, treatment_evidence, analyze_health_severity_v28)
from scripts.run_two_historical_health_v28 import evaluate
from scripts.run_two_historical_health_v27 import evaluate as past_evaluate
from src.wengua.semantic_lookup import nine_star_month_status
from src.wengua.health_severity_template import MONTH_ELEMENTS

class MedicalTimingV28Tests(unittest.TestCase):
    @staticmethod
    def fake_cell(p,stem):
        return {"palace":p,"door":"休门","deity":"六合","earth_stem":"癸",
                "heaven_stars":[{"star":"天心星","carried_stem":stem}]}
    def test_original_source_monthal_states_doctor_star_vs_yi_stem(self):
        self.assertEqual(nine_star_month_status("天心星",MONTH_ELEMENTS["戌"])["value"],"废")
        self.assertEqual(yi_month_stage("戌"),"囚")
        self.assertEqual(yi_month_stage("巳"),"休")
        self.assertEqual(yi_month_stage("寅"),"旺")
        self.assertEqual(yi_month_stage("酉"),"死")
        self.assertEqual(yi_month_stage("亥"),"相")
    def test_source_six_instruments_striking_in_exact_palace_only(self):
        for stem,p in (("戊",3),("己",2),("庚",8),("辛",9),("壬",4),("癸",4)):
            found=related_special_facts(None,[("patient",self.fake_cell(p,stem),None)])
            self.assertTrue(any(x["kind"]=="六仪击刑" and x["stem"]==stem for x in found))
            other=9 if p!=9 else 7
            unhit=related_special_facts(None,[("patient",self.fake_cell(other,stem),None)])
            self.assertFalse(any(x["kind"]=="六仪击刑" and x["stem"]==stem for x in unhit))
    def test_three_oddities_enter_tomb_source_palaces(self):
        for stem,p in (("乙",6),("丙",6),("丁",8)):
            found=related_special_facts(None,[("medicine",self.fake_cell(p,stem),[stem])])
            self.assertTrue(any(x["kind"]=="入墓地" for x in found))
        found=related_special_facts(None,[("medicine",self.fake_cell(7,"乙"),["乙"])])
        self.assertFalse(any(x["kind"]=="入墓地" for x in found))
    def test_both_independent_treatment_opportunity_triggers(self):
        from scripts.run_two_historical_health_v27 import evaluate as old
        oldcase=old()["predictions"][0]
        chart=oldcase["full_chart"]
        ill=chart["palaces"]["3"]
        doctor=chart["palaces"]["9"]
        med=chart["palaces"]["8"]
        event=doctor
        a=treatment_evidence(chart,"戌",doctor,med,ill,event,[])
        self.assertTrue(a["triggered"])
        self.assertTrue(any(m["trigger"]=="时干" and m["medicine_symbol"]=="天心" for m in a["matches"]))
        self.assertEqual(a["doc_month"],"废")
        self.assertEqual(a["yi_month"],"囚")
        self.assertIn("不能直接断治疗见效",a["timing"])
        b=treatment_evidence(chart,"戌",ill,med,ill,chart["palaces"]["7"],[])
        self.assertTrue(b["triggered"])
        self.assertTrue(any(m["trigger"]=="病宫" and m["medicine_symbol"]=="天心" for m in b["matches"]))
        c=treatment_evidence(chart,"戌",doctor,ill,ill,chart["palaces"]["7"],[])
        self.assertTrue(any(m["trigger"]=="病宫" and m["medicine_symbol"]=="乙奇" for m in c["matches"]))
        d=treatment_evidence(chart,"戌",doctor,med,ill,chart["palaces"]["7"],[])
        self.assertFalse(d["triggered"])
    def test_original_two_historical_seals_untouched_new_cases_show_medical_opportunity(self):
        old=past_evaluate()
        now=evaluate()
        self.assertEqual(old["selected_ids"],now["prior_sealed_event_ids"])
        self.assertFalse(now["prior_original_predictions_overwritten"])
        for i,case in enumerate(now["new_predictions"]):
            self.assertEqual(case["old_sealed_readout_sha256"],old["predictions"][i]["readout_sha256"])
            self.assertEqual(case["old_traditional_verdict"],case["new_traditional_verdict"])
            self.assertTrue(case["medical_timing"]["triggered"])
            self.assertIn("及时得到医治",case["new_readout"])
            self.assertIn("天心在",case["new_readout"])
            self.assertIn("月令",case["new_readout"])
            self.assertFalse(case["book_case_outcome_read"])
            self.assertEqual(case["user_review_status"],"pending")
            self.assertNotIn("门门迫",case["new_readout"])
            self.assertNotIn("与与",case["new_readout"])
            self.assertNotIn("GPT",case["new_readout"])
        self.assertIn("天心在离九宫，月令废",now["new_predictions"][0]["new_readout"])
        self.assertIn("乙奇在艮八宫，月令囚",now["new_predictions"][0]["new_readout"])
        self.assertIn("乙奇在坤二宫，月令休",now["new_predictions"][1]["new_readout"])
    def test_network_is_forbidden_and_identical_content_is_byte_stable(self):
        with patch("socket.socket",side_effect=AssertionError("Network forbidden")):
            a=evaluate();b=evaluate()
        self.assertEqual(
            [x["new_readout"].encode() for x in a["new_predictions"]],
            [x["new_readout"].encode() for x in b["new_predictions"]])
    def test_print_runtime_two_cases_for_manual_review(self):
        x=evaluate()
        print("\nV28_HISTORICAL_MEDICAL_OPPORTUNITY_START")
        for i,r in enumerate(x["new_predictions"],1):
            print(f"CASE_{i}_ID="+r["case_id"])
            print(f"CASE_{i}_SHA="+r["new_readout_sha256"])
            for j,s in enumerate(r["sections"],1):
                print(f"CASE_{i}_SECTION_{j:02d} "+s["title"]+"："+s["text"])
        print("V28_HISTORICAL_MEDICAL_OPPORTUNITY_END")

if __name__=="__main__":
    unittest.main()
