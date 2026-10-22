"""New approved-shape 11-section offline health test, self Gengshen fixture."""
from __future__ import annotations
import unittest
from unittest.mock import patch
from pathlib import Path
from scripts.run_self_health_20261021_gengshen_v26 import run,PARENT_DB,PILLARS
from src.wengua.health_severity_v26 import (
    analyze_health_severity_v26,fuyin_fanyin_facts,FORBIDDEN_CUSTOMER)
from src.wengua.casting_shenqi import layout_from_explicit_bureau


class SelfGengshenHealthV26(unittest.TestCase):
    def test_real_calendar_self_role_and_observed_four_pillars(self):
        r=run()
        self.assertEqual(r["test_receipt"]["four_pillars"],PILLARS)
        self.assertEqual(r["schema"],"wengua_health_severity_v26_strict_fact_slots")
        self.assertEqual(r["audit"]["render_mode"],"strict_static_format_map_offline_no_GPT")
        self.assertEqual(r["test_receipt"]["solar_term"],"寒露")
        self.assertEqual(r["test_receipt"]["bureau"]["dun"],"yin")
        self.assertEqual(r["test_receipt"]["bureau"]["ju"],6)
        self.assertEqual(r["test_receipt"]["chart"]["hour_ganzhi"],"庚申")
        self.assertEqual(r["audit"]["role_binding"]["stem"],"戊")
        self.assertEqual(r["audit"]["role_binding"]["relationship"],"self")
        self.assertNotIn("父亲年干",r["reading_text"])
    def test_only_one_disease_palace_paragraph_and_no_family_placeholder(self):
        r=run()
        self.assertEqual(len(r["sections"]),10)
        self.assertEqual(len(r["audit"]["source_facts_retained"]) if
                         isinstance(r["audit"]["source_facts_retained"],list)
                         else r["audit"]["source_facts_retained"],21)
        self.assertEqual(len([s for s in r["sections"] if s["id"]=="03_ill"]),1)
        self.assertNotIn("亲属辅助宫：",r["reading_text"])
        self.assertNotIn("未提供年命",r["reading_text"])
        self.assertEqual(r["sections"][-1]["id"],"11_verdict")
        self.assertIn(r["audit"]["tradition_binary_verdict"]["verdict"],r["sections"][-1]["text"])
        self.assertIn(r["audit"]["tradition_binary_verdict"]["verdict"],("病吉","病凶"))
    def test_true_star_and_door_fuyin_fanyin_separated(self):
        r=run()
        f=r["audit"]["fuyin_fanyin"]
        self.assertEqual(len(r["test_receipt"]["chart"]["palaces"]),9)
        for key in ("star","door"):
            self.assertIn(f[key],("伏吟","反吟","非伏吟反吟"))
        self.assertIn("九星、八门均非伏吟或反吟",r["reading_text"])
        # Previous time's actual home-star/home-door example must identify both.
        old=layout_from_explicit_bureau(dun="yin",ju=6,hour_ganzhi="癸亥")
        earlier=fuyin_fanyin_facts(old)
        self.assertTrue(earlier["both_fuyin"])
        self.assertEqual(earlier["star_home"],8)
        self.assertEqual(earlier["door_home"],8)
        self.assertFalse(earlier["both_fanyin"])
    def test_offline_idempotence_no_gpt_or_engine_prose(self):
        with patch("socket.socket",side_effect=AssertionError("Network accessed")):
            a=run()
            b=run()
        self.assertEqual(a["reading_text"].encode(),b["reading_text"].encode())
        self.assertEqual(a["audit"]["runtime_model_calls"],0)
        self.assertEqual(a["audit"]["runtime_network_calls"],0)
        for forbidden in FORBIDDEN_CUSTOMER:
            self.assertNotIn(forbidden,a["reading_text"])
        for placeholder in ("（患者宫）","（吉凶）","{patient}","【待补】"):
            self.assertNotIn(placeholder,a["reading_text"])
    def test_no_other_health_intents_and_no_fake_prognosis(self):
        r=run()
        self.assertEqual(r["test_receipt"]["other_four_intents_approved"],False)
        self.assertTrue(r["test_receipt"]["not_medical_diagnosis"])
        self.assertNotIn("必死",r["reading_text"])
        self.assertNotIn("癌症",r["reading_text"])
        self.assertNotIn("手术一定成功",r["reading_text"])
        with self.assertRaises(ValueError):
            analyze_health_severity_v26(
               chart=r["test_receipt"]["chart"],
               inquiry={"intent":"treatment","relationship":"self","consultation_context":"direct_self"},
               calendar={"year_ganzhi":"丙午","month_ganzhi":"戊戌","day_ganzhi":"戊辰",
                         "hour_ganzhi":"庚申","month_branch":"戌"},db_path=PARENT_DB)
    def test_verdict_uses_genuinely_calculated_evidence(self):
        r=run()
        e=r["audit"]["tradition_binary_verdict"]
        self.assertTrue(e["favorable"] or e["unfavorable"])
        self.assertTrue(e["source_judgement_requires_user_review"])
        self.assertIn("伏吟",r["reading_text"])
        self.assertIn("病吉",r["reading_text"]) if r["audit"]["tradition_binary_verdict"]["verdict"]=="病吉" else self.assertIn("病凶",r["reading_text"])
        self.assertIn("传统缓急：偏慢",r["sections"][-1]["text"])
        self.assertIn("坎一宫的死门构成门迫",r["reading_text"])
        self.assertIn("震三宫的开门构成门迫",r["reading_text"])
        self.assertIn("天芮土克病宫水",r["reading_text"])
        self.assertNotIn("幼女奸淫",r["reading_text"])
        self.assertNotIn("门门迫",r["reading_text"])
        self.assertEqual(len(r["audit"]["24_factor_statuses"]),24)
        self.assertFalse(r["audit"]["medical_severity_verified"])
        self.assertIn("幼女奸淫",r["audit"]["pair_original_still_auditable"]["name"])
    def test_print_verbatim_real_output_and_current_chart(self):
        import json
        r=run()
        print("\nUSER_SELF_GENGSHEN_OFFLINE_V26_BEGIN")
        print("CALENDAR="+json.dumps(r["test_receipt"]["bureau"],ensure_ascii=False))
        print("CHART="+json.dumps(r["test_receipt"]["chart"],ensure_ascii=False,sort_keys=True))
        print("EVIDENCE="+json.dumps(r["audit"]["tradition_binary_verdict"],ensure_ascii=False))
        for i,item in enumerate(r["sections"],1):
            print("SECTION_%02d "%i+item["title"]+"："+item["text"])
        print("USER_SELF_GENGSHEN_OFFLINE_V26_END")


if __name__=="__main__":unittest.main()
