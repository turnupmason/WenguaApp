-- Kaiwu Fengshui section 14: 1 SAME Shenqi historical question plus 2 NEW family events.
-- OCR panels were flattened; keep exact source line witnesses, do not invent 9 palace cells.
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS kaiwu_geography_source_witnesses(
 witness_key TEXT PRIMARY KEY,
 chapter_key TEXT NOT NULL REFERENCES chapter_knowledge(chapter_key),
 section_id INTEGER NOT NULL REFERENCES sections(section_id),
 case_id TEXT NOT NULL REFERENCES cases(case_id),
 witness_relationship TEXT NOT NULL CHECK(witness_relationship IN('same_shenqi_event_new_explanation','new_geography_event')),
 initial_context_first_line INTEGER NOT NULL,
 source_first_line INTEGER NOT NULL,
 source_last_line INTEGER NOT NULL,
 raw_panel_first_line INTEGER NOT NULL,
 raw_panel_last_line INTEGER NOT NULL,
 raw_panel_source TEXT NOT NULL,
 raw_panel_sha256 TEXT NOT NULL CHECK(length(raw_panel_sha256)=64),
 printed_palace_positions_status TEXT NOT NULL CHECK(printed_palace_positions_status='flattened_OCR_unresolved_no_certified_palaces'),
 metadata_json TEXT NOT NULL CHECK(json_valid(metadata_json))
);
CREATE TABLE IF NOT EXISTS kaiwu_geography_raw_lines(
 witness_key TEXT NOT NULL REFERENCES kaiwu_geography_source_witnesses(witness_key),
 source_line INTEGER NOT NULL CHECK(source_line>0),
 original_line TEXT NOT NULL,
 excerpt_sha256 TEXT NOT NULL CHECK(length(excerpt_sha256)=64),
 palace_position_confident INTEGER NOT NULL DEFAULT 0 CHECK(palace_position_confident=0),
 PRIMARY KEY(witness_key,source_line)
);
CREATE TABLE IF NOT EXISTS kaiwu_geography_author_steps(
 witness_key TEXT NOT NULL REFERENCES kaiwu_geography_source_witnesses(witness_key),
 step_index INTEGER NOT NULL,
 first_line INTEGER NOT NULL,
 last_line INTEGER NOT NULL,
 original_author_text TEXT NOT NULL,
 excerpt_sha256 TEXT NOT NULL CHECK(length(excerpt_sha256)=64),
 evidence_json TEXT NOT NULL CHECK(json_valid(evidence_json)),
 source_stage TEXT NOT NULL,
 positive_training_eligible INTEGER NOT NULL DEFAULT 0 CHECK(positive_training_eligible=0),
 PRIMARY KEY(witness_key,step_index)
);
CREATE TABLE IF NOT EXISTS kaiwu_geography_source_phases(
 witness_key TEXT NOT NULL REFERENCES kaiwu_geography_source_witnesses(witness_key),
 phase_key TEXT NOT NULL,phase_kind TEXT NOT NULL,
 source_start_line INTEGER NOT NULL,source_end_line INTEGER NOT NULL,
 original_text TEXT NOT NULL,excerpt_sha256 TEXT NOT NULL CHECK(length(excerpt_sha256)=64),
 metadata_json TEXT NOT NULL CHECK(json_valid(metadata_json)),
 PRIMARY KEY(witness_key,phase_key)
);
CREATE TABLE IF NOT EXISTS kaiwu_geography_method_candidates(
 chapter_key TEXT NOT NULL REFERENCES chapter_knowledge(chapter_key),
 method_key TEXT NOT NULL,
 source_first_line INTEGER NOT NULL,
 source_last_line INTEGER NOT NULL,
 domain_track TEXT NOT NULL,
 conditions_json TEXT NOT NULL CHECK(json_valid(conditions_json)),
 conclusion_scope TEXT NOT NULL,
 original_source TEXT NOT NULL,
 evidence_limitations_json TEXT NOT NULL CHECK(json_valid(evidence_limitations_json)),
 review_status TEXT NOT NULL DEFAULT 'draft' CHECK(review_status='draft'),
 positive_training_eligible INTEGER NOT NULL DEFAULT 0 CHECK(positive_training_eligible=0),
 PRIMARY KEY(chapter_key,method_key)
);
CREATE VIEW IF NOT EXISTS unified_geography_cases_across_books AS
 SELECT c.case_id,c.event_family_id,c.domain_id,s.book_id,s.section_key,
 c.known_before,c.author_yongshen_steps,c.author_judgment,c.later_feedback
 FROM cases c JOIN sections s ON s.section_id=c.section_id
 WHERE c.domain_id='geography_environment_historical_source';
