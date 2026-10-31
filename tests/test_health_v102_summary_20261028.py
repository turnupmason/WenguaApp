"""V11 descriptive regression on original V10.2 clocks; frozen V8 scores."""
import unittest
from scripts import ios_vnext_three_random_20261026 as generator
from src.wengua.health_reading_template_vnext import template

class ConciseV102(unittest.TestCase):
    def test_five_unchanged_real_clocks(self):
        original=generator.RELATIONS
        try:
            generator.RELATIONS=(("father","父亲","direct_proxy","male"),
                                 ("self","本人","direct_self",None),
                                 ("self","本人","direct_self",None),
                                 ("daughter","女儿","direct_proxy","female"),
                                 ("friend","朋友","direct_proxy",None))
            batch=generator.produce(seed=202610282259,count=5)
        finally:generator.RELATIONS=original
        # Frozen pre-six-Jia historical snapshot: [5,0,5,-1,-5].
        # Approved 2026-10-29 source-pillar Jia role correction moves some
        # selected palaces; keep old result in source audit, not as new expected.
        self.assertEqual([x["summary"]["score"] for x in batch["cases"]],[5,-5,0,5,-3])
        for c in batch["cases"]:
            s=next(x["text"] for x in c["source_sections"] if x["id"]=="90_review")
            self.assertIn("天芮在",s)
            self.assertIn("患者",s)
            self.assertIn("天心势",s)
            self.assertIn("乙奇势",s)
            self.assertLess(len(s),950)
            for banned in ("矩阵","加分","每宫","总分","五不遇时","伏吟主慢","反吟主快"):
                self.assertNotIn(banned,s)
            self.assertIn("综上所述，此病为",s)
    def test_wife_one_yi_source_strength_once(self):
        c=generator.produce(seed=202610282003,count=1,wife_only=True)["cases"][0]
        self.assertEqual(c["summary"]["score"],-5)
        s=next(x["text"] for x in c["source_sections"] if x["id"]=="90_review")
        self.assertIn("患者乙在坎一宫",s)
        self.assertEqual(s.count("乙奇势"),1)
    def test_real_editable_template(self):
        t=template()
        self.assertEqual(t["schema"],"health_severity_user_editable_template_v20261031_v11_full_evidence")
        self.assertIn("天芮{illness}",t["macros"]["summary_concise"])
        self.assertIn("古文：{classical_text}",t["formation"])

if __name__=="__main__":unittest.main()
