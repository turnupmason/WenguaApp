-- 053: OFFLINE health severity: 11 concise sources, user-gated family section.
-- Append-only from exact immutable V2.4 full archive.
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS health_v25_concise_sections (
    section_order INTEGER PRIMARY KEY CHECK(section_order BETWEEN 1 AND 11),
    section_id TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    template_text TEXT NOT NULL,
    optional_context TEXT,
    deterministic_python_only INTEGER NOT NULL CHECK(deterministic_python_only=1)
);
CREATE TABLE IF NOT EXISTS health_v25_evidence_acceptance (
    version TEXT PRIMARY KEY,
    exact_parent_sha256 TEXT NOT NULL CHECK(length(exact_parent_sha256)=64),
    original_book_case_families INTEGER NOT NULL CHECK(original_book_case_families=194),
    original_book_sections INTEGER NOT NULL CHECK(original_book_sections=43),
    original_v16_wrong_development_predictions INTEGER NOT NULL CHECK(original_v16_wrong_development_predictions=2),
    original_21_health_source_facts INTEGER NOT NULL CHECK(original_21_health_source_facts=21),
    source_section_count INTEGER NOT NULL CHECK(source_section_count=11),
    actual_user_preview_sections INTEGER NOT NULL CHECK(actual_user_preview_sections=10),
    four_other_unapproved_intents INTEGER NOT NULL CHECK(four_other_unapproved_intents=4),
    fuyin_fanyin_strict_separate_computation INTEGER NOT NULL CHECK(fuyin_fanyin_strict_separate_computation=1),
    verdict_traditional_only INTEGER NOT NULL CHECK(verdict_traditional_only=1),
    no_llm_runtime INTEGER NOT NULL CHECK(no_llm_runtime=1),
    medical_outcome_validated INTEGER NOT NULL CHECK(medical_outcome_validated=0),
    previous_all_rows_unchanged INTEGER NOT NULL CHECK(previous_all_rows_unchanged=1),
    user_review_status TEXT NOT NULL CHECK(user_review_status='pending')
);
