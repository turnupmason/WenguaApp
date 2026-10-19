"""Read one original business event with all genuinely supplied hour-specific charts.

Initial view excludes after-event feedback and author retrospective explanations.
Historical study view returns all author numbered methods, additional real
hourly casts, later validation, and textual-only hours separately.
This is a SOURCE study API, not a prediction engine or financial adviser.
"""
from __future__ import annotations
from .database import connect

def retrieve_business_event(db_path,event_family_id,*,view="initial"):
    if view not in ("initial","source_study"):
        raise ValueError("Unknown research view")
    with connect(db_path) as db:
        event=db.execute("""SELECT case_id,domain_id,known_before,author_judgment,
            later_feedback FROM cases WHERE event_family_id=? AND domain_id='business_profit'""",
            (event_family_id,)).fetchone()
        if not event:raise ValueError("Unknown business source event")
        cid,domain,known,prediction,feedback=event
        base=db.execute("""SELECT palace,source_line,palace_label_raw,deity_raw,
            door_position_raw,star_position_raw FROM historical_chart_cells
            WHERE case_id=? ORDER BY palace""",(cid,)).fetchall()
        if len(base)!=9:raise ValueError("Incomplete source first nine-palace chart")
        tocell=lambda row:dict(zip(
            ("palace","source_line","palace_label_raw","deity_raw","door_position_raw","star_position_raw"),row))
        primary=[tocell(r) for r in base]
        result={
          "event_family_id":event_family_id,"domain":domain,
          "initial_question_source":known,"app_target_reading_count":1,
          "first_genuine_cast":{"chart_cells":primary},
          "outcome_label":"author_book_success_default",
          "book_verdict_not_external_validation":True}
        if view=="source_study":
            raws=db.execute("""SELECT cast_key,cast_datetime_description,
                source_chart_start FROM historical_case_additional_casts WHERE case_id=?
                ORDER BY source_chart_start""",(cid,)).fetchall()
            casts=[]
            for cast_key,when,line in raws:
                cells=db.execute("""SELECT palace,source_line,palace_label_raw,deity_raw,
                   door_position_raw,star_position_raw FROM historical_case_additional_cast_cells
                   WHERE case_id=? AND cast_key=? ORDER BY palace""",(cid,cast_key)).fetchall()
                if len(cells)!=9:raise ValueError("Incomplete additional original source cast")
                casts.append({"cast_key":cast_key,"source_chart_start":line,
                              "historical_datetime":when,
                              "original_chart_cells":[tocell(r) for r in cells]})
            analysis=db.execute("""SELECT step_number,source_line,author_analysis_original,
                metadata_json FROM historical_case_reasoning WHERE case_id=?
                ORDER BY step_number""",(cid,)).fetchall()
            evidence=db.execute("""SELECT source_line,phase,fact_type,original_statement
                FROM historical_case_disclosures WHERE case_id=? ORDER BY source_line""",(cid,)).fetchall()
            segments=db.execute("""SELECT segment_kind,source_start_line,source_end_line,
                original_text FROM historical_case_source_segments WHERE case_id=?
                ORDER BY source_start_line""",(cid,)).fetchall()
            result.update({
              "all_other_supplied_real_casts":casts,
              "source_author_analysis":[{"step":j,"source_line":line,
                  "original_text":txt,"source_metadata":meta}
                 for j,line,txt,meta in analysis],
              "source_author_judgment":prediction,
              "book_validation_information":[{"line":n,"phase":phase,
                  "fact_type":kind,"original_text":txt} for n,phase,kind,txt in evidence],
              "source_editorial_and_text_only_hours":[{"kind":kind,"start":a,
                  "end":b,"original_text":txt} for kind,a,b,txt in segments],
              "original_later_feedback":feedback,
              "second_cast_never_supplements_first_cast_for_blind_original":True
            })
        return result
