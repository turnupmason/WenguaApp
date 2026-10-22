"""Pre-disclosure replay of two NEW book families using genuine V3.1 engine.

No model trained on an original author's answer may claim clean, independent
blind-test validation; these are historical-source retrospective predictions.
"""
from __future__ import annotations
import hashlib,json,unittest
from unittest.mock import patch
from scripts.replay_two_new_historical_health_v32 import evaluate,PARENT_SHA,DB,CASES

class SourceFamilyV32HistoricalCheck(unittest.TestCase):
    def test_exact_latest_v31_complete_parent_and_original_family_split(self):
        self.assertTrue(DB.is_file())
        self.assertEqual(hashlib.sha256(DB.read_bytes()).hexdigest(),PARENT_SHA)
        r=evaluate()
        self.assertEqual(len(r["samples"]),2)
        self.assertEqual(len({x["family_id"] for x in r["samples"]}),2)
        self.assertEqual({x["family_id"] for x in r["samples"]},
          {"shenqi.health.19960316.self_surgery","shenqi.health.19960727.father_illness"})
        self.assertFalse(r["original_book_conclusions_loaded"])
        self.assertFalse(r["old_evaluation_families_reused"])
    def test_original_centre_5_head_hour_uses_only_source_attested_kun_host(self):
        from src.wengua.casting_shenqi import layout_from_explicit_bureau
        from src.wengua.health_severity_v25 import fuyin_fanyin_facts
        q=layout_from_explicit_bureau(dun="yin",ju=7,hour_ganzhi="甲申")
        self.assertEqual(q["xun_shou"],"甲申")
        self.assertEqual(q["xun_start_palace"],5)
        self.assertEqual(q["value_star"],"天禽星")
        self.assertEqual(q["value_star_palace"],2)
        self.assertEqual(q["value_door"],"死门")
        self.assertEqual(q["value_door_palace"],2)
        self.assertTrue(fuyin_fanyin_facts(q)["both_fuyin"])
        # Previously blocked unknown NONZERO centre routes stay blocked.
        with self.assertRaisesRegex(ValueError,"centre 5"):
            layout_from_explicit_bureau(dun="yang",ju=1,hour_ganzhi="戊辰")
    def test_actual_calendar_charts_and_original_value_symbols_match(self):
        for x in evaluate()["samples"]:
            self.assertEqual(x["full_chart"]["hour_ganzhi"],x["four_pillars"]["hour"])
            self.assertEqual(x["original_given_bureau"]["ju"],x["full_chart"]["ju"])
            self.assertEqual(x["original_given_bureau"]["dun"],x["full_chart"]["dun"])
            self.assertEqual(x["value_star"],x["full_chart"]["value_star"])
            self.assertEqual(x["value_door"],x["full_chart"]["value_door"])
            self.assertEqual(len(x["text_sha256"]),64)
    def test_initial_patient_context_does_not_use_later_birth_or_surgery_answer(self):
        a,b=evaluate()["samples"]
        self.assertEqual(a["relation"],"self")
        self.assertIsNone(a["sex"])
        self.assertEqual(b["relation"],"father")
        self.assertEqual(b["sex"],"male")
        self.assertFalse(a["birth_year_supplied_pre_question"])
        self.assertNotIn("1943年",a["text"])
        self.assertNotIn("1991年",a["text"])
        self.assertNotIn("既往手术已经确诊",a["text"])
        self.assertIn("乾六宫",b["text"])
        self.assertIn("年干",b["text"])
    def test_same_genuine_11_section_fixed_offline_template_no_gpt(self):
        with patch("socket.socket",side_effect=AssertionError("Network forbidden")):
            a=evaluate();b=evaluate()
        self.assertEqual([x["text"].encode() for x in a["samples"]],
                         [x["text"].encode() for x in b["samples"]])
        for x in a["samples"]:
            self.assertIn(x["verdict"],("病吉","病凶"))
            self.assertEqual(x["text_sha256"],hashlib.sha256(x["text"].encode()).hexdigest())
            self.assertNotIn("GPT",x["text"])
            self.assertNotIn("模型",x["text"])
            self.assertNotIn("数据库",x["text"])
            self.assertFalse(x["original_author_outcome_used"])
            self.assertEqual(x["patient_review"],"pending")
            self.assertTrue(x["not_a_clinical_diagnosis"])
    def test_severity_only_do_not_change_other_intents(self):
        r=evaluate()
        for x in r["samples"]:
            self.assertEqual(x["live_engine"],"analyze_health_severity_v31")
        self.assertTrue(r["pure_python_no_gpt"])
    def test_print_original_generated_chinese_unmodified_for_user_review(self):
        r=evaluate()
        print("\nV32_TWO_FRESH_FAMILY_SEAL_BEGIN")
        for i,x in enumerate(r["samples"],1):
            print(f"FAMILY_{i}_ID="+x["family_id"])
            print(f"FAMILY_{i}_PILLARS="+json.dumps(x["four_pillars"],ensure_ascii=False))
            print(f"FAMILY_{i}_SHA256="+x["text_sha256"])
            print(f"FAMILY_{i}_VERDICT="+x["verdict"])
            print(f"FAMILY_{i}_START")
            print(x["text"])
            print(f"FAMILY_{i}_END")
        print("V32_TWO_FRESH_FAMILY_SEAL_END")

if __name__=="__main__":unittest.main()
