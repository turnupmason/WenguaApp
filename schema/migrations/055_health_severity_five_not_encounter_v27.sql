-- 055: exact, append-only health severity v27 full 194 original case source.
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS health_v27_fixed_customer_sections(
 ordinal INTEGER PRIMARY KEY CHECK(ordinal BETWEEN 1 AND 11),
 section_id TEXT NOT NULL UNIQUE,title TEXT NOT NULL,
 static_format TEXT NOT NULL, optional_context TEXT,
 no_model_rewrite INTEGER NOT NULL CHECK(no_model_rewrite=1),
 no_outcome_leakage INTEGER NOT NULL CHECK(no_outcome_leakage=1)
);
CREATE TABLE IF NOT EXISTS health_v27_conditional_rule_registry(
 rule_id TEXT PRIMARY KEY,source_book TEXT NOT NULL,
 source_chapter TEXT NOT NULL,source_lines TEXT NOT NULL,
 truth_conditions TEXT NOT NULL,meaning TEXT NOT NULL,
 counterexamples TEXT NOT NULL,proof_status TEXT NOT NULL,
 no_single_factor_clinical_prediction INTEGER NOT NULL CHECK(no_single_factor_clinical_prediction=1)
);
CREATE TABLE IF NOT EXISTS health_v27_sealed_historical_predictions(
 event_family_id TEXT PRIMARY KEY, user_selected_clock TEXT NOT NULL,
 selection_seed TEXT NOT NULL,full_readout_sha256 TEXT NOT NULL,
 provisional_traditional_verdict TEXT NOT NULL CHECK(provisional_traditional_verdict IN('病吉','病凶')),
 author_outcome_used_for_generation INTEGER NOT NULL CHECK(author_outcome_used_for_generation=0),
 later_feedback_still_sealed INTEGER NOT NULL CHECK(later_feedback_still_sealed=1),
 user_review_status TEXT NOT NULL CHECK(user_review_status='pending')
);
CREATE TABLE IF NOT EXISTS health_v27_acceptance_history(
 version TEXT PRIMARY KEY,parent_full_sha256 TEXT NOT NULL CHECK(length(parent_full_sha256)=64),
 original_event_families INTEGER NOT NULL CHECK(original_event_families=194),
 original_source_sections INTEGER NOT NULL CHECK(original_source_sections=43),
 old_wrong_development_predictions INTEGER NOT NULL CHECK(old_wrong_development_predictions=2),
 original_21_health_fact_sections INTEGER NOT NULL CHECK(original_21_health_fact_sections=21),
 source_template_sections INTEGER NOT NULL CHECK(source_template_sections=11),
 other_four_unreviewed_health_intents INTEGER NOT NULL CHECK(other_four_unreviewed_health_intents=4),
 no_runtime_gpt INTEGER NOT NULL CHECK(no_runtime_gpt=1),
 real_world_clinical_outcomes_verified INTEGER NOT NULL CHECK(real_world_clinical_outcomes_verified=0),
 all_previous_rows_unchanged INTEGER NOT NULL CHECK(all_previous_rows_unchanged=1),
 user_review_status TEXT NOT NULL CHECK(user_review_status='pending')
);
