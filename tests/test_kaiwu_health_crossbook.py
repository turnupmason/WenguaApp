"""Kaiwu health chapter: 5 new events + 1 ShinQi same-event witness, all six real boards."""
from __future__ import annotations
import hashlib,json,sqlite3,tempfile,unittest
from pathlib import Path
from scripts.build_kaiwu_health_from_05 import (
 ROOT,BASE_NAME,BASE_SHA,SOURCE_SHA,OLD_FATHER,NEW_NAME,
 DATA,EDITOR,original,scenarios,source_assertions,scenario_phases,build
)
SOURCE=ROOT/"sources/kaiwu/开悟之门_人体疾病预测.txt"
BASE=ROOT/"archives/sqlite"/BASE_NAME

class KaiwuHealthCrossBookTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.raw=SOURCE.read_bytes()
  cls.lines=original(cls.raw)
  cls.events=scenarios(cls.lines)
  cls.assertions=source_assertions(cls.lines,cls.events)
 def test_exact_source_all_six_printed_charts(self):
  self.assertEqual(len(self.raw),20283)
  self.assertEqual(hashlib.sha256(self.raw).hexdigest(),SOURCE_SHA)
  self.assertEqual(len(self.lines),211)
  self.assertEqual(self.lines[2],"第一节 人体疾病预测(共6例)")
  self.assertEqual(len(self.events),6)
  self.assertEqual([x["chart"] for x in self.events],[11,53,69,97,125,171])
  for e in self.events:
   self.assertEqual(len(e["cells"]),9)
   self.assertEqual(sorted(c["palace"] for c in e["cells"]),list(range(1,10)))
   cen=next(c for c in e["cells"] if c["palace"]==5)
   self.assertEqual(cen["deity"],"")
   self.assertEqual(cen["star"],"")
   self.assertIn(cen["door"],("乙","庚","丙","禽乙","禽庚"))
   self.assertEqual(sum(c["unknowns"] for c in e["cells"]),
      2 if e["key"]=="three_b" else 0)
  self.assertEqual(self.events[3]["cells"][8]["star"],"逢戊")
  self.assertEqual(self.events[3]["cells"][0]["deity"],"虎")
  self.assertEqual(self.events[3]["cells"][3]["deity"],"虎")
 def test_identical_prior_father_and_incomplete_a_not_new_blind_case(self):
  self.assertEqual(sum(x["existing"] for x in self.events),1)
  self.assertEqual(len([x for x in self.events if not x["existing"]]),5)
  self.assertEqual(self.events[2]["id"],OLD_FATHER)
  self.assertEqual(self.events[1]["pred"],None)
  self.assertEqual(self.events[1]["steps"],[85,87,89])
  for case in self.events[1:3]:
   p=scenario_phases(case,self.lines)
   self.assertFalse(any(x["kind"]=="author_initial_prediction" for x in p))
   self.assertTrue(any(x["kind"]=="source_retrospective_comparison" for x in p))
  self.assertIn("人还活着",self.lines[80])
  self.assertIn("近期必死",self.lines[80])
 def test_separate_animal_event_feedback_and_medical_report(self):
  hen=self.events[3];rooster=self.events[4];surgery=self.events[5]
  self.assertEqual(hen["subdomain"],"animal_health")
  self.assertEqual(rooster["subdomain"],"animal_health")
  self.assertEqual(hen["feedback"],(119,119))
  self.assertIn("已经10点零5分",self.lines[118])
  self.assertEqual(rooster["pred"],(145,145))
  self.assertIn("庚子日",self.lines[144])
  self.assertEqual(surgery["q"],[161,169])
  self.assertIn("颅内长了肿瘤",self.lines[160])
  self.assertEqual(surgery["feedback"],(209,209))
  self.assertTrue(all(x["subdomain"] in ("human_health","animal_health") for x in self.events))
  self.assertEqual(len(self.assertions),21+len(EDITOR))
  self.assertEqual(len({(x["concept_id"],x["line"]) for x in self.assertions}),len(self.assertions))
 def test_full_sqlite_backup_unified_health_domain_and_legacy_immutability(self):
  self.assertEqual(hashlib.sha256(BASE.read_bytes()).hexdigest(),BASE_SHA)
  with tempfile.TemporaryDirectory() as td:
   out=Path(td)/NEW_NAME;index=Path(td)/"idx"
   m=build(BASE,SOURCE,out,index)
   self.assertEqual(m["new_event_families"],5)
   self.assertEqual(m["shared_old_event_families"],1)
   self.assertEqual(m["new_independent_historical_charts"],5)
   self.assertEqual(m["total_source_sections"],27)
   with sqlite3.connect(out) as db:
    for table,n in m["cumulative_counts"].items():
     self.assertEqual(db.execute('SELECT count(*) FROM "'+table+'"').fetchone()[0],n)
    self.assertEqual(db.execute("SELECT count(*) FROM cases").fetchone()[0],108)
    self.assertEqual(db.execute("SELECT count(*) FROM health_crossbook_witness_palaces").fetchone()[0],54)
    self.assertEqual(db.execute("SELECT count(*) FROM health_crossbook_comparison_steps").fetchone()[0],6)
    self.assertEqual(db.execute("SELECT count(*) FROM historical_case_reasoning").fetchone()[0],516)
    self.assertEqual(db.execute("SELECT count(*) FROM historical_case_book_verdicts WHERE verdict='author_book_error_explicit'").fetchone()[0],6)
    self.assertEqual(db.execute("SELECT count(*) FROM health_crossbook_case_witnesses WHERE case_id=?",(OLD_FATHER,)).fetchone()[0],1)
    self.assertEqual(db.execute("SELECT count(*) FROM cases WHERE case_id=?",(OLD_FATHER,)).fetchone()[0],1)
    self.assertEqual(db.execute("SELECT count(*) FROM cases WHERE domain_id='health'").fetchone()[0]>=11,True)
    self.assertEqual(db.execute("SELECT original_text FROM sections WHERE section_key='health_prediction_ch02_section01'").fetchone()[0],self.raw.decode("utf-8"))
    self.assertEqual(db.execute("SELECT count(*) FROM health_crossbook_witness_palaces WHERE has_explicit_missing_text=1").fetchone()[0],1)
    self.assertEqual(db.execute("PRAGMA integrity_check").fetchone()[0],"ok")
    self.assertEqual(db.execute("PRAGMA foreign_key_check").fetchall(),[])
   doc=json.loads((index/"source_audit.json").read_text("utf-8"))
   self.assertTrue(doc["cross_book_father_event_not_double_counted"])
   self.assertTrue(doc["hen_dead_on_check_at_10_05_exact_death_time_unknown"])
   self.assertTrue(doc["rooster_original_missing_stems_count"]==2)

if __name__=="__main__":unittest.main()
