-- V1 source-linked semantic knowledge for Chapter 4 & 5; the raw excerpt field
-- is LOCAL-ONLY. Never add local/*.sqlite3 to the public repository.
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS semantic_assertions (
  chapter_key TEXT NOT NULL REFERENCES chapter_knowledge(chapter_key),
  concept_id TEXT NOT NULL,
  kind TEXT NOT NULL,
  relation TEXT NOT NULL,
  source_start_line INTEGER NOT NULL CHECK(source_start_line>0),
  source_end_line INTEGER NOT NULL CHECK(source_end_line>=source_start_line),
  metadata_json TEXT NOT NULL CHECK(json_valid(metadata_json)),
  original_excerpt TEXT NOT NULL DEFAULT '',
  review_status TEXT NOT NULL DEFAULT 'draft'
    CHECK(review_status IN ('draft','reviewed','approved','rejected')),
  PRIMARY KEY (chapter_key, concept_id, source_start_line)
);
CREATE INDEX IF NOT EXISTS idx_semantic_concept
  ON semantic_assertions(concept_id,kind);
CREATE INDEX IF NOT EXISTS idx_semantic_kind
  ON semantic_assertions(kind,chapter_key);
