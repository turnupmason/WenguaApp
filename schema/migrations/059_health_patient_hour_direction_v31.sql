-- 059: V3.1 correct patient-to-hour disease relationship (role-specific).
-- Strictly append to immutable V3.0 complete source, preserve all prior rows.
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS health_v31_hour_patient_fixed_templates (
 section_id TEXT PRIMARY KEY,
 exact_format TEXT NOT NULL,
 interpret_from_person_to_hour INTEGER NOT NULL CHECK(interpret_from_person_to_hour=1),
 no_post_gpt_rewrite INTEGER NOT NULL CHECK(no_post_gpt_rewrite=1)
);
CREATE TABLE IF NOT EXISTS health_v31_correction_archive (
 case_id TEXT PRIMARY KEY,
 v30_original_sha256 TEXT NOT NULL CHECK(length(v30_original_sha256)=64),
 new_v31_sha256 TEXT NOT NULL CHECK(length(new_v31_sha256)=64),
 never_overwrite_original INTEGER NOT NULL CHECK(never_overwrite_original=1),
 original_book_answer_used INTEGER NOT NULL CHECK(original_book_answer_used=0),
 content_user_approved INTEGER NOT NULL CHECK(content_user_approved=0)
);
CREATE TABLE IF NOT EXISTS health_v31_version_receipt (
 version TEXT PRIMARY KEY,
 exact_parent_v30_sha256 TEXT NOT NULL CHECK(length(exact_parent_v30_sha256)=64),
 book_cases INTEGER NOT NULL CHECK(book_cases=194),
 source_sections INTEGER NOT NULL CHECK(source_sections=43),
 original_two_failed_dev_cases INTEGER NOT NULL CHECK(original_two_failed_dev_cases=2),
 imported_ordered_pairs INTEGER NOT NULL CHECK(imported_ordered_pairs=42),
 indexed_composite_patterns INTEGER NOT NULL CHECK(indexed_composite_patterns=17),
 remaining_other_health_subtypes_unapproved INTEGER NOT NULL CHECK(remaining_other_health_subtypes_unapproved=4),
 original_rows_unchanged INTEGER NOT NULL CHECK(original_rows_unchanged=1),
 user_review_status TEXT NOT NULL CHECK(user_review_status='pending')
);
