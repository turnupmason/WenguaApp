-- V3.3 full source research archive: V3.1 replay only, no new medical prediction approval.
-- Exact parent V3.2 is sha256 e4110828...; never overwrite prior archives.
PRAGMA foreign_keys=ON;
CREATE TABLE health_v33_all_historical_health_replay (
  event_family_id TEXT PRIMARY KEY,
  source_book TEXT NOT NULL,
  source_date TEXT NOT NULL,
  source_day TEXT NOT NULL,
  source_hour TEXT NOT NULL,
  source_question_intent TEXT NOT NULL,
  actual_template_intent TEXT NOT NULL CHECK(actual_template_intent='severity'),
  original_author_answer_loaded INTEGER NOT NULL CHECK(original_author_answer_loaded=0),
  original_feedback_loaded INTEGER NOT NULL CHECK(original_feedback_loaded=0),
  cast_or_role_status TEXT NOT NULL,
  failure_reason TEXT NOT NULL DEFAULT '',
  reading_sha256 TEXT CHECK(reading_sha256 IS NULL OR length(reading_sha256)=64),
  traditional_book_method_verdict TEXT CHECK(traditional_book_method_verdict IS NULL OR traditional_book_method_verdict IN ('病吉','病凶')),
  user_review_status TEXT NOT NULL CHECK(user_review_status='pending')
);
CREATE TABLE health_v33_user_disease_curriculum_appendix (
  appendix_id TEXT PRIMARY KEY,
  source_type TEXT NOT NULL CHECK(source_type='direct_user_message'),
  status TEXT NOT NULL CHECK(status='partially_executable_not_full_rule_approval'),
  source_map_path TEXT NOT NULL,
  indexed_ordered_pairs INTEGER NOT NULL CHECK(indexed_ordered_pairs=42),
  indexed_composites INTEGER NOT NULL CHECK(indexed_composites=17),
  eleven_template_slots INTEGER NOT NULL CHECK(eleven_template_slots=11),
  v31_engine_unchanged INTEGER NOT NULL CHECK(v31_engine_unchanged=1),
  four_other_intents_unapproved INTEGER NOT NULL CHECK(four_other_intents_unapproved=4),
  ui_approval_pending INTEGER NOT NULL CHECK(ui_approval_pending=1)
);
