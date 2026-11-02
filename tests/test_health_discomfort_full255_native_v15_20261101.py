"""V15 independent body-location provenance gates; V8 severity untouched."""
from __future__ import annotations
import json
import unittest
from pathlib import Path

from src.wengua.health_discomfort_255_v15 import full_rules, match_location_inventory, stem_variants
from src.wengua.health_discomfort_template_v11_draft import template

ROOT=Path(__file__).resolve().parents[1]

class FullSourceV15Test(unittest.TestCase):
    def test_all_255_source_cases_and_conflicts_remain(self):
        book=full_rules()
        self.assertEqual(len(book["rules"]),255)
        self.assertEqual(len(book["cases"]),12)
        self.assertEqual(len(book["conflicts"]),20)
        self.assertEqual(len({x["ID"] for x in book["rules"]}),255)
        self.assertEqual({x["证据级别"][0] for x in book["rules"]},set("ABCDE"))
        self.assertTrue(all(not x["上下干方向"] for x in book["rules"]))

    def test_eight_palaces_two_sectors_and_ten_stems(self):
        for p in (1,2,3,4,6,7,8,9):
            for sector in ("inner","outer"):
                for stem in "甲乙丙丁戊己庚辛壬癸":
                    result=match_location_inventory(illness_palace=p,sector=sector,
                                                    sky_stem=stem,door="伤门",deity="白虎")
                    self.assertEqual(result["total"],255)
                    self.assertEqual(sum(map(len,(result["matched_qimen_text"],
                        result["cross_system_comparisons"],
                        result["inapplicable_or_unverified_ids"]))),255)
                    self.assertEqual(len(set(result["matched_ids"])),len(result["matched_ids"]))
                    self.assertEqual(len(result["three_stem_families"]),3)
                    self.assertEqual(result["conflicts_preserved"],20)
                    self.assertIsNone(result["severity_score"])
                    self.assertIsNone(result["clinical_diagnosis"])
                    self.assertTrue(any(x["category"]=="九宫定位"
                                        for x in result["matched_qimen_text"]))

    def test_double_stem_unknown_order_never_matched(self):
        result=match_location_inventory(illness_palace=2,sector="inner",
                    sky_stem="庚",door="死门",deity="值符")
        self.assertFalse(any(x.startswith("HLT-02") for x in result["matched_ids"]
                             if x>="HLT-0240"))
        self.assertIn("HLT-0254",result["inapplicable_or_unverified_ids"])
        self.assertIn("HLT-0203",result["inapplicable_or_unverified_ids"])

    def test_template_six_sections_source_comparison(self):
        t=template()
        self.assertEqual(len(t["sections"]),6)
        self.assertIn("source_comparison",t["macros"])
        self.assertIn("{sky}",t["macros"]["source_comparison"])
        self.assertEqual(set(stem_variants()["mapping"]),set("甲乙丙丁戊己庚辛壬癸"))

    def test_ios_bundle_and_separate_reader(self):
        y=(ROOT/"ios/WenguaAppUI/project.yml").read_text(encoding="utf8")
        app=(ROOT/"ios/WenguaAppUI/WenguaDesignPreviewApp.swift").read_text(encoding="utf8")
        reader=(ROOT/"ios/WenguaAppUI/WenguaNativeReadingRouter.swift").read_text(encoding="utf8")
        self.assertIn("complete_255_rules_v15_20261101.json",y)
        self.assertIn("three_source_stem_variants_v14_20261101.json",y)
        self.assertIn("native_discomfort_v15.json",y)
        self.assertIn('if topicID=="health.discomfort"',reader)
        self.assertIn('QuestionTopic(id:"health.severity",title:"病情轻重",domainTitle:"疾病健康",enabled:true)',app)
        self.assertIn('QuestionTopic(id:"health.discomfort",title:"伤病在哪里",domainTitle:"疾病健康",enabled:true)',app)

if __name__=="__main__":
    unittest.main()
