-- Kaiwu health case chapter / Shenqi health cases: one shared cases.domain_id='health'.
-- Preserve a parallel per-book printed-source witness for all six original figures;
-- B is same Shenqi 1996-07-27 father case and MUST NOT create a new event or chart.
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS health_crossbook_case_witnesses (
  witness_key TEXT PRIMARY KEY,
  section_id INTEGER NOT NULL REFERENCES sections(section_id),
  book_id TEXT NOT NULL REFERENCES books(book_id),
  chapter_key TEXT NOT NULL REFERENCES chapter_knowledge(chapter_key),
  case_id TEXT NOT NULL REFERENCES cases(case_id),
  event_family_id TEXT NOT NULL,
  domain_id TEXT NOT NULL DEFAULT 'health' CHECK(domain_id='health'),
  subdomain TEXT NOT NULL CHECK(subdomain IN ('human_health','animal_health')),
  printed_group TEXT NOT NULL,
  source_open_line INTEGER NOT NULL CHECK(source_open_line>0),
  source_chart_start INTEGER NOT NULL CHECK(source_chart_start>0),
  source_chart_end INTEGER NOT NULL CHECK(source_chart_end>=source_chart_start),
  full_source_sha256 TEXT NOT NULL CHECK(length(full_source_sha256)=64),
  printed_chart_sha256 TEXT NOT NULL CHECK(length(printed_chart_sha256)=64),
  witness_relationship TEXT NOT NULL CHECK(witness_relationship IN
    ('new_event_source','same_prior_event_reprinted')),
  source_outcome_independently_verified INTEGER NOT NULL DEFAULT 0
    CHECK(source_outcome_independently_verified=0),
  historical_new_prediction INTEGER NOT NULL DEFAULT 0 CHECK(historical_new_prediction=0),
  source_summary_json TEXT NOT NULL CHECK(json_valid(source_summary_json)),
  review_status TEXT NOT NULL DEFAULT 'draft',
  UNIQUE(chapter_key,source_chart_start)
);
CREATE TABLE IF NOT EXISTS health_crossbook_witness_palaces (
  witness_key TEXT NOT NULL REFERENCES health_crossbook_case_witnesses(witness_key),
  palace INTEGER NOT NULL CHECK(palace BETWEEN 1 AND 9),
  source_start_line INTEGER NOT NULL CHECK(source_start_line>0),
  source_end_line INTEGER NOT NULL CHECK(source_end_line>=source_start_line),
  palace_label_original TEXT NOT NULL,
  deity_original TEXT NOT NULL,
  door_original TEXT NOT NULL,
  star_original TEXT NOT NULL,
  source_cell_original TEXT NOT NULL,
  source_cell_sha256 TEXT NOT NULL CHECK(length(source_cell_sha256)=64),
  has_explicit_missing_text INTEGER NOT NULL DEFAULT 0 CHECK(has_explicit_missing_text IN (0,1)),
  normalized_guess_not_printed INTEGER NOT NULL DEFAULT 0 CHECK(normalized_guess_not_printed=0),
  PRIMARY KEY(witness_key,palace)
);
CREATE TABLE IF NOT EXISTS health_crossbook_comparison_steps (
  chapter_key TEXT NOT NULL REFERENCES chapter_knowledge(chapter_key),
  case_id TEXT NOT NULL REFERENCES cases(case_id),
  source_line INTEGER NOT NULL CHECK(source_line>0),
  subject_chart_label TEXT NOT NULL,
  original_editor_comparison TEXT NOT NULL,
  source_excerpt_sha256 TEXT NOT NULL CHECK(length(source_excerpt_sha256)=64),
  phase TEXT NOT NULL CHECK(phase='retrospective_editor_comparison_not_initial_prediction'),
  report_json TEXT NOT NULL CHECK(json_valid(report_json)),
  review_status TEXT NOT NULL DEFAULT 'draft',
  positive_training_eligible INTEGER NOT NULL DEFAULT 0 CHECK(positive_training_eligible=0),
  PRIMARY KEY(chapter_key,case_id,source_line)
);
CREATE VIEW IF NOT EXISTS health_cases_all_books AS
 SELECT c.case_id,c.event_family_id,c.domain_id,s.book_id,s.section_key,
        c.reviewed,c.known_before,c.author_yongshen_steps,c.author_judgment,
        c.later_feedback
 FROM cases AS c JOIN sections AS s ON s.section_id=c.section_id
 WHERE c.domain_id='health';
CREATE INDEX IF NOT EXISTS idx_health_witness_case ON health_crossbook_case_witnesses(case_id);
CREATE INDEX IF NOT EXISTS idx_health_witness_domain ON health_crossbook_case_witnesses(domain_id,subdomain);

CREATE TABLE IF NOT EXISTS health_crossbook_case_phases (
  witness_key TEXT NOT NULL REFERENCES health_crossbook_case_witnesses(witness_key),
  phase_key TEXT NOT NULL,
  phase_type TEXT NOT NULL CHECK(phase_type IN
    ('known_at_cast','original_printed_chart','author_initial_analysis',
     'author_initial_prediction','book_reported_feedback',
     'source_retrospective_comparison','post_feedback_editor_note')),
  source_start_line INTEGER NOT NULL CHECK(source_start_line>0),
  source_end_line INTEGER NOT NULL CHECK(source_end_line>=source_start_line),
  original_text TEXT NOT NULL,
  excerpt_sha256 TEXT NOT NULL CHECK(length(excerpt_sha256)=64),
  contemporaneous_evidence_independently_verified INTEGER NOT NULL DEFAULT 0
    CHECK(contemporaneous_evidence_independently_verified=0),
  eligible_for_blind_input INTEGER NOT NULL DEFAULT 0
    CHECK(eligible_for_blind_input IN (0,1)),
  PRIMARY KEY(witness_key,phase_key)
);
CREATE INDEX IF NOT EXISTS idx_health_case_phases
 ON health_crossbook_case_phases(phase_type,witness_key);
