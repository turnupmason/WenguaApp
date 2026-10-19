-- WenguaApp first source-derived casting knowledge registry.
-- Does not store copyrighted source text in the public repository.
-- Source bytes stay in local SQLite.sections; public metadata only lives here.
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS chapter_knowledge (
  chapter_key TEXT PRIMARY KEY,
  book_id TEXT NOT NULL REFERENCES books(book_id),
  title TEXT NOT NULL,
  source_sha256 TEXT NOT NULL CHECK(length(source_sha256)=64),
  source_length_bytes INTEGER NOT NULL,
  knowledge_version TEXT NOT NULL,
  review_status TEXT NOT NULL CHECK(review_status IN ('draft','reviewed','approved','rejected')),
  full_source_local_required INTEGER NOT NULL DEFAULT 1 CHECK(full_source_local_required IN (0,1)),
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS casting_knowledge_entries (
  chapter_key TEXT NOT NULL REFERENCES chapter_knowledge(chapter_key),
  entry_id TEXT NOT NULL,
  category TEXT NOT NULL CHECK(category IN ('foundation','casting_procedure','casting_example')),
  payload_json TEXT NOT NULL CHECK(json_valid(payload_json)),
  payload_sha256 TEXT NOT NULL CHECK(length(payload_sha256)=64),
  approval_state TEXT NOT NULL DEFAULT 'draft' CHECK(approval_state IN ('draft','reviewed','approved','rejected')),
  PRIMARY KEY(chapter_key,entry_id)
);
CREATE INDEX IF NOT EXISTS idx_casting_knowledge_category ON casting_knowledge_entries(category,chapter_key);
