-- 050: fixed 21-paragraph offline user prose; never overwrite old source/template rows.
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS health_v22_customer_severity_sections (
  ordinal INTEGER PRIMARY KEY CHECK(ordinal BETWEEN 1 AND 21),
  section_id TEXT NOT NULL UNIQUE,
  heading TEXT NOT NULL,
  template_text TEXT NOT NULL,
  deterministic_python_only INTEGER NOT NULL CHECK(deterministic_python_only=1),
  customer_language_no_engine_explanation INTEGER NOT NULL CHECK(customer_language_no_engine_explanation=1),
  distinct_from_internal_audit INTEGER NOT NULL CHECK(distinct_from_internal_audit=1)
);
CREATE TABLE IF NOT EXISTS health_v22_source_pair_explanations (
  source_pair_id TEXT PRIMARY KEY,
  source_line INTEGER NOT NULL,
  original_excerpt TEXT NOT NULL,
  traditional_formation_name TEXT NOT NULL,
  context TEXT NOT NULL,
  is_clinical_diagnosis INTEGER NOT NULL CHECK(is_clinical_diagnosis=0)
);
CREATE TABLE IF NOT EXISTS health_v22_acceptance_receipt (
  receipt_id TEXT PRIMARY KEY,
  parent_sha256 TEXT NOT NULL CHECK(length(parent_sha256)=64),
  previous_original_case_count INTEGER NOT NULL CHECK(previous_original_case_count=194),
  previous_original_section_count INTEGER NOT NULL CHECK(previous_original_section_count=43),
  previous_v16_dev_wrong_count INTEGER NOT NULL CHECK(previous_v16_dev_wrong_count=2),
  previous_health_v20_patient_roles INTEGER NOT NULL CHECK(previous_health_v20_patient_roles=14),
  previous_unapproved_other_health_templates INTEGER NOT NULL CHECK(previous_unapproved_other_health_templates=4),
  previous_v20_draft_template_sections INTEGER NOT NULL CHECK(previous_v20_draft_template_sections=66),
  new_user_approved_sections INTEGER NOT NULL CHECK(new_user_approved_sections=21),
  current_user_acceptance TEXT NOT NULL CHECK(current_user_acceptance='pending'),
  no_llm_customer_rewrite INTEGER NOT NULL CHECK(no_llm_customer_rewrite=1),
  all_previous_rows_kept INTEGER NOT NULL CHECK(all_previous_rows_kept=1)
);
