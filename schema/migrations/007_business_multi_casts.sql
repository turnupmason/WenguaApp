-- Additive record of multiple actual hour-specific charts within ONE historical event family.
-- Case12 in business book shows 3 distinct casts for a single 4-day drawing event.
-- Main historical_chart_cells retains first chart. This holds subsequent complete casts.
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS historical_case_additional_casts (
 case_id TEXT NOT NULL REFERENCES cases(case_id),
 cast_key TEXT NOT NULL,
 cast_datetime_description TEXT NOT NULL,
 calendar_date TEXT NOT NULL,
 hour_ganzhi TEXT NOT NULL,
 source_chart_start INTEGER NOT NULL CHECK(source_chart_start > 0),
 notes TEXT NOT NULL,
 PRIMARY KEY(case_id,cast_key)
);
CREATE TABLE IF NOT EXISTS historical_case_additional_cast_cells (
 case_id TEXT NOT NULL,
 cast_key TEXT NOT NULL,
 palace INTEGER NOT NULL CHECK(palace BETWEEN 1 AND 9),
 source_line INTEGER NOT NULL CHECK(source_line>0),
 palace_label_raw TEXT NOT NULL,
 deity_raw TEXT NOT NULL,
 door_position_raw TEXT NOT NULL,
 star_position_raw TEXT NOT NULL,
 PRIMARY KEY(case_id,cast_key,palace),
 UNIQUE(case_id,cast_key,source_line),
 FOREIGN KEY(case_id,cast_key) REFERENCES historical_case_additional_casts(case_id,cast_key)
);
