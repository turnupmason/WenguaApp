-- 056: Append V2.8 timely-medical-attention and source-checked striking/tomb templates.
-- Never rewrite the original V2.7 two permanently sealed historical outputs.
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS health_v28_fixed_customer_sections(
 ordinal INTEGER PRIMARY KEY CHECK(ordinal BETWEEN 1 AND 11),
 section_id TEXT NOT NULL UNIQUE,title TEXT NOT NULL,
 source_template_format TEXT NOT NULL,optional_context TEXT,
 pure_offline_no_gpt INTEGER NOT NULL CHECK(pure_offline_no_gpt=1)
);
CREATE TABLE IF NOT EXISTS health_v28_medical_timing_rules(
 rule_id TEXT PRIMARY KEY,condition_text TEXT NOT NULL,
 source_book_or_user TEXT NOT NULL,
 important_limit TEXT NOT NULL,clinically_validated INTEGER NOT NULL CHECK(clinically_validated=0)
);
CREATE TABLE IF NOT EXISTS health_v28_historical_review(
 case_id TEXT PRIMARY KEY,
 v27_original_sha256 TEXT NOT NULL CHECK(length(v27_original_sha256)=64),
 v28_readout_sha256 TEXT NOT NULL CHECK(length(v28_readout_sha256)=64),
 previous_book_case_outcome_used INTEGER NOT NULL CHECK(previous_book_case_outcome_used=0),
 user_review_state TEXT NOT NULL CHECK(user_review_state IN('pending','user_approved_prior_v27_only')),
 full_original_v27_unchanged INTEGER NOT NULL CHECK(full_original_v27_unchanged=1)
);
