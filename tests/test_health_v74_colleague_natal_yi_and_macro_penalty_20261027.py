# Current V9/V11/V27 contract; exact pre-migration source is retained in archives/engineering_patch_20261102/original_tests/.
"""User fixed chart: natal 乙 not a fabricated two-character birth year."""
import unittest
from scripts.ios_vnext_manual_colleague_natal_yi_20261027 import produce

class FixedColleagueNatalYi(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.one=produce()["cases"][0]

    def test_fixed_chart_and_natal_palace(self):
        c=self.one
        self.assertEqual([c["four_pillars"][key] for key in
                          ("year","month","day","hour")],
                         ["己丑","戊辰","辛卯","丁酉"])
        self.assertEqual(c["patient_birth_stem"],"乙")
        self.assertIsNone(c["patient_birth_ganzhi"])
        self.assertIsNone(c["patient_sex"])
        self.assertNotIn("gender",c["roles"])
        self.assertIn("natal",c["roles"])
        self.assertEqual(c["roles"]["natal"]["palace"],
                         c["roles"]["medicine"]["palace"])
        self.assertEqual(c["summary"]["unique_palace_count"],5)

    def test_all_adverse_and_good_actual_palaces_counted_once(self):
        q=self.one["summary"]
        actual=q["effective_palace_scores"]
        self.assertEqual({int(k) for k in actual},{1,3,4,7,8})
        self.assertEqual(actual["1"],-5)
        self.assertEqual(actual["8"],-5)
        self.assertEqual(q["post_void_known_sum"],sum(actual.values()))
        self.assertEqual(q["five_not_global_penalty"],10)
        self.assertEqual(q["five_not_penalty_per_palace"],2)
        self.assertEqual(q["five_not_penalized_unique_palace_count"],5)
        self.assertFalse(q["relationship_overlays_audit_only"])
        self.assertEqual(q["raw_final_before_saturation"],sum(actual.values())+q["relationship_bonus_score"]-10)
        self.assertEqual(q["raw_final_before_saturation"],sum(actual.values())+q["relationship_bonus_score"]-q["five_not_global_penalty"])
        self.assertEqual(q["score"],-5)
        self.assertEqual(q["score"],max(-5,min(5,q["raw_final_before_saturation"])))

    def test_two_paragraphs_include_both_global_conditions(self):
        c=self.one
        verdict=next(s["text"] for s in c["source_sections"] if s["id"]=="90_review")
        whole="\n".join(s["title"]+"："+s["text"] for s in c["source_sections"])
        self.assertTrue(verdict.strip())
        self.assertIn("五不遇时",whole)
        self.assertIn("无整盘伏吟反吟",whole)
        self.assertIn("年命",whole)
        self.assertNotIn("长辈坤宫",whole)
        self.assertNotIn("长辈乾宫",whole)
        self.assertIn("不作现实病情判断",verdict)
        self.assertEqual(c["summary"]["five_not_global_penalty"],2*c["summary"]["unique_palace_count"])

if __name__=="__main__":
    unittest.main()
