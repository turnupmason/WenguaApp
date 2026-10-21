"""Five Kaiwu missing-person stories, six source boards, 54 raw palaces.

One double-cast niece; two different hotel waitresses but one inquiry.
No OCR source reconstruction, no hindsight as first prediction, no per-case
approval, and no repeated old Shenqi female-taxi event.
"""
from __future__ import annotations
import hashlib,json,sqlite3,tempfile,unittest
from pathlib import Path
from scripts.build_kaiwu_missing_from_education import (
 ROOT,BASE_NAME,BASE_SHA,NEW_NAME,SOURCE_SHA,validate_source,parse,build
)
BASE=ROOT/"archives/sqlite"/BASE_NAME
SOURCE=ROOT/"sources/kaiwu/开悟之门_行人走失预测.txt"

class KaiwuMissingPersonFullArchiveTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.raw=SOURCE.read_bytes()
  cls.lines=validate_source(cls.raw)
  cls.cases=parse(cls.lines)
 def test_exact_source_and_all_original_six_charts(self):
  self.assertEqual(len(self.raw),27441)
  self.assertEqual(hashlib.sha256(self.raw).hexdigest(),SOURCE_SHA)
  self.assertEqual(len(self.lines),200)
  self.assertEqual(len(self.cases),5)
  self.assertEqual(sum(len(c["casts"]) for c in self.cases),6)
  self.assertEqual([p["start"] for e in self.cases for p in e["casts"]],[9,36,67,101,138,174])
  self.assertEqual(sum(len(e["steps"]) for e in self.cases),29)
  for case in self.cases:
   for p in case["casts"]:
    self.assertEqual(len(p["cells"]),9)
    self.assertEqual(sorted(c["palace"] for c in p["cells"]),list(range(1,10)))
    center=next(c for c in p["cells"] if c["palace"]==5)
    self.assertEqual(center["spirit"],"中五宫")
    self.assertEqual(center["star"],"")
    self.assertTrue(center["door"])
 def test_preserve_incomplete_OCR_and_special_extra_row(self):
  c=self.cases
  damaged=[x for e in c for p in e["casts"] for x in p["cells"] if x["damaged"]]
  self.assertGreaterEqual(len(damaged),4)
  self.assertIn("神名原OCR：牲",next(x for x in c[0]["casts"][0]["cells"] if x["palace"]==7)["spirit"])
  self.assertIn("原OCR：之",next(x for x in c[0]["casts"][1]["cells"] if x["palace"]==2)["door"])
  self.assertIn("神名缺损",next(x for x in c[1]["casts"][0]["cells"] if x["palace"]==8)["spirit"])
  self.assertIn("原OCR：乙／己／冲 丙",next(x for x in c[3]["casts"][0]["cells"] if x["palace"]==2)["door"])
  self.assertEqual(next(x for x in c[4]["casts"][0]["cells"] if x["palace"]==2)["extra"],"原OCR：庚 辛")
  self.assertEqual(next(x for x in c[2]["casts"][0]["cells"] if x["palace"]==5)["door"],"天禽 庚")
 def test_event_identities_chronology_not_fabricated(self):
  self.assertEqual(len(self.cases[0]["casts"]),2)
  self.assertEqual(len(self.cases[1]["casts"]),1)
  self.assertIn("六十六天",self.lines[58])
  self.assertIn("8月16日",self.lines[87])
  self.assertIn("8月17日",self.lines[90])
  self.assertIn("8月31日",self.lines[123])
  self.assertIn("9月10日",self.lines[124])
  self.assertIn("马兰德测女司机失踪",self.lines[163])
  self.assertIn("1999年3月9日",self.lines[129])
 def test_verified_old_full_sqlite_exact_inclusion_and_new_counts(self):
  self.assertEqual(hashlib.sha256(BASE.read_bytes()).hexdigest(),BASE_SHA)
  with tempfile.TemporaryDirectory() as d:
   output=Path(d)/NEW_NAME;idx=Path(d)/"index"
   m=build(BASE,SOURCE,output,idx)
   self.assertEqual(m["new_unique_historical_events"],5)
   self.assertEqual(m["new_original_printed_charts"],6)
   self.assertEqual(m["total_event_families"],138)
   self.assertEqual(m["total_original_historical_casts"],155)
   with sqlite3.connect(output) as db:
    for t,n in m["cumulative_counts"].items():
     self.assertEqual(db.execute('SELECT COUNT(*) FROM "'+t+'"').fetchone()[0],n)
    self.assertEqual(db.execute("SELECT COUNT(*) FROM cases WHERE domain_id='missing_person'").fetchone()[0],15)
    self.assertEqual(db.execute("SELECT COUNT(*) FROM missing_crossbook_casts").fetchone()[0],6)
    self.assertEqual(db.execute("SELECT COUNT(*) FROM missing_crossbook_palaces").fetchone()[0],54)
    self.assertEqual(db.execute("SELECT COUNT(*) FROM missing_crossbook_subjects").fetchone()[0],2)
    self.assertEqual(db.execute("SELECT COUNT(*) FROM historic_book_case_acceptance").fetchone()[0],30)
    self.assertEqual(db.execute("SELECT COUNT(*) FROM historical_case_book_verdicts WHERE verdict='author_book_error_explicit'").fetchone()[0],8)
    self.assertEqual(db.execute("SELECT original_text FROM sections WHERE section_key='missing_person_prediction_ch02_section07'").fetchone()[0],self.raw.decode("utf-8"))
    self.assertEqual(db.execute("PRAGMA integrity_check").fetchone()[0],"ok")
    self.assertEqual(db.execute("PRAGMA foreign_key_check").fetchall(),[])
   audit=json.loads((idx/"source_audit.json").read_text("utf-8"))
   self.assertTrue(audit["old_Shenqi_female_taxi_case_is_distinct_history"])
   self.assertTrue(audit["student_return_predicted_aug16_actual_aug17"])

if __name__=="__main__":unittest.main()
