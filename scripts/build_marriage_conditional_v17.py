"""Append V1.7 verbatim 27 book rules and new family-replay error limits.

One source-preserving SQLite backup from V1.6 SHA, never reinitialize or
override any original book rows. Inherited 3 older DEV questions retain
1 book match and 2 incorrect results; new families 04/05 have NO scoreable
future observed label and are recorded as abstentions, not success.
"""
from __future__ import annotations
import argparse,hashlib,json,sqlite3
from pathlib import Path
from src.wengua.marriage_book_combinator_v17 import load_author_source_rules
from scripts.evaluate_marriage_other_families_v17 import evaluate
ROOT=Path(__file__).resolve().parents[1]
PARENT_NAME="WenguaApp_双书194案例_婚姻作者式判断与家族留出评测V1_6_完整研究库.sqlite3"
NEW_NAME="WenguaApp_双书194案例_婚姻多证据条件与新增家族验证V1_7_完整研究库.sqlite3"
PARENT_SHA="89cd5eb51f4eec7e41092a2bb8f5f624c1c6e7e4eb2225d00051e2d6c8e4a5f4"
MIG=ROOT/"schema/migrations/045_marriage_conditional_combinations_other_family_v17.sql"
def digest(b):return hashlib.sha256(b).hexdigest()
def canon(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":"))
def preserve(old,new):
 for (table,) in old.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"):
  cols=[r[1] for r in old.execute('PRAGMA table_info("'+table+'")')]
  names=",".join('"'+k+'"' for k in cols)
  oldrows=list(old.execute('SELECT '+names+' FROM "'+table+'"'))
  newrows=set(new.execute('SELECT '+names+' FROM "'+table+'"'))
  if any(row not in newrows for row in oldrows):
   raise ValueError("Original family, source, or previous error record changed: "+table)
def build(parent,output,indexdir):
 parent,output,indexdir=map(Path,(parent,output,indexdir))
 if output.exists():raise ValueError("Cannot overwrite prior complete V1.7 archive")
 if digest(parent.read_bytes())!=PARENT_SHA:
  raise ValueError("Expected exact SHA of full 194-source-case marriage V1.6 parent")
 rules,pairs=load_author_source_rules()
 fresh=evaluate(db_path=parent)
 if (len(rules)!=27 or len(pairs)!=81
     or len(fresh["before_feedback_initial_study"])!=2
     or fresh["actual_new_forecast_correctness_scores"]!=0):
  raise ValueError("Cannot fake missing book method or unknown future result")
 output.parent.mkdir(parents=True,exist_ok=True)
 with sqlite3.connect("file:"+str(parent.resolve())+"?mode=ro",uri=True) as old,sqlite3.connect(output) as db:
  old.backup(db)
  db.executescript(MIG.read_text(encoding="utf8"))
  db.execute("PRAGMA foreign_keys=ON")
  with db:
   for r in rules.values():
    db.execute("""INSERT INTO marriage_v17_book_conditional_rules
      (rule_id,book_id,chapter_key,source_line,source_sha256,exact_excerpt_sha256,
       original_book_line,conditional_rule_json,positive_condition_description,
       counterexample_or_conflict,when_and_how_timing_applies)
      VALUES (?,?,?,?,?,?,?,?,?,?,?)""",(
        r["rule_id"],r["book_id"],r["source_section_key"],r["source_line"],
        r["source_sha256"],r["excerpt_sha256"],r["original_line"],canon(r),
        r["positive_source_condition"],r["negative_or_counterexample"],
        r["timing_trigger_and_scope"]))
   for i,row in enumerate(fresh["before_feedback_initial_study"]):
    item=row["initial_source_judgment"]
    if item is None or item["outcome"]!="unresolved":
     raise ValueError("Missing actual partner cannot be promoted to decisive source result")
    family=row["family"]
    if family not in ("kaiwu.marriage.case04","kaiwu.marriage.case05"):
     raise ValueError("Different family must require separate experiment")
    after=fresh["after_initial_author_comments"][i]
    subject=int(family.endswith("case04"))
    first=canon({"initial":item,"source_chart_alignment":row["source_chart_alignment"]})
    db.execute("""INSERT INTO marriage_v17_new_event_family_replays
      (study_id,heldout_event_family_id,source_original_chart_aligned,
       compared_printed_outer_palaces,original_question,subject_year_supplied,
       partner_year_supplied,initial_traditional_verdict,computed_source_rule_count,
       exact_directional_tengan_pair_count,first_inference_trace_json,
       source_author_comments_after_inference_json)
      VALUES (?, ?,1,8, ?,?,0,'unresolved',27,81,?,?)""",
      ("marriage.v17.new_family."+str(i+1),family,
       "现交往男友的恋爱走向如何？" if subject else "前夫要求复婚，复婚是否合适及何时办理？",
       subject,first,canon(after)))
   db.execute("""INSERT INTO marriage_v17_rule_change_and_error_audit
    (audit_version,previous_complete_sqlite_sha256,original_historical_cases_preserved,
     previous_source_dev_total,previous_dev_correct,previous_dev_wrong_kept,
     new_original_rule_entries,new_other_family_replays,new_other_family_scoreable_future_results,
     all_parent_database_rows_unchanged,note_json)
    VALUES ('marriage.v17.multi_evidence.new_families',?,194,3,1,2,27,2,0,1,?)""",
    (PARENT_SHA,canon({
     "existing_dev_case02_and_case03_answers_must_not_be_used_to_fit_threshold":True,
     "new_cases_04_and_05_have_incomplete_partner_birth_years":True,
     "case05_lacks_post_remarriage_actual_success_feedback":True,
     "case06_author_admitted_error_is_negative_control_never_sex_orientation_diagnosis":True,
     "no_sealed_untouched_test_opened":True,
     "twenty_four_factor_complete_evidence_still_pending":True,
     "source_27_conditions_are_not_proven_marriage_prediction":True,
     "directional_stem_pair_source_count":81})))
  preserve(old,db)
  if db.execute("PRAGMA integrity_check").fetchone()[0]!="ok" or db.execute("PRAGMA foreign_key_check").fetchall():
   raise ValueError("Complete old book and model result source rows were corrupted")
  db.execute("VACUUM");db.commit()
  names=["cases","sections","historical_chart_cells","marriage22_scenario_protocol",
         "marriage_runtime_scenario_study","phrase_intent_workflows","book_timing_method_source_rules",
         "marriage_v16_historical_holdout_inputs","marriage_v16_historical_initial_verdicts",
         "marriage_v16_post_inference_labels","marriage_v16_family_dev_audit",
         "marriage_v17_book_conditional_rules","marriage_v17_new_event_family_replays",
         "marriage_v17_rule_change_and_error_audit"]
  counts={n:db.execute('SELECT COUNT(*) FROM "'+n+'"').fetchone()[0] for n in names}
  exp={"cases":194,"sections":43,"historical_chart_cells":1440,
    "marriage22_scenario_protocol":22,"marriage_runtime_scenario_study":44,
    "phrase_intent_workflows":9,"book_timing_method_source_rules":20,
    "marriage_v16_historical_holdout_inputs":3,
    "marriage_v16_historical_initial_verdicts":3,
    "marriage_v16_post_inference_labels":3,"marriage_v16_family_dev_audit":1,
    "marriage_v17_book_conditional_rules":27,
    "marriage_v17_new_event_family_replays":2,
    "marriage_v17_rule_change_and_error_audit":1}
  if counts!=exp:raise ValueError(("Complete DB counts differ",counts,exp))
 report={"version":"marriage_original_source_rule_tree_v1.7",
  "parent_full_sqlite_sha256":PARENT_SHA,
  "new_full_sqlite_sha256":digest(output.read_bytes()),
  "unchanged_historical_book_case_count":194,
  "exact_new_original_conditional_rules":len(rules),
  "81_ordered_kaiwu_stem_pairs_read_with_source":len(pairs),
  "two_new_book_families_tested_without_scoring_unknown_future":2,
  "prior_dev_retained_total":3,"prior_dev_retained_matches":1,"prior_dev_retained_misses":2,
  "new_real_forecast_correctness_verified":0,
  "24_factor_full_inference_approved":False,
  "new_200_chinese_character_GPT_phrases_published":0,
  "source_not_predicted_reality":True,"all_previous_rows_identical":True,
  "new_event_family_study":fresh,"counts":counts}
 indexdir.mkdir(parents=True,exist_ok=True)
 (indexdir/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 return report
if __name__=="__main__":
 parser=argparse.ArgumentParser()
 for k in ("base","output","index-dir"):parser.add_argument("--"+k,required=True)
 a=parser.parse_args()
 print(canon(build(a.base,a.output,a.index_dir)))
