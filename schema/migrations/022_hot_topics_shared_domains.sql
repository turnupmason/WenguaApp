-- Shared domain/classification layer for all original Shenqi/Kaiwu historical
-- cases. Books are source witnesses, not separate domain namespaces.
-- User accepts book historical events/outcomes without case-by-case human review.
-- This internal acceptance is NOT independent empirical verification.
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS historic_book_case_acceptance (
  case_id TEXT PRIMARY KEY REFERENCES cases(case_id),
  source_book TEXT NOT NULL REFERENCES books(book_id),
  source_chapter_key TEXT NOT NULL REFERENCES chapter_knowledge(chapter_key),
  user_accepts_book_case INTEGER NOT NULL DEFAULT 1 CHECK(user_accepts_book_case=1),
  requires_manual_user_approval INTEGER NOT NULL DEFAULT 0 CHECK(requires_manual_user_approval=0),
  source_documented_outcome TEXT NOT NULL,
  external_verification TEXT NOT NULL DEFAULT 'not_required_by_user_not_claimed',
  source_has_explicit_initial_error INTEGER NOT NULL DEFAULT 0 CHECK(source_has_explicit_initial_error IN (0,1)),
  metadata_json TEXT NOT NULL CHECK(json_valid(metadata_json))
);
CREATE VIEW IF NOT EXISTS accepted_book_cases_across_books AS
 SELECT c.case_id,c.event_family_id,c.domain_id,s.book_id,s.section_key,
        1 AS user_accepts_book_case,0 AS requires_manual_user_approval,
        c.known_before,c.author_judgment,c.later_feedback
 FROM cases c JOIN sections s ON s.section_id=c.section_id;
CREATE TABLE IF NOT EXISTS hot_topic_event_source_witnesses (
  chapter_key TEXT NOT NULL REFERENCES chapter_knowledge(chapter_key),
  case_id TEXT NOT NULL REFERENCES cases(case_id),
  source_group_key TEXT NOT NULL,
  cast_key TEXT NOT NULL,
  source_chart_start INTEGER NOT NULL CHECK(source_chart_start>0),
  source_chart_end INTEGER NOT NULL CHECK(source_chart_end>=source_chart_start),
  source_chart_sha256 TEXT NOT NULL CHECK(length(source_chart_sha256)=64),
  original_book_phase TEXT NOT NULL,
  original_cast_metadata TEXT NOT NULL,
  event_domain TEXT NOT NULL,
  event_facets_json TEXT NOT NULL CHECK(json_valid(event_facets_json)),
  outcome_known_before_this_cast INTEGER NOT NULL DEFAULT 0 CHECK(outcome_known_before_this_cast IN (0,1)),
  note TEXT NOT NULL,
  PRIMARY KEY(chapter_key,case_id,cast_key),
  UNIQUE(chapter_key,source_chart_start)
);
CREATE TABLE IF NOT EXISTS hot_topic_witness_palaces (
  chapter_key TEXT NOT NULL,
  case_id TEXT NOT NULL,
  cast_key TEXT NOT NULL,
  palace INTEGER NOT NULL CHECK(palace BETWEEN 1 AND 9),
  source_start_line INTEGER NOT NULL CHECK(source_start_line>0),
  source_end_line INTEGER NOT NULL,
  palace_label TEXT NOT NULL,
  deity_raw TEXT NOT NULL,
  door_raw TEXT NOT NULL,
  star_raw TEXT NOT NULL,
  literal_original TEXT NOT NULL,
  literal_sha256 TEXT NOT NULL CHECK(length(literal_sha256)=64),
  not_inferred INTEGER NOT NULL DEFAULT 1 CHECK(not_inferred=1),
  PRIMARY KEY(chapter_key,case_id,cast_key,palace),
  FOREIGN KEY(chapter_key,case_id,cast_key)
   REFERENCES hot_topic_event_source_witnesses(chapter_key,case_id,cast_key)
);
CREATE TABLE IF NOT EXISTS hot_topic_source_phases (
 chapter_key TEXT NOT NULL REFERENCES chapter_knowledge(chapter_key),
 case_id TEXT NOT NULL REFERENCES cases(case_id),
 phase_key TEXT NOT NULL,
 phase TEXT NOT NULL,
 start_line INTEGER NOT NULL CHECK(start_line>0),
 end_line INTEGER NOT NULL CHECK(end_line>=start_line),
 original_text TEXT NOT NULL,
 original_sha256 TEXT NOT NULL CHECK(length(original_sha256)=64),
 phase_metadata_json TEXT NOT NULL CHECK(json_valid(phase_metadata_json)),
 PRIMARY KEY(chapter_key,case_id,phase_key)
);
CREATE TABLE IF NOT EXISTS hot_topic_multifacet_domains(
 chapter_key TEXT NOT NULL REFERENCES chapter_knowledge(chapter_key),
 case_id TEXT NOT NULL REFERENCES cases(case_id),
 domain_id TEXT NOT NULL,
 domain_role TEXT NOT NULL CHECK(domain_role IN ('primary','related')),
 topic TEXT NOT NULL,
 PRIMARY KEY(chapter_key,case_id,domain_id)
);
CREATE TABLE IF NOT EXISTS hot_topic_annual_forecast_parts(
 chapter_key TEXT NOT NULL REFERENCES chapter_knowledge(chapter_key),
 case_id TEXT NOT NULL REFERENCES cases(case_id),
 source_line INTEGER NOT NULL CHECK(source_line>0),
 forecast_domain TEXT NOT NULL,
 literal_original TEXT NOT NULL,
 source_sha256 TEXT NOT NULL CHECK(length(source_sha256)=64),
 printed_chart_absent INTEGER NOT NULL DEFAULT 1 CHECK(printed_chart_absent=1),
 historical_outcome_not_provided INTEGER NOT NULL DEFAULT 1 CHECK(historical_outcome_not_provided=1),
 PRIMARY KEY(chapter_key,case_id,source_line)
);
CREATE TABLE IF NOT EXISTS hot_topic_correction_audits(
 chapter_key TEXT NOT NULL REFERENCES chapter_knowledge(chapter_key),
 case_id TEXT NOT NULL REFERENCES cases(case_id),
 initial_line INTEGER NOT NULL,
 book_error_admission_line INTEGER NOT NULL,
 book_correction_line INTEGER NOT NULL,
 initial_source_prediction TEXT NOT NULL,
 correction_source_original TEXT NOT NULL,
 original_prediction_must_not_be_overwritten INTEGER NOT NULL DEFAULT 1 CHECK(original_prediction_must_not_be_overwritten=1),
 PRIMARY KEY(chapter_key,case_id)
);
CREATE INDEX IF NOT EXISTS idx_hot_topic_domain ON hot_topic_multifacet_domains(domain_id,domain_role);
CREATE INDEX IF NOT EXISTS idx_hot_topic_source_phase ON hot_topic_source_phases(case_id,phase);
