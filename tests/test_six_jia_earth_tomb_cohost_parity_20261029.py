"""Real-date source fact regression: 己亥? Qian-6 ground Yi at 墓/死 must not
be silently ignored because earth_tombs records BRANCH names, not stem labels.
Source-targeted Python/Swift parity. Never tune signed V8 score to case result.
"""
import unittest
from src.wengua.health_text_pipeline_vnext_review import auto_cast_health_review_text

class SixJiaEarthTomb(unittest.TestCase):
    def test_2014_jiawu_father_qian_earth_yi_tomb_source_bonus(self):
        r=auto_cast_health_review_text(
            iso="2014-12-06T05:00:00-05:00",
            timezone_name="America/New_York",
            inquiry={"intent":"severity","relationship":"father",
                     "consultation_context":"direct_proxy"})
        self.assertEqual(r["four_pillars"]["year"],"甲午")
        roles=r["full_health_role_strength_network"]["nodes"]
        self.assertEqual(roles["patient"]["palace"],1)
        self.assertEqual(roles["gender"]["palace"],6)
        quant=r["full_health_role_strength_network"]["candidate_five_grade_quantization"]
        summary=quant["summary"]
        cohost=summary["auspice_cohost_audit"]
        self.assertIn("6",cohost,"Actual Qian ground-Yi 墓 cohost should be eligible once")
        self.assertTrue(cohost["6"]["ground_restricted"])
        self.assertEqual(cohost["6"]["stem_family"],1)
        self.assertIn("乾六宫得地盘乙奇同宫扶助",r["reading_text"])
        self.assertNotIn("natal",quant["roles"])
        self.assertEqual(summary["score"],-5)

if __name__=="__main__":
    unittest.main()
