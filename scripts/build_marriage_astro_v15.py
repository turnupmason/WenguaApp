"""Append only real computed Kaiwu traditional timing research to full V1.4.

20 exact author timing methods source-hash checked. One actual book family
case01's original author initial conclusion and 1998 Zi/1999 Chou solar
periods are persisted without using its later feedback for candidate
generation. Feedback checking is entirely separate and retrospective.
"""
from __future__ import annotations
import argparse,hashlib,json,sqlite3
from pathlib import Path
from src.wengua.book_timing_runtime import load_source_timing_rules,book_case01_marriage_timing_study
from src.wengua.astro_calendar import EPHEMERIS_VERSION
ROOT=Path(__file__).resolve().parents[1]
PARENT_NAME="WenguaApp_双书194案例_婚姻真实排盘接入V1_4_完整研究库.sqlite3"
OUTPUT_NAME="WenguaApp_双书194案例_婚姻原书应期天文推算V1_5_完整研究库.sqlite3"
PARENT_SHA="ac4401378302319799e0cbf07c906ffdc06ffb2f91ce49e149aac40261c235da"
MIG=ROOT/"schema/migrations/043_marriage_original_book_timing_astro_v15.sql"
INDEX=ROOT/"data/knowledge/phrase_library/marriage_v1_5"
def sha(data):return hashlib.sha256(data).hexdigest()
def js(item):return json.dumps(item,ensure_ascii=False,sort_keys=True,separators=(",",":"))
def check_all_prior_rows(old,db):
 for (table,) in old.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"):
  cols=[r[1] for r in old.execute('PRAGMA table_info("'+table+'")')]
  names=",".join('"'+x+'"' for x in cols)
  before=list(old.execute('SELECT '+names+' FROM "'+table+'"'))
  after=set(db.execute('SELECT '+names+' FROM "'+table+'"'))
  if any(x not in after for x in before):
   raise ValueError("An earlier real source/case/phrase row was overwritten in "+table)
def build(parent,output,indexdir):
 parent,output,indexdir=map(Path,(parent,output,indexdir))
 if output.exists():raise ValueError("Versioned old full SQLite must not be overwritten")
 if sha(parent.read_bytes())!=PARENT_SHA:
  raise ValueError("Only SHA-pinned latest full marriage V1.4 archive allowed")
 rules=load_source_timing_rules()
 source=book_case01_marriage_timing_study()
 output.parent.mkdir(parents=True,exist_ok=True)
 study_id="kaiwu.marriage.case01.author_predicted_zi_chou.v15"
 with sqlite3.connect("file:"+str(parent.resolve())+"?mode=ro",uri=True) as old,sqlite3.connect(output) as db:
  old.backup(db)
  db.executescript(MIG.read_text("utf8"))
  db.execute("PRAGMA foreign_keys=ON")
  with db:
   if db.execute("SELECT COUNT(*) FROM cases").fetchone()[0]!=194:
    raise ValueError("Historic two-book cases missing")
   for key,rule in sorted(rules.items()):
    db.execute("""INSERT INTO book_timing_method_source_rules
      (rule_key,book_id,source_section_key,source_line,category,
       original_book_excerpt,original_book_excerpt_sha256,source_condition_json)
      VALUES (?,'kaiwu','analysis_judgment_ch04',?,?,?,?,?)""",
      (key,rule["source_line"],rule["category"],rule["original_text"],
       rule["excerpt_sha256"],js(rule["conditions"])))
   if db.execute("SELECT COUNT(*) FROM cases WHERE case_id=?",
    (source["original_case_id"],)).fetchone()[0]!=1:
    raise ValueError("No authentic Kaiwu marriage event source family")
   db.execute("""INSERT INTO marriage_author_time_source_studies
    (study_id,source_case_id,book_source_sha256,
     author_original_outcome,author_initial_outcome_lines_json,
     author_initial_timing_line,applied_source_method,
     original_void_branches_json,independent_calendar_version,
     astronomical_clock_receipt_sha256,calculation_status)
    VALUES (?,?,?,?,?,?,?,?,?,?,'original_author_success_then_real_calendar_candidates')""",
    (study_id,source["original_case_id"],source["book_source_exact_sha256"],
     source["original_judgment"],js(source["author_original_success_judgment_lines"]),
     source["author_original_timing_reasoning_line"],"successful_outcome:4",
     js(source["author_original_void_branches"]),
     source["calendar_method_version"],source["source_forecast_calendar_receipt_sha256"]))
   candidates=source["actual_solar_month_candidates_pre_feedback"]
   if len(candidates)!=2:raise ValueError("Two independent expected winter month periods required")
   for ordinal,row in enumerate(candidates,1):
    db.execute("""INSERT INTO marriage_author_timing_month_windows
     (study_id,ordinal,trigger_branch,original_void_branch,
      window_start_iso,window_end_iso,timing_method,computed_calendar_version,
      original_source_timing_line,pre_feedback_candidate)
     VALUES (?,?,?,?,?,?,?, ?,?,1)""",
     (study_id,ordinal,row["trigger_branch"],row["source_empty_branch"],
      row["window_start_iso"],row["window_end_iso"],
      "successful_outcome:4",EPHEMERIS_VERSION,
      source["author_original_timing_reasoning_line"]))
   checks=source["posterior_validation_only_not_prediction_input"]
   if len(checks)!=2 or not all(x["falls_inside_initial_author_candidate_month"] for x in checks):
    raise ValueError("Retrospective original source observations disagree with computed author candidate months")
   for row in checks:
    db.execute("""INSERT INTO marriage_author_time_feedback_validation
      (study_id,event,original_book_feedback_line,
       original_book_feedback_civil_date,calendar_day_ganzhi,
       calendar_month_ganzhi,matching_author_candidate_branch,
       observed_day_inside_candidate_month,later_book_feedback_not_initial_input)
      VALUES (?,?,?,?,?,?,?,1,1)""",
      (study_id,row["event"],row["book_source_line"],row["book_reported_date"],
       row["independent_day_ganzhi"],row["independent_solar_month"],
       row["candidate_trigger"]))
   db.execute("""INSERT INTO marriage_v15_astro_method_audit
    (version,complete_parent_sha256,method_count,
     source_original_marriage_cases_total,source_worked_casting_examples_total,
     new_computed_independently_calculated_event_windows,
     later_feedback_events_separately_checked,original_historical_rows_unchanged,
     ephemeris_model_version,computation_notes_json)
    VALUES ('marriage.book_timing.v1.5',?,20,194,2,2,2,1,?,?)""",
    (PARENT_SHA,EPHEMERIS_VERSION,js({
     "book_pre_feedback_source_lines":"kaiwu.marriage.case01 lines 39/41/43",
     "historical_later_feedback_line":45,
     "two_month_calendar_boundaries_derived_from_solar_longitude":True,
     "astronomical_algorithm":"Meeus apparent Sun longitude approximation; local stdlib no external service",
     "precision_note":"Near 15 degree term instants blocked within 0.05 degrees, month boundaries approximate tens of minutes",
     "not_one_perfect_predicted_wedding_date":True,
     "source_book_success_is_not_independent_proof":True,
     "additional_19_other_timing_methods_stored_but_not_forced_on_marriage_case":True
    })))
  check_all_prior_rows(old,db)
  if db.execute("PRAGMA integrity_check").fetchone()[0]!="ok" or db.execute("PRAGMA foreign_key_check").fetchall():
   raise ValueError("Full 194 source cases/22 scenes SQLite integrity failure")
  db.execute("VACUUM");db.commit()
  tables=["cases","sections","historical_chart_cells","marriage22_scenario_protocol",
          "marriage_runtime_source_cast_fixture","marriage_runtime_scenario_study",
          "phrase_intent_workflows","phrase_template_drafts","phrase_context_instances",
          "book_timing_method_source_rules","marriage_author_time_source_studies",
          "marriage_author_timing_month_windows","marriage_author_time_feedback_validation",
          "marriage_v15_astro_method_audit"]
  counts={name:db.execute('SELECT COUNT(*) FROM "'+name+'"').fetchone()[0] for name in tables}
  expected={
   "cases":194,"sections":43,"historical_chart_cells":1440,
   "marriage22_scenario_protocol":22,
   "marriage_runtime_source_cast_fixture":2,"marriage_runtime_scenario_study":44,
   "phrase_intent_workflows":9,"phrase_template_drafts":4,"phrase_context_instances":0,
   "book_timing_method_source_rules":20,"marriage_author_time_source_studies":1,
   "marriage_author_timing_month_windows":2,
   "marriage_author_time_feedback_validation":2,"marriage_v15_astro_method_audit":1}
  if counts!=expected:raise ValueError(("Unexpected inherited/new row counts",counts,expected))
 report={"schema":"wengua_full_194_cases_marriage_book_astro_timings_v15",
         "parent_complete_archive_sha256":PARENT_SHA,
         "new_full_archive_sha256":sha(output.read_bytes()),
         "fully_preserved_book_historical_cases":194,
         "previous_nine_workflows":9,"previous_twenty_two_scenes":22,
         "original_book_timing_methods":20,
         "astronomically_computed_original_marriage_month_windows":2,
         "posterior_feedback_checks_strictly_separated":2,
         "new_actual_unseen_real_marriage_predictions":0,
         "all_prior_source_and_phrase_rows_exactly_preserved":True,
         "calendar_method":EPHEMERIS_VERSION,
         "single_book_author_timing_study":source,
         "counts":counts}
 indexdir.mkdir(parents=True,exist_ok=True)
 (indexdir/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n","utf8")
 return report
def main():
 parser=argparse.ArgumentParser()
 for k in ("base","output","index-dir"):parser.add_argument("--"+k,required=True)
 opt=parser.parse_args()
 print(js(build(opt.base,opt.output,opt.index_dir)))
if __name__=="__main__":main()
