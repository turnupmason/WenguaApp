-- Kaiwu Chapter 3: pedagogical source figures, NOT independently witnessed predictions.
-- Separate source-level demonstrator cast cells from historical_case_* tables.
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS kaiwu_didactic_figures (
 chapter_key TEXT NOT NULL REFERENCES chapter_knowledge(chapter_key),
 figure_key TEXT NOT NULL,
 source_caption_line INTEGER NOT NULL CHECK(source_caption_line > 0),
 source_end_line INTEGER NOT NULL CHECK(source_end_line >= source_caption_line),
 caption_original TEXT NOT NULL,
 source_figure_sha256 TEXT NOT NULL CHECK(length(source_figure_sha256)=64),
 pedagogical_stage TEXT NOT NULL,
 example_key TEXT,
 actual_historical_prediction INTEGER NOT NULL DEFAULT 0 CHECK(actual_historical_prediction=0),
 verified_against_research_engine INTEGER NOT NULL DEFAULT 0 CHECK(verified_against_research_engine IN (0,1)),
 verification_scope TEXT NOT NULL DEFAULT 'source_text_layout_not_calendar_or_outcome_validation',
 metadata_json TEXT NOT NULL CHECK(json_valid(metadata_json)),
 PRIMARY KEY(chapter_key,figure_key)
);
CREATE TABLE IF NOT EXISTS kaiwu_didactic_figure_cells (
 chapter_key TEXT NOT NULL,
 figure_key TEXT NOT NULL,
 palace INTEGER NOT NULL CHECK(palace BETWEEN 1 AND 9),
 source_start_line INTEGER NOT NULL CHECK(source_start_line > 0),
 source_end_line INTEGER NOT NULL CHECK(source_end_line >= source_start_line),
 palace_label_raw TEXT NOT NULL,
 original_cell_text TEXT NOT NULL,
 original_cell_sha256 TEXT NOT NULL CHECK(length(original_cell_sha256)=64),
 is_center_palace INTEGER NOT NULL CHECK(is_center_palace IN (0,1)),
 original_center_has_no_independent_door INTEGER NOT NULL CHECK(original_center_has_no_independent_door IN (0,1)),
 normalized_guess_for_missing_parts INTEGER NOT NULL DEFAULT 0 CHECK(normalized_guess_for_missing_parts=0),
 PRIMARY KEY(chapter_key,figure_key,palace),
 FOREIGN KEY(chapter_key,figure_key) REFERENCES kaiwu_didactic_figures(chapter_key,figure_key)
);
CREATE INDEX IF NOT EXISTS idx_kaiwu_didactic_figure_by_example
 ON kaiwu_didactic_figures(example_key,pedagogical_stage);
CREATE INDEX IF NOT EXISTS idx_kaiwu_didactic_cell_palace
 ON kaiwu_didactic_figure_cells(palace,chapter_key);
