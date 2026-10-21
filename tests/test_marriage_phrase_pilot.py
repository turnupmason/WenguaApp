"""Marriage book 194-case source archive, 4 draft prototypes, concrete timing gate."""
from __future__ import annotations
from datetime import datetime
from hashlib import sha256
import sqlite3,tempfile,unittest
from pathlib import Path
from scripts.seed_marriage_phrase_library import ROOT,BASE_SHA,OLD,NEW,PHRASES,seed
from src.wengua.phrase_pipeline import (
 AGE_BANDS,SEXES,FACTOR_IDS,matrix_cardinality,matrix_base_key,inspect_marriage_input)
from src.wengua.timing_engine import derive_timing_candidates,finalize_traditional_decision
BASE=ROOT/"archives/sqlite"/OLD
class Pilot(unittest.TestCase):
 def test_1080_distinct_state_coordinates_not_1080_verified_nine_palaces(self):
  self.assertEqual(matrix_cardinality(),388800)
  self.assertEqual(matrix_base_key("yang-01-00","甲子","young","male"),
   ("yang-01-00","甲子","young","male"))
  with self.assertRaises(ValueError):matrix_base_key("yang-10-00","甲子","young","male")
  self.assertEqual(len(FACTOR_IDS),24)
  blocked=inspect_marriage_input({"chart":{"state_id":"yang-01-00",
   "school_id":"shijia_zhuanpan"},"inquiry":{"domain":"marriage",
   "subject":{"year_ganzhi":"甲子","age_band":"young","sex":"female"}}})
  self.assertEqual(blocked["status"],"blocked_requires_review")
  self.assertFalse(blocked["eligible_to_publish_predictive_reading"])
  self.assertIn("unverified_nine_palace_cast",blocked["blockers"])
 def test_real_calendar_period_interface_computes_explicit_fill_and_clash(self):
  # Purposefully SYNTHETIC intervals. These are NOT the astronomical months
  # of 2026. The engine, not GPT, must supply verified calendar period rows.
  periods=[
   dict(start_iso="2026-11-04T00:00:00-05:00",end_iso="2026-11-05T00:00:00-05:00",
        branch="午",granularity="day",calendar_method_version="fixture-test"),
   dict(start_iso="2026-11-05T00:00:00-05:00",end_iso="2026-11-06T00:00:00-05:00",
        branch="未",granularity="day",calendar_method_version="fixture-test"),
   dict(start_iso="2026-11-06T00:00:00-05:00",end_iso="2026-11-07T00:00:00-05:00",
        branch="子",granularity="day",calendar_method_version="fixture-test"),
   dict(start_iso="2026-11-07T00:00:00-05:00",end_iso="2026-11-08T00:00:00-05:00",
        branch="丑",granularity="day",calendar_method_version="fixture-test")]
  kw=dict(empty_branches=["午","未"],periods=periods,granularity="day",
          reference_iso="2026-11-01T08:00:00-05:00",
          calendar_method_version="fixture-test",
          calendar_receipt="synthetic-fixture-not-a-real-calendar-receipt",
          source_method_ref="kaiwu:marriage:chapter02_section02:line43")
  fill=derive_timing_candidates(**kw,method="fill_empty")
  clash=derive_timing_candidates(**kw,method="clash_empty")
  self.assertEqual([v["trigger_branch"] for v in fill],["午","未"])
  self.assertEqual([v["trigger_branch"] for v in clash],["子","丑"])
  self.assertEqual(clash[0]["window_start_iso"],"2026-11-06T00:00:00-05:00")
  trace=finalize_traditional_decision(
   outcome="success",reasoned_support=["yi_geng_supported_by_full_chart",
   "liuhe_and_birth_stems_cross_checked"],reasoned_counter=["void_delay_checked"],
   chosen_timing=clash[0],known_timing_candidates=clash,
   timing_choice_rule_ref="kaiwu:marriage:lines39,41,43;candidate_selected_after_mutual_evidence",
   confidence_boundary="traditional_symbolic_judgment_only_not_scientific_forecast")
  self.assertEqual(trace["status"],"conditional_concrete_traditional_forecast")
  self.assertEqual(trace["window_start_iso"],"2026-11-06T00:00:00-05:00")
  self.assertTrue(trace["this_is_not_verified_external_event_prediction"])
  with self.assertRaises(ValueError):
   finalize_traditional_decision(outcome="delayed",reasoned_support=["马星动"],
    reasoned_counter=[],chosen_timing=None,known_timing_candidates=clash,
    timing_choice_rule_ref="book",confidence_boundary="source_only")
  with self.assertRaises(ValueError):
   derive_timing_candidates(**{**kw,"calendar_method_version":""},method="clash_empty")
  with self.assertRaises(ValueError):
   derive_timing_candidates(**{**kw,"periods":[]} ,method="fill_empty")
  with self.assertRaises(ValueError):
   derive_timing_candidates(**{**kw,"reference_iso":"2026-11-01T08:00:00"},method="fill_empty")
 def test_exact_full_parent_prototypes_are_drafts_never_fake_dates(self):
  self.assertEqual(sha256(BASE.read_bytes()).hexdigest(),BASE_SHA)
  self.assertEqual(len(PHRASES),4)
  with tempfile.TemporaryDirectory() as d:
   out=Path(d)/NEW
   manifest=seed(BASE,out,Path(d)/"phrase_index")
   self.assertEqual(manifest["old_historical_events"],194)
   self.assertEqual(manifest["prototype_human_style_phrase_count"],4)
   self.assertEqual(manifest["verified_chart_phrase_instances"],0)
   self.assertEqual(manifest["theoretical_state_year_age_sex_nodes"],388800)
   with sqlite3.connect(out) as db:
    self.assertEqual(db.execute("SELECT COUNT(*) FROM cases").fetchone()[0],194)
    self.assertEqual(db.execute("SELECT COUNT(*) FROM sections").fetchone()[0],43)
    self.assertEqual(db.execute("SELECT COUNT(*) FROM historical_chart_cells").fetchone()[0],1440)
    self.assertEqual(db.execute("SELECT COUNT(*) FROM phrase_source_links").fetchone()[0],9)
    self.assertEqual(db.execute("SELECT COUNT(*) FROM phrase_template_drafts WHERE review_status='draft'").fetchone()[0],4)
    self.assertEqual(db.execute("SELECT COUNT(*) FROM phrase_context_instances").fetchone()[0],0)
    self.assertEqual(db.execute("SELECT COUNT(*) FROM phrase_domain_progress WHERE domain_id='marriage'").fetchone()[0],1)
    self.assertEqual(db.execute("PRAGMA integrity_check").fetchone()[0],"ok")
    self.assertEqual(db.execute("PRAGMA foreign_key_check").fetchall(),[])
if __name__=="__main__":unittest.main()
