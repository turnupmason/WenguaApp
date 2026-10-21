-- 044: all source original rows unchanged; deterministic marriage-first verdict studies.
-- Book CASE labels/feedback are stored ONLY in separate POST-inference validation.
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS marriage_v16_judgment_contract (
 version TEXT PRIMARY KEY,
 all_domain_six_layer_mandatory INTEGER NOT NULL CHECK(all_domain_six_layer_mandatory=1),
 original_method_source_sha256 TEXT NOT NULL CHECK(length(original_method_source_sha256)=64),
 original_source_rule_ids_json TEXT NOT NULL CHECK(json_valid(original_source_rule_ids_json)),
 main_actor_birth_year_before_liuhe INTEGER NOT NULL CHECK(main_actor_birth_year_before_liuhe=1),
 bidirectional_support_counter_trace INTEGER NOT NULL CHECK(bidirectional_support_counter_trace=1),
 source_timing_only_after_initial_outcome INTEGER NOT NULL CHECK(source_timing_only_after_initial_outcome=1),
 family_holdout_excludes_all_case_variants INTEGER NOT NULL CHECK(family_holdout_excludes_all_case_variants=1),
 book_feedback_never_initial_input INTEGER NOT NULL CHECK(book_feedback_never_initial_input=1),
 no_fake_prediction_accuracy_claim INTEGER NOT NULL CHECK(no_fake_prediction_accuracy_claim=1),
 unsupported_factors_maintain_unknown INTEGER NOT NULL CHECK(unsupported_factors_maintain_unknown=1),
 parent_full_archive_sha256 TEXT NOT NULL CHECK(length(parent_full_archive_sha256)=64),
 contract_json TEXT NOT NULL CHECK(json_valid(contract_json))
);
CREATE TABLE IF NOT EXISTS marriage_v16_historical_holdout_inputs (
 study_id TEXT PRIMARY KEY,
 heldout_family_id TEXT NOT NULL,
 source_case_id TEXT NOT NULL REFERENCES cases(case_id),
 scene_id TEXT NOT NULL REFERENCES marriage22_scenario_protocol(scene_id),
 source_civil_iso TEXT NOT NULL,
 original_case_chart_deity_door_align INTEGER NOT NULL CHECK(original_case_chart_deity_door_align=1),
 outer_palaces_checked INTEGER NOT NULL CHECK(outer_palaces_checked=8),
 subject_year_ganzhi TEXT NOT NULL,
 partner_year_ganzhi TEXT NOT NULL,
 question_text TEXT NOT NULL,
 question_packet_hash TEXT NOT NULL CHECK(length(question_packet_hash)=64),
 frozen_data_splits TEXT NOT NULL CHECK(frozen_data_splits='entire_event_family_and_all_book_source_witnesses'),
 case_specific_author_verdict_used INTEGER NOT NULL DEFAULT 0 CHECK(case_specific_author_verdict_used=0)
);
CREATE TABLE IF NOT EXISTS marriage_v16_historical_initial_verdicts (
 study_id TEXT PRIMARY KEY REFERENCES marriage_v16_historical_holdout_inputs(study_id),
 initial_traditional_outcome TEXT NOT NULL CHECK(initial_traditional_outcome IN ('success','failure','mixed','unresolved')),
 original_author_label_visible_before_initial INTEGER NOT NULL DEFAULT 0 CHECK(original_author_label_visible_before_initial=0),
 book_feedback_visible_before_initial INTEGER NOT NULL DEFAULT 0 CHECK(book_feedback_visible_before_initial=0),
 source_author_rule_trace_json TEXT NOT NULL CHECK(json_valid(source_author_rule_trace_json)),
 source_support_json TEXT NOT NULL CHECK(json_valid(source_support_json)),
 source_counter_json TEXT NOT NULL CHECK(json_valid(source_counter_json)),
 book_method_witness_family_ids_json TEXT NOT NULL CHECK(json_valid(book_method_witness_family_ids_json)),
 conditional_timing_json TEXT CHECK(conditional_timing_json IS NULL OR json_valid(conditional_timing_json)),
 original_chart_factor_count INTEGER NOT NULL CHECK(original_chart_factor_count>=5),
 intended_real_world_publication INTEGER NOT NULL DEFAULT 0 CHECK(intended_real_world_publication=0)
);
CREATE TABLE IF NOT EXISTS marriage_v16_post_inference_labels (
 study_id TEXT PRIMARY KEY REFERENCES marriage_v16_historical_holdout_inputs(study_id),
 reported_book_event_result TEXT NOT NULL CHECK(reported_book_event_result IN ('success','failure')),
 original_author_first_verdict_lines_json TEXT NOT NULL CHECK(json_valid(original_author_first_verdict_lines_json)),
 later_feedback_source_lines_json TEXT NOT NULL CHECK(json_valid(later_feedback_source_lines_json)),
 matches_initial_book_retrospective_result INTEGER NOT NULL CHECK(matches_initial_book_retrospective_result IN (0,1)),
 reported_book_result_not_independently_verified INTEGER NOT NULL CHECK(reported_book_result_not_independently_verified=1),
 available_to_initial_judger INTEGER NOT NULL DEFAULT 0 CHECK(available_to_initial_judger=0)
);
CREATE TABLE IF NOT EXISTS marriage_v16_family_dev_audit (
 version TEXT PRIMARY KEY,
 historical_book_cases_preserved INTEGER NOT NULL CHECK(historical_book_cases_preserved=194),
 inherited_twenty_two_scenes INTEGER NOT NULL CHECK(inherited_twenty_two_scenes=22),
 inherited_twenty_author_timing_methods INTEGER NOT NULL CHECK(inherited_twenty_author_timing_methods=20),
 parent_archive_sha256 TEXT NOT NULL CHECK(length(parent_archive_sha256)=64),
 source_printed_charts_aligned INTEGER NOT NULL CHECK(source_printed_charts_aligned=3),
 scored_event_questions INTEGER NOT NULL CHECK(scored_event_questions=3),
 matched_book_retrospective_events INTEGER NOT NULL CHECK(matched_book_retrospective_events=1),
 distinct_heldout_event_families INTEGER NOT NULL CHECK(distinct_heldout_event_families=2),
 untouched_secret_test_used INTEGER NOT NULL DEFAULT 0 CHECK(untouched_secret_test_used=0),
 independent_new_real_world_predictions INTEGER NOT NULL DEFAULT 0 CHECK(independent_new_real_world_predictions=0),
 old_historical_rows_unchanged INTEGER NOT NULL CHECK(old_historical_rows_unchanged=1),
 development_errors_json TEXT NOT NULL CHECK(json_valid(development_errors_json))
);
