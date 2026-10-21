"""Original Kaiwu business 11 events (one industrial mine emergency), 11 charts.

The author explicitly admits his construction start-date prediction was wrong;
linked same-company or same-mall events remain independently dated questions.
Keep all unreadable OCR placeholders, host rows, and mid-five printed literals.
"""
from __future__ import annotations
import hashlib,json,sqlite3,tempfile,unittest
from pathlib import Path
from scripts.build_kaiwu_business_from_missing import (
 ROOT,BASE_NAME,BASE_SHA,NEW_NAME,SOURCE_SHA,SPEC,prepare,events,build
)
BASE=ROOT/"archives/sqlite"/BASE_NAME
SOURCE=ROOT/"sources/kaiwu/开悟之门_经营求财预测.txt"
class KaiwuBusiness11FullArchiveTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.raw=SOURCE.read_bytes();cls.L=prepare(cls.raw);cls.events=events(cls.L)
 def test_exact_complete_source_original_and_11_actual_printed_charts(self):
  self.assertEqual(hashlib.sha256(self.raw).hexdigest(),SOURCE_SHA)
  self.assertEqual(len(self.raw),46111)
  self.assertEqual(len(self.L),467)
  self.assertEqual(len(self.events),11)
  self.assertEqual([x["caption"] for x in self.events],
   [6,59,95,142,180,211,258,294,342,379,437])
  self.assertEqual(sum(len(x["cells"]) for x in self.events),99)
  self.assertEqual(sum(len(x["steps"]) for x in self.events),64)
  for e in self.events:
   self.assertEqual(sorted(x["palace"] for x in e["cells"]),list(range(1,10)))
   center=next(x for x in e["cells"] if x["palace"]==5)
   self.assertTrue(center["head"].startswith("中5："))
   self.assertEqual(center["door"],"")
   self.assertEqual(center["star"],"")
 def test_ocr_host_extra_rows_and_damaged_preserved(self):
  cells=[c for e in self.events for c in e["cells"]]
  self.assertGreaterEqual(sum(x["damaged"] for x in cells),8)
  self.assertGreaterEqual(sum(bool(x["extra"]) for x in cells),8)
  self.assertIn("原OCR",self.events[0]["cells"][0]["extra"])
  self.assertIn("〔后续缺字〕",self.events[1]["cells"][2]["door"])
  self.assertIn("OCR：己辛",self.events[2]["cells"][2]["extra"])
  self.assertIn("〔神门缺字〕",next(c for c in self.events[5]["cells"] if c["palace"]==1)["head"])
  self.assertIn("乙（寄宫）",next(c for c in self.events[10]["cells"] if c["palace"]==3)["extra"])
 def test_source_admitted_wrong_opening_and_distinct_related_inquiries(self):
  e=self.events
  self.assertEqual(e[3]["key"],"kedi_funding_1998")
  self.assertEqual(e[4]["key"],"kedi_permit_miss_1999")
  self.assertEqual(e[6]["key"],"taihe_mall_build_1999")
  self.assertEqual(e[7]["key"],"taihe_shop_purchase_1999")
  self.assertIn("此例断错",self.L[200])
  self.assertIn("6月29日",self.L[201])
  self.assertIn("明天或后天就能开工",self.L[199])
  self.assertEqual(e[9]["domain"],"industrial_safety")
  self.assertIn("五个工人",self.L[410])
  self.assertIn("7点10分",self.L[417])
  self.assertIn("特等奖",self.L[461])
 def test_complete_prior_full_sqlite_unchanged_and_real_chapter_added(self):
  self.assertEqual(hashlib.sha256(BASE.read_bytes()).hexdigest(),BASE_SHA)
  with tempfile.TemporaryDirectory() as folder:
   new=Path(folder)/NEW_NAME;idx=Path(folder)/"indices"
   result=build(BASE,SOURCE,new,idx)
   self.assertEqual(result["new_actual_independent_events"],11)
   self.assertEqual(result["new_actual_source_printed_charts"],11)
   self.assertEqual(result["total_distinct_historical_events"],149)
   self.assertEqual(result["total_original_historical_casts"],166)
   with sqlite3.connect(new) as db:
    for table,count in result["cumulative_counts"].items():
     self.assertEqual(db.execute('SELECT COUNT(*) FROM "'+table+'"').fetchone()[0],count)
    self.assertEqual(db.execute("SELECT count(*) FROM kaiwu_business_literal_palaces").fetchone()[0],99)
    self.assertEqual(db.execute("SELECT count(*) FROM kaiwu_business_source_casts").fetchone()[0],11)
    self.assertEqual(db.execute("SELECT count(*) FROM kaiwu_business_related_projects").fetchone()[0],2)
    self.assertEqual(db.execute("SELECT count(*) FROM historical_case_book_verdicts WHERE verdict='author_book_error_explicit'").fetchone()[0],9)
    self.assertEqual(db.execute("SELECT count(*) FROM cases WHERE domain_id='industrial_safety'").fetchone()[0],1)
    self.assertEqual(db.execute("SELECT count(*) FROM historic_book_case_acceptance").fetchone()[0],41)
    self.assertEqual(db.execute("SELECT original_text FROM sections WHERE section_key='business_profit_prediction_ch02_section05'").fetchone()[0],self.raw.decode("utf8"))
    self.assertEqual(db.execute("PRAGMA integrity_check").fetchone()[0],"ok")
    self.assertEqual(db.execute("PRAGMA foreign_key_check").fetchall(),[])
   audit=json.loads((idx/"source_audit.json").read_text("utf8"))
   self.assertTrue(audit["case05_first_advance_wrong_21_22_june_actual_29_june"])
   self.assertTrue(audit["case10_five_trapped_miners_life_safety_source_only"])
if __name__=="__main__":unittest.main()
