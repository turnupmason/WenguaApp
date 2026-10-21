"""Actual Kaiwu author time-method selection over computed solar-term periods.

All 20 source entries remain intact; candidate calculations ONLY use a
conditionally applicable original method, and only AFTER the source's author
has already judged success/failure in initial reasoning. Historical outcome
feedback is isolated for validation, never used to derive initial timing.
"""
from __future__ import annotations
from pathlib import Path
import hashlib,json
from .astro_calendar import EPHEMERIS_VERSION,solar_chart_clock,branch_periods
from .timing_engine import derive_timing_candidates

ROOT=Path(__file__).resolve().parents[2]
TIMING_SOURCES=ROOT/"data/knowledge/kaiwu/analysis_judgment_ch04/timing_methods.json"
KAIWU_MARRIAGE=ROOT/"sources/kaiwu/开悟之门_恋爱婚姻预测.txt"

def load_source_timing_rules():
 source=json.loads(TIMING_SOURCES.read_text("utf8"))
 rules=source.get("methods")
 if source.get("chapter_key")!="kaiwu/analysis_judgment_ch04/v1" or len(rules)!=20:
  raise ValueError("Need all original Kaiwu 20 conditional timing method records")
 result={}
 for rule in rules:
  name=rule["method_key"]
  if name in result:raise ValueError("Duplicate source timing method: "+name)
  if hashlib.sha256(rule["original_text"].encode("utf8")).hexdigest()!=rule["excerpt_sha256"]:
   raise ValueError("Exact source excerpt SHA mismatch: "+name)
  if rule["conditions"]["source_line"]!=rule["source_line"]:
   raise ValueError("Source line metadata changed")
  result[name]=rule
 return result

def book_case01_marriage_timing_study():
 """Original author's 1998 forecast: infer seasonal windows, then compare.

 This case author's PRE-FEEDBACK reasoning (book lines 39/41/43) says marriage
 can occur, 六合 at Li9 void in 甲申旬 午未空, 子丑月冲实.
 The known dates at line45 are NEVER used in the candidate-generation input.
 """
 rules=load_source_timing_rules()
 source_text=KAIWU_MARRIAGE.read_text("utf8").splitlines()
 if not (
  "甲申旬中午、未空，子月丑月冲实" in source_text[42]
  and "庚为男，乙为女" in source_text[38]
  and "年命丁未" in source_text[40]
  and "12月16日" in source_text[44] and "1999年1月17日" in source_text[44]
 ):
  raise ValueError("Original Kaiwu case01 source lines no longer match")
 original=source_text[42]
 clock=solar_chart_clock("1998-11-09T12:00:00+08:00","Asia/Shanghai")
 periods=branch_periods("1998-11-09T12:00:00+08:00","Asia/Shanghai",
                        granularity="month",days_ahead=150)
 # Author first determines marriage can happen (lines 39/41) BEFORE choosing
 # the timing method in line 43. Do not use line 45 for this determination.
 rule=rules["successful_outcome:4"]
 rule_ref=f"kaiwu/analysis_judgment_ch04/v1:line{rule['source_line']}"
 for t in periods:
  if t["calendar_method_version"]!=EPHEMERIS_VERSION:
   raise ValueError("Inconsistent ephemeris method")
 all_raw=derive_timing_candidates(empty_branches=["午","未"],
            periods=periods,granularity="month",method="clash_empty",
            reference_iso="1998-11-09T12:00:00+08:00",
            calendar_method_version=EPHEMERIS_VERSION,
            calendar_receipt=clock["sha256"],source_method_ref=rule_ref)
 anticipated=[c for c in all_raw if c["trigger_branch"] in ("子","丑")]
 if len(anticipated)<2:raise ValueError("Original author's two winter-month timing events not computed")
 firsttwo=anticipated[:2]
 if [p["trigger_branch"] for p in firsttwo]!=["子","丑"]:
  raise ValueError("Book order of 1998-99 Zi/Chou month not honored")
 # Only after the predictions above are frozen, independently calculate
 # month/day pillars for later book feedback dates.
 observed=[
   {"event":"legal_marriage_registration","date":"1998-12-16",
    "calendar":solar_chart_clock("1998-12-16T12:00:00+08:00","Asia/Shanghai"),
    "source_feedback_line":45},
   {"event":"wedding_ceremony","date":"1999-01-17",
    "calendar":solar_chart_clock("1999-01-17T12:00:00+08:00","Asia/Shanghai"),
    "source_feedback_line":45}]
 for item in observed:
  day,month=item["calendar"]["four_pillars"]["day"],item["calendar"]["four_pillars"]["month"]
  if item["event"]=="legal_marriage_registration":
   if (day,month)!=("丁酉","甲子"):
    raise ValueError("Independent calendar fails book marriage registration day/month")
  elif item["event"]=="wedding_ceremony":
   if (day,month[1])!=("己巳","丑"):
    raise ValueError("Independent calendar fails book wedding day/month")
 def inside(observed_iso,window):
  return window["window_start_iso"]<=observed_iso<window["window_end_iso"]
 feedback_checks=[
   {"event":item["event"],"book_reported_date":item["date"],
    "book_source_line":item["source_feedback_line"],
    "independent_solar_month":item["calendar"]["four_pillars"]["month"],
    "independent_day_ganzhi":item["calendar"]["four_pillars"]["day"],
    "falls_inside_initial_author_candidate_month":inside(
     item["date"]+"T12:00:00+08:00",window),
    "candidate_trigger":window["trigger_branch"]}
    for item,window in zip(observed,firsttwo)]
 return {
  "status":"historical_author_timing_method_computed_and_feedback_separated",
  "original_case_id":"kaiwu.marriage.case01",
  "book_source_exact_sha256":hashlib.sha256(KAIWU_MARRIAGE.read_bytes()).hexdigest(),
  "author_original_success_judgment_lines":[39,41],
  "author_original_timing_reasoning_line":43,
  "source_timing_rule_ref":rule_ref,
  "original_judgment":"作者原文判定婚事能成（与现代世界事件真值保证区分）",
  "author_original_void_branches":["午","未"],
  "timing_algorithm":"real_ephemeris_solar_month_clash_empty_after_book_success_verdict",
  "actual_solar_month_candidates_pre_feedback":firsttwo,
  "all_competing_calculated_windows":all_raw,
  "posterior_validation_only_not_prediction_input":feedback_checks,
  "first_branch_month_selected_for_first_potential_event":"子",
  "second_branch_month_for_possible_followup":"丑",
  "not_a_computed_single_legal_registration_day":True,
  "historical_book_feedback_is_not_empirical_independent_verification":True,
  "first_judgment_does_not_read_book_line45":True,
  "calendar_method_version":EPHEMERIS_VERSION,
  "source_forecast_calendar_receipt_sha256":clock["sha256"]}
