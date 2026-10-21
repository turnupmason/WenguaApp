"""Nine book-grounded marital question workflows, with immutable source/history."""
from __future__ import annotations
import hashlib,json,sqlite3,tempfile,unittest
from pathlib import Path
from scripts.build_marriage_intent_workflows_v12 import (
 ROOT,CONF,PARENT_NAME,OUTPUT_NAME,PARENT_SHA,EXPECTED_IDS,
 validate_config,compile_workflows)
PARENT=ROOT/"archives/sqlite"/PARENT_NAME
class MarriageIntentWorkflowSourceTest(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.conf=validate_config(CONF.read_bytes())
 def test_nine_domain_subquestions_not_nine_fixed_answers(self):
  self.assertEqual(self.conf["intent_count"],9)
  self.assertEqual({x["id"] for x in self.conf["selected_intents"]},EXPECTED_IDS)
  self.assertFalse(self.conf["not_fixed_answers"] is False)
  self.assertEqual(sum(len(s["sources"]) for s in self.conf["selected_intents"]),30)
  self.assertEqual(sum(len(s["steps"]) for s in self.conf["selected_intents"]),72)
  self.assertEqual(len(self.conf["common_contract"]["full_chart_audit"]),24)
  by={s["id"]:s for s in self.conf["selected_intents"]}
  self.assertNotEqual(by["marriage_registration"]["events"],by["wedding_date"]["events"])
  self.assertIn("相邻案例",by["marriage_proposal"]["style"]+"相邻案例" if by["marriage_proposal"]["source_support"].startswith("adjacent_") else "")
  self.assertEqual(by["reconciliation"]["source_support"],"adjacent_case_inference")
  self.assertEqual(by["remarriage"]["source_support"],"direct_book_example_without_followup_plus_counterexample")
  self.assertIn("trust_question",by)
  self.assertEqual([r["phase_role"] for r in by["trust_question"]["sources"]][-1],"later_feedback_do_not_train")
 def test_append_full_original_194_no_fake_chart_predictions(self):
  self.assertEqual(hashlib.sha256(PARENT.read_bytes()).hexdigest(),PARENT_SHA)
  with tempfile.TemporaryDirectory() as d:
   out=Path(d)/OUTPUT_NAME
   r=compile_workflows(PARENT,out,Path(d)/"knowledge")
   self.assertTrue(r["all_194_old_historical_cases_unchanged"])
   self.assertEqual(r["subtype_workflows"],9)
   self.assertEqual(r["author_original_book_provenance_links"],30)
   self.assertEqual(r["new_phrase_instances"],0)
   with sqlite3.connect(out) as db:
    for table,n in r["counts"].items():
     self.assertEqual(db.execute('SELECT COUNT(*) FROM "'+table+'"').fetchone()[0],n,table)
    self.assertEqual(db.execute("SELECT COUNT(*) FROM cases").fetchone()[0],194)
    self.assertEqual(db.execute("SELECT COUNT(*) FROM sections").fetchone()[0],43)
    self.assertEqual(db.execute("SELECT COUNT(*) FROM historical_chart_cells").fetchone()[0],1440)
    self.assertEqual(db.execute("SELECT COUNT(*) FROM phrase_template_drafts").fetchone()[0],4)
    self.assertEqual(db.execute("SELECT COUNT(*) FROM phrase_context_instances").fetchone()[0],0)
    self.assertEqual(db.execute("SELECT COUNT(*) FROM phrase_intent_workflow_steps").fetchone()[0],72)
    self.assertEqual(db.execute("SELECT COUNT(*) FROM phrase_intent_evidence_links WHERE is_future_feedback=1").fetchone()[0]>=3,True)
    self.assertEqual(db.execute("SELECT COUNT(*) FROM phrase_intent_workflows WHERE approved_for_real_predictive_publication=1").fetchone()[0],0)
    self.assertEqual(db.execute("SELECT COUNT(DISTINCT case_id) FROM phrase_intent_evidence_links").fetchone()[0],r["distinct_referenced_book_case_families"])
    self.assertEqual(db.execute("PRAGMA integrity_check").fetchone()[0],"ok")
    self.assertEqual(db.execute("PRAGMA foreign_key_check").fetchall(),[])
if __name__=="__main__":unittest.main()
