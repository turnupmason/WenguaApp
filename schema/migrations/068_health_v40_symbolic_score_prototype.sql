-- Append-only V4.0 DRAFT symbolic score ledger (not health/probability) from full V3.9.
PRAGMA foreign_keys=ON;
CREATE TABLE health_v40_symbolic_score_model (
  version TEXT PRIMARY KEY,
  parent_full_v39_sha256 TEXT NOT NULL CHECK(length(parent_full_v39_sha256)=64),
  status TEXT NOT NULL CHECK(status='research_draft_unapproved'),
  score_baseline INTEGER NOT NULL CHECK(score_baseline=100),
  scoring_is_probability INTEGER NOT NULL CHECK(scoring_is_probability=0),
  scoring_is_medical_index INTEGER NOT NULL CHECK(scoring_is_medical_index=0),
  original_case_families INTEGER NOT NULL CHECK(original_case_families=194),
  original_chapters INTEGER NOT NULL CHECK(original_chapters=43),
  original_ordered_pairs INTEGER NOT NULL CHECK(original_ordered_pairs=81),
  supplemental_disease_pairs INTEGER NOT NULL CHECK(supplemental_disease_pairs=42),
  composite_condition_entries INTEGER NOT NULL CHECK(composite_condition_entries=17),
  old_warnings_and_failed_records_preserved INTEGER NOT NULL CHECK(old_warnings_and_failed_records_preserved=1)
);
CREATE TABLE health_v40_three_symbolic_score_trials (
  case_id TEXT PRIMARY KEY,
  question_kind TEXT NOT NULL CHECK(question_kind IN('user_new','older_book_first_question')),
  signed_delta_sum INTEGER NOT NULL,
  raw_score INTEGER NOT NULL,
  shown_score INTEGER NOT NULL CHECK(shown_score BETWEEN 0 AND 100),
  score_ledger_sha256 TEXT NOT NULL CHECK(length(score_ledger_sha256)=64),
  uncertain_rules_count INTEGER NOT NULL CHECK(uncertain_rules_count>=0),
  older_original_answer_as_input INTEGER NOT NULL CHECK(older_original_answer_as_input=0),
  customer_approved INTEGER NOT NULL CHECK(customer_approved=0),
  FOREIGN KEY (case_id) REFERENCES health_v40_three_symbolic_score_trials(case_id)
);
