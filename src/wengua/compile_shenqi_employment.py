"""Strict, additive importer for Shenqi employment case chapter.

Five indivisible events: 5 real source charts, 45 palace cells, 20 author
numbered steps, and one election with five candidates on ONE chart.
Source book feedback is in the SAME event, book success by user default.
The full copyrighted source remains in user's private SQLite.
"""
from __future__ import annotations
from pathlib import Path
import hashlib
import json
from .database import ROOT, connect, initialize, import_section

SHA = "b78ab538a090cc8f59474b49bac613318e130dd78a563929b097ac6922e7fa05"
KEY = "employment_prediction_ch05"
CHAPTER = "shenqi/employment_prediction_ch05/v1"
TITLE = "工作就业预测"
INDEX = ROOT / "data/knowledge/shenqi/employment_prediction_ch05"
PALACES = {"坎1":1,"坤2":2,"震3":3,"巽4":4,"中5":5,
           "乾6":6,"兑7":7,"艮8":8,"离9":9}
CN = "一二三四五"

def canon(value):
    return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(",",":"))

def source_line(lines,at):
    a,b=at
    if not isinstance(a,int) or not isinstance(b,int) or not 1<=a<=b<=len(lines):
        raise ValueError("Invalid original book source line range")
    return "\n".join(lines[a-1:b])

def _chart(lines,chart_groups):
    """Compact printed chart: 3 horizontal groups, each 4 literal rows.
    The original text is in private sections. source_line is a distinct
    source anchor within its horizontal group, not an inferred cell value.
    """
    if len(chart_groups)!=3:raise ValueError("Need exactly 3 printed rows")
    result=[]
    for group_index,loc in enumerate(chart_groups):
        a,b=loc
        if b!=a+3:raise ValueError("Truncated source chart group")
        parts=[]
        for n in range(a,b+1):
            s=lines[n-1]
            fields=[x.strip() for x in s.split("│")[1:-1]]
            if len(fields)!=3:raise ValueError(f"Three chart columns not found at {n}")
            parts.append(fields)
        for col in range(3):
            name,deity,door,star=(parts[k][col] for k in range(4))
            if name not in PALACES:raise ValueError("Invalid source palace")
            result.append((PALACES[name],a+1+col,name,deity,door,star))
    if sorted(x[0] for x in result)!=list(range(1,10)):
        raise ValueError("Missing or duplicate original chart palace")
    return result

def prepare(raw):
    if hashlib.sha256(raw).hexdigest()!=SHA:
        raise ValueError("Employment source SHA256 mismatch: no DB write")
    lines=raw.decode("utf-8").splitlines()
    if len(lines)!=228 or lines[0]!="第五章 工作就业预测" or not lines[18].startswith("第二节 实例解析（5例）"):
        raise ValueError("Source chapter boundary/version differs")
    indices={}
    for name in ("chapter_manifest","case_index","method_index","source_audit"):
        obj=json.loads((INDEX/(name+".json")).read_text(encoding="utf-8"))
        if obj["source_sha256"]!=SHA:
            raise ValueError("Public knowledge source does not match original text")
        indices[name]=obj
    manifest=indices["chapter_manifest"]
    cases=indices["case_index"]["cases"]
    methods=indices["method_index"]["methods"]
    ranked=indices["case_index"]["candidate_ranking"]
    if (manifest["source_utf8_bytes"],manifest["source_lines"])!=(len(raw),228):
        raise ValueError("Public source size/line mismatch")
    if len(cases)!=5 or len({c["case_id"] for c in cases})!=5:
        raise ValueError("Five whole event families required")
    if sum(len(c["step"]) for c in cases)!=20:
        raise ValueError("All 20 original numbered author steps required")
    if len(methods)!=53 or len({m["concept_id"] for m in methods})!=53:
        raise ValueError("53 unique sourced employment methods required")
    records=[]
    for i,c in enumerate(cases,1):
        if c["index"]!=i or not lines[c["span"][0]-1].startswith("实例"+CN[i-1]):
            raise ValueError("Original whole-case header mismatch")
        if c["case_id"]!=c["event_family_id"] or c["book_outcome_label"]!="author_book_success_default":
            raise ValueError("Case family or book-success default unexpectedly changed")
        cells=_chart(lines,c["chart_source_groups"])
        steps=[]
        if len(c["step"])!=len(c["topics"]):
            raise ValueError("Author step topics do not match numbered steps")
        for j,(at,topic) in enumerate(zip(c["step"],c["topics"]),1):
            txt=source_line(lines,at)
            if not lines[at[0]-1].startswith(f"（{j}）"):
                raise ValueError("Original numbered analysis step missing")
            steps.append((j,at[0],at[1],txt,topic))
        for n in c["validation"]+c["pred"]:
            if not c["span"][0]<=n<=c["span"][1]:
                raise ValueError("Validation or author judgment in another event")
        if i==2:
            if "11月4日" not in lines[92] or "一看" not in lines[92]:
                raise ValueError("Late November follow-up must reuse old November 4 cast")
        if i==4:
            if "五次" not in lines[149] or "第一次" not in lines[149]:
                raise ValueError("Only FIRST of five mentioned chart readings is supplied")
        if i==5:
            if ranked["case_id"]!=c["case_id"] or len(ranked["candidates"])!=5:
                raise ValueError("One-chart five-candidate ranking incomplete")
            if sorted(x["palace"] for x in ranked["candidates"])!=[1,2,3,4,6]:
                raise ValueError("Candidate palace assignments differ from book")
            if sorted(x["reported_final_rank"] for x in ranked["candidates"])!=list(range(1,6)):
                raise ValueError("Five complete book-reported ranks required")
            if sorted(x["author_predicted_rank"] for x in ranked["candidates"] if x["author_predicted_rank"] is not None)!=[1,2]:
                raise ValueError("Do not pretend author predicted ranks 3-5")
        # Case4's line144 contains early interpretation and subsequent narrative.
        # One-shot question stops just BEFORE the author started casting.
        initial=source_line(lines,c["question"])
        if i==4:
            cut="于是，我便用信笺纸起了个局"
            if cut not in initial:raise ValueError("Case4 original question cannot be isolated")
            initial=initial.split(cut,1)[0]
            if "阴历六月份" in initial:raise ValueError("Later prediction leaked into initial question")
        records.append((c,cells,steps,initial))
    for m in methods:
        source_line(lines,[m["source_line"],m["source_line"]])
    return lines,methods,records,ranked

def import_employment_chapter(db_path,source_file):
    raw=Path(source_file).read_bytes()
    lines,methods,records,ranked=prepare(raw)  # all five checked first
    import_section(db_path,"shenqi",KEY,TITLE,raw.decode("utf-8"))
    initialize(db_path)
    with connect(db_path) as db:
        s=db.execute("""SELECT section_id FROM sections WHERE book_id='shenqi'
            AND section_key=? AND sha256=?""",(KEY,SHA)).fetchone()
        if not s:raise ValueError("Exact full source section not found")
        section_id=s[0]
        old=db.execute("SELECT source_sha256 FROM chapter_knowledge WHERE chapter_key=?",(CHAPTER,)).fetchone()
        if old is None:
            db.execute("""INSERT INTO chapter_knowledge
              (chapter_key,book_id,title,source_sha256,source_length_bytes,knowledge_version,review_status)
              VALUES (?,'shenqi',?,?,?,'1','draft')""",(CHAPTER,TITLE,SHA,len(raw)))
        elif old[0]!=SHA:raise ValueError("Previously registered original chapter changed")
        for m in methods:
            n=m["source_line"];key=m["concept_id"]
            txt=source_line(lines,[n,n])
            old=db.execute("""SELECT original_excerpt,metadata_json FROM semantic_assertions
                WHERE chapter_key=? AND concept_id=? AND source_start_line=?""",
                (CHAPTER,key,n)).fetchone()
            if old is None:
                db.execute("""INSERT INTO semantic_assertions
                  (chapter_key,concept_id,kind,relation,source_start_line,
                   source_end_line,metadata_json,original_excerpt,review_status)
                  VALUES (?,?,'employment_domain_method','source_condition_candidate',
                   ?,?,?,?,'draft')""",(CHAPTER,key,n,n,canon(m),txt))
            elif old!=(txt,canon(m)):
                raise ValueError("Original source assertion differs, no overwrite")
        for c,cells,steps,initial in records:
            cid=c["case_id"]
            author_text="\n\n".join(row[3] for row in steps)
            judgment="\n".join(source_line(lines,[n,n]) for n in c["pred"])
            verification="\n".join(source_line(lines,[n,n]) for n in c["validation"])
            desired=(section_id,cid,"employment",initial,author_text,judgment,verification)
            old=db.execute("""SELECT section_id,event_family_id,domain_id,known_before,
                 author_yongshen_steps,author_judgment,later_feedback
                 FROM cases WHERE case_id=?""",(cid,)).fetchone()
            if old is None:
                db.execute("""INSERT INTO cases
                 (case_id,section_id,event_family_id,domain_id,known_before,
                  author_yongshen_steps,author_judgment,later_feedback,reviewed)
                 VALUES (?,?,?,?,?,?,?,?,0)""",(cid,*desired))
            elif old!=desired:
                raise ValueError("Existing original whole case changed, no overwrite")
            meta={"source_sha256":SHA,"source_span":c["span"],"chart_groups":c["chart_source_groups"],
                "book_success_default":True,"case_relation":c["role"],"cast":c["time"],
                "hour_ganzhi":c["hour"],"dun":c["dun"],"ju":c["ju"],
                "uncast_additional_predictions":4 if c["index"]==4 else 0,
                "one_cast_one_complete_reading":True,"source_not_recast":True,
                "notes":c["notes"]}
            old=db.execute("SELECT case_source_sha256 FROM historical_case_protocol WHERE case_id=?",
                           (cid,)).fetchone()
            if old is None:
                db.execute("""INSERT INTO historical_case_protocol
                   (case_id,completeness,published_chart_verification,
                    feedback_independently_verified,eligible_blind_test,case_source_sha256,metadata_json)
                   VALUES (?,'one_source_chart_full_book_analysis',
                    'compact_nine_palace_original_not_independently_cast',
                    0,0,?,?)""",(cid,SHA,canon(meta)))
            elif old[0]!=SHA:raise ValueError("Old case chart SHA conflict")
            for palace,source_anchor,name,deity,door,star in cells:
                wanted=(source_anchor,name,deity,door,star)
                old=db.execute("""SELECT source_line,palace_label_raw,deity_raw,
                        door_position_raw,star_position_raw
                        FROM historical_chart_cells WHERE case_id=? AND palace=?""",
                       (cid,palace)).fetchone()
                if old is None:
                    db.execute("""INSERT INTO historical_chart_cells
                      (case_id,palace,source_line,palace_label_raw,deity_raw,
                       door_position_raw,star_position_raw) VALUES (?,?,?,?,?,?,?)""",
                      (cid,palace,*wanted))
                elif old!=wanted:raise ValueError("Original book palace changed")
            for j,a,b,original,topic in steps:
                old=db.execute("""SELECT source_line,author_analysis_original
                       FROM historical_case_reasoning WHERE case_id=? AND step_number=?""",
                      (cid,j)).fetchone()
                if old is None:
                    db.execute("""INSERT INTO historical_case_reasoning
                       (case_id,step_number,source_line,author_analysis_original,
                        short_method_topic,metadata_json) VALUES (?,?,?,?,?,?)""",
                        (cid,j,a,original,topic,canon({"original_source_span":[a,b],
                         "complete_author_step_not_new_case":True})))
                elif old!=(a,original):raise ValueError("Author full reasoning step changed")
            for n in c["validation"]:
                stmt=source_line(lines,[n,n])
                old=db.execute("""SELECT original_statement FROM historical_case_disclosures
                     WHERE case_id=? AND source_line=?""",(cid,n)).fetchone()
                if old is None:
                    db.execute("""INSERT INTO historical_case_disclosures
                       (case_id,source_line,phase,fact_type,original_statement)
                       VALUES (?,?,'same_event_book_validation','validation_information',?)""",
                       (cid,n,stmt))
                elif old[0]!=stmt:raise ValueError("Original book validation differs")
            wanted=(cid,"author_book_success_default",0,"[]",canon(c["validation"]),
                   "not_verified","single_answer_for_one_cast","book_source_only",
                   "User default book success without independent real-world validation")
            old=db.execute("""SELECT primary_case_id,verdict,explicit_source_correction,
                source_correction_lines_json,feedback_source_lines_json,
                independent_external_verification,app_output_protocol,
                evidence_review_status,note FROM historical_case_book_verdicts
                WHERE event_family_id=?""",(cid,)).fetchone()
            if old is None:
                db.execute("""INSERT INTO historical_case_book_verdicts
                   (event_family_id,primary_case_id,verdict,explicit_source_correction,
                    source_correction_lines_json,feedback_source_lines_json,
                    independent_external_verification,app_output_protocol,evidence_review_status,note)
                   VALUES (?,?,?,?,?,?,?,?,?,?)""",(cid,*wanted))
            elif old!=wanted:raise ValueError("Existing original book verdict differs")
        # Unnumbered source notes still belong to the SAME story, not a new case.
        additions=[
          (records[0][0]["case_id"],"initial_directional_method",[44,44]),
          (records[1][0]["case_id"],"same_cast_november_followup",[91,93]),
          (records[3][0]["case_id"],"other_four_casts_not_supplied",[150,150]),
          (records[4][0]["case_id"],"five_candidates_assigned_to_palaces",[206,206]),
          (records[4][0]["case_id"],"author_editor_review",[226,228])
        ]
        for cid,kind,loc in additions:
            stmt=source_line(lines,loc)
            old=db.execute("""SELECT original_text FROM historical_case_source_segments
               WHERE case_id=? AND segment_kind=? AND source_start_line=?""",
               (cid,kind,loc[0])).fetchone()
            if old is None:
                db.execute("""INSERT INTO historical_case_source_segments
                 (case_id,segment_kind,source_start_line,source_end_line,original_text,metadata_json)
                 VALUES (?,?,?,?,?,?)""",(cid,kind,*loc,stmt,
                  canon({"historical_same_event":True,"independent_new_cast":False})))
            elif old[0]!=stmt:raise ValueError("Source case note changed")
        fifth=records[4][0]["case_id"]
        for i,candidate in enumerate(ranked["candidates"],1):
            cid=f"candidate_{i}"
            wanted=(candidate["name"],candidate["palace"],candidate["source_line"],
                    candidate["author_analysis_line"],candidate["author_predicted_rank"],
                    candidate["reported_final_rank"],canon({"source_reported_rank":True,
                    "author_only_predicted_first_and_second":True}))
            old=db.execute("""SELECT candidate_name_private,assigned_palace,assignment_source_line,
                analysis_source_line,predicted_rank,book_reported_rank,metadata_json
                FROM historical_event_candidates WHERE case_id=? AND candidate_key=?""",
                (fifth,cid)).fetchone()
            if old is None:
                db.execute("""INSERT INTO historical_event_candidates
                 (case_id,candidate_key,candidate_name_private,assigned_palace,
                  assignment_source_line,analysis_source_line,predicted_rank,book_reported_rank,
                  metadata_json) VALUES (?,?,?,?,?,?,?,?,?)""",
                  (fifth,cid,*wanted))
            elif old!=wanted:raise ValueError("Historical candidate assignment changed")
        result={}
        for table in ("cases","historical_chart_cells","historical_case_reasoning",
                      "historical_case_source_segments","historical_event_candidates"):
            where="section_id=?" if table=="cases" else "case_id IN (SELECT case_id FROM cases WHERE section_id=?)"
            result[table]=db.execute(f"SELECT count(*) FROM {table} WHERE {where}",
                                     (section_id,)).fetchone()[0]
        result["methods"]=db.execute("SELECT count(*) FROM semantic_assertions WHERE chapter_key=?",
                                      (CHAPTER,)).fetchone()[0]
    return {"chapter":CHAPTER,"source_sha256":SHA,"source_cases":result["cases"],
            "nine_palace_raw_cells":result["historical_chart_cells"],
            "numbered_author_reasoning_steps":result["historical_case_reasoning"],
            "source_segments":result["historical_case_source_segments"],
            "candidate_rank_records":result["historical_event_candidates"],
            "method_candidates":result["methods"],"all_book_success_default":True}
