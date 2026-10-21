-- 038: one domain at a time: marriage GPT draft library, never a second case archive.
-- Existing 194 book events and source texts are immutable; phrase artifacts are separate.
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS phrase_domain_progress (
 domain_id TEXT PRIMARY KEY, stage TEXT NOT NULL CHECK(stage IN
 ('not_started','prototype_draft','engine_blocked','verified_pilot','approved_for_release')),
 source_family_count INTEGER NOT NULL DEFAULT 0, source_note TEXT NOT NULL,
 state_space_per_domain INTEGER NOT NULL DEFAULT 388800,
 base_state_count INTEGER NOT NULL DEFAULT 1080,
 birth_year_count INTEGER NOT NULL DEFAULT 60,age_band_count INTEGER NOT NULL DEFAULT 3,
 sex_count INTEGER NOT NULL DEFAULT 2,
 computed_verified_charts INTEGER NOT NULL DEFAULT 0,
 instantiated_phrase_nodes INTEGER NOT NULL DEFAULT 0,
 approved_phrase_nodes INTEGER NOT NULL DEFAULT 0,
 last_prompt_version TEXT NOT NULL,update_note TEXT NOT NULL,
 CHECK(state_space_per_domain=base_state_count*birth_year_count*age_band_count*sex_count),
 CHECK(approved_phrase_nodes<=instantiated_phrase_nodes)
);
CREATE TABLE IF NOT EXISTS phrase_template_drafts (
 phrase_id TEXT PRIMARY KEY,
 domain_id TEXT NOT NULL REFERENCES phrase_domain_progress(domain_id),
 scenario TEXT NOT NULL,
 question_type TEXT NOT NULL,
 relationship_scope TEXT NOT NULL,
 target_age_band TEXT NOT NULL CHECK(target_age_band IN ('any','young','adult','older')),
 target_sex TEXT NOT NULL CHECK(target_sex IN ('any','male','female')),
 rule_conditions_json TEXT NOT NULL CHECK(json_valid(rule_conditions_json)),
 obligatory_evidence_json TEXT NOT NULL CHECK(json_valid(obligatory_evidence_json)),
 counterevidence_json TEXT NOT NULL CHECK(json_valid(counterevidence_json)),
 reasoning_trace_json TEXT NOT NULL CHECK(json_valid(reasoning_trace_json)),
 draft_text TEXT NOT NULL,
 draft_text_sha256 TEXT NOT NULL CHECK(length(draft_text_sha256)=64),
 origin TEXT NOT NULL DEFAULT 'gpt_authored_candidate_not_book_quote',
 review_status TEXT NOT NULL DEFAULT 'draft' CHECK(review_status IN ('draft','needs_rewrite','source_reviewed','approved','rejected')),
 chart_instantiated INTEGER NOT NULL DEFAULT 0 CHECK(chart_instantiated=0),
 confirmed_chart_sha256 TEXT,
 style_version TEXT NOT NULL,
 version INTEGER NOT NULL DEFAULT 1 CHECK(version>0),
 created_utc TEXT NOT NULL,
 CHECK(confirmed_chart_sha256 IS NULL)
);
CREATE TABLE IF NOT EXISTS phrase_source_links (
 phrase_id TEXT NOT NULL REFERENCES phrase_template_drafts(phrase_id),
 book_id TEXT NOT NULL CHECK(book_id IN ('shenqi','kaiwu')),
 source_section_key TEXT NOT NULL,
 source_sha256 TEXT NOT NULL CHECK(length(source_sha256)=64),
 source_lines_json TEXT NOT NULL CHECK(json_valid(source_lines_json)),
 case_id TEXT REFERENCES cases(case_id),
 relevance TEXT NOT NULL,
 epistemic_role TEXT NOT NULL CHECK(epistemic_role IN
 ('method_basis','author_example','counterexample_original_error','after_fact_warning')),
 PRIMARY KEY(phrase_id,book_id,source_section_key,relevance)
);
CREATE TABLE IF NOT EXISTS phrase_context_instances (
 instance_id TEXT PRIMARY KEY,
 phrase_id TEXT NOT NULL REFERENCES phrase_template_drafts(phrase_id),
 domain_id TEXT NOT NULL REFERENCES phrase_domain_progress(domain_id),
 state_id TEXT NOT NULL,
 birth_year_ganzhi TEXT NOT NULL,
 age_band TEXT NOT NULL CHECK(age_band IN ('young','adult','older')),
 sex TEXT NOT NULL CHECK(sex IN ('male','female')),
 relationship TEXT NOT NULL,question_type TEXT NOT NULL,
 cast_engine_version TEXT NOT NULL,full_board_sha256 TEXT NOT NULL CHECK(length(full_board_sha256)=64),
 facts_sha256 TEXT NOT NULL CHECK(length(facts_sha256)=64),
 complete_input_json TEXT NOT NULL CHECK(json_valid(complete_input_json)),
 matched_rule_evidence_json TEXT NOT NULL CHECK(json_valid(matched_rule_evidence_json)),
 generated_text TEXT NOT NULL,generated_text_sha256 TEXT NOT NULL CHECK(length(generated_text_sha256)=64),
 status TEXT NOT NULL CHECK(status IN ('draft','source_reviewed','approved','rejected')),
 created_utc TEXT NOT NULL,
 UNIQUE(domain_id,state_id,birth_year_ganzhi,age_band,sex,relationship,question_type,cast_engine_version,full_board_sha256,phrase_id)
);
CREATE TABLE IF NOT EXISTS phrase_pipeline_audit (
 event_id TEXT PRIMARY KEY,domain_id TEXT NOT NULL REFERENCES phrase_domain_progress(domain_id),
 prompt_version TEXT NOT NULL,source_archive_sha256 TEXT NOT NULL CHECK(length(source_archive_sha256)=64),
 stage TEXT NOT NULL,source_book_count INTEGER NOT NULL,
 source_case_count INTEGER NOT NULL,
 verified_board_count INTEGER NOT NULL,prototype_draft_count INTEGER NOT NULL,
 coverage_nodes_materialized INTEGER NOT NULL,notes_json TEXT NOT NULL CHECK(json_valid(notes_json))
);
