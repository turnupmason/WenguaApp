"""Supplementary body region research is a source-guarded candidate, not V8."""
import json
import unittest
from pathlib import Path
from src.wengua.casting_shenqi import layout_from_explicit_bureau
from src.wengua.health_discomfort_location_draft import (
    load_traditional_location_candidates, inspect_traditional_body_clues)

ROOT = Path(__file__).resolve().parents[1]


class HealthDiscomfortExternalNotes(unittest.TestCase):
    def test_eight_palaces_ten_stems_all_eight_doors_and_deities(self):
        data = load_traditional_location_candidates()
        self.assertEqual(data["title"], "难受部位")
        self.assertIsNone(data["source"]["book_id"])
        self.assertFalse(data["medical_diagnosis_allowed"])
        self.assertFalse(data["release_approved"])
        self.assertEqual(set(data["palace"]), set("12346789"))
        self.assertEqual(set(data["stems"]), set("甲乙丙丁戊己庚辛壬癸"))
        for s in "乙丙丁戊己庚辛壬癸":
            self.assertEqual(set(data["stems"][s]["by_palace"]),set("12346789"))
        self.assertEqual(len(data["doors"]), 8)
        self.assertEqual(len(data["deities"]), 8)
        self.assertNotEqual(data["doors"]["生门"]["illness"],
                            data["doors"]["生门"]["patient"])
        self.assertNotEqual(data["deities"]["值符"]["illness"],
                            data["deities"]["值符"]["patient"])

    def test_real_charts_keep_both_sky_stems_distinct_without_diagnosis(self):
        data = load_traditional_location_candidates()
        for dun,ju,hour in [("yang",3,"丁巳"),("yin",8,"戊戌"),("yang",2,"丁卯")]:
            with self.subTest(dun=dun,ju=ju,hour=hour):
                chart = layout_from_explicit_bureau(dun=dun,ju=ju,hour_ganzhi=hour)
                r = inspect_traditional_body_clues(chart)
                p = chart["palaces"][str(r["tianrui_palace"])]
                s = next(q["carried_stem"] for q in p["heaven_stars"]
                         if q["star"] == "天芮星")
                second = next((q["carried_stem"] for q in p["heaven_stars"]
                               if q["star"] == "天禽星"),None)
                self.assertEqual(r["tianrui_stem_main_clues"],data["stems"][s])
                self.assertEqual(r["tianqin_stem_secondary_clues"],
                                 data["stems"].get(second))
                for key in ["patient_door_clues","inner_outer_decision",
                            "new_old_decision","cancer_or_other_diagnosis",
                            "diagnosis","conclusion","v80_score"]:
                    self.assertIsNone(r[key])
                self.assertFalse(r["customer_template_approved"])

    def test_ui_only_label_updated_and_router_still_blocked(self):
        ui=(ROOT/"ios/WenguaAppUI/WenguaDesignPreviewApp.swift").read_text()
        router=(ROOT/"ios/WenguaAppUI/WenguaNativeReadingRouter.swift").read_text()
        profile=json.loads((ROOT/"data/knowledge/health_discomfort/body_location_profile_20261029.json").read_text())
        self.assertIn('QuestionTopic(id:"health.discomfort",title:"难受部位",domainTitle:"疾病健康",enabled:false)',ui)
        self.assertIn('static let supportedTopics = ["health.severity"]',router)
        self.assertIsNone(profile["approved_customer_template"])
        self.assertFalse(profile["iOS_enabled"])


if __name__=="__main__":
    unittest.main()
