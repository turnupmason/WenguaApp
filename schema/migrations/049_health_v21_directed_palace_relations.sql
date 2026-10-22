-- 049: V2.1 fix directed five element wording; never alter V2.0 source tables.
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS health_v21_directed_palace_relations (
  relation_id TEXT PRIMARY KEY CHECK(relation_id IN ('克','受克','生','受生','比和')),
  conditional_meaning TEXT NOT NULL,
  direction_is_strict INTEGER NOT NULL CHECK(direction_is_strict=1),
  parent_evidence_kind TEXT NOT NULL DEFAULT 'actual_palace_five_elements'
);
CREATE TABLE IF NOT EXISTS health_v21_calendar_guard (
  guard_id TEXT PRIMARY KEY,
  valid_year_pillar_required_when_supplied INTEGER NOT NULL CHECK(valid_year_pillar_required_when_supplied=1),
  valid_month_pillar_required_when_supplied INTEGER NOT NULL CHECK(valid_month_pillar_required_when_supplied=1),
  month_branch_consistent_with_month_pillar INTEGER NOT NULL CHECK(month_branch_consistent_with_month_pillar=1),
  hour_pillar_matches_actual_cast INTEGER NOT NULL CHECK(hour_pillar_matches_actual_cast=1),
  no_invented_birth_year INTEGER NOT NULL CHECK(no_invented_birth_year=1),
  no_false_solar_term_certification INTEGER NOT NULL CHECK(no_false_solar_term_certification=1)
);
CREATE TABLE IF NOT EXISTS health_v21_archive_audit (
  version TEXT PRIMARY KEY,
  parent_sqlite_sha256 TEXT NOT NULL CHECK(length(parent_sqlite_sha256)=64),
  old_source_events INTEGER NOT NULL CHECK(old_source_events=194),
  old_source_sections INTEGER NOT NULL CHECK(old_source_sections=43),
  old_v16_incorrect_development_answers INTEGER NOT NULL CHECK(old_v16_incorrect_development_answers=2),
  old_health_role_profiles INTEGER NOT NULL CHECK(old_health_role_profiles=14),
  old_health_intent_templates INTEGER NOT NULL CHECK(old_health_intent_templates=5),
  old_health_template_sections INTEGER NOT NULL CHECK(old_health_template_sections=66),
  old_rows_unchanged INTEGER NOT NULL CHECK(old_rows_unchanged=1),
  actual_clinical_predictive_validations INTEGER NOT NULL CHECK(actual_clinical_predictive_validations=0)
);
