"""V7.2 conditional co-host rules; regression of real elderly female clock.
No fake medical assertion; test the deterministically scored cultural system.
"""
import unittest
from src.wengua.health_quant_overlay_vnext import special_cohost_total
from src.wengua.health_text_pipeline_vnext_review import auto_cast_health_review_text

class ElderCohostV72(unittest.TestCase):
    def test_exact_four_deity_earth_combinations_and_void_half_floor(self):
        for chief,earth,total in ((3,3,6),(2,3,5),(3,1,4),(2,1,3)):
            with self.subTest(chief=chief,earth=earth):
                self.assertEqual(special_cohost_total(chief,earth),total)
                self.assertEqual(special_cohost_total(chief,earth,void=True),total//2)
        self.assertEqual(special_cohost_total(0,3,void=True),1)
        self.assertEqual(special_cohost_total(3,0,void=True),1)
        with self.assertRaises(ValueError):
            special_cohost_total(7,3)

    def test_real_original_four_pillars_elder_female_and_unique_real_palaces(self):
        r=auto_cast_health_review_text(
            iso="2010-02-02T07:00:00-05:00",timezone_name="America/New_York",
            inquiry={"intent":"severity","relationship":"older_relative",
                     "consultation_context":"direct_proxy",
                     "patient_sex":"female","patient_birth_ganzhi":"庚午"})
        self.assertEqual(tuple(r["four_pillars"][k] for k in
                           ("year","month","day","hour")),
                         ("己丑","丁丑","癸未","丙辰"))
        q=r["full_health_role_strength_network"]["candidate_five_grade_quantization"]
        self.assertEqual(q["roles"]["gender"]["palace"],2)
        self.assertIn("natal",q["roles"])
        summary=q["summary"]
        self.assertEqual(summary["auspice_bonus_score"],
                         sum(x["points"] for x in summary["auspice_bonus_details"].values()))
        for palace,record in summary["auspice_cohost_audit"].items():
            self.assertEqual(record["after_void"],
                             special_cohost_total(record["chief"],record["stem_family"],
                                                  void=record["empty"]))
            self.assertLessEqual(len(set(x["stem"] for x in
                                record["stem_candidates"])),2)
            self.assertIn(record["after_void"],range(0,7))
        for forbidden in ("按新规则加3分","同宫去重","每宫加3分",
                          "完全失控","长生分支待核（"):
            self.assertNotIn(forbidden,r["reading_text"])
        self.assertIn("以上只作传统古籍象意参考",r["reading_text"])

    def test_second_real_person_cannot_duplicate_qian_kun(self):
        r=auto_cast_health_review_text(
            iso="2010-02-02T07:00:00-05:00",timezone_name="America/New_York",
            inquiry={"intent":"severity","relationship":"friend",
                     "consultation_context":"direct_proxy","patient_sex":"male"})
        selected=r["full_health_role_strength_network"]["candidate_five_grade_quantization"]
        self.assertNotIn("gender",selected["roles"])

if __name__=="__main__":
    unittest.main()
