"""Source-grounded, immutable full-parent regression for Kaiwu school/debate."""
import hashlib,sqlite3,tempfile,unittest
from pathlib import Path
from scripts.build_kaiwu_competition_from_litigation import (
 ROOT,BASE_SHA,BASE_NAME,NEW_NAME,SOURCE_SHA,CASES,CASTS,METHODS,validate,build)
BASE=ROOT/'archives/sqlite'/BASE_NAME
SOURCE=ROOT/'sources/kaiwu/开悟之门_竞争评比预测.txt'
class CompetitionFullSourceTest(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.raw=SOURCE.read_bytes();cls.L=validate(cls.raw)
 def test_source_casts_and_group_winners(self):
  self.assertEqual(hashlib.sha256(self.raw).hexdigest(),SOURCE_SHA)
  self.assertEqual(len(self.raw),14348)
  self.assertEqual(len(self.L),120)
  self.assertEqual(len(CASES),2)
  self.assertEqual(len(CASTS),4)
  self.assertEqual(len([x for x in CASTS if x[-1] is None]),1)
  self.assertEqual(sum(x[-1][1]-x[-1][0]+1 for x in CASTS if x[-1]),51)
  self.assertEqual(sum(len(s) for e in CASES for s in e['steps'].values()),14)
  self.assertEqual(len(METHODS),12)
  self.assertIn('格局只好阙如',self.L[9])
  self.assertIn('A 组冠军',self.L[115])
  self.assertIn('B组的冠军',self.L[115])
  self.assertIn('修改加工',self.L[119])
 def test_append_to_exact_179_no_old_row_mutations(self):
  self.assertEqual(hashlib.sha256(BASE.read_bytes()).hexdigest(),BASE_SHA)
  with tempfile.TemporaryDirectory() as d:
   out=Path(d)/NEW_NAME
   m=build(BASE,SOURCE,out,Path(d)/'index')
   self.assertEqual(m['new_distinct_event_families'],2)
   with sqlite3.connect(out) as db:
    for table,expect in m['counts'].items():
     self.assertEqual(db.execute('SELECT COUNT(*) FROM "'+table+'"').fetchone()[0],expect,table)
    self.assertEqual(db.execute('SELECT COUNT(*) FROM cases').fetchone()[0],181)
    self.assertEqual(db.execute("SELECT COUNT(*) FROM kaiwu_competition_source_episodes WHERE cast_state='historical_original_lost'").fetchone()[0],1)
    self.assertEqual(db.execute('SELECT COUNT(*) FROM kaiwu_competition_raw_casts').fetchone()[0],3)
    self.assertEqual(db.execute('SELECT COUNT(*) FROM kaiwu_competition_raw_lines').fetchone()[0],51)
    self.assertEqual(db.execute('SELECT COUNT(*) FROM historical_chart_cells').fetchone()[0],1440)
    self.assertEqual(db.execute("SELECT COUNT(*) FROM historical_case_book_verdicts WHERE verdict='author_book_error_explicit'").fetchone()[0],11)
    self.assertEqual(db.execute("SELECT original_text FROM sections WHERE section_key='competition_evaluation_ch02_section12'").fetchone()[0],self.raw.decode('utf8'))
    self.assertEqual(db.execute('PRAGMA integrity_check').fetchone()[0],'ok')
    self.assertEqual(db.execute('PRAGMA foreign_key_check').fetchall(),[])
if __name__=='__main__':unittest.main()
