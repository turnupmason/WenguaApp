-- V4.2 append-only complete-source research database. V3.9 customer prose untouched.
PRAGMA foreign_keys=ON;
CREATE TABLE health_v42_book_anchored_twelve_stages (
 stem TEXT NOT NULL, stage TEXT NOT NULL, branch TEXT NOT NULL,
 already_explicit_in_old_book_index INTEGER NOT NULL CHECK(already_explicit_in_old_book_index IN(0,1)),
 polarity TEXT NOT NULL, anchor_original_book_start_line INTEGER NOT NULL,
 PRIMARY KEY (stem,stage), UNIQUE (stem,branch)
);
CREATE TABLE health_v42_unified_five_qualitative_numeric (
 case_id TEXT PRIMARY KEY,
 real_day TEXT NOT NULL,
 real_hour TEXT NOT NULL,
 relation TEXT NOT NULL,
 original_v39_sha256 TEXT NOT NULL CHECK(length(original_v39_sha256)=64),
 integrated_v42_sha256 TEXT NOT NULL CHECK(length(integrated_v42_sha256)=64),
 original_v39_verbatim_preserved INTEGER NOT NULL CHECK(original_v39_verbatim_preserved=1),
 six_module_symbolic_score INTEGER NOT NULL CHECK(six_module_symbolic_score BETWEEN 0 AND 100),
 new_chronic_conditional_low INTEGER NOT NULL CHECK(new_chronic_conditional_low BETWEEN 0 AND 100),
 new_chronic_conditional_high INTEGER NOT NULL CHECK(new_chronic_conditional_high BETWEEN 0 AND 100),
 never_predicted_medical_risk INTEGER NOT NULL CHECK(never_predicted_medical_risk=1),
 original_author_post_event_as_input INTEGER NOT NULL CHECK(original_author_post_event_as_input=0),
 user_approved INTEGER NOT NULL CHECK(user_approved=0)
);
CREATE TABLE health_v42_six_module_ledger (
 case_id TEXT NOT NULL,
 module_name TEXT NOT NULL,
 max_abs_points INTEGER NOT NULL CHECK(max_abs_points >= 0),
 raw_unbounded_candidate_sum INTEGER NOT NULL,
 applied_signed_points INTEGER NOT NULL,
 number_real_triggered_rules INTEGER NOT NULL CHECK(number_real_triggered_rules>=0),
 ledger_sha256 TEXT NOT NULL CHECK(length(ledger_sha256)=64),
 PRIMARY KEY(case_id,module_name),
 FOREIGN KEY(case_id) REFERENCES health_v42_unified_five_qualitative_numeric(case_id)
);
CREATE TABLE health_v42_appendonly_full_original_retention (
 version TEXT PRIMARY KEY CHECK(version='v4.2'),
 full_v41_parent_sha256 TEXT NOT NULL CHECK(length(full_v41_parent_sha256)=64),
 original_book_case_families INTEGER NOT NULL CHECK(original_book_case_families=194),
 original_chapters INTEGER NOT NULL CHECK(original_chapters=43),
 exact_original_81_pairs INTEGER NOT NULL CHECK(exact_original_81_pairs=81),
 user_supplement_pairs INTEGER NOT NULL CHECK(user_supplement_pairs=42),
 composite_conditions INTEGER NOT NULL CHECK(composite_conditions=17),
 old_failed_dev_cases INTEGER NOT NULL CHECK(old_failed_dev_cases=2),
 original_v39_verbatim_user_three INTEGER NOT NULL CHECK(original_v39_verbatim_user_three=3),
 extra_first_question_new_families INTEGER NOT NULL CHECK(extra_first_question_new_families=2),
 lifecycle_facts_10times12 INTEGER NOT NULL CHECK(lifecycle_facts_10times12=120),
 six_budget_5times6 INTEGER NOT NULL CHECK(six_budget_5times6=30),
 user_approved_for_ui INTEGER NOT NULL CHECK(user_approved_for_ui=0)
);
