"""Kaiwu geography source regression: one SAME old cemetery, only TWO new events."""
from __future__ import annotations
import hashlib,sqlite3,tempfile,unittest
from pathlib import Path
from scripts.build_kaiwu_geography_from_recent import (ROOT,BASE_SHA,BASE_NAME,NEW_NAME,
 SOURCE_SHA,CASES,METHODS,validate,build)
BASE=ROOT/'archives/sqlite'/BASE_NAME
SOURCE=ROOT/'sources/kaiwu/开悟之门_地理风水预测.txt'
class GeographyCrossBookTest(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.raw=SOURCE.read_bytes();cls.L=validate(cls.raw)
 def test_precise_source_and_explicit_same_prior_event(self):
  self.assertEqual(len(self.raw),7161)
  self.assertEqual(hashlib.sha256(self.raw).hexdigest(),SOURCE_SHA)
  self.assertEqual(len(self.L),103)
  self.assertEqual([e['id'] for e in CASES],
   ['shenqi.geography.case02','kaiwu.geography.case02','kaiwu.geography.case03'])
  self.assertEqual([len(e['steps']) for e in CASES],[5,7,2])
  self.assertEqual(sum(e['panel'][1]-e['panel'][0]+1 for e in CASES),41)
  self.assertEqual(len(METHODS),11)
  self.assertIn('《神奇之门》书中测阴宅',self.L[3])
  self.assertIn('房屋尚未盖好',self.L[71])
  self.assertIn('一万元订金',self.L[102])
  self.assertEqual(self.L[53],'开  乙 心 ，乙')
 def test_exact_previous_full_archive_and_all_old_rows_unchanged(self):
  self.assertEqual(hashlib.sha256(BASE.read_bytes()).hexdigest(),BASE_SHA)
  with tempfile.TemporaryDirectory() as d:
   out=Path(d)/NEW_NAME
   manifest=build(BASE,SOURCE,out,Path(d)/'index')
   self.assertEqual(manifest['new_unique_historical_events'],2)
   self.assertEqual(manifest['author_source_steps'],14)
   self.assertEqual(manifest['new_certified_complete_original_nine_palaces'],0)
   with sqlite3.connect(out) as db:
    for k,v in manifest['counts'].items():
     self.assertEqual(db.execute('SELECT count(*) FROM "'+k+'"').fetchone()[0],v,k)
    self.assertEqual(db.execute('SELECT count(*) FROM cases').fetchone()[0],175)
    self.assertEqual(db.execute("SELECT count(*) FROM cases WHERE case_id='shenqi.geography.case02'").fetchone()[0],1)
    self.assertEqual(db.execute('SELECT count(*) FROM kaiwu_geography_source_witnesses').fetchone()[0],3)
    self.assertEqual(db.execute('SELECT count(*) FROM kaiwu_geography_raw_lines').fetchone()[0],41)
    self.assertEqual(db.execute('SELECT count(*) FROM kaiwu_geography_author_steps').fetchone()[0],14)
    self.assertEqual(db.execute('SELECT count(*) FROM kaiwu_geography_method_candidates').fetchone()[0],11)
    self.assertEqual(db.execute('SELECT count(*) FROM historical_chart_cells').fetchone()[0],1440)
    self.assertEqual(db.execute("SELECT count(*) FROM historical_case_book_verdicts WHERE verdict='author_book_error_explicit'").fetchone()[0],11)
    self.assertEqual(db.execute("SELECT original_text FROM sections WHERE section_key='fengshui_geography_ch02_section14'").fetchone()[0],self.raw.decode('utf8'))
    self.assertEqual(db.execute("SELECT count(*) FROM kaiwu_geography_source_witnesses WHERE witness_relationship='same_shenqi_event_new_explanation'").fetchone()[0],1)
    self.assertEqual(db.execute("SELECT count(*) FROM kaiwu_geography_author_steps WHERE witness_key LIKE '%shenqi.geography.case02'").fetchone()[0],5)
    self.assertEqual(db.execute("SELECT count(*) FROM kaiwu_geography_method_candidates WHERE review_status='draft' AND positive_training_eligible=0").fetchone()[0],11)
    self.assertEqual(db.execute('PRAGMA integrity_check').fetchone()[0],'ok')
    self.assertEqual(db.execute('PRAGMA foreign_key_check').fetchall(),[])
if __name__=='__main__':unittest.main()
