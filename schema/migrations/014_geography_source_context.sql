-- Traditional geographic-environment source provenance; old source rows immutable.
-- The author's unarticulated causal steps are NOT invented by the importer.
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS historical_geography_source_context (
 case_id TEXT PRIMARY KEY NOT NULL REFERENCES cases(case_id),
 source_chart_line INTEGER NOT NULL CHECK(source_chart_line>0),
 cast_calendar_date TEXT NOT NULL,
 cast_hour_ganzhi TEXT NOT NULL,
 comparison_preknown INTEGER NOT NULL DEFAULT 0 CHECK(comparison_preknown IN(0,1)),
 other_subquestion_without_chart INTEGER NOT NULL DEFAULT 0 CHECK(other_subquestion_without_chart IN(0,1)),
 author_causal_steps_available INTEGER NOT NULL DEFAULT 0 CHECK(author_causal_steps_available IN(0,1)),
 missing_causal_reason_warning TEXT NOT NULL,
 metadata_json TEXT NOT NULL CHECK(json_valid(metadata_json))
);
