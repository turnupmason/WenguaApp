"""First step after TRUE chart cast: 五不遇时 general adverse, 伏吟慢, 反吟快.

Use unchanged original methods (V2.7 five-not-encounter and V2.5 full
external-star/door fuyin/fanyin); no new casting rules or medical claims.
"""
import unittest
from datetime import datetime,timedelta

from src.wengua.health_macro_facts_vnext import (
    first_stage_macro,render_first_stage_macro)
from src.wengua.health_severity_v27 import five_not_encounter
from src.wengua.health_severity_v25 import fuyin_fanyin_facts
from src.wengua.astro_calendar import solar_chart_clock
from src.wengua.health_text_pipeline_vnext_review import (
    auto_cast_health_review_text)
from src.wengua.casting_shenqi import (
    bureau_for_term,layout_from_explicit_bureau)

QUERY={"intent":"severity","relationship":"self",
       "consultation_context":"direct_self"}


class FirstStageMacroFacts(unittest.TestCase):
    def test_existing_exact_daily_hourly_rule_five_not_encounter(self):
        self.assertTrue(five_not_encounter("甲子","庚午")["triggered"])
        self.assertTrue(five_not_encounter("乙丑","辛巳")["triggered"])
        self.assertTrue(five_not_encounter("己卯","乙丑")["triggered"])
        # Matching five elements not enough: yang/yang or yin/yin required.
        self.assertFalse(five_not_encounter("甲子","辛巳")["triggered"])
        self.assertFalse(five_not_encounter("乙丑","庚申")["triggered"])
        self.assertEqual(five_not_encounter("甲子","庚午")["effect"],
                         "凶时信号，但不单条断生死")

    def test_live_cast_macro_before_selected_palace_sections(self):
        out=auto_cast_health_review_text(
            iso="2026-10-22T12:00:00-04:00",
            timezone_name="America/New_York",inquiry=QUERY)
        macro=out["first_stage_macro"]
        self.assertEqual(macro["version"],"user_health_macro_first_20261023_v1")
        chart={"palaces":out["nine_palaces"],
               "hour_ganzhi":out["four_pillars"]["hour"]}
        self.assertEqual(macro["fuyin_fanyin"],fuyin_fanyin_facts(chart))
        self.assertIn(macro["tempo"],
                      ("fast","slow","mixed","not_assessed_from_fuyin"))
        self.assertTrue(macro["tempo_is_not_auspiciousness"])
        self.assertEqual(out["sections"][0]["id"],"01_macro")
        self.assertIn("五不遇时",out["sections"][0]["text"])
        self.assertIn("伏吟",out["sections"][0]["text"])
        self.assertIn("反吟",out["sections"][0]["text"])
        self.assertTrue(out["reading_text"].startswith("起盘总纲"))
        # Latest signed-energy conclusion demotes old count-only text.
        self.assertNotIn("宫位五级吉凶净分合断",out["reading_text"])
        self.assertIn("candidate_five_grade_quantization",\n                      out["full_health_role_strength_network"])
        self.assertIn("天芮病宫",out["reading_text"])
        self.assertIn("八神",out["reading_text"])

    def test_real_not_encounter_hour_counts_exactly_one_global_bad_fact(self):
        # Find a REAL future-free ordinary dated chart, never invent a
        # day/hour stem pair inconsistent with the actual casting calendar.
        day=datetime.fromisoformat("2026-10-01T12:00:00-04:00")
        found=None
        for n in range(12):
            iso=(day+timedelta(days=n)).isoformat()
            clock=solar_chart_clock(iso,"America/New_York")
            p=clock["four_pillars"]
            if five_not_encounter(p["day"],p["hour"])["triggered"]:
                found=iso
                break
        self.assertIsNotNone(found,"Expected at least one five-not-encounter date")
        # At a 五不遇时 instant the original self-day stem can be 甲 and
        # hide; do NOT fake its placement to force a self reading. Instead
        # use an explicitly bound real 乾六 father as a proxy patient.
        out=auto_cast_health_review_text(
            iso=found,timezone_name="America/New_York",
            inquiry={"intent":"severity","relationship":"father",
                     "consultation_context":"direct_proxy"})
        macro=out["first_stage_macro"]
        self.assertTrue(macro["five_not_encounter_triggered"])
        self.assertIn("主诸事凶",out["sections"][0]["text"])
        evidence=out["evidence_ledger"]
        hits=[e for e in evidence["adverse"]
              if e["id"].startswith("macro:five_not_encounter:")]
        self.assertEqual(len(hits),1)
        self.assertEqual(
            out["evidence_counts"]["qualified_adverse"],
            len(out["evidence_ledger"]["adverse"]))
        self.assertNotIn(
            "macro:five_not_encounter",str(out["evidence_ledger"]["favorable"]))
        self.assertTrue(out["no_scoring"])

    def test_fuyin_and_fanyin_tempo_do_not_cast_good_or_bad_vote(self):
        macro={
            "five_not_encounter":{
                "triggered":False,"hour_stem":"辛","day_stem":"甲"},
            "fuyin_fanyin":{
                "star":"伏吟","door":"反吟","pace":"混合"},
            "tempo":"mixed"}
        txt=render_first_stage_macro(macro)
        self.assertIn("伏吟主慢",txt)
        self.assertIn("反吟主快",txt)
        self.assertIn("缓急不自动等于吉凶",txt)
        for state,label,expected in (
            ("slow","伏吟","伏吟主慢"),
            ("fast","反吟","反吟主快")):
            macro["tempo"]=state
            macro["fuyin_fanyin"]={"star":label,"door":label}
            self.assertIn(expected,render_first_stage_macro(macro))


if __name__=="__main__":
    unittest.main()
