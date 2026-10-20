"""For the published 14-section public SQLite archive, verify strong source lineage."""
import json,sqlite3,hashlib
from pathlib import Path
from unittest import TestCase
ROOT=Path(__file__).resolve().parents[1]
class ArchiveCaseTests(TestCase):
    def test_manifest_and_source_count(self):
        base=ROOT/"data/knowledge/shenqi/criminal_case_prediction_ch10"
        manifest=json.loads((base/"chapter_manifest.json").read_text(encoding="utf8"))
        cases=json.loads((base/"case_index.json").read_text(encoding="utf8"))["cases"]
        self.assertEqual((len(cases),sum(len(c["actual_book_printed_chart_starts"]) for c in cases)),(5,6))
        self.assertEqual(sum(len(c["source_author_step_lines"]) for c in cases),29)
        self.assertEqual((manifest["source_lines"],manifest["source_utf8_bytes"]),(261,37260))
        self.assertEqual(cases[3]["author_admits_initial_timing_wrong"],True)
    def test_published_sqlite_and_centre_provenance(self):
        m=json.loads((ROOT/"archives/sqlite/14chapters_71cases_manifest.json").read_text(encoding="utf8"))
        db=ROOT/m["published_github_public_path"]
        self.assertEqual(hashlib.sha256(db.read_bytes()).hexdigest(),m["sha256"])
        with sqlite3.connect(db) as c:
            self.assertEqual(c.execute("PRAGMA integrity_check").fetchone()[0],"ok")
            self.assertEqual(c.execute("PRAGMA foreign_key_check").fetchall(),[])
            self.assertEqual(c.execute("SELECT count(*) FROM cases").fetchone()[0],71)
            self.assertEqual(c.execute("SELECT count(*) FROM historical_palace_standardization").fetchone()[0],684)
            self.assertEqual(c.execute("SELECT count(*) FROM historical_palace_standardization WHERE palace=5 and derived_host_palace=2").fetchone()[0],76)
            self.assertEqual(c.execute("SELECT count(*) FROM historical_case_reasoning_trace").fetchone()[0],319)
            self.assertEqual(c.execute("SELECT count(*) FROM historical_outcome_reclassification_audit").fetchone()[0],1)
            self.assertEqual(c.execute("SELECT count(*) FROM historical_case_book_verdicts WHERE verdict='author_book_error_explicit'").fetchone()[0],4)
            self.assertEqual(c.execute("SELECT count(*) FROM historical_case_additional_cast_cells").fetchone()[0],45)
