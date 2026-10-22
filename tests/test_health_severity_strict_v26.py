"""Actual 2026 戊辰日庚申时 SELF + regression 2026 癸亥 father.

Tests true offline Chinese template semantics, not brittle generic CI green flags.
"""
from __future__ import annotations
import json, tempfile, unittest
from pathlib import Path
from unittest.mock import patch

from scripts.run_self_gengshen_v26 import run,PARENT_DB
from src.wengua.health_severity_v26 import (
    analyze_health_severity_v26,fuyin_fanyin_facts,_direction,
    _star_relation,_source_pair_prose
)
from src.wengua.health_severity_v22 import FORBIDDEN_CUSTOMER
from src.wengua.casting_shenqi import layout_from_explicit_bureau


class RealSelfGengshenStrictTemplateV26(unittest.TestCase):
    def test_real_self_chart_no_old_hour_or_father_substitution(self):
        r=run()
        c=r["test_receipt"]["chart"]
        self.assertEqual(c["hour_ganzhi"],"庚申")
        self.assertEqual(r["test_receipt"]["solar_term"],"寒露")
        self.assertEqual(r["test_receipt"]["bureau"]["ju"],6)
        self.assertEqual(r["audit"]["role_binding"]["stem"],"戊")
        self.assertEqual(r["audit"]["role_binding"]["relationship"],"self")
        self.assertEqual(len(r["sections"]),10)
        self.assertIn("日干戊",r["sections"][0]["text"])
        self.assertNotIn("父亲",r["reading_text"])
    def test_true_disease_palace_element_direction(self):
        for palace,expected in [(1,"天芮土克病宫水，病星克宫"),
                  (2,"宫星同气"),(3,"病星受宫制"),
                  (6,"天芮土生病宫金"),(9,"病宫火生天芮土")]:
            self.assertIn(expected,_star_relation({"palace":palace}))
        r=run()
        self.assertIn("天芮土克病宫水，病星克宫",r["reading_text"])
        self.assertNotIn("病星与落宫受克",r["reading_text"])
        self.assertNotIn("病星受落宫克制",r["reading_text"])
    def test_five_element_directional_arguments(self):
        cells={p:{"palace":p} for p in (1,2,3,6,9)}
        self.assertIn("木生",_direction(cells[3],cells[9],"甲","乙"))
        self.assertIn("乙受生",_direction(cells[3],cells[9],"甲","乙"))
        self.assertIn("土克",_direction(cells[2],cells[1],"病宫","值使"))
        self.assertIn("值使受制",_direction(cells[2],cells[1],"病宫","值使"))
        self.assertIn("金克",_direction(cells[6],cells[3],"医药","病宫"))
        self.assertIn("病宫受制",_direction(cells[6],cells[3],"医药","病宫"))
    def test_irrelevant_anachronistic_pair_title_never_in_customer_prose(self):
        x=run()
        original=x["audit"]["pair_original_still_auditable"]
        self.assertIn("幼女奸淫",original["name"])
        self.assertNotIn("幼女奸淫",x["reading_text"])
        self.assertIn("壬加癸",x["sections"][2]["text"])
        self.assertIn("两干同属水",x["sections"][2]["text"])
        self.assertNotIn("须看事体所在宫",x["reading_text"])
    def test_targeted_door_pressure_no_bad_repeated_phrase(self):
        x=run()
        t=x["sections"][7]["text"]
        self.assertIn("坎一宫的死门构成门迫",t)
        self.assertIn("震三宫的开门构成门迫",t)
        self.assertNotIn("门门迫",x["reading_text"])
        self.assertNotIn("影响病宫",x["reading_text"])
        self.assertNotIn("与与",x["reading_text"])
        self.assertNotIn("同同",x["reading_text"])
        self.assertEqual(set(x["audit"]["actual_door_press_palaces"]),{1,3})
    def test_real_pace_in_timing_and_final_and_fuyin_regression(self):
        x=run()
        fy=x["audit"]["fuyin_fanyin"]
        self.assertEqual(fy["star"],"非伏吟反吟")
        self.assertEqual(fy["door"],"非伏吟反吟")
        self.assertEqual(x["audit"]["illness_inner_outer"],"外盘")
        self.assertEqual(x["audit"]["patient_inner_outer"],"外盘")
        self.assertIn("传统主慢",x["sections"][-2]["text"])
        self.assertIn("传统主慢",x["sections"][-1]["text"])
        old=layout_from_explicit_bureau(dun="yin",ju=6,hour_ganzhi="癸亥")
        a=fuyin_fanyin_facts(old)
        self.assertTrue(a["both_fuyin"])
        self.assertEqual(a["star_home"],8)
        self.assertEqual(a["door_home"],8)
        self.assertFalse(a["both_fanyin"])
    def test_same_engine_prior_father_regression_not_frozen_old_verdict(self):
        from scripts.run_father_health_20261021_v24 import run as old_case
        case=old_case()
        c=case["test_receipt"]["chart"]
        cal={"year_ganzhi":"丙午","month_ganzhi":"戊戌","day_ganzhi":"戊辰",
             "hour_ganzhi":"癸亥","month_branch":"戌"}
        output=analyze_health_severity_v26(
            chart=c,inquiry={"intent":"severity","relationship":"father",
               "consultation_context":"direct_proxy"},calendar=cal,db_path=PARENT_DB)
        self.assertEqual(len(output["sections"]),11)
        self.assertIn("年干",output["sections"][0]["text"])
        self.assertIn("乾六宫",output["reading_text"])
        self.assertIn("九星、八门俱伏吟",output["reading_text"])
        self.assertNotIn("病星受宫制",output["reading_text"])
        self.assertNotIn("门门迫",output["reading_text"])
    def test_offline_no_network_no_gpt_stable_render_and_fixed_template_loaded(self):
        with patch("socket.socket",side_effect=AssertionError("NO NETWORK")):
            a=run();b=run()
        self.assertEqual(a["reading_text"].encode(),b["reading_text"].encode())
        self.assertEqual(a["audit"]["runtime_model_calls"],0)
        self.assertEqual(a["audit"]["runtime_network_calls"],0)
        self.assertTrue(a["audit"]["source_facts_retained"]==21)
        for forbidden in FORBIDDEN_CUSTOMER:
            self.assertNotIn(forbidden,a["reading_text"])
        import src.wengua.health_severity_v26 as module
        with tempfile.TemporaryDirectory() as folder:
            base=json.loads(module.TEMPLATE.read_text("utf8"))
            base["sections"][0]["format"]="依据古籍，校验标记：（{patient_label}）。"
            temp=Path(folder)/"test_template.json"
            temp.write_text(json.dumps(base,ensure_ascii=False),"utf8")
            with patch.object(module,"TEMPLATE",temp):
                changed=run()
            self.assertIn("校验标记：（本人）",changed["sections"][0]["text"])
            self.assertNotIn("校验标记",a["reading_text"])
    def test_final_traditional_not_actual_medical(self):
        x=run()
        verdict=x["audit"]["tradition_binary_verdict"]
        self.assertIn(verdict["verdict"],("病吉","病凶"))
        self.assertEqual(verdict["verdict"],"病凶")
        self.assertTrue(verdict["not_a_real_medical_risk_grade"])
        self.assertFalse(x["audit"]["medical_severity_verified"])
        self.assertEqual(len(x["audit"]["24_factor_statuses"]),24)
        self.assertEqual(x["status"],"software_test_not_user_content_acceptance")
        self.assertIn("传统主判：病凶",x["sections"][-1]["text"])
        self.assertNotIn("必死",x["reading_text"])
    def test_four_other_health_subdomains_remain_unreviewed(self):
        old=run()
        cal={"year_ganzhi":"丙午","month_ganzhi":"戊戌","day_ganzhi":"戊辰","hour_ganzhi":"庚申"}
        for intent in ("treatment","discharge","surgery","travel_for_treatment"):
            with self.assertRaises(ValueError):
                analyze_health_severity_v26(chart=old["test_receipt"]["chart"],
                    inquiry={"intent":intent,"relationship":"self","consultation_context":"direct_self"},
                    calendar=cal,db_path=PARENT_DB)
    def test_print_unedited_real_offline_user_output(self):
        x=run()
        print("\nWENGUA_REAL_GENGSHEN_V26_BEGIN")
        for i,section in enumerate(x["sections"],1):
            print("SECTION_%02d "%i+section["title"]+"："+section["text"])
        print("AUDIT="+json.dumps({
            "verdict":x["audit"]["tradition_binary_verdict"],
            "fuyin_fanyin":x["audit"]["fuyin_fanyin"],
            "inner_outer":[x["audit"]["illness_inner_outer"],x["audit"]["patient_inner_outer"]],
            "source_name":x["audit"]["pair_original_still_auditable"]["name"],
            "production_type":x["audit"]["render_mode"]
        },ensure_ascii=False))
        print("WENGUA_REAL_GENGSHEN_V26_END")

if __name__=="__main__":
    unittest.main()
