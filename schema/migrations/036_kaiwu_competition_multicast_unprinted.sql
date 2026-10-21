-- Kaiwu competition/ranking: one school accreditation event with 3 source cast
-- mentions (first unprinted), one 1999 collegiate debate event (two group winners).
-- OCR spatial position of all three printed fragments is not independently recoverable.
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS kaiwu_competition_source_episodes(
 chapter_key TEXT NOT NULL REFERENCES chapter_knowledge(chapter_key),
 case_id TEXT NOT NULL REFERENCES cases(case_id),
 episode_key TEXT NOT NULL,
 first_source_line INTEGER NOT NULL,last_source_line INTEGER NOT NULL,
 date_claim TEXT NOT NULL,topic TEXT NOT NULL,
 cast_state TEXT NOT NULL CHECK(cast_state IN('historical_original_lost','printed_OCR_flattened')),
 original_excerpt TEXT NOT NULL,sha256 TEXT NOT NULL,
 event_family_is_shared INTEGER NOT NULL DEFAULT 1 CHECK(event_family_is_shared=1),
 metadata_json TEXT NOT NULL CHECK(json_valid(metadata_json)),
 PRIMARY KEY(chapter_key,case_id,episode_key));
CREATE TABLE IF NOT EXISTS kaiwu_competition_raw_casts(
 chapter_key TEXT NOT NULL REFERENCES chapter_knowledge(chapter_key),
 case_id TEXT NOT NULL REFERENCES cases(case_id),episode_key TEXT NOT NULL,
 source_start INTEGER NOT NULL,source_end INTEGER NOT NULL,
 original_OCR TEXT NOT NULL,source_sha256 TEXT NOT NULL,
 original_source_position_certified INTEGER NOT NULL DEFAULT 0 CHECK(original_source_position_certified=0),
 retained_as_fragment_only INTEGER NOT NULL DEFAULT 1 CHECK(retained_as_fragment_only=1),
 PRIMARY KEY(chapter_key,case_id,episode_key),
 FOREIGN KEY(chapter_key,case_id,episode_key)
 REFERENCES kaiwu_competition_source_episodes(chapter_key,case_id,episode_key));
CREATE TABLE IF NOT EXISTS kaiwu_competition_raw_lines(
 chapter_key TEXT NOT NULL,case_id TEXT NOT NULL,episode_key TEXT NOT NULL,
 original_line_number INTEGER NOT NULL,original_line TEXT NOT NULL,sha256 TEXT NOT NULL,
 PRIMARY KEY(chapter_key,case_id,episode_key,original_line_number),
 FOREIGN KEY(chapter_key,case_id,episode_key)
 REFERENCES kaiwu_competition_raw_casts(chapter_key,case_id,episode_key));
CREATE TABLE IF NOT EXISTS kaiwu_competition_source_phases(
 chapter_key TEXT NOT NULL REFERENCES chapter_knowledge(chapter_key),
 case_id TEXT NOT NULL REFERENCES cases(case_id),
 phase_key TEXT NOT NULL,phase_kind TEXT NOT NULL,
 source_start INTEGER NOT NULL,source_end INTEGER NOT NULL,
 source_original TEXT NOT NULL,sha256 TEXT NOT NULL,
 initially_visible INTEGER NOT NULL DEFAULT 0 CHECK(initially_visible IN(0,1)),
 metadata_json TEXT NOT NULL CHECK(json_valid(metadata_json)),
 PRIMARY KEY(chapter_key,case_id,phase_key));
CREATE TABLE IF NOT EXISTS kaiwu_competition_author_steps(
 chapter_key TEXT NOT NULL REFERENCES chapter_knowledge(chapter_key),
 case_id TEXT NOT NULL REFERENCES cases(case_id),
 episode_key TEXT NOT NULL,step_number INTEGER NOT NULL,
 source_line INTEGER NOT NULL,original_author_text TEXT NOT NULL,sha256 TEXT NOT NULL,
 evidence_json TEXT NOT NULL CHECK(json_valid(evidence_json)),
 status TEXT NOT NULL DEFAULT 'draft' CHECK(status='draft'),
 positive_training_eligible INTEGER NOT NULL DEFAULT 0 CHECK(positive_training_eligible=0),
 PRIMARY KEY(chapter_key,case_id,episode_key,step_number));
CREATE TABLE IF NOT EXISTS kaiwu_competition_conditional_methods(
 chapter_key TEXT NOT NULL REFERENCES chapter_knowledge(chapter_key),
 method_id TEXT NOT NULL,case_id TEXT NOT NULL REFERENCES cases(case_id),
 original_line INTEGER NOT NULL,source_original TEXT NOT NULL,
 preconditions_json TEXT NOT NULL CHECK(json_valid(preconditions_json)),
 source_level_claim TEXT NOT NULL,limits_json TEXT NOT NULL CHECK(json_valid(limits_json)),
 status TEXT NOT NULL DEFAULT 'draft' CHECK(status='draft'),
 positive_training_eligible INTEGER NOT NULL DEFAULT 0 CHECK(positive_training_eligible=0),
 PRIMARY KEY(chapter_key,method_id));
CREATE VIEW IF NOT EXISTS unified_competition_cross_book_cases AS
 SELECT c.case_id,c.event_family_id,s.book_id,s.section_key,c.domain_id,
 c.known_before,c.author_yongshen_steps,c.author_judgment,c.later_feedback
 FROM cases c JOIN sections s ON c.section_id=s.section_id
 WHERE c.domain_id IN ('competition_evaluation','sports_competition')
 OR EXISTS(SELECT 1 FROM unified_case_domain_facets f
 WHERE f.case_id=c.case_id AND f.domain_id='competition_evaluation');
