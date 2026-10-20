"""Non-destructive historical+future step trace backfill; lexical is not expert proof."""
from __future__ import annotations
import json
from .database import connect

def lexical_mentions(t):
    v=[]
    for n in "开休生伤杜景死惊":
        if n+"门" in t:v.append("door:"+n)
    for n in "蓬任冲辅英芮柱心禽":
        if "天"+n in t:v.append("star:"+n)
    for n in ("玄武","白虎","九天","九地","六合","太阴","螣蛇","值符"):
        if n in t:v.append("deity:"+n)
    for n in ("乾","坤","巽","离","震","兑","艮","坎"):
        if n+"宫" in t:v.append("trigram:"+n)
    return sorted(set(v))

def backfill_existing_case_traces(db):
    """Creates trace candidates for EVERY stored author step incl. legacy; never approved."""
    rows=db.execute("""SELECT case_id,step_number,source_line,author_analysis_original,short_method_topic
      FROM historical_case_reasoning ORDER BY case_id,step_number""").fetchall()
    created=0
    for cid,k,line,original,topic in rows:
        old=db.execute("SELECT 1 FROM historical_case_reasoning_trace WHERE case_id=? AND step_number=?",(cid,k)).fetchone()
        if old:continue
        entry={"case_id":cid,"source_step":k,"source_line":line,
           "author_original_retained_in_private_sqlite":True,
           "lexical_concept_candidates_not_validated_rules":lexical_mentions(original),
           "original_topic":topic,"subject_relation":"requires_human_source_review",
           "actual_palace_evidence":"requires_human_source_review",
           "cross_chapter_condition_links":"requires_human_source_review",
           "supporting_counterevidence":"requires_human_source_review",
           "yingqi":"requires_human_source_review",
           "initial_vs_hindsight":"requires_human_source_review",
           "positive_training_eligible":False,"review_status":"mechanical_source_link_needs_author_chain_review"}
        db.execute("""INSERT INTO historical_case_reasoning_trace
          (case_id,step_number,source_line,evidence_json,review_status,positive_training_eligible)
          VALUES (?,?,?,?,'mechanical_source_link_needs_author_chain_review',0)""",
          (cid,k,line,json.dumps(entry,ensure_ascii=False,sort_keys=True)))
        created+=1
    return {"created":created,"total":len(rows),"human_reviewed_complete":0}

def get_case_trace(db_path,case_id,view="initial_question"):
    if view not in ("initial_question","source_study"):raise ValueError("Invalid view")
    with connect(db_path) as c:
        row=c.execute("SELECT known_before,author_judgment,later_feedback FROM cases WHERE case_id=?",(case_id,)).fetchone()
        if not row:raise ValueError("Unknown case")
        chart=c.execute("""SELECT palace,palace_label_raw,deity_raw,door_position_raw,star_position_raw
            FROM historical_chart_cells WHERE case_id=? ORDER BY palace""",(case_id,)).fetchall()
        if len(chart)!=9:raise ValueError("Nine true source palace cells required")
        v={"known_before":row[0],"original_palace_cells":chart,"case_id":case_id}
        if view=="source_study":
            v["author_judgment"]=row[1];v["later_feedback"]=row[2]
            v["author_step_traces"]=[json.loads(r[0]) for r in c.execute(
            "SELECT evidence_json FROM historical_case_reasoning_trace WHERE case_id=? ORDER BY step_number",(case_id,))]
            v["subsequent_disclosures"]=c.execute("""SELECT source_line,phase,fact_type,original_statement
             FROM historical_case_disclosures WHERE case_id=? ORDER BY source_line""",(case_id,)).fetchall()
        return v


def attach_lost_property_source_drafts(db, index_path=None):
    """Apply line-anchored evidence/contrast outlines, but never auto-approve."""
    from pathlib import Path
    from .database import ROOT
    if index_path is None:
        index_path=ROOT/"data/knowledge/shenqi/lost_money_property_prediction_ch09/author_reasoning_evidence_index.json"
    data=json.loads(Path(index_path).read_text(encoding="utf8"))
    if data["source_sha256"]!="ed3c80f32c213563bf35d9f9790e330ea04e4def404f6e6ca904006a94a9eaf9":
        raise ValueError("Source-specific evidence hash mismatch")
    if len(data["cases"])!=8 or sum(len(c["steps"]) for c in data["cases"])!=36:
        raise ValueError("Incomplete source reasoning steps")
    count=0
    for case in data["cases"]:
        cid=case["case_id"]
        for step in case["steps"]:
            k=step["step_number"];line=step["source_line"]
            actual=db.execute("""SELECT source_line FROM historical_case_reasoning
              WHERE case_id=? AND step_number=?""",(cid,k)).fetchone()
            if actual!=(line,):raise ValueError("Original author step does not match index")
            before=db.execute("""SELECT review_status,evidence_json FROM historical_case_reasoning_trace
              WHERE case_id=? AND step_number=?""",(cid,k)).fetchone()
            if before is None:raise ValueError("Case trace missing")
            if before[0]=="human_verified_complete_author_chain":continue
            if before[0]=="source_grounded_reconstruction_draft_human_review_required":
                if json.loads(before[1])!=step:raise ValueError("Previously imported source draft differs")
                continue
            if before[0]!="mechanical_source_link_needs_author_chain_review":
                raise ValueError("Unrecognized review status, refusing overwrite")
            db.execute("""UPDATE historical_case_reasoning_trace
               SET evidence_json=?,review_status='source_grounded_reconstruction_draft_human_review_required',
                   positive_training_eligible=0 WHERE case_id=? AND step_number=?""",
               (json.dumps(step,ensure_ascii=False,sort_keys=True),cid,k))
            count+=1
    return {"source_draft_step_links_added":count,"approved":0}
