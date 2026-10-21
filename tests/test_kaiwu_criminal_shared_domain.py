"""Kaiwu original ch2 section9 robbery/murder source and immutable whole SQLite."""
from __future__ import annotations
import hashlib,json,sqlite3,tempfile,unittest
from pathlib import Path
from scripts.build_kaiwu_criminal_from_travel import (
 ROOT,BASE_NAME,BASE_SHA,NEW_NAME,SOURCE_SHA,CLAIMS,
 check_source,validate_cases,build
)
PARENT=ROOT/"archives/sqlite"/BASE_NAME
SOURCE=ROOT/"sources/kaiwu/开悟之门_刑事案件预测.txt"

class KaiwuCriminalTwoCasesFullSourceTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.raw=SOURCE.read_bytes();cls.L=check_source(cls.raw);cls.events=validate_cases(cls.L)
 def test_original_bytes_two_real_panels_and_18_literal_palaces(self):
  self.assertEqual(len(self.raw),12565)
  self.assertEqual(len(self.L),100)
  self.assertEqual(hashlib.sha256(self.raw).hexdigest(),SOURCE_SHA)
  self.assertEqual(len(self.events),2)
  self.assertEqual([c["start"] for c in self.events],[15,58])
  self.assertEqual(sum(len(c["steps"]) for c in self.events),13)
  self.assertEqual(sum(len(c["cells"]) for c in self.events),18)
  for e in self.events:
   self.assertEqual(sorted(c["palace"] for c in e["cells"]),list(range(1,10)))
   center=next(c for c in e["cells"] if c["palace"]==5)
   self.assertEqual(center["header"],"中5")
   self.assertEqual(center["god"],"")
   self.assertEqual(center["star"],"")
   self.assertIn("原OCR中宫字符",center["door"])
  self.assertEqual(next(c for c in self.events[1]["cells"] if c["palace"]==8)["star"],"天芮 丙、天禽 壬")
  self.assertEqual(next(c for c in self.events[0]["cells"] if c["palace"]==4)["door"],"庚；杜门 癸")
 def test_classroom_staged_disclosures_and_not_verified_final_arrest(self):
  self.assertEqual(self.events[0]["steps"],[31,35,39,43,45,49])
  self.assertIn("整七千",self.L[32])
  self.assertIn("两个人作案",self.L[36])
  self.assertIn("确实是女的",self.L[44])
  self.assertIn("说明能抓住一个罪犯",self.L[48])
  self.assertEqual(CLAIMS[3][4],"unconfirmed_forecast")
  self.assertEqual(CLAIMS[3][3],None)
 def test_two_admitted_errors_homicide_count_and_arrest_time(self):
  self.assertEqual(self.events[1]["steps"],[74,76,78,80,82,84,86])
  self.assertIn("案发时间起局",self.L[52])
  self.assertIn("问测时间验证",self.L[52])
  self.assertIn("案犯二至三人",self.L[77])
  self.assertIn("最迟于今年丁丑月侦破",self.L[85])
  self.assertIn("案犯一人",self.L[87])
  self.assertIn("丁丑日",self.L[87])
  self.assertIn("人数及破案时间未断准",self.L[89])
  self.assertIn("不是二至三人",self.L[97])
  self.assertIn("丁丑日",self.L[99])
  self.assertEqual(sum(c[4]=="book_explicit_error" for c in CLAIMS),2)
  self.assertEqual(sum(c[4]=="book_reported_difference" for c in CLAIMS),1)
 def test_shapinned_full_parent_untouched_new_2_cases_real_db(self):
  self.assertEqual(hashlib.sha256(PARENT.read_bytes()).hexdigest(),BASE_SHA)
  with tempfile.TemporaryDirectory() as temp:
   new=Path(temp)/NEW_NAME;index=Path(temp)/"index"
   result=build(PARENT,SOURCE,new,index)
   self.assertEqual(result["total_independent_historical_cases"],161)
   self.assertEqual(result["total_genuinely_original_printed_historical_casts"],179)
   with sqlite3.connect(new) as db:
    for table,n in result["counts"].items():
     self.assertEqual(db.execute('SELECT count(*) FROM "'+table+'"').fetchone()[0],n)
    self.assertEqual(db.execute("SELECT count(*) FROM unified_criminal_cases_across_books").fetchone()[0],7)
    self.assertEqual(db.execute("SELECT count(*) FROM kaiwu_criminal_original_palaces").fetchone()[0],18)
    self.assertEqual(db.execute("SELECT count(*) FROM kaiwu_criminal_scoped_claims WHERE verdict='book_explicit_error'").fetchone()[0],2)
    self.assertEqual(db.execute("SELECT count(*) FROM kaiwu_criminal_unprinted_cast_mentions").fetchone()[0],1)
    self.assertEqual(db.execute("SELECT count(*) FROM historical_case_book_verdicts WHERE verdict='author_book_error_explicit'").fetchone()[0],10)
    self.assertEqual(db.execute("SELECT original_text FROM sections WHERE section_key='criminal_case_prediction_ch02_section09'").fetchone()[0],self.raw.decode("utf8"))
    self.assertEqual(db.execute("PRAGMA integrity_check").fetchone()[0],"ok")
    self.assertEqual(db.execute("PRAGMA foreign_key_check").fetchall(),[])
   audit=json.loads((index/"claim_and_timing_audit.json").read_text("utf8"))
   self.assertTrue(audit["case1_final_arrest_prediction_has_no_book_feedback"])
   self.assertTrue(audit["case2_first_unprinted_crime_time_cast_not_fabricated"])
if __name__=="__main__":unittest.main()
