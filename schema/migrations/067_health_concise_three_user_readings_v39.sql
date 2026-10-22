-- Append-only original book and customer-facing V3.9 real readings.
PRAGMA foreign_keys=ON;
CREATE TABLE health_v39_concise_user_readings (
  case_id TEXT PRIMARY KEY,
  kind TEXT NOT NULL CHECK(kind IN ('user_noon','pre_disclosure_book')),
  original_chart_day TEXT NOT NULL,
  original_chart_hour TEXT NOT NULL,
  illness_star_tomb INTEGER NOT NULL CHECK(illness_star_tomb IN(0,1)),
  illness_star_extinct INTEGER NOT NULL CHECK(illness_star_extinct IN(0,1)),
  illness_palace_xun_void INTEGER NOT NULL CHECK(illness_palace_xun_void IN(0,1)),
  personal_role_verified INTEGER NOT NULL CHECK(personal_role_verified=1),
  source_line_metadata_customer_visible INTEGER NOT NULL CHECK(source_line_metadata_customer_visible=0),
  old_forecast_as_input INTEGER NOT NULL CHECK(old_forecast_as_input=0),
  reading_sha256 TEXT NOT NULL CHECK(length(reading_sha256)=64),
  user_acceptance TEXT NOT NULL CHECK(user_acceptance='pending')
);
CREATE TABLE health_v39_appendonly_full_audit (
  version TEXT PRIMARY KEY CHECK(version='v3.9'),
  full_parent_v38_sha256 TEXT NOT NULL CHECK(length(full_parent_v38_sha256)=64),
  source_original_event_families INTEGER NOT NULL CHECK(source_original_event_families=194),
  original_source_chapters INTEGER NOT NULL CHECK(original_source_chapters=43),
  book_source_ordered_stems INTEGER NOT NULL CHECK(book_source_ordered_stems=81),
  illness_pairs INTEGER NOT NULL CHECK(illness_pairs=42),
  composite_conditions INTEGER NOT NULL CHECK(composite_conditions=17),
  seeded_historical_cases INTEGER NOT NULL CHECK(seeded_historical_cases=2),
  old_errors_retained INTEGER NOT NULL CHECK(old_errors_retained=2),
  older_v38_three_results_retained INTEGER NOT NULL CHECK(older_v38_three_results_retained=3),
  pending_user_review INTEGER NOT NULL CHECK(pending_user_review=1),
  design_ui_before_approval INTEGER NOT NULL CHECK(design_ui_before_approval=0)
);
