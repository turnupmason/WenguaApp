"""Regression for the shared-domain Kaiwu employment three original cases.

The same 1997 cast includes two issues but only one historical event/board.
Keep 1999 post-incident exact-day deduction separate from 1997 initial warning.
"""
from __future__ import annotations
import hashlib,json,sqlite3,tempfile,unittest
from pathlib import Path
from scripts.build_kaiwu_employment_from_marriage import (
 ROOT,BASE_NAME,BASE_SHA,NEW_NAME,SOURCE_SHA,SPECS,ISSUES,
 parse_source,parse_events,build
)
BASE=ROOT/"archives/sqlite"/BASE_NAME
SOURCE=ROOT/"sources/kaiwu/开悟之门_工作就业预测.txt"

class KaiwuEmploymentUnifiedTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.raw=SOURCE.read_bytes()
  cls.lines=parse_source(cls.raw)
  cls.items=parse_events(cls.lines)
 def test_exact_original_full_and_three_16_line_panels(self):
  self.assertEqual(len(self.raw),14577)
  self.assertEqual(len(self.lines),150)
  self.assertEqual(hashlib.sha256(self.raw).hexdigest(),SOURCE_SHA)
  self.assertEqual(len(self.items),3)
  self.assertEqual([x["chart"] for x in self.items],[9,43,101])
  self.assertEqual([len(x["cells"]) for x in self.items],[9,9,9])
  self.assertEqual(sum(len(x["steps"]) for x in self.items),13)
  for event in self.items:
   self.assertEqual(sorted(c["palace"] for c in event["cells"]),list(range(1,10)))
   center=next(c for c in event["cells"] if c["palace"]==5)
   self.assertEqual(center["original_door"],"")
   self.assertEqual(center["original_star"],"")
   self.assertIn(center["original_spirit"],("戊","辛","壬"))
  kan=next(c for c in self.items[0]["cells"] if c["palace"]==1)
  self.assertEqual(kan["undeciphered_stems"],2)
  self.assertIn("生门（原文未辨干）",kan["original_door"])
  self.assertIn("天心（原文未辨干）",kan["original_star"])
  star=next(c for c in self.items[2]["cells"] if c["palace"]==2)
  self.assertEqual(star["original_star"],"天禽、天芮 己")
 def test_same_event_two_issues_not_two_case_families_or_charts(self):
  self.assertEqual(len(ISSUES),4)
  self.assertEqual(sum(x[0]=="application_accident" for x in ISSUES),2)
  self.assertEqual(self.items[2]["id"],"kaiwu.employment.19971218.zhang_application_and_accident")
  self.assertEqual(self.items[2]["chart"],101)
  self.assertIn("1999年阴历二月",self.lines[80])
  self.assertNotIn("二月二十三日",self.lines[80])
  self.assertIn("前几天死了一个人",self.lines[88])
  self.assertIn("二月二十三日",self.lines[90])
  self.assertIn("二月二十三日",self.lines[96])
  self.assertEqual(self.items[2]["facets"],["employment","organizational_membership","transport_accident"])
 def test_exact_original_cast_methods_and_audit(self):
  self.assertIn("置闰法",self.lines[6])
  self.assertIn("杜门落5宫寄2宫",self.lines[40])
  self.assertIn("甲午日甲戌时",self.lines[98])
  self.assertIn("日干辛为求测之人",self.lines[121])
  self.assertEqual([len(e["editor"]) for e in self.items],[0,1,4])
 def test_new_version_full_sqlite_no_changes_to_old_tables_and_accepted_source(self):
  self.assertEqual(hashlib.sha256(BASE.read_bytes()).hexdigest(),BASE_SHA)
  with tempfile.TemporaryDirectory() as temp:
   new=Path(temp)/NEW_NAME;idx=Path(temp)/"index"
   report=build(BASE,SOURCE,new,idx)
   self.assertEqual(report["new_independent_event_families"],3)
   self.assertEqual(report["new_source_published_palace_cells"],27)
   self.assertEqual(report["new_author_numbered_reasoning_steps"],13)
   self.assertTrue(report["case3_two_issues_one_historical_event_one_chart"])
   with sqlite3.connect(new) as db:
    for table,count in report["cumulative_counts"].items():
     self.assertEqual(db.execute('SELECT COUNT(*) FROM "'+table+'"').fetchone()[0],count)
    self.assertEqual(db.execute("SELECT COUNT(*) FROM cases").fetchone()[0],130)
    self.assertEqual(db.execute("SELECT COUNT(*) FROM unified_employment_cases_across_books").fetchone()[0]>=8,True)
    self.assertEqual(db.execute("SELECT COUNT(*) FROM crossbook_employment_case_issues").fetchone()[0],4)
    self.assertEqual(db.execute("SELECT COUNT(*) FROM crossbook_employment_source_charts").fetchone()[0],3)
    self.assertEqual(db.execute("SELECT COUNT(*) FROM crossbook_employment_source_palaces").fetchone()[0],27)
    self.assertEqual(db.execute("SELECT COUNT(*) FROM historical_case_book_verdicts WHERE verdict='author_book_error_explicit'").fetchone()[0],8)
    self.assertEqual(db.execute("SELECT COUNT(*) FROM historic_book_case_acceptance").fetchone()[0],22)
    self.assertEqual(db.execute("SELECT original_text FROM sections WHERE section_key='employment_prediction_ch02_section04' AND book_id='kaiwu'").fetchone()[0],self.raw.decode("utf-8"))
    self.assertEqual(db.execute("PRAGMA integrity_check").fetchone()[0],"ok")
    self.assertEqual(db.execute("PRAGMA foreign_key_check").fetchall(),[])
   audit=json.loads((idx/"source_audit.json").read_text("utf8"))
   self.assertTrue(audit["case3_post_accident_specific_date_deduction_not_pre_crash"])
   self.assertTrue(audit["case1_unknown_stems_both_preserved_as_printed"])

if __name__=="__main__":unittest.main()
