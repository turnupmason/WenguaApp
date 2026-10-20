-- Adds context without rewriting any original chart or previously archived case.
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS historical_sports_cast_qualification (
 case_id TEXT NOT NULL REFERENCES cases(case_id),
 source_line INTEGER NOT NULL CHECK(source_line>0),
 kind TEXT NOT NULL,
 original_text TEXT NOT NULL,
 metadata_json TEXT NOT NULL CHECK(json_valid(metadata_json)),
 PRIMARY KEY(case_id,source_line,kind)
);
CREATE TABLE IF NOT EXISTS historical_source_literal_anomalies (
 case_id TEXT NOT NULL REFERENCES cases(case_id),
 source_line INTEGER NOT NULL CHECK(source_line>0),
 palace INTEGER NOT NULL CHECK(palace BETWEEN 1 AND 9),
 source_literal TEXT NOT NULL,
 possible_variant TEXT,
 interpretation_status TEXT NOT NULL,
 original_retained INTEGER NOT NULL DEFAULT 1 CHECK(original_retained IN(0,1)),
 PRIMARY KEY(case_id,source_line,palace)
);
