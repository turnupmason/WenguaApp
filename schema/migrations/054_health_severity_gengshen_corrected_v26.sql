-- 054: V2.6 corrected Gengshen self-test after V2.5 failure; append only.
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS health_v26_source_grounded_language (
  section_order INTEGER PRIMARY KEY CHECK(section_order BETWEEN 1 AND 11),
  section_id TEXT NOT NULL UNIQUE,
  title TEXT NOT NULL,
  template_text TEXT NOT NULL,
  optional_context TEXT,
  no_llm_after_cast INTEGER NOT NULL CHECK(no_llm_after_cast=1)
);
CREATE TABLE IF NOT EXISTS health_v26_acceptance_audit (
  version TEXT PRIMARY KEY,
  exact_parent_v25_sha256 TEXT NOT NULL CHECK(length(exact_parent_v25_sha256)=64),
  original_case_count INTEGER NOT NULL CHECK(original_case_count=194),
  original_section_count INTEGER NOT NULL CHECK(original_section_count=43),
  old_wrong_prediction_count INTEGER NOT NULL CHECK(old_wrong_prediction_count=2),
  old_21_health_facts INTEGER NOT NULL CHECK(old_21_health_facts=21),
  visible_self_paragraphs INTEGER NOT NULL CHECK(visible_self_paragraphs=10),
  source_template_sections INTEGER NOT NULL CHECK(source_template_sections=11),
  user_has_not_approved_four_other_intents INTEGER NOT NULL CHECK(user_has_not_approved_four_other_intents=1),
  false_stem_pair_illness_name_suppressed INTEGER NOT NULL CHECK(false_stem_pair_illness_name_suppressed=1),
  directional_five_elements_corrected INTEGER NOT NULL CHECK(directional_five_elements_corrected=1),
  illness_and_patient_door_pressure_distinct INTEGER NOT NULL CHECK(illness_and_patient_door_pressure_distinct=1),
  yin_outer_palace_slowness_in_final INTEGER NOT NULL CHECK(yin_outer_palace_slowness_in_final=1),
  all_previous_rows_preserved INTEGER NOT NULL CHECK(all_previous_rows_preserved=1),
  actual_medical_prognosis_validated INTEGER NOT NULL CHECK(actual_medical_prognosis_validated=0),
  user_status TEXT NOT NULL CHECK(user_status='pending')
);
