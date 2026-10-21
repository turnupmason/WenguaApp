-- 043: Source-verified Kaiwu 20 timing method catalogue and calculated Jie months.
-- Append-only from V1.4 full 194 historical cases + 22 marriage scene methods.
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS book_timing_method_source_rules (
 rule_key TEXT PRIMARY KEY,
 book_id TEXT NOT NULL CHECK(book_id='kaiwu'),
 source_section_key TEXT NOT NULL,
 source_line INTEGER NOT NULL CHECK(source_line>0),
 category TEXT NOT NULL CHECK(category IN ('successful_outcome','failed_outcome','interception_recovery','limitation')),
 original_book_excerpt TEXT NOT NULL,
 original_book_excerpt_sha256 TEXT NOT NULL CHECK(length(original_book_excerpt_sha256)=64),
 source_condition_json TEXT NOT NULL CHECK(json_valid(source_condition_json)),
 source_rule_kind TEXT NOT NULL DEFAULT 'research_book_rule_not_outcome_guarantee',
 CHECK(source_rule_kind='research_book_rule_not_outcome_guarantee')
);
CREATE TABLE IF NOT EXISTS marriage_author_time_source_studies (
 study_id TEXT PRIMARY KEY,
 source_case_id TEXT NOT NULL REFERENCES cases(case_id),
 book_source_sha256 TEXT NOT NULL CHECK(length(book_source_sha256)=64),
 author_original_outcome TEXT NOT NULL,
 author_initial_outcome_lines_json TEXT NOT NULL CHECK(json_valid(author_initial_outcome_lines_json)),
 author_initial_timing_line INTEGER NOT NULL,
 applied_source_method TEXT NOT NULL REFERENCES book_timing_method_source_rules(rule_key),
 original_void_branches_json TEXT NOT NULL CHECK(json_valid(original_void_branches_json)),
 independent_calendar_version TEXT NOT NULL,
 astronomical_clock_receipt_sha256 TEXT NOT NULL CHECK(length(astronomical_clock_receipt_sha256)=64),
 calculation_status TEXT NOT NULL CHECK(calculation_status='original_author_success_then_real_calendar_candidates'),
 new_independent_prediction_on_live_unseen_chart INTEGER NOT NULL DEFAULT 0 CHECK(new_independent_prediction_on_live_unseen_chart=0),
 feedback_as_initial_reasoning INTEGER NOT NULL DEFAULT 0 CHECK(feedback_as_initial_reasoning=0)
);
CREATE TABLE IF NOT EXISTS marriage_author_timing_month_windows (
 study_id TEXT NOT NULL REFERENCES marriage_author_time_source_studies(study_id),
 ordinal INTEGER NOT NULL CHECK(ordinal>0),
 trigger_branch TEXT NOT NULL,
 original_void_branch TEXT NOT NULL,
 window_start_iso TEXT NOT NULL,
 window_end_iso TEXT NOT NULL,
 timing_method TEXT NOT NULL REFERENCES book_timing_method_source_rules(rule_key),
 computed_calendar_version TEXT NOT NULL,
 original_source_timing_line INTEGER NOT NULL,
 pre_feedback_candidate INTEGER NOT NULL CHECK(pre_feedback_candidate=1),
 PRIMARY KEY(study_id,ordinal)
);
CREATE TABLE IF NOT EXISTS marriage_author_time_feedback_validation (
 study_id TEXT NOT NULL REFERENCES marriage_author_time_source_studies(study_id),
 event TEXT NOT NULL,
 original_book_feedback_line INTEGER NOT NULL,
 original_book_feedback_civil_date TEXT NOT NULL,
 calendar_day_ganzhi TEXT NOT NULL,
 calendar_month_ganzhi TEXT NOT NULL,
 matching_author_candidate_branch TEXT NOT NULL,
 observed_day_inside_candidate_month INTEGER NOT NULL CHECK(observed_day_inside_candidate_month=1),
 later_book_feedback_not_initial_input INTEGER NOT NULL CHECK(later_book_feedback_not_initial_input=1),
 PRIMARY KEY(study_id,event)
);
CREATE TABLE IF NOT EXISTS marriage_v15_astro_method_audit (
 version TEXT PRIMARY KEY,
 complete_parent_sha256 TEXT NOT NULL CHECK(length(complete_parent_sha256)=64),
 method_count INTEGER NOT NULL CHECK(method_count=20),
 source_original_marriage_cases_total INTEGER NOT NULL CHECK(source_original_marriage_cases_total=194),
 source_worked_casting_examples_total INTEGER NOT NULL CHECK(source_worked_casting_examples_total=2),
 new_computed_independently_calculated_event_windows INTEGER NOT NULL CHECK(new_computed_independently_calculated_event_windows=2),
 later_feedback_events_separately_checked INTEGER NOT NULL CHECK(later_feedback_events_separately_checked=2),
 verified_unseen_marriage_forecasts INTEGER NOT NULL DEFAULT 0 CHECK(verified_unseen_marriage_forecasts=0),
 original_historical_rows_unchanged INTEGER NOT NULL CHECK(original_historical_rows_unchanged=1),
 ephemeris_model_version TEXT NOT NULL,
 computation_notes_json TEXT NOT NULL CHECK(json_valid(computation_notes_json))
);
