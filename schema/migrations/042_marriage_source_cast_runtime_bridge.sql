-- 042: deterministic book-source nine-palace runtime bridge, NOT a published reading.
-- Existing 194 cases, 22 scenarios, 89 citations, 9 intents, 4 prose drafts
-- and all 041 all-domain six-layer controls remain unchanged.
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS marriage_runtime_source_cast_fixture (
  fixture_id TEXT PRIMARY KEY,
  casting_school TEXT NOT NULL CHECK(casting_school='shijia_zhuanpan'),
  casting_method TEXT NOT NULL,
  day_ganzhi TEXT NOT NULL,
  supplied_solar_term TEXT NOT NULL,
  derived_dun TEXT NOT NULL CHECK(derived_dun IN ('yang','yin')),
  derived_ju INTEGER NOT NULL CHECK(derived_ju BETWEEN 1 AND 9),
  hour_ganzhi TEXT NOT NULL,
  nine_palace_layout_json TEXT NOT NULL CHECK(json_valid(nine_palace_layout_json)),
  layout_sha256 TEXT NOT NULL CHECK(length(layout_sha256)=64),
  verified_original_nine_palace_cells INTEGER NOT NULL CHECK(verified_original_nine_palace_cells=9),
  physical_factors_audited INTEGER NOT NULL CHECK(physical_factors_audited=24),
  factor_results_json TEXT NOT NULL CHECK(json_valid(factor_results_json)),
  source_calendar_independently_verified INTEGER NOT NULL DEFAULT 0 CHECK(source_calendar_independently_verified=0),
  is_genuine_marriage_question INTEGER NOT NULL DEFAULT 0 CHECK(is_genuine_marriage_question=0),
  book_citation_note TEXT NOT NULL,
  human_forecast_text TEXT,
  CHECK(human_forecast_text IS NULL)
);
CREATE TABLE IF NOT EXISTS marriage_runtime_scenario_study (
  fixture_id TEXT NOT NULL REFERENCES marriage_runtime_source_cast_fixture(fixture_id),
  scene_id TEXT NOT NULL REFERENCES marriage22_scenario_protocol(scene_id),
  questioner_role_bound INTEGER NOT NULL DEFAULT 0 CHECK(questioner_role_bound=0),
  book_original_method_ref_count INTEGER NOT NULL CHECK(book_original_method_ref_count>=1),
  later_feedback_not_used_as_initial_evidence INTEGER NOT NULL DEFAULT 1 CHECK(later_feedback_not_used_as_initial_evidence=1),
  candidate_yongshen_palaces_json TEXT NOT NULL CHECK(json_valid(candidate_yongshen_palaces_json)),
  initial_book_witness_refs_json TEXT NOT NULL CHECK(json_valid(initial_book_witness_refs_json)),
  validation_book_feedback_refs_json TEXT NOT NULL CHECK(json_valid(validation_book_feedback_refs_json)),
  missing_real_forecast_inputs_json TEXT NOT NULL CHECK(json_valid(missing_real_forecast_inputs_json)),
  study_status TEXT NOT NULL CHECK(study_status='research_partial_chart_pipeline_not_final_forecast'),
  explicit_result TEXT,
  calculated_primary_timing TEXT,
  final_phrase TEXT,
  CHECK(explicit_result IS NULL AND calculated_primary_timing IS NULL AND final_phrase IS NULL),
  PRIMARY KEY(fixture_id,scene_id)
);
CREATE TABLE IF NOT EXISTS marriage_runtime_study_audit (
  audit_version TEXT PRIMARY KEY,
  full_previous_parent_SHA256 TEXT NOT NULL CHECK(length(full_previous_parent_SHA256)=64),
  source_cast_fixture_count INTEGER NOT NULL CHECK(source_cast_fixture_count=2),
  marriage_scenarios_regression_count INTEGER NOT NULL CHECK(marriage_scenarios_regression_count=44),
  complete_original_book_nine_palace_cells_compared INTEGER NOT NULL CHECK(complete_original_book_nine_palace_cells_compared=18),
  unified_mechanical_factor_slots_per_chart INTEGER NOT NULL CHECK(unified_mechanical_factor_slots_per_chart=24),
  new_verified_independent_astronomy_calendars INTEGER NOT NULL DEFAULT 0 CHECK(new_verified_independent_astronomy_calendars=0),
  published_real_marriage_predictions INTEGER NOT NULL DEFAULT 0 CHECK(published_real_marriage_predictions=0),
  remaining_method_or_calendar_blockers_json TEXT NOT NULL CHECK(json_valid(remaining_method_or_calendar_blockers_json)),
  full_previous_rows_unchanged INTEGER NOT NULL CHECK(full_previous_rows_unchanged=1)
);
