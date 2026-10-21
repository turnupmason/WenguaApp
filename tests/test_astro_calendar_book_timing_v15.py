"""Real Chinese solar-term ephemeris regression vs TWO historical books.

No fabricated dates; both original Shenqi casting worked days and the Kaiwu
paper-board worked day are compared with an independent Moshier Sun model.
Kaiwu marriage case01's author-before-feedback Zi/Chou timing is computed
from astronomical 30-degree Jie-month boundaries, then separately checked
against book later outcome information.
"""
import unittest
from datetime import datetime
from src.wengua.astro_calendar import solar_chart_clock,branch_periods,EPHEMERIS_VERSION
from src.wengua.book_timing_runtime import load_source_timing_rules,book_case01_marriage_timing_study
class ActualSolarTermAndBookTimingTests(unittest.TestCase):
 def test_shenqi_both_worked_casting_dates_and_kaiwu_third_day(self):
  for civil,day,solar_term,month in [
   ("1995-06-11T12:00:00+08:00","癸酉","芒种","壬午"),
   ("1995-08-13T12:00:00+08:00","丙子","立秋","甲申"),
   ("2001-08-20T12:00:00+08:00","乙卯","立秋","丙申")]:
   with self.subTest(civil=civil):
    clock=solar_chart_clock(civil,"Asia/Shanghai")
    self.assertEqual(clock["four_pillars"]["day"],day)
    self.assertEqual(clock["active_solar_term"],solar_term)
    self.assertEqual(clock["four_pillars"]["month"],month)
    self.assertEqual(clock["method"],EPHEMERIS_VERSION)
    self.assertEqual(len(clock["sha256"]),64)
 def test_lunar_calendar_non_civil_month_boundaries_and_exact_1998_1999_feedback(self):
  earlier=solar_chart_clock("1998-12-05T12:00:00+08:00","Asia/Shanghai")
  later=solar_chart_clock("1998-12-16T12:00:00+08:00","Asia/Shanghai")
  wedding=solar_chart_clock("1999-01-17T12:00:00+08:00","Asia/Shanghai")
  self.assertEqual(earlier["four_pillars"]["month"][1],"亥")
  self.assertEqual(later["four_pillars"]["month"],"甲子")
  self.assertEqual(later["four_pillars"]["day"],"丁酉")
  self.assertEqual(wedding["four_pillars"]["month"],"乙丑")
  self.assertEqual(wedding["four_pillars"]["day"],"己巳")
  periods=branch_periods("1998-11-09T12:00:00+08:00","Asia/Shanghai",
                         granularity="month",days_ahead=160)
  month_by_branch={p["branch"]:p for p in periods}
  self.assertIn("子",month_by_branch)
  self.assertIn("丑",month_by_branch)
  self.assertTrue(
    datetime.fromisoformat(month_by_branch["子"]["start_iso"]).month==12
    and datetime.fromisoformat(month_by_branch["子"]["start_iso"]).day in (6,7,8))
  self.assertTrue(
    datetime.fromisoformat(month_by_branch["丑"]["start_iso"]).month==1
    and datetime.fromisoformat(month_by_branch["丑"]["start_iso"]).day in (5,6,7))
  self.assertLess(month_by_branch["子"]["start_iso"],"1998-12-16T12:00:00+08:00")
  self.assertGreater(month_by_branch["子"]["end_iso"],"1998-12-16T12:00:00+08:00")
  self.assertLess(month_by_branch["丑"]["start_iso"],"1999-01-17T12:00:00+08:00")
  self.assertGreater(month_by_branch["丑"]["end_iso"],"1999-01-17T12:00:00+08:00")
 def test_all_20_original_kaiwu_conditioned_timing_methods_are_source_hash_verified(self):
  x=load_source_timing_rules()
  self.assertEqual(len(x),20)
  self.assertIn("successful_outcome:4",x)
  self.assertIn("failed_outcome:3",x)
  self.assertEqual(x["successful_outcome:4"]["source_line"],184)
  self.assertEqual(x["failed_outcome:3"]["source_line"],199)
 def test_real_book_case01_pre_feedback_timing_then_separate_validation(self):
  data=book_case01_marriage_timing_study()
  self.assertEqual(data["original_case_id"],"kaiwu.marriage.case01")
  self.assertEqual(data["author_original_void_branches"],["午","未"])
  self.assertEqual([x["trigger_branch"] for x in data["actual_solar_month_candidates_pre_feedback"]],["子","丑"])
  self.assertEqual([x["candidate_trigger"] for x in data["posterior_validation_only_not_prediction_input"]],["子","丑"])
  self.assertTrue(all(r["falls_inside_initial_author_candidate_month"]
      for r in data["posterior_validation_only_not_prediction_input"]))
  self.assertTrue(data["first_judgment_does_not_read_book_line45"])
  self.assertTrue(data["not_a_computed_single_legal_registration_day"])
  self.assertTrue(data["historical_book_feedback_is_not_empirical_independent_verification"])
 def test_ephemeris_timezone_and_zi_hour_must_not_be_faked(self):
  with self.assertRaises(ValueError):
   solar_chart_clock("2026-07-01T12:00:00-05:00","America/New_York")
  with self.assertRaises(ValueError):
   solar_chart_clock("2026-10-21T12:00:00","America/New_York")
  with self.assertRaises(ValueError):
   solar_chart_clock("2026-10-21T23:30:00-04:00","America/New_York")
  p=branch_periods("1998-12-15T10:00:00+08:00","Asia/Shanghai",
                  granularity="day",days_ahead=3)
  self.assertEqual(len(p),3)
  self.assertEqual(p[0]["ganzhi"],"丁酉")
if __name__=="__main__":unittest.main()
