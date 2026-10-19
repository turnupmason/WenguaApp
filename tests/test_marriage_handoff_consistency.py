"""Gate latest six-chapter cross-conversation handoff and user's book-success policy."""
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
SHA="64c7e9c1c0e646814c11644809277f71587d21736bdbd49679e6ad65611303c9"
MAR=ROOT/"data/knowledge/shenqi/marriage_prediction_ch02"
HLT=ROOT/"data/knowledge/shenqi/health_prediction_ch01"

class LatestHandoffTests(unittest.TestCase):
    def test_agent_status_ledger_are_updated_no_failed_file(self):
        for p in ("AGENTS.md","docs/PROJECT_STATUS.md","docs/CHAPTER_LEDGER.md"):
            txt=(ROOT/p).read_text(encoding="utf-8")
            with self.subTest(path=p):
                self.assertIn("6章",txt)
                self.assertIn(SHA,txt)
                self.assertIn("CASE_OUTCOME_POLICY.md",txt)
                self.assertIn("恋爱婚姻预测",txt)
        policy=(ROOT/"docs/CASE_OUTCOME_POLICY.md").read_text(encoding="utf-8")
        self.assertIn("author_book_success_default",policy)
        self.assertIn("author_book_error_explicit",policy)
        self.assertIn("single",policy)
        self.assertIn("一次",policy)
        self.assertIn("CASE_OUTCOME_POLICY.md",
            (ROOT/"docs/CHAPTER_WORKFLOW.md").read_text(encoding="utf-8"))
        self.assertTrue((ROOT/"docs/MARRIAGE_CASE_REASONING_PROTOCOL.md").exists())

    def test_exact_metadata_source_and_six_books_are_success_by_default(self):
        a=json.loads((MAR/"chapter_manifest.json").read_text(encoding="utf-8"))
        b=json.loads((MAR/"case_index.json").read_text(encoding="utf-8"))
        c=json.loads((MAR/"method_index.json").read_text(encoding="utf-8"))
        h=json.loads((HLT/"case_index.json").read_text(encoding="utf-8"))
        self.assertEqual(a["source_sha256"],SHA)
        self.assertEqual((a["source_utf8_bytes"],a["source_lines"]),(35777,367))
        self.assertEqual((a["complete_original_text_events"],a["nine_palace_literal_cells"],
                          a["author_numbered_analysis_steps"]),(6,54,23))
        self.assertEqual(b["source_sha256"],SHA)
        self.assertEqual(len(b["cases"]),6)
        self.assertEqual(len(c["author_method_candidates"]),18)
        self.assertEqual(sum(len(x["author_numbered_step_lines"]) for x in b["cases"]),23)
        self.assertEqual(len({x["event_family_id"] for x in b["cases"]}),6)
        for x in b["cases"]+h["cases"]:
            self.assertEqual(x["book_outcome_label"],"author_book_success_default")
            self.assertIs(x["book_explicit_failure_or_correction"],False)
            self.assertEqual(x["independent_external_verification"],"not_verified")
        self.assertEqual(len(h["cases"]),6)
        self.assertTrue(b["cases"][-1]["casting"]["original_1997_call_has_no_full_chart"])
        for rel in ("src/wengua/compile_shenqi_marriage.py","src/wengua/book_case_retrieval.py",
                    "src/wengua/book_verdict_sync.py","scripts/sync_author_book_verdicts.py",
                    "schema/migrations/005_book_case_verdicts.sql","tests/test_marriage_case_import.py"):
            self.assertTrue((ROOT/rel).exists(),rel)

if __name__=="__main__":unittest.main()
