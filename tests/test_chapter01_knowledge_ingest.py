import hashlib
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest

from src.wengua.chapter_ingest import DEFAULT_CHAPTER, register_chapter_knowledge
from src.wengua.database import connect


class FirstCastingChapterDatabaseTests(unittest.TestCase):
    def test_import_32_metadata_records_and_idempotency(self):
        with tempfile.TemporaryDirectory() as td:
            db=Path(td)/"wengua.sqlite3"
            first=register_chapter_knowledge(db)
            self.assertEqual(first["extracted_counts"],
                {"foundation":12,"casting_procedure":17,"casting_example":3})
            self.assertEqual(first["stored_entries"],32)
            self.assertEqual(first["approved_casting_rules"],0)
            self.assertEqual(first["source_status"],"metadata_only_original_not_in_db")
            again=register_chapter_knowledge(db)
            self.assertEqual(again["stored_entries"],32)
            with connect(db) as con:
                self.assertEqual(con.execute("SELECT COUNT(*) FROM chapter_knowledge").fetchone()[0],1)
                self.assertEqual(con.execute("SELECT COUNT(*) FROM casting_knowledge_entries").fetchone()[0],32)
                self.assertEqual(con.execute("SELECT COUNT(*) FROM sections").fetchone()[0],0)
                self.assertEqual(con.execute("SELECT COUNT(*) FROM rules").fetchone()[0],0)
                self.assertEqual(con.execute("SELECT COUNT(*) FROM casting_knowledge_entries WHERE approval_state='approved'").fetchone()[0],0)

    def test_raw_source_hash_protection(self):
        with tempfile.TemporaryDirectory() as td:
            db=Path(td)/"wengua.sqlite3"
            bogus=Path(td)/"private.txt"
            bogus.write_text("This is not the uploaded chapter",encoding="utf-8")
            with self.assertRaisesRegex(ValueError,"SHA256"):
                register_chapter_knowledge(db,source_file=bogus)
            self.assertFalse(db.exists())

    def test_released_metadata_contains_no_long_original_text(self):
        manifest=json.loads((DEFAULT_CHAPTER/"chapter_manifest.json").read_text())
        self.assertEqual(manifest["source_utf8_bytes"],26691)
        self.assertEqual(manifest["source_sha256"],
            "177f6ecba2bf4c165524a48adbdab8fdbd535cdb700dca12b5e5f29b1a75afb2")
        self.assertFalse(manifest["original_text_publicly_released"])
        self.assertEqual(manifest["prediction_event_families"],0)
        self.assertEqual(manifest["cast_examples"],
                         {"full_text_reconstructed":2,"partial_supplementary":1})
        for name in ("foundation.json","casting_rules.json","casting_examples.json"):
            raw=(DEFAULT_CHAPTER/name).read_bytes()
            self.assertLess(len(raw),30000)

if __name__=="__main__":
    unittest.main()
