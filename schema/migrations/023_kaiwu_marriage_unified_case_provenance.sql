-- Kaiwu relationship cases share Shenqi's existing marriage cases.domain_id.
-- Same person across different question-times is LINKED, not merged into one event.
-- User accepts original-book cases without individual approval; an explicit
-- incorrect initial prediction still remains wrong, not a positive example.
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS crossbook_relationship_cast_witnesses (
  chapter_key TEXT NOT NULL REFERENCES chapter_knowledge(chapter_key),
  case_id TEXT NOT NULL REFERENCES cases(case_id),
  cast_key TEXT NOT NULL,
  printed_chart_start INTEGER NOT NULL CHECK(printed_chart_start>0),
  printed_chart_end INTEGER NOT NULL CHECK(printed_chart_end>=printed_chart_start),
  raw_chart_sha256 TEXT NOT NULL CHECK(length(raw_chart_sha256)=64),
  source_cast_header_line INTEGER NOT NULL,
  source_header_original TEXT NOT NULL,
  domain_id TEXT NOT NULL DEFAULT 'marriage' CHECK(domain_id='marriage'),
  note TEXT NOT NULL,
  PRIMARY KEY(chapter_key,case_id,cast_key),
  UNIQUE(chapter_key,printed_chart_start)
);
CREATE TABLE IF NOT EXISTS crossbook_relationship_literal_palaces (
  chapter_key TEXT NOT NULL,
  case_id TEXT NOT NULL,
  cast_key TEXT NOT NULL,
  palace INTEGER NOT NULL CHECK(palace BETWEEN 1 AND 9),
  line_start INTEGER NOT NULL,
  line_end INTEGER NOT NULL,
  palace_label_original TEXT NOT NULL,
  deity_original TEXT NOT NULL,
  door_original TEXT NOT NULL,
  star_original TEXT NOT NULL,
  literal_original TEXT NOT NULL,
  literal_sha256 TEXT NOT NULL CHECK(length(literal_sha256)=64),
  no_inference INTEGER NOT NULL DEFAULT 1 CHECK(no_inference=1),
  PRIMARY KEY(chapter_key,case_id,cast_key,palace),
  FOREIGN KEY(chapter_key,case_id,cast_key)
    REFERENCES crossbook_relationship_cast_witnesses(chapter_key,case_id,cast_key)
);
CREATE TABLE IF NOT EXISTS crossbook_relationship_case_phases (
  chapter_key TEXT NOT NULL REFERENCES chapter_knowledge(chapter_key),
  case_id TEXT NOT NULL REFERENCES cases(case_id),
  phase_key TEXT NOT NULL,
  phase TEXT NOT NULL,
  start_line INTEGER NOT NULL,
  end_line INTEGER NOT NULL CHECK(end_line>=start_line),
  original_text TEXT NOT NULL,
  source_sha256 TEXT NOT NULL CHECK(length(source_sha256)=64),
  chronology_json TEXT NOT NULL CHECK(json_valid(chronology_json)),
  PRIMARY KEY(chapter_key,case_id,phase_key)
);
CREATE TABLE IF NOT EXISTS crossbook_relationship_event_links (
  chapter_key TEXT NOT NULL REFERENCES chapter_knowledge(chapter_key),
  case_id TEXT NOT NULL REFERENCES cases(case_id),
  related_case_id TEXT NOT NULL REFERENCES cases(case_id),
  relationship TEXT NOT NULL,
  evidence_original TEXT NOT NULL,
  evidence_source_line INTEGER NOT NULL,
  same_person_but_different_cast INTEGER NOT NULL DEFAULT 1 CHECK(same_person_but_different_cast=1),
  same_historical_event INTEGER NOT NULL DEFAULT 0 CHECK(same_historical_event=0),
  PRIMARY KEY(chapter_key,case_id,related_case_id)
);
CREATE TABLE IF NOT EXISTS unified_case_domain_facets (
  case_id TEXT NOT NULL REFERENCES cases(case_id),
  domain_id TEXT NOT NULL,
  source_chapter_key TEXT NOT NULL REFERENCES chapter_knowledge(chapter_key),
  primary_domain INTEGER NOT NULL CHECK(primary_domain IN(0,1)),
  note TEXT NOT NULL,
  PRIMARY KEY(case_id,domain_id,source_chapter_key)
);
CREATE TABLE IF NOT EXISTS crossbook_relationship_missing_casts (
  chapter_key TEXT NOT NULL REFERENCES chapter_knowledge(chapter_key),
  case_id TEXT NOT NULL REFERENCES cases(case_id),
  cast_key TEXT NOT NULL,
  source_line INTEGER NOT NULL,
  original_source_claim TEXT NOT NULL,
  printed_nine_palace_grid_missing INTEGER NOT NULL DEFAULT 1 CHECK(printed_nine_palace_grid_missing=1),
  must_never_backfill INTEGER NOT NULL DEFAULT 1 CHECK(must_never_backfill=1),
  PRIMARY KEY(chapter_key,case_id,cast_key)
);
CREATE TABLE IF NOT EXISTS crossbook_relationship_source_errors (
  chapter_key TEXT NOT NULL REFERENCES chapter_knowledge(chapter_key),
  case_id TEXT NOT NULL REFERENCES cases(case_id),
  initial_prediction_line INTEGER NOT NULL,
  explicit_user_rejection_line INTEGER NOT NULL,
  later_user_disclosure_line INTEGER NOT NULL,
  retrospective_author_response_line INTEGER NOT NULL,
  initial_original TEXT NOT NULL,
  explicit_rejection_original TEXT NOT NULL,
  later_disclosure_original TEXT NOT NULL,
  later_reinterpretation_original TEXT NOT NULL,
  initial_was_wrong INTEGER NOT NULL DEFAULT 1 CHECK(initial_was_wrong=1),
  retrospect_not_blind_success INTEGER NOT NULL DEFAULT 1 CHECK(retrospect_not_blind_success=1),
  no_orientation_as_illness_label INTEGER NOT NULL DEFAULT 1 CHECK(no_orientation_as_illness_label=1),
  PRIMARY KEY(chapter_key,case_id)
);
CREATE INDEX IF NOT EXISTS idx_rel_event_links ON crossbook_relationship_event_links(case_id,related_case_id);
CREATE INDEX IF NOT EXISTS idx_unified_facets ON unified_case_domain_facets(domain_id,case_id);
CREATE VIEW IF NOT EXISTS relationships_across_all_books AS
 SELECT c.case_id,c.event_family_id,c.domain_id,s.book_id,s.section_key,
        c.known_before,c.author_judgment,c.later_feedback
 FROM cases c JOIN sections s ON s.section_id=c.section_id
 WHERE c.domain_id='marriage';
