"""Marriage first-domain phrase corpus and 1080 x 60 x 3 x 2 review gates."""
import hashlib,json,sqlite3,tempfile,unittest
from pathlib import Path
from src.wengua.core import state_index
from src.wengua.phrase_pipeline import (matrix_cardinality,matrix_base_key,
 FACTOR_IDS,inspect_marriage_input)
from scripts.seed_marriage_phrase_library import ROOT,BASE_SHA,OLD,NEW,PHRASES,seed
BASE=ROOT/"archives/sqlite"/OLD
class MarriagePhrasePilotTest(unittest.TestCase):
 def test_1080_immutable_unique_states_not_assumed_full_charts(self):
  s=state_index()
  self.assertEqual(len(s),1080)
  self.assertEqual(len({v["state_id"] for v in s}),1080)
  self.assertTrue(all(v["status"]=="index_only_unverified_chart" for v in s))
  self.assertEqual(matrix_cardinality(),388800)
  self.assertEqual(matrix_base_key("yang-01-00","甲子","adult","female"),
    ("yang-01-00","甲子","adult","female"))
  for wrong in ("yang-00-00","yang-01-60","whatever"):
   with self.assertRaises(ValueError):
    matrix_base_key(wrong,"甲子","adult","female")
 def test_unverified_charts_and_missing_factors_never_emit_predictions(self):
  invalid=inspect_marriage_input({})
  self.assertNotEqual(invalid["status"],"ready_for_draft_review")
  self.assertFalse(invalid["eligible_to_publish_predictive_reading"])
  chart={"status":"engine_verified","school_id":"shijia_zhuanpan",
   "state_id":"yang-01-00","method_version":"test_only",
   "verification_receipt":"test_only_not_crypto",
   "calendar_inputs":{"time_iso":"2026-01-02T10:00","timezone":"UTC","solar_term_basis":"test"},
   "palaces":[{"palace_id":i,"heaven_stem":"庚","earth_stem":"戊",
    **({} if i==5 else {"door":"开门","star":"天蓬星","deity":"六合"})} for i in range(1,10)]}
  inquiry={"domain":"marriage","question_type":"new_relationship","relationship":"self",
   "querent":{"id":"person"},"subject":{"year_ganzhi":"甲子",
     "age_band":"adult","sex":"female"}}
  data={"chart":chart,"inquiry":inquiry}
  first=inspect_marriage_input(data)
  self.assertIn("missing_or_unchecked_factor:door_press_palace",first["blockers"])
  self.assertFalse(first["eligible_to_publish_predictive_reading"])
  data["calculated_factors"]={key:{"checked":True,"status":"absent",
    "rule_ref":"test:only_not_a_traditional_rule",
    "evidence":{"mocked":True}} for key in FACTOR_IDS}
  ok=inspect_marriage_input(data)
  self.assertEqual(ok["status"],"ready_for_draft_review")
  self.assertEqual(ok["coverage_key"],["yang-01-00","甲子","adult","female"])
  self.assertEqual(ok["factors_checked"],len(FACTOR_IDS))
  self.assertFalse(ok["cast_receipt_cryptographically_verified"])
  self.assertFalse(ok["eligible_to_publish_predictive_reading"])
  data["calculated_factors"]["primary_secondary_yongshen"]={"checked":True,
    "status":"unknown","rule_ref":"no_binding","evidence":{},"reason":"source unspecified"}
  self.assertIn("decisive_unknown_factor:primary_secondary_yongshen",
    inspect_marriage_input(data)["blockers"])
 def test_exact_full_194_database_preserved_and_drafts_in_sqlite(self):
  self.assertEqual(hashlib.sha256(BASE.read_bytes()).hexdigest(),BASE_SHA)
  with tempfile.TemporaryDirectory() as t:
   output=Path(t)/NEW
   index=Path(t)/"index"
   m=seed(BASE,output,index)
   self.assertEqual(m["theoretical_state_year_age_sex_nodes"],388800)
   self.assertTrue(m["all_previous_DB_rows_unchanged"])
   self.assertEqual(m["prototype_human_style_phrase_count"],4)
   self.assertEqual(m["verified_chart_phrase_instances"],0)
   self.assertEqual(m["approved_phrase_instances"],0)
   self.assertEqual(len(PHRASES),4)
   with sqlite3.connect(output) as db:
    for name,count in m["counts"].items():
     self.assertEqual(db.execute('SELECT count(*) FROM "'+name+'"').fetchone()[0],count,name)
    self.assertEqual(db.execute("SELECT count(*) FROM cases").fetchone()[0],194)
    self.assertEqual(db.execute("SELECT count(*) FROM sections").fetchone()[0],43)
    self.assertEqual(db.execute("SELECT count(*) FROM historical_chart_cells").fetchone()[0],1440)
    self.assertEqual(db.execute("SELECT count(*) FROM phrase_context_instances").fetchone()[0],0)
    self.assertEqual(db.execute("SELECT count(*) FROM phrase_template_drafts WHERE review_status='draft' AND chart_instantiated=0").fetchone()[0],4)
    self.assertEqual(db.execute("SELECT count(*) FROM phrase_template_drafts WHERE review_status='approved'").fetchone()[0],0)
    self.assertGreaterEqual(db.execute("SELECT count(*) FROM phrase_source_links").fetchone()[0],8)
    self.assertEqual(db.execute("SELECT source_family_count FROM phrase_domain_progress WHERE domain_id='marriage'").fetchone()[0],14)
    for phrase,conditions,trace in db.execute("SELECT draft_text,rule_conditions_json,reasoning_trace_json FROM phrase_template_drafts"):
     self.assertTrue(160<=sum('\u4e00'<=c<='\u9fff' for c in phrase)<=240)
     self.assertEqual(json.loads(conditions)["unknown"],"abstain")
     self.assertTrue(json.loads(trace)["not_applied_to_any_1080_state"])
    self.assertEqual(db.execute("PRAGMA integrity_check").fetchone()[0],"ok")
    self.assertEqual(db.execute("PRAGMA foreign_key_check").fetchall(),[])
if __name__=="__main__":unittest.main()
