-- V3.2 historical evaluation archive only. Engine still V3.1, source rows untouched.
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS health_v32_pre_disclosure_history (
    source_family_id TEXT PRIMARY KEY,
    exact_v31_parent_sha256 TEXT NOT NULL CHECK(length(exact_v31_parent_sha256)=64),
    pre_disclosure_pillars TEXT NOT NULL CHECK(json_valid(pre_disclosure_pillars)),
    book_casting_bureau TEXT NOT NULL CHECK(json_valid(book_casting_bureau)),
    original_book_outcome_was_read INTEGER NOT NULL CHECK(original_book_outcome_was_read=0),
    original_book_feedback_was_read INTEGER NOT NULL CHECK(original_book_feedback_was_read=0),
    reading_sha256 TEXT NOT NULL CHECK(length(reading_sha256)=64),
    provisional_traditional_verdict TEXT NOT NULL CHECK(provisional_traditional_verdict IN('病吉','病凶')),
    older_known_family_not_new_blind INTEGER NOT NULL CHECK(older_known_family_not_new_blind=1),
    user_acceptance TEXT NOT NULL CHECK(user_acceptance='pending')
);
CREATE TABLE IF NOT EXISTS health_v32_handoff_gate (
    version TEXT PRIMARY KEY,
    parent_full_sha256 TEXT NOT NULL CHECK(length(parent_full_sha256)=64),
    original_case_families INTEGER NOT NULL CHECK(original_case_families=194),
    original_chapters INTEGER NOT NULL CHECK(original_chapters=43),
    old_wrong_development_predictions INTEGER NOT NULL CHECK(old_wrong_development_predictions=2),
    indexed_original_stem_pairs INTEGER NOT NULL CHECK(indexed_original_stem_pairs=42),
    indexed_composite_rules INTEGER NOT NULL CHECK(indexed_composite_rules=17),
    old_four_health_intents_unapproved INTEGER NOT NULL CHECK(old_four_health_intents_unapproved=4),
    app_ui_cannot_be_accepted_ahead_of_user INTEGER NOT NULL CHECK(app_ui_cannot_be_accepted_ahead_of_user=1),
    previous_all_rows_preserved INTEGER NOT NULL CHECK(previous_all_rows_preserved=1),
    clinical_prediction_validated INTEGER NOT NULL CHECK(clinical_prediction_validated=0),
    user_review_status TEXT NOT NULL CHECK(user_review_status='pending')
);
