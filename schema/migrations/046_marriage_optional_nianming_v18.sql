-- 046: optional year (年命) source-authored marriage questions.
-- Append-only to the exact V1.7 194-case complete archive. Source lines,
-- prior book errors (including V1.6 two misses) must remain unchanged.
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS marriage_v18_optional_nianming_protocol (
 protocol_id TEXT PRIMARY KEY,
 scope TEXT NOT NULL CHECK(scope='ALL_22_MARRIAGE_SCENES'),
 birth_year_is_optional INTEGER NOT NULL CHECK(birth_year_is_optional=1),
 no_fabricated_year INTEGER NOT NULL CHECK(no_fabricated_year=1),
 fallback_yi_geng_liuhe_day_hour INTEGER NOT NULL CHECK(fallback_yi_geng_liuhe_day_hour=1),
 actual_partner_identity_cannot_be_inferred INTEGER NOT NULL CHECK(actual_partner_identity_cannot_be_inferred=1),
 author_method_and_case_error_separated INTEGER NOT NULL CHECK(author_method_and_case_error_separated=1),
 original_book_source_anchor_count INTEGER NOT NULL CHECK(original_book_source_anchor_count=10),
 parent_full_archive_sha256 TEXT NOT NULL CHECK(length(parent_full_archive_sha256)=64),
 rule_priority_json TEXT NOT NULL CHECK(json_valid(rule_priority_json)),
 no_approved_unseen_forecast_claim INTEGER NOT NULL CHECK(no_approved_unseen_forecast_claim=1)
);
CREATE TABLE IF NOT EXISTS marriage_v18_book_optional_role_sources (
 protocol_id TEXT NOT NULL REFERENCES marriage_v18_optional_nianming_protocol(protocol_id),
 source_key TEXT NOT NULL,
 book_id TEXT NOT NULL,
 section_key TEXT NOT NULL,
 source_line INTEGER NOT NULL CHECK(source_line>0),
 original_whole_book_sha256 TEXT NOT NULL CHECK(length(original_whole_book_sha256)=64),
 original_line_sha256 TEXT NOT NULL CHECK(length(original_line_sha256)=64),
 source_original_excerpt TEXT NOT NULL,
 person_year_required INTEGER NOT NULL DEFAULT 0 CHECK(person_year_required=0),
 PRIMARY KEY(protocol_id,source_key)
);
CREATE TABLE IF NOT EXISTS marriage_v18_optional_year_scene_methods (
 scene_id TEXT PRIMARY KEY REFERENCES marriage22_scenario_protocol(scene_id),
 protocol_id TEXT NOT NULL REFERENCES marriage_v18_optional_nianming_protocol(protocol_id),
 no_year_route_available INTEGER NOT NULL CHECK(no_year_route_available=1),
 one_year_route_available INTEGER NOT NULL CHECK(one_year_route_available=1),
 both_years_route_available INTEGER NOT NULL CHECK(both_years_route_available=1),
 unseen_full_24_factors_approved INTEGER NOT NULL DEFAULT 0 CHECK(unseen_full_24_factors_approved=0),
 human_gpt_phrase_approved INTEGER NOT NULL DEFAULT 0 CHECK(human_gpt_phrase_approved=0),
 intended_question_needs_true_relation_binding INTEGER NOT NULL CHECK(intended_question_needs_true_relation_binding=1),
 source_method_status TEXT NOT NULL CHECK(source_method_status='draft_source_grounded_not_sealed')
);
CREATE TABLE IF NOT EXISTS marriage_v18_missing_year_dev_studies (
 study_id TEXT PRIMARY KEY,
 protocol_id TEXT NOT NULL REFERENCES marriage_v18_optional_nianming_protocol(protocol_id),
 source_event_family TEXT NOT NULL,
 question_scene_id TEXT NOT NULL REFERENCES marriage22_scenario_protocol(scene_id),
 book_source_palaces_original_match INTEGER NOT NULL CHECK(book_source_palaces_original_match=1),
 person_nianming_mode TEXT NOT NULL CHECK(person_nianming_mode IN ('no_year_optional','one_year_optional')),
 missing_year_not_fabricated INTEGER NOT NULL CHECK(missing_year_not_fabricated=1),
 source_decision TEXT NOT NULL CHECK(source_decision IN ('success','failure','mixed','unresolved')),
 first_initial_evidence_json TEXT NOT NULL CHECK(json_valid(first_initial_evidence_json)),
 original_book_source_provenance_json TEXT NOT NULL CHECK(json_valid(original_book_source_provenance_json)),
 history_family_feedback_as_initial_input INTEGER NOT NULL DEFAULT 0 CHECK(history_family_feedback_as_initial_input=0),
 future_actual_book_feedback_scored INTEGER NOT NULL DEFAULT 0 CHECK(future_actual_book_feedback_scored=0),
 non_approved_human_phrase_generated INTEGER NOT NULL DEFAULT 0 CHECK(non_approved_human_phrase_generated=0),
 reading_publication_ready INTEGER NOT NULL DEFAULT 0 CHECK(reading_publication_ready=0)
);
CREATE TABLE IF NOT EXISTS marriage_v18_optional_year_archive_audit (
 version TEXT PRIMARY KEY,
 parent_full_archive_sha256 TEXT NOT NULL CHECK(length(parent_full_archive_sha256)=64),
 original_book_case_count INTEGER NOT NULL CHECK(original_book_case_count=194),
 existing_v16_wrong_dev_answers INTEGER NOT NULL CHECK(existing_v16_wrong_dev_answers=2),
 previous_v17_original_rule_count INTEGER NOT NULL CHECK(previous_v17_original_rule_count=27),
 all_marriage_scenes_with_year_optional INTEGER NOT NULL CHECK(all_marriage_scenes_with_year_optional=22),
 original_line_sources INTEGER NOT NULL CHECK(original_line_sources=10),
 no_year_extra_dev_studies INTEGER NOT NULL CHECK(no_year_extra_dev_studies=2),
 new_validated_real_unseen_predictions INTEGER NOT NULL DEFAULT 0 CHECK(new_validated_real_unseen_predictions=0),
 all_earlier_source_rows_unchanged INTEGER NOT NULL CHECK(all_earlier_source_rows_unchanged=1),
 audit_notes_json TEXT NOT NULL CHECK(json_valid(audit_notes_json))
);
