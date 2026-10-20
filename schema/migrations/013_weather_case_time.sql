-- Weather-source case provenance; records time selection without changing any legacy row.
-- Do not interpret historical Qimen weather remarks as meteorological evidence.
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS historical_weather_cast_context (
 case_id TEXT NOT NULL PRIMARY KEY REFERENCES cases(case_id),
 cast_strategy TEXT NOT NULL,
 question_date TEXT NOT NULL,
 forecast_target_date TEXT NOT NULL,
 printed_cast_line INTEGER NOT NULL CHECK(printed_cast_line>0),
 alternative_techniques_not_printed_json TEXT NOT NULL CHECK(json_valid(alternative_techniques_not_printed_json)),
 metadata_json TEXT NOT NULL CHECK(json_valid(metadata_json)),
 scientific_external_verification INTEGER NOT NULL DEFAULT 0 CHECK(scientific_external_verification IN (0,1))
);
