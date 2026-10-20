PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS education_crossbook_source_casts(
 chapter_key TEXT REFERENCES chapter_knowledge(chapter_key),case_id TEXT REFERENCES cases(case_id),
 source_start_line INTEGER NOT NULL,source_end_line INTEGER NOT NULL,
 source_sha256 TEXT NOT NULL,calendar_line INTEGER NOT NULL,original_calendar TEXT NOT NULL,
 PRIMARY KEY(chapter_key,case_id));
CREATE TABLE IF NOT EXISTS education_crossbook_source_palaces(
 chapter_key TEXT,case_id TEXT,palace INTEGER CHECK(palace BETWEEN 1 AND 9),
 source_start_line INTEGER,source_end_line INTEGER,header_raw TEXT NOT NULL,
 god_raw TEXT NOT NULL,door_raw TEXT NOT NULL,star_raw TEXT NOT NULL,
 original_text TEXT NOT NULL,source_sha256 TEXT NOT NULL,
 PRIMARY KEY(chapter_key,case_id,palace),
 FOREIGN KEY(chapter_key,case_id) REFERENCES education_crossbook_source_casts(chapter_key,case_id));
CREATE TABLE IF NOT EXISTS education_crossbook_candidates(
 chapter_key TEXT REFERENCES chapter_knowledge(chapter_key),case_id TEXT REFERENCES cases(case_id),
 candidate_key TEXT NOT NULL,birth_year_original TEXT NOT NULL,
 prediction_line INTEGER NOT NULL,source_prediction TEXT NOT NULL,
 feedback_line INTEGER NOT NULL,source_reported_outcome TEXT NOT NULL,
 result_class TEXT NOT NULL,metadata_json TEXT NOT NULL CHECK(json_valid(metadata_json)),
 PRIMARY KEY(chapter_key,case_id,candidate_key));
CREATE TABLE IF NOT EXISTS education_crossbook_book_claims(
 chapter_key TEXT REFERENCES chapter_knowledge(chapter_key),case_id TEXT REFERENCES cases(case_id),
 claim_key TEXT NOT NULL,claim_type TEXT NOT NULL,
 initial_prediction_line INTEGER NOT NULL,initial_original TEXT NOT NULL,
 later_report_line INTEGER NOT NULL,later_original TEXT NOT NULL,
 source_verdict TEXT NOT NULL CHECK(source_verdict IN ('book_reported_match','book_explicit_partial_error')),
 no_retrospective_revision INTEGER NOT NULL DEFAULT 1 CHECK(no_retrospective_revision=1),
 PRIMARY KEY(chapter_key,case_id,claim_key));
CREATE TABLE IF NOT EXISTS education_crossbook_source_phases(
 chapter_key TEXT REFERENCES chapter_knowledge(chapter_key),case_id TEXT REFERENCES cases(case_id),
 phase_key TEXT NOT NULL,phase_kind TEXT NOT NULL,source_start INTEGER NOT NULL,
 source_end INTEGER NOT NULL,original_text TEXT NOT NULL,sha256 TEXT NOT NULL,
 metadata_json TEXT NOT NULL CHECK(json_valid(metadata_json)),
 PRIMARY KEY(chapter_key,case_id,phase_key));
CREATE VIEW IF NOT EXISTS unified_education_cases_across_books AS
 SELECT c.case_id,c.event_family_id,c.domain_id,s.book_id,s.section_key,c.known_before,c.author_judgment,c.later_feedback
 FROM cases c JOIN sections s ON c.section_id=s.section_id WHERE c.domain_id='education';
