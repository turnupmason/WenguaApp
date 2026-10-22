PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS health_v29_no_duplicate_medical_template(
 section_id TEXT PRIMARY KEY,
 format_text TEXT NOT NULL,
 no_gpt_runtime INTEGER NOT NULL CHECK(no_gpt_runtime=1),
 user_review_status TEXT NOT NULL CHECK(user_review_status='pending')
);
CREATE TABLE IF NOT EXISTS health_v29_archival_readouts(
 case_id TEXT PRIMARY KEY,
 v28_original_sha256 TEXT NOT NULL CHECK(length(v28_original_sha256)=64),
 v29_updated_sha256 TEXT NOT NULL CHECK(length(v29_updated_sha256)=64),
 old_user_approved_v27 INTEGER NOT NULL CHECK(old_user_approved_v27 IN (0,1)),
 original_results_used INTEGER NOT NULL CHECK(original_results_used=0),
 original_seals_preserved INTEGER NOT NULL CHECK(original_seals_preserved=1)
);
