"""Kaiwu 2nd chapter 8th section: 4 user-accepted lost-property cases.

Regression covers source SHA, exactly 4 printed original charts, two true
thefts versus bag loss and mislaid earring, six-yao-first case04 chronology,
and verified full 149-case parent copied without changing any old rows.
"""
from __future__ import annotations
import hashlib,json,sqlite3,tempfile,unittest
from pathlib import Path
from scripts.build_kaiwu_lost_from_business import (
 ROOT,BASE_NAME,BASE_SHA,NEW_NAME,SOURCE_SHA,prepare,events,build
)
BASE=ROOT/"archives/sqlite"/BASE_NAME
SOURCE=ROOT/"sources/kaiwu/开悟之门_钱物丢失预测.txt"
class KaiwuLostUnifiedFullArchiveTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.raw=SOURCE.read_bytes()
  cls.lines=prepare(cls.raw)
  cls.examples=events(cls.lines)
 def test_exact_original_four_full_nine_palace_panels(self):
  self.assertEqual(len(self.raw),19588)
  self.assertEqual(len(self.lines),180)
  self.assertEqual(hashlib.sha256(self.raw).hexdigest(),SOURCE_SHA)
  self.assertEqual([e["grid"] for e in self.examples],[16,57,97,156])
  self.assertEqual(len(self.examples),4)
  self.assertEqual(sum(len(e["cells"]) for e in self.examples),36)
  self.assertEqual(sum(len(e["steps"]) for e in self.examples),25)
  for e in self.examples:
   self.assertEqual(sorted(c["palace"] for c in e["cells"]),list(range(1,10)))
   center=next(c for c in e["cells"] if c["palace"]==5)
   self.assertEqual(center["header"],"中5")
   self.assertTrue(center["door"])
   self.assertEqual(center["star"],"")
 def test_genuine_uncertain_OCR_and_theft_not_the_same_as_missing(self):
  one=self.examples[0]["cells"]
  self.assertIn("原OCR",next(c for c in one if c["palace"]==8)["door"])
  self.assertIn("缺损",next(c for c in one if c["palace"]==1)["door"])
  self.assertIn("天禽、天芮",next(c for c in one if c["palace"]==6)["star"])
  self.assertEqual([e["theft"] for e in self.examples],[False,True,False,True])
  self.assertIn("现金不见了",self.lines[10])
  self.assertIn("赔偿了摩托车修理费九百九十元",self.lines[51])
  self.assertIn("床上找到了",self.lines[122])
 def test_fourth_initial_sixyao_later_qimen_and_no_extra_full_charts(self):
  self.assertIn("六爻卦",self.lines[138])
  self.assertIn("8月26日",self.lines[140])
  self.assertIn("七天后学会起局",self.lines[140])
  self.assertIn("8月2日",self.lines[142])
  self.assertIn("路基被雨水冲塌",self.lines[144])
  self.assertIn("9月17日",self.lines[179])
  self.assertEqual(len(self.examples[3]["cells"]),9)
  self.assertEqual(self.examples[3]["first"],139)
 def test_full_parent_sha_source_rows_verbatim_new_four_real_cases(self):
  self.assertEqual(hashlib.sha256(BASE.read_bytes()).hexdigest(),BASE_SHA)
  with tempfile.TemporaryDirectory() as folder:
   out=Path(folder)/NEW_NAME;index=Path(folder)/"index"
   result=build(BASE,SOURCE,out,index)
   self.assertEqual(result["new_original_cases"],4)
   self.assertEqual(result["new_source_printed_nine_palace_charts"],4)
   self.assertEqual(result["total_distinct_historical_events"],153)
   self.assertEqual(result["total_actual_source_original_charts"],170)
   with sqlite3.connect(out) as db:
    for table,count in result["counts"].items():
     self.assertEqual(db.execute('SELECT count(*) FROM "'+table+'"').fetchone()[0],count)
    self.assertEqual(db.execute("SELECT count(*) FROM unified_lost_property_cases_across_books").fetchone()[0],12)
    self.assertEqual(db.execute("SELECT count(*) FROM kaiwu_lost_source_palaces").fetchone()[0],36)
    self.assertEqual(db.execute("SELECT count(*) FROM kaiwu_lost_issue_outcomes WHERE is_criminal_theft=1").fetchone()[0],2)
    self.assertEqual(db.execute("SELECT count(*) FROM kaiwu_lost_temporal_caveats").fetchone()[0],4)
    self.assertEqual(db.execute("SELECT count(*) FROM historic_book_case_acceptance").fetchone()[0],45)
    self.assertEqual(db.execute("SELECT count(*) FROM historical_case_book_verdicts WHERE verdict='author_book_error_explicit'").fetchone()[0],9)
    self.assertEqual(db.execute("SELECT original_text FROM sections WHERE section_key='lost_property_prediction_ch02_section08'").fetchone()[0],self.raw.decode("utf8"))
    self.assertEqual(db.execute("PRAGMA integrity_check").fetchone()[0],"ok")
    self.assertEqual(db.execute("PRAGMA foreign_key_check").fetchall(),[])
   a=json.loads((index/"chronology_audit.json").read_text("utf8"))
   self.assertTrue(a["case04_initial_aug20_sixyao_not_qimen"])
   self.assertTrue(a["case01_lost_cash_no_collector_theft_as_proven_fact"])
if __name__=="__main__":unittest.main()
