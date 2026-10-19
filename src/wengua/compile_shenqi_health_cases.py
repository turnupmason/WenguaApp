"""Source-preserving health chapter importer: six events, nine literal cells each.

DO NOT use historic author's answers or after-event feedback as input to
blind interpretation. Source text stays in user's private local SQLite,
not public Git. All method/index records are draft, never diagnoses.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import re

from .database import ROOT,connect,initialize,import_section

EXPECTED_SHA="3f9a01be996e6230c73cc7df27f00c11134f9308e4115cf934f59fead6de0e3a"
KEY="health_prediction_ch01"
CHAPTER_KEY=f"shenqi/{KEY}/v1"
TITLE="人体疾病预测"
DATA=ROOT/"data/knowledge/shenqi/health_prediction_ch01"
LABELS={"坎一宫":1,"坤二宫":2,"震三宫":3,"巽四宫":4,"中五宫":5,
        "乾六宫":6,"兑七宫":7,"艮八宫":8,"离九宫":9}

def _json(row):
    return json.dumps(row,ensure_ascii=False,sort_keys=True,separators=(",",":"))

def _text(lines,loc):
    a,b=loc
    if type(a) is not int or type(b) is not int or not 1<=a<=b<=len(lines):
        raise ValueError("Invalid source text line pointer")
    return "\n".join(lines[a-1:b])

def _build(source_text):
    lines=source_text.splitlines()
    if (len(lines)!=298 or lines[0].strip()!="第一章 人体疾病预测"
        or lines[12].strip()!="第二节 实例解析（6例）"
        or not lines[292].startswith("—— 精校及盘面转写说明")):
        raise ValueError("Different health source version, boundary or editorial notes")
    idx=json.loads((DATA/"case_index.json").read_text(encoding="utf-8"))
    methods=json.loads((DATA/"method_index.json").read_text(encoding="utf-8"))
    if idx["file_source_sha256"]!=EXPECTED_SHA or methods["source_sha256"]!=EXPECTED_SHA:
        raise ValueError("Public index does not match user's health chapter text")
    cases=idx["cases"]
    if len(cases)!=6 or sorted(c["index"] for c in cases)!=list(range(1,7)):
        raise ValueError("Expected six complete, distinct source stories")
    if sum(len(c["steps"]) for c in cases)!=29:
        raise ValueError("Expected 29 numbered author analysis steps")
    if len({c["event_family_id"] for c in cases})!=6:
        raise ValueError("Reused event family, not six independent stories")
    records=[]
    for case in cases:
        start,end=case["line_range"]
        if case["source_sha256"]!=EXPECTED_SHA:
            raise ValueError("One case comes from a different source text")
        if not _text(lines,(start,start)).startswith("实例"+("一","二","三","四","五","六")[case["index"]-1]):
            raise ValueError("Incorrect case chapter boundary")
        rows=[]
        a,b=case["chart_rows"]
        if b-a!=8 or not start<=a<=b<=end:
            raise ValueError("Need nine source-preserved palace rows per event")
        for n in range(a,b+1):
            cols=lines[n-1].split()
            if len(cols)!=4 or cols[0] not in LABELS:
                raise ValueError(f"Unparseable, nonverbatim nine-palace row at {n}")
            rows.append((LABELS[cols[0]],n,*cols))
        if sorted(row[0] for row in rows)!=list(range(1,10)):
            raise ValueError("Duplicated/missing source palace")
        steps=[]
        for n,loc in enumerate(case["steps"],start=1):
            txt=_text(lines,(loc,loc))
            if not txt.strip().startswith(f"（{n}）"):
                raise ValueError(f"Case {case['index']} step {n} missing author numbering")
            topic=case["analysis_topics"][n-1]
            steps.append((n,loc,txt,topic))
        if len(case["analysis_topics"])!=len(steps):
            raise ValueError("Case steps and method topics misaligned")
        disclosures=[]
        for entry in case.get("progressive_disclosures",[])+case.get("disclosure",{}).get("line_events",[]):
            at=entry["lines"]
            if not start<=at[0]<=at[1]<=end:
                raise ValueError("Disclosure outside own story")
            disclosures.append((at[0],entry["phase"],entry["type"],_text(lines,at)))
        if len({r[0] for r in disclosures})!=len(disclosures):
            raise ValueError("Duplicate disclosure turn")
        predictions=case["author_predictions"]["lines"]
        feedback=case["feedback_lines"]
        if any(not start<=n<=end for n in predictions+feedback):
            raise ValueError("Prediction/feedback reference outside case")
        records.append({"index":case["index"],"case":case,
                        "prior":_text(lines,case["opening"]),
                        "author_steps":"\n".join(s[2] for s in steps),
                        "author_judgment":"\n".join(_text(lines,(n,n)) for n in predictions),
                        "later_feedback":"\n".join(_text(lines,(n,n)) for n in feedback),
                        "chart_rows":rows,"steps":steps,"disclosures":disclosures})
    return lines,methods,records

def _method_entries(methods,lines):
    """Store compact public research methods as citation-linked local assertions."""
    groups=(("body_palace_mappings","health_body_map"),
            ("yongshen_rules","health_yongshen"),
            ("author_workflow_nodes","health_reasoning_workflow"))
    entries=[]
    for attr,kind in groups:
        for rule in methods[attr]:
            cid=rule["concept_id"]
            if attr=="body_palace_mappings":
                a,b=rule["source_lines"]
            elif attr=="yongshen_rules":
                a=b=rule["source_line"]
            else:
                a=b=rule["lines"][0]
            if not 1<=a<=b<=len(lines):
                raise ValueError("Health research method source span invalid")
            entries.append((cid,kind,a,b,_json(rule),_text(lines,(a,b))))
    if len(entries)!=30 or len({e[0] for e in entries})!=30:
        raise ValueError("Unexpected health method coverage")
    return entries

def import_health_chapter(db_path,source_file):
    raw=Path(source_file).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=EXPECTED_SHA:
        raise ValueError("Health chapter source SHA256 mismatch")
    text=raw.decode("utf-8")
    lines,methods,records=_build(text)  # validate all 6 complete charts BEFORE mutation
    method_entries=_method_entries(methods,lines)
    # Append-only; existing 4 chapters + semantic facts remain unchanged.
    import_section(db_path,"shenqi",KEY,TITLE,text)
    initialize(db_path)
    with connect(db_path) as db:
        existing=db.execute("SELECT source_sha256 FROM chapter_knowledge WHERE chapter_key=?",(CHAPTER_KEY,)).fetchone()
        if existing is None:
            db.execute("""INSERT INTO chapter_knowledge
                (chapter_key,book_id,title,source_sha256,source_length_bytes,
                 knowledge_version,review_status) VALUES (?,?,?,?,?,'1','draft')""",
                 (CHAPTER_KEY,"shenqi",TITLE,EXPECTED_SHA,len(raw)))
        elif existing[0]!=EXPECTED_SHA:
            raise ValueError("Source hash conflict; make a versioned migration")
        section=db.execute("""SELECT section_id FROM sections WHERE book_id='shenqi'
            AND section_key=? AND sha256=?""",(KEY,EXPECTED_SHA)).fetchone()
        if not section:raise ValueError("Missing exact full source section")
        section_id=section[0]
        for cid,kind,source_start,source_end,metadata,excerpt in method_entries:
            old=db.execute("""SELECT kind,metadata_json,original_excerpt
                 FROM semantic_assertions WHERE chapter_key=? AND concept_id=?
                 AND source_start_line=?""",
                 (CHAPTER_KEY,cid,source_start)).fetchone()
            wanted=(kind,metadata,excerpt)
            if old is None:
                db.execute("""INSERT INTO semantic_assertions
                     (chapter_key,concept_id,kind,relation,source_start_line,
                      source_end_line,metadata_json,original_excerpt,review_status)
                     VALUES (?,?,?,'source_health_method',?,?,?,?,'draft')""",
                     (CHAPTER_KEY,cid,kind,source_start,source_end,metadata,excerpt))
            elif old!=wanted:
                raise ValueError("Previously imported health method changed")
        for rec in records:
            info=rec["case"]
            case_id=info["event_family_id"]
            record=(section_id,case_id,"health",rec["prior"],rec["author_steps"],
                    rec["author_judgment"],rec["later_feedback"])
            existing=db.execute("""SELECT section_id,event_family_id,domain_id,
                known_before,author_yongshen_steps,author_judgment,later_feedback
                FROM cases WHERE case_id=?""",(case_id,)).fetchone()
            if existing is None:
                db.execute("""INSERT INTO cases
                    (case_id,section_id,event_family_id,domain_id,known_before,
                     author_yongshen_steps,author_judgment,later_feedback,reviewed)
                     VALUES (?,?,?,?,?,?,?,?,0)""",(case_id,*record))
            elif existing!=record:
                raise ValueError(f"Case {case_id} changed; no overwrite")
            meta={k:v for k,v in info.items() if k not in ("author_predictions","feedback_lines")}
            proto=("complete_source_text_chart_unverified_by_independent_cast",
                   "user_reordered_chart_transcription_only",0,0,EXPECTED_SHA,_json(meta))
            prior=db.execute("""SELECT completeness,published_chart_verification,
                feedback_independently_verified,eligible_blind_test,case_source_sha256,
                metadata_json FROM historical_case_protocol WHERE case_id=?""",(case_id,)).fetchone()
            if prior is None:
                db.execute("""INSERT INTO historical_case_protocol
                    (case_id,completeness,published_chart_verification,
                     feedback_independently_verified,eligible_blind_test,
                     case_source_sha256,metadata_json)
                    VALUES (?,?,?,?,?,?,?)""",(case_id,*proto))
            elif prior!=proto:
                raise ValueError("Case protocol metadata changed")
            for palace,n,label,deity,door,star in rec["chart_rows"]:
                original=(n,label,deity,door,star)
                old=db.execute("""SELECT source_line,palace_label_raw,deity_raw,
                    door_position_raw,star_position_raw
                    FROM historical_chart_cells WHERE case_id=? AND palace=?""",(case_id,palace)).fetchone()
                if old is None:
                    db.execute("""INSERT INTO historical_chart_cells
                        (case_id,palace,source_line,palace_label_raw,deity_raw,
                         door_position_raw,star_position_raw) VALUES (?,?,?,?,?,?,?)""",
                         (case_id,palace,*original))
                elif old!=original:
                    raise ValueError("Original chart literal changed; refuse to replace")
            for n,source_line,author_step,topic in rec["steps"]:
                metadata={"source_fact_role":"author_reasoning_not_live_prediction",
                          "case_relation":info["patient_relation"],
                          "method_topic":topic,
                          "source_book":"shenqi","source_chapter":KEY,
                          "after_intermediate_disclosure":any(d[0]<source_line for d in rec["disclosures"])}
                wanted=(source_line,author_step,topic,_json(metadata))
                old=db.execute("""SELECT source_line,author_analysis_original,
                    short_method_topic,metadata_json FROM historical_case_reasoning
                    WHERE case_id=? AND step_number=?""",(case_id,n)).fetchone()
                if old is None:
                    db.execute("""INSERT INTO historical_case_reasoning
                        (case_id,step_number,source_line,author_analysis_original,
                         short_method_topic,metadata_json) VALUES (?,?,?,?,?,?)""",
                         (case_id,n,*wanted))
                elif old!=wanted:
                    raise ValueError("Author step changed; refuse to overwrite")
            for source_line,phase,kind,statement in rec["disclosures"]:
                wanted=(phase,kind,statement)
                old=db.execute("""SELECT phase,fact_type,original_statement
                     FROM historical_case_disclosures WHERE case_id=? AND source_line=?""",
                     (case_id,source_line)).fetchone()
                if old is None:
                    db.execute("""INSERT INTO historical_case_disclosures
                        (case_id,source_line,phase,fact_type,original_statement)
                        VALUES (?,?,?,?,?)""",
                        (case_id,source_line,*wanted))
                elif old!=wanted:
                    raise ValueError("Progressive disclosure changed")
        results={}
        for tbl in ("cases","historical_chart_cells","historical_case_reasoning",
                    "historical_case_disclosures","historical_case_protocol"):
            results[tbl]=db.execute(f"""SELECT count(*) FROM {tbl}
               WHERE case_id IN (SELECT case_id FROM cases WHERE section_id=?)""" if tbl!="cases"
               else "SELECT count(*) FROM cases WHERE section_id=?",(section_id,)).fetchone()[0]
        # semantic methods are public compact candidates; local remains available
        # with this chapter in its complete source. No silent promotion to approved.
        approved=db.execute("""SELECT count(*) FROM rules WHERE status='approved'
                          AND section_id=?""",(section_id,)).fetchone()[0]
        method_count=db.execute("SELECT count(*) FROM semantic_assertions WHERE chapter_key=?",
                               (CHAPTER_KEY,)).fetchone()[0]
    return {"method_assertions":method_count,"status":"complete_source_studies_imported_as_draft",
            "chapter_key":CHAPTER_KEY,"source_sha256":EXPECTED_SHA,
            "source_lines":len(lines),"case_charts":results["historical_case_protocol"],
            "nine_palace_literal_cells":results["historical_chart_cells"],
            "author_reasoning_steps":results["historical_case_reasoning"],
            "staged_disclosures":results["historical_case_disclosures"],
            "complete_event_families":results["cases"],
            "approved_rules":approved,"raw_original_stored_only_locally":True}
