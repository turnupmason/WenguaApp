"""Immutable V1.6 append: initial book-method decisions + real error ledger.

Database predecessor V1.5 is SHA-pinned. Existing 194 cases, 43 original
chapters, 22 scene methods, original nine workflows, 20 timing methods, and
all source text rows are kept unchanged. Book validation is inserted into
physically distinct tables AFTER the independent first-judgment record.
"""
from __future__ import annotations
import argparse,hashlib,json,sqlite3
from pathlib import Path
from scripts.evaluate_marriage_family_holdout_v16 import evaluate,QUESTIONS
ROOT=Path(__file__).resolve().parents[1]
OLD="WenguaApp_双书194案例_婚姻原书应期天文推算V1_5_完整研究库.sqlite3"
NEW="WenguaApp_双书194案例_婚姻作者式判断与家族留出评测V1_6_完整研究库.sqlite3"
PARENT_SHA="619867ef0f81234c662fbc1796de1c6844e9c1ecf12f59a904d20f9c90b757f3"
MIG=ROOT/"schema/migrations/044_marriage_source_initial_judgment_and_family_holdout_v16.sql"
INDEX=ROOT/"data/knowledge/phrase_library/marriage_v1_6"
METHOD_INDEX=ROOT/"data/knowledge/shenqi/marriage_prediction_ch02/method_index.json"
def sha(raw):return hashlib.sha256(raw).hexdigest()
def js(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":"))
def preserve(old,new):
 for (name,) in old.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"):
  columns=[c[1] for c in old.execute('PRAGMA table_info("'+name+'")')]
  expression=",".join('"'+c+'"' for c in columns)
  before=list(old.execute('SELECT '+expression+' FROM "'+name+'"'))
  after=set(new.execute('SELECT '+expression+' FROM "'+name+'"'))
  if any(x not in after for x in before):
   raise ValueError("Original archive historical row was overwritten: "+name)
def build(parent,out,indexdir):
 parent,out,indexdir=map(Path,(parent,out,indexdir))
 if out.exists():raise ValueError("No overwrite of versioned complete SQLite")
 if sha(parent.read_bytes())!=PARENT_SHA:
  raise ValueError("Only the latest exact V1.5 complete book source archive may be extended")
 result=evaluate(db_path=parent)
 if not (result["printed_original_chart_alignment_count"]==3
         and result["candidate_questions"]==3 and result["scored_decisive_cases"]==3):
  raise ValueError("Historical source printed charts must be checked before results are archived")
 if result["matched_book_reported_outcomes"]!=1:
  # Freeze today's heldout error count. Any improvements require an explicit
  # NEW version and a different heldout family, not retrospectively relabeling.
  raise ValueError("This frozen V1.6 dev baseline changed: create a NEW validation version")
 sourceindex=json.loads(METHOD_INDEX.read_text(encoding="utf8"))
 full_source_hash=sourceindex["source_sha256"]
 out.parent.mkdir(parents=True,exist_ok=True)
 with sqlite3.connect("file:"+str(parent.resolve())+"?mode=ro",uri=True) as old,sqlite3.connect(out) as db:
  old.backup(db)
  db.executescript(MIG.read_text(encoding="utf8"))
  db.execute("PRAGMA foreign_keys=ON")
  with db:
   rule_ids=["person_palace","traditional_yi_geng","liuhe","book_exception","kaiwu_marriage_case01"]
   db.execute("""INSERT INTO marriage_v16_judgment_contract
    (version,all_domain_six_layer_mandatory,original_method_source_sha256,
     original_source_rule_ids_json,main_actor_birth_year_before_liuhe,
     bidirectional_support_counter_trace,source_timing_only_after_initial_outcome,
     family_holdout_excludes_all_case_variants,book_feedback_never_initial_input,
     no_fake_prediction_accuracy_claim,unsupported_factors_maintain_unknown,
     parent_full_archive_sha256,contract_json)
    VALUES ('marriage.initial_judgment.v1.6',1,?,?,1,1,1,1,1,1,1,?,?)""",
    (full_source_hash,js(rule_ids),PARENT_SHA,js({
     "stage":"development_only_not_validated_predictive_accuracy",
     "book_a": "shenqi/marriage_prediction_ch02/v1",
     "book_b": "kaiwu/marriage_prediction_ch02_section02/v1",
     "recorded_errors_required":True,
     "conditional_outcome_not_personality_accusation":True,
     "no_look_at_post_event_results_when_generating_first_judgment":True,
     "method_scope":"birth-year relationship primary, 六合 secondary, season/door/source breaks",
     "does_not_yet_satisfy_all_24_factor_publication":True})))
   for i,row in enumerate(result["results"]):
    q=QUESTIONS[i]
    (family,iso,day,hour,year,month,term,dun,ju,subject,partner,
     scene,question,expect,firstlines,backlines)=q
    initial=row["initial_inference_without_author_label_or_feedback"]
    if initial is None:raise ValueError("No actual initial inference for a source-aligned historical case")
    study_id="marriage.v16.book_dev."+str(i+1)
    if (row["heldout_event_family_id"]!=family or row["actual_question"]!=question
        or family in initial["book_witness_families_used"]):
     raise ValueError("Source-family leak or story-index drift")
    db.execute("""INSERT INTO marriage_v16_historical_holdout_inputs
    (study_id,heldout_family_id,source_case_id,scene_id,source_civil_iso,
     original_case_chart_deity_door_align,outer_palaces_checked,
     subject_year_ganzhi,partner_year_ganzhi,question_text,question_packet_hash,
     frozen_data_splits)
    VALUES (?,?,?,?,?,1,8,?,?,?,?,'entire_event_family_and_all_book_source_witnesses')""",
    (study_id,family,family,scene,iso,subject,partner,question,
     sha(js({"scene":scene,"question":question,"iso":iso,
        "actors":[subject,partner],"hour":hour,"day":day}).encode())))
    db.execute("""INSERT INTO marriage_v16_historical_initial_verdicts
    (study_id,initial_traditional_outcome,source_author_rule_trace_json,
     source_support_json,source_counter_json,book_method_witness_family_ids_json,
     conditional_timing_json,original_chart_factor_count)
    VALUES (?,?,?,?,?,?,?,?)""",
    (study_id,initial["outcome"],
     js({"rule_family":"shenqi marriage line5,line11;Kaiwu timing conditional",
         "source_first_and_contradiction_separate":True,"reasoning_stage":"before book outcome/feedback",
         "source_case_family_heldout":family}),
     js(initial["support"]),js(initial["counter"]),
     js(initial["book_witness_families_used"]),
     js(initial["other_computed_timing"]) if initial["other_computed_timing"] is not None else None,
     initial["computed_factors"]))
   # This second loop physically inserts sealed AFTER-INFERENCE labels.
   for i,row in enumerate(result["results"]):
    q=QUESTIONS[i]
    label=row["validation_only_later"]
    if (q[14]!=label["original_author_forecast_lines"] or q[15]!=label["later_source_feedback_lines"] or q[13]!=label["book_reported_event_outcome"]):
     raise ValueError("Post-inference label source line mismatch")
    db.execute("""INSERT INTO marriage_v16_post_inference_labels
     (study_id,reported_book_event_result,original_author_first_verdict_lines_json,
      later_feedback_source_lines_json,matches_initial_book_retrospective_result,
      reported_book_result_not_independently_verified)
     VALUES (?,?,?,?,?,1)""",
     ("marriage.v16.book_dev."+str(i+1),label["book_reported_event_outcome"],
      js(label["original_author_forecast_lines"]),
      js(label["later_source_feedback_lines"]),
      int(label["matched_initial_decision"])))
   errors=[{"study":i+1,"family":r["heldout_event_family_id"],
     "question":r["actual_question"],"book_feedback":r["validation_only_later"]["book_reported_event_outcome"],
     "initial_answer":r["initial_inference_without_author_label_or_feedback"]["outcome"]}
     for i,r in enumerate(result["results"]) if not r["validation_only_later"]["matched_initial_decision"]]
   if len(errors)!=2:raise ValueError("Original two model error records must be preserved")
   db.execute("""INSERT INTO marriage_v16_family_dev_audit
    (version,historical_book_cases_preserved,inherited_twenty_two_scenes,
     inherited_twenty_author_timing_methods,parent_archive_sha256,
     source_printed_charts_aligned,scored_event_questions,matched_book_retrospective_events,
     distinct_heldout_event_families,old_historical_rows_unchanged,
     development_errors_json)
    VALUES ('marriage.dev_family_holdout.v1.6',194,22,20,?,3,3,1,2,1,?)""",
    (PARENT_SHA,js(errors)))
  preserve(old,db)
  if db.execute("PRAGMA integrity_check").fetchone()[0]!="ok" or db.execute("PRAGMA foreign_key_check").fetchall():
   raise ValueError("Source-original 194 book case sqlite integrity failed")
  db.execute("VACUUM");db.commit()
  names=["cases","sections","historical_chart_cells","marriage22_scenario_protocol",
         "marriage_runtime_scenario_study","phrase_intent_workflows",
         "book_timing_method_source_rules","marriage_author_time_source_studies",
         "marriage_v16_judgment_contract","marriage_v16_historical_holdout_inputs",
         "marriage_v16_historical_initial_verdicts","marriage_v16_post_inference_labels",
         "marriage_v16_family_dev_audit"]
  counts={name:db.execute('SELECT COUNT(*) FROM "'+name+'"').fetchone()[0] for name in names}
 expected={
  "cases":194,"sections":43,"historical_chart_cells":1440,
  "marriage22_scenario_protocol":22,"marriage_runtime_scenario_study":44,
  "phrase_intent_workflows":9,"book_timing_method_source_rules":20,
  "marriage_author_time_source_studies":1,
  "marriage_v16_judgment_contract":1,"marriage_v16_historical_holdout_inputs":3,
  "marriage_v16_historical_initial_verdicts":3,
  "marriage_v16_post_inference_labels":3,"marriage_v16_family_dev_audit":1}
 if counts!=expected:raise ValueError(("Archive v16 count mismatch",counts,expected))
 report={"schema":"marriage_v16_book_family_heldout_initial_verdict_full_sqlite",
  "complete_parent_archive_sha256":PARENT_SHA,"new_full_sqlite_sha256":sha(out.read_bytes()),
  "prior_original_book_cases_exactly_preserved":194,"old_22_scenes_kept":22,
  "new_executable_author_initial_decisions":3,
  "two_complete_event_families_heldout":2,
  "printed_original_eight_deity_doors_aligned":24,
  "matched_book_reported_feedback_in_dev":1,
  "mismatched_book_reported_feedback_in_dev":2,
  "external_unseen_real_predictions":0,
  "not_a_sealed_untouched_final_blind_test":True,
  "all_parent_rows_unchanged":True,
  "development_source_eval":result,"counts":counts}
 indexdir.mkdir(parents=True,exist_ok=True)
 (indexdir/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 return report
def main():
 p=argparse.ArgumentParser()
 for key in ("base","output","index-dir"):p.add_argument("--"+key,required=True)
 opt=p.parse_args()
 print(js(build(opt.base,opt.output,opt.index_dir)))
if __name__=="__main__":main()
