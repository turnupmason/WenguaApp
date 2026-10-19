-- Private-only author narrative sections for incomplete historical examples.
-- Separate prior-known, author-predicted, and after-the-event feedback.
-- Do not export copyrighted excerpts or sensitive user data from local SQLite.
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS incomplete_historical_cases (
  event_family_id TEXT PRIMARY KEY,
  chapter_key TEXT NOT NULL REFERENCES chapter_knowledge(chapter_key),
  reference_json TEXT NOT NULL CHECK(json_valid(reference_json)),
  prior_known_text TEXT NOT NULL,
  chart_evidence_text TEXT NOT NULL,
  author_prediction_text TEXT NOT NULL,
  after_event_feedback_text TEXT NOT NULL,
  chart_is_complete INTEGER NOT NULL DEFAULT 0 CHECK(chart_is_complete IN (0,1)),
  approved_for_blind_test INTEGER NOT NULL DEFAULT 0 CHECK(approved_for_blind_test IN (0,1)),
  review_status TEXT NOT NULL DEFAULT 'draft' CHECK(review_status IN ('draft','reviewed','approved','rejected'))
);
CREATE INDEX IF NOT EXISTS idx_incomplete_cases_chapter
ON incomplete_historical_cases(chapter_key,review_status);
