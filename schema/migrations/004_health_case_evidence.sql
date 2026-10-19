-- Preserve the 6 complete source transcriptions as indivisible event families.
-- Raw nine-palace *tokens* are the user's transcription, not algorithm output;
-- all original quoted words stay in private local SQLite, not public GitHub.
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS historical_chart_cells (
    case_id TEXT NOT NULL REFERENCES cases(case_id),
    palace INTEGER NOT NULL CHECK(palace BETWEEN 1 AND 9),
    source_line INTEGER NOT NULL CHECK(source_line>0),
    palace_label_raw TEXT NOT NULL,
    deity_raw TEXT NOT NULL,
    door_position_raw TEXT NOT NULL,
    star_position_raw TEXT NOT NULL,
    source_status TEXT NOT NULL DEFAULT 'source_transcription_not_independently_cast',
    PRIMARY KEY(case_id,palace),
    UNIQUE(case_id,source_line)
);
CREATE INDEX IF NOT EXISTS idx_historical_chart_palace ON historical_chart_cells(palace);

CREATE TABLE IF NOT EXISTS historical_case_reasoning (
    case_id TEXT NOT NULL REFERENCES cases(case_id),
    step_number INTEGER NOT NULL CHECK(step_number>0),
    source_line INTEGER NOT NULL CHECK(source_line>0),
    author_analysis_original TEXT NOT NULL,
    short_method_topic TEXT NOT NULL,
    metadata_json TEXT NOT NULL CHECK(json_valid(metadata_json)),
    draft_status TEXT NOT NULL DEFAULT 'source_transcription_draft',
    PRIMARY KEY(case_id,step_number),
    UNIQUE(case_id,source_line)
);

CREATE TABLE IF NOT EXISTS historical_case_disclosures (
    case_id TEXT NOT NULL REFERENCES cases(case_id),
    source_line INTEGER NOT NULL CHECK(source_line>0),
    phase TEXT NOT NULL,
    fact_type TEXT NOT NULL,
    original_statement TEXT NOT NULL,
    PRIMARY KEY(case_id,source_line)
);

CREATE TABLE IF NOT EXISTS historical_case_protocol (
    case_id TEXT PRIMARY KEY REFERENCES cases(case_id),
    completeness TEXT NOT NULL,
    published_chart_verification TEXT NOT NULL,
    feedback_independently_verified INTEGER NOT NULL DEFAULT 0 CHECK(feedback_independently_verified IN(0,1)),
    eligible_blind_test INTEGER NOT NULL DEFAULT 0 CHECK(eligible_blind_test IN(0,1)),
    case_source_sha256 TEXT NOT NULL CHECK(length(case_source_sha256)=64),
    metadata_json TEXT NOT NULL CHECK(json_valid(metadata_json))
);
