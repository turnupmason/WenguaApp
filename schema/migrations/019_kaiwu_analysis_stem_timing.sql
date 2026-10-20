-- Kaiwu chapter 4: source-backed directional ten-stem pair interpretations and timing.
-- New tables never replace old rule, case, source or V1 snapshots.
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS kaiwu_ordered_stem_pair_occurrences (
  chapter_key TEXT NOT NULL REFERENCES chapter_knowledge(chapter_key),
  upper_stem TEXT NOT NULL,
  lower_stem TEXT NOT NULL,
  source_line INTEGER NOT NULL CHECK(source_line>0),
  source_excerpt TEXT NOT NULL,
  source_excerpt_sha256 TEXT NOT NULL CHECK(length(source_excerpt_sha256)=64),
  reverse_pair_key TEXT NOT NULL,
  source_conditions_json TEXT NOT NULL CHECK(json_valid(source_conditions_json)),
  rule_scope TEXT NOT NULL DEFAULT 'traditional_annotated_source_draft',
  review_status TEXT NOT NULL DEFAULT 'draft' CHECK(review_status IN ('draft','reviewed','approved','rejected')),
  positive_training_eligible INTEGER NOT NULL DEFAULT 0 CHECK(positive_training_eligible=0),
  PRIMARY KEY(chapter_key,upper_stem,lower_stem),
  UNIQUE(chapter_key,source_line),
  FOREIGN KEY(chapter_key) REFERENCES chapter_knowledge(chapter_key)
);
CREATE INDEX IF NOT EXISTS idx_kaiwu_stem_pair_lookup
 ON kaiwu_ordered_stem_pair_occurrences(upper_stem,lower_stem,chapter_key);
CREATE TABLE IF NOT EXISTS kaiwu_timing_source_methods (
  chapter_key TEXT NOT NULL REFERENCES chapter_knowledge(chapter_key),
  method_key TEXT NOT NULL,
  category TEXT NOT NULL CHECK(category IN ('successful_outcome','failed_outcome','interception_recovery','limitation')),
  source_line INTEGER NOT NULL CHECK(source_line>0),
  original_text TEXT NOT NULL,
  excerpt_sha256 TEXT NOT NULL CHECK(length(excerpt_sha256)=64),
  method_metadata_json TEXT NOT NULL CHECK(json_valid(method_metadata_json)),
  review_status TEXT NOT NULL DEFAULT 'draft' CHECK(review_status IN ('draft','reviewed','approved','rejected')),
  positive_training_eligible INTEGER NOT NULL DEFAULT 0 CHECK(positive_training_eligible=0),
  PRIMARY KEY(chapter_key,method_key)
);
