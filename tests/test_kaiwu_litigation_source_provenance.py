"""Append-only Kaiwu litigation source phase, book cautions and SQL parent regression."""
from __future__ import annotations
import hashlib,sqlite3,tempfile,unittest
from pathlib import Path
from scripts.build_kaiwu_litigation_from_geography import (
 ROOT,BASE_SHA,BASE_NAME,NEW_NAME,SOURCE_SHA,CASES,METHODS,validate,
 transcribed_palaces,build)
BASE=ROOT/'archives/sqlite'/BASE_NAME
SOURCE=ROOT/'sources/kaiwu/开悟之门_官司诉讼预测.txt'
class KaiwuLitigation(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.raw=SOURCE.read_bytes()
  cls.L=validate(cls.raw)
 def test_full_source_sha_and_derived_reconstruction_only(self):
  self.assertEqual(hashlib.sha256(self.raw).hexdigest(),SOURCE_SHA)
  self.assertEqual(len(self.raw),19964)
  self.assertEqual(len(self.L),203)
  self.assertEqual(len(CASES),4)
  self.assertEqual(sum(len(e['steps']) for e in CASES),19)
  self.assertEqual(sum(len(e['teacher']) for e in CASES),6)
  self.assertEqual(len(METHODS),16)
  for e in CASES:
   self.assertEqual(len(transcribed_palaces(self.L,*e['panel'])),9)
  self.assertIn('未能看出',self.L[192])
  self.assertIn('不够规范',self.L[101])
 def test_175_parent_all_original_rows_and_179_cases(self):
  self.assertEqual(hashlib.sha256(BASE.read_bytes()).hexdigest(),BASE_SHA)
  with tempfile.TemporaryDirectory() as t:
   dbfile=Path(t)/NEW_NAME
   doc=build(BASE,SOURCE,dbfile,Path(t)/'index')
   self.assertEqual(doc['new_distinct_event_families'],4)
   with sqlite3.connect(dbfile) as db:
    for table,count in doc['counts'].items():
     self.assertEqual(db.execute('SELECT COUNT(*) FROM "'+table+'"').fetchone()[0],count,table)
    self.assertEqual(db.execute('SELECT COUNT(*) FROM cases').fetchone()[0],179)
    self.assertEqual(db.execute("SELECT COUNT(*) FROM cases WHERE domain_id='litigation'").fetchone()[0]>=10,True)
    self.assertEqual(db.execute('SELECT COUNT(*) FROM historical_chart_cells').fetchone()[0],1440)
    self.assertEqual(db.execute("SELECT COUNT(*) FROM kaiwu_litigation_transcribed_palaces WHERE center_unprinted_deity_door_star=1").fetchone()[0],4)
    self.assertEqual(db.execute('SELECT COUNT(*) FROM kaiwu_litigation_source_panels').fetchone()[0],4)
    self.assertEqual(db.execute("SELECT COUNT(*) FROM historical_case_book_verdicts WHERE verdict='author_book_error_explicit'").fetchone()[0],11)
    self.assertEqual(db.execute("SELECT original_text FROM sections WHERE section_key='litigation_prediction_ch02_section10'").fetchone()[0],self.raw.decode('utf8'))
    self.assertEqual(db.execute('PRAGMA integrity_check').fetchone()[0],'ok')
    self.assertEqual(db.execute('PRAGMA foreign_key_check').fetchall(),[])
if __name__=='__main__':unittest.main()
