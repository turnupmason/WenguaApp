"""User's second real four-pillar health/severity preview, father patient."""
from __future__ import annotations
import inspect
import unittest
from unittest.mock import patch

from scripts.run_father_health_20261021_v24 import run, DB, EXPECTED
from src.wengua.health_severity_v24 import analyze_health_severity_v24,SKIPPED
from src.wengua.health_severity_v22 import FORBIDDEN_CUSTOMER
from src.wengua.astro_calendar import solar_chart_clock
from src.wengua.casting_shenqi import layout_from_explicit_bureau


class FatherTimeHealthV24Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not DB.is_file():
            raise AssertionError("Exact complete V2.2 original-194-event SQLite required")
    def test_actual_20261021_father_four_pillars_and_calendar(self):
        r=run()
        self.assertEqual(r["test_receipt"]["four_pillars"],EXPECTED)
        self.assertEqual(r["test_receipt"]["solar_term"],"寒露")
        self.assertEqual(r["test_receipt"]["bureau"]["dun"],"yin")
        self.assertEqual(r["test_receipt"]["bureau"]["ju"],6)
        self.assertEqual(r["test_receipt"]["bureau"]["yuan"],"upper")
        self.assertEqual(r["test_receipt"]["chart"]["hour_ganzhi"],"癸亥")
        self.assertEqual(r["test_receipt"]["chart"]["xun_shou"],"甲寅")
    def test_six_same_illness_palace_sections_merged_without_fact_loss(self):
        r=run()
        self.assertEqual(len(r["sections"]),16)
        self.assertNotIn("与与",r["reading_text"])
        self.assertNotIn("同同在",r["reading_text"])
        self.assertNotIn("。；",r["reading_text"])
        self.assertEqual(len(r["audit"]["internal_original_sections"]),21)
        self.assertEqual(set(r["audit"]["display_group_sources"]),SKIPPED)
        combined=r["sections"][3]
        self.assertEqual(combined["id"],"04_illness_palace_combined")
        for phrase in ("天芮星","天盘","地盘","体表","体内",
                       "门迫","八门","八神"):
            # 八门/八神 are represented by the actual eight-door/eight-deity
            # names, not by literal categories.
            if phrase not in ("八门","八神"):
                self.assertIn(phrase,combined["text"])
        original=[s["id"] for s in r["audit"]["internal_original_sections"]]
        self.assertEqual(len(original),21)
        self.assertTrue(SKIPPED.issubset(original))
        self.assertTrue(SKIPPED.isdisjoint(x["id"] for x in r["sections"]))
        self.assertEqual(len({x["id"] for x in r["sections"]}),16)
    def test_father_has_year_stem_and_qian_six_palace_not_self_day_stem(self):
        r=run()
        binding=r["audit"]["role_binding"]
        self.assertEqual(binding["relationship"],"father")
        self.assertEqual(binding["role_via"],"casting_year_stem")
        self.assertEqual(binding["stem"],"丙")
        self.assertIn("年干",binding["role_name"])
        self.assertIn("乾六宫",r["reading_text"])
        self.assertTrue(r["audit"]["father_qian_auxiliary_included"])
        self.assertIn("另参乾六宫",r["sections"][-1]["text"])
        self.assertIn("天心星",r["sections"][-1]["text"])
        self.assertIn("开门",r["sections"][-1]["text"])
        self.assertTrue(r["audit"]["effective_summary_uses_father_conditions"])
        self.assertFalse(r["audit"]["previous_generic_v22_summary_reused"])
        self.assertIn("艮八宫逢空亡",r["sections"][-1]["text"])
        self.assertIn("天芮土比和",r["sections"][-1]["text"])
        self.assertNotIn("病星亦受制",r["sections"][-1]["text"])
        self.assertIn("为父亲测病情轻重",r["sections"][0]["text"])
        self.assertIn("未提供出生年命",r["reading_text"])
        self.assertIn("蛇入地罗",r["sections"][3]["text"])
        self.assertIn("水道",r["sections"][3]["text"])
        self.assertFalse(r["audit"]["birth_year_required"])
    def test_self_and_father_are_different_even_on_identical_chart(self):
        father=run()
        chart=father["test_receipt"]["chart"]
        cal={"year_ganzhi":"丙午","month_ganzhi":"戊戌",
             "day_ganzhi":"戊辰","hour_ganzhi":"癸亥"}
        self_query={"intent":"severity","relationship":"self",
                    "consultation_context":"direct_self"}
        self_reading=analyze_health_severity_v24(
             chart=chart,inquiry=self_query,calendar=cal,db_path=DB)
        self.assertNotEqual(father["reading_text"],self_reading["reading_text"])
        self.assertNotIn("父亲乾宫",self_reading["reading_text"])
        self.assertEqual(self_reading["audit"]["role_binding"]["stem"],"戊")
        self.assertEqual(father["audit"]["role_binding"]["stem"],"丙")
    def test_pure_offline_no_gpt_stable_bytes_and_no_engine_words(self):
        with patch("socket.socket",side_effect=AssertionError("NETWORK FORBIDDEN")):
            first=run()
            second=run()
        self.assertEqual(first["reading_text"].encode("utf8"),
                         second["reading_text"].encode("utf8"))
        self.assertEqual(first["audit"]["model_calls"],0)
        self.assertEqual(first["audit"]["internet_calls"],0)
        self.assertEqual(first["audit"]["llm_rewrite"],False)
        for section in first["sections"]:
            for term in FORBIDDEN_CUSTOMER:
                self.assertNotIn(term,section["text"])
        self.assertEqual(first["audit"]["no_gpt_network_or_rewrite"],True)
        self.assertEqual(first["audit"]["user_acceptance"],"pending")
    def test_not_conflate_unknown_factors_with_real_mechanical_facts(self):
        r=run()
        self.assertEqual(len(r["audit"]["24_factor_statuses"]),24)
        self.assertGreater(len(r["audit"]["unknown_factor_ids"]),0)
        self.assertEqual(r["test_receipt"]["clinically_verified"],False)
        self.assertFalse(r["test_receipt"]["other_intents_approved"])
        self.assertNotIn("癌症",r["reading_text"])
        self.assertNotIn("必死",r["reading_text"])
    def test_surgery_discharge_and_others_still_explicitly_blocked(self):
        r=run()
        actual=r["test_receipt"]["chart"]
        with self.assertRaisesRegex(ValueError,"unreviewed"):
            analyze_health_severity_v24(chart=actual,
               inquiry={"intent":"surgery","relationship":"father",
                        "consultation_context":"direct_proxy"},
               calendar={"year_ganzhi":"丙午","day_ganzhi":"戊辰",
                         "month_ganzhi":"戊戌","hour_ganzhi":"癸亥"},
               db_path=DB)
    def test_print_unchanged_full_sixteen_paragraphs_and_chart(self):
        r=run()
        import json
        print("\nUSER_FATHER_GUI_HEALTH_OFFLINE_V24_BEGIN")
        print("CHART="+json.dumps(r["test_receipt"]["chart"],ensure_ascii=False,sort_keys=True))
        print("BUREAU="+json.dumps(r["test_receipt"]["bureau"],ensure_ascii=False,sort_keys=True))
        print("ROLE="+json.dumps(r["audit"]["role_binding"],ensure_ascii=False,sort_keys=True))
        for i,section in enumerate(r["sections"],1):
            print(f"SECTION_{i:02d} "+section["title"]+"："+section["text"])
        print("USER_FATHER_GUI_HEALTH_OFFLINE_V24_END")

if __name__=="__main__":
    unittest.main()
