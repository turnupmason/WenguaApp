-- V2.6 append-only 11 concise user-approved-shaped template; previous full V2.5 archive is immutable.
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS health_v26_strict_customer_template (
  section_order INTEGER PRIMARY KEY CHECK(section_order BETWEEN 1 AND 11),
  section_id TEXT NOT NULL UNIQUE,
  title TEXT NOT NULL,
  format_text TEXT NOT NULL,
  optional_context TEXT,
  no_llm_or_rewrite INTEGER NOT NULL CHECK(no_llm_or_rewrite=1),
  no_duplicate_palaces INTEGER NOT NULL CHECK(no_duplicate_palaces=1)
);
CREATE TABLE IF NOT EXISTS health_v26_acceptance_receipt (
  receipt_id TEXT PRIMARY KEY,
  v25_exact_parent_sha256 TEXT NOT NULL CHECK(length(v25_exact_parent_sha256)=64),
  cases_unchanged INTEGER NOT NULL CHECK(cases_unchanged=194),
  source_sections_unchanged INTEGER NOT NULL CHECK(source_sections_unchanged=43),
  prior_wrong_predictions_unchanged INTEGER NOT NULL CHECK(prior_wrong_predictions_unchanged=2),
  old_health_21_facets_unchanged INTEGER NOT NULL CHECK(old_health_21_facets_unchanged=21),
  customer_section_count INTEGER NOT NULL CHECK(customer_section_count=11),
  user_self_section_count INTEGER NOT NULL CHECK(user_self_section_count=10),
  previous_health_subtypes_unapproved INTEGER NOT NULL CHECK(previous_health_subtypes_unapproved=4),
  medically_validated INTEGER NOT NULL CHECK(medically_validated=0),
  external_model_calls INTEGER NOT NULL CHECK(external_model_calls=0),
  previous_rows_kept INTEGER NOT NULL CHECK(previous_rows_kept=1),
  user_review_status TEXT NOT NULL CHECK(user_review_status='pending')
);
