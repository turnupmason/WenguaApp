-- Kaiwu 5: keep classical verses and later modern author commentary as two provenance
-- layers. No generated paraphrase may masquerade as a literal classical verse.
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS kaiwu_classical_verse_explanations(
 chapter_key TEXT NOT NULL REFERENCES chapter_knowledge(chapter_key),
 verse_number INTEGER NOT NULL CHECK(verse_number BETWEEN 1 AND 12),
 verse_marker_line INTEGER NOT NULL,
 verse_source_line INTEGER NOT NULL,
 verse_original_text TEXT NOT NULL,
 verse_source_sha256 TEXT NOT NULL CHECK(length(verse_source_sha256)=64),
 commentary_marker_line INTEGER NOT NULL,
 commentary_source_line INTEGER NOT NULL,
 commentary_original_text TEXT NOT NULL,
 commentary_source_sha256 TEXT NOT NULL CHECK(length(commentary_source_sha256)=64),
 text_relation TEXT NOT NULL DEFAULT 'original_verse_plus_author_explanation',
 not_independent_ancient_authority INTEGER NOT NULL DEFAULT 1 CHECK(not_independent_ancient_authority=1),
 review_status TEXT NOT NULL DEFAULT 'draft',
 positive_training_eligible INTEGER NOT NULL DEFAULT 0 CHECK(positive_training_eligible=0),
 PRIMARY KEY(chapter_key,verse_number),
 UNIQUE(chapter_key,verse_source_line),
 UNIQUE(chapter_key,commentary_source_line)
);
CREATE TABLE IF NOT EXISTS kaiwu_classical_fate_motifs(
 chapter_key TEXT NOT NULL REFERENCES chapter_knowledge(chapter_key),
 motif_key TEXT NOT NULL,
 verse_number INTEGER NOT NULL CHECK(verse_number BETWEEN 1 AND 12),
 source_line INTEGER NOT NULL CHECK(source_line>0),
 layer TEXT NOT NULL CHECK(layer IN ('ancient_verse','author_explanation')),
 source_excerpt TEXT NOT NULL,
 excerpt_sha256 TEXT NOT NULL CHECK(length(excerpt_sha256)=64),
 track_id TEXT NOT NULL,
 canonical_concept_id TEXT NOT NULL,
 normalized_conditions_json TEXT NOT NULL CHECK(json_valid(normalized_conditions_json)),
 evidence_status TEXT NOT NULL DEFAULT 'verbatim_source_match',
 review_status TEXT NOT NULL DEFAULT 'draft',
 positive_training_eligible INTEGER NOT NULL DEFAULT 0 CHECK(positive_training_eligible=0),
 PRIMARY KEY(chapter_key,motif_key)
);
CREATE INDEX IF NOT EXISTS idx_kaiwu_fate_motifs_concept
 ON kaiwu_classical_fate_motifs(canonical_concept_id,track_id);
