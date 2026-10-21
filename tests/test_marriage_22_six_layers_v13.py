"""Six-layer all-domain hard gate; 22 marriage scenarios exact book-source lineage."""
import hashlib,json,sqlite3,tempfile,unittest
from pathlib import Path
from scripts.build_marriage_22_six_layers_v13 import (
 ROOT,OLD,NEW,PARENT_SHA,CONF,verify_config,build)
from src.wengua.six_layer_contract import LAYERS,audit_all_domains
from src.wengua.phrase_pipeline import FACTOR_IDS
PARENT=ROOT/"archives/sqlite"/OLD
class GlobalSixLayerMarriage22(unittest.TestCase):
 def test_six_stages_are_compulsory_for_any_domain(self):
  self.assertEqual(len(LAYERS),6)
  for domain in ("marriage","employment","health","finance","weather"):
   result=audit_all_domains({"domain":domain,"layer_trace":{}})
   self.assertEqual(result["status"],"blocked_incomplete_pipeline")
   self.assertEqual(result["layers_checked"],6)
   self.assertTrue(any("layer_missing" in msg for msg in result["missing"]))
   self.assertEqual(result["checked_24_physical_factors"],0)
  self.assertEqual(len(FACTOR_IDS),24)
 def test_full_factor_list_and_timing_are_gated_independently(self):
  f={k:{"checked":True,"status":"absent","rule_ref":"test_fixture_not_real_traditional_method",
    "evidence":"fixture"} for k in FACTOR_IDS}
  stages={s:{"status":"passed","source_evidence":["fake unit test"],"rule_version":"fixture"} for s in LAYERS}
  stages[LAYERS[0]].update({"receipt_verified":True,"chart":{"palaces":[{}]*9}})
  stages[LAYERS[1]]["factors"]=f
  stages[LAYERS[2]].update({"intent_id":"job_change","target_event":"got_offer",
    "querent_subject_roles":{"self":"test"},"primary_yongshen":"test",
    "secondary_yongshen":"test"})
  stages[LAYERS[3]].update({"book_case_rule_refs":[{
    "book_id":"shenqi","original_source_sha256":"f"*64,
    "line_numbers":[1],"case_id":"fixture"}],"future_outcome_feedback_as_prediction_input":False})
  stages[LAYERS[4]].update({"traditional_outcome":"delayed",
    "supporting_evidence":["test evidence"],"counterevidence":[],
    "timing_applicable":True})
  stages[LAYERS[5]].update({"user_text":"我判断这件事情会延迟，但不能凭空编造日期。"*6,
    "new_facts_introduced":False})
  b=audit_all_domains({"domain":"employment","layer_trace":stages})
  self.assertEqual(b["status"],"blocked_incomplete_pipeline")
  self.assertEqual(b["checked_24_physical_factors"],24)
  self.assertTrue(any("missing_computed_timing:" in a for a in b["missing"]))
  stages[LAYERS[4]].update({"primary_window":{"start_iso":"2026-11-01T00:00:00-05:00",
   "end_iso":"2026-12-01T00:00:00-05:00"},
    "calendar_method_version":"synthetic_test_fixture",
    "verified_calendar_receipt":"fixture_not_authentic",
    "timing_choice_method_ref":"fake test reference",
    "other_candidates_and_why_rejected":["fixture period"]})
  ready=audit_all_domains({"domain":"employment","layer_trace":stages})
  self.assertEqual(ready["status"],"passed_six_layers_ready_for_external_review")
  self.assertFalse(ready["real_world_predictive_accuracy_guaranteed"])
 def test_22_source_grounded_scenes_append_full_194_and_nine_methods(self):
  cfg=verify_config(CONF.read_bytes())
  self.assertEqual(len(cfg["scenes"]),22)
  self.assertEqual([v["display_number"] for v in cfg["scenes"]],list(range(1,23)))
  self.assertEqual(hashlib.sha256(PARENT.read_bytes()).hexdigest(),PARENT_SHA)
  with tempfile.TemporaryDirectory() as temp:
   output=Path(temp)/NEW
   result=build(PARENT,output,Path(temp)/"knowledge")
   self.assertEqual(result["marriage_scenes"],22)
   self.assertEqual(result["six_layer_mandatory_stage_rows"],132)
   self.assertTrue(result["all_source_and_phrase_prior_rows_unchanged"])
   self.assertGreaterEqual(result["author_source_line_links_inherited"],22)
   with sqlite3.connect(output) as db:
    for table,n in result["counts"].items():
     self.assertEqual(db.execute('SELECT COUNT(*) FROM "'+table+'"').fetchone()[0],n,table)
    self.assertEqual(db.execute("SELECT COUNT(*) FROM cases").fetchone()[0],194)
    self.assertEqual(db.execute("SELECT COUNT(*) FROM phrase_intent_workflows").fetchone()[0],9)
    self.assertEqual(db.execute("SELECT COUNT(*) FROM phrase_template_drafts").fetchone()[0],4)
    self.assertEqual(db.execute("SELECT COUNT(*) FROM marriage22_six_layer_steps WHERE check_required=1").fetchone()[0],132)
    self.assertEqual(db.execute("SELECT COUNT(*) FROM marriage22_scenario_protocol WHERE approved_phrase_count>0").fetchone()[0],0)
    self.assertEqual(db.execute("SELECT COUNT(*) FROM six_layer_instance_trace").fetchone()[0],0)
    self.assertEqual(db.execute("SELECT COUNT(*) FROM marriage22_original_case_links WHERE feedback_not_initial_reasoning=1").fetchone()[0]>0,True)
    self.assertEqual(db.execute("PRAGMA integrity_check").fetchone()[0],"ok")
    self.assertEqual(db.execute("PRAGMA foreign_key_check").fetchall(),[])
if __name__=="__main__":unittest.main()
