"""Kaiwu exam three source cases share Shenqi education domain: 3 casts/4 students."""
from __future__ import annotations
import hashlib,json,sqlite3,tempfile,unittest
from pathlib import Path
from scripts.build_kaiwu_education_from_employment import (
 ROOT,BASE_SHA,BASE_NAME,NEW_NAME,SOURCE_SHA,SPECS,CANDIDATES,CLAIMS,
 read_original,events,build
)
BASE=ROOT/"archives/sqlite"/BASE_NAME
SOURCE=ROOT/"sources/kaiwu/开悟之门_求学考试预测.txt"

class KaiwuEducationFullArchiveTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.raw=SOURCE.read_bytes();cls.L=read_original(cls.raw);cls.es=events(cls.L)
 def test_exact_source_and_three_only_real_printed_boards(self):
  self.assertEqual(len(self.raw),16257)
  self.assertEqual(len(self.L),151)
  self.assertEqual(hashlib.sha256(self.raw).hexdigest(),SOURCE_SHA)
  self.assertEqual([e["chart"] for e in self.es],[29,69,125])
  self.assertEqual(len(self.es),3)
  self.assertEqual(sum(len(e["cells"]) for e in self.es),27)
  self.assertEqual(sum(len(e["reasoning"]) for e in self.es),9)
  for e in self.es:
   self.assertEqual(sorted(v["palace"] for v in e["cells"]),list(range(1,10)))
   mid=next(x for x in e["cells"] if x["palace"]==5)
   self.assertEqual(mid["god"],"")
   self.assertEqual(mid["star"],"")
   self.assertIn(mid["door"],("丁","丙"))
  self.assertEqual(next(x for x in self.es[2]["cells"] if x["palace"]==4)["star"],"禽芮丙")
 def test_no_fake_extra_cast_for_two_sisters_or_street_diviner(self):
  self.assertEqual(len(CANDIDATES),4)
  self.assertEqual(sum(x[0]=="sisters" for x in CANDIDATES),2)
  self.assertEqual(len(self.es[2]["cells"]),9)
  self.assertIn("花费四元钱",self.L[120])
  self.assertIn("自费上了西安电子科技大学",self.L[150])
  self.assertIn("内蒙古工业大学",self.L[150])
  self.assertIn("大女儿考不上",self.L[142])
  self.assertIn("二女儿有把握考上大学",self.L[146])
 def test_predict_score_but_preserve_two_directional_misses(self):
  self.assertEqual(len(CLAIMS),6)
  self.assertEqual(sum(c[-1]=="book_explicit_partial_error" for c in CLAIMS),2)
  self.assertIn("五百四十分",self.L[20])
  self.assertIn("五百四十分",self.L[22])
  self.assertIn("三百五十分",self.L[86])
  self.assertIn("三百四十二分",self.L[102])
  self.assertIn("最后录取学校的方向就没测准",self.L[106])
  self.assertIn("判断得不够准确",self.L[58])
  self.assertIn("《神奇之门》",self.L[10])
 def test_real_full_database_backup_and_unchanged_130_prior_cases(self):
  self.assertEqual(hashlib.sha256(BASE.read_bytes()).hexdigest(),BASE_SHA)
  with tempfile.TemporaryDirectory() as temp:
   output=Path(temp)/NEW_NAME;idx=Path(temp)/"index"
   doc=build(BASE,SOURCE,output,idx)
   self.assertEqual(doc["new_independent_events"],3)
   self.assertEqual(doc["new_student_candidate_outcomes"],4)
   self.assertEqual(doc["total_distinct_event_families"],133)
   self.assertEqual(doc["total_original_printed_historical_casts"],149)
   with sqlite3.connect(output) as db:
    for table,count in doc["counts"].items():
     self.assertEqual(db.execute('SELECT COUNT(*) FROM "'+table+'"').fetchone()[0],count)
    self.assertEqual(db.execute("SELECT COUNT(*) FROM unified_education_cases_across_books").fetchone()[0]>=8,True)
    self.assertEqual(db.execute("SELECT COUNT(*) FROM education_crossbook_source_palaces").fetchone()[0],27)
    self.assertEqual(db.execute("SELECT COUNT(*) FROM education_crossbook_candidates").fetchone()[0],4)
    self.assertEqual(db.execute("SELECT COUNT(*) FROM education_crossbook_book_claims WHERE source_verdict='book_explicit_partial_error'").fetchone()[0],2)
    self.assertEqual(db.execute("SELECT COUNT(*) FROM historic_book_case_acceptance").fetchone()[0],25)
    self.assertEqual(db.execute("SELECT COUNT(*) FROM historical_case_book_verdicts WHERE verdict='author_book_error_explicit'").fetchone()[0],8)
    self.assertEqual(db.execute("SELECT original_text FROM sections WHERE section_key='education_prediction_ch02_section03'").fetchone()[0],self.raw.decode("utf-8"))
    self.assertEqual(db.execute("PRAGMA integrity_check").fetchone()[0],"ok")
    self.assertEqual(db.execute("PRAGMA foreign_key_check").fetchall(),[])
   self.assertTrue(json.loads((idx/"claim_audit.json").read_text("utf8"))["two_directional_errors_not_rewriting_true_score_predictions"])

if __name__=="__main__":unittest.main()
