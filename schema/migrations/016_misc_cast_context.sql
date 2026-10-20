-- Additive source-specific event and cast chronology. Never modify old source rows.
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS historical_misc_cast_context (
 case_id TEXT NOT NULL REFERENCES cases(case_id),
 cast_key TEXT NOT NULL,
 source_chart_line INTEGER NOT NULL CHECK(source_chart_line>0),
 case_phase TEXT NOT NULL,
 original_question_and_method TEXT NOT NULL,
 retrospective_qimen_provenance_unverified INTEGER NOT NULL DEFAULT 0 CHECK(retrospective_qimen_provenance_unverified IN (0,1)),
 additional_non_qimen_casts_count INTEGER NOT NULL DEFAULT 0 CHECK(additional_non_qimen_casts_count>=0),
 metadata_json TEXT NOT NULL CHECK(json_valid(metadata_json)),
 PRIMARY KEY(case_id,cast_key)
);
