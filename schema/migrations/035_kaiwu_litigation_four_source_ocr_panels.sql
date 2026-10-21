-- Kaiwu litigation ch2 s10, 4 NEW legal question families. Reassembled user-provided
-- OCR grids are transcriptions with uncertainties, NOT certified original printed plates.
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS kaiwu_litigation_source_panels(
 chapter_key TEXT NOT NULL REFERENCES chapter_knowledge(chapter_key),
 case_id TEXT NOT NULL REFERENCES cases(case_id),
 range_start INTEGER NOT NULL,range_end INTEGER NOT NULL,
 original_source_text TEXT NOT NULL,source_sha256 TEXT NOT NULL,
 provenance_class TEXT NOT NULL CHECK(provenance_class='user_transcribed_OCR_reconstruction_uncertainties'),
 certified_original_plate INTEGER NOT NULL DEFAULT 0 CHECK(certified_original_plate=0),
 PRIMARY KEY(chapter_key,case_id)
);
CREATE TABLE IF NOT EXISTS kaiwu_litigation_panel_lines(
 chapter_key TEXT NOT NULL,case_id TEXT NOT NULL,
 source_line INTEGER NOT NULL,original_line TEXT NOT NULL,
 sha256 TEXT NOT NULL,PRIMARY KEY(chapter_key,case_id,source_line),
 FOREIGN KEY(chapter_key,case_id) REFERENCES kaiwu_litigation_source_panels(chapter_key,case_id)
);
CREATE TABLE IF NOT EXISTS kaiwu_litigation_transcribed_palaces(
 chapter_key TEXT NOT NULL,case_id TEXT NOT NULL,palace INTEGER NOT NULL CHECK(palace BETWEEN 1 AND 9),
 deity_literal TEXT NOT NULL,door_literal TEXT NOT NULL,star_literal TEXT NOT NULL,
 printed_layer_line_start INTEGER NOT NULL,source_cell_text TEXT NOT NULL,source_cell_sha256 TEXT NOT NULL,
 provenance_class TEXT NOT NULL CHECK(provenance_class='structured_from_uncertain_user_transcription_not_verified_original_plate'),
 source_uncertainty INTEGER NOT NULL DEFAULT 1 CHECK(source_uncertainty=1),
 center_unprinted_deity_door_star INTEGER NOT NULL CHECK(center_unprinted_deity_door_star IN(0,1)),
 PRIMARY KEY(chapter_key,case_id,palace),
 FOREIGN KEY(chapter_key,case_id) REFERENCES kaiwu_litigation_source_panels(chapter_key,case_id)
);
CREATE TABLE IF NOT EXISTS kaiwu_litigation_source_phases(
 chapter_key TEXT NOT NULL REFERENCES chapter_knowledge(chapter_key),
 case_id TEXT NOT NULL REFERENCES cases(case_id),phase_key TEXT NOT NULL,
 phase_type TEXT NOT NULL,first_line INTEGER NOT NULL,last_line INTEGER NOT NULL,
 source_original TEXT NOT NULL,excerpt_sha256 TEXT NOT NULL,
 metadata_json TEXT NOT NULL CHECK(json_valid(metadata_json)),
 PRIMARY KEY(chapter_key,case_id,phase_key)
);
CREATE TABLE IF NOT EXISTS kaiwu_litigation_author_steps(
 chapter_key TEXT NOT NULL REFERENCES chapter_knowledge(chapter_key),
 case_id TEXT NOT NULL REFERENCES cases(case_id),
 step_number INTEGER NOT NULL,speaker TEXT NOT NULL,
 first_line INTEGER NOT NULL,last_line INTEGER NOT NULL,
 original_text TEXT NOT NULL,excerpt_sha256 TEXT NOT NULL,
 reasoning_json TEXT NOT NULL CHECK(json_valid(reasoning_json)),
 review_status TEXT NOT NULL DEFAULT 'draft' CHECK(review_status='draft'),
 positive_training_eligible INTEGER NOT NULL DEFAULT 0 CHECK(positive_training_eligible=0),
 PRIMARY KEY(chapter_key,case_id,step_number)
);
CREATE TABLE IF NOT EXISTS kaiwu_litigation_source_timing_criticisms(
 chapter_key TEXT NOT NULL REFERENCES chapter_knowledge(chapter_key),
 case_id TEXT NOT NULL REFERENCES cases(case_id),
 critic_line INTEGER NOT NULL,
 original_author_method_lines_json TEXT NOT NULL CHECK(json_valid(original_author_method_lines_json)),
 teacher_original_text TEXT NOT NULL,source_sha256 TEXT NOT NULL,
 scope TEXT NOT NULL,initial_source_not_overwritten INTEGER NOT NULL DEFAULT 1 CHECK(initial_source_not_overwritten=1),
 PRIMARY KEY(chapter_key,case_id,critic_line)
);
CREATE TABLE IF NOT EXISTS kaiwu_litigation_source_claim_conflicts(
 chapter_key TEXT NOT NULL REFERENCES chapter_knowledge(chapter_key),
 case_id TEXT NOT NULL REFERENCES cases(case_id),
 conflict_key TEXT NOT NULL,source_line_one INTEGER NOT NULL,source_line_two INTEGER NOT NULL,
 claim_one TEXT NOT NULL,claim_two TEXT NOT NULL,
 conflict_kind TEXT NOT NULL,reconciled_as_original_fact INTEGER NOT NULL DEFAULT 0 CHECK(reconciled_as_original_fact=0),
 PRIMARY KEY(chapter_key,case_id,conflict_key)
);
CREATE TABLE IF NOT EXISTS kaiwu_litigation_conditional_methods(
 chapter_key TEXT NOT NULL REFERENCES chapter_knowledge(chapter_key),
 method_key TEXT NOT NULL,
 source_line INTEGER NOT NULL,source_case_id TEXT NOT NULL REFERENCES cases(case_id),
 source_original TEXT NOT NULL,conditions_json TEXT NOT NULL CHECK(json_valid(conditions_json)),
 reasoning_summary TEXT NOT NULL,critical_limits_json TEXT NOT NULL CHECK(json_valid(critical_limits_json)),
 review_status TEXT NOT NULL DEFAULT 'draft' CHECK(review_status='draft'),
 positive_training_eligible INTEGER NOT NULL DEFAULT 0 CHECK(positive_training_eligible=0),
 PRIMARY KEY(chapter_key,method_key)
);
CREATE VIEW IF NOT EXISTS unified_litigation_cases_across_books AS
 SELECT c.case_id,c.event_family_id,s.book_id,s.section_key,c.domain_id,
 c.known_before,c.author_yongshen_steps,c.author_judgment,c.later_feedback
 FROM cases c JOIN sections s ON c.section_id=s.section_id WHERE c.domain_id='litigation';
