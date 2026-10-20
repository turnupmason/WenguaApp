"""回归: Kaiwu恋爱婚姻 six cases share Shenqi marriage domain, literal six boards.
Case6 has explicitly incorrect initial reading and two unprinted mentioned casts.
"""
from __future__ import annotations
import hashlib,json,sqlite3,tempfile,unittest
from pathlib import Path
from scripts.build_kaiwu_marriage_from_hot_topics import (
 BASE_NAME,BASE_SHA,NEW_NAME,SOURCE_SHA,ROOT,SPEC,
 parse_original,board,parsed,build
)
BASE=ROOT/"archives/sqlite"/BASE_NAME
SOURCE=ROOT/"sources/kaiwu/开悟之门_恋爱婚姻预测.txt"

class KaiwuRelationshipTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.raw=SOURCE.read_bytes()
  cls.lines=parse_original(cls.raw)
  cls.events=parsed(cls.lines)
 def test_source_exact_unmodified_and_six_actual_printed_panels(self):
  self.assertEqual(len(self.raw),34960)
  self.assertEqual(len(self.lines),305)
  self.assertEqual(hashlib.sha256(self.raw).hexdigest(),SOURCE_SHA)
  self.assertEqual(len(self.events),6)
  self.assertEqual([e["chart"] for e in self.events],[15,57,105,143,195,265])
  self.assertEqual([len(e["cells"]) for e in self.events],[9]*6)
  for e in self.events:
   self.assertEqual(sorted(c["palace"] for c in e["cells"]),list(range(1,10)))
   center=next(c for c in e["cells"] if c["palace"]==5)
   self.assertEqual(center["deity"],"")
   self.assertEqual(center["star"],"")
   self.assertIn(center["door"],("丙","癸","戊","壬","乙"))
  self.assertEqual(sum(len(e["step"]) for e in self.events),26)
 def test_related_person_different_event_and_domains(self):
  a,b=self.events[1:3]
  self.assertNotEqual(a["id"],b["id"])
  self.assertEqual(a["date"],"1997-02-23")
  self.assertEqual(b["date"],"1998-06-04")
  self.assertIn("employment",self.events[3]["facets"])
  self.assertIn("lost_property",self.events[3]["facets"])
  self.assertIn("business_profit",self.events[4]["facets"])
  self.assertTrue(all("marriage" in e["facets"] for e in self.events))
  self.assertIn("结婚证",self.lines[44])
  self.assertIn("办理了离婚手续",self.lines[92])
 def test_case_six_first_reading_wrong_and_unprinted_charts_not_invented(self):
  self.assertEqual(self.events[5]["chart"],265)
  self.assertTrue(self.events[5]["explicit_error"])
  self.assertIn("出生时间局在此省略",self.lines[260])
  self.assertIn("具体格局略",self.lines[302])
  self.assertIn("所测与所问大相径庭",self.lines[296])
  self.assertIn("我爱上了他",self.lines[300])
  self.assertIn("准确度应该说是极低的",self.lines[296])
  self.assertNotIn("我爱上了他",self.lines[258])
 def test_complete_sqlite_old_rows_immutable_new_six_accepted_and_provenance(self):
  self.assertEqual(hashlib.sha256(BASE.read_bytes()).hexdigest(),BASE_SHA)
  with tempfile.TemporaryDirectory() as folder:
   out=Path(folder)/NEW_NAME;idx=Path(folder)/"idx"
   m=build(BASE,SOURCE,out,idx)
   self.assertEqual(m["new_unique_historical_events"],6)
   self.assertEqual(m["new_actual_printed_qimen_casts"],6)
   self.assertEqual(m["total_historical_cases"],127)
   self.assertEqual(m["total_original_historical_printed_casts"],143)
   with sqlite3.connect(out) as db:
    for table,n in m["counts"].items():
     self.assertEqual(db.execute('SELECT COUNT(*) FROM "'+table+'"').fetchone()[0],n)
    self.assertEqual(db.execute("SELECT COUNT(*) FROM cases").fetchone()[0],127)
    self.assertEqual(db.execute("SELECT COUNT(*) FROM historical_case_book_verdicts WHERE verdict='author_book_error_explicit'").fetchone()[0],8)
    self.assertEqual(db.execute("SELECT COUNT(*) FROM crossbook_relationship_literal_palaces").fetchone()[0],54)
    self.assertEqual(db.execute("SELECT COUNT(*) FROM crossbook_relationship_missing_casts").fetchone()[0],2)
    self.assertEqual(db.execute("SELECT COUNT(*) FROM crossbook_relationship_source_errors").fetchone()[0],1)
    self.assertEqual(db.execute("SELECT COUNT(*) FROM historic_book_case_acceptance").fetchone()[0],19)
    self.assertEqual(db.execute("SELECT COUNT(*) FROM relationships_across_all_books").fetchone()[0]>=12,True)
    self.assertEqual(db.execute("SELECT original_text FROM sections WHERE section_key='marriage_prediction_ch02_section02' AND book_id='kaiwu'").fetchone()[0],self.raw.decode("utf-8"))
    self.assertEqual(db.execute("PRAGMA integrity_check").fetchone()[0],"ok")
    self.assertEqual(db.execute("PRAGMA foreign_key_check").fetchall(),[])
   audit=json.loads((idx/"source_audit.json").read_text("utf-8"))
   self.assertTrue(audit["case6_orientation_never_treated_as_disease"])
   self.assertTrue(audit["case2_3_same_person_but_different_dated_question"])

if __name__=="__main__":unittest.main()
