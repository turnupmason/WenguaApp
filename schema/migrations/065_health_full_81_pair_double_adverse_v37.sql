-- V3.7 append-only full book archive from exact V3.6.
-- No old source events, source rows, previous failures, or sealed V3.1-V3.6 readings are overwritten.
PRAGMA foreign_keys=ON;
CREATE TABLE health_v37_ordered_81_pair_policy (
  policy_id TEXT PRIMARY KEY,
  book_source_path TEXT NOT NULL,
  full_ordered_pair_count INTEGER NOT NULL CHECK(full_ordered_pair_count=81),
  original_order_is_directional INTEGER NOT NULL CHECK(original_order_is_directional=1),
  historical_42_user_disease_supplements_retained INTEGER NOT NULL CHECK(historical_42_user_disease_supplements_retained=42),
  historical_17_composite_conditions_retained INTEGER NOT NULL CHECK(historical_17_composite_conditions_retained=17),
  original_book_rows_preserved INTEGER NOT NULL CHECK(original_book_rows_preserved=81),
  requires_role_and_gate_conditions INTEGER NOT NULL CHECK(requires_role_and_gate_conditions=1),
  incomplete_source_condition_not_asserted INTEGER NOT NULL CHECK(incomplete_source_condition_not_asserted=1),
  is_real_clinical_evidence INTEGER NOT NULL CHECK(is_real_clinical_evidence=0)
);
CREATE TABLE health_v37_user_noon_test (
  test_id TEXT PRIMARY KEY,
  local_date_time TEXT NOT NULL,
  local_timezone TEXT NOT NULL,
  birth_year_ganzhi TEXT NOT NULL,
  month_ganzhi TEXT NOT NULL,
  day_ganzhi TEXT NOT NULL,
  hour_ganzhi TEXT NOT NULL,
  term TEXT NOT NULL,
  dun TEXT NOT NULL CHECK(dun IN ('yin','yang')),
  bureau INTEGER NOT NULL CHECK(bureau BETWEEN 1 AND 9),
  selected_consultation_role TEXT NOT NULL CHECK(selected_consultation_role='self'),
  parent_full_database_sha256 TEXT NOT NULL CHECK(length(parent_full_database_sha256)=64),
  double_control INTEGER NOT NULL CHECK(double_control IN(0,1)),
  double_adverse_geometry INTEGER NOT NULL CHECK(double_adverse_geometry IN(0,1)),
  double_adverse_patient_source_formation INTEGER NOT NULL CHECK(double_adverse_patient_source_formation IN(0,1)),
  observed_traditional_verdict TEXT NOT NULL CHECK(observed_traditional_verdict IN ('病吉','病凶')),
  source_81_book_pair_footprint INTEGER NOT NULL CHECK(source_81_book_pair_footprint=9),
  reading_sha256 TEXT NOT NULL CHECK(length(reading_sha256)=64),
  original_case_feedback_as_input INTEGER NOT NULL CHECK(original_case_feedback_as_input=0),
  clinical_predictive_proof INTEGER NOT NULL CHECK(clinical_predictive_proof=0),
  user_approval_status TEXT NOT NULL CHECK(user_approval_status='pending')
);
CREATE TABLE health_v37_full_archive_audit (
  version TEXT PRIMARY KEY CHECK(version='v3.7'),
  parent_v36_sha256 TEXT NOT NULL CHECK(length(parent_v36_sha256)=64),
  original_case_families INTEGER NOT NULL CHECK(original_case_families=194),
  source_chapters INTEGER NOT NULL CHECK(source_chapters=43),
  old_wrong_development_forecasts_preserved INTEGER NOT NULL CHECK(old_wrong_development_forecasts_preserved=2),
  prior_source_health_replays_preserved INTEGER NOT NULL CHECK(prior_source_health_replays_preserved=12),
  patient_first_double_control_kept INTEGER NOT NULL CHECK(patient_first_double_control_kept=1),
  double_unfavorable_added INTEGER NOT NULL CHECK(double_unfavorable_added=1),
  extra_external_user_test INTEGER NOT NULL CHECK(extra_external_user_test=1),
  direct_medical_outcome_claim INTEGER NOT NULL CHECK(direct_medical_outcome_claim=0)
);
