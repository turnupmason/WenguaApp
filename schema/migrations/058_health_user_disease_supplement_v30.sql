-- 058: V3.0 user-confirmed supplemental illness method, append-only after V2.9.
-- Archive source readouts as immutable and distinguish indexed rules from executed ones.
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS health_v30_method_curriculum (
  method_key TEXT PRIMARY KEY,
  content TEXT NOT NULL,
  origin TEXT NOT NULL CHECK(origin='user_supplied_2026_10_22'),
  verification_state TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS health_v30_stem_pair_rules (
  rule_id TEXT PRIMARY KEY,
  heaven_stem TEXT NOT NULL, earth_stem TEXT NOT NULL,
  traditional_name TEXT NOT NULL, role_mode TEXT NOT NULL,
  traditional_reading TEXT NOT NULL,
  source_status TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS health_v30_composite_rule_index(
  composite_rule_id TEXT PRIMARY KEY,name TEXT NOT NULL,
  required_conditions TEXT NOT NULL,
  traditional_reading TEXT NOT NULL,
  executable_status TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS health_v30_fixed_template (
  section_id TEXT PRIMARY KEY,
  ordinal INTEGER NOT NULL UNIQUE,
  title TEXT NOT NULL, format_text TEXT NOT NULL,
  no_gpt_runtime INTEGER NOT NULL CHECK(no_gpt_runtime=1)
);
CREATE TABLE IF NOT EXISTS health_v30_historical_readout_seals(
  case_id TEXT PRIMARY KEY,
  readout_sha256 TEXT NOT NULL CHECK(length(readout_sha256)=64),
  old_v27_sha256 TEXT NOT NULL CHECK(length(old_v27_sha256)=64),
  author_outcome_used INTEGER NOT NULL CHECK(author_outcome_used=0),
  previously_approved_only_v27_case_2 INTEGER NOT NULL,
  v30_user_approved INTEGER NOT NULL CHECK(v30_user_approved=0)
);
CREATE TABLE IF NOT EXISTS health_v30_version_receipt(
  version TEXT PRIMARY KEY,
  parent_full_sha256 TEXT NOT NULL CHECK(length(parent_full_sha256)=64),
  event_families INTEGER NOT NULL CHECK(event_families=194),
  old_source_sections INTEGER NOT NULL CHECK(old_source_sections=43),
  old_failed_dev_cases INTEGER NOT NULL CHECK(old_failed_dev_cases=2),
  unreviewed_other_health_domains INTEGER NOT NULL CHECK(unreviewed_other_health_domains=4),
  imported_pairs INTEGER NOT NULL CHECK(imported_pairs>=35),
  no_real_medical_outcome_proof INTEGER NOT NULL CHECK(no_real_medical_outcome_proof=1),
  old_rows_preserved INTEGER NOT NULL CHECK(old_rows_preserved=1),
  user_acceptance TEXT NOT NULL CHECK(user_acceptance='pending')
);
