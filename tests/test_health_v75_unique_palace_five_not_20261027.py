# Current V9/V11/V27 contract; exact pre-migration source is retained in archives/engineering_patch_20261102/original_tests/.
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
        self.assertEqual(q["raw_final_before_saturation"],q["post_void_known_sum"]+q["relationship_bonus_score"]-q["five_not_global_penalty"])
        self.assertEqual(q["score"],-5)
        self.assertEqual(c["roles"]["natal"]["palace"],c["roles"]["medicine"]["palace"])
        self.assertFalse(q["relationship_overlays_audit_only"])
        self.assertEqual(q["historical_overlay_total_if_stacked"],q["v76_role_score_sum_if_repeated"]+q["historical_role_stacked_bonus_score"]-2*q["role_count"])
        s=next(x["text"] for x in c["source_sections"] if x["id"]=="90_review")
        self.assertIn("五不遇时","\n".join(x["text"] for x in c["source_sections"]))
        self.assertIn("此病为极大凶",s)
        self.assertTrue(s.strip())
    def test_1920_elder_without_five_not(self):
        c=self.e;q=c["summary"]
        self.assertFalse(c["firstStage"])
        self.assertEqual(q["effective_palace_scores"],{"9":5,"7":-5,"3":0,"2":-3})
        self.assertEqual(q["unique_palace_count"],4)
        self.assertEqual(q["five_not_global_penalty"],0)
        self.assertEqual(q["raw_final_before_saturation"],q["post_void_known_sum"]+q["relationship_bonus_score"])
        self.assertEqual(q["score"],3)
        s=next(x["text"] for x in c["source_sections"] if x["id"]=="90_review")
        self.assertIn("此病为中吉",s)
        self.assertIn("无整盘伏吟反吟","\n".join(x["text"] for x in c["source_sections"]))
        self.assertNotIn("每个独立实宫均减两分",s)
        self.assertTrue(s.strip())
    def test_cultural_not_clinical(self):
        for c in (self.c,self.e):
            s=next(x["text"] for x in c["source_sections"] if x["id"]=="90_review")
            self.assertIn("以上仅作传统古籍象意参考",s)
            self.assertIn("不作现实病情判断",s)

if __name__=="__main__":
    unittest.main()
