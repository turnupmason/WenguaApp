"""Regression: immutable 167-case baseline plus six correctly typed recent-fortune events."""
import hashlib,sqlite3,tempfile,unittest
from pathlib import Path
from scripts.build_kaiwu_recent_from_lifetime import ROOT,BASE_SHA,BASE_NAME,NEW_NAME,SOURCE_SHA,CASES,validate,build
BASE=ROOT/'archives/sqlite'/BASE_NAME
SOURCE=ROOT/'sources/kaiwu/开悟之门_人生运气预测.txt'
class RecentSourceTest(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.raw=SOURCE.read_bytes();cls.L=validate(cls.raw)
 def test_source_exact_and_exception_phases(self):
  self.assertEqual(hashlib.sha256(self.raw).hexdigest(),SOURCE_SHA)
  self.assertEqual(sum(e['chart'][1]-e['chart'][0]+1 for e in CASES),84)
  self.assertEqual(len(CASES),6)
  self.assertEqual([len(e['steps']) for e in CASES],[5,7,5,7,5,6])
  self.assertEqual(sum(len(e['steps'])+len(e['teacher']) for e in CASES),51)
  self.assertIn('错局正断',self.L[211])
  self.assertIn('没有预测到这么严重',self.L[243])
 def test_append_exact_167_parent(self):
  self.assertEqual(hashlib.sha256(BASE.read_bytes()).hexdigest(),BASE_SHA)
  with tempfile.TemporaryDirectory() as temp:
   out=Path(temp)/NEW_NAME
   m=build(BASE,SOURCE,out,Path(temp)/'index')
   self.assertEqual(m['new_independent_source_events'],6)
   with sqlite3.connect(out) as db:
    for k,v in m['counts'].items():self.assertEqual(db.execute('SELECT COUNT(*) FROM "'+k+'"').fetchone()[0],v)
    self.assertEqual(db.execute("SELECT COUNT(*) FROM cases WHERE case_id LIKE 'kaiwu.recent_fortune.%'").fetchone()[0],6)
    self.assertEqual(db.execute('SELECT count(*) FROM kaiwu_recent_panels').fetchone()[0],6)
    self.assertEqual(db.execute('SELECT count(*) FROM kaiwu_recent_unprinted_anecdotes').fetchone()[0],2)
    self.assertEqual(db.execute('SELECT count(*) FROM historical_chart_cells').fetchone()[0],1440)
    self.assertEqual(db.execute("SELECT count(*) FROM historical_case_book_verdicts WHERE verdict='author_book_error_explicit'").fetchone()[0],11)
    self.assertEqual(db.execute('PRAGMA integrity_check').fetchone()[0],'ok')
    self.assertEqual(db.execute('PRAGMA foreign_key_check').fetchall(),[])
if __name__=='__main__':unittest.main()
