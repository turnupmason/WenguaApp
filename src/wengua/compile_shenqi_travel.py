"""Lossless source-checked Shenqi travel chapter importer; public repo contains NO copyrighted full text."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
from .database import ROOT,connect,initialize,import_section

SHA="c273c803eb78a02cfb3c6c00065da81312c1851a679a1e3bca4911acdbc3bc55"
CHAPTER="shenqi/travel_abroad_prediction_ch07/v1"
KEY="travel_abroad_prediction_ch07"
INDEX=ROOT/"data/knowledge/shenqi/travel_abroad_prediction_ch07"
PAL={"巽四宫":4,"离九宫":9,"坤二宫":2,"震三宫":3,"中五宫":5,
     "兑七宫":7,"艮八宫":8,"坎一宫":1,"乾六宫":6}
def canon(o):return json.dumps(o,ensure_ascii=False,sort_keys=True,separators=(",",":"))
def segment(lines,a,b=None):
    if b is None:b=a
    if not 1<=a<=b<=len(lines):raise ValueError("Bad original source line range")
    return "\n".join(lines[a-1:b])
def parse_original_chart(lines,start):
    if not lines[start-1].startswith("┌"):raise ValueError("Original nine-palace drawing missing")
    result=[]
    for row in range(3):
        trip=[]
        for offset in (1,2,3):
            text=lines[start+4*row+offset-1]
            fields=[x.strip() for x in text.split("│")[1:-1]]
            if len(fields)!=3:raise ValueError("Source chart must have three columns")
            trip.append(fields)
        for col in range(3):
            name,door,star=(trip[k][col] for k in range(3))
            matching=[v for k,v in PAL.items() if name.startswith(k)]
            if len(matching)!=1:raise ValueError("Unrecognized original palace")
            deity=name.split("八神：",1)[1].strip() if "八神：" in name else ""
            # Existing SQLite chart schema enforces unique source_line among 3
            # same printed-row palaces; reserve row's 3 physical line anchors.
            result.append((matching[0],start+4*row+1+col,name,deity,door,star))
    if sorted(c[0] for c in result)!=list(range(1,10)):
        raise ValueError("Source chart missing or duplicate palaces")
    return result

def validate_original(raw):
    if hashlib.sha256(raw).hexdigest()!=SHA:
        raise ValueError("Source SHA256 mismatch: refusing DB mutation")
    lines=raw.decode("utf-8").splitlines()
    if len(lines)!=350 or lines[0]!="出行出国预测" or lines[20]!="第二节 实例解析（6例）":
        raise ValueError("Incorrect Shenqi travel chapter boundaries")
    meta={k:json.loads((INDEX/(k+".json")).read_text(encoding="utf-8")) for k in
          ("chapter_manifest","case_index","method_index","source_audit")}
    if any(x["source_sha256"]!=SHA for x in meta.values()):
        raise ValueError("Public source metadata SHA mismatch")
    manifest=meta["chapter_manifest"]
    cases=meta["case_index"]["cases"]
    rules=meta["method_index"]["methods"]
    if manifest["source_utf8_bytes"]!=len(raw) or len(cases)!=6 or len(rules)!=38:
        raise ValueError("Original source byte count or indexed cases/rules differ")
    if sum(len(c["original_chart_starts"]) for c in cases)!=7 or sum(len(c["numbered_reasoning_lines"]) for c in cases)!=29:
        raise ValueError("Seven real original charts and 29 numbered steps required")
    for c in cases:
        if not lines[c["source_span"][0]-1].startswith("实例"):
            raise ValueError("Missing source complete case heading")
        if c["case_id"]!=c["event_family_id"] or c["book_outcome_label"]!="author_book_success_default":
            raise ValueError("Incorrect whole-event book study policy")
        for p in c["original_chart_starts"]:parse_original_chart(lines,p)
        for p in c["numbered_reasoning_lines"]:
            if not lines[p-1].startswith("（"):raise ValueError("Author numbered analysis text missing")
        for p in c["book_feedback_lines"]:segment(lines,p)
    if cases[3]["original_chart_starts"]!=[157] or cases[5]["original_chart_starts"]!=[293,324]:
        raise ValueError("Original old-chart reuse or Germany second chart lost")
    return lines,meta

def import_travel_chapter(db_path,source_file):
    raw=Path(source_file).read_bytes()
    lines,meta=validate_original(raw)  # CHECK before touching database
    initialize(db_path)
    import_section(db_path,"shenqi",KEY,"出行出国预测",raw.decode("utf-8"))
    with connect(db_path) as db:
        row=db.execute("SELECT section_id FROM sections WHERE book_id='shenqi' AND section_key=? AND sha256=?",(KEY,SHA)).fetchone()
        if not row:raise ValueError("Full original private source missing")
        sid=row[0]
        prev=db.execute("SELECT source_sha256 FROM chapter_knowledge WHERE chapter_key=?",(CHAPTER,)).fetchone()
        if prev is None:
            db.execute("""INSERT INTO chapter_knowledge(chapter_key,book_id,title,source_sha256,source_length_bytes,knowledge_version,review_status)
             VALUES (?,'shenqi','出行出国预测',?,?,'1','draft')""",(CHAPTER,SHA,len(raw)))
        elif prev[0]!=SHA:raise ValueError("Old chapter source conflict")
        for r in meta["method_index"]["methods"]:
            line=r["source_line"];cid=r["concept_id"];value=segment(lines,line)
            old=db.execute("SELECT original_excerpt FROM semantic_assertions WHERE chapter_key=? AND concept_id=? AND source_start_line=?",(CHAPTER,cid,line)).fetchone()
            if old is None:
                db.execute("""INSERT INTO semantic_assertions(chapter_key,concept_id,kind,relation,source_start_line,source_end_line,
                 metadata_json,original_excerpt,review_status) VALUES (?,?,'travel_source_method','conditional_source',?,?,?,?,'draft')""",
                 (CHAPTER,cid,line,line,canon(r),value))
            elif old[0]!=value:raise ValueError("Original method conflict")
        for c in meta["case_index"]["cases"]:
            cid=c["case_id"]
            full="\n\n".join(segment(lines,s) for s in c["numbered_reasoning_lines"])
            guess="\n".join(segment(lines,s) for s in c["original_judgment_lines"])
            feedback="\n".join(segment(lines,s) for s in c["book_feedback_lines"])
            initial=segment(lines,*c["initial_source_lines"])
            wanted=(sid,cid,"travel_abroad",initial,full,guess,feedback)
            old=db.execute("SELECT section_id,event_family_id,domain_id,known_before,author_yongshen_steps,author_judgment,later_feedback FROM cases WHERE case_id=?",(cid,)).fetchone()
            if old is None:
                db.execute("""INSERT INTO cases(case_id,section_id,event_family_id,domain_id,known_before,author_yongshen_steps,author_judgment,later_feedback,reviewed)
                 VALUES (?,?,?,?,?,?,?,?,0)""",(cid,*wanted))
            elif old!=wanted:raise ValueError("Existing story data differs")
            old=db.execute("SELECT case_source_sha256 FROM historical_case_protocol WHERE case_id=?",(cid,)).fetchone()
            if old is None:
                db.execute("""INSERT INTO historical_case_protocol(case_id,completeness,published_chart_verification,
                 feedback_independently_verified,eligible_blind_test,case_source_sha256,metadata_json)
                 VALUES (?,'full_original_whole_event','source_transcription_not_recast',0,0,?,?)""",
                 (cid,SHA,canon({"source_sha256":SHA,"original_case":c,"source_cast_count":len(c["original_chart_starts"]),"not_external_safety_validation":True})))
            elif old[0]!=SHA:raise ValueError("Old case protocol conflict")
            for cell in parse_original_chart(lines,c["original_chart_starts"][0]):
                existing=db.execute("SELECT source_line,palace_label_raw,deity_raw,door_position_raw,star_position_raw FROM historical_chart_cells WHERE case_id=? AND palace=?",(cid,cell[0])).fetchone()
                if existing is None:
                    db.execute("INSERT INTO historical_chart_cells(case_id,palace,source_line,palace_label_raw,deity_raw,door_position_raw,star_position_raw) VALUES (?,?,?,?,?,?,?)",(cid,*cell))
                elif existing!=cell[1:]:raise ValueError("Original source palace has changed")
            for i,n in enumerate(c["numbered_reasoning_lines"],1):
                original=segment(lines,n)
                phase="first_cast"
                if c["index"]==4 and i>=4:phase="later_october_old_cast_reuse"
                if c["index"]==6 and i>=4:phase="genuine_second_cast"
                old=db.execute("SELECT source_line,author_analysis_original FROM historical_case_reasoning WHERE case_id=? AND step_number=?",(cid,i)).fetchone()
                if old is None:
                    db.execute("""INSERT INTO historical_case_reasoning(case_id,step_number,source_line,author_analysis_original,short_method_topic,metadata_json)
                     VALUES (?,?,?,?,?,?)""",(cid,i,n,original,"原书整案分段来源",canon({"phase":phase,"source_line":n})))
                elif old!=(n,original):raise ValueError("Original numbered reasoning has changed")
            for n in c["book_feedback_lines"]:
                original=segment(lines,n)
                old=db.execute("SELECT original_statement FROM historical_case_disclosures WHERE case_id=? AND source_line=?",(cid,n)).fetchone()
                if old is None:
                    db.execute("""INSERT INTO historical_case_disclosures(case_id,source_line,phase,fact_type,original_statement)
                     VALUES (?,?,'same_original_event_book_followup','validation_information',?)""",(cid,n,original))
                elif old[0]!=original:raise ValueError("Original feedback has changed")
            old=db.execute("SELECT verdict FROM historical_case_book_verdicts WHERE event_family_id=?",(cid,)).fetchone()
            if old is None:
                db.execute("""INSERT INTO historical_case_book_verdicts(event_family_id,primary_case_id,verdict,
                 explicit_source_correction,source_correction_lines_json,feedback_source_lines_json,
                 independent_external_verification,app_output_protocol,evidence_review_status,note)
                 VALUES (?,?,'author_book_success_default',0,'[]',?,'not_verified','single_answer_for_one_cast','book_source_only',?)""",
                 (cid,cid,canon(c["book_feedback_lines"]),"Research source author default is not independent travel safety proof"))
            elif old[0]!="author_book_success_default":raise ValueError("Existing author verdict differs")
        sixth=meta["case_index"]["cases"][5]["case_id"]
        key="planned_departure_1996_06_24_戊申";chart_start=324
        row=db.execute("SELECT source_chart_start FROM historical_case_additional_casts WHERE case_id=? AND cast_key=?",(sixth,key)).fetchone()
        if row is None:
            db.execute("""INSERT INTO historical_case_additional_casts(case_id,cast_key,cast_datetime_description,calendar_date,
             hour_ganzhi,source_chart_start,notes) VALUES (?,?,?,?,?,?,?)""",
             (sixth,key,"Planned flight time 1996-06-24 15:00; actual delayed to 18:00","1996-06-24","戊申",324,"ONE story, real printed second time chart, no implied actual 18:00 chart"))
        elif row[0]!=chart_start:raise ValueError("Second source chart changed")
        for cell in parse_original_chart(lines,chart_start):
            old=db.execute("""SELECT source_line,palace_label_raw,deity_raw,door_position_raw,star_position_raw
              FROM historical_case_additional_cast_cells WHERE case_id=? AND cast_key=? AND palace=?""",(sixth,key,cell[0])).fetchone()
            if old is None:
                db.execute("""INSERT INTO historical_case_additional_cast_cells(case_id,cast_key,palace,
                 source_line,palace_label_raw,deity_raw,door_position_raw,star_position_raw)
                 VALUES (?,?,?,?,?,?,?,?)""",(sixth,key,*cell))
            elif old!=cell[1:]:raise ValueError("Second source chart fields have changed")
        for part in meta["case_index"]["retrospective_segments"]:
            c=meta["case_index"]["cases"][part["case"]-1]
            cid=c["case_id"];a,b=part["source_lines"];original=segment(lines,a,b)
            old=db.execute("""SELECT original_text FROM historical_case_source_segments
                 WHERE case_id=? AND segment_kind=? AND source_start_line=?""",(cid,part["kind"],a)).fetchone()
            if old is None:
                db.execute("""INSERT INTO historical_case_source_segments
                 (case_id,segment_kind,source_start_line,source_end_line,original_text,metadata_json)
                 VALUES (?,?,?,?,?,?)""",(cid,part["kind"],a,b,original,canon({"same_event":True,"not_initial_known":True})))
            elif old[0]!=original:raise ValueError("Original later review changed")
        result={"section_id":sid}
        scoped="case_id IN (SELECT case_id FROM cases WHERE section_id=?)"
        for tab in ("historical_chart_cells","historical_case_reasoning","historical_case_book_verdicts","historical_case_additional_casts"):
            col="primary_case_id" if tab=="historical_case_book_verdicts" else "case_id"
            result[tab]=db.execute(f"SELECT COUNT(*) FROM {tab} WHERE {col} IN (SELECT case_id FROM cases WHERE section_id=?)",(sid,)).fetchone()[0]
        result["source_cases"]=db.execute("SELECT count(*) FROM cases WHERE section_id=?",(sid,)).fetchone()[0]
        result["source_rules"]=db.execute("SELECT count(*) FROM semantic_assertions WHERE chapter_key=?",(CHAPTER,)).fetchone()[0]
        if (result["source_cases"],result["historical_chart_cells"],result["historical_case_reasoning"],
            result["historical_case_additional_casts"],result["source_rules"])!=(6,54,29,1,38):
            raise ValueError("Incomplete original six cases/seven casts/methods")
        return result
