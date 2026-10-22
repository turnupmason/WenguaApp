-- 052: V2.4 corrected father use and grouped complete traditional illness reading.
-- Never replace, truncate, or update original V2.3 archive tables/rows.
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS health_v24_corrected_father_prose (
    template_key TEXT PRIMARY KEY,
    template_text TEXT NOT NULL,
    deterministic_no_llm INTEGER NOT NULL CHECK(deterministic_no_llm=1),
    role_source_is_actual_year_stem INTEGER NOT NULL CHECK(role_source_is_actual_year_stem=1),
    qian6_auxiliary_required INTEGER NOT NULL CHECK(qian6_auxiliary_required=1)
);
CREATE TABLE IF NOT EXISTS health_v24_acceptance_audit (
    version TEXT PRIMARY KEY,
    parent_full_sha256 TEXT NOT NULL CHECK(length(parent_full_sha256)=64),
    historical_cases INTEGER NOT NULL CHECK(historical_cases=194),
    historical_sections INTEGER NOT NULL CHECK(historical_sections=43),
    old_wrong_development_cases INTEGER NOT NULL CHECK(old_wrong_development_cases=2),
    old_source_facets INTEGER NOT NULL CHECK(old_source_facets=21),
    merged_user_paragraphs INTEGER NOT NULL CHECK(merged_user_paragraphs=16),
    old_other_unreviewed_intents INTEGER NOT NULL CHECK(old_other_unreviewed_intents=4),
    no_gpt_or_network INTEGER NOT NULL CHECK(no_gpt_or_network=1),
    real_medical_accuracy_verified INTEGER NOT NULL CHECK(real_medical_accuracy_verified=0),
    previous_rows_unchanged INTEGER NOT NULL CHECK(previous_rows_unchanged=1),
    user_acceptance TEXT NOT NULL CHECK(user_acceptance='pending')
);
