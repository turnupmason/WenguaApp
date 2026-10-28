"""2026-10-28 user-authorized Tianxian and centre-earth Kun host."""
import unittest
from pathlib import Path
from src.wengua.health_macro_facts_vnext import tianxian_hour, TIANXIAN_HOURS, tianxian_palace_bonus
from src.wengua.health_81_excel_catalog_vnext import for_real_palace
ROOT=Path(__file__).resolve().parents[1]
class UserTianxianKunContract(unittest.TestCase):
    def test_six_jia_by_day(self):
        expected={"甲":{"甲子","甲戌"},"己":{"甲子","甲戌"},
                  "乙":{"甲申"},"庚":{"甲申"},"丙":{"甲午"},"辛":{"甲午"},
                  "丁":{"甲辰"},"壬":{"甲辰"},"戊":{"甲寅"},"癸":{"甲寅"}}
        self.assertEqual(len(TIANXIAN_HOURS),10)
        for d,yes in expected.items():
            for h in ("甲子","甲戌","甲申","甲午","甲辰","甲寅"):
                self.assertEqual(tianxian_hour(d+"子",h),h in yes)
            self.assertFalse(tianxian_hour(d+"子","庚寅"))
    def test_aggregate_half_units_not_one_floor_each(self):
        for n in range(9):
            self.assertEqual(tianxian_palace_bonus(n,triggered=True,fuyin=False),2*n)
            self.assertEqual(tianxian_palace_bonus(n,triggered=True,fuyin=True),3*n//2)
            self.assertEqual(tianxian_palace_bonus(n,triggered=False,fuyin=True),0)
        self.assertEqual(tianxian_palace_bonus(3,triggered=True,fuyin=True),4)
        self.assertEqual(tianxian_palace_bonus(5,triggered=True,fuyin=True),7)
        with self.assertRaises(ValueError):
            tianxian_palace_bonus(9,triggered=True,fuyin=False)
    def test_kun_one_real_star_two_earth_pairs(self):
        c={"palace":2,"earth_stem":"戊","hosted_centre_earth_stem":"丁",
           "heaven_stars":[{"star":"天任星","carried_stem":"庚"}]}
        a=for_real_palace(c)
        self.assertEqual([(x["heaven"],x["earth"]) for x in a],[("庚","戊"),("庚","丁")])
        self.assertEqual(len({x["fact_id"] for x in a}),2)
        with self.assertRaisesRegex(ValueError,"Kun 2 lacks"):
            for_real_palace({k:v for k,v in c.items() if k!="hosted_centre_earth_stem"})
    def test_kun_two_stars_and_elsewhere_tianqin(self):
        st=[{"star":"天芮星","carried_stem":"戊"},{"star":"天禽星","carried_stem":"丁"}]
        k={"palace":2,"earth_stem":"戊","hosted_centre_earth_stem":"丁","heaven_stars":st}
        self.assertEqual([(x["heaven"],x["earth"]) for x in for_real_palace(k)],
                         [("戊","戊"),("丁","丁")])
        elsewhere=dict(k,palace=8,earth_stem="乙")
        self.assertEqual([(x["heaven"],x["earth"]) for x in for_real_palace(elsewhere)],
                         [("戊","乙"),("丁","乙")])
        self.assertEqual(for_real_palace(dict(k,palace=5)),[])
    def test_swift_python_ui_scope_matches(self):
        p=(ROOT/"src/wengua/health_quant_overlay_vnext.py").read_text()
        e=(ROOT/"ios/WenguaAppUI/WenguaNativeVNextEngine.swift").read_text()
        b=(ROOT/"ios/WenguaAppUI/WenguaHealthTemplateBridge.swift").read_text()
        u=(ROOT/"ios/WenguaAppUI/WenguaDesignPreviewApp.swift").read_text()
        n=(ROOT/"ios/WenguaAppUI/WenguaNativeCore.swift").read_text()
        self.assertIn('tianxian_palace_bonus(',p)
        self.assertIn('summary["unique_palace_count"]',p)
        self.assertIn('(selectedPalaces.count*(tianxianFuyin ? 3 : 4))/2',e)
        self.assertIn('wholeChartFuyin(chart)',e)
        self.assertIn('if p.id==2 && p.heavenStars.count==1',e)
        self.assertIn('if id==2 && palace.heavenStars.count==1',b)
        self.assertIn('p==2',u)
        self.assertIn('strikingPalaces',u)
        self.assertIn('QFive.stemMarks(palace,stem:stem,plane:plane)',u)
        self.assertIn('.background(QStyle.surface,in:RoundedRectangle(cornerRadius:4))',u)
        self.assertNotIn('Text("🐎")',u)
        self.assertIn('if p==2,let centreEarth=earth[5]',n)
if __name__=="__main__": unittest.main()
