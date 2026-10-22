"""Acceptance-focused tests: pure offline 21-section health severity, not GPT prose."""
from __future__ import annotations
import inspect
import socket
import unittest
from pathlib import Path
from unittest.mock import patch

from src.wengua.casting_shenqi import layout_from_explicit_bureau
from src.wengua.health_severity_v22 import (
    analyze_health_severity_v22, _read_stem_pair_from_source,FORBIDDEN_CUSTOMER)
from src.wengua.health_dynamic_v21 import bind_patient
from scripts.run_health_severity_v22 import run,DEFAULT_DB,PILLARS


class OfflineSeverityV22Gate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not DEFAULT_DB.is_file():
            raise AssertionError("Real latest V2.1 source SQLite required for test")
    def test_01_all_21_real_source_with_no_gpt_network_or_polishing(self):
        # Deny *all* socket creation in the test environment; every result
        # must come from original local chart/SQLite and plain Python formats.
        with patch("socket.socket",side_effect=AssertionError("NETWORK ACCESSED")):
            result=run()
        self.assertEqual(len(result["sections"]),21)
        self.assertGreater(len(result["reading_text"]),1800)
        self.assertEqual(result["audit"]["model_calls"],0)
        self.assertEqual(result["audit"]["internet_calls"],0)
        self.assertIs(result["audit"]["llm_rewrite"],False)
        self.assertEqual(result["audit"]["render_mode"],"stdlib_python_format_map_no_llm")
        for x in result["sections"]:
            for keyword in FORBIDDEN_CUSTOMER:
                self.assertNotIn(keyword,x["text"],msg=keyword)
        self.assertNotIn("{",result["reading_text"])
        self.assertNotIn("《开悟之门》",result["reading_text"])
        self.assertNotIn("《神奇之门》",result["reading_text"])
    def test_02_same_input_exact_bytes_identical_no_random_or_gpt(self):
        a=run()
        b=run()
        self.assertEqual(a["reading_text"].encode("utf8"),b["reading_text"].encode("utf8"))
        self.assertEqual([x["id"] for x in a["sections"]],
            [f"{i:02d}_"+ending for i,ending in enumerate((
             "question","far_star","far_door","illness_star","body_part",
             "stem_image","strength","stem_pair","formations","deity","door","void",
             "patient","doctor","medicine","event","hard_factors","movement",
             "counter","timing","summary"),1)])
    def test_03_true_book_pair_name_and_context_without_db_meta(self):
        x=run()
        t=x["sections"][7]["text"]
        self.assertIn("壬加辛",t)
        self.assertIn("螣蛇相缠",t)
        self.assertIn("纠缠",t)
        self.assertIn("天芮",x["sections"][8]["text"])
        self.assertIn("死门",x["sections"][8]["text"])
        self.assertIn("六合",x["sections"][8]["text"])
        source=x["audit"]["stem_pair_source"]
        self.assertEqual(source["id"],"heaven_over_earth:壬:辛")
        self.assertEqual(source["provenance"]["line"],661)
        self.assertIn("螣蛇相缠",source["original_excerpt"])
    def test_04_not_confuse_whole_board_door_press_with_illness(self):
        x=run()
        self.assertEqual(x["audit"]["actual_door_press_palaces"],[4])
        self.assertFalse(x["audit"]["illness_palace_door_press"])
        txt=x["sections"][10]["text"]+x["sections"][16]["text"]
        self.assertIn("巽四宫",txt)
        self.assertIn("惊门",txt)
        self.assertIn("门迫",txt)
        self.assertIn("病星宫死门不构成门迫",txt)
    def test_05_no_dropping_known_beneficial_or_adverse_in_final(self):
        x=run()
        e=x["audit"]["evidence"]
        a="；".join(e["adverse"])
        f="；".join(e["favorable"])
        self.assertIn("天芮临死门",a)
        self.assertIn("螣蛇相缠",a)
        self.assertIn("戌",x["sections"][6]["text"])
        self.assertIn("震三宫属木，克天芮土",f)
        self.assertIn("离九宫不逢旬空",f)
        self.assertIn("开门",f)
        self.assertIn("吉凶",x["sections"][18]["text"])
        self.assertIn("吉凶交见",x["sections"][20]["text"])
    def test_06_no_fake_clinical_medical_lifespan_or_timing(self):
        x=run()
        self.assertTrue(x["audit"]["clinically_verified"] is False)
        self.assertEqual(x["test_receipt"]["role_assumption_unconfirmed"],True)
        self.assertEqual(x["audit"]["render_approval"],"pending_user_confirmation")
        self.assertNotIn("必死",x["reading_text"])
        self.assertNotIn("癌症",x["reading_text"])
        self.assertNotIn("2026年11月",x["reading_text"])
        self.assertIn("不指定日期",x["sections"][19]["text"])
    def test_07_person_role_inquiry_routes_change_without_replacing_names(self):
        a=run()
        father=run(who="father",context="direct_proxy")
        friend=run(who="friend",context="direct_proxy")
        heard=run(who="friend",context="event_news")
        child=run(who="son",context="direct_proxy")
        self.assertEqual(a["audit"]["role_binding"]["role_via"],"day_stem")
        self.assertEqual(father["audit"]["role_binding"]["role_via"],"casting_year_stem")
        self.assertEqual(friend["audit"]["role_binding"]["role_via"],"casting_month_stem")
        self.assertEqual(heard["audit"]["role_binding"]["role_via"],"day_stem")
        self.assertEqual(child["audit"]["role_binding"]["role_via"],"casting_hour_stem")
        self.assertIn("乾六宫",father["sections"][12]["text"])
        self.assertNotEqual(a["reading_text"],father["reading_text"])
        self.assertNotEqual(friend["reading_text"],heard["reading_text"])
        self.assertNotEqual(child["reading_text"],father["reading_text"])
    def test_08_chart_mutation_and_other_intents_strictly_rejected(self):
        chart=layout_from_explicit_bureau(dun="yin",ju=6,hour_ganzhi="壬戌")
        inquiry={"intent":"severity","relationship":"self","consultation_context":"direct_self"}
        cal={"year_ganzhi":"丙午","month_ganzhi":"戊戌",
             "day_ganzhi":"戊辰","hour_ganzhi":"壬戌"}
        chart["palaces"]["3"]["door"]="开门"
        with self.assertRaises(ValueError):
            analyze_health_severity_v22(chart=chart,inquiry=inquiry,calendar=cal,db_path=DEFAULT_DB)
        chart=layout_from_explicit_bureau(dun="yin",ju=6,hour_ganzhi="壬戌")
        with self.assertRaises(ValueError):
            analyze_health_severity_v22(chart=chart,
                inquiry={**inquiry,"intent":"treatment"},calendar=cal,db_path=DEFAULT_DB)
    def test_09_guard_offline_runtime_dependencies_stdlib_no_gpt(self):
        import src.wengua.health_severity_v22 as m
        source=inspect.getsource(m)
        for prohibited in ("openai", "anthropic", "google.generativeai",
                           "ChatCompletion", "requests.", "httpx.", "urllib.request",
                           "subprocess.", "eval(", "exec(", "transformers"):
            self.assertNotIn(prohibited,source)
    def test_10_show_exact_unedited_python_21_paragraphs(self):
        r=run()
        print("\nOFFLINE_SEVERITY_V22_CUSTOMER_TEXT_START")
        print(r["reading_text"])
        print("OFFLINE_SEVERITY_V22_CUSTOMER_TEXT_END")
        print("OFFLINE_SEVERITY_V22_AUDIT="+str({
            "source":r["audit"]["stem_pair_source"]["id"],
            "source_line":r["audit"]["stem_pair_source"]["provenance"]["line"],
            "factors_unknown":len(r["audit"]["unknown_factor_ids"]),
            "actual_door_press_palaces":r["audit"]["actual_door_press_palaces"],
            "all_sections":len(r["sections"]),"approved_by_user":False}))


if __name__=="__main__":
    unittest.main()
