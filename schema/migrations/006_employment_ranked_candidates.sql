-- Additive fifth topic: one-event multi-candidate ranking and separate editorial/source notes.
-- Never recast missing historical charts or split the five competitors into five cases.
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS historical_case_source_segments (
    case_id TEXT NOT NULL REFERENCES cases(case_id),
    segment_kind TEXT NOT NULL,
    source_start_line INTEGER NOT NULL CHECK(source_start_line > 0),
    source_end_line INTEGER NOT NULL CHECK(source_end_line >= source_start_line),
    original_text TEXT NOT NULL,
    metadata_json TEXT NOT NULL CHECK(json_valid(metadata_json)),
    PRIMARY KEY (case_id, segment_kind, source_start_line)
);
CREATE TABLE IF NOT EXISTS historical_event_candidates (
    case_id TEXT NOT NULL REFERENCES cases(case_id),
    candidate_key TEXT NOT NULL,
    candidate_name_private TEXT NOT NULL,
    assigned_palace INTEGER NOT NULL CHECK(assigned_palace BETWEEN 1 AND 9),
    assignment_source_line INTEGER NOT NULL CHECK(assignment_source_line>0),
    analysis_source_line INTEGER NOT NULL CHECK(analysis_source_line>0),
    predicted_rank INTEGER CHECK(predicted_rank IS NULL OR predicted_rank>0),
    book_reported_rank INTEGER CHECK(book_reported_rank IS NULL OR book_reported_rank>0),
    metadata_json TEXT NOT NULL CHECK(json_valid(metadata_json)),
    PRIMARY KEY (case_id,candidate_key),
    UNIQUE (case_id,assigned_palace)
);
