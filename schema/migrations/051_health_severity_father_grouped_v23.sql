-- 051: V2.3 group six same-palace source sections, father relation-specific use.
-- Append-only over exact V2.2 complete SQLite. No original row modifications.
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS health_v23_display_groups (
  group_id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  source_sections_json TEXT NOT NULL CHECK(json_valid(source_sections_json)),
  group_format TEXT NOT NULL,
  merge_without_dropping_source INTEGER NOT NULL CHECK(merge_without_dropping_source=1),
  deterministic_no_llm INTEGER NOT NULL CHECK(deterministic_no_llm=1),
  user_review_status TEXT NOT NULL CHECK(user_review_status='pending')
);
CREATE TABLE IF NOT EXISTS health_v23_role_auxiliary (
  role_id TEXT PRIMARY KEY,
  auxiliary_palace INTEGER NOT NULL CHECK(auxiliary_palace BETWEEN 1 AND 9),
  detailed_text TEXT NOT NULL,
  evidence_text TEXT NOT NULL,
  summary_text TEXT NOT NULL,
  requires_patient_birth_year INTEGER NOT NULL CHECK(requires_patient_birth_year=0)
);
CREATE TABLE IF NOT EXISTS health_v23_acceptance_audit (
  audit_id TEXT PRIMARY KEY,
  parent_exact_sha256 TEXT NOT NULL CHECK(length(parent_exact_sha256)=64),
  historical_cases INTEGER NOT NULL CHECK(historical_cases=194),
  historical_sections INTEGER NOT NULL CHECK(historical_sections=43),
  old_wrong_development_cases INTEGER NOT NULL CHECK(old_wrong_development_cases=2),
  parent_customer_sections INTEGER NOT NULL CHECK(parent_customer_sections=21),
  merged_source_sections INTEGER NOT NULL CHECK(merged_source_sections=6),
  presented_sections INTEGER NOT NULL CHECK(presented_sections=16),
  other_four_intents_still_unapproved INTEGER NOT NULL CHECK(other_four_intents_still_unapproved=4),
  real_patient_birth_year_inferred INTEGER NOT NULL CHECK(real_patient_birth_year_inferred=0),
  old_tables_preserved INTEGER NOT NULL CHECK(old_tables_preserved=1),
  actual_medical_accuracy_verified INTEGER NOT NULL CHECK(actual_medical_accuracy_verified=0),
  user_acceptance TEXT NOT NULL CHECK(user_acceptance='pending')
);
