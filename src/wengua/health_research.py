"""Research-only case retrieval and health-domain source method planning.

Allows studying an author's decision process without revealing author judgment
or later outcome in the initial-question view. No real medical diagnosis.
"""
from __future__ import annotations
import json
from pathlib import Path
from .database import connect,ROOT

INDEX=ROOT/"data/knowledge/shenqi/health_prediction_ch01/case_index.json"
METHOD=ROOT/"data/knowledge/shenqi/health_prediction_ch01/method_index.json"
SUPPORTED_RELATIONS={"self":"self","father":"father","nephew":"nephew",
                     "older_relative":"aunt"}
def _load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def health_method_plan(subject_relation,question_subtype="health"):
    """Keep case-specific relations conditional; never fabricate spouse's stem."""
    if question_subtype not in ("health","treatment","discharge","travel_for_treatment"):
        raise ValueError("Unsupported health subtopic")
    if subject_relation not in SUPPORTED_RELATIONS:
        return {"status":"needs_domain_specific_relationship_method",
                "subject_relation":subject_relation,"selected_person_yongshen":[],
                "no_personal_stem_fabricated":True}
    target=SUPPORTED_RELATIONS[subject_relation]
    method=_load(METHOD)
    personal=[r for r in method["yongshen_rules"] if r["concept_id"]==f"health:role:{target}"]
    if not personal:raise ValueError("Missing source role profile")
    disease=[r for r in method["yongshen_rules"] if r["priority"] in ("primary","treatment")]
    return {"status":"draft_research_method_not_medical_advice",
            "subject_relation":subject_relation,"question_subtype":question_subtype,
            "personal_reference":personal[0],
            "disease_and_treatment_candidates":disease,
            "body_palaces":method["body_palace_mappings"],
            "reasoning_sequence":method["author_workflow_nodes"],
            "independent_professional_validation":False,
            "medical_advice_prohibited":True}

def retrieve_historical_case(db_path,case_id,*,view="initial_question"):
    """Initial question excludes every author step, prediction, and feedback.

    The source_study view intentionally reveals all parts for source analysis.
    It is NOT appropriate for sealed/held-out evaluation prompts.
    """
    if view not in ("initial_question","source_study"):
        raise ValueError("Only two explicit views; no implicit leaked fields")
    index=_load(INDEX)
    known_ids={x["event_family_id"] for x in index["cases"]}
    if case_id not in known_ids:
        raise ValueError("Case ID is not a registered historical family")
    with connect(db_path) as db:
        base=db.execute("""SELECT known_before,author_yongshen_steps,
                          author_judgment,later_feedback FROM cases WHERE case_id=?""",
                          (case_id,)).fetchone()
        proto=db.execute("""SELECT completeness,published_chart_verification,
            eligible_blind_test FROM historical_case_protocol WHERE case_id=?""",
            (case_id,)).fetchone()
        if base is None or proto is None:
            raise ValueError("Case not imported into this private SQLite")
        cells=db.execute("""SELECT palace,palace_label_raw,deity_raw,
            door_position_raw,star_position_raw FROM historical_chart_cells
            WHERE case_id=? ORDER BY palace""",(case_id,)).fetchall()
        if len(cells)!=9:
            raise ValueError("Historical source chart is missing a palace")
        result={"case_id":case_id,"event_family_id":case_id,
            "status":"historical_source_not_clinical_guidance",
            "known_before":base[0],
            "verbatim_chart_cells":[{"palace":p,"source_palace":name,
                                     "deity_raw":deity,"door_position_raw":door,
                                     "star_position_raw":star}
                                    for p,name,deity,door,star in cells],
            "chart_source_status":proto[1],
            "eligible_blind_test":bool(proto[2]),
            "raw_chart_is_not_independent_algorithm_recast":True,
            "multi_turn_disclosures_unavailable_in_initial_question":True}
        if view=="source_study":
            steps=db.execute("""SELECT step_number,source_line,author_analysis_original,
                short_method_topic FROM historical_case_reasoning
                WHERE case_id=? ORDER BY step_number""",(case_id,)).fetchall()
            turns=db.execute("""SELECT source_line,phase,fact_type,original_statement
                FROM historical_case_disclosures WHERE case_id=? ORDER BY source_line""",
                (case_id,)).fetchall()
            result.update({"author_reasoning":[{"step":n,"source_line":line,
                "author_source_text":author,"topic":topic}
                for n,line,author,topic in steps],
                "author_judgment":base[2],"later_feedback":base[3],
                "progressive_disclosures":[{"source_line":line,"phase":phase,
                    "type":kind,"source_text":txt} for line,phase,kind,txt in turns]})
        return result
