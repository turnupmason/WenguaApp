"""Source fixed clocks, no resampling and no clinical claims."""
import unittest
from scripts.ios_vnext_manual_colleague_natal_yi_20261027 import produce as colleague
from scripts.ios_vnext_manual_1920_female_20261027 import produce as elder

class FinalUniquePalaceV75(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c=colleague()["cases"][0]
        cls.e=elder()["cases"][0]
    def test_colleague_five_not_each_real_palace(self):
        c=self.c;q=c["summary"]
        self.assertTrue(c["firstStage"])
        self.assertEqual(q["effective_palace_scores"],{"1":-5,"3":3,"8":-5,"7":5,"4":4})
        self.assertEqual(q["unique_palace_count"],5)
        self.assertEqual(q["post_void_known_sum"],2)
        self.assertEqual(q["five_not_global_penalty"],10)
        self.assertEqual(q["raw_final_before_saturation"],-8)
        self.assertEqual(q["score"],-5)
        self.assertEqual(c["roles"]["natal"]["palace"],c["roles"]["medicine"]["palace"])
        self.assertTrue(q["relationship_overlays_audit_only"])
        self.assertEqual(q["historical_overlay_total_if_stacked"],2+q["relationship_bonus_score"]-2)
        s=next(x["text"] for x in c["source_sections"] if x["id"]=="90_review")
        self.assertIn("五不遇时成立，参与合断的每个独立实宫均减两分",s)
        self.assertIn("此病为极大凶",s)
        self.assertEqual(len(s.split("\n\n")),2)
    def test_1920_elder_without_five_not(self):
        c=self.e;q=c["summary"]
        self.assertFalse(c["firstStage"])
        self.assertEqual(q["effective_palace_scores"],{"9":5,"7":-5,"3":0,"2":-3})
        self.assertEqual(q["unique_palace_count"],4)
        self.assertEqual(q["five_not_global_penalty"],0)
        self.assertEqual(q["raw_final_before_saturation"],-3)
        self.assertEqual(q["score"],-3)
        s=next(x["text"] for x in c["source_sections"] if x["id"]=="90_review")
        self.assertIn("此病为中凶",s)
        self.assertIn("无整盘伏吟反吟",s)
        self.assertNotIn("每个独立实宫均减两分",s)
        self.assertEqual(len(s.split("\n\n")),2)
    def test_cultural_not_clinical(self):
        for c in (self.c,self.e):
            s=next(x["text"] for x in c["source_sections"] if x["id"]=="90_review")
            self.assertIn("以上只作传统古籍象意参考",s)
            self.assertIn("不能据此判断真实病情",s)

if __name__=="__main__":
    unittest.main()
