-- Source-only incremental provenance for 《开悟之门》出行出国6例.
-- SIX distinct reported inquiries, SEVEN actual printed Qimen boards.
-- Case1 is a post-disaster retrospective reconstruction (NOT a prediction).
-- Case3 same immigration application with two consultations and original boards.
-- Unknown OCR/extra lines are never interpreted as source regular stars/doors.
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS kaiwu_travel_source_casts(
 chapter_key TEXT NOT NULL REFERENCES chapter_knowledge(chapter_key),
 case_id TEXT NOT NULL REFERENCES cases(case_id),cast_key TEXT NOT NULL,
 caption_line INTEGER NOT NULL,source_start_line INTEGER NOT NULL,
 source_end_line INTEGER NOT NULL,grid_source_sha256 TEXT NOT NULL,
 calendar_source_line INTEGER NOT NULL,calendar_original TEXT NOT NULL,
 source_time_phase TEXT NOT NULL,outcome_known_at_cast INTEGER NOT NULL CHECK(outcome_known_at_cast IN(0,1)),
 cast_metadata_json TEXT NOT NULL CHECK(json_valid(cast_metadata_json)),
 PRIMARY KEY(chapter_key,case_id,cast_key),UNIQUE(chapter_key,source_start_line)
);
CREATE TABLE IF NOT EXISTS kaiwu_travel_original_palaces(
 chapter_key TEXT NOT NULL,case_id TEXT NOT NULL,cast_key TEXT NOT NULL,
 palace INTEGER NOT NULL CHECK(palace BETWEEN 1 AND 9),
 original_start_line INTEGER NOT NULL,original_end_line INTEGER NOT NULL,
 palace_header_raw TEXT NOT NULL,spirit_raw TEXT NOT NULL,
 gate_raw TEXT NOT NULL,star_raw TEXT NOT NULL,
 extra_rows_json TEXT NOT NULL CHECK(json_valid(extra_rows_json)),
 source_literal_text TEXT NOT NULL,source_literal_sha256 TEXT NOT NULL,
 ocr_unresolved INTEGER NOT NULL CHECK(ocr_unresolved IN(0,1)),
 no_inferred_source_characters INTEGER NOT NULL DEFAULT 1 CHECK(no_inferred_source_characters=1),
 PRIMARY KEY(chapter_key,case_id,cast_key,palace),
 FOREIGN KEY(chapter_key,case_id,cast_key)
 REFERENCES kaiwu_travel_source_casts(chapter_key,case_id,cast_key)
);
CREATE TABLE IF NOT EXISTS kaiwu_travel_chronology(
 chapter_key TEXT NOT NULL REFERENCES chapter_knowledge(chapter_key),
 case_id TEXT NOT NULL REFERENCES cases(case_id),phase_key TEXT NOT NULL,
 phase_kind TEXT NOT NULL,source_start_line INTEGER NOT NULL,source_end_line INTEGER NOT NULL,
 source_literal TEXT NOT NULL,excerpt_sha256 TEXT NOT NULL,
 timing_metadata_json TEXT NOT NULL CHECK(json_valid(timing_metadata_json)),
 PRIMARY KEY(chapter_key,case_id,phase_key)
);
CREATE TABLE IF NOT EXISTS kaiwu_travel_scoped_outcomes(
 chapter_key TEXT NOT NULL REFERENCES chapter_knowledge(chapter_key),
 case_id TEXT NOT NULL REFERENCES cases(case_id),question_key TEXT NOT NULL,
 prior_prediction_line INTEGER,
 initial_prediction_original TEXT,
 book_feedback_line INTEGER NOT NULL,
 book_feedback_original TEXT NOT NULL,
 book_report_scope TEXT NOT NULL,
 originally_retrospective INTEGER NOT NULL DEFAULT 0 CHECK(originally_retrospective IN(0,1)),
 independent_external_verification INTEGER NOT NULL DEFAULT 0 CHECK(independent_external_verification=0),
 PRIMARY KEY(chapter_key,case_id,question_key)
);
CREATE TABLE IF NOT EXISTS kaiwu_travel_source_context_links(
 chapter_key TEXT NOT NULL REFERENCES chapter_knowledge(chapter_key),
 case_id TEXT NOT NULL REFERENCES cases(case_id),
 related_case_id TEXT NOT NULL REFERENCES cases(case_id),
 relation_type TEXT NOT NULL,matching_person_but_distinct_event INTEGER NOT NULL DEFAULT 1
 CHECK(matching_person_but_distinct_event=1),
 new_source_line INTEGER NOT NULL,previous_source_line INTEGER NOT NULL,
 original_line TEXT NOT NULL,metadata_json TEXT NOT NULL CHECK(json_valid(metadata_json)),
 PRIMARY KEY(chapter_key,case_id,related_case_id)
);
CREATE TABLE IF NOT EXISTS kaiwu_travel_missing_cast_mentions(
 chapter_key TEXT NOT NULL REFERENCES chapter_knowledge(chapter_key),
 case_id TEXT NOT NULL REFERENCES cases(case_id),reference_key TEXT NOT NULL,
 source_line INTEGER NOT NULL,original_literal TEXT NOT NULL,
 printed_source_chart_missing INTEGER NOT NULL DEFAULT 1 CHECK(printed_source_chart_missing=1),
 no_fabricated_cast INTEGER NOT NULL DEFAULT 1 CHECK(no_fabricated_cast=1),
 PRIMARY KEY(chapter_key,case_id,reference_key)
);
CREATE VIEW IF NOT EXISTS unified_travel_abroad_cases_across_books AS
 SELECT c.case_id,c.event_family_id,c.domain_id,s.book_id,s.section_key,
 c.known_before,c.author_judgment,c.later_feedback
 FROM cases c JOIN sections s ON c.section_id=s.section_id
 WHERE c.domain_id='travel_abroad';
