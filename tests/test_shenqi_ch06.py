import hashlib
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from src.wengua import compile_shenqi_ch06 as importer
from src.wengua.ch06_knowledge import (
    source_index,count_units,yin_yang_inner_outer,horizontal_between_palaces,
    vertical_star_palace,five_no_encounter,host_guest_hour,
    yongshen_candidates,timing_candidate_requirements
)
from src.wengua.database import connect

class ChapterSixKnowledgeTests(unittest.TestCase):
    def test_source_index_and_count_units_are_not_repeat_claim(self):
        idx=source_index()
        self.assertEqual(idx["method_count"],20)
        self.assertEqual(idx["role_count"],68)
        self.assertEqual(idx["timing_count"],14)
        self.assertEqual(idx["five_no_encounter_count"],10)
        self.assertEqual(len(importer._entries(idx)),112)
        self.assertEqual(count_units()["state_keys"],1080)
        self.assertEqual(count_units()["palace_records"],8640)
        self.assertEqual(count_units()["repeated_full_charts_claim"],"not_established")

    def test_yin_yang_inner_outer_same_palace_opposite(self):
        self.assertEqual(yin_yang_inner_outer("yang",1)["zone"],"inner")
        self.assertEqual(yin_yang_inner_outer("yin",1)["zone"],"outer")
        self.assertEqual(yin_yang_inner_outer("yin",9)["speed"],"fast")
        self.assertEqual(yin_yang_inner_outer("yang",9)["speed"],"slow")
        self.assertEqual(yin_yang_inner_outer("yang",5)["status"],"unresolved_center_palace")

    def test_cross_palace_relation_never_uses_intrinsic_stem(self):
        result=horizontal_between_palaces(6,3)
        self.assertEqual(result["relation"],"a_controls_b")  # 金克木
        self.assertIn("palace_elements_not_intrinsic",result["based_on"])
        self.assertEqual(horizontal_between_palaces(2,8)["relation"],"equal")
        self.assertEqual(vertical_star_palace("天心星",3)["relation"],"a_controls_b")
        with self.assertRaises(ValueError):
            horizontal_between_palaces(1,10)

    def test_five_no_encounter_ten_pairs_and_guest_hour(self):
        for item in source_index()["five_no_encounter"]:
            self.assertTrue(five_no_encounter(item["day_stem"],item["hour_ganzhi"])["is_five_no_encounter"])
        self.assertFalse(five_no_encounter("甲","甲子")["is_five_no_encounter"])
        self.assertEqual(host_guest_hour("甲子")["preferred_traditional_role"],"guest")
        self.assertEqual(host_guest_hour("己巳")["preferred_traditional_role"],"host")
        with self.assertRaises(ValueError):five_no_encounter("丁","unknown")

    def test_primary_person_is_not_all_relatives_at_once(self):
        parent=yongshen_candidates("health","father")
        self.assertEqual(parent["subject_symbols"],["stem:年干","trigram:乾"])
        self.assertEqual(parent["questioner_symbol"],"stem:日干")
        self.assertEqual(yongshen_candidates("health","child")["subject_symbols"],["stem:时干"])
        self.assertEqual(yongshen_candidates("health","colleague")["subject_symbols"],["stem:月干"])
        self.assertEqual(yongshen_candidates("marriage","friend")["status"],
                         "needs_explicit_subject_relationship")
        born=yongshen_candidates("health","self",birth_year_known=True)
        self.assertIn("stem:年命",born["reference_symbols"])

    def test_timing_requires_full_context_never_invents_date(self):
        a=timing_candidate_requirements(set())
        self.assertEqual(len(a["methods"]),14)
        self.assertTrue(all(x["missing"] for x in a["methods"]))
        self.assertIsNone(a["specific_calendar_date"])
        b=timing_candidate_requirements({"yongshen","stem_growth_stage","season"})
        selected=next(i for i in b["methods"] if i["concept_id"]=="timing:yongshen_birth_growth")
        self.assertTrue(selected["requirements_satisfied"])
        self.assertFalse(selected["approved_for_specific_date"])

    def test_source_guard_prevents_wrong_file_touching_database(self):
        with tempfile.TemporaryDirectory() as tmp:
            f=Path(tmp)/"wrong.txt";f.write_text("not chapter 6")
            db=Path(tmp)/"db.sqlite3"
            with self.assertRaisesRegex(ValueError,"SHA256 mismatch"):
                importer.import_chapter6(db,f)
            self.assertFalse(db.exists())

    def test_private_append_preserves_existing_sections_and_feedback_separation(self):
        # Synthetic source, NOT the user copyrighted original, and never
        # committed after applying patches. This tests the exact DB process.
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            lines=[""]*240
            lines[0]="第六章"
            lines[1]="奇门遁甲应用概述"
            lines[205]="第五节奇门定应期的主要方法"
            lines[31]="该事的事前公共公告"
            lines[33]="排盘作者所见的部分证据"
            lines[35]="作者预测，不可混入事前"
            lines[37]="后来结果，不能用于事前判断"
            original="\n".join(lines)+"\n"
            p=root/"case.txt";p.write_text(original,encoding="utf-8")
            digest=hashlib.sha256(p.read_bytes()).hexdigest()
            idx=json.loads(json.dumps(source_index(),ensure_ascii=False))
            idx["source_sha256"]=digest
            case={"source_sha256":digest,"events":[{
                "event_family_id":"ch06.synthetic.1995",
                "complete_nine_palace_chart":False,
                "eligible_as_sealed_independent_test":False,
                "source_lines":{"prior_news":[32,32],"known_time_and_casting":[34,34],
                                "author_prediction":[36,36],"later_result":[38,38]}}]}
            case_path=root/"cases.json"
            case_path.write_text(json.dumps(case,ensure_ascii=False),encoding="utf-8")
            db=root/"local.sqlite3"
            with patch.object(importer,"EXPECTED_SHA",digest), \
                 patch.object(importer,"source_index",return_value=idx), \
                 patch.object(importer,"PUBLIC_CASE",case_path):
                first=importer.import_chapter6(db,p)
                second=importer.import_chapter6(db,p)
            self.assertEqual(first["indexed_assertions"],112)
            self.assertEqual(second["indexed_assertions"],112)
            self.assertEqual(first["incomplete_historical_cases"],1)
            with connect(db) as con:
                self.assertEqual(con.execute("SELECT COUNT(*) FROM sections").fetchone()[0],1)
                self.assertEqual(con.execute("SELECT COUNT(*) FROM semantic_assertions").fetchone()[0],112)
                row=con.execute("""SELECT prior_known_text,author_prediction_text,
                       after_event_feedback_text,approved_for_blind_test
                       FROM incomplete_historical_cases""").fetchone()
                self.assertNotIn("后来结果",row[0])
                self.assertIn("作者预测",row[1])
                self.assertIn("后来结果",row[2])
                self.assertEqual(row[3],0)
                self.assertEqual(con.execute("SELECT COUNT(*) FROM rules WHERE status='approved'").fetchone()[0],0)

if __name__=="__main__":
    unittest.main()
