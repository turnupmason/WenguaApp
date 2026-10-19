"""CI guard: no eight-chapter deliverable without complete handoff and five real source indexes."""
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
SHA="88d641e3b2ba541e5ea2acce40cd73af28c362befbff7cbc39fb558f3d84eb43"
INDEX=ROOT/"data/knowledge/shenqi/education_prediction_ch04"

class EducationHandoffTests(unittest.TestCase):
    def test_required_agent_status_ledger_and_protocol_source_match(self):
        for path in ("AGENTS.md","docs/PROJECT_STATUS.md","docs/CHAPTER_LEDGER.md",
                     "docs/SEMANTIC_KNOWLEDGE_MODEL.md","docs/EDUCATION_CASE_REASONING_PROTOCOL.md"):
            with self.subTest(file=path):
                text=(ROOT/path).read_text(encoding="utf-8")
                self.assertIn(SHA,text)
                self.assertIn("求学考试",text)
                self.assertIn("8章",text)
        for path in ("AGENTS.md","docs/PROJECT_STATUS.md","docs/CHAPTER_LEDGER.md"):
            text=(ROOT/path).read_text(encoding="utf-8")
            self.assertIn("518",text)
            self.assertIn("23",text)
            self.assertIn("CASE_OUTCOME_POLICY.md",text)

    def test_education_full_book_events_and_no_future_case5_feedback_in_initial(self):
        meta=json.loads((INDEX/"chapter_manifest.json").read_text(encoding="utf-8"))
        cases=json.loads((INDEX/"case_index.json").read_text(encoding="utf-8"))
        methods=json.loads((INDEX/"method_index.json").read_text(encoding="utf-8"))
        audit=json.loads((INDEX/"source_audit.json").read_text(encoding="utf-8"))
        for x in (meta,cases,methods,audit):
            self.assertEqual(x["source_sha256"],SHA)
        self.assertEqual((meta["source_lines"],meta["source_utf8_bytes"]),(349,30539))
        self.assertEqual((meta["historical_event_families"],meta["original_nine_palace_rows"],
                          meta["author_numbered_reasoning_groups"]),(5,45,17))
        self.assertEqual(len(cases["cases"]),5)
        self.assertEqual(len(methods["methods"]),35)
        self.assertEqual(len({x["concept_id"] for x in methods["methods"]}),35)
        self.assertEqual(sum(len(x["reasoning_topics"]) for x in cases["cases"]),17)
        self.assertEqual(sum(len(x["author_analysis_numbered_lines"]) for x in cases["cases"]),17)
        self.assertEqual(len({x["event_family_id"] for x in cases["cases"]}),5)
        for x in cases["cases"]:
            self.assertEqual(x["original_nine_palace_row_lines"][1]-x["original_nine_palace_row_lines"][0],8)
            self.assertEqual(x["book_outcome_label"],"author_book_success_default")
            self.assertEqual(x["independent_external_verification"],"not_verified")
            self.assertTrue(x["single_answer_for_one_cast"])
        five=cases["cases"][-1]
        self.assertEqual(five["original_question_source_lines"],[264,264])
        self.assertEqual(five["retrospective_cast_source_lines"],[284,284])
        self.assertEqual(five["author_full_analysis_ranges"],
                        [[325,329],[331,335],[337,339],[341,343],[345,349]])
        self.assertIn("feedback",five["retroactive_source_view_guard"])

    def test_import_code_tests_and_source_policy_available(self):
        for rel in (
            "docs/CASE_OUTCOME_POLICY.md","docs/CHAPTER_WORKFLOW.md",
            "src/wengua/compile_shenqi_education.py",
            "scripts/import_shenqi_education.py",
            "tests/test_education_case_import.py",
            "data/knowledge/shenqi/education_prediction_ch04/case_index.json",
            "data/knowledge/shenqi/education_prediction_ch04/method_index.json",
            "docs/EDUCATION_CASE_REASONING_PROTOCOL.md"):
            self.assertTrue((ROOT/rel).is_file(),rel)
        source=(ROOT/"src/wengua/compile_shenqi_education.py").read_text(encoding="utf-8")
        self.assertIn("original_question_source_lines",source)
        self.assertIn("Case5 initial question must stop",source)
        self.assertIn("author_full_analysis_ranges",source)

if __name__=="__main__":
    unittest.main()
