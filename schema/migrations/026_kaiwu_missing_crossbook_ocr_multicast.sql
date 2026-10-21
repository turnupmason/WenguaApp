PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS missing_crossbook_casts(
 chapter_key TEXT NOT NULL REFERENCES chapter_knowledge(chapter_key),
 case_id TEXT NOT NULL REFERENCES cases(case_id),cast_key TEXT NOT NULL,
 grid_start INTEGER NOT NULL,grid_end INTEGER NOT NULL,
 source_sha256 TEXT NOT NULL,calendar_line INTEGER NOT NULL,
 original_calendar TEXT NOT NULL,context TEXT NOT NULL,
 PRIMARY KEY(chapter_key,case_id,cast_key), UNIQUE(chapter_key,grid_start));
CREATE TABLE IF NOT EXISTS missing_crossbook_palaces(
 chapter_key TEXT NOT NULL,case_id TEXT NOT NULL,cast_key TEXT NOT NULL,
 palace INTEGER NOT NULL CHECK(palace BETWEEN 1 AND 9),
 source_line_start INTEGER NOT NULL,source_line_end INTEGER NOT NULL,
 header TEXT NOT NULL,spirit TEXT NOT NULL,door TEXT NOT NULL,star TEXT NOT NULL,
 extra_source_row TEXT NOT NULL DEFAULT '',literal TEXT NOT NULL,source_sha256 TEXT NOT NULL,
 ocr_deficient INTEGER NOT NULL CHECK(ocr_deficient IN (0,1)),
 no_inferred_original_data INTEGER NOT NULL DEFAULT 1 CHECK(no_inferred_original_data=1),
 PRIMARY KEY(chapter_key,case_id,cast_key,palace),
 FOREIGN KEY(chapter_key,case_id,cast_key) REFERENCES missing_crossbook_casts(chapter_key,case_id,cast_key));
CREATE TABLE IF NOT EXISTS missing_crossbook_phases(
 chapter_key TEXT NOT NULL REFERENCES chapter_knowledge(chapter_key),
 case_id TEXT NOT NULL REFERENCES cases(case_id),phase_key TEXT NOT NULL,
 phase_type TEXT NOT NULL,first_line INTEGER NOT NULL,last_line INTEGER NOT NULL,
 original TEXT NOT NULL,source_sha256 TEXT NOT NULL,
 chronology_json TEXT NOT NULL CHECK(json_valid(chronology_json)),
 PRIMARY KEY(chapter_key,case_id,phase_key));
CREATE TABLE IF NOT EXISTS missing_crossbook_subjects(
 chapter_key TEXT NOT NULL REFERENCES chapter_knowledge(chapter_key),
 case_id TEXT NOT NULL REFERENCES cases(case_id),subject_key TEXT NOT NULL,
 source_relation TEXT NOT NULL,outcome_original TEXT NOT NULL,
 outcome_line INTEGER NOT NULL,metadata_json TEXT NOT NULL CHECK(json_valid(metadata_json)),
 PRIMARY KEY(chapter_key,case_id,subject_key));
CREATE TABLE IF NOT EXISTS missing_crossbook_claim_checks(
 chapter_key TEXT NOT NULL REFERENCES chapter_knowledge(chapter_key),
 case_id TEXT NOT NULL REFERENCES cases(case_id),claim_key TEXT NOT NULL,
 predicted_date_original TEXT NOT NULL,feedback_date_original TEXT NOT NULL,
 source_prediction_line INTEGER NOT NULL,source_feedback_line INTEGER NOT NULL,
 status TEXT NOT NULL,original_qualified_context TEXT NOT NULL,
 PRIMARY KEY(chapter_key,case_id,claim_key));
CREATE VIEW IF NOT EXISTS unified_missing_person_cases_across_books AS
 SELECT c.case_id,c.event_family_id,c.domain_id,s.book_id,s.section_key,
 c.known_before,c.author_judgment,c.later_feedback FROM cases c
 JOIN sections s ON s.section_id=c.section_id WHERE c.domain_id='missing_person';
