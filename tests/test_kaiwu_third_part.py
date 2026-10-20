"""Kaiwu 3: verify entire input and each printed source didactic palace, no historical leakage."""
from __future__ import annotations
import hashlib,json,sqlite3,tempfile,unittest
from pathlib import Path
from scripts.build_kaiwu_03_from_02 import (
 BASE_SHA,BASE_NAME,CHAPTER,FIGURES,NEW_NAME,SOURCE_SHA,STEPS,WORKED,
 ROOT,build,original_lines,read_figures,source_assertions,source_engine_consistency
)
from src.wengua.casting_shenqi import (
 bureau_for_term,hour_ganzhi_from_day,layout_from_explicit_bureau,
 hour_branch_from_wall_clock
)

BASE=ROOT/"archives/sqlite"/BASE_NAME
SOURCE=ROOT/"sources/kaiwu/开悟之门_第三章.txt"

class KaiwuThirdChapterTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.raw=SOURCE.read_bytes()
  cls.lines=original_lines(cls.raw)
  cls.figures=read_figures(cls.lines)
  cls.records=source_assertions(cls.lines,cls.figures)
  cls.checks=source_engine_consistency(cls.figures)

 def test_source_version_and_seven_ordered_methods(self):
  self.assertEqual(hashlib.sha256(self.raw).hexdigest(),SOURCE_SHA)
  self.assertEqual(len(self.raw),22715)
  self.assertEqual(len(self.lines),189)
  self.assertEqual(len(STEPS),7)
  self.assertEqual([x[0] for x in STEPS],list(range(1,8)))
  self.assertEqual(self.lines[0],"纸上井字格起局法的步骤")
  self.assertTrue(all(not x["positive_training_eligible"] for x in self.records))
  self.assertEqual(len(self.records),
    len({(x["concept_id"],x["source_start_line"]) for x in self.records}))

 def test_twelve_didactic_figures_all_nine_source_cells_and_literal_center(self):
  self.assertEqual(len(self.figures),12)
  self.assertEqual([x["caption_line"] for x in self.figures],list(FIGURES))
  self.assertEqual(sum(len(x["cells"]) for x in self.figures),108)
  for fig in self.figures:
   self.assertFalse(fig["actual_historical_prediction"])
   self.assertEqual(sorted(c["palace"] for c in fig["cells"]),list(range(1,10)))
   center=next(c for c in fig["cells"] if c["palace"]==5)
   self.assertTrue(center["source_is_center_bare_or_no_door"])
   self.assertNotIn("／",center["original_cell_text"])
  fully=[x for x in self.figures if x["pedagogical_stage"]=="complete_four_layer"]
  simplified=[x for x in self.figures if x["pedagogical_stage"]=="simplified_chart_no_deities"]
  self.assertEqual(len(fully),2);self.assertEqual(len(simplified),2)
  self.assertTrue(all(not x["complete_deity_information"] for x in simplified))

 def test_four_source_consistency_not_external_calendar_verification(self):
  self.assertEqual(len(self.checks),4)
  self.assertEqual([x["source_caption_line"] for x in self.checks],[139,151,168,180])
  for x in self.checks:
   self.assertEqual(x["checked_peripheral_palaces"],8)
   self.assertTrue(x["not_independent_historical_prediction"])
   # intentionally no scientific or independent ephemeris validation
   self.assertTrue(x["not_astronomical_calendar_verification"])
  self.assertEqual(hour_branch_from_wall_clock(16),"申")
  self.assertEqual(hour_ganzhi_from_day("乙","申"),"甲申")
  source_bureau=bureau_for_term("乙卯","立秋")
  self.assertEqual((source_bureau["dun"],source_bureau["ju"],
                    source_bureau["yuan"],source_bureau["futou"]),
                   ("yin",5,"middle","甲寅"))
  for name,(dun,ju,hour,ln,day,date,full,head,star_p,door_p) in WORKED.items():
   b=layout_from_explicit_bureau(dun=dun,ju=ju,hour_ganzhi=hour)
   self.assertEqual((b["xun_shou"],b["value_star_palace"],b["value_door_palace"]),
     (head,star_p,door_p))

 def test_additive_sqlite_backup_and_book_conflicts_unmodified(self):
  self.assertEqual(hashlib.sha256(BASE.read_bytes()).hexdigest(),BASE_SHA)
  with tempfile.TemporaryDirectory() as temp:
   out=Path(temp)/NEW_NAME;index=Path(temp)/"indices"
   doc=build(BASE,SOURCE,out,index)
   self.assertEqual(doc["total_source_sections"],24)
   self.assertEqual(doc["new_historical_event_families"],0)
   self.assertEqual(doc["source_figure_palace_text_cells"],108)
   self.assertTrue(doc["all_previous_source_rows_preserved"])
   with sqlite3.connect(out) as db:
    self.assertEqual(db.execute("SELECT count(*) FROM sections").fetchone()[0],24)
    self.assertEqual(db.execute("SELECT count(*) FROM sections WHERE book_id='kaiwu'").fetchone()[0],3)
    self.assertEqual(db.execute("SELECT original_text FROM sections WHERE section_key='paper_grid_casting_ch03'").fetchone()[0],self.raw.decode("utf-8"))
    self.assertEqual(db.execute("SELECT count(*) FROM cases").fetchone()[0],103)
    self.assertEqual(db.execute("SELECT count(*) FROM historical_palace_standardization").fetchone()[0],1008)
    self.assertEqual(db.execute("SELECT count(*) FROM historical_case_reasoning").fetchone()[0],495)
    self.assertEqual(db.execute("SELECT count(*) FROM kaiwu_didactic_figure_cells").fetchone()[0],108)
    self.assertEqual(db.execute("SELECT count(*) FROM kaiwu_didactic_figures WHERE verified_against_research_engine=1").fetchone()[0],4)
    self.assertEqual(db.execute("SELECT count(*) FROM historical_case_book_verdicts WHERE verdict='author_book_error_explicit'").fetchone()[0],6)
    self.assertEqual(db.execute("SELECT count(*) FROM cross_book_example_references").fetchone()[0],16)
    self.assertEqual(db.execute("PRAGMA integrity_check").fetchone()[0],"ok")
    self.assertEqual(db.execute("PRAGMA foreign_key_check").fetchall(),[])
   i=json.loads((index/"chapter_manifest.json").read_text("utf-8"))
   self.assertEqual(i["source_sha256"],SOURCE_SHA)
   self.assertEqual(i["new_concept_occurrences"],len(self.records))
   self.assertTrue(i["source_origin_unmodified"])

if __name__=="__main__":unittest.main()
