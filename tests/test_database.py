import tempfile
from pathlib import Path
import unittest
from src.wengua.database import initialize,import_section,connect

class DBTest(unittest.TestCase):
    def test_initialize_empty_rules_two_books(self):
        with tempfile.TemporaryDirectory() as tmp:
            db=Path(tmp)/"wen.sqlite3"
            initialize(db)
            with connect(db) as con:
                self.assertEqual(con.execute("SELECT book_id FROM books ORDER BY book_id").fetchall(),
                                [("kaiwu",),("shenqi",)])
                self.assertEqual(con.execute("SELECT COUNT(*) FROM rules").fetchone()[0],0)
    def test_preserve_original_and_versions(self):
        with tempfile.TemporaryDirectory() as tmp:
            db=Path(tmp)/"wen.sqlite3"
            a=import_section(db,"shenqi","chapter1","第一章","原文第一个版本")
            b=import_section(db,"shenqi","chapter1","第一章","原文第一个版本")
            c=import_section(db,"shenqi","chapter1","第一章","原文第二个版本")
            self.assertEqual(a["version"],1)
            self.assertEqual(b["status"],"identical_source_already_present")
            self.assertEqual(c["version"],2)
            with connect(db) as con:
                self.assertEqual(con.execute("SELECT COUNT(*) FROM sections").fetchone()[0],2)
    def test_unknown_book_and_blank_text_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            db=Path(tmp)/"wen.sqlite3"
            with self.assertRaises(ValueError):import_section(db,"outside","one","test","原文")
            with self.assertRaises(ValueError):import_section(db,"kaiwu","one","test","  ")

if __name__=="__main__":
    unittest.main()
