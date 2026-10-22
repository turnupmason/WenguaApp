-- V3.4 append-only rules audit and twelve original cases, preserve V3.3 sealed results.
PRAGMA foreign_keys=ON;
CREATE TABLE health_v34_role_and_condition_replay (
  event_family_id TEXT PRIMARY KEY,
  source_original_intent TEXT NOT NULL,
  template_intent TEXT NOT NULL CHECK(template_intent='severity'),
  actual_source_day TEXT NOT NULL,
  actual_source_hour TEXT NOT NULL,
  patient_relation TEXT NOT NULL,
  result_status TEXT NOT NULL CHECK(result_status IN('rendered','blocked')),
  blockade_reason TEXT NOT NULL DEFAULT '',
  sealed_reading_sha256 TEXT CHECK(sealed_reading_sha256 IS NULL OR length(sealed_reading_sha256)=64),
  traditional_research_verdict TEXT CHECK(traditional_research_verdict IS NULL OR traditional_research_verdict IN('病吉','病凶')),
  all_42_pairs_tristate_checked INTEGER NOT NULL,
  all_17_composite_tristate_checked INTEGER NOT NULL,
  user_acceptance TEXT NOT NULL CHECK(user_acceptance='pending'),
  original_book_result_loaded INTEGER NOT NULL CHECK(original_book_result_loaded=0),
  medical_accuracy_proven INTEGER NOT NULL CHECK(medical_accuracy_proven=0)
);
CREATE TABLE health_v34_source_rule_audit (
  audit_id TEXT PRIMARY KEY,
  parent_database_sha256 TEXT NOT NULL,
  actor_rules_source TEXT NOT NULL,
  exact_v34_engine TEXT NOT NULL,
  previous_v31_and_v33_seals_untouched INTEGER NOT NULL CHECK(previous_v31_and_v33_seals_untouched=1),
  indexed_ordered_pairs INTEGER NOT NULL CHECK(indexed_ordered_pairs=42),
  indexed_composites INTEGER NOT NULL CHECK(indexed_composites=17),
  incomplete_predicates_cannot_claim_executable INTEGER NOT NULL CHECK(incomplete_predicates_cannot_claim_executable=1),
  prior_book_families INTEGER NOT NULL CHECK(prior_book_families=194),
  prior_book_chapters INTEGER NOT NULL CHECK(prior_book_chapters=43),
  prior_failed_developer_predictions INTEGER NOT NULL CHECK(prior_failed_developer_predictions=2),
  source_author_feedback_not_used INTEGER NOT NULL CHECK(source_author_feedback_not_used=1),
  medical_approval_pending INTEGER NOT NULL CHECK(medical_approval_pending=1)
);
