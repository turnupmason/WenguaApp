-- New ACTIVE score-free health severity V3.9.1, append only from exact
-- complete archive V4.2. Previous numerical studies are history only.
PRAGMA foreign_keys=ON;
CREATE TABLE health_v391_active_narrative_policy (
 version TEXT PRIMARY KEY CHECK(version='v3.9.1'),
 exact_original_full_v42_parent_sha256 TEXT NOT NULL CHECK(length(exact_original_full_v42_parent_sha256)=64),
 original_v39_template_unchanged INTEGER NOT NULL CHECK(original_v39_template_unchanged=1),
 original_v39_logic_unchanged INTEGER NOT NULL CHECK(original_v39_logic_unchanged=1),
 score_engine_disabled INTEGER NOT NULL CHECK(score_engine_disabled=1),
 original_book_event_families INTEGER NOT NULL CHECK(original_book_event_families=194),
 original_source_chapters INTEGER NOT NULL CHECK(original_source_chapters=43),
 original_ordered_pairs INTEGER NOT NULL CHECK(original_ordered_pairs=81),
 old_user_disease_pairs INTEGER NOT NULL CHECK(old_user_disease_pairs=42),
 old_composites INTEGER NOT NULL CHECK(old_composites=17),
 old_development_failures INTEGER NOT NULL CHECK(old_development_failures=2),
 stage_table_source_anchors_verified INTEGER NOT NULL CHECK(stage_table_source_anchors_verified=120),
 total_random_demo_cases INTEGER NOT NULL CHECK(total_random_demo_cases=4),
 customer_approved INTEGER NOT NULL CHECK(customer_approved=0)
);
CREATE TABLE health_v391_random_hour_narratives (
 sample_id TEXT PRIMARY KEY,
 original_local_date_time TEXT NOT NULL,
 true_year_pillar TEXT NOT NULL,
 true_month_pillar TEXT NOT NULL,
 true_day_pillar TEXT NOT NULL,
 true_hour_pillar TEXT NOT NULL,
 actual_solar_term TEXT NOT NULL,
 person_role TEXT NOT NULL CHECK(person_role='self'),
 patient_palace INTEGER NOT NULL CHECK(patient_palace IN(1,2,3,4,6,7,8,9)),
 tianrui_palace INTEGER NOT NULL CHECK(tianrui_palace IN(1,2,3,4,6,7,8,9)),
 old_v39_reading_sha256 TEXT NOT NULL CHECK(length(old_v39_reading_sha256)=64),
 new_v391_reading_sha256 TEXT NOT NULL CHECK(length(new_v391_reading_sha256)=64),
 real_health_diagnosis_as_input INTEGER NOT NULL CHECK(real_health_diagnosis_as_input=0),
 any_scoring_model_invoked INTEGER NOT NULL CHECK(any_scoring_model_invoked=0),
 approval_status TEXT NOT NULL CHECK(approval_status='pending_user_review')
);
CREATE TABLE health_v391_actual_role_lifecycle (
 sample_id TEXT NOT NULL,
 role TEXT NOT NULL CHECK(role IN('patient','illness','doctor','yi','hour')),
 heavenly_stem TEXT NOT NULL,
 real_palace INTEGER NOT NULL,
 actual_branches_stages_json TEXT NOT NULL,
 source_original_five_anchors_verified INTEGER NOT NULL CHECK(source_original_five_anchors_verified=1),
 PRIMARY KEY(sample_id,role),
 FOREIGN KEY(sample_id) REFERENCES health_v391_random_hour_narratives(sample_id)
);
