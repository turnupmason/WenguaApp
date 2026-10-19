"""Append one complete marriage-question chapter with six whole source families.

Each case is ONE event + ONE supplied source chart + ONE full author analysis.
Per user policy, book verdict defaults to author-book success unless the
author EXPLICITLY reports an error and correction. Later reports are book
validation within the same family. This is not independent real-life proof.
All original text remains in user's local SQLite, never public GitHub.
"""
from __future__ import annotations
import hashlib,json
from pathlib import Path
from .database import ROOT,connect,initialize,import_section

SHA="64c7e9c1c0e646814c11644809277f71587d21736bdbd49679e6ad65611303c9"
KEY="marriage_prediction_ch02"
CHAPTER=f"shenqi/{KEY}/v1"
TITLE="恋爱婚姻预测"
DATA=ROOT/"data/knowledge/shenqi/marriage_prediction_ch02"
PALACES={"坎一宫":1,"坤二宫":2,"震三宫":3,"巽四宫":4,"中五宫":5,
         "乾六宫":6,"兑七宫":7,"艮八宫":8,"离九宫":9}
NUMBERS="一二三四五六"

def _canon(x):
    return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":"))

def _span(lines,at):
    a,b=at
    if type(a)!=int or type(b)!=int or not 1<=a<=b<=len(lines):
        raise ValueError("Source line span outside chapter")
    return "\n".join(lines[a-1:b])

def _prepare(raw):
    if hashlib.sha256(raw).hexdigest()!=SHA:
        raise ValueError("Marriage chapter exact source SHA256 mismatch")
    lines=raw.decode("utf-8").splitlines()
    if len(lines)!=367 or lines[0].strip()!="第二章 恋爱婚姻预测" or not lines[14].startswith("第二节 实例解析（6例）"):
        raise ValueError("Wrong marriage chapter or incomplete source boundary")
    index=json.loads((DATA/"case_index.json").read_text(encoding="utf-8"))
    method=json.loads((DATA/"method_index.json").read_text(encoding="utf-8"))
    if index["source_sha256"]!=SHA or method["source_sha256"]!=SHA:
        raise ValueError("Index/version hash disagrees with raw source")
    cases=index["cases"]
    if len(cases)!=6 or len({c["event_family_id"] for c in cases})!=6:
        raise ValueError("Need six source event families")
    if sum(len(c["author_numbered_step_lines"]) for c in cases)!=23:
        raise ValueError("All 23 numbered author steps required")
    if len(method["author_method_candidates"])!=18:
        raise ValueError("Chapter methods drift from reviewed public structure")
    parsed=[]
    for c in sorted(cases,key=lambda x:x["case_number"]):
        i=c["case_number"]
        if i not in range(1,7) or not lines[c["source_case_span"][0]-1].startswith("实例"+NUMBERS[i-1]):
            raise ValueError("Case family header mismatch")
        if c["book_outcome_label"]!="author_book_success_default" or c["book_explicit_failure_or_correction"] is not False:
            raise ValueError("Book default policy changed; explicit author error must be separately sourced")
        a,b=c["source_nine_palace_table_span"]
        if b-a!=8:raise ValueError("Exactly nine literal palace rows per case")
        cells=[]
        for n in range(a,b+1):
            cols=lines[n-1].split()
            if len(cols)!=4 or cols[0] not in PALACES:
                raise ValueError(f"Invalid source chart cell line {n}, never reconstruct missing cell")
            cells.append((PALACES[cols[0]],n,*cols))
        if sorted(x[0] for x in cells)!=list(range(1,10)):
            raise ValueError("Incomplete or duplicated source nine-palace chart")
        steps=[]
        for stepno,at in enumerate(c["author_numbered_step_lines"],start=1):
            if not lines[at-1].startswith(f"（{stepno}）"):
                raise ValueError("Numbered author reasoning step missing")
            steps.append((stepno,at,lines[at-1]))
        predictions=[_span(lines,[p,p]) for p in c["author_judgment_source_lines"]]
        feedback=[(p,lines[p-1]) for p in c["author_book_feedback_lines"]]
        # Case 3 is an unsolicited reading whose source narration already
        # quotes predictions and answers before the chart; only the very first
        # question context is eligible for the initial source-only view.
        # Case 6's 1997 inquiry has no chart; the actual chart is from 1998.
        safe_context=([134,134] if i==3 else [319,320] if i==6 else c["question_context_span"])
        parsed.append((c,cells,steps,predictions,feedback,_span(lines,safe_context)))
    return lines,method,parsed

def import_marriage_chapter(db_path,source_file):
    raw=Path(source_file).read_bytes()
    lines,method,events=_prepare(raw) # full validation before writing
    import_section(db_path,"shenqi",KEY,TITLE,raw.decode("utf-8"))
    initialize(db_path)
    with connect(db_path) as db:
        section=db.execute("""SELECT section_id FROM sections WHERE book_id='shenqi'
            AND section_key=? AND sha256=?""",(KEY,SHA)).fetchone()
        if not section:raise ValueError("Section import failed")
        section_id=section[0]
        chapter=db.execute("SELECT source_sha256 FROM chapter_knowledge WHERE chapter_key=?",(CHAPTER,)).fetchone()
        if chapter is None:
            db.execute("""INSERT INTO chapter_knowledge
                (chapter_key,book_id,title,source_sha256,source_length_bytes,knowledge_version,review_status)
                VALUES (?,?,?,?,?,'1','draft')""",(CHAPTER,"shenqi",TITLE,SHA,len(raw)))
        elif chapter[0]!=SHA:raise ValueError("Chapter source conflict: do not overwrite")
        for rule in method["author_method_candidates"]:
            cid=rule["concept_id"];line=rule["source_line"]
            full=(rule["review_status"],_canon(rule),lines[line-1])
            old=db.execute("""SELECT review_status,metadata_json,original_excerpt
                FROM semantic_assertions WHERE chapter_key=? AND concept_id=?
                AND source_start_line=?""",(CHAPTER,cid,line)).fetchone()
            if old is None:
                db.execute("""INSERT INTO semantic_assertions
                    (chapter_key,concept_id,kind,relation,source_start_line,
                     source_end_line,metadata_json,original_excerpt,review_status)
                    VALUES (?,?,'marriage_method','one_shot_source_domain_method',?,?,?,?,'draft')""",
                    (CHAPTER,cid,line,line,_canon(rule),lines[line-1]))
            elif old[1:]!=full[1:] or old[0]!="draft":
                raise ValueError("Source method already exists with different content")
        for c,cells,steps,preds,feedback,known in events:
            cid=c["case_id"]
            source_steps="\n".join(x[2] for x in steps)
            judgment="\n".join(preds)
            post="\n".join(x[1] for x in feedback)
            record=(section_id,cid,"marriage",known,source_steps,judgment,post)
            old=db.execute("""SELECT section_id,event_family_id,domain_id,known_before,
                author_yongshen_steps,author_judgment,later_feedback
                FROM cases WHERE case_id=?""",(cid,)).fetchone()
            if old is None:
                db.execute("""INSERT INTO cases
                    (case_id,section_id,event_family_id,domain_id,known_before,
                     author_yongshen_steps,author_judgment,later_feedback,reviewed)
                    VALUES (?,?,?,?,?,?,?,?,0)""",(cid,*record))
            elif old!=record:raise ValueError("Case source differs; no overwrite")
            protocol=("one_story_one_source_chart_original_text","user_rearranged_book_chart_not_independent_cast",
                      0,0,SHA,_canon(c))
            old=db.execute("""SELECT completeness,published_chart_verification,
                feedback_independently_verified,eligible_blind_test,case_source_sha256,
                metadata_json FROM historical_case_protocol WHERE case_id=?""",(cid,)).fetchone()
            if old is None:
                db.execute("""INSERT INTO historical_case_protocol
                    (case_id,completeness,published_chart_verification,
                     feedback_independently_verified,eligible_blind_test,case_source_sha256,metadata_json)
                    VALUES (?,?,?,?,?,?,?)""",(cid,*protocol))
            elif old!=protocol:raise ValueError("Protocol mismatch")
            for p,n,label,deity,door,star in cells:
                wanted=(n,label,deity,door,star)
                old=db.execute("""SELECT source_line,palace_label_raw,deity_raw,
                       door_position_raw,star_position_raw
                       FROM historical_chart_cells WHERE case_id=? AND palace=?""",(cid,p)).fetchone()
                if old is None:
                    db.execute("""INSERT INTO historical_chart_cells
                        (case_id,palace,source_line,palace_label_raw,deity_raw,
                         door_position_raw,star_position_raw)
                         VALUES (?,?,?,?,?,?,?)""",(cid,p,*wanted))
                elif old!=wanted:raise ValueError("Original source chart cell changed")
            for step,n,txt in steps:
                topic=c["method_key_points"][step-1]
                metadata=_canon({"one_event_one_chart":True,"book_outcome_label":c["book_outcome_label"],
                                 "explanation_scope":"original_author_source","event_family_id":cid})
                old=db.execute("""SELECT source_line,author_analysis_original,short_method_topic,
                    metadata_json FROM historical_case_reasoning WHERE case_id=? AND step_number=?""",
                    (cid,step)).fetchone()
                wanted=(n,txt,topic,metadata)
                if old is None:
                    db.execute("""INSERT INTO historical_case_reasoning
                        (case_id,step_number,source_line,author_analysis_original,short_method_topic,
                         metadata_json) VALUES (?,?,?,?,?,?)""",(cid,step,*wanted))
                elif old!=wanted:raise ValueError("Numbered author step changed")
            for n,statement in feedback:
                old=db.execute("""SELECT phase,fact_type,original_statement
                    FROM historical_case_disclosures WHERE case_id=? AND source_line=?""",
                    (cid,n)).fetchone()
                wanted=("same_event_book_validation","validation_information",statement)
                if old is None:
                    db.execute("""INSERT INTO historical_case_disclosures
                        (case_id,source_line,phase,fact_type,original_statement)
                        VALUES (?,?,?,?,?)""",(cid,n,*wanted))
                elif old!=wanted:raise ValueError("Book validation text changed")
            label=(cid,c["book_outcome_label"],0,"[]",
                   _canon(c["author_book_feedback_lines"]),"not_verified",
                   "single_answer_for_one_cast","book_source_only",
                   "User policy: author-book verdict defaults correct absent explicit author correction")
            previous=db.execute("""SELECT primary_case_id,verdict,explicit_source_correction,
                source_correction_lines_json,feedback_source_lines_json,
                independent_external_verification,app_output_protocol,
                evidence_review_status,note
                FROM historical_case_book_verdicts WHERE event_family_id=?""",(cid,)).fetchone()
            if previous is None:
                db.execute("""INSERT INTO historical_case_book_verdicts
                    (event_family_id,primary_case_id,verdict,explicit_source_correction,
                     source_correction_lines_json,feedback_source_lines_json,
                     independent_external_verification,app_output_protocol,
                     evidence_review_status,note)
                    VALUES (?,?,?,?,?,?,?,?,?,?)""",(cid,*label))
            elif previous!=label:raise ValueError("Prior book outcome has changed")
        n=db.execute("SELECT count(*) FROM cases WHERE section_id=?",(section_id,)).fetchone()[0]
        chart=db.execute("""SELECT count(*) FROM historical_chart_cells WHERE case_id
                        IN (SELECT case_id FROM cases WHERE section_id=?)""",(section_id,)).fetchone()[0]
        steps=db.execute("""SELECT count(*) FROM historical_case_reasoning WHERE case_id
                        IN (SELECT case_id FROM cases WHERE section_id=?)""",(section_id,)).fetchone()[0]
    return {"source_sha256":SHA,"new_chapter_case_families":n,"literal_chart_cells":chart,
            "original_author_numbered_steps":steps,"book_verdict_default_success":n,
            "externally_verified":0,"one_shot_protocol":True,"status":"source_research_private_import_draft"}
