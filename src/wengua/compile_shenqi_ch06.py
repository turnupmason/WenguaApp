"""Safely append user-provided Shenqi Chapter 6 to a local existing SQLite.

The public repository stores no verbatim book chapter, no author forecasts
as training prompts, and no post-event outcomes within prior known context.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

from .database import connect,initialize,import_section,ROOT
from .ch06_knowledge import source_index

EXPECTED_SHA="50c76ce5354d3378a842d6117f06c239bcdfe2f04786663c2e89f606d98c402e"
BOOK="shenqi"
SECTION_KEY="application_overview_ch06"
CHAPTER_KEY="shenqi/application_overview_ch06/v1"
TITLE="奇门遁甲应用概述"
PUBLIC_CASE=ROOT/"data/knowledge/shenqi/application_overview_ch06/historical_cases_index.json"

def _canonical(row):
    return json.dumps(row,ensure_ascii=False,sort_keys=True,separators=(",",":"))

def _entries(index):
    groups=("method_steps","yongshen_candidates","timing_candidates","five_no_encounter")
    result=[]
    for group in groups:
        for row in index[group]:
            kind=row["kind"]
            cid=row["concept_id"]
            loc=row["source_lines"]
            if len(loc)!=2 or not all(type(x) is int for x in loc) or not 1<=loc[0]<=loc[1]<=240:
                raise ValueError("Invalid Ch6 source span")
            result.append((cid,kind,loc[0],loc[1],_canonical(row)))
    if len({r[0] for r in result})!=len(result):
        raise ValueError("Duplicate Chapter6 concept ID")
    if len(result)!=index["method_count"]+index["role_count"]+index["timing_count"]+index["five_no_encounter_count"]:
        raise ValueError("Chapter6 registry summary/count mismatch")
    return result

def import_chapter6(db_path,source_file):
    """Validate complete source and index BEFORE mutating any database."""
    raw=Path(source_file).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=EXPECTED_SHA:
        raise ValueError("Chapter 6 source SHA256 mismatch; do not import another edition")
    original=raw.decode("utf-8")
    lines=original.splitlines()
    if (len(lines)!=240 or lines[0].strip()!="第六章"
        or lines[1].strip()!="奇门遁甲应用概述"
        or "第五节奇门定应期的主要方法" not in lines[205]):
        raise ValueError("Unexpected Chapter 6 content/boundary")
    index=source_index()
    if index["source_sha256"]!=EXPECTED_SHA or index["source"]["lines"]!=len(lines):
        raise ValueError("Public source index does not match original")
    entries=_entries(index)
    cases=json.loads(PUBLIC_CASE.read_text(encoding="utf-8"))
    if cases["source_sha256"]!=EXPECTED_SHA or len(cases["events"])!=1:
        raise ValueError("Case index corrupted or source changed")
    event=cases["events"][0]
    if event["complete_nine_palace_chart"] or event["eligible_as_sealed_independent_test"]:
        raise ValueError("Historical partial case incorrectly marked complete")
    # Original can be imported only in a private local DB. No raw words enter git.
    import_section(db_path,BOOK,SECTION_KEY,TITLE,original)
    initialize(db_path)
    with connect(db_path) as db:
        prior=db.execute("SELECT source_sha256 FROM chapter_knowledge WHERE chapter_key=?",
                         (CHAPTER_KEY,)).fetchone()
        if prior is None:
            db.execute("""INSERT INTO chapter_knowledge
                (chapter_key,book_id,title,source_sha256,source_length_bytes,knowledge_version,review_status)
                VALUES (?,?,?,?,?,'1','draft')""",
                (CHAPTER_KEY,BOOK,TITLE,EXPECTED_SHA,len(raw)))
        elif prior[0]!=EXPECTED_SHA:
            raise ValueError("Chapter source changed; create a new source version")
        for cid,kind,start,end,metadata in entries:
            excerpt="\n".join(lines[start-1:end])
            old=db.execute("""SELECT metadata_json,original_excerpt FROM semantic_assertions
                WHERE chapter_key=? AND concept_id=? AND source_start_line=?""",
                (CHAPTER_KEY,cid,start)).fetchone()
            if old is not None:
                if old!=(metadata,excerpt):
                    raise ValueError("Previously stored source assertion differs; no mutation allowed")
                continue
            db.execute("""INSERT INTO semantic_assertions
                (chapter_key,concept_id,kind,relation,source_start_line,
                 source_end_line,metadata_json,original_excerpt,review_status)
                VALUES (?,?,?,?,?,?,?,?,'draft')""",
                (CHAPTER_KEY,cid,kind,"ch06_source_method",start,end,metadata,excerpt))
        event_id=event["event_family_id"]
        pieces=event["source_lines"]
        def part(name):
            a,b=pieces[name]
            if a<1 or b>240 or a>b:
                raise ValueError("Invalid historical source lines")
            return "\n".join(lines[a-1:b])
        case_parts=(part("prior_news"),part("known_time_and_casting"),
                    part("author_prediction"),part("later_result"))
        case_json=_canonical({k:v for k,v in event.items() if k!="source_lines"})
        old=db.execute("""SELECT reference_json,prior_known_text,chart_evidence_text,
            author_prediction_text,after_event_feedback_text,chart_is_complete,approved_for_blind_test
            FROM incomplete_historical_cases WHERE event_family_id=?""",(event_id,)).fetchone()
        wanted=(case_json,*case_parts,0,0)
        if old is None:
            db.execute("""INSERT INTO incomplete_historical_cases
                (event_family_id,chapter_key,reference_json,prior_known_text,chart_evidence_text,
                 author_prediction_text,after_event_feedback_text,chart_is_complete,
                 approved_for_blind_test,review_status)
                VALUES (?,?,?,?,?,?,?,0,0,'draft')""",
                (event_id,CHAPTER_KEY,case_json,*case_parts))
        elif tuple(old)!=wanted:
            raise ValueError("Historical case changed; do not overwrite")
        count=db.execute("SELECT COUNT(*) FROM semantic_assertions WHERE chapter_key=?",
                         (CHAPTER_KEY,)).fetchone()[0]
        incomplete=db.execute("SELECT COUNT(*) FROM incomplete_historical_cases WHERE chapter_key=?",
                         (CHAPTER_KEY,)).fetchone()[0]
    return {"chapter_key":CHAPTER_KEY,"source_sha256":EXPECTED_SHA,
            "source_lines":len(lines),"indexed_assertions":count,
            "incomplete_historical_cases":incomplete,
            "complete_historical_cases":0,
            "approved_rules":0,"approved_readings":0,
            "source_text":"local_only_not_public_git",
            "result":"draft_import_completed_no_prediction_release"}
