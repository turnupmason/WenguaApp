"""Last Kaiwu source chapter must not leak hindsight into 194-event full database."""
import hashlib,json,sqlite3,tempfile,unittest
from pathlib import Path
from scripts.build_kaiwu_ch03_source_final_194 import ROOT,CFG,SOURCE,PARENT,OUTPUT,verify,build
BASE=ROOT/"archives/sqlite"/PARENT
class FinalTwoBooksTest(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.cfg=json.loads(CFG.read_text("utf8"))
  cls.raw=SOURCE.read_bytes()
  cls.L=verify(cls.raw,cls.cfg)
 def test_original_file_subsections_and_casts(self):
  self.assertEqual(hashlib.sha256(self.raw).hexdigest(),self.cfg["source_sha256"])
  self.assertEqual(len(self.raw),62625)
  self.assertEqual(len(self.L),571)
  self.assertEqual(len(self.cfg["headings"]),14)
  self.assertEqual(len(self.cfg["question_answers"]),15)
  self.assertEqual(len(self.cfg["cases"]),13)
  self.assertEqual(len(self.cfg["casts"]),16)
  self.assertEqual(sum(b-a+1 for _,a,b,_ in self.cfg["casts"]),295)
  self.assertIn("放之四海而皆准",self.L[384])
  self.assertIn("三次断错",self.L[201])
  self.assertIn("测错了",self.L[106])
  self.assertTrue(self.L[-1].endswith("还得恢复一段时间"))
 def test_true_parent_13_unique_with_Kedi_same_old(self):
  self.assertEqual(hashlib.sha256(BASE.read_bytes()).hexdigest(),self.cfg["parent_sha256"])
  with tempfile.TemporaryDirectory() as d:
   out=Path(d)/OUTPUT
   m=build(BASE,SOURCE,out,Path(d)/"knowledge")
   self.assertEqual(m["new_independent_events"],13)
   self.assertEqual(m["book_first_answer_errors_after"],19)
   self.assertTrue(m["all_historical_original_rows_unchanged"])
   with sqlite3.connect(out) as db:
    for k,c in m["counts"].items():
     self.assertEqual(db.execute('SELECT COUNT(*) FROM "'+k+'"').fetchone()[0],c,k)
    self.assertEqual(db.execute("SELECT count(*) FROM cases").fetchone()[0],194)
    self.assertEqual(db.execute("SELECT count(*) FROM cases WHERE case_id='kaiwu.business.case05'").fetchone()[0],1)
    self.assertEqual(db.execute("SELECT count(*) FROM kaiwu_final_cast_case_links WHERE cast_key='three_people'").fetchone()[0],3)
    self.assertEqual(db.execute("SELECT count(*) FROM kaiwu_final_cast_case_links WHERE cast_key='marriage_shared'").fetchone()[0],2)
    self.assertEqual(db.execute("SELECT count(*) FROM kaiwu_final_event_witnesses WHERE relation='same_prior_question_no_new_family'").fetchone()[0],1)
    self.assertEqual(db.execute("SELECT count(*) FROM historical_chart_cells").fetchone()[0],1440)
    self.assertEqual(db.execute("SELECT count(*) FROM historical_case_book_verdicts WHERE verdict='author_book_error_explicit'").fetchone()[0],19)
    self.assertEqual(db.execute("SELECT original_text FROM sections WHERE section_key='questions_answers_errors_and_methods_ch03'").fetchone()[0],self.raw.decode("utf8"))
    self.assertEqual(db.execute("PRAGMA integrity_check").fetchone()[0],"ok")
    self.assertEqual(db.execute("PRAGMA foreign_key_check").fetchall(),[])
if __name__=="__main__":unittest.main()
