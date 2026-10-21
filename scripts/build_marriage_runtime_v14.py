"""Build V1.4 complete source-preserving marriage runtime audit SQLite.

This proves existing, actually computed nine-palace symbol layouts can feed
all 22 source-anchored marriage problem methods. The two worked source charts
originate in the *casting book chapter*, not the 14 marriage anecdotes; no
fake subject, intent outcome or dates are attached. Unsupported 24-factor
items are explicitly UNKNOWN rather than filled by GPT.
"""
from __future__ import annotations
import argparse,hashlib,json,sqlite3
from pathlib import Path
from src.wengua.marriage_runtime import (
 SOURCE_EXAMPLES,inspect_marriage_study_cast)
ROOT=Path(__file__).resolve().parents[1]
PARENT_NAME="WenguaApp_双书194案例_婚姻22场景六层流程V1_3_完整研究库.sqlite3"
NEW_NAME="WenguaApp_双书194案例_婚姻真实排盘接入V1_4_完整研究库.sqlite3"
PARENT_SHA="0eda2e3996192c31b7e75aeaf45745c6659dd2a73f5fe74bbf495dece36e6857"
MIG=ROOT/"schema/migrations/042_marriage_source_cast_runtime_bridge.sql"
def h(b):return hashlib.sha256(b).hexdigest()
def js(o):return json.dumps(o,ensure_ascii=False,sort_keys=True,separators=(",",":"))
def preserve(old,db):
 for (table,) in old.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"):
  columns=[row[1] for row in old.execute('PRAGMA table_info("'+table+'")')]
  expression=",".join('"'+x+'"' for x in columns)
  now=set(db.execute('SELECT '+expression+' FROM "'+table+'"'))
  if any(r not in now for r in old.execute('SELECT '+expression+' FROM "'+table+'"')):
   raise ValueError("New runtime import changed original source/book/phrase/22-scene data: "+table)
def build(base,output,index_dir):
 base,output,index_dir=map(Path,(base,output,index_dir))
 if output.exists():raise ValueError("No archive overwrite: use a distinct version")
 if h(base.read_bytes())!=PARENT_SHA:
  raise ValueError("Exact 22-scene complete V1.3 source parent SHA required")
 output.parent.mkdir(parents=True,exist_ok=True)
 examples={
  "shenqi_casting_example_1995_06_11":{
    "day_ganzhi":"癸酉","solar_term":"芒种","hour_ganzhi":"丁巳"},
  "shenqi_casting_example_1995_08_13":{
    "day_ganzhi":"丙子","solar_term":"立秋","hour_ganzhi":"戊戌"}}
 statuses={}
 distinct=[]
 with sqlite3.connect("file:"+str(base.resolve())+"?mode=ro",uri=True) as old,sqlite3.connect(output) as db:
  old.backup(db)
  db.executescript(MIG.read_text("utf8"))
  db.execute("PRAGMA foreign_keys=ON")
  with db:
   for example_key,data in examples.items():
    if example_key not in SOURCE_EXAMPLES:
     raise ValueError("Cannot reconstruct an unauthored source-example chart")
    first=inspect_marriage_study_cast(db_path=base,scene_id="marriage.scene.02",
      example_key=example_key,people=None,**data)
    bureau=first["bureau_from_explicit_term"]
    chart=first["source_chart"]
    if chart["status"]!="source_text_consistency_only":
     raise ValueError("Do not falsely promote external calendar trust")
    if first["factor_checked_count"]!=24 or len(chart["palaces"])!=9:
     raise ValueError("Must audit every palace and all 24 named factors")
    db.execute("""INSERT INTO marriage_runtime_source_cast_fixture
     (fixture_id,casting_school,casting_method,day_ganzhi,supplied_solar_term,
      derived_dun,derived_ju,hour_ganzhi,nine_palace_layout_json,
      layout_sha256,verified_original_nine_palace_cells,
      physical_factors_audited,factor_results_json,book_citation_note)
     VALUES (?,'shijia_zhuanpan',?,?,?,?,?,?,?,?,9,24,?,?)""",
     (example_key,chart["casting_variant"],data["day_ganzhi"],
      data["solar_term"],bureau["dun"],bureau["ju"],data["hour_ganzhi"],
      js(chart),h(js(chart).encode()),js(first["factor_audit"]),
      "Complete worked diagram from Shenqi book casting chapter01, not a marriage question; supplied calendar is not independently astronomy-verified"))
    for num in range(1,23):
     scene=f"marriage.scene.{num:02d}"
     run=first if num==2 else inspect_marriage_study_cast(db_path=base,
         scene_id=scene,example_key=example_key,people=None,**data)
     if run["scene_id"]!=scene or run["traditional_forecast_result"] is not None or run["human_natural_phrase"] is not None:
      raise ValueError("This is only factual layout and provenance path, no fabricated forecasts")
     original=run["author_first_and_method_source_links"]
     feedback=run["source_later_feedback_validation_only"]
     if not original or len(run["factor_audit"])!=24:raise ValueError("Source/book/full factors incomplete")
     db.execute("""INSERT INTO marriage_runtime_scenario_study
      (fixture_id,scene_id,book_original_method_ref_count,
       candidate_yongshen_palaces_json,initial_book_witness_refs_json,
       validation_book_feedback_refs_json,missing_real_forecast_inputs_json,
       study_status)
      VALUES (?,?,?,?,?,?,?,'research_partial_chart_pipeline_not_final_forecast')""",
      (example_key,scene,len(original),js(run["role_candidates_not_final_yongshen"]),
       js(original),js(feedback),js(run["missing_to_publish"])))
     distinct.append((example_key,scene))
    statuses[example_key]={
      "dun":bureau["dun"],"ju":bureau["ju"],
      "hour_ganzhi":data["hour_ganzhi"],
      "xun_void_branches":first["factor_audit"]["xun_kong"]["evidence"]["xun_kong_branches"],
      "mechanical_door_pressure":first["factor_audit"]["door_press_palace"]["evidence"]["exact_mechanical_door_press_palaces"],
      "resolved_factors":first["factor_mechanically_resolved_count"],
      "factor_count":first["factor_checked_count"],"palace_count":len(chart["palaces"])}
   if len(distinct)!=44:raise ValueError("Every 22-scene method must resolve source text for both complete worked charts")
   db.execute("""INSERT INTO marriage_runtime_study_audit
    (audit_version,full_previous_parent_SHA256,source_cast_fixture_count,
     marriage_scenarios_regression_count,complete_original_book_nine_palace_cells_compared,
     unified_mechanical_factor_slots_per_chart,remaining_method_or_calendar_blockers_json,
     full_previous_rows_unchanged)
    VALUES('marriage.runtime.v1.4',?,2,44,18,24,?,1)""",
    (PARENT_SHA,js({
     "remaining":"real astronomical term + timezone trust, correct middle-door hosting, all 24 book-specific factor rules, subject year and true binding, source-validated composite judgment, genuine calendar event-timing selection",
     "source_examples_do_not_represent_marriage_case_or_actual_people":True,
     "calendar_not_independently_verified":True,
     "cannot_reuse_book_event_outcome_as_fresh_prediction":True,
     "no_synthetic_cases_added":True})))
  preserve(old,db)
  if db.execute("PRAGMA integrity_check").fetchone()[0]!="ok" or db.execute("PRAGMA foreign_key_check").fetchall():
   raise ValueError("SQLite full archive corruption")
  db.execute("VACUUM");db.commit()
  names=["sections","cases","historical_chart_cells","phrase_template_drafts",
         "phrase_intent_workflows","marriage22_scenario_protocol",
         "marriage22_six_layer_steps","marriage22_original_case_links",
         "phrase_context_instances","marriage_runtime_source_cast_fixture",
         "marriage_runtime_scenario_study","marriage_runtime_study_audit"]
  counts={n:db.execute('SELECT COUNT(*) FROM "'+n+'"').fetchone()[0] for n in names}
 expected={"sections":43,"cases":194,"historical_chart_cells":1440,
           "phrase_template_drafts":4,"phrase_intent_workflows":9,
           "marriage22_scenario_protocol":22,"marriage22_six_layer_steps":132,
           "marriage22_original_case_links":89,"phrase_context_instances":0,
           "marriage_runtime_source_cast_fixture":2,"marriage_runtime_scenario_study":44,
           "marriage_runtime_study_audit":1}
 if counts!=expected:raise ValueError(("Study count mismatch",counts,expected))
 result={"schema":"marriage_v14_real_book_cast_source_fact_runtime_integration",
   "full_parent_SQLite_SHA256":PARENT_SHA,
   "new_complete_SQLite_SHA256":h(output.read_bytes()),
   "book_case_count":194,"source_book_sections":43,
   "real_original_casting_book_examples_compared":2,
   "source_chart_palaces_compared":18,
   "all_scene_source_retrieval_checks":44,
   "marriage_question_scenarios":22,
   "factor_slots_in_each_sample":24,
   "real_marriage_questioners_in_source_examples":0,
   "new_verified_external_calendar_dates":0,
   "genuinely_end_to_end_decisive_reading_instances":0,
   "new_gpt_prose_generated_for_nonexistent_casts":0,
   "all_previous_sqlite_rows_unmodified":True,
   "source_comparison_only_not_real_world_accuracy":True,
   "per_sample_analysis":statuses,
   "counts":counts}
 index_dir.mkdir(parents=True,exist_ok=True)
 (index_dir/"manifest.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n","utf8")
 return result
def main():
 p=argparse.ArgumentParser()
 for x in ("base","output","index-dir"):p.add_argument("--"+x,required=True)
 a=p.parse_args()
 print(js(build(a.base,a.output,a.index_dir)))
if __name__=="__main__":main()
