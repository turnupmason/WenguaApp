-- 045 V1.7: original two-book multi-evidence method training, no fabricated outcomes.
-- This is an append-only migration from EXACT complete V1.6 194-case source DB.
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS marriage_v17_book_conditional_rules (
 rule_id TEXT PRIMARY KEY,
 book_id TEXT NOT NULL CHECK(book_id='kaiwu'),
 chapter_key TEXT NOT NULL,
 source_line INTEGER NOT NULL CHECK(source_line>0),
 source_sha256 TEXT NOT NULL CHECK(length(source_sha256)=64),
 exact_excerpt_sha256 TEXT NOT NULL CHECK(length(exact_excerpt_sha256)=64),
 original_book_line TEXT NOT NULL,
 conditional_rule_json TEXT NOT NULL CHECK(json_valid(conditional_rule_json)),
 positive_condition_description TEXT NOT NULL,
 counterexample_or_conflict TEXT NOT NULL,
 when_and_how_timing_applies TEXT NOT NULL,
 independent_reality_proof INTEGER NOT NULL DEFAULT 0 CHECK(independent_reality_proof=0),
 automatically_final_rule INTEGER NOT NULL DEFAULT 0 CHECK(automatically_final_rule=0)
);
CREATE TABLE IF NOT EXISTS marriage_v17_new_event_family_replays (
 study_id TEXT PRIMARY KEY,
 heldout_event_family_id TEXT NOT NULL REFERENCES cases(case_id),
 source_original_chart_aligned INTEGER NOT NULL CHECK(source_original_chart_aligned=1),
 compared_printed_outer_palaces INTEGER NOT NULL CHECK(compared_printed_outer_palaces=8),
 original_question TEXT NOT NULL,
 subject_year_supplied INTEGER NOT NULL CHECK(subject_year_supplied IN (0,1)),
 partner_year_supplied INTEGER NOT NULL CHECK(partner_year_supplied=0),
 initial_traditional_verdict TEXT NOT NULL CHECK(initial_traditional_verdict='unresolved'),
 computed_source_rule_count INTEGER NOT NULL CHECK(computed_source_rule_count=27),
 exact_directional_tengan_pair_count INTEGER NOT NULL CHECK(exact_directional_tengan_pair_count=81),
 first_inference_trace_json TEXT NOT NULL CHECK(json_valid(first_inference_trace_json)),
 source_author_comments_after_inference_json TEXT NOT NULL CHECK(json_valid(source_author_comments_after_inference_json)),
 feedback_loaded_during_initial_inference INTEGER NOT NULL DEFAULT 0 CHECK(feedback_loaded_during_initial_inference=0),
 retrospective_future_outcome_score INTEGER CHECK(retrospective_future_outcome_score IS NULL),
 genuinely_new_live_prediction INTEGER NOT NULL DEFAULT 0 CHECK(genuinely_new_live_prediction=0)
);
CREATE TABLE IF NOT EXISTS marriage_v17_rule_change_and_error_audit (
 audit_version TEXT PRIMARY KEY,
 previous_complete_sqlite_sha256 TEXT NOT NULL CHECK(length(previous_complete_sqlite_sha256)=64),
 original_historical_cases_preserved INTEGER NOT NULL CHECK(original_historical_cases_preserved=194),
 previous_source_dev_total INTEGER NOT NULL CHECK(previous_source_dev_total=3),
 previous_dev_correct INTEGER NOT NULL CHECK(previous_dev_correct=1),
 previous_dev_wrong_kept INTEGER NOT NULL CHECK(previous_dev_wrong_kept=2),
 new_original_rule_entries INTEGER NOT NULL CHECK(new_original_rule_entries=27),
 new_other_family_replays INTEGER NOT NULL CHECK(new_other_family_replays=2),
 new_other_family_scoreable_future_results INTEGER NOT NULL CHECK(new_other_family_scoreable_future_results=0),
 complete_24_rules_automatically_verified INTEGER NOT NULL DEFAULT 0 CHECK(complete_24_rules_automatically_verified=0),
 natural_200_character_final_phrases_published INTEGER NOT NULL DEFAULT 0 CHECK(natural_200_character_final_phrases_published=0),
 genuine_real_world_success_predictions_verified INTEGER NOT NULL DEFAULT 0 CHECK(genuine_real_world_success_predictions_verified=0),
 all_parent_database_rows_unchanged INTEGER NOT NULL CHECK(all_parent_database_rows_unchanged=1),
 note_json TEXT NOT NULL CHECK(json_valid(note_json))
);
