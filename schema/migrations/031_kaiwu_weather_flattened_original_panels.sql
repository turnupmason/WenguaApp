-- Kaiwu ch2 s13 weather source: TWO historical questions and TWO UNRECOVERABLE
-- OCR nine-palace fragments. DO NOT synthesize nine standard original cells.
-- Older Shenqi weather cases use cases.domain_id='weather_historical_source'.
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS kaiwu_weather_raw_cast_fragments (
 chapter_key TEXT NOT NULL REFERENCES chapter_knowledge(chapter_key),
 case_id TEXT NOT NULL REFERENCES cases(case_id),
 cast_key TEXT NOT NULL DEFAULT 'primary',
 source_start_line INTEGER NOT NULL,
 source_end_line INTEGER NOT NULL,
 raw_original_text TEXT NOT NULL,
 raw_sha256 TEXT NOT NULL CHECK(length(raw_sha256)=64),
 raw_line_count INTEGER NOT NULL CHECK(raw_line_count>0),
 source_status TEXT NOT NULL CHECK(source_status='ocr_flattened_unresolvable_nine_palace'),
 nine_palace_positions_confirmed INTEGER NOT NULL DEFAULT 0 CHECK(nine_palace_positions_confirmed=0),
 no_synthesized_chart INTEGER NOT NULL DEFAULT 1 CHECK(no_synthesized_chart=1),
 PRIMARY KEY(chapter_key,case_id,cast_key)
);
CREATE TABLE IF NOT EXISTS kaiwu_weather_raw_fragment_lines (
 chapter_key TEXT NOT NULL,case_id TEXT NOT NULL,cast_key TEXT NOT NULL,
 source_line INTEGER NOT NULL,original_literal TEXT NOT NULL,
 line_sha256 TEXT NOT NULL CHECK(length(line_sha256)=64),
 original_location_not_recovered INTEGER NOT NULL DEFAULT 1 CHECK(original_location_not_recovered=1),
 PRIMARY KEY(chapter_key,case_id,cast_key,source_line),
 FOREIGN KEY(chapter_key,case_id,cast_key)
 REFERENCES kaiwu_weather_raw_cast_fragments(chapter_key,case_id,cast_key)
);
CREATE TABLE IF NOT EXISTS kaiwu_weather_source_claims (
 chapter_key TEXT NOT NULL REFERENCES chapter_knowledge(chapter_key),
 case_id TEXT NOT NULL REFERENCES cases(case_id),
 claim_key TEXT NOT NULL,
 source_line INTEGER NOT NULL,source_literal TEXT NOT NULL,
 claim_type TEXT NOT NULL,
 verification_state TEXT NOT NULL,
 does_not_confirm_printed_palace_cell INTEGER NOT NULL DEFAULT 1 CHECK(does_not_confirm_printed_palace_cell=1),
 metadata_json TEXT NOT NULL CHECK(json_valid(metadata_json)),
 PRIMARY KEY(chapter_key,case_id,claim_key)
);
CREATE TABLE IF NOT EXISTS kaiwu_weather_chronology (
 chapter_key TEXT NOT NULL REFERENCES chapter_knowledge(chapter_key),
 case_id TEXT NOT NULL REFERENCES cases(case_id),
 phase_key TEXT NOT NULL,phase_kind TEXT NOT NULL,
 first_source_line INTEGER NOT NULL,last_source_line INTEGER NOT NULL,
 source_text TEXT NOT NULL,excerpt_sha256 TEXT NOT NULL CHECK(length(excerpt_sha256)=64),
 metadata_json TEXT NOT NULL CHECK(json_valid(metadata_json)),
 PRIMARY KEY(chapter_key,case_id,phase_key)
);
CREATE VIEW IF NOT EXISTS unified_weather_source_cases_across_books AS
 SELECT c.case_id,c.event_family_id,c.domain_id,s.book_id,s.section_key,
 c.known_before,c.author_judgment,c.later_feedback
 FROM cases c JOIN sections s ON c.section_id=s.section_id
 WHERE c.domain_id='weather_historical_source';
