-- Kaiwu section 16: five printed source witnesses, ONE Shenqi reprint, FOUR new historical events.
-- Printed OCR was flattened: neither nine-palace location nor center deity/gate/star can be reconstructed.
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS kaiwu_life_source_witnesses (
 witness_key TEXT PRIMARY KEY,
 chapter_key TEXT NOT NULL REFERENCES chapter_knowledge(chapter_key),
 section_id INTEGER NOT NULL REFERENCES sections(section_id),
 case_id TEXT NOT NULL REFERENCES cases(case_id),
 source_book TEXT NOT NULL CHECK(source_book='kaiwu'),
 source_start_line INTEGER NOT NULL,
 source_end_line INTEGER NOT NULL,
 printed_chart_first_line INTEGER NOT NULL,
 printed_chart_last_line INTEGER NOT NULL,
 original_raw_chart TEXT NOT NULL,
 original_raw_chart_sha256 TEXT NOT NULL CHECK(length(original_raw_chart_sha256)=64),
 original_chart_spatial_status TEXT NOT NULL CHECK(original_chart_spatial_status='flattened_OCR_no_source_position_certification'),
 witness_relationship TEXT NOT NULL CHECK(witness_relationship IN ('same_prior_event_new_author_explanation','new_retrospective_birth_time_study')),
 metadata_json TEXT NOT NULL CHECK(json_valid(metadata_json))
);
CREATE TABLE IF NOT EXISTS kaiwu_life_original_chart_lines (
 witness_key TEXT NOT NULL REFERENCES kaiwu_life_source_witnesses(witness_key),
 source_line INTEGER NOT NULL, source_original TEXT NOT NULL,
 excerpt_sha256 TEXT NOT NULL CHECK(length(excerpt_sha256)=64),
 original_palace_position_unresolved INTEGER NOT NULL DEFAULT 1 CHECK(original_palace_position_unresolved=1),
 PRIMARY KEY(witness_key,source_line)
);
CREATE TABLE IF NOT EXISTS kaiwu_life_author_step_witnesses (
 witness_key TEXT NOT NULL REFERENCES kaiwu_life_source_witnesses(witness_key),
 step_index INTEGER NOT NULL,
 first_source_line INTEGER NOT NULL,last_source_line INTEGER NOT NULL,
 author_original_text TEXT NOT NULL,
 excerpt_sha256 TEXT NOT NULL CHECK(length(excerpt_sha256)=64),
 phase_kind TEXT NOT NULL,
 evidence_json TEXT NOT NULL CHECK(json_valid(evidence_json)),
 positive_training_eligible INTEGER NOT NULL DEFAULT 0 CHECK(positive_training_eligible=0),
 review_status TEXT NOT NULL DEFAULT 'draft',
 PRIMARY KEY(witness_key,step_index)
);
CREATE TABLE IF NOT EXISTS kaiwu_life_source_phases (
 witness_key TEXT NOT NULL REFERENCES kaiwu_life_source_witnesses(witness_key),
 phase_key TEXT NOT NULL, phase_kind TEXT NOT NULL,
 source_start_line INTEGER NOT NULL, source_end_line INTEGER NOT NULL,
 exact_original_text TEXT NOT NULL,excerpt_sha256 TEXT NOT NULL CHECK(length(excerpt_sha256)=64),
 retrospective_not_prospective INTEGER NOT NULL DEFAULT 1 CHECK(retrospective_not_prospective=1),
 PRIMARY KEY(witness_key,phase_key)
);
CREATE VIEW IF NOT EXISTS unified_life_source_cases_across_books AS
 SELECT c.case_id,c.event_family_id,c.domain_id,s.book_id,s.section_key,c.known_before,
 c.author_yongshen_steps,c.author_judgment,c.later_feedback
 FROM cases c JOIN sections s ON c.section_id=s.section_id
 WHERE c.domain_id='life_opportunity_book_study';
