-- V3.6 source revision of value-door formations and original hour-branch horse.
-- Append only to exact latest V3.5 full source backup; preserve V3.1-V3.5.
PRAGMA foreign_keys=ON;
CREATE TABLE health_v36_source_horse_and_value_door (
  source_family_id TEXT PRIMARY KEY,
  source_hour_pillar TEXT NOT NULL,
  horse_from_hour_branch TEXT NOT NULL,
  original_book_outcome_as_prediction_input INTEGER NOT NULL CHECK(original_book_outcome_as_prediction_input=0),
  original_user_sources_preserved INTEGER NOT NULL CHECK(original_user_sources_preserved=1),
  source_verified_three_wonders INTEGER NOT NULL CHECK(source_verified_three_wonders IN(0,1)),
  source_verified_jade_woman_gate INTEGER NOT NULL CHECK(source_verified_jade_woman_gate IN(0,1)),
  old_day_based_horse_rule_retired INTEGER NOT NULL CHECK(old_day_based_horse_rule_retired=1),
  full_original_case_reading_sha256 TEXT NOT NULL CHECK(length(full_original_case_reading_sha256)=64),
  template_user_approval TEXT NOT NULL CHECK(template_user_approval='pending')
);
CREATE TABLE health_v36_full_archive_audit (
  version TEXT PRIMARY KEY CHECK(version='v3.6'),
  exact_parent_sha256 TEXT NOT NULL CHECK(length(exact_parent_sha256)=64),
  full_book_families INTEGER NOT NULL CHECK(full_book_families=194),
  original_sections INTEGER NOT NULL CHECK(original_sections=43),
  old_failed_developer_forecasts INTEGER NOT NULL CHECK(old_failed_developer_forecasts=2),
  last_v35_replays_kept INTEGER NOT NULL CHECK(last_v35_replays_kept=12),
  v36_42_pair_coverage INTEGER NOT NULL CHECK(v36_42_pair_coverage=42),
  v36_17_composite_audits INTEGER NOT NULL CHECK(v36_17_composite_audits=17),
  incomplete_source_predicates_not_claimed_resolved INTEGER NOT NULL CHECK(incomplete_source_predicates_not_claimed_resolved=1),
  user_approval_status TEXT NOT NULL CHECK(user_approval_status='pending')
);
