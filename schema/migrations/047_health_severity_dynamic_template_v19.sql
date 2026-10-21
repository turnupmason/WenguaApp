-- 047: health/severity deterministic slot-fill protocol. Existing source rows unchanged.
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS health_severity_v19_protocol (
 protocol_id TEXT PRIMARY KEY,
 domain TEXT NOT NULL CHECK(domain='health'),
 intent TEXT NOT NULL CHECK(intent='severity'),
 version TEXT NOT NULL,
 parent_full_archive_sha256 TEXT NOT NULL CHECK(length(parent_full_archive_sha256)=64),
 template_sha256 TEXT NOT NULL CHECK(length(template_sha256)=64),
 sections_count INTEGER NOT NULL CHECK(sections_count=21),
 medical_diagnosis_prohibited INTEGER NOT NULL CHECK(medical_diagnosis_prohibited=1),
 status TEXT NOT NULL CHECK(status='draft_research_not_clinical'),
 note TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS health_severity_v19_template_sections (
 protocol_id TEXT NOT NULL REFERENCES health_severity_v19_protocol(protocol_id),
 section_id TEXT NOT NULL,
 section_order INTEGER NOT NULL CHECK(section_order BETWEEN 1 AND 21),
 title TEXT NOT NULL,
 format_text TEXT NOT NULL,
 source_links_json TEXT NOT NULL CHECK(json_valid(source_links_json)),
 no_historical_answers_in_initial_input INTEGER NOT NULL CHECK(no_historical_answers_in_initial_input=1),
 PRIMARY KEY(protocol_id,section_id),
 UNIQUE(protocol_id,section_order)
);
CREATE TABLE IF NOT EXISTS health_severity_v19_archive_audit (
 version TEXT PRIMARY KEY,
 parent_full_archive_sha256 TEXT NOT NULL CHECK(length(parent_full_archive_sha256)=64),
 historical_cases INTEGER NOT NULL CHECK(historical_cases=194),
 historical_sections INTEGER NOT NULL CHECK(historical_sections=43),
 original_v16_misses INTEGER NOT NULL CHECK(original_v16_misses=2),
 retained_v17_condition_rules INTEGER NOT NULL CHECK(retained_v17_condition_rules=27),
 detailed_severity_sections INTEGER NOT NULL CHECK(detailed_severity_sections=21),
 all_old_rows_unchanged INTEGER NOT NULL CHECK(all_old_rows_unchanged=1),
 newly_validated_real_patient_prognoses INTEGER NOT NULL CHECK(newly_validated_real_patient_prognoses=0)
);
