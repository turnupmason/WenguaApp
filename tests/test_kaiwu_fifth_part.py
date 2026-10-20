"""《开悟之门》第五章：12古文+12作者解说的逐字双轨回归。"""
from __future__ import annotations
import hashlib,json,sqlite3,tempfile,unittest
from pathlib import Path
from scripts.build_kaiwu_05_from_04 import (
 BASE_NAME,BASE_SHA,CHAPTER,NEW_NAME,SOURCE_SHA,MOTIFS,ROOT,
 build,evidence,get_lines,pairs
)

BASE=ROOT/"archives/sqlite"/BASE_NAME
SOURCE=ROOT/"sources/kaiwu/开悟之门_第五章.txt"

class KaiwuFifthChapterTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.raw=SOURCE.read_bytes()
  cls.lines=get_lines(cls.raw)
  cls.verses=pairs(cls.lines)
  cls.items,cls.motifs=evidence(cls.lines,cls.verses)
 def test_original_exact_12_verses_and_12_explanations(self):
  self.assertEqual(len(self.raw),37219)
  self.assertEqual(len(self.lines),73)
  self.assertEqual(hashlib.sha256(self.raw).hexdigest(),SOURCE_SHA)
  self.assertEqual(len(self.verses),12)
  self.assertEqual([(x["verse_source_line"],x["commentary_source_line"]) for x in self.verses],
                   [(4+6*i,7+6*i) for i in range(12)])
  self.assertEqual(self.verses[0]["verse_original"][:6],"其法先明戴九")
  self.assertIn("我提倡用拆补法定局",self.verses[0]["commentary_original"])
  self.assertIn("用置闰法定局",self.verses[0]["commentary_original"])
  self.assertEqual(self.verses[-1]["verse_source_line"],70)
  self.assertTrue(self.verses[-1]["commentary_original"].endswith("在实践中去体会去领悟了。"))

 def test_all_source_motifs_exact_provenance_draft_not_invented_rules(self):
  self.assertEqual(len(self.motifs),len(MOTIFS))
  self.assertGreaterEqual(len(self.motifs),95)
  self.assertEqual(len(self.items),24+len(self.motifs))
  self.assertEqual(len({(x["concept_id"],x["source_start_line"]) for x in self.items}),len(self.items))
  self.assertTrue(all(x["review_status"]=="draft" and
   not x["positive_training_eligible"] for x in self.items))
  for m in self.motifs:
   self.assertIn(m["source_excerpt"],self.lines[m["source_line"]-1])
   self.assertEqual(hashlib.sha256(m["source_excerpt"].encode("utf-8")).hexdigest(),m["excerpt_sha256"])
  keys={(x["verse_number"],x["layer"],x["concept_id"]) for x in self.motifs}
  self.assertIn((10,"author_explanation","stem_pair:戊:丙"),keys)
  self.assertIn((10,"author_explanation","stem_pair:丙:戊"),keys)
  self.assertIn((11,"author_explanation","fate:marriage:yi_guest_ding_host"),keys)
  self.assertIn((11,"author_explanation","fate:marriage:ding_guest_yi_host"),keys)
  self.assertIn((1,"author_explanation","casting:bureau:chaibu_preferred"),keys)

 def test_no_historical_casts_old_explanations_not_replaced(self):
  self.assertEqual(sum("《神奇之门》" in ln for ln in self.lines),1)
  self.assertEqual(sum("│" in ln for ln in self.lines),0)
  self.assertIn("天芮星旺相得地",self.lines[36])
  self.assertTrue(any(x["track_id"].endswith(":author_explanation")
   for x in self.items))
  self.assertTrue(any(x["track_id"].endswith(":ancient_verse")
   for x in self.items))

 def test_append_only_real_sqlite_and_old_error_preservation(self):
  self.assertEqual(hashlib.sha256(BASE.read_bytes()).hexdigest(),BASE_SHA)
  with tempfile.TemporaryDirectory() as td:
   out=Path(td)/NEW_NAME;index=Path(td)/"knowledge"
   doc=build(BASE,SOURCE,out,index)
   self.assertEqual(doc["total_source_sections"],26)
   self.assertEqual(doc["contextual_source_motifs"],len(self.motifs))
   self.assertEqual(doc["new_semantic_source_occurrences"],len(self.items))
   self.assertEqual(doc["new_historical_event_families"],0)
   self.assertEqual(doc["new_original_qimen_case_charts"],0)
   with sqlite3.connect(out) as db:
    self.assertEqual(db.execute("SELECT count(*) FROM sections").fetchone()[0],26)
    self.assertEqual(db.execute("SELECT count(*) FROM sections WHERE book_id='kaiwu'").fetchone()[0],5)
    self.assertEqual(db.execute("SELECT count(*) FROM cases").fetchone()[0],103)
    self.assertEqual(db.execute("SELECT count(*) FROM historical_case_reasoning").fetchone()[0],495)
    self.assertEqual(db.execute("SELECT count(*) FROM historical_palace_standardization").fetchone()[0],1008)
    self.assertEqual(db.execute("SELECT count(*) FROM kaiwu_ordered_stem_pair_occurrences").fetchone()[0],81)
    self.assertEqual(db.execute("SELECT count(*) FROM kaiwu_timing_source_methods").fetchone()[0],20)
    self.assertEqual(db.execute("SELECT count(*) FROM kaiwu_classical_verse_explanations").fetchone()[0],12)
    self.assertEqual(db.execute("SELECT count(*) FROM kaiwu_classical_fate_motifs").fetchone()[0],len(MOTIFS))
    self.assertEqual(db.execute("SELECT count(*) FROM cross_book_example_references").fetchone()[0],42)
    self.assertEqual(db.execute("SELECT count(*) FROM historical_case_book_verdicts WHERE verdict='author_book_error_explicit'").fetchone()[0],6)
    self.assertEqual(db.execute("SELECT original_text FROM sections WHERE book_id='kaiwu' AND section_key='classical_fate_exposition_ch05'").fetchone()[0],self.raw.decode("utf-8"))
    self.assertEqual(db.execute("SELECT count(*) FROM semantic_assertions").fetchone()[0],2034+len(self.items))
    self.assertEqual(db.execute("PRAGMA integrity_check").fetchone()[0],"ok")
    self.assertEqual(db.execute("PRAGMA foreign_key_check").fetchall(),[])
   self.assertTrue(json.loads((index/"chapter_manifest.json").read_text("utf8"))["all_previous_rows_unchanged"])

if __name__=="__main__":unittest.main()
