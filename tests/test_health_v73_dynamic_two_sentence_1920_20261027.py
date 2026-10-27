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
            self.assertEqual(summary.count("。"),2,summary)
            self.assertEqual(summary.count("\n\n"),1,summary)
            first,second=summary.split("\n\n")
            self.assertTrue(first.endswith("。"))
            self.assertTrue(second.endswith("。"))
            self.assertIn("天芮病宫落",summary)
            self.assertIn("天心医生落",summary)
            self.assertIn("乙奇医药落",summary)
            self.assertIn("患者用神落",summary)
            self.assertIn("时干事体落",summary)
            self.assertIn("值符落",summary)
            self.assertIn("患者年命落",summary)
            self.assertIn("坤宫辅助落",summary)
            self.assertNotIn("乾宫辅助落",summary)
            self.assertIn("综上所述，此病为",summary)
            self.assertIn("不能据此判断真实病情",summary)
            for confidential in ("+3分","+5分","完全失控","同宫去重"):
                self.assertNotIn(confidential,summary)
            passages.append(summary)
        self.assertNotEqual(passages[0],passages[1])
        self.assertIn("患者用神落震三宫，宫象中平且逢真空",passages[1])
        self.assertIn("乙奇医药与天芮病宫同在离九宫",passages[1])
        self.assertIn("虽逢空仍有余气克制病宫",passages[0])

    def test_1920_natal_is_conditional_after_lichun(self):
        fixture=new_1920()["cases"][0]
        self.assertEqual(fixture["patient_birth_ganzhi"],"庚申")
        self.assertEqual(fixture["patient_sex"],"female")
        self.assertEqual(fixture["relationship"],"其他长辈")
        self.assertEqual(fixture["roles"]["gender"]["palace"],2)

if __name__=="__main__":
    unittest.main()
