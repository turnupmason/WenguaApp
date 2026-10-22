-- New append-only V3.8 audience-safe health reading and historical case acceptance audit.
-- Parent V3.7 entire full 194 book cases DB is immutable.
PRAGMA foreign_keys=ON;
CREATE TABLE health_v38_case_readouts (
  case_id TEXT PRIMARY KEY,
  case_kind TEXT NOT NULL CHECK(case_kind IN ('new_user_question','ancient_source_first_question')),
  day_pillar TEXT NOT NULL,
  hour_pillar TEXT NOT NULL,
  patient_palace INTEGER NOT NULL CHECK(patient_palace BETWEEN 1 AND 9),
  illness_palace INTEGER NOT NULL CHECK(illness_palace BETWEEN 1 AND 9),
  illness_carried_tomb INTEGER NOT NULL CHECK(illness_carried_tomb IN(0,1)),
  illness_carried_extinct INTEGER NOT NULL CHECK(illness_carried_extinct IN(0,1)),
  illness_palace_hour_void INTEGER NOT NULL CHECK(illness_palace_hour_void IN(0,1)),
  source_lines_internal_only INTEGER NOT NULL CHECK(source_lines_internal_only=1),
  author_post_outcome_unused INTEGER NOT NULL CHECK(author_post_outcome_unused=1),
  readout_sha256 TEXT NOT NULL CHECK(length(readout_sha256)=64),
  user_review_status TEXT NOT NULL CHECK(user_review_status='pending')
);
CREATE TABLE health_v38_latest_full_archive (
 version TEXT PRIMARY KEY CHECK(version='v3.8'),
 exact_parent_v37_sha256 TEXT NOT NULL CHECK(length(exact_parent_v37_sha256)=64),
 source_book_event_count INTEGER NOT NULL CHECK(source_book_event_count=194),
 source_book_chapters INTEGER NOT NULL CHECK(source_book_chapters=43),
 historical_pair_catalog INTEGER NOT NULL CHECK(historical_pair_catalog=81),
 disease_supplement_pair_catalog INTEGER NOT NULL CHECK(disease_supplement_pair_catalog=42),
 compound_conditional_catalog INTEGER NOT NULL CHECK(compound_conditional_catalog=17),
 two_original_cases_randomly_drawn INTEGER NOT NULL CHECK(two_original_cases_randomly_drawn=2),
 prior_bad_developer_predictions_preserved INTEGER NOT NULL CHECK(prior_bad_developer_predictions_preserved=2),
 prior_v37_noon_and_12_historical_cases_preserved INTEGER NOT NULL CHECK(prior_v37_noon_and_12_historical_cases_preserved=1),
 user_approved_for_ui INTEGER NOT NULL CHECK(user_approved_for_ui=0)
);
