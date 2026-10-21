"""Actually execute public JSON-in source-method outcome interface without labels."""
from __future__ import annotations
from pathlib import Path
import json,tempfile,unittest
from scripts.run_marriage_judgment_v16 import main
from src.wengua.casting_shenqi import layout_from_explicit_bureau
ROOT=Path(__file__).resolve().parents[1]
DB=ROOT/"archives/sqlite/WenguaApp_双书194案例_婚姻作者式判断与家族留出评测V1_6_完整研究库.sqlite3"
class PublicJSONDecisionV16(unittest.TestCase):
 def test_first_outcome_and_computed_month_from_actual_book_calendar(self):
  document={
   "chart":layout_from_explicit_bureau(dun="yin",ju=3,hour_ganzhi="丁亥"),
   "calendar_inputs":{"day_ganzhi":"庚申","hour_ganzhi":"丁亥",
    "year_ganzhi":"戊寅","month_ganzhi":"癸亥","solar_term":"立冬",
    "local_time_iso":"1998-11-09T21:22:00+08:00",
    "iana_timezone":"Asia/Shanghai"},
   "inquiry":{"domain":"marriage","scene_id":"marriage.scene.02",
    "question_text":"母亲问儿子与现有对象能否结婚？",
    "relationship":"parent_of_subject",
    "subject":{"year_ganzhi":"丁未"},"partner":{"year_ganzhi":"庚戌"}}}
  with tempfile.TemporaryDirectory() as d:
   f=Path(d)/"chart.json";o=Path(d)/"independent_initial_decision.json"
   f.write_text(json.dumps(document,ensure_ascii=False),encoding="utf8")
   result=main(["--input",str(f),"--database",str(DB),
    "--exclude-event-family","kaiwu.marriage.case01","--output",str(o)])
   self.assertEqual(result["traditional_initial_outcome"],"success")
   self.assertTrue(result["calculated_timing_if_source_condition_met"])
   self.assertEqual(result["calculated_timing_if_source_condition_met"]["timing_calculation"]["trigger_branch"],"子")
   self.assertFalse(result["publication_ready"])
   self.assertTrue(o.is_file())
   self.assertEqual(json.loads(o.read_text("utf8"))["traditional_initial_outcome"],"success")
   self.assertTrue(all(w["event_family_id"]!="kaiwu.marriage.case01" for w in
     result["book_witnesses_excluding_holdout"]["pre_event_method_witnesses"]))
   with self.assertRaises(SystemExit):
    main(["--input",str(f),"--database",str(DB),"--output",str(f)])
if __name__=="__main__":unittest.main()
