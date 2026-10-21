"""Historical-family holdouts test NO label or posterior-answer leakage.

Scores are held-out *source replay* only, not genuinely novel 2026 forecasts.
The first marriage case has already been used in a V1.5 historical timing
regression, so it is NOT counted as an unseen blind success here.
"""
from __future__ import annotations
from pathlib import Path
import sqlite3,unittest
from src.wengua.casting_shenqi import layout_from_explicit_bureau
from src.wengua.marriage_judgment_v16 import (
 analyze_marriage_unseen_chart,_source_witnesses,
 grounded_factor_extensions,_traditional_decision,_load_rules_and_source)
from src.wengua.astro_calendar import solar_chart_clock
ROOT=Path(__file__).resolve().parents[1]
DB=ROOT/"archives/sqlite/WenguaApp_双书194案例_婚姻原书应期天文推算V1_5_完整研究库.sqlite3"
def chart_packet(*,dun,ju,day,hour,date,month,year,term,subject,partner,
                 scene="marriage.scene.02",question="这段感情可否谈成？"):
 return {
  "chart":layout_from_explicit_bureau(dun=dun,ju=ju,hour_ganzhi=hour),
  "calendar_inputs":{"day_ganzhi":day,"hour_ganzhi":hour,"solar_term":term,
    "year_ganzhi":year,"month_ganzhi":month,
    "local_time_iso":date,"iana_timezone":"Asia/Shanghai"},
  "inquiry":{"domain":"marriage","scene_id":scene,
    "question_text":question,"relationship":"parent_of_subject",
    "subject":{"year_ganzhi":subject},"partner":{"year_ganzhi":partner}}}
class InitialBookReasoning(unittest.TestCase):
 def test_original_book_rule_citations_first_outcome_no_case_verdict(self):
  with sqlite3.connect(DB) as db:
   methods=_load_rules_and_source(db)
   self.assertEqual(methods["person_palace"]["rule_ref"],
                    "shenqi/marriage_prediction_ch02/v1:line11")
   self.assertEqual(len(methods["person_palace"]["original_source_sha256"]),64)
 def test_frozen_original_marriage_case01_replay_not_new_blind_success(self):
  p=chart_packet(dun="yin",ju=3,day="庚申",hour="丁亥",
    date="1998-11-09T21:22:00+08:00",term="立冬",year="戊寅",month="癸亥",
    subject="丁未",partner="庚戌",scene="marriage.scene.02",
    question="王大妈代问儿子与现有对象能否结婚？")
  r=analyze_marriage_unseen_chart(
      db_path=DB,payload=p,held_out_family_id="kaiwu.marriage.case01")
  self.assertNotIn(r["status"],("blocked_unverified_calendar","blocked_no_nonheldout_author_method_witness"))
  self.assertEqual(r["traditional_initial_outcome"],"success")
  self.assertTrue(r["book_witnesses_excluding_holdout"]["feedback_text_ever_visible_to_outcome_decider"] is False)
  self.assertTrue(all(x["event_family_id"]!="kaiwu.marriage.case01"
     for x in r["book_witnesses_excluding_holdout"]["pre_event_method_witnesses"]))
  self.assertTrue(r["calculated_timing_if_source_condition_met"])
  t=r["calculated_timing_if_source_condition_met"]
  self.assertEqual(t["outcome"],"success")
  self.assertEqual(t["timing_calculation"]["method"],"clash_empty")
  self.assertEqual(t["timing_calculation"]["trigger_branch"],"子")
  self.assertLess(t["window_start_iso"],"1998-12-16T12:00:00+08:00")
  self.assertGreater(t["window_end_iso"],"1998-12-16T12:00:00+08:00")
  self.assertFalse(r["publication_ready"])
 def test_unseen_family_both_marriage_1998_suitors_are_held_out_by_whole_event(self):
  p=chart_packet(dun="yang",ju=5,day="壬午",hour="辛亥",
    date="1998-06-04T21:30:00+08:00",term="小满",year="戊寅",month="丁巳",
    subject="戊申",partner="丙午",scene="marriage.scene.02",
    question="女儿和第一位求婚对象能否谈成？")
  results=[]
  for partner in ("丙午","乙巳"):
   p["inquiry"]["partner"]["year_ganzhi"]=partner
   r=analyze_marriage_unseen_chart(db_path=DB,payload=p,
                  held_out_family_id="kaiwu.marriage.case03")
   self.assertNotIn(r["status"],("blocked_unverified_calendar","blocked_no_nonheldout_author_method_witness"))
   self.assertTrue(all(x["event_family_id"]!="kaiwu.marriage.case03"
      for x in r["book_witnesses_excluding_holdout"]["pre_event_method_witnesses"]))
   self.assertTrue(r["book_witnesses_excluding_holdout"]["feedback_text_ever_visible_to_outcome_decider"] is False)
   self.assertIn(r["traditional_initial_outcome"],("success","failure","mixed","unresolved"))
   self.assertEqual(r["initial_judgment"]["priority"],
      "primary_real_birth_year_relation_then_secondary_liuhe")
   self.assertFalse(r["publication_ready"])
   results.append(r["traditional_initial_outcome"])
  self.assertEqual(len(results),2)
 def test_no_leakage_by_family_for_all_22_scenes_and_explicit_wrong_case(self):
  with sqlite3.connect(DB) as db:
   allcases=db.execute("""SELECT DISTINCT c.event_family_id FROM marriage22_original_case_links l
    JOIN cases c ON c.case_id=l.original_case_id""").fetchall()
   self.assertGreaterEqual(len(allcases),10)
   checked=0
   for scene in range(1,23):
    key=f"marriage.scene.{scene:02d}"
    for (family,) in allcases:
     w=_source_witnesses(db,key,held_out_family_id=family)
     self.assertNotIn(family,[x["event_family_id"] for x in w["pre_event_method_witnesses"]])
     self.assertTrue(w["feedback_text_ever_visible_to_outcome_decider"] is False)
     for x in w["pre_event_method_witnesses"]:
      self.assertNotEqual(x["case_id"],"kaiwu.marriage.case06")
     checked+=1
   self.assertGreaterEqual(checked,220)
 def test_real_source_relations_are_applied_not_generic_scored_phrases(self):
  p=chart_packet(dun="yin",ju=3,day="庚申",hour="丁亥",
    date="1998-11-09T21:22:00+08:00",term="立冬",year="戊寅",month="癸亥",
    subject="丁未",partner="庚戌")
  r=analyze_marriage_unseen_chart(db_path=DB,payload=p,
       held_out_family_id="kaiwu.marriage.case01")
  facts=r["fact_audit_all_24"]
  self.assertEqual(len(facts),24)
  for k in ("branch_opposition","branch_harm","branch_punishment",
            "month_day_break","seasonal_prosperity","heaven_stem_tomb"):
   self.assertIn(facts[k]["status"],("present","absent"))
   self.assertIn("source_data_sha256",facts[k]["evidence"])
  self.assertFalse(r["complete_24_rule_coverage"])
  self.assertGreaterEqual(r["fact_calculated_count"],10)
if __name__=="__main__":unittest.main()
