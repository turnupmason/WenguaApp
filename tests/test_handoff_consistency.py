"""Fail CI if a new source chapter is registered without durable agent handoff.

Old source files remain untracked due to copyright; this audit checks public
source manifest, method integrity, append-only ledger and latest status.
"""
import hashlib
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
CH="application_overview_ch06"
DATA=ROOT/"data"/"knowledge"/"shenqi"/CH
SHA="50c76ce5354d3378a842d6117f06c239bcdfe2f04786663c2e89f606d98c402e"

class ChapterHandoffTests(unittest.TestCase):
    def test_all_three_handoff_files_have_latest_source(self):
        for name in ("AGENTS.md","docs/PROJECT_STATUS.md","docs/CHAPTER_LEDGER.md"):
            with self.subTest(name=name):
                s=(ROOT/name).read_text(encoding="utf-8")
                self.assertIn("奇门遁甲应用概述",s)
                self.assertIn(SHA,s)
                self.assertIn("4章",s)
        self.assertTrue((ROOT/"docs/CH06_LINKED_REASONING_PROTOCOL.md").exists())

    def test_chapter_registry_all_referenced_files_and_draft(self):
        meta=json.loads((DATA/"chapter_manifest.json").read_text(encoding="utf-8"))
        idx=json.loads((DATA/"method_index.json").read_text(encoding="utf-8"))
        case=json.loads((DATA/"historical_cases_index.json").read_text(encoding="utf-8"))
        self.assertEqual(meta["source_sha256"],SHA)
        self.assertEqual(meta["source_lines"],240)
        self.assertEqual(meta["source_utf8_bytes"],31549)
        self.assertFalse(meta["source_publicly_committed"])
        self.assertEqual(case["source_sha256"],SHA)
        self.assertEqual(len(case["events"]),1)
        self.assertFalse(case["events"][0]["eligible_as_sealed_independent_test"])
        self.assertEqual(idx["source_sha256"],SHA)
        sets=[("method_steps","method_count",20),("yongshen_candidates","role_count",68),
              ("timing_candidates","timing_count",14),("five_no_encounter","five_no_encounter_count",10)]
        ids=[]
        for group,count,expected in sets:
            self.assertEqual(idx[count],expected)
            self.assertEqual(len(idx[group]),expected)
            for x in idx[group]:
                self.assertEqual(x["review_status"],"draft")
                ids.append(x["concept_id"])
                a,b=x["source_lines"]
                self.assertTrue(1<=a<=b<=240)
        self.assertEqual(len(ids),len(set(ids)))
        self.assertEqual(len(ids),112)
        for relative in ("src/wengua/ch06_knowledge.py",
                         "src/wengua/compile_shenqi_ch06.py",
                         "scripts/import_shenqi_ch06.py",
                         "schema/migrations/003_incomplete_historical_case_parts.sql",
                         "tests/test_shenqi_ch06.py"):
            self.assertTrue((ROOT/relative).exists(),relative)

if __name__=="__main__":
    unittest.main()
