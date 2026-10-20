-- Military literary study only: store four actual printed boards across two whole families.
-- Do not synthesize board numbers or treat retrospectively known WW2 history as blind prediction.
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS historical_military_cast_protocol (
 case_id TEXT NOT NULL REFERENCES cases(case_id),
 cast_key TEXT NOT NULL,
 cast_date TEXT NOT NULL,
 hour_ganzhi TEXT NOT NULL,
 source_chart_line INTEGER NOT NULL CHECK(source_chart_line>0),
 event_phase TEXT NOT NULL,
 source_initial_lines_json TEXT NOT NULL CHECK(json_valid(source_initial_lines_json)),
 original_analysis_lines_json TEXT NOT NULL CHECK(json_valid(original_analysis_lines_json)),
 is_retrospective INTEGER NOT NULL DEFAULT 0 CHECK(is_retrospective IN(0,1)),
 is_prospective_blind_test_approved INTEGER NOT NULL DEFAULT 0 CHECK(is_prospective_blind_test_approved IN(0,1)),
 PRIMARY KEY(case_id,cast_key)
);
CREATE TABLE IF NOT EXISTS historical_military_source_caveat (
 case_id TEXT NOT NULL REFERENCES cases(case_id),
 source_line INTEGER NOT NULL CHECK(source_line>0),
 caveat_kind TEXT NOT NULL,
 source_literal TEXT NOT NULL,
 review_status TEXT NOT NULL,
 note TEXT NOT NULL,
 PRIMARY KEY(case_id,source_line,caveat_kind)
);
