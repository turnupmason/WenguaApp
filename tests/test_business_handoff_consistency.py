"""Mandatory tenth-chapter source ledger, 14-event /16-cast cross-chat handoff gate."""
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
SHA="c955d56bc7deb1b5c4a99f5b2594625d3d7f690e60063eed10f55864b514698c"
D=ROOT/"data/knowledge/shenqi/business_profit_prediction_ch06"

class BusinessHandoffTests(unittest.TestCase):
    def test_agent_status_ledger_source_and_latest_totals(self):
        for path in ("AGENTS.md","docs/PROJECT_STATUS.md",
                     "docs/CHAPTER_LEDGER.md","docs/SEMANTIC_KNOWLEDGE_MODEL.md"):
            with self.subTest(path=path):
                s=(ROOT/path).read_text(encoding="utf-8")
                for pattern in (SHA,"10章","经营求财","42","652"):
                    self.assertIn(pattern,s)
        for path in ("docs/CASE_OUTCOME_POLICY.md",
                     "docs/BUSINESS_CASE_REASONING_PROTOCOL.md",
                     "docs/CHAPTER_WORKFLOW.md"):
            self.assertTrue((ROOT/path).is_file(),path)
        doc=(ROOT/"docs/BUSINESS_CASE_REASONING_PROTOCOL.md").read_text(encoding="utf-8")
        self.assertIn(SHA,doc)
        self.assertIn("16张",doc)
        self.assertIn("一事",doc)

    def test_original_source_indexes_and_uninvented_casts(self):
        idx=json.loads((D/"case_index.json").read_text(encoding="utf-8"))
        methods=json.loads((D/"method_index.json").read_text(encoding="utf-8"))
        manifest=json.loads((D/"chapter_manifest.json").read_text(encoding="utf-8"))
        audit=json.loads((D/"source_audit.json").read_text(encoding="utf-8"))
        for j in (idx,methods,manifest,audit):
            self.assertEqual(j["source_sha256"],SHA)
        self.assertEqual((manifest["source_lines"],manifest["source_utf8_bytes"]),(717,67599))
        self.assertEqual((manifest["event_families"],manifest["complete_nine_palace_casts"],
                          manifest["original_literal_palace_cells"]),(14,16,144))
        self.assertEqual((len(idx["cases"]),len(methods["methods"])),(14,81))
        self.assertEqual(len({m["concept_id"] for m in methods["methods"]}),81)
        self.assertEqual(sum(len(c["numbered_or_explicit_analysis_ranges"]) for c in idx["cases"]),59)
        self.assertEqual(sum(len(c["chart_source_starts"]) for c in idx["cases"]),16)
        self.assertEqual(idx["cases"][11]["chart_source_starts"],[555,585,614])
        self.assertEqual(idx["cases"][9]["numbered_or_explicit_analysis_ranges"],
                          [[502,502],[504,504],[506,506]])
        for c in idx["cases"]:
            self.assertEqual(c["case_id"],c["event_family_id"])
            self.assertEqual(c["book_outcome_label"],"author_book_success_default")
            self.assertEqual(c["independent_external_verification"],"not_verified")
        self.assertTrue(manifest["source_last_line_unfinished"])

    def test_real_schema_import_research_api_and_tests_exist(self):
        for p in ("schema/migrations/007_business_multi_casts.sql",
                  "src/wengua/compile_shenqi_business.py",
                  "src/wengua/business_case_retrieval.py",
                  "scripts/import_shenqi_business.py",
                  "tests/test_business_case_import.py"):
            self.assertTrue((ROOT/p).exists(),p)
        sql=(ROOT/"schema/migrations/007_business_multi_casts.sql").read_text(encoding="utf-8")
        self.assertIn("historical_case_additional_casts",sql)
        self.assertIn("historical_case_additional_cast_cells",sql)
        root=(ROOT/"src/wengua/database.py").read_text(encoding="utf-8")
        self.assertIn("007_business_multi_casts.sql",root)
        x=(ROOT/"src/wengua/compile_shenqi_business.py").read_text(encoding="utf-8")
        self.assertIn("SHA256 mismatch",x)
        self.assertIn("original",x)
        self.assertIn("59",x)
        self.assertIn("16",x)

if __name__=="__main__":
    unittest.main()
