-- User-prescribed source-internal case verdicts, distinct from scientific validation.
-- Designed for indivisible event families and single-response product flow.
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS historical_case_book_verdicts (
  event_family_id TEXT PRIMARY KEY,
  primary_case_id TEXT NOT NULL REFERENCES cases(case_id),
  verdict TEXT NOT NULL CHECK(verdict IN
     ('author_book_success_default','author_book_error_explicit')),
  explicit_source_correction INTEGER NOT NULL DEFAULT 0 CHECK(explicit_source_correction IN(0,1)),
  source_correction_lines_json TEXT NOT NULL DEFAULT '[]' CHECK(json_valid(source_correction_lines_json)),
  feedback_source_lines_json TEXT NOT NULL DEFAULT '[]' CHECK(json_valid(feedback_source_lines_json)),
  independent_external_verification TEXT NOT NULL DEFAULT 'not_verified',
  app_output_protocol TEXT NOT NULL DEFAULT 'single_answer_for_one_cast',
  evidence_review_status TEXT NOT NULL DEFAULT 'book_source_only',
  note TEXT NOT NULL DEFAULT ''
);
CREATE INDEX IF NOT EXISTS idx_book_verdict_status
  ON historical_case_book_verdicts(verdict,independent_external_verification);
