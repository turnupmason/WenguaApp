-- V3.5 append-only patient-first interpretation of complete 194 historical source family DB.
PRAGMA foreign_keys=ON;
CREATE TABLE health_v35_patient_first_replay (
    event_family_id TEXT PRIMARY KEY,
    actual_source_day TEXT NOT NULL,
    actual_source_hour TEXT NOT NULL,
    original_author_outcome_was_used INTEGER NOT NULL CHECK(original_author_outcome_was_used=0),
    readout_sha256 TEXT NOT NULL CHECK(length(readout_sha256)=64),
    prior_v34_traditional_verdict TEXT NOT NULL CHECK(prior_v34_traditional_verdict IN ('病吉','病凶')),
    revised_v35_traditional_verdict TEXT NOT NULL CHECK(revised_v35_traditional_verdict IN ('病吉','病凶')),
    real_double_control INTEGER NOT NULL CHECK(real_double_control IN(0,1)),
    patient_void_limits_control INTEGER NOT NULL CHECK(patient_void_limits_control IN(0,1)),
    natal_year_qualified_by_source INTEGER NOT NULL CHECK(natal_year_qualified_by_source IN(0,1)),
    medical_co_palace_not_vetoed_by_weakness INTEGER NOT NULL CHECK(medical_co_palace_not_vetoed_by_weakness=1),
    user_review TEXT NOT NULL CHECK(user_review='pending')
);
CREATE TABLE health_v35_complete_parent_archive (
    version TEXT PRIMARY KEY,
    exact_v34_parent_sha256 TEXT NOT NULL CHECK(length(exact_v34_parent_sha256)=64),
    originals_kept INTEGER NOT NULL CHECK(originals_kept=194),
    original_sections_kept INTEGER NOT NULL CHECK(original_sections_kept=43),
    old_failed_development_predictions_retained INTEGER NOT NULL CHECK(old_failed_development_predictions_retained=2),
    previous_12_v33_and_v34_records_immutable INTEGER NOT NULL CHECK(previous_12_v33_and_v34_records_immutable=1),
    user_rule_catalog_pairs INTEGER NOT NULL CHECK(user_rule_catalog_pairs=42),
    user_rule_catalog_composites INTEGER NOT NULL CHECK(user_rule_catalog_composites=17),
    incomplete_rule_definitions_still_explicit INTEGER NOT NULL CHECK(incomplete_rule_definitions_still_explicit=1),
    no_clinical_prognosis INTEGER NOT NULL CHECK(no_clinical_prognosis=1),
    ui_approval TEXT NOT NULL CHECK(ui_approval='pending')
);
