PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS historical_case_reasoning_trace (
case_id TEXT NOT NULL,step_number INTEGER NOT NULL,source_line INTEGER NOT NULL CHECK(source_line>0),
evidence_json TEXT NOT NULL CHECK(json_valid(evidence_json)),
review_status TEXT NOT NULL DEFAULT 'mechanical_source_link_needs_author_chain_review',
positive_training_eligible INTEGER NOT NULL DEFAULT 0 CHECK(positive_training_eligible IN(0,1)),
PRIMARY KEY(case_id,step_number),
FOREIGN KEY(case_id,step_number) REFERENCES historical_case_reasoning(case_id,step_number));
CREATE INDEX IF NOT EXISTS idx_case_reasoning_trace_status ON historical_case_reasoning_trace(review_status);
