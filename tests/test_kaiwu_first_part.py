"""Kaiwu Part 1: source-accurate multi-book provenance and immutable 21-chapter parent."""
import hashlib
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from scripts.build_kaiwu_01_from_21 import (
 BASE_SHA, SOURCE_SHA, BRANCH_MONTH_TERMS, PALACE_NUMBERS,
 build, extract, figure_index, lines_of, ROOT
)

BASE=ROOT/"archives/sqlite/WenguaApp_神奇之门_21章_103案例_完整研究库.sqlite3"
SOURCE=ROOT/"sources/kaiwu/开悟之门_第一篇.txt"
MIGRATION=ROOT/"schema/migrations/017_cross_book_multitrack.sql"

class KaiwuFirstPartTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.raw=SOURCE.read_bytes()
  cls.lines=lines_of(cls.raw)
  cls.items=extract(cls.lines)

 def test_exact_source_and_figures(self):
  self.assertEqual(hashlib.sha256(self.raw).hexdigest(),SOURCE_SHA)
  self.assertEqual(len(self.raw),38067)
  self.assertEqual(len(self.lines),281)
  self.assertEqual(len(figure_index(self.lines)),22)

 def test_crossbook_dedup_and_source_number_logic(self):
  self.assertEqual(len(set((i["concept_id"],i["source_start_line"]) for i in self.items)),len(self.items))
  old_sourced=[i for i in self.items if i["relation_to_shenqi"]=="reaffirms"]
  self.assertGreaterEqual(len(old_sourced),35)
  number_options={int(x["concept_id"].split(":")[1]):x["normalized"]["source_numbers"]
       for x in self.items if x["kind"]=="numerical_symbolism"}
  self.assertEqual(number_options,{k:v for k,v in PALACE_NUMBERS.items()})
  all_terms=[i for i in self.items if i["kind"]=="term_reference_date"]
  self.assertEqual(len(all_terms),24)
  self.assertTrue(all(x["normalized"]["not_exact_ephemeris_for_arbitrary_year"] for x in all_terms))

 def test_month_branch_palaces_not_solar_sector_palaces(self):
  x=[i for i in self.items if i["kind"]=="branch_fixed_palace" and i["concept_id"]=="branch:子"]
  self.assertEqual(len(x),1)
  self.assertEqual(x[0]["normalized"]["palace"],1)
  y=[i for i in self.items if i["kind"]=="three_terms_per_palace"
      and i["concept_id"]=="solar_term:大雪"]
  self.assertEqual(len(y),1)
  self.assertEqual(y[0]["normalized"]["seasonal_sector_palace"],6)
  self.assertNotEqual(x[0]["track_id"],y[0]["track_id"])
  self.assertEqual(len(BRANCH_MONTH_TERMS),12)

 def test_full_increment_preserves_shenqi(self):
  self.assertEqual(hashlib.sha256(BASE.read_bytes()).hexdigest(),BASE_SHA)
  with tempfile.TemporaryDirectory() as tmp:
   out=Path(tmp)/"new.sqlite3"
   index=Path(tmp)/"index"
   manifest=build(BASE,SOURCE,out,index,MIGRATION)
   self.assertEqual(manifest["new_independent_event_families"],0)
   self.assertEqual(manifest["new_original_qimen_charts"],0)
   self.assertEqual(manifest["new_cross_book_citations"],6)
   with sqlite3.connect(out) as db:
    self.assertEqual(db.execute("SELECT COUNT(*) FROM sections").fetchone()[0],22)
    self.assertEqual(db.execute("SELECT COUNT(*) FROM cases").fetchone()[0],103)
    self.assertEqual(db.execute("SELECT COUNT(*) FROM historical_case_reasoning").fetchone()[0],495)
    self.assertEqual(db.execute("SELECT COUNT(*) FROM historical_palace_standardization").fetchone()[0],1008)
    self.assertEqual(db.execute("SELECT COUNT(*) FROM cross_book_concept_tracks").fetchone()[0],
                     len(self.items))
    self.assertEqual(db.execute("PRAGMA integrity_check").fetchone()[0],"ok")
    self.assertEqual(db.execute("PRAGMA foreign_key_check").fetchall(),[])
    self.assertIn("先天八卦",db.execute("SELECT original_text FROM sections WHERE book_id='kaiwu'").fetchone()[0])
   index_doc=json.loads((index/"chapter_manifest.json").read_text("utf8"))
   self.assertEqual(index_doc["source_sha256"],SOURCE_SHA)
   self.assertTrue(index_doc["all_legacy_rows_preserved"])

if __name__=="__main__":
 unittest.main()
