"""Fixed user coworker illness: no elder Qian/Kun, no sex or natal.
Never synthesize a successful verdict or change clock to match an outcome.
"""
import unittest
from scripts.ios_vnext_manual_colleague_20261027 import produce

class ColleagueUserClock(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.case=produce()["cases"][0]

    def test_exact_input_and_real_month_peer_source(self):
        q=self.case
        self.assertEqual([q["four_pillars"][k] for k in
                         ("year","month","day","hour")],
                         ["己丑","戊辰","辛卯","丁酉"])
        self.assertEqual(q["instant"],"2009-04-16T17:00:00-04:00")
        self.assertEqual(q["relationship"],"同事")
        self.assertIsNone(q["patient_sex"])
        self.assertIsNone(q["patient_birth_ganzhi"])
        self.assertIn("patient",q["roles"])
        self.assertNotIn("gender",q["roles"])
        self.assertNotIn("natal",q["roles"])

    def test_dynamic_exactly_two_paragraphs_for_this_colleague(self):
        s=next(x["text"] for x in self.case["source_sections"]
               if x["id"]=="90_review")
        self.assertEqual(s.count("。"),2,s)
        self.assertEqual(len(s.split("\n\n")),2,s)
        for role in ("天芮病宫","天心医生","乙奇医药","患者用神",
                     "时干事体","值符"):
            self.assertIn(role,s)
        for unsupported in ("长辈乾宫","长辈坤宫","患者年命",
                            "乾宫辅助（男）","坤宫辅助（女）",
                            "1930","1920","+3分","+5分",
                            "完全失控","同宫去重"):
            self.assertNotIn(unsupported,s)
        self.assertIn("不能据此判断真实病情",s)
        self.assertTrue("综上所述，此病为" in s or "暂不强断" in s)

if __name__=="__main__":
    unittest.main()
