"""One-shot historical event families with source-internal author verdicts.

Read-view selection is about data provenance for source learning; it does
NOT create a multi-turn user-facing chat. Original after-the-event facts
are only visible in source_study mode, not in candidate-generation context.
"""
from __future__ import annotations
from .database import connect

def get_whole_event(db_path,event_family_id,*,view="one_shot_question"):
    if view not in ("one_shot_question","source_study"):
        raise ValueError("Unknown read-view")
    with connect(db_path) as db:
        cases=db.execute("""SELECT case_id,domain_id,known_before,author_yongshen_steps,
            author_judgment,later_feedback FROM cases WHERE event_family_id=?
            ORDER BY case_id""",(event_family_id,)).fetchall()
        if not cases:raise ValueError("Unknown event family")
        if len(cases)!=1:
            raise ValueError("This implementation expects one documented source chart per family; multi-chart family must have explicit time versions")
        cid,domain,known,steps,prediction,feedback=cases[0]
        chart=db.execute("""SELECT palace,source_line,palace_label_raw,deity_raw,
            door_position_raw,star_position_raw FROM historical_chart_cells
            WHERE case_id=? ORDER BY palace""",(cid,)).fetchall()
        if len(chart)!=9:
            raise ValueError("One complete original nine-palace chart required")
        verdict=db.execute("""SELECT verdict,explicit_source_correction,
            independent_external_verification,app_output_protocol
            FROM historical_case_book_verdicts WHERE event_family_id=?""",
            (event_family_id,)).fetchone()
        if not verdict:raise ValueError("Book verdict not registered")
        result={"event_family_id":event_family_id,"domain_id":domain,
            "known_before":known,"one_shot":True,"one_source_chart":[
              {"palace":p,"source_line":line,"palace_label_raw":label,
               "deity_raw":deity,"door_position_raw":door,"star_position_raw":star}
               for p,line,label,deity,door,star in chart],
            "book_outcome_label":verdict[0],
            "external_verification":verdict[2],
            "book_verdict_is_not_independent_accuracy":True}
        if view=="source_study":
            author=db.execute("""SELECT step_number,source_line,author_analysis_original,
                short_method_topic FROM historical_case_reasoning
                WHERE case_id=? ORDER BY step_number""",(cid,)).fetchall()
            validation=db.execute("""SELECT source_line,phase,fact_type,original_statement
                FROM historical_case_disclosures WHERE case_id=?
                ORDER BY source_line""",(cid,)).fetchall()
            result.update({"author_analysis_steps":[
                {"step":n,"source_line":line,"original_text":txt,"topic":topic}
                for n,line,txt,topic in author],
                "author_judgment":prediction,
                "validation_information":[
                  {"source_line":n,"original_text":txt,"source_phase":phase,
                   "fact_type":typ} for n,phase,typ,txt in validation],
                "original_later_feedback":feedback})
        return result
