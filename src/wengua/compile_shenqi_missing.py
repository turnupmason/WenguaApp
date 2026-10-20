"""Add one original Shenqi missing-person chapter without replacing any earlier event.

10 whole stories, 11 genuinely printed source charts, 54 numbered steps.
Source book is private, with line-based public metadata. Three explicit
original-judgment failures stay as NEGATIVE evidence, with later corrections.
These historical techniques are NOT reliable missing-person safety assessment.
"""
from __future__ import annotations
import hashlib,json,re
from pathlib import Path
from .database import ROOT,connect,initialize,import_section

SHA="5eca2a1a0914691ec439040a9b538fb8e4385fa5cf8ac5286bc5ae86d25b6574"
KEY="missing_person_prediction_ch08"
CHAPTER="shenqi/missing_person_prediction_ch08/v1"
INDEX=ROOT/"data/knowledge/shenqi/missing_person_prediction_ch08"
PAL={"巽四宫":4,"离九宫":9,"坤二宫":2,"震三宫":3,"中五宫":5,"兑七宫":7,"艮八宫":8,"坎一宫":1,"乾六宫":6}
def canon(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":"))
def span(lines,a,b=None):
    if b is None:b=a
    if not 1<=a<=b<=len(lines):raise ValueError("Source line out of range")
    return "\n".join(lines[a-1:b])
def chart(lines,start):
    """Use EXACT printed three 3-column panels: offsets +1,+6,+11.

    A single physical row represents three palaces. The SQLite schema
    requires a unique source_line per palace: three adjacent panel lines
    anchor each palace; source paragraph itself is stored fully as original.
    """
    if not lines[start-1].startswith("┌"):
        raise ValueError("Missing actual nine-palace source chart")
    data=[]
    for offset in (1,6,11):
        rows=[]
        for n in range(start+offset,start+offset+4):
            fields=[v.strip() for v in lines[n-1].split("│")[1:-1]]
            if len(fields)!=3:raise ValueError("Incomplete three-column printed chart")
            rows.append(fields)
        for col in range(3):
            name,deity,door,star=(r[col] for r in rows)
            if name not in PAL:raise ValueError("Unknown palace name in original")
            data.append((PAL[name],start+offset+col,name,deity,door,star))
    if sorted(x[0] for x in data)!=list(range(1,10)):
        raise ValueError("Original chart lacks all nine unique palaces")
    return data
def prepare(raw):
    if hashlib.sha256(raw).hexdigest()!=SHA:
        raise ValueError("Original chapter SHA256 mismatch; DB untouched")
    lines=raw.decode("utf-8").splitlines()
    if len(lines)!=477 or lines[0]!="行人走失预测" or lines[14]!="第二节 实例解析（10例）":
        raise ValueError("Unexpected missing-person chapter source")
    metadata={n:json.loads((INDEX/(n+".json")).read_text(encoding="utf-8"))
              for n in ("chapter_manifest","case_index","method_index","source_audit")}
    if any(d["source_sha256"]!=SHA for d in metadata.values()):
        raise ValueError("Public metadata source SHA mismatch")
    m=metadata["chapter_manifest"];events=metadata["case_index"]["cases"]
    methods=metadata["method_index"]["methods"]
    if m["source_utf8_bytes"]!=len(raw) or len(events)!=10 or len(methods)!=81:
        raise ValueError("Source size, case count or method count mismatch")
    if sum(map(lambda c:len(c["original_chart_starts"]),events))!=11:
        raise ValueError("Actual 11 source charts not intact")
    if sum(map(lambda c:len(c["numbered_reasoning_lines"]),events))!=54:
        raise ValueError("Actual 54 source steps not intact")
    if len({r["concept_id"] for r in methods})!=81:
        raise ValueError("Duplicate original method concept")
    for j,c in enumerate(events,1):
        if c["case_number"]!=j or not lines[c["source_span"][0]-1].startswith("实例"):
            raise ValueError("Historical story heading is missing")
        if c["case_id"]!=c["event_family_id"]:
            raise ValueError("Do not split one event into several predictions")
        for x in c["original_chart_starts"]:chart(lines,x)
        for x in c["numbered_reasoning_lines"]:
            if not re.match(r"^\([1-9]\)",lines[x-1]):
                raise ValueError("Original numbered reasoning step missing")
        if (j in (5,9,10))!=bool(c["explicit_source_error"]):
            raise ValueError("Author explicit failures were lost")
    if "此例断错" not in lines[238] or "此例断错" not in lines[400] or "哪里判断不对" not in lines[456]:
        raise ValueError("Source's three original failures must be retained")
    if events[1]["original_chart_starts"]!=[68,104]:
        raise ValueError("Same boy two REAL different-time charts required")
    return lines,metadata

def import_missing_chapter(db_path,source_path):
    raw=Path(source_path).read_bytes()
    lines,metadata=prepare(raw)  # strictly validate before DB mutation
    initialize(db_path)
    import_section(db_path,"shenqi",KEY,"行人走失预测",raw.decode("utf-8"))
    with connect(db_path) as db:
        section=db.execute("SELECT section_id FROM sections WHERE section_key=? AND sha256=?",(KEY,SHA)).fetchone()
        if not section:raise ValueError("Exact private source missing")
        sid=section[0]
        old=db.execute("SELECT source_sha256 FROM chapter_knowledge WHERE chapter_key=?",(CHAPTER,)).fetchone()
        if old is None:
            db.execute("""INSERT INTO chapter_knowledge(chapter_key,book_id,title,source_sha256,source_length_bytes,knowledge_version,review_status)
              VALUES (?,'shenqi','行人走失预测',?,?,'1','draft')""",(CHAPTER,SHA,len(raw)))
        elif old[0]!=SHA:raise ValueError("Original chapter source differs")
        for m in metadata["method_index"]["methods"]:
            n=m["source_line"];literal=span(lines,n);cid=m["concept_id"]
            old=db.execute("""SELECT original_excerpt FROM semantic_assertions
             WHERE chapter_key=? AND concept_id=? AND source_start_line=?""",(CHAPTER,cid,n)).fetchone()
            if old is None:
                db.execute("""INSERT INTO semantic_assertions
                 (chapter_key,concept_id,kind,relation,source_start_line,source_end_line,
                  metadata_json,original_excerpt,review_status)
                  VALUES (?,?,?,?,?,?,?,?,?)""",
                  (CHAPTER,cid,"missing_"+m["category"],"conditional_source",
                   n,n,canon(m),literal,"draft"))
            elif old[0]!=literal:raise ValueError("Original source method literal changed")
        for c in metadata["case_index"]["cases"]:
            cid=c["case_id"];i=c["case_number"]
            initial=span(lines,*c["initial_question_source_lines"])
            if i==3:
                mark="4月11日其父母找到我预测"
                if mark not in initial:raise ValueError("Cannot isolate hindsight from case3")
                initial=initial.split(mark,1)[0].strip()
            full="\n\n".join(span(lines,n) for n in c["numbered_reasoning_lines"])
            pred="\n".join(span(lines,n) for n in c["original_judgment_source_lines"])
            feedback="\n".join(span(lines,n) for n in c["book_feedback_source_lines"])
            desired=(sid,cid,"missing_person",initial,full,pred,feedback)
            old=db.execute("""SELECT section_id,event_family_id,domain_id,known_before,
             author_yongshen_steps,author_judgment,later_feedback FROM cases WHERE case_id=?""",(cid,)).fetchone()
            if old is None:
                db.execute("""INSERT INTO cases(case_id,section_id,event_family_id,domain_id,
                 known_before,author_yongshen_steps,author_judgment,later_feedback,reviewed)
                 VALUES (?,?,?,?,?,?,?,?,0)""",(cid,*desired))
            elif old!=desired:raise ValueError("Historical case literal has changed")
            old=db.execute("SELECT case_source_sha256 FROM historical_case_protocol WHERE case_id=?",(cid,)).fetchone()
            if old is None:
                db.execute("""INSERT INTO historical_case_protocol
                 (case_id,completeness,published_chart_verification,feedback_independently_verified,
                  eligible_blind_test,case_source_sha256,metadata_json)
                 VALUES (?,'one_full_original_story','source_not_independently_recast',
                 0,0,?,?)""",(cid,SHA,canon(c)))
            elif old[0]!=SHA:raise ValueError("Historical case source SHA changed")
            for cell in chart(lines,c["original_chart_starts"][0]):
                old=db.execute("""SELECT source_line,palace_label_raw,deity_raw,
                 door_position_raw,star_position_raw FROM historical_chart_cells
                 WHERE case_id=? AND palace=?""",(cid,cell[0])).fetchone()
                if old is None:
                    db.execute("""INSERT INTO historical_chart_cells
                     (case_id,palace,source_line,palace_label_raw,deity_raw,
                      door_position_raw,star_position_raw,source_status)
                     VALUES (?,?,?,?,?,?,?,'original_book_literal')""",(cid,*cell))
                elif old!=cell[1:]:raise ValueError("Original palace literal differs")
            for k,n in enumerate(c["numbered_reasoning_lines"],1):
                phase=("second_genuine_disappearance_cast" if i==2 and n>=123 else
                  "incorrect_first_reading_counterexample" if (i==5 and n==237) or
                  (i==9 and n==399) or (i==10 and n<463) else
                  "teacher_correction" if i==10 and n>=463 else
                  "corrective_book_analysis" if (i==5 and n>=243) or (i==9 and n>=407)
                  else "initial_source_analysis")
                literal=span(lines,n)
                old=db.execute("""SELECT source_line,author_analysis_original
                  FROM historical_case_reasoning WHERE case_id=? AND step_number=?""",(cid,k)).fetchone()
                if old is None:
                    db.execute("""INSERT INTO historical_case_reasoning
                     (case_id,step_number,source_line,author_analysis_original,short_method_topic,metadata_json)
                     VALUES (?,?,?,?,?,?)""",(cid,k,n,literal,phase,
                      canon({"reasoning_layer":phase,"source_line":n})))
                elif old!=(n,literal):raise ValueError("Author's original full step changed")
            for n in c["book_feedback_source_lines"]:
                original=span(lines,n)
                old=db.execute("""SELECT original_statement FROM historical_case_disclosures
                  WHERE case_id=? AND source_line=?""",(cid,n)).fetchone()
                if old is None:
                    db.execute("""INSERT INTO historical_case_disclosures
                     (case_id,source_line,phase,fact_type,original_statement)
                     VALUES (?,?,'later_book_feedback','validation_information',?)""",(cid,n,original))
                elif old[0]!=original:raise ValueError("Historical book feedback changed")
            verdict=c["book_outcome_label"]
            corrections=([c["explicit_source_error"]["source_line"]] if c["explicit_source_error"] else [])
            old=db.execute("SELECT verdict FROM historical_case_book_verdicts WHERE event_family_id=?",(cid,)).fetchone()
            if old is None:
                db.execute("""INSERT INTO historical_case_book_verdicts
                  (event_family_id,primary_case_id,verdict,explicit_source_correction,
                   source_correction_lines_json,feedback_source_lines_json,
                   independent_external_verification,app_output_protocol,evidence_review_status,note)
                   VALUES (?,?,?,?,?,?,'not_verified','single_answer_for_one_cast','book_source_only',?)""",
                   (cid,cid,verdict,int(bool(corrections)),canon(corrections),
                    canon(c["book_feedback_source_lines"]),
                    "Initial author/learner forecast explicitly failed and source corrected"
                    if corrections else "Source-book default success, not outside verified"))
            elif old[0]!=verdict:raise ValueError("Book verdict changed without review")
            for rv in c["retrospective_review_segments"]:
                a,b,kind=rv["start"],rv["end"],rv["kind"];original=span(lines,a,b)
                old=db.execute("""SELECT original_text FROM historical_case_source_segments
                 WHERE case_id=? AND segment_kind=? AND source_start_line=?""",(cid,kind,a)).fetchone()
                if old is None:
                    db.execute("""INSERT INTO historical_case_source_segments
                     (case_id,segment_kind,source_start_line,source_end_line,original_text,metadata_json)
                     VALUES (?,?,?,?,?,?)""",
                     (cid,kind,a,b,original,canon({"same_event":True,"source_sha256":SHA})))
                elif old[0]!=original:raise ValueError("Book retrospective text altered")
        # Case 2: retain the true disappearance-time secondary chart in same story.
        second=metadata["case_index"]["cases"][1]["case_id"]
        key="1996_06_06_己巳_actual_disappearance"
        existing=db.execute("SELECT source_chart_start FROM historical_case_additional_casts WHERE case_id=? AND cast_key=?",(second,key)).fetchone()
        if existing is None:
            db.execute("""INSERT INTO historical_case_additional_casts
             (case_id,cast_key,cast_datetime_description,calendar_date,hour_ganzhi,source_chart_start,notes)
             VALUES (?,?,?,?,?,?,?)""",
             (second,key,"1996年6月6日10点真实走失时","1996-06-06","己巳",104,
              "Same missing child, genuine second source chart. Six later unprinted casts NOT supplied."))
        elif existing[0]!=104:raise ValueError("Genuine secondary source chart offset changed")
        for cell in chart(lines,104):
            old=db.execute("""SELECT source_line,palace_label_raw,deity_raw,
             door_position_raw,star_position_raw
             FROM historical_case_additional_cast_cells
             WHERE case_id=? AND cast_key=? AND palace=?""",(second,key,cell[0])).fetchone()
            if old is None:
                db.execute("""INSERT INTO historical_case_additional_cast_cells
                 (case_id,cast_key,palace,source_line,palace_label_raw,deity_raw,door_position_raw,star_position_raw)
                 VALUES (?,?,?,?,?,?,?,?)""",(second,key,*cell))
            elif old!=cell[1:]:raise ValueError("Second actual chart literal altered")
        def count(table,where,arg):
            return db.execute(f"SELECT count(*) FROM {table} WHERE {where}",arg).fetchone()[0]
        ans={"event_families":count("cases","section_id=?",(sid,)),
          "main_chart_cells":count("historical_chart_cells","case_id IN (SELECT case_id FROM cases WHERE section_id=?)",(sid,)),
          "source_analysis_steps":count("historical_case_reasoning","case_id IN (SELECT case_id FROM cases WHERE section_id=?)",(sid,)),
          "conditional_methods":count("semantic_assertions","chapter_key=?",(CHAPTER,)),
          "real_extra_charts":count("historical_case_additional_casts","case_id=?",(second,))}
        if tuple(ans.values())!=(10,90,54,81,1):
            raise ValueError(f"Original story/chart import incomplete: {ans}")
    return {"chapter":CHAPTER,"source_sha256":SHA,**ans,
            "initial_book_errors_preserved":3,"initial_book_success_defaults":7}
