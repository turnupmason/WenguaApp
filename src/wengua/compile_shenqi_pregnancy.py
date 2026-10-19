"""Incremental local-only Shenqi pregnancy chapter importer and old health backfill.

Whole event families, one actual cast each, one source-success label each.
A book-success assessment is not independent clinical or scientific validation.
All original Chinese full prose stays ONLY in the private local SQLite.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from .database import ROOT,connect,initialize,import_section

SHA="51af5117a1390f8af44e27c70fde83722d5df98d9c517e303a1dde7d433b5b9e"
HEALTH_SHA="3f9a01be996e6230c73cc7df27f00c11134f9308e4115cf934f59fead6de0e3a"
KEY="pregnancy_prediction_ch03"
CHAPTER="shenqi/"+KEY+"/v1"
TITLE="怀孕分娩预测"
DATA=ROOT/"data/knowledge/shenqi/pregnancy_prediction_ch03"
HEALTH_INDEX=ROOT/"data/knowledge/shenqi/health_prediction_ch01/case_index.json"
PALACE={"坎一宫":1,"坤二宫":2,"震三宫":3,"巽四宫":4,"中五宫":5,
        "乾六宫":6,"兑七宫":7,"艮八宫":8,"离九宫":9}
HAN="一二三四五六"

def canon(x):
    return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":"))

def extract(lines,a,b):
    if not all(type(x) is int for x in (a,b)) or not 1<=a<=b<=len(lines):
        raise ValueError("Source pointer out of actual chapter")
    return "\n".join(lines[a-1:b])

def validate_pregnancy_source(raw):
    if hashlib.sha256(raw).hexdigest()!=SHA:
        raise ValueError("Pregnancy chapter SHA256 mismatch: do not touch DB")
    lines=raw.decode("utf-8").splitlines()
    if len(lines)!=313 or not lines[1].startswith("第三章 怀孕分娩预测"):
        raise ValueError("Unexpected pregnancy source boundaries")
    cases=json.loads((DATA/"case_index.json").read_text(encoding="utf-8"))
    methods=json.loads((DATA/"method_index.json").read_text(encoding="utf-8"))
    if cases["source_sha256"]!=SHA or methods["source_sha256"]!=SHA:
        raise ValueError("Public source index hash mismatch")
    if len(cases["cases"])!=6 or sum(len(x["numbered_author_step_lines"]) for x in cases["cases"])!=23:
        raise ValueError("Expected 6 indivisible original cases, 23 author steps")
    if len(methods["methods"])!=24 or len({r["concept_id"] for r in methods["methods"]})!=24:
        raise ValueError("Source method list corrupted")
    valid=[]
    for i,c in enumerate(cases["cases"],1):
        if c["case_number"]!=i or not lines[c["source_case_span"][0]-1].startswith("实例"+HAN[i-1]):
            raise ValueError("Case number/header mismatch")
        a,b=c["raw_nine_palace_rows"]
        if b-a!=8:raise ValueError("Missing source palace table")
        cells=[]
        for n in range(a,b+1):
            v=lines[n-1].split()
            if len(v)!=4 or v[0] not in PALACE:raise ValueError("Unparseable nine-palace source cell")
            cells.append((PALACE[v[0]],n,*v))
        if sorted(x[0] for x in cells)!=list(range(1,10)):
            raise ValueError("Duplicate or missing original palace")
        steps=[]
        for j,n in enumerate(c["numbered_author_step_lines"],1):
            if not lines[n-1].startswith(f"（{j}）"):
                raise ValueError("Missing numbered author reasoning")
            steps.append((j,n,lines[n-1]))
        if len(steps)!=len(c["method_topics"]):
            raise ValueError("Method topics no longer match author step count")
        if c["book_outcome_label"]!="author_book_success_default" or c["author_explicit_error_admission"]:
            raise ValueError("Unapproved change to book-outcome default")
        for n in c["author_judgment_lines"]+c["validation_information_lines"]:
            if not c["source_case_span"][0]<=n<=c["source_case_span"][1]:
                raise ValueError("Judgment or feedback is from a different case")
        question=extract(lines,*c["initial_question_lines"])
        if i==3:
            question=lines[119].split("卢请",1)[0]
        valid.append((c,cells,steps,question))
    return lines,methods,valid

def retroactively_sync_health_book_validation(db):
    """Update all six old health events in place without splitting/replacing any story.

    Old intermediate disclosures and later evidence become one same-event book
    validation collection. Existing source words and original 29 author steps
    are never modified or removed.
    """
    index=json.loads(HEALTH_INDEX.read_text(encoding="utf-8"))
    cases=index["cases"]
    if len(cases)!=6:
        raise ValueError("Expected all six prior health case families")
    row=db.execute("""SELECT original_text FROM sections
        WHERE book_id='shenqi' AND section_key='health_prediction_ch01'
        ORDER BY content_version DESC LIMIT 1""").fetchone()
    if row is None:
        raise ValueError("Health chapter original missing in this private DB")
    raw=row[0].encode("utf-8")
    if hashlib.sha256(raw).hexdigest()!=HEALTH_SHA:
        raise ValueError("Health original has unexpected hash")
    lines=raw.decode("utf-8").splitlines()
    updated=0
    for c in cases:
        cid=c["event_family_id"]
        verdict=db.execute("""SELECT verdict,independent_external_verification
            FROM historical_case_book_verdicts WHERE event_family_id=?""",(cid,)).fetchone()
        if verdict is None:
            raise ValueError("Health case book verdict missing; run original verdict migration first")
        if verdict[0]=="author_book_error_explicit":
            continue
        if verdict[0]!="author_book_success_default":
            raise ValueError("Unrecognized earlier health verdict")
        feedback=set(c.get("feedback_lines",[]))
        for item in c.get("progressive_disclosures",[])+c.get("disclosure",{}).get("line_events",[]):
            feedback.update(range(item["lines"][0],item["lines"][1]+1))
        # An earlier quoted birth-year fact is validation in the one-shot book reading.
        for n in sorted(feedback):
            excerpt=extract(lines,n,n)
            old=db.execute("""SELECT original_statement FROM historical_case_disclosures
                WHERE case_id=? AND source_line=?""",(cid,n)).fetchone()
            if old is not None and old[0]!=excerpt:
                raise ValueError("Old health feedback source words changed")
            if old is None:
                db.execute("""INSERT INTO historical_case_disclosures
                    (case_id,source_line,phase,fact_type,original_statement)
                    VALUES (?,?,'same_event_book_validation','validation_information',?)""",
                    (cid,n,excerpt))
            else:
                db.execute("""UPDATE historical_case_disclosures
                     SET phase='same_event_book_validation',fact_type='validation_information'
                     WHERE case_id=? AND source_line=?""",(cid,n))
        db.execute("""UPDATE historical_case_book_verdicts
            SET feedback_source_lines_json=?,app_output_protocol='single_answer_for_one_cast'
            WHERE event_family_id=?""",(canon(sorted(feedback)),cid))
        old=db.execute("""SELECT metadata_json FROM historical_case_protocol WHERE case_id=?""",
                       (cid,)).fetchone()
        if old is None:raise ValueError("Health source case protocol missing")
        metadata=json.loads(old[0])
        metadata.update({"book_outcome_label":"author_book_success_default",
            "app_delivery_protocol":"single_answer_for_one_cast",
            "later_disclosures_role":"same_event_book_validation_information",
            "independent_external_verification":"not_verified",
            "individual_steps_not_independent_cases":True})
        db.execute("""UPDATE historical_case_protocol SET metadata_json=? WHERE case_id=?""",
                   (canon(metadata),cid))
        updated+=1
    return updated

def import_pregnancy_chapter(db_path,source_file,*,retrofit_health=True):
    """Run strict source validation first; append a new chapter into existing local DB.

    Do not force history's author statements into live prenatal diagnosis.
    """
    raw=Path(source_file).read_bytes()
    lines,methods,cases=validate_pregnancy_source(raw)
    # Will not erase existing original section. Returning users can rerun safely.
    import_section(db_path,"shenqi",KEY,TITLE,raw.decode("utf-8"))
    initialize(db_path)
    with connect(db_path) as db:
        section=db.execute("""SELECT section_id FROM sections WHERE book_id='shenqi'
             AND section_key=? AND sha256=?""",(KEY,SHA)).fetchone()
        if section is None:raise ValueError("New section missing")
        section_id=section[0]
        old=db.execute("SELECT source_sha256 FROM chapter_knowledge WHERE chapter_key=?",
                       (CHAPTER,)).fetchone()
        if old is None:
            db.execute("""INSERT INTO chapter_knowledge
              (chapter_key,book_id,title,source_sha256,source_length_bytes,knowledge_version,review_status)
              VALUES (?,'shenqi',?,?,?,'1','draft')""",(CHAPTER,TITLE,SHA,len(raw)))
        elif old[0]!=SHA:
            raise ValueError("Source chapter conflict")
        # All 24 source method abstractions keep their provenance in local SQL.
        for m in methods["methods"]:
            key=m["concept_id"];n=m["source_line"]
            original=extract(lines,n,n)
            prior=db.execute("""SELECT original_excerpt FROM semantic_assertions
                 WHERE chapter_key=? AND concept_id=? AND source_start_line=?""",
                 (CHAPTER,key,n)).fetchone()
            if prior is None:
                db.execute("""INSERT INTO semantic_assertions
                  (chapter_key,concept_id,kind,relation,source_start_line,source_end_line,
                   metadata_json,original_excerpt,review_status)
                  VALUES (?,?,'pregnancy_method','source_provenance_only',?,?,?,?,'draft')""",
                  (CHAPTER,key,n,n,canon(m),original))
            elif prior[0]!=original:raise ValueError("Original method line changed")
        for c,cells,steps,known in cases:
            cid=c["event_family_id"]
            author="\n".join(x[2] for x in steps)
            prediction="\n".join(extract(lines,n,n) for n in c["author_judgment_lines"])
            feedback="\n".join(extract(lines,n,n) for n in c["validation_information_lines"])
            wanted=(section_id,cid,"pregnancy",known,author,prediction,feedback)
            old=db.execute("""SELECT section_id,event_family_id,domain_id,known_before,
                author_yongshen_steps,author_judgment,later_feedback
                FROM cases WHERE case_id=?""",(cid,)).fetchone()
            if old is None:
                db.execute("""INSERT INTO cases(case_id,section_id,event_family_id,domain_id,
                    known_before,author_yongshen_steps,author_judgment,later_feedback,reviewed)
                    VALUES (?,?,?,?,?,?,?,?,0)""",(cid,*wanted))
            elif old[:3]!=wanted[:3] or old[3]!=known or old[4]!=author or old[6]!=feedback:
                raise ValueError("Previously imported whole case original has changed")
            old=db.execute("""SELECT case_source_sha256 FROM historical_case_protocol WHERE case_id=?""",
                           (cid,)).fetchone()
            if old is None:
                db.execute("""INSERT INTO historical_case_protocol
                   (case_id,completeness,published_chart_verification,
                    feedback_independently_verified,eligible_blind_test,case_source_sha256,metadata_json)
                   VALUES (?,'complete_source_chart_one_cast','user_transcribed_not_independently_cast',
                    0,0,?,?)""",(cid,SHA,canon(c)))
            elif old[0]!=SHA:
                raise ValueError("Historical case source changed")
            for p,n,label,deity,door,star in cells:
                old=db.execute("""SELECT source_line,palace_label_raw,deity_raw,
                   door_position_raw,star_position_raw FROM historical_chart_cells
                   WHERE case_id=? AND palace=?""",(cid,p)).fetchone()
                wanted=(n,label,deity,door,star)
                if old is None:
                    db.execute("""INSERT INTO historical_chart_cells
                      (case_id,palace,source_line,palace_label_raw,deity_raw,door_position_raw,star_position_raw)
                      VALUES (?,?,?,?,?,?,?)""",(cid,p,*wanted))
                elif old!=wanted:raise ValueError("Original pregnancy source cell changed")
            for (j,n,original),topic in zip(steps,c["method_topics"]):
                old=db.execute("""SELECT source_line,author_analysis_original
                    FROM historical_case_reasoning WHERE case_id=? AND step_number=?""",
                    (cid,j)).fetchone()
                if old is None:
                    db.execute("""INSERT INTO historical_case_reasoning
                      (case_id,step_number,source_line,author_analysis_original,
                       short_method_topic,metadata_json) VALUES (?,?,?,?,?,?)""",
                       (cid,j,n,original,topic,canon({"one_shot":True,
                        "source_research_only":True,"book_outcome_label":c["book_outcome_label"]})))
                elif old!=(n,original):
                    raise ValueError("Numbered author original changed")
            for n in c["validation_information_lines"]:
                original=extract(lines,n,n)
                old=db.execute("""SELECT original_statement FROM historical_case_disclosures
                    WHERE case_id=? AND source_line=?""",(cid,n)).fetchone()
                if old is None:
                    db.execute("""INSERT INTO historical_case_disclosures
                    (case_id,source_line,phase,fact_type,original_statement)
                    VALUES (?,?,'same_event_book_validation','validation_information',?)""",
                    (cid,n,original))
                elif old[0]!=original:raise ValueError("Feedback original changed")
            if c["case_number"] in (4,5):
                n=206 if c["case_number"]==4 else 253
                original=extract(lines,n,n)
                old=db.execute("""SELECT original_statement FROM historical_case_disclosures
                    WHERE case_id=? AND source_line=?""",(cid,n)).fetchone()
                if old is None:
                    db.execute("""INSERT INTO historical_case_disclosures
                    (case_id,source_line,phase,fact_type,original_statement)
                    VALUES (?,?,'source_editor_annotation','source_provenance_not_case_failure',?)""",
                    (cid,n,original))
                elif old[0]!=original:raise ValueError("Editor source note changed")
            verdict=db.execute("""SELECT verdict FROM historical_case_book_verdicts
                WHERE event_family_id=?""",(cid,)).fetchone()
            if verdict is None:
                db.execute("""INSERT INTO historical_case_book_verdicts
                (event_family_id,primary_case_id,verdict,explicit_source_correction,
                 source_correction_lines_json,feedback_source_lines_json,
                 independent_external_verification,app_output_protocol,evidence_review_status,note)
                VALUES (?,?,'author_book_success_default',0,'[]',?,
                 'not_verified','single_answer_for_one_cast','book_source_only',?)""",
                 (cid,cid,canon(c["validation_information_lines"]),
                  "User default book success; uncertainty/editor corrections preserved as provenance"))
            elif verdict[0]!="author_book_success_default":
                raise ValueError("Existing corrected book outcome cannot be silently overwritten")
        previous_health=retroactively_sync_health_book_validation(db) if retrofit_health else 0
        count=db.execute("SELECT count(*) FROM cases WHERE section_id=?",(section_id,)).fetchone()[0]
        charts=db.execute("""SELECT count(*) FROM historical_chart_cells
            WHERE case_id IN (SELECT case_id FROM cases WHERE section_id=?)""",(section_id,)).fetchone()[0]
        steps_count=db.execute("""SELECT count(*) FROM historical_case_reasoning
            WHERE case_id IN (SELECT case_id FROM cases WHERE section_id=?)""",(section_id,)).fetchone()[0]
        methods_count=db.execute("SELECT count(*) FROM semantic_assertions WHERE chapter_key=?",
                                (CHAPTER,)).fetchone()[0]
    return {"status":"source_research_only_one_shot",
            "source_sha256":SHA,"case_families":count,"literal_chart_rows":charts,
            "author_reasoning_steps":steps_count,"source_method_items":methods_count,
            "health_families_retroactively_updated":previous_health,
            "book_success_defaults":count,"external_validation":0}
