-- 041: all-domain six-layer hard gate; marriage 22-scene incremental curriculum.
-- Append only to the SHA-pinned full V1.2 194-book-case marriage archive.
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS domain_six_layer_contract (
  contract_version TEXT PRIMARY KEY,
  scope TEXT NOT NULL CHECK(scope='ALL_DOMAINS'),
  enforce_all_six INTEGER NOT NULL CHECK(enforce_all_six=1),
  physical_factor_count INTEGER NOT NULL CHECK(physical_factor_count>=24),
  author_provenance_mandatory INTEGER NOT NULL CHECK(author_provenance_mandatory=1),
  no_feedback_leakage INTEGER NOT NULL CHECK(no_feedback_leakage=1),
  outcome_required_if_supported INTEGER NOT NULL CHECK(outcome_required_if_supported=1),
  computed_timing_when_supported INTEGER NOT NULL CHECK(computed_timing_when_supported=1),
  gpt_cannot_invent_evidence INTEGER NOT NULL CHECK(gpt_cannot_invent_evidence=1),
  field_missing_means_blocked INTEGER NOT NULL CHECK(field_missing_means_blocked=1),
  applied_to_all_new_domains INTEGER NOT NULL CHECK(applied_to_all_new_domains=1),
  archive_parent_sha256 TEXT NOT NULL CHECK(length(archive_parent_sha256)=64),
  notes_json TEXT NOT NULL CHECK(json_valid(notes_json))
);
CREATE TABLE IF NOT EXISTS marriage22_scenario_protocol (
 scene_id TEXT PRIMARY KEY,
 domain_id TEXT NOT NULL REFERENCES phrase_domain_progress(domain_id),
 scene_number INTEGER NOT NULL UNIQUE CHECK(scene_number BETWEEN 1 AND 22),
 title TEXT NOT NULL,
 parent_intent_id TEXT NOT NULL REFERENCES phrase_intent_workflows(intent_id),
 target_event TEXT NOT NULL,
 evidence_grade TEXT NOT NULL,
 role_and_yongshen_candidates TEXT NOT NULL,
 dynamic_factor_focus TEXT NOT NULL,
 explicit_unsupported_claims TEXT NOT NULL,
 timing_target TEXT NOT NULL,
 source_status TEXT NOT NULL DEFAULT 'draft_source_grounded' CHECK(source_status='draft_source_grounded'),
 user_scenario_as_author_verified INTEGER NOT NULL DEFAULT 0 CHECK(user_scenario_as_author_verified=0),
 real_verified_cast_count INTEGER NOT NULL DEFAULT 0 CHECK(real_verified_cast_count=0),
 approved_phrase_count INTEGER NOT NULL DEFAULT 0 CHECK(approved_phrase_count=0),
 protocol_json TEXT NOT NULL CHECK(json_valid(protocol_json))
);
CREATE TABLE IF NOT EXISTS marriage22_six_layer_steps (
 scene_id TEXT NOT NULL REFERENCES marriage22_scenario_protocol(scene_id),
 layer_number INTEGER NOT NULL CHECK(layer_number BETWEEN 1 AND 6),
 layer_id TEXT NOT NULL,
 full_requirement_json TEXT NOT NULL CHECK(json_valid(full_requirement_json)),
 subtype_action_json TEXT NOT NULL CHECK(json_valid(subtype_action_json)),
 check_required INTEGER NOT NULL DEFAULT 1 CHECK(check_required=1),
 publication_allowed_without_this_layer INTEGER NOT NULL DEFAULT 0 CHECK(publication_allowed_without_this_layer=0),
 PRIMARY KEY(scene_id,layer_number)
);
CREATE TABLE IF NOT EXISTS marriage22_original_case_links (
 scene_id TEXT NOT NULL REFERENCES marriage22_scenario_protocol(scene_id),
 source_ordinal INTEGER NOT NULL,
 inherited_parent_intent_id TEXT NOT NULL REFERENCES phrase_intent_workflows(intent_id),
 book_id TEXT NOT NULL CHECK(book_id IN ('shenqi','kaiwu')),
 section_key TEXT NOT NULL,
 original_source_sha256 TEXT NOT NULL CHECK(length(original_source_sha256)=64),
 original_case_id TEXT NOT NULL REFERENCES cases(case_id),
 source_lines_json TEXT NOT NULL CHECK(json_valid(source_lines_json)),
 source_snippets_json TEXT NOT NULL CHECK(json_valid(source_snippets_json)),
 source_phase TEXT NOT NULL,
 feedback_not_initial_reasoning INTEGER NOT NULL CHECK(feedback_not_initial_reasoning IN (0,1)),
 applicable_to_subscene TEXT NOT NULL,
 independent_confirmation_of_scene INTEGER NOT NULL DEFAULT 0 CHECK(independent_confirmation_of_scene=0),
 PRIMARY KEY(scene_id,source_ordinal)
);
CREATE TABLE IF NOT EXISTS six_layer_instance_trace (
 instance_id TEXT NOT NULL REFERENCES phrase_context_instances(instance_id),
 layer_number INTEGER NOT NULL CHECK(layer_number BETWEEN 1 AND 6),
 layer_id TEXT NOT NULL,
 layer_status TEXT NOT NULL CHECK(layer_status IN ('passed','blocked','unknown')),
 source_evidence_json TEXT NOT NULL CHECK(json_valid(source_evidence_json)),
 evidence_sha256 TEXT NOT NULL CHECK(length(evidence_sha256)=64),
 rule_and_calendar_versions_json TEXT NOT NULL CHECK(json_valid(rule_and_calendar_versions_json)),
 PRIMARY KEY(instance_id,layer_number)
);
CREATE TRIGGER IF NOT EXISTS trg_six_layers_on_final_phrase_status
 BEFORE UPDATE OF status ON phrase_context_instances
 WHEN NEW.status='approved'
 BEGIN
  SELECT CASE WHEN (SELECT COUNT(*) FROM six_layer_instance_trace tr
   WHERE tr.instance_id=NEW.instance_id AND tr.layer_status='passed')<>6
    THEN RAISE(ABORT,'SIX_LAYER_PIPELINE_NOT_COMPLETE') END;
 END;
CREATE TABLE IF NOT EXISTS marriage22_scene_catalog_audit (
 audit_version TEXT PRIMARY KEY,
 full_parent_sha256 TEXT NOT NULL CHECK(length(full_parent_sha256)=64),
 catalog_sha256 TEXT NOT NULL CHECK(length(catalog_sha256)=64),
 scene_count INTEGER NOT NULL CHECK(scene_count=22),
 mandatory_layer_rows INTEGER NOT NULL CHECK(mandatory_layer_rows=132),
 inherited_source_references INTEGER NOT NULL CHECK(inherited_source_references>=22),
 previous_book_case_count INTEGER NOT NULL CHECK(previous_book_case_count=194),
 earlier_nine_workflows_preserved INTEGER NOT NULL CHECK(earlier_nine_workflows_preserved=9),
 verified_new_chart_instances INTEGER NOT NULL DEFAULT 0 CHECK(verified_new_chart_instances=0),
 claims_of_100_percent_predictive_accuracy INTEGER NOT NULL DEFAULT 0 CHECK(claims_of_100_percent_predictive_accuracy=0),
 notes_json TEXT NOT NULL CHECK(json_valid(notes_json))
);
