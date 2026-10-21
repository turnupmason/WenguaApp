-- Kaiwu 经营求财 source cases join the existing Shenqi business_profit domain.
-- A mine-collapse rescue has primary industrial_safety, not a claim of business profit.
-- A wrong construction-permit opening date remains a source-explicit FAILURE.
-- 11 independent real inquiries / 11 actual book boards; linked ongoing projects
-- do NOT merge unrelated dated inquiry outcomes or speakers.
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS kaiwu_business_source_casts(
 chapter_key TEXT NOT NULL REFERENCES chapter_knowledge(chapter_key),
 case_id TEXT NOT NULL REFERENCES cases(case_id),
 cast_key TEXT NOT NULL DEFAULT 'primary',
 source_grid_caption_line INTEGER NOT NULL, source_grid_start INTEGER NOT NULL,
 source_grid_end INTEGER NOT NULL,source_grid_sha256 TEXT NOT NULL,
 first_calendar_source_line INTEGER NOT NULL,source_calendar_literal TEXT NOT NULL,
 PRIMARY KEY(chapter_key,case_id,cast_key),UNIQUE(chapter_key,source_grid_start));
CREATE TABLE IF NOT EXISTS kaiwu_business_literal_palaces(
 chapter_key TEXT NOT NULL,case_id TEXT NOT NULL,cast_key TEXT NOT NULL,
 palace INTEGER NOT NULL CHECK(palace BETWEEN 1 AND 9),
 source_start_line INTEGER NOT NULL,source_end_line INTEGER NOT NULL,
 source_header TEXT NOT NULL,source_door TEXT NOT NULL,source_star TEXT NOT NULL,
 extra_row_raw TEXT NOT NULL DEFAULT '',source_literal TEXT NOT NULL,
 source_literal_sha256 TEXT NOT NULL,ocr_incomplete INTEGER NOT NULL CHECK(ocr_incomplete IN(0,1)),
 original_inferred INTEGER NOT NULL DEFAULT 0 CHECK(original_inferred=0),
 PRIMARY KEY(chapter_key,case_id,cast_key,palace),
 FOREIGN KEY(chapter_key,case_id,cast_key) REFERENCES kaiwu_business_source_casts(chapter_key,case_id,cast_key));
CREATE TABLE IF NOT EXISTS kaiwu_business_case_phases(
 chapter_key TEXT NOT NULL REFERENCES chapter_knowledge(chapter_key),
 case_id TEXT NOT NULL REFERENCES cases(case_id),phase_key TEXT NOT NULL,
 phase_type TEXT NOT NULL,first_source_line INTEGER NOT NULL,last_source_line INTEGER NOT NULL,
 full_original_text TEXT NOT NULL,original_sha256 TEXT NOT NULL,
 chronological_notes_json TEXT NOT NULL CHECK(json_valid(chronological_notes_json)),
 PRIMARY KEY(chapter_key,case_id,phase_key));
CREATE TABLE IF NOT EXISTS kaiwu_business_claim_verdicts(
 chapter_key TEXT NOT NULL REFERENCES chapter_knowledge(chapter_key),
 case_id TEXT NOT NULL REFERENCES cases(case_id),claim_key TEXT NOT NULL,
 original_prediction_line INTEGER NOT NULL,original_prediction TEXT NOT NULL,
 reported_feedback_line INTEGER NOT NULL,reported_feedback TEXT NOT NULL,
 verdict TEXT NOT NULL,scope TEXT NOT NULL,
 post_outcome_knowledge_cannot_be_initial INTEGER NOT NULL DEFAULT 1 CHECK(post_outcome_knowledge_cannot_be_initial=1),
 PRIMARY KEY(chapter_key,case_id,claim_key));
CREATE TABLE IF NOT EXISTS kaiwu_business_related_projects(
 chapter_key TEXT NOT NULL REFERENCES chapter_knowledge(chapter_key),
 case_id TEXT NOT NULL REFERENCES cases(case_id),
 related_case_id TEXT NOT NULL REFERENCES cases(case_id),
 association TEXT NOT NULL,
 same_project INTEGER NOT NULL CHECK(same_project=1),
 same_question INTEGER NOT NULL CHECK(same_question=0),
 source_evidence_line INTEGER NOT NULL,source_evidence_literal TEXT NOT NULL,
 PRIMARY KEY(chapter_key,case_id,related_case_id));
CREATE VIEW IF NOT EXISTS unified_business_cases_across_books AS
 SELECT c.case_id,c.event_family_id,c.domain_id,s.book_id,s.section_key,
 c.known_before,c.author_judgment,c.later_feedback FROM cases c
 JOIN sections s ON s.section_id=c.section_id WHERE c.domain_id='business_profit';
CREATE VIEW IF NOT EXISTS unified_industrial_safety_cases_across_books AS
 SELECT c.case_id,c.event_family_id,c.domain_id,s.book_id,s.section_key,
 c.known_before,c.author_judgment,c.later_feedback FROM cases c
 JOIN sections s ON s.section_id=c.section_id WHERE c.domain_id='industrial_safety';
