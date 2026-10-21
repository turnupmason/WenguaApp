-- Kaiwu ch2 s9; original criminal-case evidence only, unified with Shenqi.
-- 2 true historical questions + 2 printed panels; no unprinted offense-time cast.
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS kaiwu_criminal_source_casts(
 chapter_key TEXT NOT NULL REFERENCES chapter_knowledge(chapter_key),
 case_id TEXT NOT NULL REFERENCES cases(case_id),
 cast_key TEXT NOT NULL DEFAULT 'primary',
 original_chart_start INTEGER NOT NULL,
 original_chart_end INTEGER NOT NULL,
 source_sha256 TEXT NOT NULL CHECK(length(source_sha256)=64),
 calendar_source_line INTEGER NOT NULL,
 calendar_original TEXT NOT NULL,
 original_cast_type TEXT NOT NULL,
 PRIMARY KEY(chapter_key,case_id,cast_key),
 UNIQUE(chapter_key,original_chart_start)
);
CREATE TABLE IF NOT EXISTS kaiwu_criminal_original_palaces(
 chapter_key TEXT NOT NULL,case_id TEXT NOT NULL,cast_key TEXT NOT NULL,
 palace INTEGER NOT NULL CHECK(palace BETWEEN 1 AND 9),
 source_start_line INTEGER NOT NULL,source_end_line INTEGER NOT NULL,
 header_original TEXT NOT NULL,deity_original TEXT NOT NULL,
 door_original TEXT NOT NULL,star_original TEXT NOT NULL,
 full_literal_original TEXT NOT NULL,
 source_sha256 TEXT NOT NULL CHECK(length(source_sha256)=64),
 ocr_marked INTEGER NOT NULL CHECK(ocr_marked IN (0,1)),
 not_inferred INTEGER NOT NULL DEFAULT 1 CHECK(not_inferred=1),
 PRIMARY KEY(chapter_key,case_id,cast_key,palace),
 FOREIGN KEY(chapter_key,case_id,cast_key)
 REFERENCES kaiwu_criminal_source_casts(chapter_key,case_id,cast_key)
);
CREATE TABLE IF NOT EXISTS kaiwu_criminal_source_phases(
 chapter_key TEXT NOT NULL REFERENCES chapter_knowledge(chapter_key),
 case_id TEXT NOT NULL REFERENCES cases(case_id),
 phase_key TEXT NOT NULL,phase_type TEXT NOT NULL,
 first_line INTEGER NOT NULL,last_line INTEGER NOT NULL,
 original_text TEXT NOT NULL,excerpt_sha256 TEXT NOT NULL CHECK(length(excerpt_sha256)=64),
 timing_json TEXT NOT NULL CHECK(json_valid(timing_json)),
 PRIMARY KEY(chapter_key,case_id,phase_key)
);
CREATE TABLE IF NOT EXISTS kaiwu_criminal_scoped_claims(
 chapter_key TEXT NOT NULL REFERENCES chapter_knowledge(chapter_key),
 case_id TEXT NOT NULL REFERENCES cases(case_id),
 claim_key TEXT NOT NULL,prediction_line INTEGER NOT NULL,
 prediction_original TEXT NOT NULL,feedback_line INTEGER,
 feedback_original TEXT,
 verdict TEXT NOT NULL CHECK(verdict IN
 ('book_dialogue_confirmed','book_explicit_error','book_reported_difference','unconfirmed_forecast','book_reported_match')),
 interpretation_json TEXT NOT NULL CHECK(json_valid(interpretation_json)),
 PRIMARY KEY(chapter_key,case_id,claim_key)
);
CREATE TABLE IF NOT EXISTS kaiwu_criminal_unprinted_cast_mentions(
 chapter_key TEXT NOT NULL REFERENCES chapter_knowledge(chapter_key),
 case_id TEXT NOT NULL REFERENCES cases(case_id),
 reference_key TEXT NOT NULL,original_line INTEGER NOT NULL,
 original_quote TEXT NOT NULL,
 no_source_panel INTEGER NOT NULL DEFAULT 1 CHECK(no_source_panel=1),
 not_a_new_independent_case INTEGER NOT NULL DEFAULT 1 CHECK(not_a_new_independent_case=1),
 PRIMARY KEY(chapter_key,case_id,reference_key)
);
CREATE VIEW IF NOT EXISTS unified_criminal_cases_across_books AS
 SELECT c.case_id,c.event_family_id,c.domain_id,s.book_id,s.section_key,
 c.known_before,c.author_judgment,c.later_feedback
 FROM cases c JOIN sections s ON s.section_id=c.section_id
 WHERE c.domain_id='criminal_case';
