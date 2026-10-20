-- The employment domain is shared by Shenqi and Kaiwu case sources.
-- One 1997 original chart includes *two* separately evidenced questions:
-- party-application decision and a later road-accident warning.
-- Never promote a post-accident calendar deduction into a 1997 exact-day call.
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS crossbook_employment_source_charts(
 chapter_key TEXT NOT NULL REFERENCES chapter_knowledge(chapter_key),
 case_id TEXT NOT NULL REFERENCES cases(case_id),
 cast_key TEXT NOT NULL DEFAULT 'primary',
 original_grid_start INTEGER NOT NULL,
 original_grid_end INTEGER NOT NULL,
 original_grid_sha256 TEXT NOT NULL CHECK(length(original_grid_sha256)=64),
 casting_description_line INTEGER NOT NULL,
 original_casting_description TEXT NOT NULL,
 special_center_undisturbed INTEGER NOT NULL DEFAULT 1 CHECK(special_center_undisturbed=1),
 original_undeciphered_stems_preserved INTEGER NOT NULL DEFAULT 1 CHECK(original_undeciphered_stems_preserved=1),
 PRIMARY KEY(chapter_key,case_id,cast_key)
);
CREATE TABLE IF NOT EXISTS crossbook_employment_source_palaces(
 chapter_key TEXT NOT NULL,
 case_id TEXT NOT NULL,
 cast_key TEXT NOT NULL,
 palace INTEGER NOT NULL CHECK(palace BETWEEN 1 AND 9),
 original_start_line INTEGER NOT NULL,
 original_end_line INTEGER NOT NULL,
 original_palace_label TEXT NOT NULL,
 original_spirit_text TEXT NOT NULL,
 original_door_text TEXT NOT NULL,
 original_star_text TEXT NOT NULL,
 source_literal_text TEXT NOT NULL,
 source_literal_sha256 TEXT NOT NULL CHECK(length(source_literal_sha256)=64),
 undeciphered_source_stem_count INTEGER NOT NULL DEFAULT 0 CHECK(undeciphered_source_stem_count>=0),
 inference_added INTEGER NOT NULL DEFAULT 0 CHECK(inference_added=0),
 PRIMARY KEY(chapter_key,case_id,cast_key,palace),
 FOREIGN KEY(chapter_key,case_id,cast_key)
   REFERENCES crossbook_employment_source_charts(chapter_key,case_id,cast_key)
);
CREATE TABLE IF NOT EXISTS crossbook_employment_case_issues(
 chapter_key TEXT NOT NULL REFERENCES chapter_knowledge(chapter_key),
 case_id TEXT NOT NULL REFERENCES cases(case_id),
 issue_key TEXT NOT NULL,
 domain_facet TEXT NOT NULL,
 known_before_original TEXT NOT NULL,
 original_prediction TEXT NOT NULL,
 book_reported_outcome TEXT NOT NULL,
 original_prediction_source_line INTEGER NOT NULL,
 outcome_source_line INTEGER NOT NULL,
 first_prediction_independently_corroborated INTEGER NOT NULL DEFAULT 0 CHECK(first_prediction_independently_corroborated=0),
 source_label TEXT NOT NULL DEFAULT 'user_accepts_book_report',
 user_case_by_case_review_required INTEGER NOT NULL DEFAULT 0 CHECK(user_case_by_case_review_required=0),
 metadata_json TEXT NOT NULL CHECK(json_valid(metadata_json)),
 PRIMARY KEY(chapter_key,case_id,issue_key)
);
CREATE TABLE IF NOT EXISTS crossbook_employment_source_phases(
 chapter_key TEXT NOT NULL REFERENCES chapter_knowledge(chapter_key),
 case_id TEXT NOT NULL REFERENCES cases(case_id),
 phase_key TEXT NOT NULL,
 phase_name TEXT NOT NULL,
 source_start_line INTEGER NOT NULL,
 source_end_line INTEGER NOT NULL CHECK(source_end_line>=source_start_line),
 original_literal TEXT NOT NULL,
 excerpt_sha256 TEXT NOT NULL CHECK(length(excerpt_sha256)=64),
 chronological_metadata_json TEXT NOT NULL CHECK(json_valid(chronological_metadata_json)),
 PRIMARY KEY(chapter_key,case_id,phase_key)
);
CREATE TABLE IF NOT EXISTS crossbook_employment_source_caveats(
 chapter_key TEXT NOT NULL REFERENCES chapter_knowledge(chapter_key),
 case_id TEXT NOT NULL REFERENCES cases(case_id),
 caveat_key TEXT NOT NULL,
 source_line INTEGER NOT NULL,
 original_quote TEXT NOT NULL,
 explanation TEXT NOT NULL,
 must_not_autocorrect INTEGER NOT NULL DEFAULT 1 CHECK(must_not_autocorrect=1),
 PRIMARY KEY(chapter_key,case_id,caveat_key)
);
CREATE VIEW IF NOT EXISTS unified_employment_cases_across_books AS
 SELECT c.case_id,c.event_family_id,c.domain_id,s.book_id,s.section_key,
 c.known_before,c.author_yongshen_steps,c.author_judgment,c.later_feedback
 FROM cases c JOIN sections s ON c.section_id=s.section_id
 WHERE c.domain_id='employment';
CREATE INDEX IF NOT EXISTS idx_crossbook_employment_issue_domain
 ON crossbook_employment_case_issues(domain_facet,case_id);
