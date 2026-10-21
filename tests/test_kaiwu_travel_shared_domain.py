"""Book travel cases are six inquiries and seven genuine printed boards.

A post-news plane-crash investigation cannot be evaluated as a pre-accident
forecast. Canada two Qimen consultations represent one immigration application,
and feedback only reports interview passage. Raw OCR and the source's added
fifth rows must be preserved without fabricated normalized stems.
"""
from __future__ import annotations
import hashlib,json,sqlite3,tempfile,unittest
from pathlib import Path
from scripts.build_kaiwu_travel_from_lost import (
 ROOT,BASE_NAME,BASE_SHA,NEW_NAME,SOURCE_SHA,validate,prepare_cases,build
)
PARENT=ROOT/"archives/sqlite"/BASE_NAME
SOURCE=ROOT/"sources/kaiwu/开悟之门_出行出国预测.txt"

class KaiwuTravelAdditiveSixEventsTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.raw=SOURCE.read_bytes();cls.lines=validate(cls.raw)
  cls.cases=prepare_cases(cls.lines)
 def test_exact_original_and_nonrectangular_source_panels(self):
  self.assertEqual(len(self.raw),28678)
  self.assertEqual(len(self.lines),230)
  self.assertEqual(hashlib.sha256(self.raw).hexdigest(),SOURCE_SHA)
  self.assertEqual(len(self.cases),6)
  self.assertEqual([b["start"] for e in self.cases for b in e["boards"]],
                   [11,42,75,104,144,176,207])
  self.assertEqual(sum(len(e["boards"]) for e in self.cases),7)
  self.assertEqual(sum(len(b["cells"]) for e in self.cases for b in e["boards"]),63)
  self.assertEqual(sum(len(e["steps"]) for e in self.cases),34)
  self.assertEqual(sum(bool(c["extra"] and any(c["extra"]))
    for e in self.cases for b in e["boards"] for c in b["cells"]),4)
  for e in self.cases:
   for board in e["boards"]:
    self.assertEqual(sorted(c["palace"] for c in board["cells"]),list(range(1,10)))
    center=next(c for c in board["cells"] if c["palace"]==5)
    self.assertEqual(center["door"],"")
    self.assertEqual(center["star"],"")
  self.assertEqual(self.cases[2]["boards"][1]["cells"][1]["extra"],["天心 己"])
  self.assertEqual(next(c for c in self.cases[0]["boards"][0]["cells"] if c["palace"]==7)["extra"],["原OCR游离：己 丁"])
 def test_retro_airline_and_two_cast_same_canadian_applicant(self):
  self.assertIn("事后用奇门",self.lines[5])
  self.assertTrue(self.cases[0]["boards"][0]["outcome_known"])
  self.assertEqual(self.cases[0]["original_forecast"],[])
  self.assertEqual(len(self.cases[2]["boards"]),2)
  self.assertEqual(self.cases[2]["boards"][1]["key"],"additional_1")
  self.assertIn("1998年7月27日",self.lines[68])
  self.assertIn("出现了许多矛盾的信息",self.lines[128])
  self.assertIn("10月29日",self.lines[130])
  self.assertIn("6月16日上午11点40分",self.lines[134])
  self.assertIn("虽有难度，但能通过",self.lines[129])
 def test_travel_person_links_but_distinct_events_and_ocr(self):
  self.assertEqual(len(self.cases[4]["boards"]),1)
  self.assertEqual(len(self.cases[5]["boards"]),1)
  self.assertIn("受阻",self.lines[199])
  self.assertIn("突然停电",self.lines[226])
  self.assertIn("石家庄",self.lines[226])
  self.assertIn("沈阳",self.lines[201])
  self.assertTrue(next(c for c in self.cases[5]["boards"][0]["cells"] if c["palace"]==9)["damaged"])
 def test_append_only_real_parent_all_old_rows_and_safeguards(self):
  self.assertEqual(hashlib.sha256(PARENT.read_bytes()).hexdigest(),BASE_SHA)
  with tempfile.TemporaryDirectory() as d:
   dbfile=Path(d)/NEW_NAME;idx=Path(d)/"indices"
   manifest=build(PARENT,SOURCE,dbfile,idx)
   self.assertEqual(manifest["total_distinct_historical_events"],159)
   self.assertEqual(manifest["total_original_historical_casts"],177)
   with sqlite3.connect(dbfile) as db:
    for table,count in manifest["counts"].items():
     self.assertEqual(db.execute('SELECT count(*) FROM "'+table+'"').fetchone()[0],count)
    self.assertEqual(db.execute("SELECT count(*) FROM unified_travel_abroad_cases_across_books").fetchone()[0],12)
    self.assertEqual(db.execute("SELECT count(*) FROM kaiwu_travel_source_casts").fetchone()[0],7)
    self.assertEqual(db.execute("SELECT count(*) FROM kaiwu_travel_original_palaces").fetchone()[0],63)
    self.assertEqual(db.execute("SELECT count(*) FROM kaiwu_travel_source_casts WHERE outcome_known_at_cast=1").fetchone()[0],1)
    self.assertFalse(db.execute("SELECT 1 FROM historical_case_book_verdicts WHERE primary_case_id='kaiwu.travel.case01'").fetchone())
    self.assertEqual(db.execute("SELECT count(*) FROM kaiwu_travel_source_context_links").fetchone()[0],2)
    self.assertEqual(db.execute("SELECT count(*) FROM kaiwu_travel_missing_cast_mentions").fetchone()[0],1)
    self.assertEqual(db.execute("SELECT count(*) FROM historical_case_book_verdicts WHERE verdict='author_book_error_explicit'").fetchone()[0],9)
    self.assertEqual(db.execute("SELECT count(*) FROM historic_book_case_acceptance").fetchone()[0],51)
    self.assertEqual(db.execute("SELECT original_text FROM sections WHERE section_key='travel_abroad_prediction_ch02_section06'").fetchone()[0],self.raw.decode("utf-8"))
    self.assertEqual(db.execute("PRAGMA integrity_check").fetchone()[0],"ok")
    self.assertEqual(db.execute("PRAGMA foreign_key_check").fetchall(),[])
   audit=json.loads((idx/"chronology_scope_audit.json").read_text("utf-8"))
   self.assertTrue(audit["flight_newscast_precedes_qimen_retro_analysis"])
   self.assertTrue(audit["canada_reported_interview_pass_not_final_immigration_document"])

if __name__=="__main__":unittest.main()
