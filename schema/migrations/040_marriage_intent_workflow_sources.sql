-- 040: V1.2 author-grounded question-specific marriage reasoning workflows.
-- Append workflow definitions, never overwrite 194 events, four language drafts
-- or timing V1.1; NO presumed 1080 fully verified charts.
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS phrase_intent_workflows (
  intent_id TEXT PRIMARY KEY,
  domain_id TEXT NOT NULL REFERENCES phrase_domain_progress(domain_id),
  title TEXT NOT NULL,
  workflow_version TEXT NOT NULL,
  coverage_stage TEXT NOT NULL CHECK(coverage_stage='draft_source_grounded'),
  evidence_strength TEXT NOT NULL CHECK(evidence_strength IN
    ('direct_examples','adjacent_cases_no_independent_engagement_prediction',
     'direct_case_feedback_separate_events','direct_case_with_distinct_wedding_outcome',
     'direct_and_explicit_counterexamples','adjacent_case_inference',
     'direct_book_example_without_followup_plus_counterexample',
     'direct_traditional_symbols_but_not_independent_reality_proof')),
  target_events_json TEXT NOT NULL CHECK(json_valid(target_events_json)),
  applied_context_json TEXT NOT NULL CHECK(json_valid(applied_context_json)),
  human_delivery_policy TEXT NOT NULL,
  require_concrete_outcome INTEGER NOT NULL DEFAULT 1 CHECK(require_concrete_outcome=1),
  require_calendar_calculated_timing_if_applicable INTEGER NOT NULL DEFAULT 1 CHECK(require_calendar_calculated_timing_if_applicable=1),
  forbid_source_feedback_leakage INTEGER NOT NULL DEFAULT 1 CHECK(forbid_source_feedback_leakage=1),
  has_verified_concrete_chart_instance INTEGER NOT NULL DEFAULT 0 CHECK(has_verified_concrete_chart_instance=0),
  approved_for_real_predictive_publication INTEGER NOT NULL DEFAULT 0 CHECK(approved_for_real_predictive_publication=0)
);
CREATE TABLE IF NOT EXISTS phrase_intent_workflow_steps (
  intent_id TEXT NOT NULL REFERENCES phrase_intent_workflows(intent_id),
  step_order INTEGER NOT NULL CHECK(step_order BETWEEN 1 AND 8),
  stage_id TEXT NOT NULL,
  operation_original TEXT NOT NULL,
  required_output TEXT NOT NULL,
  coverage_type TEXT NOT NULL DEFAULT 'source_grounded_workflow_draft',
  PRIMARY KEY(intent_id,step_order)
);
CREATE TABLE IF NOT EXISTS phrase_intent_evidence_links (
  intent_id TEXT NOT NULL REFERENCES phrase_intent_workflows(intent_id),
  source_ordinal INTEGER NOT NULL,
  book_id TEXT NOT NULL CHECK(book_id IN ('shenqi','kaiwu')),
  source_section_key TEXT NOT NULL,
  source_sha256 TEXT NOT NULL CHECK(length(source_sha256)=64),
  case_id TEXT NOT NULL REFERENCES cases(case_id),
  original_source_line_numbers_json TEXT NOT NULL CHECK(json_valid(original_source_line_numbers_json)),
  original_book_snippets_json TEXT NOT NULL CHECK(json_valid(original_book_snippets_json)),
  original_phase_role TEXT NOT NULL,
  is_future_feedback INTEGER NOT NULL DEFAULT 0 CHECK(is_future_feedback IN (0,1)),
  research_only INTEGER NOT NULL DEFAULT 1 CHECK(research_only=1),
  PRIMARY KEY(intent_id,source_ordinal)
);
CREATE TABLE IF NOT EXISTS phrase_intent_workflow_audit (
  domain_id TEXT NOT NULL REFERENCES phrase_domain_progress(domain_id),
  workflow_version TEXT NOT NULL,
  source_archive_parent_sha256 TEXT NOT NULL CHECK(length(source_archive_parent_sha256)=64),
  definitions_sha256 TEXT NOT NULL CHECK(length(definitions_sha256)=64),
  source_method_only INTEGER NOT NULL DEFAULT 1 CHECK(source_method_only=1),
  intent_count INTEGER NOT NULL,
  distinct_source_case_count INTEGER NOT NULL,
  step_count INTEGER NOT NULL,
  source_anchor_count INTEGER NOT NULL,
  published_real_chart_prediction_count INTEGER NOT NULL DEFAULT 0 CHECK(published_real_chart_prediction_count=0),
  original_phrase_draft_count INTEGER NOT NULL,
  qa_status TEXT NOT NULL,
  notes_json TEXT NOT NULL CHECK(json_valid(notes_json)),
  PRIMARY KEY(domain_id,workflow_version)
);
CREATE VIEW IF NOT EXISTS phrase_marriage_intent_author_methods AS
 SELECT w.intent_id,w.title,w.target_events_json,w.evidence_strength,
        st.step_order,st.stage_id,st.operation_original,st.required_output
 FROM phrase_intent_workflows w
 JOIN phrase_intent_workflow_steps st ON st.intent_id=w.intent_id
 WHERE w.domain_id='marriage'
 ORDER BY w.intent_id,st.step_order;
