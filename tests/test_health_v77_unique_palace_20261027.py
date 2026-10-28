"""V7.7: same real palace and same stem NEVER scored twice."""
import unittest
from scripts.ios_vnext_manual_colleague_natal_yi_20261027 import produce as coworker
from scripts.ios_vnext_manual_1920_female_20261027 import produce as old_woman
from src.wengua.health_five_level_quant_vnext import saturate

class StrictPhysicalPalaceOnce(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.colleague=coworker()["cases"][0]
        cls.elder=old_woman()["cases"][0]
        # Retain this historical version test unmodified in semantics; it is
        # not the acceptance oracle for later current scoring versions.
        if cls.colleague["summary"]["final_scoring_policy"]!="V7.7_UNIQUE_PHYSICAL_PALACE_AND_SIGNIFIER_THREE_STAGE":
            raise unittest.SkipTest("Historical V7.7_UNIQUE_PHYSICAL_PALACE_AND_SIGNIFIER_THREE_STAGE assertions; run V7.9 general tests for active engine")

    def audit(self,record,expected_palaces):
        q=record["summary"]
        physical=q["unique_palace_score_details"]
        self.assertEqual(len(physical),expected_palaces)
        self.assertEqual(q["unique_palace_count"],expected_palaces)
        self.assertEqual(q["post_void_known_sum"],
            sum(p["score"] for p in physical.values()))
        self.assertFalse(q["pending_palaces"])
        self.assertTrue(q["repeated_signifier_merged"])
        self.assertTrue(q["auspice_merged_into_physical_palace"])
        self.assertEqual(q["auspice_applied_extra_score"],0)
        self.assertEqual(q["relationship_bonus_score"],
            q["control_bonus_score"]+q["weak_illness_drain_bonus_score"])
        self.assertEqual(q["five_not_global_penalty"],
            2*expected_palaces if record["firstStage"] else 0)
        self.assertEqual(q["raw_final_before_saturation"],
            q["post_void_known_sum"]+q["relationship_bonus_score"]-
            q["five_not_global_penalty"])
        self.assertEqual(q["score"],saturate(q["raw_final_before_saturation"]))
        self.assertEqual(q["final_scoring_policy"],
            "V7.7_UNIQUE_PHYSICAL_PALACE_AND_SIGNIFIER_THREE_STAGE")
        for role,item in record["roles"].items():
            pid=str(item["palace"])
            self.assertEqual(item["score"],physical[pid]["score"],role)
        conclusion=next(x["text"] for x in record["source_sections"]
                        if x["id"]=="90_review")
        self.assertEqual(len(conclusion.split("\n\n")),2)
        self.assertIn("不能据此判断真实病情",conclusion)

    def test_colleague_yearstem_乙_not_double(self):
        c=self.colleague
        self.audit(c,5)
        q=c["summary"]
        self.assertTrue(c["firstStage"])
        self.assertEqual(c["roles"]["doctor"]["palace"],
                         c["roles"]["medicine"]["palace"])
        self.assertEqual(c["roles"]["medicine"]["palace"],
                         c["roles"]["natal"]["palace"])
        self.assertEqual(set(q["unique_palace_score_details"]["3"]["unique_stem_scores"]),{"乙"})
        self.assertEqual(q["five_not_global_penalty"],10)
        self.assertIn("各实际参与实宫均减两分",
            next(x["text"] for x in c["source_sections"] if x["id"]=="90_review"))

    def test_elder_乙_hour_medicine_one_stem(self):
        c=self.elder
        self.audit(c,4)
        q=c["summary"]
        self.assertFalse(c["firstStage"])
        self.assertEqual(c["roles"]["medicine"]["palace"],9)
        self.assertEqual(c["roles"]["hour"]["palace"],9)
        self.assertEqual(c["roles"]["natal"]["palace"],9)
        self.assertEqual(set(q["unique_palace_score_details"]["9"]["unique_stem_scores"]),{"乙","庚"})
        self.assertEqual(c["roles"]["chief"]["palace"],
                         c["roles"]["gender"]["palace"])
        self.assertEqual(c["roles"]["medicine"]["score"],
                         c["roles"]["hour"]["score"])
        self.assertEqual(q["five_not_global_penalty"],0)

if __name__=="__main__":
    unittest.main()
