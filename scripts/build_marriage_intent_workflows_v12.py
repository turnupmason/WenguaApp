"""Append source-anchored workflows for nine marriage question intents to V1.1.

All workflow definitions are author-method research artifacts, not precomputed
decisive forecasts. Versioned complete SQLite backup preserves every previous
source case, source phrase draft and timing requirement.
"""
from __future__ import annotations
import argparse,hashlib,json,sqlite3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PARENT_NAME="WenguaApp_双书194案例_婚姻断语V1_1_应期强制_完整研究库.sqlite3"
OUTPUT_NAME="WenguaApp_双书194案例_婚姻各类问事流程V1_2_完整研究库.sqlite3"
PARENT_SHA="53bab00cefa4754753ab124b0653c0b7b2f68f0d63dae7783f6eea3d387f0e75"
CONF=ROOT/"data/knowledge/phrase_library/marriage_v1_2/intent_workflows.json"
MIG=ROOT/"schema/migrations/040_marriage_intent_workflow_sources.sql"
VERSION="marriage.intent.v1.2"
EXPECTED_IDS={
 "relationship_form","marriage_proposal","marriage_registration",
 "wedding_date","marriage_stability","divorce","reconciliation",
 "remarriage","trust_question"}
STEP_SEQUENCE=[
 "resolve_query","role_bind","select_primary_secondary",
 "evaluate_support","evaluate_counterevidence","form_outcome",
 "calculate_timing","write_and_audit"]
def sha(v):return hashlib.sha256(v).hexdigest()
def jsonv(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(",",":"))
def validate_config(raw):
 j=json.loads(raw)
 if j.get("schema")!="wengua_marriage_source_anchored_intent_workflows_v1":
  raise ValueError("Unexpected canonical workflow config type")
 if j.get("scope")!="marriage_only" or j.get("intent_count")!=9:
  raise ValueError("Only nine marriage intents; no employment flows")
 if {x["id"] for x in j["selected_intents"]}!=EXPECTED_IDS:
  raise ValueError("Each recognized marriage subtype must have exactly one flow")
 if len(j["selected_intents"])!=9:
  raise ValueError("Duplicate marriage subtype definition")
 if j.get("not_fixed_answers") is not True:
  raise ValueError("Cannot make nine universal fixed marriage answers")
 for x in j["selected_intents"]:
  if len(x["steps"])!=8 or [t["stage"] for t in x["steps"]]!=STEP_SEQUENCE:
   raise ValueError("Incomplete ordered author-style evidence workflow: "+x["id"])
  if not x.get("sources") or not x.get("events") or not x.get("source_support"):
   raise ValueError("A subtype cannot be source-free: "+x["id"])
  for k,r in enumerate(x["sources"],1):
   if not r.get("source_sha256") or not r.get("lines") or not r.get("case_id"):
    raise ValueError("A source row lacks exact book attribution/line: "+x["id"])
   if r["phase_role"]=="later_feedback_date_not_training_label" and x["id"]!="marriage_registration":
    raise ValueError("Later outcome not in dedicated validation role")
 if len(j["common_contract"]["full_chart_audit"])!=24:
  raise ValueError("User-required complete physical relation audit not declared")
 return j
def check_parent_unmodified(old,db):
 for (table,) in old.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"):
  cols=[r[1] for r in old.execute('PRAGMA table_info("'+table+'")')]
  select=",".join('"'+v+'"' for v in cols)
  past=list(old.execute('SELECT '+select+' FROM "'+table+'"'))
  after=set(db.execute('SELECT '+select+' FROM "'+table+'"'))
  if any(x not in after for x in past):
   raise ValueError("Historical/source/prototype parent row changed: "+table)
def compile_workflows(base,output,index_dir):
 base,output,index_dir=map(Path,(base,output,index_dir))
 if output.exists():raise ValueError("Immutable complete archive must not be replaced")
 if sha(base.read_bytes())!=PARENT_SHA:
  raise ValueError("Only latest verified V1.1 full SQLite parent is permitted")
 original=CONF.read_bytes()
 work=validate_config(original)
 output.parent.mkdir(parents=True,exist_ok=True)
 distinct=set()
 source_count=0
 step_count=0
 with sqlite3.connect("file:"+str(base.resolve())+"?mode=ro",uri=True) as old,sqlite3.connect(output) as db:
  old.backup(db)
  db.executescript(MIG.read_text("utf8"))
  db.execute("PRAGMA foreign_keys=ON")
  with db:
   if db.execute("SELECT COUNT(*) FROM cases").fetchone()[0]!=194:
    raise ValueError("Two-book 194 historical cases missing")
   if db.execute("SELECT COUNT(*) FROM phrase_template_drafts").fetchone()[0]!=4:
    raise ValueError("Four old GPT style drafts missing")
   if db.execute("SELECT COUNT(*) FROM phrase_version_progress WHERE domain_id='marriage'").fetchone()[0]!=1:
    raise ValueError("Mandatory V1.1 timing policy missing")
   if db.execute("SELECT COUNT(*) FROM phrase_context_instances").fetchone()[0]!=0:
    raise ValueError("No existing verified source chart phrase instances expected")
   for item in work["selected_intents"]:
    db.execute("""INSERT INTO phrase_intent_workflows
       (intent_id,domain_id,title,workflow_version,coverage_stage,evidence_strength,
        target_events_json,applied_context_json,human_delivery_policy)
       VALUES (?,'marriage',? ,?,'draft_source_grounded',?,?,?,?)""",
       (item["id"],item["title"],VERSION,item["source_support"],
        jsonv(item["events"]),jsonv({"source_scope":work["based_on"],
          "full_chart_audit":work["common_contract"]["full_chart_audit"],
          "required_preconditions":work["common_contract"]["preconditions"],
          "strict_stop_conditions":work["common_contract"]["strict_stop_conditions"],
          "scenario_requires_querent_partner_role_binding":True,
          "outcome_and_timing_must_be_computed_not_template_text":True,
          "source_support":item["source_support"]}),
        item["style"]))
    for st in item["steps"]:
     db.execute("""INSERT INTO phrase_intent_workflow_steps
       (intent_id,step_order,stage_id,operation_original,required_output)
       VALUES (?,?,?,?,?)""",
       (item["id"],st["order"],st["stage"],st["instruction"],st["required_output"]))
     step_count+=1
    for idx,r in enumerate(item["sources"],1):
     row=db.execute("""SELECT original_text FROM sections
       WHERE book_id=? AND section_key=? AND sha256=?""",
       (r["book_id"],r["source_section_key"],r["source_sha256"])).fetchone()
     if row is None:raise ValueError("Book source SHA mismatch: "+jsonv(r))
     if db.execute("SELECT COUNT(*) FROM cases WHERE case_id=?",(r["case_id"],)).fetchone()[0]!=1:
      raise ValueError("Case source case missing: "+r["case_id"])
     lines=row[0].splitlines()
     nums=r["lines"]
     if nums!=sorted(set(nums)) or any(not 1<=n<=len(lines) for n in nums):
      raise ValueError("Invalid or out-of-order original source lines: "+jsonv(r))
     excerpts=[{"line":n,"original":lines[n-1],
                "sha256":sha(lines[n-1].encode("utf8"))} for n in nums]
     is_feedback=int("feedback" in r["phase_role"] or r["phase_role"]=="later_distinct_wedding_date")
     db.execute("""INSERT INTO phrase_intent_evidence_links
       (intent_id,source_ordinal,book_id,source_section_key,
        source_sha256,case_id,original_source_line_numbers_json,
        original_book_snippets_json,original_phase_role,is_future_feedback)
       VALUES (?,?,?,?,?,?,?,?,?,?)""",
       (item["id"],idx,r["book_id"],r["source_section_key"],
        r["source_sha256"],r["case_id"],jsonv(nums),jsonv(excerpts),
        r["phase_role"],is_feedback))
     distinct.add(r["case_id"])
     source_count+=1
   if source_count!=28 or step_count!=72:
    raise ValueError("All 28 exact author source witness links and 72 steps required")
   details={"source_status":"book_original_method_drafts_not_independent_science",
    "applies_one_subquestion_specific_event_at_a_time":True,
    "nine_intents_with_not_all_direct_examples":True,
    "register_vs_wedding_times_separate":True,
    "four_earlier_style_prototypes_not_approved":True,
    "no_new_1080_verified_chart_or_388800_texts":True,
    "later_feedback_never_inputs_of_initial_forecast":True,
    "new_question_type_requires_explicit_registry_extension":True}
   db.execute("""INSERT INTO phrase_intent_workflow_audit
      (domain_id,workflow_version,source_archive_parent_sha256,
       definitions_sha256,intent_count,distinct_source_case_count,
       step_count,source_anchor_count,original_phrase_draft_count,
       qa_status,notes_json)
      VALUES ('marriage',?,?,?,?,?,?,?,4,'source_anchored_draft_not_chart_tested',?)""",
      (VERSION,PARENT_SHA,sha(original),9,len(distinct),step_count,source_count,
       jsonv(details)))
  check_parent_unmodified(old,db)
  if db.execute("PRAGMA integrity_check").fetchone()[0]!="ok" or db.execute("PRAGMA foreign_key_check").fetchall():
   raise ValueError("Full historical SQLite integrity/fk failure")
  db.execute("VACUUM");db.commit()
  counts={t:db.execute('SELECT COUNT(*) FROM "'+t+'"').fetchone()[0] for t in [
   "sections","cases","historical_chart_cells","phrase_template_drafts",
   "phrase_source_links","phrase_context_instances","phrase_outcome_timing_contracts",
   "phrase_intent_workflows","phrase_intent_workflow_steps",
   "phrase_intent_evidence_links","phrase_intent_workflow_audit"]}
 if counts!={"sections":43,"cases":194,"historical_chart_cells":1440,
  "phrase_template_drafts":4,"phrase_source_links":9,"phrase_context_instances":0,
  "phrase_outcome_timing_contracts":4,"phrase_intent_workflows":9,
  "phrase_intent_workflow_steps":72,"phrase_intent_evidence_links":28,
  "phrase_intent_workflow_audit":1}:
  raise ValueError(("New full source database has unexpected counts",counts))
 result={"schema":"wengua_marriage_question_specific_workflows_v1_2",
  "parent_complete_sqlite_sha256":PARENT_SHA,"full_new_sqlite_sha256":sha(output.read_bytes()),
  "workflow_source_json_sha256":sha(original),"workflow_version":VERSION,
  "domains_completed_for_method_design":1,"domain":"marriage",
  "subtype_workflows":9,"eight_stage_methods":72,
  "author_original_book_provenance_links":source_count,
  "distinct_referenced_book_case_families":len(distinct),
  "all_194_old_historical_cases_unchanged":True,
  "four_older_draft_phrases_unchanged":True,
  "source_approved_full_chart_reading_instances":0,
  "new_phrase_instances":0,
  "new_verified_nine_palace_state_instances":0,
  "no_unconditional_phrase_presets":True,
  "empirical_accuracy_not_claimed":True,
  "counts":counts}
 index_dir.mkdir(parents=True,exist_ok=True)
 (index_dir/"manifest.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n","utf8")
 return result
def main():
 p=argparse.ArgumentParser()
 for key in ("base","output","index-dir"):
  p.add_argument("--"+key,required=True)
 a=p.parse_args()
 print(jsonv(compile_workflows(a.base,a.output,a.index_dir)))
if __name__=="__main__":main()
