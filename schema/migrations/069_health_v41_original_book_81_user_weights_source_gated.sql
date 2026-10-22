-- 2026-10-22 immutable appendix from full exact V4.0 194-case SQL.
-- This table represents all 81 USER PROPOSED candidate weights, not original author numerical scores.
PRAGMA foreign_keys=ON;
CREATE TABLE health_v41_candidate_ordered_pair_weights (
  pair_key TEXT PRIMARY KEY,
  heaven TEXT NOT NULL,
  earth TEXT NOT NULL,
  user_alias TEXT NOT NULL,
  proposed_points INTEGER,
  duration_weights_json TEXT,
  book_original_sha256 TEXT NOT NULL CHECK(length(book_original_sha256)=64),
  book_original_source_line INTEGER NOT NULL,
  approval_status TEXT NOT NULL CHECK(approval_status='candidate_not_approved'),
  health_certified INTEGER NOT NULL CHECK(health_certified=0)
);
CREATE TABLE health_v41_real_chart_81_pair_checks (
  case_id TEXT NOT NULL,
  star TEXT NOT NULL,
  palace INTEGER NOT NULL CHECK(palace BETWEEN 1 AND 9),
  ordered_pair TEXT NOT NULL,
  actual_role TEXT,
  original_health_severity TEXT NOT NULL,
  match_status TEXT NOT NULL,
  applied_delta INTEGER NOT NULL,
  source_sha256 TEXT NOT NULL CHECK(length(source_sha256)=64),
  PRIMARY KEY (case_id,star,palace,ordered_pair),
  FOREIGN KEY(ordered_pair) REFERENCES health_v41_candidate_ordered_pair_weights(pair_key)
);
CREATE TABLE health_v41_scoring_3_fixed_cases (
  case_id TEXT PRIMARY KEY,
  previous_v40_raw_score INTEGER NOT NULL,
  new_v41_raw_score INTEGER NOT NULL,
  new_v41_shown_score INTEGER NOT NULL CHECK(new_v41_shown_score BETWEEN 0 AND 100),
  score_evidence_json_sha256 TEXT NOT NULL CHECK(length(score_evidence_json_sha256)=64),
  no_post_event_results_used INTEGER NOT NULL CHECK(no_post_event_results_used=1),
  clinical_utility_claim INTEGER NOT NULL CHECK(clinical_utility_claim=0),
  approved INTEGER NOT NULL CHECK(approved=0)
);
CREATE TABLE health_v41_source_gate_archive_policy (
  version TEXT PRIMARY KEY CHECK(version='v4.1'),
  full_v40_parent_sha256 TEXT NOT NULL CHECK(length(full_v40_parent_sha256)=64),
  original_cases INTEGER NOT NULL CHECK(original_cases=194),
  original_chapters INTEGER NOT NULL CHECK(original_chapters=43),
  all_source_ordered_pairs INTEGER NOT NULL CHECK(all_source_ordered_pairs=81),
  old_user_disease_supplements INTEGER NOT NULL CHECK(old_user_disease_supplements=42),
  old_composites INTEGER NOT NULL CHECK(old_composites=17),
  preserved_known_failed_predictions INTEGER NOT NULL CHECK(preserved_known_failed_predictions=2),
  all_proposed_81_weight_rows INTEGER NOT NULL CHECK(all_proposed_81_weight_rows=81),
  context_checked_3_times_9 INTEGER NOT NULL CHECK(context_checked_3_times_9=27),
  no_generic_disease_role_inversion INTEGER NOT NULL CHECK(no_generic_disease_role_inversion=1)
);
