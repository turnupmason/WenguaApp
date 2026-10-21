"""V1.3: extend full 194-case marriage V1.2 SQLite with 22 detailed scenarios.

Existing 9 core marriage intents, 194 book cases, 4 linguistic prototypes,
and original historical errors remain byte-for-row identical. 22 user scenarios
are NOT 22 original independently author-verified book methods: they inherit
verified exact source lines from the 9 intents and explicit evidence gaps.
"""
from __future__ import annotations
import argparse,hashlib,json,sqlite3
from pathlib import Path
from src.wengua.six_layer_contract import LAYERS
ROOT=Path(__file__).resolve().parents[1]
OLD="WenguaApp_双书194案例_婚姻各类问事流程V1_2_完整研究库.sqlite3"
NEW="WenguaApp_双书194案例_婚姻22场景六层流程V1_3_完整研究库.sqlite3"
PARENT_SHA="2119735b5772feb0177c03b032be8070fef629060b509d30a26b5ce204c9aa2d"
CONF=ROOT/"data/knowledge/phrase_library/marriage_v1_3/twenty_two_scene_methods.json"
MIG=ROOT/"schema/migrations/041_global_six_layers_marriage22_scenarios.sql"
VERSION="marriage.scene.v1.3"
def sha(data):return hashlib.sha256(data).hexdigest()
def js(obj):return json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(",",":"))
def verify_config(raw):
 d=json.loads(raw)
 if d.get("schema")!="wengua_marriage_22_scene_two_phase_six_layer_author_protocol_v1" or len(d.get("scenes",[]))!=22:
  raise ValueError("All user 22 marriage scenarios must be mapped")
 if d["parent_full_SQLite_sha256"]!=PARENT_SHA:
  raise ValueError("Must cite exact latest 9-flow full SQLite SHA")
 if [x["display_number"] for x in d["scenes"]]!=list(range(1,23)):
  raise ValueError("22 scenes must retain user-specified order")
 if tuple(s["id"] for s in d["stages"])!=LAYERS:
  raise ValueError("Each of the exact six mandatory all-domain stages is required")
 if any(not x.get("stage_4",{}).get("negative_case_coverage")
        or not x.get("stage_5",{}).get("unsupported_absolute_claim_to_exclude")
        or x.get("required_review_status")!="draft_source_grounded"
        for x in d["scenes"]):
  raise ValueError("Per-scene book errors and prohibited unjustified absolutes required")
 return d
def row_preservation(old,db):
 for (name,) in old.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"):
  cols=[r[1] for r in old.execute('PRAGMA table_info("'+name+'")')]
  select=",".join('"'+x+'"' for x in cols)
  old_rows=list(old.execute('SELECT '+select+' FROM "'+name+'"'))
  new_rows=set(db.execute('SELECT '+select+' FROM "'+name+'"'))
  if any(row not in new_rows for row in old_rows):
   raise ValueError("Original parent historical row replaced: "+name)
def build(base,out,indexdir):
 base,out,indexdir=map(Path,(base,out,indexdir))
 if out.exists():raise ValueError("Never overwrite archive versions")
 if sha(base.read_bytes())!=PARENT_SHA:
  raise ValueError("Source full original marriage V1.2 archive SHA mismatch")
 raw=CONF.read_bytes()
 d=verify_config(raw)
 out.parent.mkdir(parents=True,exist_ok=True)
 booklinks=0
 case_ids=set()
 with sqlite3.connect("file:"+str(base.resolve())+"?mode=ro",uri=True) as old,sqlite3.connect(out) as db:
  old.backup(db)
  db.executescript(MIG.read_text("utf8"))
  db.execute("PRAGMA foreign_keys=ON")
  with db:
   if db.execute("SELECT COUNT(*) FROM cases").fetchone()[0]!=194:
    raise ValueError("Original source cases 194 missing")
   if db.execute("SELECT COUNT(*) FROM phrase_intent_workflows").fetchone()[0]!=9:
    raise ValueError("Nine existing workflows missing")
   if db.execute("SELECT COUNT(*) FROM phrase_template_drafts").fetchone()[0]!=4:
    raise ValueError("Four original human language drafts must remain intact")
   db.execute("""INSERT INTO domain_six_layer_contract
   (contract_version,scope,enforce_all_six,physical_factor_count,
    author_provenance_mandatory,no_feedback_leakage,
    outcome_required_if_supported,computed_timing_when_supported,
    gpt_cannot_invent_evidence,field_missing_means_blocked,
    applied_to_all_new_domains,archive_parent_sha256,notes_json)
   VALUES (?,'ALL_DOMAINS',1,24,1,1,1,1,1,1,1,?,?)""",
   (VERSION,PARENT_SHA,js({"all_new_domains_must_implement_100percent_stage_checks":True,
    "does_not_guarantee_100percent_future_accuracy":True,
    "source_charts_and_calendar_must_be_actually_verified":True,
    "l6_only_polishes_l5_structured_conclusion":True,
    "malicious_absolute_medical_crime_abuse_infidelity_legal_claims_blocked":True})))
   for s in d["scenes"]:
    pid=s["parent_intent_id"]
    if not db.execute("SELECT 1 FROM phrase_intent_workflows WHERE intent_id=?",(pid,)).fetchone():
     raise ValueError("Orphan scenario, must inherit exact 9-flow author-method lineage")
    db.execute("""INSERT INTO marriage22_scenario_protocol
     (scene_id,domain_id,scene_number,title,parent_intent_id,target_event,
      evidence_grade,role_and_yongshen_candidates,dynamic_factor_focus,
      explicit_unsupported_claims,timing_target,protocol_json)
     VALUES (?,'marriage',?,?,?,?,?,?,?,?,?,?)""",
     (s["scene_id"],s["display_number"],s["title"],pid,
      s["target_event_definition"],s["stage_4"]["evidence_grade"],
      s["stage_3"]["primary_and_secondary_yongshen_binding"],
      s["stage_2"]["additional_dynamic_cross_checks"],
      s["stage_5"]["unsupported_absolute_claim_to_exclude"],
      s["stage_5"]["timing_target"],js(s)))
    for i,layer in enumerate(d["stages"],1):
     if layer["number"]!=i or layer["id"]!=LAYERS[i-1]:
      raise ValueError("Universal stage order corrupted")
     action=s["stage_"+str(i)]
     db.execute("""INSERT INTO marriage22_six_layer_steps
      (scene_id,layer_number,layer_id,full_requirement_json,subtype_action_json)
      VALUES (?,?,?,?,?)""",
      (s["scene_id"],i,layer["id"],js(layer["required"]),js(action)))
    citations=db.execute("""SELECT book_id,source_section_key,source_sha256,
       case_id,original_source_line_numbers_json,original_book_snippets_json,original_phase_role,
       is_future_feedback
       FROM phrase_intent_evidence_links
       WHERE intent_id=? ORDER BY source_ordinal""",(pid,)).fetchall()
    if not citations:raise ValueError("No actual canonical book evidence for "+pid)
    for i,(bk,sec,sourcehash,case,source_lines,snippets,phase,feedback) in enumerate(citations,1):
     matching=db.execute("SELECT original_text FROM sections WHERE book_id=? AND section_key=? AND sha256=?",
                         (bk,sec,sourcehash)).fetchone()
     if matching is None:raise ValueError("Missing cited book source hash")
     source_rows=matching[0].splitlines()
     for item in json.loads(snippets):
      line=item["line"]
      if (line<1 or line>len(source_rows) or source_rows[line-1]!=item["original"]
          or sha(item["original"].encode())!=item["sha256"]):
       raise ValueError("Book citation source line hashes no longer match")
     db.execute("""INSERT INTO marriage22_original_case_links
     (scene_id,source_ordinal,inherited_parent_intent_id,book_id,section_key,
      original_source_sha256,original_case_id,source_lines_json,
      source_snippets_json,source_phase,feedback_not_initial_reasoning,
      applicable_to_subscene)
     VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
     (s["scene_id"],i,pid,bk,sec,sourcehash,case,source_lines,
      snippets,phase,feedback,"relevant_parent_method_not_independently_tested_22_scene"))
     case_ids.add(case)
     booklinks+=1
   if booklinks<22:raise ValueError("Each of 22 scenes must be grounded by at least one historical source")
   db.execute("""INSERT INTO marriage22_scene_catalog_audit
    (audit_version,full_parent_sha256,catalog_sha256,scene_count,mandatory_layer_rows,
     inherited_source_references,previous_book_case_count,earlier_nine_workflows_preserved,
     notes_json)
     VALUES (?,?,?,22,132,?,194,9,?)""",
     (VERSION,PARENT_SHA,sha(raw),booklinks,
      js({"scene_citations_inherited_from_9_workflows":True,
       "distinct_cited_historical_case_ids":len(case_ids),
       "no_user_hardcoded_absolute_claims_promoted":True,
       "no_published_answers_without_engine_and_calendar_verified":True,
       "truthfulness_requires_no_hidden_private_life_disease_or_crime_proofs":True})))
  row_preservation(old,db)
  if db.execute("PRAGMA integrity_check").fetchone()[0]!="ok" or db.execute("PRAGMA foreign_key_check").fetchall():
   raise ValueError("Six layer versioned source SQLite failed integrity")
  db.execute("VACUUM");db.commit()
  tables=["sections","cases","historical_chart_cells","phrase_template_drafts",
          "phrase_context_instances","phrase_intent_workflows","phrase_intent_workflow_steps",
          "phrase_intent_evidence_links","phrase_outcome_timing_contracts",
          "domain_six_layer_contract","marriage22_scenario_protocol",
          "marriage22_six_layer_steps","marriage22_original_case_links",
          "six_layer_instance_trace","marriage22_scene_catalog_audit"]
  counts={t:db.execute('SELECT COUNT(*) FROM "'+t+'"').fetchone()[0] for t in tables}
  if counts["sections"]!=43 or counts["cases"]!=194 or counts["historical_chart_cells"]!=1440:
   raise ValueError("Original historical book case archive is damaged")
  if counts["phrase_intent_workflows"]!=9 or counts["phrase_template_drafts"]!=4 or counts["phrase_context_instances"]!=0:
   raise ValueError("Earlier 9 flows and 4 drafts must remain intact")
  if counts["marriage22_scenario_protocol"]!=22 or counts["marriage22_six_layer_steps"]!=132:
   raise ValueError("22 x 6 mandatory stage definitions not fully inserted")
  if counts["marriage22_original_case_links"]!=booklinks:
   raise ValueError("Source reference lineage lost")
 indexdir.mkdir(parents=True,exist_ok=True)
 result={"schema":"wengua_marriage_22_scenes_global_six_layers_v1_3",
  "parent_full_SQLite_SHA256":PARENT_SHA,
  "new_full_SQLite_SHA256":sha(out.read_bytes()),
  "book_sources_unchanged":43,"book_case_families_unchanged":194,
  "nine_prior_marriage_subtype_flows_preserved":9,
  "initial_four_phrase_drafts_unchanged":4,
  "marriage_scenes":22,"six_layer_mandatory_stage_rows":132,
  "author_source_line_links_inherited":booklinks,
  "distinct_historical_books_cases_cited":len(case_ids),
  "verified_new_casts_or_instances":0,
  "all_source_and_phrase_prior_rows_unchanged":True,
  "predicted_future_success_rate_100_percent":False,
  "contract_is_all_domain_mandatory":True,
  "book_original_phase_distinct_from_later_feedback":True,
  "output_conditions_remain_draft_pending_engine":True,
  "counts":counts}
 (indexdir/"manifest.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n","utf8")
 return result
def main():
 p=argparse.ArgumentParser()
 for key in ("base","output","index-dir"):p.add_argument("--"+key,required=True)
 args=p.parse_args()
 print(js(build(args.base,args.output,args.index_dir)))
if __name__=="__main__":main()
