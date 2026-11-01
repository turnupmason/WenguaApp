"""V11 site-language contract: real chart, independent patient, no V8 grade."""
import json
import unittest
from pathlib import Path

from src.wengua.casting_shenqi import layout_from_explicit_bureau
from src.wengua.health_discomfort_template_v11_draft import (
    compose_draft, template, SCHEMA,
)

ROOT = Path(__file__).resolve().parents[1]
CAL = {"year_ganzhi":"庚午", "month_ganzhi":"己丑", "day_ganzhi":"辛卯"}
FRIEND = {"intent":"discomfort", "relationship":"friend",
          "consultation_context":"direct_proxy"}


class DiscomfortV11Draft(unittest.TestCase):
    def test_approved_version_is_not_claimed(self):
        data=template()
        self.assertEqual(data["topic_id"],"health.discomfort")
        self.assertEqual(len(data["sections"]),6)
        self.assertTrue(all(data["guards"].values()))
        profile=json.loads((ROOT/"data/knowledge/health_discomfort/body_location_profile_20261029.json").read_text())
        self.assertEqual(profile["release_status"],"research_draft_not_enabled")
        self.assertIsNone(profile["approved_customer_template"])
        self.assertFalse(profile["iOS_enabled"])

    def test_two_original_example_source_charts_and_independent_actors(self):
        for dun,ju,hour,expected in (("yang",3,"丁巳",1),("yin",8,"戊戌",8)):
            with self.subTest(dun=dun,ju=ju,hour=hour):
                chart=layout_from_explicit_bureau(dun=dun,ju=ju,hour_ganzhi=hour)
                result=compose_draft(chart=chart,inquiry=FRIEND,calendar=CAL)
                self.assertEqual(result["schema"],SCHEMA)
                self.assertEqual(result["audit"]["tianrui_palace"],expected)
                self.assertEqual(len(result["sections"]),6)
                self.assertIn("综上",result["sections"][-1]["text"])
                self.assertIn("体表",result["reading_text"])
                self.assertIn("体内",result["reading_text"])
                self.assertIn("时干",result["reading_text"])
                self.assertIn("伤门",result["reading_text"])
                self.assertIn("患者",result["reading_text"])
                for key in ("v80_severity_score","grade","timing","medical_diagnosis"):
                    self.assertIsNone(result["audit"][key])
                self.assertFalse(result["ios_enabled"])
                self.assertFalse(result["locks_15_days"])
                self.assertFalse(result["released"])

    def test_friend_sex_and_age_do_not_change_v11_main_signifier(self):
        chart=layout_from_explicit_bureau(dun="yang",ju=3,hour_ganzhi="丁巳")
        baseline=compose_draft(chart=chart,inquiry=FRIEND,calendar=CAL)
        other=compose_draft(chart=chart,inquiry={**FRIEND,"patient_sex":"female",
                   "relative_age":"older"},calendar=CAL)
        self.assertEqual(baseline["reading_text"],other["reading_text"])
        self.assertEqual(other["audit"]["patient_role"],"casting_month_stem")

    def test_wrong_intent_and_missing_center_fail_without_fake_chart(self):
        chart=layout_from_explicit_bureau(dun="yang",ju=3,hour_ganzhi="丁巳")
        with self.assertRaises(ValueError):
            compose_draft(chart=chart,inquiry={**FRIEND,"intent":"severity"},calendar=CAL)
        bad={**chart,"palaces":{k:dict(v) for k,v in chart["palaces"].items()}}
        bad["palaces"]["5"]["door"]="生门"
        with self.assertRaises(ValueError):
            compose_draft(chart=bad,inquiry=FRIEND,calendar=CAL)
        with self.assertRaises(ValueError):
            compose_draft(chart=chart,inquiry={**FRIEND,"relationship":"unknown"},calendar=CAL)

    def test_no_dangerous_diagnosis_or_score_in_all_real_states(self):
        for dun,ju,hour in (("yang",1,"甲子"),("yang",3,"丁巳"),
                            ("yin",2,"戊戌"),("yin",8,"戊戌")):
            chart=layout_from_explicit_bureau(dun=dun,ju=ju,hour_ganzhi=hour)
            r=compose_draft(chart=chart,inquiry=FRIEND,calendar=CAL)
            for word in ("确诊","患癌","不治之症","判为极大凶","总分"):
                self.assertNotIn(word,r["reading_text"])
            self.assertIn("可参"+r["audit"]["surface_all"][0],
                          r["sections"][-1]["text"])


if __name__=="__main__":
    unittest.main()
