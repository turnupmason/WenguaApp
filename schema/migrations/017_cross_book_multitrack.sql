-- Cross-book additive provenance, no alteration to Shenqi V1 or existing author cases.
-- A shared concept identity does NOT imply replacing, merging or approving source statements.
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS cross_book_concept_tracks (
 chapter_key TEXT NOT NULL,
 concept_id TEXT NOT NULL,
 source_start_line INTEGER NOT NULL CHECK(source_start_line>0),
 source_end_line INTEGER NOT NULL CHECK(source_end_line>=source_start_line),
 source_section_id INTEGER NOT NULL REFERENCES sections(section_id),
 source_sha256 TEXT NOT NULL CHECK(length(source_sha256)=64),
 excerpt_sha256 TEXT NOT NULL CHECK(length(excerpt_sha256)=64),
 track_id TEXT NOT NULL,
 relation_to_prior TEXT NOT NULL CHECK(relation_to_prior IN
 ('reaffirms','clarifies','extends','supplements','additional_exposition','potential_conflict','separate_context')),
 comparison_state TEXT NOT NULL DEFAULT 'candidate_not_human_verified',
 normalized_json TEXT NOT NULL CHECK(json_valid(normalized_json)),
 review_status TEXT NOT NULL DEFAULT 'draft' CHECK(review_status IN
 ('draft','reviewed','approved','rejected')),
 PRIMARY KEY (chapter_key,concept_id,source_start_line),
 FOREIGN KEY (chapter_key,concept_id,source_start_line)
 REFERENCES semantic_assertions(chapter_key,concept_id,source_start_line)
);
CREATE INDEX IF NOT EXISTS idx_cross_book_tracks_concept ON cross_book_concept_tracks(concept_id,track_id);
CREATE INDEX IF NOT EXISTS idx_cross_book_tracks_source ON cross_book_concept_tracks(source_section_id,source_sha256);

-- Explicit bibliographic references: pointing at an old book is NOT a new case,
-- a new chart, an independent confirmation, or a validated event-id linkage.
CREATE TABLE IF NOT EXISTS cross_book_example_references (
 source_chapter_key TEXT NOT NULL REFERENCES chapter_knowledge(chapter_key),
 source_line INTEGER NOT NULL CHECK(source_line>0),
 target_book_id TEXT NOT NULL REFERENCES books(book_id),
 target_printed_page TEXT NOT NULL,
 reference_key TEXT NOT NULL,
 metadata_json TEXT NOT NULL CHECK(json_valid(metadata_json)),
 verified_target_case_id TEXT REFERENCES cases(case_id),
 PRIMARY KEY(source_chapter_key,reference_key),
 UNIQUE(source_chapter_key,source_line)
);
CREATE INDEX IF NOT EXISTS idx_cross_book_ref_target ON cross_book_example_references(target_book_id,target_printed_page);
