"""Source-anchored Kaiwu chapter 4 regression: asymmetric 81 pairs; full old V1."""
import hashlib,json,sqlite3,tempfile,unittest
from pathlib import Path

from scripts.build_kaiwu_04_from_03 import (
 BASE_NAME,BASE_SHA,CHAPTER,SOURCE_SHA,SUCCESS_LINES,FAIL_LINES,GENG_LINES,
 FORMATION_SOURCE,ROOT,build,original_lines,ordered_pairs,references,source_figures,
 timings,assertions
)

BASE=ROOT/"archives/sqlite"/BASE_NAME
SOURCE=ROOT/"sources/kaiwu/开悟之门_第四章.txt"

class KaiwuFourthChapterTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.raw=SOURCE.read_bytes()
  cls.lines=original_lines(cls.raw)
  cls.pairs=ordered_pairs(cls.lines)
  cls.refs=references(cls.lines)
  cls.figures=source_figures(cls.lines)
  cls.timing=timings(cls.lines)
  cls.items=assertions(cls.lines,cls.pairs,cls.refs,cls.timing)

 def test_original_entire_source_and_sections(self):
  self.assertEqual(len(self.raw),84327)
  self.assertEqual(len(self.lines),656)
  self.assertEqual(hashlib.sha256(self.raw).hexdigest(),SOURCE_SHA)
  for section in ("第一节","第二节","第三节","第四节","第五节"):
   self.assertTrue(any(x.startswith(section) for x in self.lines))
  self.assertEqual(self.lines[0],"第四章 如何分析判断奇门格局")

 def test_exact_81_directed_pairs_source_provenance(self):
  self.assertEqual(len(self.pairs),81)
  self.assertEqual(len({x["pair_key"] for x in self.pairs}),81)
  mp={x["pair_key"]:x for x in self.pairs}
  for k in ("戊/庚","庚/戊","丙/庚","庚/丙","乙/辛","辛/乙"):
   self.assertIn(k,mp)
  self.assertNotEqual(mp["戊/庚"]["source_line"],mp["庚/戊"]["source_line"])
  self.assertIn("值符飞宫",mp["戊/庚"]["source_original"])
  self.assertIn("值符伏宫",mp["庚/戊"]["source_original"])
  self.assertIn("荧入太白",mp["丙/庚"]["source_original"])
  self.assertIn("贼来",mp["庚/丙"]["source_original"])
  self.assertTrue(all(x["review_status"]=="draft" for x in self.pairs))

 def test_success_failure_interception_not_same_timing_rule(self):
  self.assertEqual([x["source_line"] for x in self.timing if x["category"]=="successful_outcome"],SUCCESS_LINES)
  self.assertEqual([x["source_line"] for x in self.timing if x["category"]=="failed_outcome"],FAIL_LINES)
  self.assertEqual([x["source_line"] for x in self.timing if x["category"]=="interception_recovery"],GENG_LINES)
  self.assertTrue(any(x["source_line"]==224 and "乙庚合不为格" in x["original_text"] for x in self.timing))
  self.assertTrue(any(x["source_line"]==232 and "提前了一天" in x["original_text"] for x in self.timing))
  self.assertIn("没有断出来",self.lines[227])
  self.assertGreaterEqual(len(FORMATION_SOURCE),35)

 def test_book_links_and_literally_printed_palace_cells(self):
  self.assertEqual(len(self.refs),25)
  self.assertTrue(all(x["not_new_event"] and x["not_independently_verified_case_match"] for x in self.refs))
  self.assertEqual(len(self.figures),2)
  self.assertEqual(sum(len(x["cells"]) for x in self.figures),18)
  a,b=self.figures
  self.assertEqual(a["pedagogical_stage"],"crossbook_old_case_illustration")
  self.assertEqual(b["pedagogical_stage"],"didactic_five_element_palaces")
  self.assertTrue(all(x["not_new_independent_prediction"] for x in self.figures))
  self.assertEqual(next(x["original_cell_text"] for x in a["cells"] if x["palace"]==5),"中五宫\n庚")
  self.assertTrue(all(x["review_status"]=="draft" for x in self.items))
  self.assertEqual(len(self.items),len({(x["concept_id"],x["source_start_line"]) for x in self.items}))

 def test_full_backup_stem_timing_and_immutability(self):
  self.assertEqual(hashlib.sha256(BASE.read_bytes()).hexdigest(),BASE_SHA)
  with tempfile.TemporaryDirectory() as tmp:
   out=Path(tmp)/"new.sqlite3";index=Path(tmp)/"indices"
   m=build(BASE,SOURCE,out,index)
   self.assertEqual(m["total_source_sections"],25)
   self.assertEqual(m["source_ordered_stem_pair_count"],81)
   self.assertEqual(m["new_independent_historical_cases"],0)
   self.assertEqual(m["new_historical_prediction_charts"],0)
   self.assertEqual(m["source_diagram_palace_cells"],18)
   with sqlite3.connect(out) as db:
    self.assertEqual(db.execute("SELECT count(*) FROM sections").fetchone()[0],25)
    self.assertEqual(db.execute("SELECT count(*) FROM sections WHERE book_id='kaiwu'").fetchone()[0],4)
    self.assertEqual(db.execute("SELECT count(*) FROM cases").fetchone()[0],103)
    self.assertEqual(db.execute("SELECT count(*) FROM historical_case_reasoning").fetchone()[0],495)
    self.assertEqual(db.execute("SELECT count(*) FROM historical_palace_standardization").fetchone()[0],1008)
    self.assertEqual(db.execute("SELECT count(*) FROM kaiwu_ordered_stem_pair_occurrences").fetchone()[0],81)
    self.assertEqual(db.execute("SELECT count(*) FROM kaiwu_didactic_figures").fetchone()[0],14)
    self.assertEqual(db.execute("SELECT count(*) FROM kaiwu_didactic_figure_cells").fetchone()[0],126)
    self.assertEqual(db.execute("SELECT count(*) FROM cross_book_example_references").fetchone()[0],41)
    self.assertEqual(db.execute("SELECT count(*) FROM historical_case_book_verdicts WHERE verdict='author_book_error_explicit'").fetchone()[0],6)
    self.assertEqual(db.execute("SELECT original_text FROM sections WHERE book_id='kaiwu' AND section_key='analysis_judgment_ch04'").fetchone()[0],self.raw.decode("utf-8"))
    self.assertEqual(db.execute("SELECT count(*) FROM semantic_assertions").fetchone()[0],1771+len(self.items))
    self.assertEqual(db.execute("PRAGMA integrity_check").fetchone()[0],"ok")
    self.assertEqual(db.execute("PRAGMA foreign_key_check").fetchall(),[])
   doc=json.loads((index/"chapter_manifest.json").read_text("utf8"))
   self.assertTrue(doc["all_previous_source_rows_preserved"])
   self.assertEqual(doc["source_sha256"],SOURCE_SHA)

if __name__=="__main__":unittest.main()
