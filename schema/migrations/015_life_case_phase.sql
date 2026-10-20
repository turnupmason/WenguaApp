-- Traditional birth-time versus inquiry-time case interpretation; strictly additive.
-- No added field may imply that the author's fatality/accident/medical claims have been empirically validated.
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS historical_life_case_context (
  case_id TEXT NOT NULL PRIMARY KEY REFERENCES cases(case_id),
  source_chart_line INTEGER NOT NULL CHECK(source_chart_line>0),
  cast_strategy TEXT NOT NULL CHECK(cast_strategy IN ('birth_time_post_outcome','birth_time_inquiry','inquiry_time')),
  initial_context_json TEXT NOT NULL CHECK(json_valid(initial_context_json)),
  retrospective_case INTEGER NOT NULL DEFAULT 0 CHECK(retrospective_case IN (0,1)),
  original_book_explicit_year_error INTEGER NOT NULL DEFAULT 0 CHECK(original_book_explicit_year_error IN (0,1)),
  original_book_initial_years_json TEXT NOT NULL CHECK(json_valid(original_book_initial_years_json)),
  source_revealed_year INTEGER,
  source_method_missing_for_claims INTEGER NOT NULL DEFAULT 0 CHECK(source_method_missing_for_claims IN (0,1)),
  scientific_independent_verification INTEGER NOT NULL DEFAULT 0 CHECK(scientific_independent_verification IN (0,1)),
  metadata_json TEXT NOT NULL CHECK(json_valid(metadata_json))
);
CREATE TABLE IF NOT EXISTS historical_life_source_error_segments (
  case_id TEXT NOT NULL REFERENCES cases(case_id),
  source_line INTEGER NOT NULL CHECK(source_line>0),
  error_kind TEXT NOT NULL,
  original_statement TEXT NOT NULL,
  subsequent_evidence TEXT NOT NULL,
  eligible_positive_training INTEGER NOT NULL DEFAULT 0 CHECK(eligible_positive_training IN (0,1)),
  PRIMARY KEY(case_id,source_line)
);
