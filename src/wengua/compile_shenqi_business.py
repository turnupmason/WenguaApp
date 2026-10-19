"""Append Shenqi business source: 14 intact families, 16 genuine printed hour charts.

The original 717-line book source is kept only in the user's private SQLite.
One charity drawing family has three actual distinct hour casts (14 event
families != 14 unique cast configurations). Two later days have no printed
charts; never reconstruct or invent those charts.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from .database import ROOT,connect,initialize,import_section

SHA="c955d56bc7deb1b5c4a99f5b2594625d3d7f690e60063eed10f55864b514698c"
KEY="business_profit_prediction_ch06"
CHAPTER="shenqi/"+KEY+"/v1"
INDEX=ROOT/"data/knowledge/shenqi/business_profit_prediction_ch06"
PALACES={"坎1":1,"坤2":2,"震3":3,"巽4":4,"中5":5,"乾6":6,"兑7":7,"艮8":8,"离9":9}
CN="一二三四五六七八九十"
# Real source is authoritative; these are SOURCE-SCOPED predictions, not independent truths.
PRED_LINES=[[99],[135],[175,181,187,191],[228],[266],[300],[308],
 [362,364,366],[422,424,426,428],[468,472,474],[512],[580,608,637],
 [671,673,675,677],[687]]
SOURCE_SEGMENTS=[(7,"original_rental_question_and_disclosed_forecast",308,310),
 (12,"lottery_posterior_event_narrative",546,552),
 (12,"lottery_editor_review_cast1",582,582),
 (12,"lottery_editor_review_cast2",610,610),
 (12,"lottery_editor_review_cast3",639,639),
 (12,"lottery_text_only_third_day",641,641),
 (12,"lottery_text_only_fourth_day",643,643),
 (8,"book_art_authentication_followups",368,370),
 (14,"book_source_final_line_unfinished",717,717)]
EXTRA=[(12,"1997-01-25_丁未","1997-01-25","丁未",585),
       (12,"1997-01-26_丁巳","1997-01-26","丁巳",614)]

def canon(x):
    return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":"))

def span(lines,a,b=None):
    if b is None:b=a
    if not isinstance(a,int) or not isinstance(b,int) or not 1<=a<=b<=len(lines):
        raise ValueError("Source line reference out of uploaded original")
    return "\n".join(lines[a-1:b])

def chart(lines,start):
    """Parse 3×3 original text table without inferring missing center facts."""
    if not lines[start-1].startswith("┌"):
        raise ValueError(f"No printed nine-palace table at line {start}")
    result=[]
    for group in range(3):
        a=start+1+5*group
        rows=[]
        for n in range(a,a+4):
            v=[s.strip() for s in lines[n-1].split("│")[1:-1]]
            if len(v)!=3:raise ValueError(f"Missing chart columns at line {n}")
            rows.append(v)
        for i in range(3):
            name,deity,door,star=(rows[j][i] for j in range(4))
            if name not in PALACES:raise ValueError(f"Invalid source palace {name}")
            result.append((PALACES[name],a+i,name,deity,door,star))
    if sorted(x[0] for x in result)!=list(range(1,10)):
        raise ValueError("Duplicate/missing nine palace cell")
    return result

def prepare(raw):
    if hashlib.sha256(raw).hexdigest()!=SHA:
        raise ValueError("Business source SHA256 mismatch; no writes to database")
    lines=raw.decode("utf-8").splitlines()
    if len(lines)!=717 or lines[0]!="第六章 经营求财预测" or not lines[62].startswith("第二节 实例解析（14例）"):
        raise ValueError("Business source original chapter boundaries differ")
    data={n:json.loads((INDEX/(n+".json")).read_text(encoding="utf-8"))
          for n in ("chapter_manifest","case_index","method_index","source_audit")}
    if any(d["source_sha256"]!=SHA for d in data.values()):
        raise ValueError("Public metadata does not match private original SHA")
    cases=data["case_index"]["cases"]
    methods=data["method_index"]["methods"]
    if data["chapter_manifest"]["source_utf8_bytes"]!=len(raw):
        raise ValueError("Source manifest byte count mismatch")
    if len(cases)!=14 or sum(len(x["chart_source_starts"]) for x in cases)!=16:
        raise ValueError("Need exactly 14 event families and all 16 supplied casts")
    if len(methods)!=81 or len({m["concept_id"] for m in methods})!=81:
        raise ValueError("All 81 original-line-linked method concepts required")
    if sum(len(x["numbered_or_explicit_analysis_ranges"]) for x in cases)!=59:
        raise ValueError("Need 56 numbered steps and all 3 unnumbered banking methods")
    rec=[]
    for i,c in enumerate(cases):
        a,b=c["source_span"]
        if not lines[a-1].startswith("实例"):
            raise ValueError("Original case heading not found")
        if c["book_outcome_label"]!="author_book_success_default":
            raise ValueError("Book default verdict changed without explicit author correction")
        if len(c["chart_source_starts"])!=(3 if i==11 else 1):
            raise ValueError("Unexpected complete chart count in historical case")
        full_charts=[chart(lines,start) for start in c["chart_source_starts"]]
        steps=[]
        for j,(begin,end) in enumerate(c["numbered_or_explicit_analysis_ranges"],1):
            text=span(lines,begin,end)
            if i==9:
                if not text.startswith(("第一种方法：","第二种方法：","第三种方法")):
                    raise ValueError("Three unnumbered loan methods were dropped")
            elif not text.startswith(f"（{j}）") and i!=11:
                raise ValueError("Numbered source reasoning no longer matches chapter")
            steps.append((j,begin,end,text))
        initial=span(lines,*c["initial_source_lines"])
        if i==6:
            if "杜起出奇门局看了一会儿说" not in initial:
                raise ValueError("Rental case's initial narration changed")
            initial=initial.split("杜起出奇门局看了一会儿说",1)[0]
        if i==8:
            initial=initial.split("杜依奇门格局首先对企业目前运行态势指出有三",1)[0]
        if i==11:
            if "事后，" not in initial:raise ValueError("Lottery initial account has no clear feedback cut")
            initial=initial.split("事后，",1)[0]
            if "实际被抽" in initial:raise ValueError("Book result leaked into initial lottery input")
        for n in c["same_case_feedback_lines"]:
            if not a<=n<=b:raise ValueError("Feedback source lies outside case")
        rec.append((c,full_charts,steps,initial))
    if len(EXTRA)!=2 or len(data["case_index"]["unsupplied_source_casts"])!=1:
        raise ValueError("Extra chart study structure incomplete")
    return lines,methods,rec

def _same_or_insert(db,table,where,params,columns,values):
    fields=", ".join(columns)
    old=db.execute(f"SELECT {fields} FROM {table} WHERE {where}",params).fetchone()
    if old is None:
        all_cols=list(columns)
        # Only used where params correspond to a primary key.
        db.execute(f"INSERT INTO {table} ({fields}) VALUES ({','.join('?' for _ in values)})",values)
    elif tuple(old)!=tuple(values[(-len(columns)):]):
        raise ValueError(f"Prior original {table} content differs; no silent overwrite")

def import_business_chapter(db_path,source_file):
    raw=Path(source_file).read_bytes()
    lines,methods,events=prepare(raw) # reject wrong source BEFORE any DB creation/write
    import_section(db_path,"shenqi",KEY,"经营求财预测",raw.decode("utf-8"))
    initialize(db_path)
    with connect(db_path) as db:
        sec=db.execute("""SELECT section_id FROM sections WHERE book_id='shenqi'
             AND section_key=? AND sha256=?""",(KEY,SHA)).fetchone()
        if not sec:raise ValueError("Exact original full text not imported")
        section_id=sec[0]
        old=db.execute("SELECT source_sha256 FROM chapter_knowledge WHERE chapter_key=?",(CHAPTER,)).fetchone()
        if old is None:
            db.execute("""INSERT INTO chapter_knowledge
                (chapter_key,book_id,title,source_sha256,source_length_bytes,knowledge_version,review_status)
                VALUES (?,'shenqi','经营求财预测',?,?,'1','draft')""",(CHAPTER,SHA,len(raw)))
        elif old[0]!=SHA:raise ValueError("Existing original source has different SHA")
        for m in methods:
            n=m["source_line"];cid=m["concept_id"]; original=span(lines,n)
            old=db.execute("""SELECT original_excerpt FROM semantic_assertions
                WHERE chapter_key=? AND concept_id=? AND source_start_line=?""",(CHAPTER,cid,n)).fetchone()
            if old is None:
                db.execute("""INSERT INTO semantic_assertions
                   (chapter_key,concept_id,kind,relation,source_start_line,source_end_line,
                   metadata_json,original_excerpt,review_status)
                   VALUES (?,?,'business_domain_method','source_condition_candidate',?,?,?,?,'draft')""",
                   (CHAPTER,cid,n,n,canon(m),original))
            elif old[0]!=original:raise ValueError("Prior original knowledge source changed")
        for i,(c,charts,steps,initial) in enumerate(events):
            cid=c["case_id"]
            body="\n\n".join(step[3] for step in steps)
            pred="\n".join(span(lines,n) for n in PRED_LINES[i])
            if i==6:pred=pred.split("李助理说",1)[0]
            if i==11:pred="\n".join(s.split("实际",1)[0] for s in pred.split("\n"))
            if i==13:pred=pred.split("结果是白跑一趟",1)[0]
            feedback="\n".join(span(lines,n) for n in c["same_case_feedback_lines"])
            wanted=(section_id,cid,"business_profit",initial,body,pred,feedback)
            old=db.execute("""SELECT section_id,event_family_id,domain_id,known_before,
                author_yongshen_steps,author_judgment,later_feedback FROM cases
                WHERE case_id=?""",(cid,)).fetchone()
            if old is None:
                db.execute("""INSERT INTO cases(case_id,section_id,event_family_id,domain_id,
                   known_before,author_yongshen_steps,author_judgment,later_feedback,reviewed)
                   VALUES (?,?,?,?,?,?,?,?,0)""",(cid,*wanted))
            elif old!=wanted:raise ValueError("Source case changed, do not overwrite")
            old=db.execute("SELECT case_source_sha256 FROM historical_case_protocol WHERE case_id=?",(cid,)).fetchone()
            if old is None:
                db.execute("""INSERT INTO historical_case_protocol
                   (case_id,completeness,published_chart_verification,feedback_independently_verified,
                    eligible_blind_test,case_source_sha256,metadata_json)
                   VALUES (?,'complete_original_case_multicast_if_present',
                    'user_source_not_independently_cast',0,0,?,?)""",
                    (cid,SHA,canon({"one_indivisible_event_family":True,"complete_casts":len(charts),
                     "original_case":c,"private_full_text":True,"book_success_default":True})))
            elif old[0]!=SHA:raise ValueError("Original case protocol differs")
            for palace,n,name,deity,door,star in charts[0]:
                wanted=(n,name,deity,door,star)
                old=db.execute("""SELECT source_line,palace_label_raw,deity_raw,
                     door_position_raw,star_position_raw FROM historical_chart_cells
                     WHERE case_id=? AND palace=?""",(cid,palace)).fetchone()
                if old is None:
                    db.execute("""INSERT INTO historical_chart_cells
                         (case_id,palace,source_line,palace_label_raw,deity_raw,
                          door_position_raw,star_position_raw) VALUES (?,?,?,?,?,?,?)""",(cid,palace,*wanted))
                elif old!=wanted:raise ValueError("Original nine-palace cell changed")
            for j,start,end,excerpt in steps:
                old=db.execute("""SELECT source_line,author_analysis_original FROM historical_case_reasoning
                         WHERE case_id=? AND step_number=?""",(cid,j)).fetchone()
                if old is None:
                    db.execute("""INSERT INTO historical_case_reasoning
                       (case_id,step_number,source_line,author_analysis_original,short_method_topic,metadata_json)
                       VALUES (?,?,?,?,?,?)""",(cid,j,start,excerpt,f"原书第{j}组",
                       canon({"source_line_span":[start,end],"one_event":True})))
                elif old!=(start,excerpt):raise ValueError("Original author method changed")
            for n in c["same_case_feedback_lines"]:
                excerpt=span(lines,n)
                old=db.execute("""SELECT original_statement FROM historical_case_disclosures
                         WHERE case_id=? AND source_line=?""",(cid,n)).fetchone()
                if old is None:
                    db.execute("""INSERT INTO historical_case_disclosures
                         (case_id,source_line,phase,fact_type,original_statement)
                         VALUES (?,?,'same_event_book_validation','validation_information',?)""",
                         (cid,n,excerpt))
                elif old[0]!=excerpt:raise ValueError("Original case feedback changed")
            old=db.execute("SELECT verdict FROM historical_case_book_verdicts WHERE event_family_id=?",(cid,)).fetchone()
            if old is None:
                db.execute("""INSERT INTO historical_case_book_verdicts
                    (event_family_id,primary_case_id,verdict,explicit_source_correction,
                     source_correction_lines_json,feedback_source_lines_json,
                     independent_external_verification,app_output_protocol,evidence_review_status,note)
                    VALUES (?,?,'author_book_success_default',0,'[]',?,
                      'not_verified','single_answer_for_one_cast','book_source_only',?)""",
                     (cid,cid,canon(c["same_case_feedback_lines"]),
                      "Success by user author-book default; not independent predictive proof"))
            elif old[0]!="author_book_success_default":
                raise ValueError("Explicit book correction was previously recorded")
        # Case 12: 3 charts, not 3 separate book events. First chart above.
        family=events[11][0]["case_id"]
        for case_no,key,date,hour,start in EXTRA:
            additional=[entry for entry in events[case_no-1][1]
                        if entry[0][1]==start+2]
            # Use source start directly: avoids relying on table cell order.
            cells=chart(lines,start)
            old=db.execute("""SELECT source_chart_start FROM historical_case_additional_casts
                WHERE case_id=? AND cast_key=?""",(family,key)).fetchone()
            if old is None:
                db.execute("""INSERT INTO historical_case_additional_casts
                  (case_id,cast_key,cast_datetime_description,calendar_date,hour_ganzhi,source_chart_start,notes)
                  VALUES (?,?,?,?,?,?,?)""",
                  (family,key,f"{date} {hour}",date,hour,start,
                   "Same drawing event, different real hour-specific printed nine-palace cast"))
            elif old[0]!=start:raise ValueError("Additional chart metadata changed")
            for palace,n,name,deity,door,star in cells:
                wanted=(n,name,deity,door,star)
                old=db.execute("""SELECT source_line,palace_label_raw,deity_raw,door_position_raw,star_position_raw
                    FROM historical_case_additional_cast_cells
                    WHERE case_id=? AND cast_key=? AND palace=?""",(family,key,palace)).fetchone()
                if old is None:
                    db.execute("""INSERT INTO historical_case_additional_cast_cells
                      (case_id,cast_key,palace,source_line,palace_label_raw,deity_raw,door_position_raw,star_position_raw)
                      VALUES (?,?,?,?,?,?,?,?)""",(family,key,palace,*wanted))
                elif old!=wanted:raise ValueError("Additional source chart palace changed")
        # Original source editorial reviews and later hours without printed charts.
        for number,kind,a,b in SOURCE_SEGMENTS:
            cid=events[number-1][0]["case_id"]; original=span(lines,a,b)
            old=db.execute("""SELECT original_text FROM historical_case_source_segments
               WHERE case_id=? AND segment_kind=? AND source_start_line=?""",(cid,kind,a)).fetchone()
            if old is None:
                db.execute("""INSERT INTO historical_case_source_segments
                   (case_id,segment_kind,source_start_line,source_end_line,original_text,metadata_json)
                   VALUES (?,?,?,?,?,?)""",
                   (cid,kind,a,b,original,canon({"same_event":True,"source_sha256":SHA})))
            elif old[0]!=original:raise ValueError("Original source editorial segment changed")
        def count(table,predicate=None):
            return db.execute(f"SELECT COUNT(*) FROM {table}"+(f" WHERE {predicate}" if predicate else "")).fetchone()[0]
        totals={
         "new_event_families":count("cases",f"section_id={int(section_id)}"),
         "primary_source_cells":count("historical_chart_cells",
             f"case_id IN (SELECT case_id FROM cases WHERE section_id={int(section_id)})"),
         "additional_source_cells":count("historical_case_additional_cast_cells"),
         "fully_sourced_additional_casts":count("historical_case_additional_casts"),
         "author_analysis_units":count("historical_case_reasoning",
             f"case_id IN (SELECT case_id FROM cases WHERE section_id={int(section_id)})"),
         "source_method_candidates":count("semantic_assertions",f"chapter_key='{CHAPTER}'")}
        if tuple(totals.values())!=(14,126,18,2,59,81):
            raise ValueError(f"Incomplete 14-event/16-chart original import: {totals}")
    return {"source_sha256":SHA,"chapter":CHAPTER,**totals,
      "book_success_default":14,"independent_external_proof":0}
