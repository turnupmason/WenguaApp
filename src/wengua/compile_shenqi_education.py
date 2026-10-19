"""Source-exact local importer for Shenqi fourth predictive topic: education/exams.

Five inseparable book cases; five whole historical charts, 17 author step ranges,
35 source-linked research methods. Source prose is private local SQLite only.
Case 5 recounts future outcome BEFORE retrospective chart commentary: never
include lines 268-280 in the initial question at 264.
"""
from __future__ import annotations
import hashlib,json
from pathlib import Path
from .database import ROOT,connect,initialize,import_section

SHA="88d641e3b2ba541e5ea2acce40cd73af28c362befbff7cbc39fb558f3d84eb43"
KEY="education_prediction_ch04"
CHAPTER="shenqi/education_prediction_ch04/v1"
TITLE="求学考试预测"
INDEX=ROOT/"data/knowledge/shenqi/education_prediction_ch04"
PALACES={"坎一宫":1,"坤二宫":2,"震三宫":3,"巽四宫":4,"中五宫":5,
         "乾六宫":6,"兑七宫":7,"艮八宫":8,"离九宫":9}
NUMBERS="一二三四五"

def canon(x):
    return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":"))

def span(lines,loc):
    a,b=loc
    if type(a) is not int or type(b) is not int or not 1<=a<=b<=len(lines):
        raise ValueError("Invalid education source line reference")
    return "\n".join(lines[a-1:b])

def prepare_source(raw):
    if hashlib.sha256(raw).hexdigest()!=SHA:
        raise ValueError("Education source SHA256 mismatch; no DB mutation")
    lines=raw.decode("utf-8").splitlines()
    if len(lines)!=349 or lines[1]!="第四章 求学考试预测" or not lines[21].startswith("第二节 实例解析（5例）"):
        raise ValueError("Unexpected education source version or incomplete chapter")
    cases=json.loads((INDEX/"case_index.json").read_text(encoding="utf-8"))
    methods=json.loads((INDEX/"method_index.json").read_text(encoding="utf-8"))
    manifest=json.loads((INDEX/"chapter_manifest.json").read_text(encoding="utf-8"))
    if any(obj["source_sha256"]!=SHA for obj in (cases,methods,manifest)):
        raise ValueError("Public source manifest hash disagrees with original text")
    if (manifest["source_lines"],manifest["source_utf8_bytes"])!=(349,len(raw)):
        raise ValueError("Public manifest does not identify exact original")
    if len(cases["cases"])!=5 or sum(len(x["author_analysis_numbered_lines"]) for x in cases["cases"])!=17:
        raise ValueError("Expected 5 entire book event families and 17 numbered explanations")
    if len(methods["methods"])!=35 or len({m["concept_id"] for m in methods["methods"]})!=35:
        raise ValueError("Expected all 35 education method concept identifiers")
    records=[]
    for index,case in enumerate(cases["cases"],1):
        if case["index"]!=index or not lines[case["source_lines"][0]-1].startswith("实例"+NUMBERS[index-1]):
            raise ValueError("Book event family header mismatch")
        cid=case["event_family_id"]
        if cid!=case["case_id"] or case["book_outcome_label"]!="author_book_success_default":
            raise ValueError("Unexpected new case ID or source book verdict")
        start,end=case["original_nine_palace_row_lines"]
        if end-start!=8:
            raise ValueError("Full 9-row book chart required")
        cells=[]
        for n in range(start,end+1):
            original=lines[n-1].split()
            if len(original)!=4 or original[0] not in PALACES:
                raise ValueError("Invalid original nine-palace literal row")
            cells.append((PALACES[original[0]],n,*original))
        if sorted(r[0] for r in cells)!=list(range(1,10)):
            raise ValueError("Original chart has missing/duplicated palace")
        step_ranges=case["author_full_analysis_ranges"]
        if len(step_ranges)!=len(case["author_analysis_numbered_lines"]) or len(step_ranges)!=len(case["reasoning_topics"]):
            raise ValueError("Numbered source steps/method topics not aligned")
        steps=[]
        for j,(first,last) in enumerate(step_ranges,1):
            if first!=case["author_analysis_numbered_lines"][j-1]:
                raise ValueError("Case number-to-range mismatch")
            raw_step=span(lines,[first,last])
            if not lines[first-1].startswith(f"（{j}）"):
                raise ValueError("Missing numbered author step")
            steps.append((j,first,last,raw_step,case["reasoning_topics"][j-1]))
        initial=span(lines,case["original_question_source_lines"])
        if index==5:
            # The account's chart summary is at 284, but all intervening
            # October outcomes belong to book validation, not initial facts.
            if case["original_question_source_lines"]!=[264,264]:
                raise ValueError("Case5 initial question must stop before reported outcomes")
            if case["retrospective_cast_source_lines"]!=[284,284]:
                raise ValueError("Case5 cast metadata is retrospective and separate")
            if "10月9日" in initial or "10月7号" in initial:
                raise ValueError("October future feedback leaked into prior question")
            if step_ranges[-1]!=[345,349]:
                raise ValueError("Final multi-paragraph author analysis incomplete")
        for n in case["author_predicted_or_interpreted_source_lines"]+case["book_validation_lines"]:
            if not case["source_lines"][0]<=n<=case["source_lines"][1]:
                raise ValueError("Source judgment/feedback crosses into another case")
        records.append((case,cells,steps,initial))
    for method in methods["methods"]:
        if not method["concept_id"].startswith("education:method:"):
            raise ValueError("Nonuniform cross-chapter concept ID")
        n=method["source_line"]
        span(lines,[n,n])
    return lines,methods,records

def import_education_chapter(db_path,source_file):
    raw=Path(source_file).read_bytes()
    lines,methods,records=prepare_source(raw)  # verify BEFORE touching DB
    import_section(db_path,"shenqi",KEY,TITLE,raw.decode("utf-8"))
    initialize(db_path)
    with connect(db_path) as db:
        section=db.execute("""SELECT section_id FROM sections WHERE book_id='shenqi'
            AND section_key=? AND sha256=?""",(KEY,SHA)).fetchone()
        if section is None:raise ValueError("Exact original section not imported")
        section_id=section[0]
        old=db.execute("SELECT source_sha256 FROM chapter_knowledge WHERE chapter_key=?",(CHAPTER,)).fetchone()
        if old is None:
            db.execute("""INSERT INTO chapter_knowledge
                (chapter_key,book_id,title,source_sha256,source_length_bytes,knowledge_version,review_status)
                VALUES (?,'shenqi',?,?,?,'1','draft')""",(CHAPTER,TITLE,SHA,len(raw)))
        elif old[0]!=SHA:
            raise ValueError("Chapter version conflict; never silently reset source")
        for method in methods["methods"]:
            n=method["source_line"]
            key=method["concept_id"]
            original=span(lines,[n,n])
            old=db.execute("""SELECT original_excerpt FROM semantic_assertions
                 WHERE chapter_key=? AND concept_id=? AND source_start_line=?""",
                 (CHAPTER,key,n)).fetchone()
            if old is None:
                db.execute("""INSERT INTO semantic_assertions
                    (chapter_key,concept_id,kind,relation,source_start_line,source_end_line,
                     metadata_json,original_excerpt,review_status)
                    VALUES (?,?,'education_domain_method','cross_chapter_evidence_candidate',
                       ?,?,?,?,'draft')""",(CHAPTER,key,n,n,canon(method),original))
            elif old[0]!=original:
                raise ValueError("Previously saved source excerpt changed")
        for case,cells,steps,prior in records:
            cid=case["case_id"]
            reasoning="\n\n".join(s[3] for s in steps)
            prediction="\n".join(span(lines,[n,n]) for n in case["author_predicted_or_interpreted_source_lines"])
            validation="\n".join(span(lines,[n,n]) for n in case["book_validation_lines"]
                                  if n!=276)
            original=(section_id,cid,"education",prior,reasoning,prediction,validation)
            old=db.execute("""SELECT section_id,event_family_id,domain_id,known_before,
               author_yongshen_steps,author_judgment,later_feedback FROM cases WHERE case_id=?""",
               (cid,)).fetchone()
            if old is None:
                db.execute("""INSERT INTO cases
                   (case_id,section_id,event_family_id,domain_id,known_before,
                    author_yongshen_steps,author_judgment,later_feedback,reviewed)
                   VALUES (?,?,?,?,?,?,?,?,0)""",(cid,*original))
            elif old!=original:
                raise ValueError("Previously imported book case has source text mismatch")
            previous=db.execute("SELECT case_source_sha256 FROM historical_case_protocol WHERE case_id=?",(cid,)).fetchone()
            if previous is None:
                db.execute("""INSERT INTO historical_case_protocol
                   (case_id,completeness,published_chart_verification,
                    feedback_independently_verified,eligible_blind_test,case_source_sha256,metadata_json)
                   VALUES (?,'one_source_event_chart_complete',
                    'user_book_transcription_not_independently_recast',0,0,?,?)""",
                    (cid,SHA,canon(case)))
            elif previous[0]!=SHA:
                raise ValueError("Existing case source SHA changed")
            for palace,n,name,deity,door,star in cells:
                old=db.execute("""SELECT source_line,palace_label_raw,deity_raw,door_position_raw,
                    star_position_raw FROM historical_chart_cells WHERE case_id=? AND palace=?""",
                    (cid,palace)).fetchone()
                row=(n,name,deity,door,star)
                if old is None:
                    db.execute("""INSERT INTO historical_chart_cells
                       (case_id,palace,source_line,palace_label_raw,deity_raw,
                        door_position_raw,star_position_raw)
                       VALUES (?,?,?,?,?,?,?)""",(cid,palace,*row))
                elif old!=row:raise ValueError("Literal book chart overwritten or changed")
            for j,start,end,txt,topic in steps:
                old=db.execute("""SELECT source_line,author_analysis_original FROM historical_case_reasoning
                     WHERE case_id=? AND step_number=?""",(cid,j)).fetchone()
                if old is None:
                    db.execute("""INSERT INTO historical_case_reasoning
                     (case_id,step_number,source_line,author_analysis_original,
                      short_method_topic,metadata_json) VALUES (?,?,?,?,?,?)""",
                      (cid,j,start,txt,topic,canon({"source_line_span":[start,end],
                       "author_book_success_default":True,"one_shot_source_study":True})))
                elif old!=(start,txt):
                    raise ValueError("Original author step or multi-paragraph source changed")
            for n in case["book_validation_lines"]:
                statement=span(lines,[n,n])
                phase="same_event_followup" if n==276 else "same_event_book_validation"
                kind="author_reaffirmation_not_new_prediction" if n==276 else "validation_information"
                old=db.execute("""SELECT original_statement FROM historical_case_disclosures
                    WHERE case_id=? AND source_line=?""",(cid,n)).fetchone()
                if old is None:
                    db.execute("""INSERT INTO historical_case_disclosures
                       (case_id,source_line,phase,fact_type,original_statement)
                       VALUES (?,?,?,?,?)""",(cid,n,phase,kind,statement))
                elif old[0]!=statement:
                    raise ValueError("Previously saved after-case material changed")
            verdict=db.execute("SELECT verdict FROM historical_case_book_verdicts WHERE event_family_id=?",(cid,)).fetchone()
            if verdict is None:
                db.execute("""INSERT INTO historical_case_book_verdicts
                    (event_family_id,primary_case_id,verdict,explicit_source_correction,
                     source_correction_lines_json,feedback_source_lines_json,
                     independent_external_verification,app_output_protocol,evidence_review_status,note)
                    VALUES (?,?,'author_book_success_default',0,'[]',?,
                     'not_verified','single_answer_for_one_cast','book_source_only',?)""",
                    (cid,cid,canon(case["book_validation_lines"]),
                     "Book-success default per user; do not split one event into feedback turns"))
            elif verdict[0]!="author_book_success_default":
                raise ValueError("Existing explicitly corrected verdict requires review")
        result={}
        for table in ("cases","historical_chart_cells","historical_case_reasoning"):
            predicate=("section_id=?" if table=="cases" else
                "case_id IN (SELECT case_id FROM cases WHERE section_id=?)")
            result[table]=db.execute(f"SELECT count(*) FROM {table} WHERE {predicate}",
                (section_id,)).fetchone()[0]
        result["semantic_assertions"]=db.execute("SELECT count(*) FROM semantic_assertions WHERE chapter_key=?",
            (CHAPTER,)).fetchone()[0]
    return {"chapter":CHAPTER,"source_sha256":SHA,"one_shot_cases":result["cases"],
        "source_palace_rows":result["historical_chart_cells"],
        "full_author_analysis_steps":result["historical_case_reasoning"],
        "domain_method_records":result["semantic_assertions"],
        "book_outcome_labels":"default_success_not_external_validation"}
