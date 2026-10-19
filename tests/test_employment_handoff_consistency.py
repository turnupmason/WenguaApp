"""Gate latest original chapter data and persistent AGENTS cross-chat handoff."""
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
SOURCE="b78ab538a090cc8f59474b49bac613318e130dd78a563929b097ac6922e7fa05"
D=ROOT/"data/knowledge/shenqi/employment_prediction_ch05"

class EmploymentHandoffTests(unittest.TestCase):
    def test_agent_project_status_and_ledger_all_current(self):
        for name in ("AGENTS.md","docs/PROJECT_STATUS.md","docs/CHAPTER_LEDGER.md"):
            with self.subTest(path=name):
                s=(ROOT/name).read_text(encoding="utf-8")
                for needle in (SOURCE,"9章","28","571","工作就业","CASE_OUTCOME_POLICY.md"):
                    self.assertIn(needle,s)
        for p in ("docs/EMPLOYMENT_CASE_REASONING_PROTOCOL.md",
                  "docs/SEMANTIC_KNOWLEDGE_MODEL.md",
                  "docs/CHAPTER_WORKFLOW.md"):
            self.assertIn(SOURCE,(ROOT/p).read_text(encoding="utf-8"))

    def test_five_complete_cases_method_counts_and_original_source_pointers(self):
        files={n:json.loads((D/(n+".json")).read_text(encoding="utf-8"))
               for n in ("chapter_manifest","case_index","method_index","source_audit")}
        for n,d in files.items():
            self.assertEqual(d["source_sha256"],SOURCE,n)
        manifest=files["chapter_manifest"]
        self.assertEqual((manifest["source_lines"],manifest["source_utf8_bytes"]),(228,25748))
        self.assertEqual((manifest["case_families"],manifest["source_raw_palace_cells"],
                          manifest["author_or_student_numbered_steps"]),(5,45,20))
        idx=files["case_index"]
        self.assertEqual(len(idx["cases"]),5)
        self.assertEqual(sum(len(x["step"]) for x in idx["cases"]),20)
        self.assertEqual(len(files["method_index"]["methods"]),53)
        self.assertEqual(len({x["concept_id"] for x in files["method_index"]["methods"]}),53)
        for event in idx["cases"]:
            self.assertEqual(event["case_id"],event["event_family_id"])
            self.assertEqual(event["book_outcome_label"],"author_book_success_default")
            self.assertEqual(event["independent_external_verification"],"not_verified")
            self.assertEqual(len(event["chart_source_groups"]),3)
            self.assertTrue(all(b-a==3 for a,b in event["chart_source_groups"]))
            self.assertEqual(len(event["step"]),len(event["topics"]))

    def test_single_cast_multiple_candidates_and_unsupplied_other_four(self):
        idx=json.loads((D/"case_index.json").read_text(encoding="utf-8"))
        second,fourth,fifth=idx["cases"][1],idx["cases"][3],idx["cases"][4]
        self.assertEqual(second["step"][-1],[95,95])
        self.assertEqual(fourth["step"],[[173,177],[179,181]])
        self.assertTrue(any("其他四" in note for note in fourth["notes"]))
        ranked=idx["candidate_ranking"]
        self.assertEqual(ranked["case_id"],fifth["case_id"])
        self.assertEqual(ranked["predicted_top_k"],2)
        self.assertEqual(ranked["reported_full_ranks"],5)
        self.assertEqual(len(ranked["candidates"]),5)
        self.assertEqual(sorted(x["author_predicted_rank"] for x in ranked["candidates"]
                                if x["author_predicted_rank"] is not None),[1,2])
        self.assertEqual(sorted(x["reported_final_rank"] for x in ranked["candidates"]),[1,2,3,4,5])

    def test_shared_database_migration_and_import_tests_really_exist(self):
        for path in (
            "schema/migrations/006_employment_ranked_candidates.sql",
            "src/wengua/compile_shenqi_employment.py",
            "scripts/import_shenqi_employment.py",
            "tests/test_employment_case_import.py",
            "docs/EMPLOYMENT_CASE_REASONING_PROTOCOL.md",
            "data/knowledge/shenqi/employment_prediction_ch05/source_audit.json"):
            self.assertTrue((ROOT/path).is_file(),path)
        sql=(ROOT/"schema/migrations/006_employment_ranked_candidates.sql").read_text(encoding="utf-8")
        self.assertIn("historical_event_candidates",sql)
        self.assertIn("historical_case_source_segments",sql)
        db=(ROOT/"src/wengua/database.py").read_text(encoding="utf-8")
        self.assertIn("006_employment_ranked_candidates.sql",db)

if __name__=="__main__":
    unittest.main()
