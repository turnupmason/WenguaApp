-- New chapter event-time provenance. No changes to old books/cases/charts.
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS historical_case_phase_events (
 case_id TEXT NOT NULL REFERENCES cases(case_id),
 source_start_line INTEGER NOT NULL CHECK(source_start_line > 0),
 source_end_line INTEGER NOT NULL CHECK(source_end_line >= source_start_line),
 phase TEXT NOT NULL CHECK(phase IN ('initial_question','initial_judgment','new_disclosure','continued_judgment','book_feedback','editor_posthoc_correction','retrospective_author_explanation','cast_metadata')),
 original_excerpt TEXT NOT NULL,
 metadata_json TEXT NOT NULL CHECK(json_valid(metadata_json)),
 visible_to_initial_blind_test INTEGER NOT NULL DEFAULT 0 CHECK(visible_to_initial_blind_test IN(0,1)),
 PRIMARY KEY(case_id,source_start_line,phase)
);
CREATE INDEX IF NOT EXISTS idx_case_phase_events ON historical_case_phase_events(case_id,phase);
CREATE TABLE IF NOT EXISTS historical_case_reasoning_corrections (
 case_id TEXT NOT NULL REFERENCES cases(case_id),
 source_line INTEGER NOT NULL CHECK(source_line > 0),
 original_step_number INTEGER,
 correction_kind TEXT NOT NULL,
 corrected_yongshen_policy TEXT NOT NULL,
 original_analysis_is_positive_training INTEGER NOT NULL DEFAULT 0 CHECK(original_analysis_is_positive_training IN(0,1)),
 source_review_status TEXT NOT NULL DEFAULT 'source_documented_needs_professional_review',
 rationale_original TEXT NOT NULL,
 PRIMARY KEY(case_id,source_line)
);
