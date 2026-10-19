"""Prevent a new conversation from losing pregnancy data or prior health user policy."""
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
SHA="51af5117a1390f8af44e27c70fde83722d5df98d9c517e303a1dde7d433b5b9e"
P=ROOT/"data/knowledge/shenqi/pregnancy_prediction_ch03"
H=ROOT/"data/knowledge/shenqi/health_prediction_ch01"

class LatestPregnancyHandoffTests(unittest.TestCase):
    def test_agent_status_ledger_semantics_follow_actual_source(self):
        for name in ("AGENTS.md","docs/PROJECT_STATUS.md",
                     "docs/CHAPTER_LEDGER.md","docs/SEMANTIC_KNOWLEDGE_MODEL.md"):
            with self.subTest(path=name):
                text=(ROOT/name).read_text(encoding="utf-8")
                self.assertIn("怀孕分娩",text)
                self.assertIn(SHA,text)
                self.assertIn("7章",text)
                self.assertIn("健康",text)
        doc=(ROOT/"docs/PREGNANCY_CASE_REASONING_PROTOCOL.md").read_text(encoding="utf-8")
        self.assertIn(SHA,doc)
        self.assertIn("拿不准",doc)
        self.assertIn("CASE_OUTCOME_POLICY.md",doc)

    def test_six_full_cases_methods_and_per_source_validation(self):
        m=json.loads((P/"chapter_manifest.json").read_text(encoding="utf-8"))
        c=json.loads((P/"case_index.json").read_text(encoding="utf-8"))
        d=json.loads((P/"method_index.json").read_text(encoding="utf-8"))
        a=json.loads((P/"source_audit.json").read_text(encoding="utf-8"))
        self.assertEqual((m["source_lines"],m["source_utf8_bytes"]),(313,28082))
        self.assertEqual(m["source_sha256"],SHA)
        self.assertEqual(c["source_sha256"],SHA)
        self.assertEqual(d["source_sha256"],SHA)
        self.assertEqual(a["source_sha256"],SHA)
        self.assertEqual(len(c["cases"]),6)
        self.assertEqual(len(d["methods"]),24)
        self.assertEqual(len({z["event_family_id"] for z in c["cases"]}),6)
        self.assertEqual(sum(len(z["numbered_author_step_lines"]) for z in c["cases"]),23)
        for z in c["cases"]:
            self.assertEqual(z["raw_nine_palace_rows"][1]-z["raw_nine_palace_rows"][0],8)
            self.assertTrue(z["validation_information_lines"])
            self.assertEqual(z["book_outcome_label"],"author_book_success_default")
            self.assertIs(z["author_explicit_error_admission"],False)
            self.assertEqual(z["independent_external_verification"],"not_verified")
        self.assertNotEqual(c["cases"][0]["casting"]["local_date"],c["cases"][1]["casting"]["local_date"])
        self.assertEqual(c["cases"][0]["linked_event_family"],c["cases"][1]["linked_event_family"])

    def test_health_six_cases_are_retroactively_fully_one_shot_validated(self):
        c=json.loads((H/"case_index.json").read_text(encoding="utf-8"))
        expected={1:[24,26,28],2:[108,109],3:[148,154],4:[197],5:[243],6:[288,289,290]}
        self.assertEqual(len(c["cases"]),6)
        for z in c["cases"]:
            self.assertEqual(z["validation_information_lines"],expected[z["index"]])
            self.assertTrue(z["single_one_shot_reading"])
            self.assertEqual(z["book_outcome_label"],"author_book_success_default")
            self.assertTrue(z["no_independent_multiturn_predictions"])
        s=(ROOT/"src/wengua/compile_shenqi_pregnancy.py").read_text(encoding="utf-8")
        self.assertIn("def retroactively_sync_health_book_validation",s)
        self.assertIn("same_event_book_validation",s)
        self.assertIn("single_answer_for_one_cast",s)

    def test_complete_current_files_are_accessible_to_next_agent(self):
        for path in (
          "docs/CASE_OUTCOME_POLICY.md",
          "data/knowledge/shenqi/pregnancy_prediction_ch03/chapter_manifest.json",
          "data/knowledge/shenqi/pregnancy_prediction_ch03/case_index.json",
          "data/knowledge/shenqi/pregnancy_prediction_ch03/method_index.json",
          "data/knowledge/shenqi/pregnancy_prediction_ch03/source_audit.json",
          "scripts/import_shenqi_pregnancy.py",
          "src/wengua/compile_shenqi_pregnancy.py",
          "tests/test_pregnancy_case_import.py"):
            self.assertTrue((ROOT/path).is_file(),path)

if __name__=="__main__":
    unittest.main()
