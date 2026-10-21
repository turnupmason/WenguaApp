-- 039: V1.1 explicit outcome + concrete book-based timing, append only.
-- All V1 pilot drafts and 194 book events remain unchanged and inherited.
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS phrase_version_progress(
 domain_id TEXT NOT NULL REFERENCES phrase_domain_progress(domain_id),
 prompt_version TEXT NOT NULL,
 prompt_sha256 TEXT NOT NULL CHECK(length(prompt_sha256)=64),
 release_stage TEXT NOT NULL,
 inherited_archive_sha256 TEXT NOT NULL CHECK(length(inherited_archive_sha256)=64),
 asserted_original_events INTEGER NOT NULL,
 approved_concrete_instance_count INTEGER NOT NULL DEFAULT 0,
 decision_required INTEGER NOT NULL DEFAULT 1 CHECK(decision_required=1),
 concrete_timing_required_if_calculable INTEGER NOT NULL DEFAULT 1 CHECK(concrete_timing_required_if_calculable=1),
 source_calendar_validation_required INTEGER NOT NULL DEFAULT 1 CHECK(source_calendar_validation_required=1),
 created_utc TEXT NOT NULL,
 notes_json TEXT NOT NULL CHECK(json_valid(notes_json)),
 PRIMARY KEY(domain_id,prompt_version));
CREATE TABLE IF NOT EXISTS phrase_outcome_timing_contracts(
 phrase_id TEXT NOT NULL REFERENCES phrase_template_drafts(phrase_id),
 contract_version INTEGER NOT NULL CHECK(contract_version>=2),
 prompt_version TEXT NOT NULL,
 concrete_outcome_required INTEGER NOT NULL DEFAULT 1 CHECK(concrete_outcome_required=1),
 target_event_required INTEGER NOT NULL DEFAULT 1 CHECK(target_event_required=1),
 source_method_required INTEGER NOT NULL DEFAULT 1 CHECK(source_method_required=1),
 candidate_windows_computed_required INTEGER NOT NULL DEFAULT 1 CHECK(candidate_windows_computed_required=1),
 selected_primary_window_required INTEGER NOT NULL DEFAULT 1 CHECK(selected_primary_window_required=1),
 verified_calendar_provenance_required INTEGER NOT NULL DEFAULT 1 CHECK(verified_calendar_provenance_required=1),
 no_deducible_timing_requires_exact_blockers INTEGER NOT NULL DEFAULT 1 CHECK(no_deducible_timing_requires_exact_blockers=1),
 style_only_until_chart_verified INTEGER NOT NULL DEFAULT 1 CHECK(style_only_until_chart_verified=1),
 release_status TEXT NOT NULL DEFAULT 'needs_verified_chart_and_timing' CHECK(release_status='needs_verified_chart_and_timing'),
 user_directive TEXT NOT NULL,
 PRIMARY KEY(phrase_id,contract_version));
CREATE TABLE IF NOT EXISTS phrase_instance_timing_windows(
 window_id TEXT PRIMARY KEY,
 instance_id TEXT NOT NULL REFERENCES phrase_context_instances(instance_id),
 event_type TEXT NOT NULL,
 predicted_outcome TEXT NOT NULL CHECK(predicted_outcome IN ('success','failure','delayed','mixed')),
 timing_granularity TEXT NOT NULL CHECK(timing_granularity IN ('day','month','year')),
 window_start_iso TEXT NOT NULL,window_end_iso TEXT NOT NULL,
 source_method_refs_json TEXT NOT NULL CHECK(json_valid(source_method_refs_json)),
 competing_candidates_json TEXT NOT NULL CHECK(json_valid(competing_candidates_json)),
 supporting_evidence_json TEXT NOT NULL CHECK(json_valid(supporting_evidence_json)),
 contrary_evidence_json TEXT NOT NULL CHECK(json_valid(contrary_evidence_json)),
 primary_window_selection_reason TEXT NOT NULL,
 complete_calendar_receipt TEXT NOT NULL,
 calendar_method_version TEXT NOT NULL,
 traditional_forecast_not_externally_verified INTEGER NOT NULL DEFAULT 1 CHECK(traditional_forecast_not_externally_verified=1),
 created_utc TEXT NOT NULL);
CREATE TRIGGER IF NOT EXISTS trg_marriage_instance_approved_requires_computed_timing
 BEFORE UPDATE OF status ON phrase_context_instances
 WHEN NEW.status='approved'
 BEGIN
 SELECT CASE WHEN NOT EXISTS(
  SELECT 1 FROM phrase_instance_timing_windows t WHERE t.instance_id=NEW.instance_id
  AND t.event_type=NEW.question_type AND t.predicted_outcome<>'unresolved'
  AND length(t.complete_calendar_receipt)>0
  AND length(t.primary_window_selection_reason)>0
  ) THEN RAISE(ABORT,'APPROVAL_BLOCKED_MISSING_COMPUTED_SOURCE_TIMING') END;
 END;
CREATE TRIGGER IF NOT EXISTS trg_marriage_instance_cannot_insert_directly_approved
 BEFORE INSERT ON phrase_context_instances
 WHEN NEW.status='approved'
 BEGIN
  SELECT RAISE(ABORT,'CREATE_DRAFT_THEN_CALCULATE_SOURCE_TIMING_BEFORE_APPROVAL');
 END;
