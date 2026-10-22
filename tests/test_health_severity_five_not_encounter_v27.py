"""Regression: 五不遇时, gender/Qian-Kun auxiliary and random historical source family draw."""
from __future__ import annotations
import json, unittest
from unittest.mock import patch

from src.wengua.health_severity_v27 import (
  five_not_encounter,analyze_health_severity_v27,_clinical_role_sign)
from scripts.run_two_historical_health_v27 import (
   draw,evaluate,CHOSEN_EXPECTED,PARENT_DB,SEED,fnv32,CASE_METADATA)

class FiveNoEncounterAndTwoHistoricalCases(unittest.TestCase):
    def test_formula_correct_same_polarity_and_true_hour_controls_day(self):
        a=five_not_encounter("庚申","丙戌")
        self.assertTrue(a["triggered"])
        self.assertTrue(a["same_yin_yang"])
        self.assertTrue(a["hour_controls_day"])
        self.assertEqual((a["hour_stem"],a["day_stem"]),("丙","庚"))
        self.assertEqual((a["hour_element"],a["day_element"]),("火","金"))
        self.assertTrue(five_not_encounter("癸卯","己未")["triggered"])
        self.assertTrue(five_not_encounter("乙丑","辛巳")["triggered"])
        self.assertFalse(five_not_encounter("癸卯","庚申")["triggered"])
        self.assertFalse(five_not_encounter("庚申","丁亥")["triggered"])
        self.assertFalse(five_not_encounter("戊辰","庚申")["triggered"])
        self.assertFalse(five_not_encounter("庚申","戊寅")["triggered"])
    def test_directional_health_interpretations_have_auditable_good_or_bad(self):
        checks=[
            ("patient","克","偏吉"),("patient","受克","偏凶"),
            ("patient","生","偏凶"),("patient","受生","偏吉"),
            ("doctor","克","偏吉"),("doctor","生","偏凶"),
            ("medicine","受克","偏凶"),("medicine","受生","未制病"),
            ("gender","克","偏吉"),("gender","受克","偏凶"),
            ("hour","克","偏吉"),("hour","生","偏凶")
        ]
        for role,relation,word in checks:
            self.assertIn(word,_clinical_role_sign(role,relation))
        self.assertIn("吉凶未定",_clinical_role_sign("gender","比和"))
    def test_reproducible_draw_has_two_different_real_families(self):
        cases,ranks=draw()
        self.assertEqual(cases,CHOSEN_EXPECTED)
        self.assertNotEqual(cases[0],cases[1])
        self.assertEqual(len(ranks),6)
        self.assertEqual(len(SEED),64)
        self.assertEqual(CASE_METADATA[cases[1]]["sex"],"female")
        self.assertIsNone(CASE_METADATA[cases[0]]["sex"])
    def test_real_calendar_original_chart_book_metadata_before_author_outcome(self):
        report=evaluate()
        self.assertEqual(len(report["predictions"]),2)
        self.assertFalse(report["original_book_outcomes_appended"])
        for p in report["predictions"]:
            self.assertTrue(p["book_metadata_only_used"])
            self.assertFalse(p["original_pred_and_feedback_read"])
            self.assertEqual(len(p["readout_sha256"]),64)
            self.assertEqual(p["full_chart"]["hour_ganzhi"],p["hour_ganzhi"])
        a,b=report["predictions"]
        self.assertFalse(a["five_not_encounter"]["triggered"])
        self.assertTrue(b["five_not_encounter"]["triggered"])
        self.assertIn("不属五不遇时",a["readout_text"])
        self.assertIn("阳克阳",b["readout_text"])
        self.assertIn("测病为传统凶时",b["readout_text"])
        self.assertEqual(b["gender_auxiliary_palace"],2)
        self.assertIsNone(a["gender_auxiliary_palace"])
        self.assertEqual(len(b["readout_sections"]),11)
        self.assertEqual(len(a["readout_sections"]),10)
        self.assertIn("坤二宫",b["readout_text"])
        self.assertNotIn("另参乾六宫",a["readout_text"])
    def test_gender_explicit_known_man_gets_qian_but_not_otherwise(self):
        from src.wengua.astro_calendar import solar_chart_clock
        from src.wengua.casting_shenqi import layout_from_explicit_bureau
        c=solar_chart_clock("1996-11-02T16:00:00+08:00","Asia/Shanghai")["four_pillars"]
        chart=layout_from_explicit_bureau(dun="yin",ju=8,hour_ganzhi="庚申")
        cal={"year_ganzhi":c["year"],"month_ganzhi":c["month"],
             "day_ganzhi":c["day"],"hour_ganzhi":c["hour"],"month_branch":c["month"][1]}
        reading=analyze_health_severity_v27(
          chart=chart,inquiry={"intent":"severity","relationship":"self",
            "consultation_context":"direct_self","patient_sex":"male"},
          calendar=cal,db_path=PARENT_DB)
        self.assertEqual(reading["audit"]["gender_auxiliary_palace"],6)
        self.assertEqual(len(reading["sections"]),11)
        self.assertIn("乾六宫",reading["sections"][5]["text"])
    def test_no_network_no_gpt_byte_reproducibility_and_original_not_read(self):
        with patch("socket.socket",side_effect=AssertionError("NETWORK NOT ALLOWED")):
            a=evaluate();b=evaluate()
        self.assertEqual(a["predictions"][0]["readout_text"].encode(),
                         b["predictions"][0]["readout_text"].encode())
        self.assertEqual(a["predictions"][1]["readout_text"].encode(),
                         b["predictions"][1]["readout_text"].encode())
        for p in a["predictions"]:
            text=p["readout_text"]
            for forbidden in ("GPT","程序","规则库","数据库","模型","门门迫","与与"):
                self.assertNotIn(forbidden,text)
            self.assertIn("病吉",text) if p["traditional_verdict"]=="病吉" else self.assertIn("病凶",text)
            self.assertNotIn("例如符合",text)
            self.assertNotIn("必死",text)
            self.assertNotIn("原书结果",text)
            self.assertEqual(p["readout_text"].count("最后断词："),1)
    def test_four_unapproved_health_intents_still_blocked(self):
        from src.wengua.casting_shenqi import layout_from_explicit_bureau
        chart=layout_from_explicit_bureau(dun="yin",ju=8,hour_ganzhi="庚申")
        cal={"year_ganzhi":"丙子","month_ganzhi":"戊戌",
             "day_ganzhi":"癸卯","hour_ganzhi":"庚申","month_branch":"戌"}
        for intent in ("treatment","discharge","surgery","travel_for_treatment"):
            with self.assertRaises(ValueError):
                analyze_health_severity_v27(
                  chart=chart,inquiry={"intent":intent,"relationship":"self",
                    "consultation_context":"direct_self"},
                  calendar=cal,db_path=PARENT_DB)
    def test_print_both_raw_sealed_predictions(self):
        report=evaluate()
        print("\nV27_SEALED_TWO_HISTORICAL_START")
        for i,p in enumerate(report["predictions"],1):
            print(f"CASE_{i}_ID="+p["case_id"])
            print(f"CASE_{i}_HOUR="+p["day_ganzhi"]+"日"+p["hour_ganzhi"]+"时")
            print(f"CASE_{i}_READOUT_SHA="+p["readout_sha256"])
            print(f"CASE_{i}_READOUT_BEGIN")
            print(p["readout_text"])
            print(f"CASE_{i}_READOUT_END")
        print("V27_SEALED_TWO_HISTORICAL_END")

if __name__=="__main__":
    unittest.main()
