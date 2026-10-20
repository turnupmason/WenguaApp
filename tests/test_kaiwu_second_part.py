"""Regression for second Kaiwu chapter: exact source, 120 stem stages, immutable V1."""
import hashlib
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from scripts.build_kaiwu_02_from_01 import (
 BASE_SHA,SOURCE_SHA,BASE_ARCHIVE,BRANCH_PALACE,DEITIES,DOORS,METHODS,
 NEW_ARCHIVE,SIX_JIA,STAGES,STARS,STEM_SEQUENCE,build,extract,figures,
 references,source_lines,ROOT
)

BASE=ROOT/"archives/sqlite"/BASE_ARCHIVE
SOURCE=ROOT/"sources/kaiwu/开悟之门_第二章.txt"

class KaiwuSecondPartTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.raw=SOURCE.read_bytes()
  cls.lines=source_lines(cls.raw)
  cls.records=extract(cls.lines)
 def test_all_original_source_not_figure_as_actual_qimen_chart(self):
  self.assertEqual(hashlib.sha256(self.raw).hexdigest(),SOURCE_SHA)
  self.assertEqual(len(self.raw),56862)
  self.assertEqual(len(self.lines),239)
  f=figures(self.lines)
  self.assertEqual([x["figure"] for x in f],list(range(23,34)))
  self.assertTrue(all(not x["printed_actual_qimen_cast"] for x in f))
  self.assertTrue(self.lines[-1].endswith("之中"))

 def test_ten_stems_all_120_source_anchored_stages(self):
  stages=[x for x in self.records if x["kind"]=="heavenly_stem_twelve_state"]
  self.assertEqual(len(stages),120)
  self.assertEqual(len({(x["normalized"]["stem"],x["normalized"]["stage"]) for x in stages}),120)
  for s,branches in STEM_SEQUENCE.items():
   mine=[x for x in stages if x["normalized"]["stem"]==s]
   self.assertEqual(set(x["normalized"]["stage"] for x in mine),set(STAGES))
   for x in mine:
    self.assertEqual(x["normalized"]["palace"],BRANCH_PALACE[x["normalized"]["branch"]])
  self.assertEqual(STEM_SEQUENCE["戊"],STEM_SEQUENCE["丙"])
  self.assertEqual(STEM_SEQUENCE["己"],STEM_SEQUENCE["丁"])

 def test_four_factors_domain_conditional_and_multitrack(self):
  self.assertEqual(len(SIX_JIA),6)
  self.assertEqual(len(STARS),9)
  self.assertEqual(len(DOORS),8)
  self.assertEqual(len(DEITIES),8)
  self.assertGreaterEqual(len(METHODS),35)
  self.assertEqual(len(references(self.lines)),9)
  self.assertEqual(len(self.records),len({(x["concept_id"],x["source_start_line"]) for x in self.records}))
  star=[x for x in self.records if x["kind"]=="nine_star_wang_xiang_xiu_qiu_fei"]
  self.assertEqual({x["normalized"]["then"] for x in star},{"旺","相","休","废","囚"})
  self.assertTrue(all(x["normalized"]["priority"]=="palace_first_and_month_secondary" for x in star))
  self.assertTrue(any(x["concept_id"]=="kaiwu:four_factors:method:grave_versus_storehouse"
    for x in self.records))
  self.assertTrue(any(x["concept_id"]=="kaiwu:four_factors:method:center_no_ninth_gate"
    for x in self.records))
  self.assertTrue(all(not x["positive_training_eligible"] for x in self.records))

 def test_immutable_full_SQLite_and_section_version(self):
  self.assertEqual(hashlib.sha256(BASE.read_bytes()).hexdigest(),BASE_SHA)
  with tempfile.TemporaryDirectory() as tmp:
   out=Path(tmp)/NEW_ARCHIVE;idx=Path(tmp)/"knowledge"
   doc=build(BASE,SOURCE,out,idx)
   self.assertEqual(doc["total_source_sections"],23)
   self.assertEqual(doc["new_independent_event_families"],0)
   self.assertEqual(doc["new_original_qimen_charts"],0)
   self.assertEqual(doc["new_cross_book_citations"],9)
   with sqlite3.connect(out) as db:
    self.assertEqual(db.execute("SELECT count(*) FROM sections").fetchone()[0],23)
    self.assertEqual(db.execute("SELECT count(*) FROM cases").fetchone()[0],103)
    self.assertEqual(db.execute("SELECT count(*) FROM historical_case_reasoning").fetchone()[0],495)
    self.assertEqual(db.execute("SELECT count(*) FROM historical_palace_standardization").fetchone()[0],1008)
    self.assertEqual(db.execute("SELECT count(*) FROM cross_book_concept_tracks").fetchone()[0],208+len(self.records))
    self.assertEqual(db.execute("SELECT count(*) FROM cross_book_example_references").fetchone()[0],15)
    self.assertEqual(db.execute("SELECT count(*) FROM sections WHERE book_id='kaiwu'").fetchone()[0],2)
    self.assertEqual(db.execute("SELECT sha256 FROM sections WHERE book_id='kaiwu' AND content_version=1 AND section_key='space_time_model_part01'").fetchone()[0],
     "97e2285b25fd97f120ac1015104c6bf750fbba8c3c8bd0228be82b53563d4598")
    self.assertEqual(db.execute("SELECT original_text FROM sections WHERE book_id='kaiwu' AND section_key='four_factors_ch02'").fetchone()[0],self.raw.decode("utf8"))
    self.assertEqual(db.execute("SELECT count(*) FROM historical_case_book_verdicts WHERE verdict='author_book_error_explicit'").fetchone()[0],6)
    self.assertEqual(db.execute("PRAGMA integrity_check").fetchone()[0],"ok")
    self.assertEqual(db.execute("PRAGMA foreign_key_check").fetchall(),[])
   self.assertEqual(json.loads((idx/"chapter_manifest.json").read_text("utf8"))["source_sha256"],SOURCE_SHA)
   self.assertEqual(json.loads((idx/"cross_book_links.json").read_text("utf8"))["no_new_case_or_chart"],True)

if __name__=="__main__":unittest.main()
