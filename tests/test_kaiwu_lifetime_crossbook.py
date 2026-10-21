"""Source-level & full-parent no-loss tests for Kaiwu lifetime source case witnesses."""
from __future__ import annotations
import hashlib,sqlite3,tempfile,unittest
from pathlib import Path
from scripts.build_kaiwu_lifetime_from_weather import (
 ROOT,BASE_NAME,NEW_NAME,BASE_SHA,SOURCE_SHA,CASES,validate,get_steps,build
)
BASE=ROOT/'archives/sqlite'/BASE_NAME
SOURCE=ROOT/'sources/kaiwu/开悟之门_人生命运预测.txt'
class KaiwuLifetimeSourceTest(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.raw=SOURCE.read_bytes();cls.L=validate(cls.raw)
 def test_source_integrity_duplicates_and_all_seventy_four_author_units(self):
  self.assertEqual(hashlib.sha256(self.raw).hexdigest(),SOURCE_SHA)
  self.assertEqual(len(self.raw),26715)
  self.assertEqual([e['id'] for e in CASES],
   ['shenqi.life.case05']+[f'kaiwu.life.case0{i}' for i in range(2,6)])
  self.assertEqual([len(get_steps(self.L,e)) for e in CASES],[19,6,26,20,3])
  self.assertEqual(sum(e['chart'][1]-e['chart'][0]+1 for e in CASES),85)
  self.assertIn('断错',self.L[54]);self.assertIn('1996年病故',self.L[54])
  self.assertIn('局限性也是很大的',self.L[121])
 def test_complete_append_never_alters_163_events_and_old_error(self):
  self.assertEqual(hashlib.sha256(BASE.read_bytes()).hexdigest(),BASE_SHA)
  with tempfile.TemporaryDirectory() as temp:
   out=Path(temp)/NEW_NAME
   info=build(BASE,SOURCE,out,Path(temp)/'index')
   self.assertEqual(info['total_independent_event_families'],167)
   self.assertEqual(info['author_steps_full_original'],74)
   with sqlite3.connect(out) as db:
    self.assertEqual(db.execute('SELECT count(*) FROM cases').fetchone()[0],167)
    self.assertEqual(db.execute('SELECT count(*) FROM kaiwu_life_source_witnesses').fetchone()[0],5)
    self.assertEqual(db.execute('SELECT count(*) FROM kaiwu_life_author_step_witnesses').fetchone()[0],74)
    self.assertEqual(db.execute('SELECT count(*) FROM historical_chart_cells').fetchone()[0],1440)
    self.assertEqual(db.execute('SELECT count(*) FROM kaiwu_life_original_chart_lines').fetchone()[0],85)
    self.assertEqual(db.execute("SELECT count(*) FROM cases WHERE case_id='shenqi.life.case05'").fetchone()[0],1)
    self.assertEqual(db.execute("SELECT count(*) FROM historical_case_book_verdicts WHERE verdict='author_book_error_explicit'").fetchone()[0],10)
    self.assertEqual(db.execute("SELECT original_text FROM sections WHERE section_key='lifetime_fate_prediction_ch02_section16'").fetchone()[0],self.raw.decode('utf8'))
    self.assertEqual(db.execute('PRAGMA integrity_check').fetchone()[0],'ok')
    self.assertEqual(db.execute('PRAGMA foreign_key_check').fetchall(),[])
if __name__=='__main__':unittest.main()
