PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS books (
    book_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    edition TEXT NOT NULL DEFAULT 'unknown_user_edition',
    source_status TEXT NOT NULL DEFAULT 'awaiting_source'
);
CREATE TABLE IF NOT EXISTS sections (
    section_id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id TEXT NOT NULL REFERENCES books(book_id),
    section_key TEXT NOT NULL,
    title TEXT NOT NULL,
    original_text TEXT NOT NULL,
    sha256 TEXT NOT NULL CHECK (length(sha256)=64),
    content_version INTEGER NOT NULL CHECK(content_version>0),
    reviewed INTEGER NOT NULL DEFAULT 0 CHECK(reviewed IN (0,1)),
    UNIQUE(book_id, section_key, content_version),
    UNIQUE(book_id, section_key, sha256)
);
CREATE TABLE IF NOT EXISTS cases (
    case_id TEXT PRIMARY KEY,
    section_id INTEGER NOT NULL REFERENCES sections(section_id),
    event_family_id TEXT NOT NULL,
    domain_id TEXT NOT NULL,
    known_before TEXT NOT NULL,
    author_yongshen_steps TEXT NOT NULL,
    author_judgment TEXT,
    later_feedback TEXT,
    reviewed INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_case_family ON cases(event_family_id);
CREATE TABLE IF NOT EXISTS rules (
    rule_id TEXT NOT NULL,
    version INTEGER NOT NULL,
    school_id TEXT NOT NULL,
    domain_id TEXT NOT NULL,
    relationship_id TEXT NOT NULL,
    section_id INTEGER NOT NULL REFERENCES sections(section_id),
    excerpt_start INTEGER NOT NULL,
    excerpt_end INTEGER NOT NULL,
    excerpt_sha256 TEXT NOT NULL,
    conditions_json TEXT NOT NULL,
    interpretation TEXT NOT NULL,
    summary TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('draft','reviewed','approved','rejected')),
    PRIMARY KEY(rule_id,version)
);
CREATE TABLE IF NOT EXISTS reading_releases (
    release_id TEXT PRIMARY KEY,
    version TEXT NOT NULL,
    school_id TEXT NOT NULL,
    approved_at TEXT,
    manifest_sha256 TEXT,
    note TEXT
);
CREATE TABLE IF NOT EXISTS chart_checks (
    chart_check_id TEXT PRIMARY KEY,
    school_id TEXT NOT NULL,
    method_version TEXT NOT NULL,
    datetime_iso TEXT NOT NULL,
    timezone TEXT NOT NULL,
    source_section_id INTEGER REFERENCES sections(section_id),
    expected_chart_sha256 TEXT NOT NULL,
    result TEXT NOT NULL DEFAULT 'pending'
);
