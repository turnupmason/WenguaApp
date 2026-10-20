"""Strict loss-property historical chapter importer: 8 stories, 8 printed 9-palace charts."""
from __future__ import annotations
import hashlib,json,re
from pathlib import Path
from .database import ROOT,connect,initialize,import_section
from .case_reasoning_trace import backfill_existing_case_traces
SHA="ed3c80f32c213563bf35d9f9790e330ea04e4def404f6e6ca904006a94a9eaf9"
CHAPTER="shenqi/lost_money_property_prediction_ch09/v1"
KEY="lost_money_property_prediction_ch09"
INDEX=ROOT/"data/knowledge/shenqi/lost_money_property_prediction_ch09"
PAL={"巽四宫":4,"离九宫":9,"坤二宫":2,"震三宫":3,"中五宫":5,
     "兑七宫":7,"艮八宫":8,"坎一宫":1,"乾六宫":6}
def canon(o):return json.dumps(o,ensure_ascii=False,sort_keys=True,separators=(",",":"))
def span(lines,a,b=None):
    b=a if b is None else b
    if not 1<=a<=b<=len(lines):raise ValueError("Bad book line")
    return "\n".join(lines[a-1:b])
def chart(lines,start):
    if not lines[start-1].startswith("┌"):raise ValueError("Missing genuine source chart")
    out=[]
    for row in range(3):
        anchor=start+1+row*4
        triples=[]
        for d in range(3):
            col=[x.strip() for x in lines[anchor+d-1].split("│")[1:-1]]
            if len(col)!=3:raise ValueError("Source chart column count")
            triples.append(col)
        for pos in range(3):
            name,door,star=(r[pos] for r in triples)
            label=next((x for x in PAL if name.startswith(x)),None)
            if label is None:raise ValueError("Wrong source palace label")
            if label=="中五宫":
                # Centre has NO door/star/deity; retaining the author's centre literal.
                deity="";door=door or "";star=star or ""
            else:
                if "八神：" not in name or not door.startswith("门位原字：") or not star.startswith("星位原字："):
                    raise ValueError("Incomplete outer palace literal")
                deity=name.split("八神：",1)[1].strip()
                door=door.split("：",1)[1];star=star.split("：",1)[1]
            out.append((PAL[label],anchor+pos,name,deity,door,star))
    if sorted(v[0] for v in out)!=list(range(1,10)):raise ValueError("Not nine distinct palaces")
    return out
def prepare(raw):
    if hashlib.sha256(raw).hexdigest()!=SHA:raise ValueError("Source SHA256 mismatch")
    lines=raw.decode("utf-8").splitlines()
    if len(lines)!=362 or lines[0]!="钱物丢失预测" or lines[13]!="第二节 实例解析（8例）":
        raise ValueError("Original chapter differs")
    meta={name:json.loads((INDEX/(name+".json")).read_text(encoding="utf8")) for name in
          ("chapter_manifest","case_index","method_index","source_audit")}
    if any(x["source_sha256"]!=SHA for x in meta.values()):raise ValueError("Index SHA mismatch")
    cases=meta["case_index"]["cases"]
    if len(raw)!=meta["chapter_manifest"]["source_utf8_bytes"] or len(cases)!=8:
        raise ValueError("Chapter size/case count altered")
    if sum(len(c["numbered_or_unnumbered_analysis_lines"]) for c in cases)!=36:raise ValueError("Author steps incomplete")
    if len(meta["method_index"]["general_methods"])!=18:raise ValueError("General methods incomplete")
    for n,c in enumerate(cases,1):
        if n!=c["case_number"] or not lines[c["source_span"][0]-1].startswith("实例"):raise ValueError("Case missing")
        chart(lines,c["original_chart_start"])
        for x in c["numbered_or_unnumbered_analysis_lines"]:
            if not re.match(r"^（\d+）",lines[x-1]) and not(n==3 and x in (113,117)):
                raise ValueError("Missing author analysis source step")
    if "没有断出" not in lines[252] or "张志春按" not in lines[306]:
        raise ValueError("Author omission / editor after-result commentary omitted")
    return lines,meta

def import_lost_property(db_path,source_path):
    raw=Path(source_path).read_bytes()
    lines,meta=prepare(raw)
    initialize(db_path)
    import_section(db_path,"shenqi",KEY,"钱物丢失预测",raw.decode("utf8"))
    with connect(db_path) as db:
        sid=db.execute("SELECT section_id FROM sections WHERE section_key=? AND sha256=?",(KEY,SHA)).fetchone()[0]
        prior=db.execute("SELECT source_sha256 FROM chapter_knowledge WHERE chapter_key=?",(CHAPTER,)).fetchone()
        if prior is None:
            db.execute("""INSERT INTO chapter_knowledge
             (chapter_key,book_id,title,source_sha256,source_length_bytes,knowledge_version,review_status)
             VALUES (?,'shenqi','钱物丢失预测',?,?,'1','draft')""",(CHAPTER,SHA,len(raw)))
        elif prior[0]!=SHA:raise ValueError("Existing chapter source conflict")
        sources=list(meta["method_index"]["general_methods"])
        for c in meta["case_index"]["cases"]:
            for s in c["author_step_evidence_index"]:
                sources.append({"concept_id":"lost:case%02d:step%02d"%(c["case_number"],s["step_number"]),
                 "source_line":s["source_line"],"conditional_method":s["method_topic"],"status":"draft"})
        for m in sources:
            cid=m["concept_id"];n=m["source_line"];literal=span(lines,n)
            old=db.execute("""SELECT original_excerpt FROM semantic_assertions
               WHERE chapter_key=? AND concept_id=? AND source_start_line=?""",(CHAPTER,cid,n)).fetchone()
            if old is None:
                db.execute("""INSERT INTO semantic_assertions
                  (chapter_key,concept_id,kind,relation,source_start_line,source_end_line,
                   metadata_json,original_excerpt,review_status) VALUES (?,?,?,?,?,?,?,?,?)""",
                   (CHAPTER,cid,"lost_property_method","conditional_source",n,n,canon(m),literal,"draft"))
            elif old[0]!=literal:raise ValueError("Previously registered method changed")
        for c in meta["case_index"]["cases"]:
            cid=c["case_id"];i=c["case_number"];known=span(lines,*c["initial_question_lines"])
            steps="\n\n".join(span(lines,n) for n in c["numbered_or_unnumbered_analysis_lines"])
            judgment="\n".join(span(lines,n) for n in c["original_judgment_lines"])
            feedback="\n".join(span(lines,n) for n in c["later_book_feedback_lines"])
            expected=(sid,cid,"lost_property",known,steps,judgment,feedback)
            old=db.execute("""SELECT section_id,event_family_id,domain_id,known_before,
              author_yongshen_steps,author_judgment,later_feedback FROM cases WHERE case_id=?""",(cid,)).fetchone()
            if old is None:
                db.execute("""INSERT INTO cases(case_id,section_id,event_family_id,domain_id,
                known_before,author_yongshen_steps,author_judgment,later_feedback,reviewed)
                VALUES (?,?,?,?,?,?,?,?,0)""",(cid,*expected))
            elif old!=expected:raise ValueError("Existing case differs")
            old=db.execute("SELECT case_source_sha256 FROM historical_case_protocol WHERE case_id=?",(cid,)).fetchone()
            if old is None:
                db.execute("""INSERT INTO historical_case_protocol(case_id,completeness,
                 published_chart_verification,feedback_independently_verified,
                 eligible_blind_test,case_source_sha256,metadata_json)
                 VALUES (?,'source_complete_case','not_independently_recast',0,0,?,?)""",
                 (cid,SHA,canon(c)))
            elif old[0]!=SHA:raise ValueError("Case hash mismatch")
            for cell in chart(lines,c["original_chart_start"]):
                old=db.execute("""SELECT source_line,palace_label_raw,deity_raw,door_position_raw,
                 star_position_raw FROM historical_chart_cells WHERE case_id=? AND palace=?""",
                 (cid,cell[0])).fetchone()
                if old is None:
                    db.execute("""INSERT INTO historical_chart_cells(case_id,palace,source_line,
                    palace_label_raw,deity_raw,door_position_raw,star_position_raw,source_status)
                    VALUES (?,?,?,?,?,?,?,'provided_transcription_not_print_verified')""",(cid,*cell))
                elif old!=cell[1:]:raise ValueError("Source palace differs")
            for s in c["author_step_evidence_index"]:
                k=s["step_number"];n=s["source_line"];literal=span(lines,n)
                old=db.execute("""SELECT source_line,author_analysis_original FROM historical_case_reasoning
                 WHERE case_id=? AND step_number=?""",(cid,k)).fetchone()
                if old is None:
                    db.execute("""INSERT INTO historical_case_reasoning
                     (case_id,step_number,source_line,author_analysis_original,short_method_topic,metadata_json)
                     VALUES (?,?,?,?,?,?)""",(cid,k,n,literal,s["method_topic"],canon(s)))
                elif old!=(n,literal):raise ValueError("Author source reasoning changed")
            feedback_lines=c["later_book_feedback_lines"]
            for n in feedback_lines:
                old=db.execute("SELECT original_statement FROM historical_case_disclosures WHERE case_id=? AND source_line=?",(cid,n)).fetchone()
                if old is None:
                    db.execute("""INSERT INTO historical_case_disclosures
                     (case_id,source_line,phase,fact_type,original_statement)
                     VALUES (?,?,'later_book_feedback','validation_information',?)""",(cid,n,span(lines,n)))
                elif old[0]!=span(lines,n):raise ValueError("Feedback source changed")
            for n in c["disclosures"]:
                old=db.execute("SELECT original_statement FROM historical_case_disclosures WHERE case_id=? AND source_line=?",(cid,n)).fetchone()
                if old is None:
                    db.execute("""INSERT INTO historical_case_disclosures
                     (case_id,source_line,phase,fact_type,original_statement)
                     VALUES (?,?,'subsequent_not_initial','conditional_disclosure_or_posthoc',?)""",(cid,n,span(lines,n)))
                elif old[0]!=span(lines,n):raise ValueError("Later source differs")
            verdict=db.execute("SELECT verdict FROM historical_case_book_verdicts WHERE event_family_id=?",(cid,)).fetchone()
            if verdict is None:
                db.execute("""INSERT INTO historical_case_book_verdicts
                  (event_family_id,primary_case_id,verdict,explicit_source_correction,
                   source_correction_lines_json,feedback_source_lines_json,
                   independent_external_verification,app_output_protocol,evidence_review_status,note)
                   VALUES (?,?,'author_book_success_default',0,'[]',?,
                     'not_verified','single_answer_for_one_cast','book_source_only',?)""",
                  (cid,cid,canon(feedback_lines),
                   "Case6 retains line253 admission of missed location" if i==6 else "Historical source only"))
            elif verdict[0]!=c["book_outcome_label"]:raise ValueError("Verdict was altered")
            for n,kind in (([(253,"author_location_omission")] if i==6 else
                             [(307,"editor_retrospective_method")] if i==7 else [])):
                original=span(lines,n)
                old=db.execute("""SELECT original_text FROM historical_case_source_segments
                  WHERE case_id=? AND segment_kind=? AND source_start_line=?""",(cid,kind,n)).fetchone()
                if old is None:
                    db.execute("""INSERT INTO historical_case_source_segments
                     (case_id,segment_kind,source_start_line,source_end_line,original_text,metadata_json)
                     VALUES (?,?,?,?,?,?)""",(cid,kind,n,n,original,canon({"posthoc":True})))
                elif old[0]!=original:raise ValueError("Editorial source altered")
        from .case_reasoning_trace import backfill_existing_case_traces
        done=backfill_existing_case_traces(db)
        def number(tbl,condition,args):
            return db.execute("SELECT count(*) FROM "+tbl+" WHERE "+condition,args).fetchone()[0]
        result={"cases":number("cases","section_id=?",(sid,)),
         "palaces":number("historical_chart_cells","case_id IN (SELECT case_id FROM cases WHERE section_id=?)",(sid,)),
         "author_steps":number("historical_case_reasoning","case_id IN (SELECT case_id FROM cases WHERE section_id=?)",(sid,)),
         "candidates":number("semantic_assertions","chapter_key=?",(CHAPTER,)),
         "traces":number("historical_case_reasoning_trace","case_id IN (SELECT case_id FROM cases WHERE section_id=?)",(sid,))}
        if tuple(result.values())!=(8,72,36,54,36):raise ValueError("Incomplete chapter import: "+str(result))
    return {"chapter":CHAPTER,"source_sha256":SHA,**result,
            "mechanical_legacy_traces_newly_created_if_private_db_supplied":done["created"],
            "author_full_chains_not_yet_human_verified":True}
