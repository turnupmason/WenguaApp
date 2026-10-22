-- 048: role-specific five health intents; do not mutate any V1.9 source rows.
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS health_v20_actor_role_profiles (
  profile_id TEXT PRIMARY KEY,
  label TEXT NOT NULL,
  profile_json TEXT NOT NULL CHECK(json_valid(profile_json)),
  reference_count INTEGER NOT NULL CHECK(reference_count BETWEEN 0 AND 4),
  selection_context_required INTEGER NOT NULL DEFAULT 1 CHECK(selection_context_required=1),
  birth_year_optional INTEGER NOT NULL DEFAULT 1 CHECK(birth_year_optional=1),
  no_medical_prediction INTEGER NOT NULL DEFAULT 1 CHECK(no_medical_prediction=1)
);
CREATE TABLE IF NOT EXISTS health_v20_intent_templates (
  intent TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  template_hash_sha256 TEXT NOT NULL CHECK(length(template_hash_sha256)=64),
  template_json TEXT NOT NULL CHECK(json_valid(template_json)),
  sections_count INTEGER NOT NULL CHECK(sections_count BETWEEN 10 AND 21),
  author_method_different_from_severity INTEGER NOT NULL CHECK(author_method_different_from_severity IN (0,1)),
  user_reading_says_source_book_names INTEGER NOT NULL DEFAULT 0 CHECK(user_reading_says_source_book_names=0),
  medically_validated INTEGER NOT NULL DEFAULT 0 CHECK(medically_validated=0)
);
CREATE TABLE IF NOT EXISTS health_v20_intent_steps (
  intent TEXT NOT NULL REFERENCES health_v20_intent_templates(intent),
  ordinal INTEGER NOT NULL,
  section_id TEXT NOT NULL,
  title TEXT NOT NULL,
  template_text TEXT NOT NULL,
  all_required_roles_dynamically_bound INTEGER NOT NULL DEFAULT 1 CHECK(all_required_roles_dynamically_bound=1),
  PRIMARY KEY(intent, ordinal), UNIQUE(intent,section_id)
);
CREATE TABLE IF NOT EXISTS health_v20_archive_audit (
  audit_id TEXT PRIMARY KEY,
  parent_full_archive_sha256 TEXT NOT NULL CHECK(length(parent_full_archive_sha256)=64),
  source_event_families INTEGER NOT NULL CHECK(source_event_families=194),
  source_sections INTEGER NOT NULL CHECK(source_sections=43),
  previous_dev_misses INTEGER NOT NULL CHECK(previous_dev_misses=2),
  previous_conditional_rules INTEGER NOT NULL CHECK(previous_conditional_rules=27),
  older_health_v19_template_rows INTEGER NOT NULL CHECK(older_health_v19_template_rows=21),
  source_old_rows_unchanged INTEGER NOT NULL CHECK(source_old_rows_unchanged=1),
  independent_clinical_accuracy_estimate INTEGER NOT NULL CHECK(independent_clinical_accuracy_estimate=0)
);
