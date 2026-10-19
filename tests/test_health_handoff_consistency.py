import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
SOURCE="3f9a01be996e6230c73cc7df27f00c11134f9308e4115cf934f59fead6de0e3a"
D=ROOT/"data/knowledge/shenqi/health_prediction_ch01"

class HealthHandoffGate(unittest.TestCase):
    def test_current_agent_status_ledger_and_model_are_updated(self):
        for p in ("AGENTS.md","docs/PROJECT_STATUS.md","docs/CHAPTER_LEDGER.md",
                  "docs/SEMANTIC_KNOWLEDGE_MODEL.md",
                  "docs/HEALTH_CASE_REASONING_PROTOCOL.md"):
            with self.subTest(path=p):
                text=(ROOT/p).read_text(encoding="utf-8")
                self.assertIn(SOURCE,text)
                self.assertIn("人体疾病预测",text)
        for p in ("AGENTS.md","docs/PROJECT_STATUS.md","docs/CHAPTER_LEDGER.md"):
            self.assertIn("5章",(ROOT/p).read_text(encoding="utf-8"))

    def test_chapter_manifest_and_full_family_source_consistency(self):
        m=json.loads((D/"chapter_manifest.json").read_text(encoding="utf-8"))
        cases=json.loads((D/"case_index.json").read_text(encoding="utf-8"))
        idx=json.loads((D/"method_index.json").read_text(encoding="utf-8"))
        audit=json.loads((D/"source_audit.json").read_text(encoding="utf-8"))
        self.assertEqual(m["source_sha256"],SOURCE)
        self.assertEqual(m["source_lines"],298)
        self.assertEqual(m["source_utf8_bytes"],34625)
        self.assertEqual((m["case_families"],m["source_nine_palace_cells"],
                         m["author_numbered_reasoning_steps"]),(6,54,29))
        self.assertEqual(cases["file_source_sha256"],SOURCE)
        self.assertEqual(len(cases["cases"]),6)
        self.assertEqual(sum(len(c["steps"]) for c in cases["cases"]),29)
        self.assertEqual(idx["source_sha256"],SOURCE)
        self.assertEqual((len(idx["body_palace_mappings"]),len(idx["yongshen_rules"]),
                         len(idx["author_workflow_nodes"])),(8,14,8))
        self.assertEqual(audit["source_sha256"],SOURCE)
        self.assertTrue(all(c["event_family_id"]==c["id"] for c in cases["cases"]))
        self.assertTrue(all(c["case_split"].startswith("unassigned") for c in cases["cases"]))
        for p in ("src/wengua/compile_shenqi_health_cases.py","src/wengua/health_research.py",
                  "schema/migrations/004_health_case_evidence.sql",
                  "scripts/import_shenqi_health.py","tests/test_health_case_import.py"):
            self.assertTrue((ROOT/p).is_file(),p)

if __name__=="__main__":
    unittest.main()
