"""V7.3 conditional summary, original clocks, no result-based resampling."""
import unittest
from scripts.ios_vnext_manual_birth_20261027 import produce as old_1930
from scripts.ios_vnext_manual_1920_female_20261027 import produce as new_1920

class TestTwoSentenceDynamicSummary(unittest.TestCase):
    def test_all_roles_dynamic_for_both_user_supplied_clocks(self):
        passages=[]
        for fn,expected in (
            (old_1930,("己丑","丁丑","癸未","丙辰")),
            (new_1920,("己丑","庚午","丁亥","乙巳"))):
            fixture=fn()["cases"][0]
            self.assertEqual(tuple(fixture["four_pillars"].values()),expected)
            summary=next(s["text"] for s in fixture["source_sections"]
                         if s["id"]=="90_review")
            # Historical two-sentence review is superseded by current four
            # condition-aware V8 paragraphs. Keep *facts* and case identity;
            # do not require obsolete customer wording or historical verdict.
            chunks=summary.split("\n\n")
            self.assertEqual(len(chunks),4,summary)
            self.assertEqual(summary.count("。"),4,summary)
            self.assertTrue(all(part.endswith("。") for part in chunks))
            self.assertIn("病星天芮在",chunks[0])
            self.assertIn("天心",chunks[1])
            self.assertIn("乙奇",chunks[1])
            self.assertIn("患者",chunks[0])
            self.assertIn("时干事体",chunks[2])
            self.assertIn("年命",chunks[2])
            self.assertIn("值符",chunks[2])
            self.assertIn("综上所述，此病为",chunks[3])
            self.assertIn("不作现实病情判断",chunks[3])
            for confidential in ("+3分","+5分","完全失控","同宫去重"):
                self.assertNotIn(confidential,summary)
            passages.append(summary)
        self.assertNotEqual(passages[0],passages[1])
        self.assertIn("患者己在震三宫",passages[1])
        self.assertIn("乙奇势",passages[1])
        self.assertIn("患者",passages[0])

    def test_1920_natal_is_conditional_after_lichun(self):
        fixture=new_1920()["cases"][0]
        self.assertEqual(fixture["patient_birth_ganzhi"],"庚申")
        self.assertEqual(fixture["patient_sex"],"female")
        self.assertEqual(fixture["relationship"],"其他长辈")
        self.assertEqual(fixture["roles"]["gender"]["palace"],2)

if __name__=="__main__":
    unittest.main()
