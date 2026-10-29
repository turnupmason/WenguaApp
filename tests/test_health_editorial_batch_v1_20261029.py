"""Actual 1080 topologies and 12 sealed review candidates, no fake completeness."""
import json
import unittest
from src.wengua.casting_shenqi import cycle60
from scripts.health_editorial_batch_v1 import (
    GRADE,first_complete_batch,topology1080,requests_for_batch,validate_candidate)

class EditorialBatchContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases=first_complete_batch()
    def test_all_1080_are_incomplete_casting_indices(self):
        x=topology1080()
        self.assertEqual(len(x),2*9*len(cycle60()))
        self.assertEqual(len({v["base_id"] for v in x}),1080)
        self.assertTrue(all(not v["complete_severity_reading"] for v in x))
        self.assertTrue(all("actual_month" in v["not_supplied"] for v in x))
    def test_twelve_actual_clock_cases_immutable(self):
        self.assertEqual(len(self.cases),12)
        self.assertEqual(len({z["case_fingerprint"] for z in self.cases}),12)
        self.assertTrue(all(z["freeze"]["grade"] in GRADE.values() for z in self.cases))
        self.assertTrue(all(not z["approved_for_app"] and z["status"].startswith("queued")
                            for z in self.cases))
        self.assertEqual([(x["case_facts"]["relationship_id"],x["freeze"]["score"])
                          for x in self.cases if x["case_facts"]["instant"][11:13]=="10"],
                          [("father",-5),("mother",-5),("grandfather",-5),
                           ("grandmother",-5),("older_sibling",0),("younger_sibling",0)])
        for z in self.cases:
            self.assertFalse(z["case_facts"]["nine_palaces"]["5"]["heaven_stars"])
            self.assertEqual(z["source_sections"][-1]["id"],"91_timing")
    def test_requests_and_grade_guard(self):
        req=requests_for_batch(self.cases,"gpt-test-model")
        self.assertEqual(len(req),12)
        self.assertTrue(all(r["url"]=="/v1/responses" and
                            r["body"]["text"]["format"]["strict"] for r in req))
        source=self.cases[0]
        candidate={"case_id":source["case_id"],
                   "case_fingerprint":source["case_fingerprint"],
                   "grade_anchor":source["freeze"]["grade"],
                   "summary":"此局传统病象不利之势较为突出，病宫与患者所处之宫虽然存在相互制约，但相应的门星神与格局条件并非完全相合。天心和乙奇都应按自身的力量与落宫核查，不能单凭吉名就认定医药奏效。伏吟之局多取进展迟滞的象意，遇假空还需结合真假空和相关刑墓门迫之限制。将这些证据合在一起，整体仍偏向不利，宜谨慎观察后续变化，以实际专业医疗意见为准。本次盘象不能作为医学诊断或临床预后，也不据此编造具体日期。",
                   "detailed_sections":[{"id":s["id"],"title":s["title"],
                         "text":s["text"]+"详细核读保持原事实。",
                         "evidence_ids":["section:"+s["id"]]} for s in source["source_sections"]],
                   "audit_flags":[]}
        review=validate_candidate(source,candidate)
        self.assertEqual(review["status"],"draft_needs_source_semantic_and_human_review")
        candidate["grade_anchor"]="极大吉"
        with self.assertRaisesRegex(ValueError,"grade drift"):
            validate_candidate(source,candidate)
        candidate["grade_anchor"]=source["freeze"]["grade"]
        candidate["detailed_sections"].pop()
        with self.assertRaisesRegex(ValueError,"missing long-form"):
            validate_candidate(source,candidate)
if __name__=="__main__":unittest.main()
