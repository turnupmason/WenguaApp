"""Draft body-location: every source palace and two real historical charts.

This suite must not enable the iOS topic or alter frozen V8 scoring/V10.2 copy.
"""
import json
import unittest
from pathlib import Path

from src.wengua.casting_shenqi import layout_from_explicit_bureau
from src.wengua.health_discomfort_location_draft import (
    inspect_traditional_body_clues, load_body_source,
)

ROOT=Path(__file__).resolve().parents[1]

class TraditionalBodySite(unittest.TestCase):
    def test_all_eight_source_palaces_and_line_level_provenance(self):
        rows=load_body_source()
        self.assertEqual(set(rows),{1,2,3,4,6,7,8,9})
        self.assertEqual(rows[9]["surface"],["头","眼","面"])
        self.assertIn("胃",rows[2]["internal"])
        self.assertEqual(rows[1]["internal"],["肾","膀胱","内分泌系统"])
        self.assertTrue(all(r["source_lines"]==[5,7] for r in rows.values()))
        self.assertTrue(all(r["review_status"]=="draft" for r in rows.values()))

    def test_original_historical_charts_return_alternatives_not_a_diagnosis(self):
        cases=[
            ("yang",3,"丁巳",1,"坎"),
            ("yin",8,"戊戌",8,"艮"),
        ]
        for dun,ju,hour,expected_palace,trigram in cases:
            with self.subTest(dun=dun,ju=ju,hour=hour):
                chart=layout_from_explicit_bureau(dun=dun,ju=ju,hour_ganzhi=hour)
                evidence=inspect_traditional_body_clues(chart)
                self.assertEqual(evidence["tianrui_palace"],expected_palace)
                self.assertEqual(evidence["tianrui_trigram"],trigram)
                self.assertEqual(evidence["diagnosis"],None)
                self.assertEqual(evidence["conclusion"],None)
                self.assertEqual(evidence["v80_score"],None)
                self.assertFalse(evidence["medical_claim"])
                self.assertTrue(evidence["surface_symbol_candidates"])
                self.assertTrue(evidence["internal_symbol_candidates"])
                self.assertNotEqual(evidence["injury_door_palace_for_secondary_review"],5)
                self.assertEqual(evidence["topic_id"],"health.discomfort")

    def test_missing_or_fabricated_palace_fails_closed(self):
        chart=layout_from_explicit_bureau(dun="yang",ju=3,hour_ganzhi="丁巳")
        with self.assertRaises(ValueError):
            inspect_traditional_body_clues({**chart,"school_id":"unverified"})
        del chart["palaces"]["5"]
        with self.assertRaises(ValueError):
            inspect_traditional_body_clues(chart)

    def test_ui_topic_changes_only_label_and_remains_gated(self):
        ui=(ROOT/"ios/WenguaAppUI/WenguaDesignPreviewApp.swift").read_text()
        router=(ROOT/"ios/WenguaAppUI/WenguaNativeReadingRouter.swift").read_text()
        manifest=json.loads((ROOT/"data/knowledge/health_discomfort/body_location_profile_20261029.json").read_text())
        self.assertIn('QuestionTopic(id:"health.severity",title:"病情轻重",domainTitle:"疾病健康",enabled:true)',ui)
        self.assertIn('QuestionTopic(id:"health.discomfort",title:"难受部位",domainTitle:"疾病健康",enabled:false)',ui)
        self.assertNotIn('QuestionTopic(id:"health.trend"',ui)
        self.assertEqual(manifest["release_status"],"research_draft_not_enabled")
        self.assertIsNone(manifest["approved_customer_template"])
        self.assertIn('static let supportedTopics = ["health.severity"]',router)
        self.assertIn('guard topic.enabled && topic.id == "health.severity"',ui)
        self.assertTrue(manifest["no_15_day_lock_until_verified"])

if __name__=="__main__":
    unittest.main()
