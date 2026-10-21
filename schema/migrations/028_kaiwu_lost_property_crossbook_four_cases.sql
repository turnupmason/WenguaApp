-- Kaiwu 8th source section: 4 genuinely different lost-property inquiries,
-- 4 historical printed charts, 36 literal nine-palace cells. The older
-- Shenqi 8 cases use THE SAME lost_property cases.domain_id, not book silos.
-- Reconstructed OCR text is retained exactly, never algorithmically repaired.
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS kaiwu_lost_source_charts(
 chapter_key TEXT NOT NULL REFERENCES chapter_knowledge(chapter_key),
 case_id TEXT NOT NULL REFERENCES cases(case_id),
 cast_key TEXT NOT NULL DEFAULT 'primary',
 original_caption_line INTEGER NOT NULL,
 source_board_start INTEGER NOT NULL,
 source_board_end INTEGER NOT NULL,
 raw_chart_sha256 TEXT NOT NULL,
 original_cast_calendar_line INTEGER NOT NULL,
 original_cast_calendar_text TEXT NOT NULL,
 PRIMARY KEY(chapter_key,case_id,cast_key),
 UNIQUE(chapter_key,source_board_start));
CREATE TABLE IF NOT EXISTS kaiwu_lost_source_palaces(
 chapter_key TEXT NOT NULL,case_id TEXT NOT NULL,cast_key TEXT NOT NULL,
 palace INTEGER NOT NULL CHECK(palace BETWEEN 1 AND 9),
 source_start_line INTEGER NOT NULL,
 source_end_line INTEGER NOT NULL,
 original_label TEXT NOT NULL,
 original_header TEXT NOT NULL,
 original_door TEXT NOT NULL,
 original_star TEXT NOT NULL,
 literal_text TEXT NOT NULL,
 literal_sha256 TEXT NOT NULL,
 ocr_incomplete INTEGER NOT NULL CHECK(ocr_incomplete IN (0,1)),
 no_inferred_original_data INTEGER NOT NULL DEFAULT 1 CHECK(no_inferred_original_data=1),
 PRIMARY KEY(chapter_key,case_id,cast_key,palace),
 FOREIGN KEY(chapter_key,case_id,cast_key)
 REFERENCES kaiwu_lost_source_charts(chapter_key,case_id,cast_key));
CREATE TABLE IF NOT EXISTS kaiwu_lost_chronological_phases(
 chapter_key TEXT NOT NULL REFERENCES chapter_knowledge(chapter_key),
 case_id TEXT NOT NULL REFERENCES cases(case_id),
 phase_key TEXT NOT NULL,
 phase_kind TEXT NOT NULL,
 source_start_line INTEGER NOT NULL,
 source_end_line INTEGER NOT NULL,
 source_literal TEXT NOT NULL,
 excerpt_sha256 TEXT NOT NULL,
 temporal_guard_json TEXT NOT NULL CHECK(json_valid(temporal_guard_json)),
 PRIMARY KEY(chapter_key,case_id,phase_key));
CREATE TABLE IF NOT EXISTS kaiwu_lost_issue_outcomes(
 chapter_key TEXT NOT NULL REFERENCES chapter_knowledge(chapter_key),
 case_id TEXT NOT NULL REFERENCES cases(case_id),
 issue_key TEXT NOT NULL,
 prediction_source_line INTEGER NOT NULL,
 prediction_original TEXT NOT NULL,
 feedback_source_line INTEGER NOT NULL,
 feedback_original TEXT NOT NULL,
 reported_result_scope TEXT NOT NULL,
 is_criminal_theft INTEGER NOT NULL CHECK(is_criminal_theft IN (0,1)),
 source_book_accepted INTEGER NOT NULL DEFAULT 1 CHECK(source_book_accepted=1),
 externally_verified INTEGER NOT NULL DEFAULT 0 CHECK(externally_verified=0),
 PRIMARY KEY(chapter_key,case_id,issue_key));
CREATE TABLE IF NOT EXISTS kaiwu_lost_temporal_caveats(
 chapter_key TEXT NOT NULL REFERENCES chapter_knowledge(chapter_key),
 case_id TEXT NOT NULL REFERENCES cases(case_id),
 caveat_key TEXT NOT NULL,
 original_source_start INTEGER NOT NULL,
 original_source_end INTEGER NOT NULL,
 original_quote TEXT NOT NULL,
 interpretation_not_in_original_earlier_prediction TEXT NOT NULL,
 mandatory_preserve INTEGER NOT NULL DEFAULT 1 CHECK(mandatory_preserve=1),
 PRIMARY KEY(chapter_key,case_id,caveat_key));
CREATE VIEW IF NOT EXISTS unified_lost_property_cases_across_books AS
 SELECT c.case_id,c.event_family_id,c.domain_id,s.book_id,s.section_key,
 c.known_before,c.author_judgment,c.later_feedback
 FROM cases c JOIN sections s ON s.section_id=c.section_id
 WHERE c.domain_id='lost_property';
