"""Versioned, local-only SQLite store for user-supplied book chapters."""
import hashlib
from pathlib import Path
import sqlite3

ROOT = Path(__file__).resolve().parents[2]
BOOKS = {"shenqi": "神奇之门", "kaiwu": "开悟之门"}

def connect(path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path)
    con.execute("PRAGMA foreign_keys=ON")
    return con

def initialize(path):
    with connect(path) as con:
        con.executescript((ROOT/"schema/schema.sql").read_text(encoding="utf-8"))
        con.executescript((ROOT/"schema/migrations/001_chapter_knowledge.sql").read_text(encoding="utf-8"))
        con.executescript((ROOT/"schema/migrations/002_semantic_assertions.sql").read_text(encoding="utf-8"))
        con.executescript((ROOT/"schema/migrations/003_incomplete_historical_case_parts.sql").read_text(encoding="utf-8"))
        con.executescript((ROOT/"schema/migrations/004_health_case_evidence.sql").read_text(encoding="utf-8"))
        con.executescript((ROOT/"schema/migrations/005_book_case_verdicts.sql").read_text(encoding="utf-8"))
        con.executescript((ROOT/"schema/migrations/006_employment_ranked_candidates.sql").read_text(encoding="utf-8"))
        con.executescript((ROOT/"schema/migrations/007_business_multi_casts.sql").read_text(encoding="utf-8"))
        con.executescript((ROOT/"schema/migrations/008_case_reasoning_trace.sql").read_text(encoding="utf-8"))
        con.executescript((ROOT/"schema/migrations/009_full_archive_center_provenance.sql").read_text(encoding="utf-8"))
        con.executescript((ROOT/"schema/migrations/010_litigation_event_phase.sql").read_text(encoding="utf-8"))
        con.executemany("INSERT OR IGNORE INTO books(book_id,title) VALUES (?,?)",
                        sorted(BOOKS.items()))

def import_section(path, book, section_key, title, original_text):
    if book not in BOOKS:
        raise ValueError("V1 accepts only 神奇之门 and 开悟之门")
    if not all(isinstance(s,str) and s.strip() for s in
               (section_key,title,original_text)):
        raise ValueError("Nonempty original chapter and metadata required")
    initialize(path)
    digest = hashlib.sha256(original_text.encode("utf-8")).hexdigest()
    with connect(path) as con:
        prior = con.execute(
            "SELECT section_id,content_version FROM sections WHERE book_id=? AND section_key=? AND sha256=?",
            (book,section_key,digest)).fetchone()
        if prior:
            return {"status":"identical_source_already_present",
                    "section_id":prior[0],"version":prior[1],"sha256":digest}
        version = con.execute(
            "SELECT COALESCE(MAX(content_version),0)+1 FROM sections WHERE book_id=? AND section_key=?",
            (book,section_key)).fetchone()[0]
        cursor = con.execute(
            "INSERT INTO sections(book_id,section_key,title,original_text,sha256,content_version) "
            "VALUES (?,?,?,?,?,?)",
            (book,section_key,title,original_text,digest,version))
        return {"status":"imported_unreviewed","section_id":cursor.lastrowid,
                "version":version,"sha256":digest}
