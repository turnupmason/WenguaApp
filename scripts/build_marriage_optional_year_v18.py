"""Create complete V1.8 WenguaApp immutable SQLite, with optional 年命.

Preserves the entire V1.7 SHA-pinned SQLite via sqlite3.backup and validates
EVERY original historical database row unmodified. User absence of year
must not block all-day/hour/marriage symbolic reading. Book method witnesses
stored separately from later case outcomes, with original SHA/line anchors.
"""
from __future__ import annotations
import argparse,hashlib,json,sqlite3
from pathlib import Path
from src.wengua.marriage_no_year_v18 import analyze_marriage_v18,_original_rules
from src.wengua.casting_shenqi import layout_from_explicit_bureau
from scripts.evaluate_marriage_other_families_v17 import CASES,_compare_printed_chart
ROOT=Path(__file__).resolve().parents[1]
PARENT_NAME="WenguaApp_双书194案例_婚姻多证据条件与新增家族验证V1_7_完整研究库.sqlite3"
OUTPUT_NAME="WenguaApp_双书194案例_婚姻无年命作者取用方法V1_8_完整研究库.sqlite3"
PARENT_SHA="e6bc297b10b0f911b1cc03392afe7e53bc51a34d8acffecd674a9f5e343af675"
MIG=ROOT/"schema/migrations/046_marriage_optional_nianming_v18.sql"
PROTOCOL="marriage.optional_year_author_methods.v1.8"
def sha(data):return hashlib.sha256(data).hexdigest()
def js(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":"))
def preserve(old,new):
 for (tab,) in old.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"):
  cols=[x[1] for x in old.execute('PRAGMA table_info("'+tab+'")')]
  selects=",".join('"'+x+'"' for x in cols)
  prev=list(old.execute('SELECT '+selects+' FROM "'+tab+'"'))
  now=set(new.execute('SELECT '+selects+' FROM "'+tab+'"'))
  if any(x not in now for x in prev):
   raise ValueError("Prior original source/old dev error row changed: "+tab)
def build(parent,output,indexdir):
 parent,output,indexdir=map(Path,(parent,output,indexdir))
 if output.exists():raise ValueError("Refuse to overwrite versioned full source database")
 if sha(parent.read_bytes())!=PARENT_SHA:
  raise ValueError("Exact latest V1.7 full archive SHA required")
 with sqlite3.connect("file:"+str(parent.resolve())+"?mode=ro",uri=True) as prior:
  refs=_original_rules(prior)
 if len(refs)!=10:raise ValueError("Ten unique source rule references required")
 computed=[]
 for case in CASES:
  chart=layout_from_explicit_bureau(
   dun=case["dun"],ju=case["ju"],hour_ganzhi=case["hour"])
  x=_compare_printed_chart(chart,case["family"])
  if not x["agrees_with_original_book"] or x["eight_printed_outer_palaces_checked"]!=8:
   raise ValueError("Printed source board disagrees with casting engine; do not score")
  payload={"chart":chart,"calendar_inputs":{
    "day_ganzhi":case["day"],"hour_ganzhi":case["hour"],
    "year_ganzhi":case["year"],"month_ganzhi":case["month"],
    "solar_term":case["solar_term"],
    "local_time_iso":case["date"],"iana_timezone":"Asia/Shanghai"},
   "inquiry":{"domain":"marriage","scene_id":case["scene"],
    "question_text":case["question"],"relationship":"self",
    "subject":({"year_ganzhi":case["year_subject"]} if case["year_subject"] else {}),
    "partner":{}}}
  result=analyze_marriage_v18(db_path=parent,payload=payload,
              held_out_family_id=case["family"])
  if result["status"]!="v18_source_author_initial_decision_no_year_optional":
   raise ValueError("Optional year route erroneously blocks original cast")
  if result["traditional_initial_outcome"]=="unresolved":
   raise ValueError("User asked to read without a year, must not require year")
  if result["author_future_feedback_used_in_initial_decision"]:
   raise ValueError("Historical feedback contaminated the initial reading")
  if not result["missing_year_no_year_value_invented"] or result["publication_ready"]:
   raise ValueError("No fabricated birth-year or premature published claims")
  if any(x["event_family_id"]==case["family"] for x in
        result["prior_method_witness_holdout"]["pre_event_method_witnesses"]):
   raise ValueError("Heldout entire historical family leaked")
  computed.append((case,payload,result))
 output.parent.mkdir(parents=True,exist_ok=True)
 with sqlite3.connect("file:"+str(parent.resolve())+"?mode=ro",uri=True) as old,sqlite3.connect(output) as db:
  old.backup(db)
  db.executescript(MIG.read_text("utf8"))
  db.execute("PRAGMA foreign_keys=ON")
  with db:
   if db.execute("SELECT COUNT(*) FROM cases").fetchone()[0]!=194:
    raise ValueError("Original 194 book events not preserved")
   if db.execute("""SELECT COUNT(*) FROM marriage_v16_post_inference_labels
     WHERE matches_initial_book_retrospective_result=0""").fetchone()[0]!=2:
    raise ValueError("Two original V1.6 misses must NOT be erased")
   if db.execute("SELECT COUNT(*) FROM marriage_v17_book_conditional_rules").fetchone()[0]!=27:
    raise ValueError("Prior book-sourced V1.7 combinator must be preserved")
   db.execute("""INSERT INTO marriage_v18_optional_nianming_protocol(
     protocol_id,scope,birth_year_is_optional,no_fabricated_year,
     fallback_yi_geng_liuhe_day_hour,actual_partner_identity_cannot_be_inferred,
     author_method_and_case_error_separated,original_book_source_anchor_count,
     parent_full_archive_sha256,rule_priority_json,no_approved_unseen_forecast_claim)
     VALUES (?,'ALL_22_MARRIAGE_SCENES',1,1,1,1,1,10,?,?,1)""",
     (PROTOCOL,PARENT_SHA,js({
      "no_year":"甲乙庚六合+日干时干事体 are conditional original author candidate methods",
      "one_year":"keep only known person's 年命 and never invent other",
      "both_years":"retain original V1.7 multiple persons + 27 symbol rules",
      "source_method":"shenqi marriage line 5/9/11/54/107; kaiwu 39/75/79/281/285",
      "specific_person_not_yi_geng_from_generic_symbols_without_roles":True,
      "no_question_conclusion_for_unverified_sex_or_health":True,
      "real_event_timing_requires_proven_source_trigger":True})))
   for key,ref in sorted(refs.items()):
    db.execute("""INSERT INTO marriage_v18_book_optional_role_sources
     (protocol_id,source_key,book_id,section_key,source_line,
      original_whole_book_sha256,original_line_sha256,source_original_excerpt)
     VALUES (?,?,?,?,?,?,?,?)""",
     (PROTOCOL,key,ref["book_id"],ref["section_key"],ref["line"],
      ref["whole_chapter_sha256"],ref["original_line_sha256"],ref["source_excerpt"]))
   rows=db.execute("SELECT scene_id FROM marriage22_scenario_protocol ORDER BY scene_number").fetchall()
   if len(rows)!=22:raise ValueError("22 existing source-scene cases not found")
   for (sid,) in rows:
    db.execute("""INSERT INTO marriage_v18_optional_year_scene_methods
     (scene_id,protocol_id,no_year_route_available,one_year_route_available,
      both_years_route_available,intended_question_needs_true_relation_binding,
      source_method_status)
     VALUES (?,?,1,1,1,1,'draft_source_grounded_not_sealed')""",
     (sid,PROTOCOL))
   for case,payload,result in computed:
    db.execute("""INSERT INTO marriage_v18_missing_year_dev_studies
     (study_id,protocol_id,source_event_family,question_scene_id,
      book_source_palaces_original_match,person_nianming_mode,missing_year_not_fabricated,
      source_decision,first_initial_evidence_json,original_book_source_provenance_json)
     VALUES (?,?,?,?,1,?,1,?,?,?)""",
     ("marriage.v18.optional."+case["family"],PROTOCOL,
      case["family"],case["scene"],result["year_role_binding"]["strategy"],
      result["traditional_initial_outcome"],
      js({"question":case["question"],
       "true_year_if_available":case["year_subject"],
       "source_first_judgment":result["evidence_decision"],
       "if_any_calculated_timing":result["primary_timing_if_justified"],
       "never_looked_at_book_case_future_feedback":True}),
      js({"original_method_lines":result["source_rule_refs"],
       "original_case_family_heldout":case["family"],
       "source_witnesses_excluding_this_family":result["prior_method_witness_holdout"]})))
   db.execute("""INSERT INTO marriage_v18_optional_year_archive_audit
     (version,parent_full_archive_sha256,original_book_case_count,
      existing_v16_wrong_dev_answers,previous_v17_original_rule_count,
      all_marriage_scenes_with_year_optional,original_line_sources,
      no_year_extra_dev_studies,all_earlier_source_rows_unchanged,audit_notes_json)
     VALUES('marriage.optional-year.v1.8',?,194,2,27,22,10,2,1,?)""",
     (PARENT_SHA,js({
       "real_world_unseen_prediction_result_verified":0,
       "source_case04_one_birth_year_case05_no_birth_year":True,
       "case04_05_no_later_independently_reported_future":True,
       "legacy_v16_two_dev_misses_preserved":True,
       "original_194_historical_case_families_not_duplicated":True,
       "source_method_no_year_does_not_assume_true_partner_gender":True,
       "missing_original_24_factors_still_require_future_source_review":True})))
  preserve(old,db)
  if db.execute("PRAGMA integrity_check").fetchone()[0]!="ok" or db.execute("PRAGMA foreign_key_check").fetchall():
   raise ValueError("Full archive source row/foreign key integrity check failed")
  db.execute("VACUUM")
  db.commit()
  names=["cases","sections","historical_chart_cells","marriage22_scenario_protocol",
         "marriage_v16_post_inference_labels","marriage_v17_book_conditional_rules",
         "marriage_v18_optional_nianming_protocol","marriage_v18_book_optional_role_sources",
         "marriage_v18_optional_year_scene_methods","marriage_v18_missing_year_dev_studies",
         "marriage_v18_optional_year_archive_audit"]
  counts={n:db.execute('SELECT COUNT(*) FROM "'+n+'"').fetchone()[0] for n in names}
  expected={"cases":194,"sections":43,"historical_chart_cells":1440,
            "marriage22_scenario_protocol":22,"marriage_v16_post_inference_labels":3,
            "marriage_v17_book_conditional_rules":27,
            "marriage_v18_optional_nianming_protocol":1,
            "marriage_v18_book_optional_role_sources":10,
            "marriage_v18_optional_year_scene_methods":22,
            "marriage_v18_missing_year_dev_studies":2,
            "marriage_v18_optional_year_archive_audit":1}
  if counts!=expected:raise ValueError(("Archive error",counts,expected))
 r={"schema":"wengua_marriage_optional_nianming_v18",
   "parent_full_sqlite_sha256":PARENT_SHA,
   "new_full_sqlite_sha256":sha(output.read_bytes()),
   "all_book_events_preserved":194,"previous_27_author_rules_preserved":27,
   "previous_v16_wrong_dev_predictions_preserved":2,
   "all_22_marriage_scenes_accept_absent_year":True,
   "exact_original_method_line_hashes":10,
   "other_two_historical_families_no_year_comparison":2,
   "new_independently_verified_real_world_predictions":0,
   "original_all_prior_database_rows_unchanged":True,
   "source_methods_development_not_certified_complete":True,
   "first_results":[{"family":c["family"],"year_mode":r0["year_role_binding"]["strategy"],
      "initial_traditional_symbolic_result":r0["traditional_initial_outcome"],
      "person_identification_guessed":False}
      for c,_,r0 in computed],"counts":counts}
 indexdir.mkdir(parents=True,exist_ok=True)
 (indexdir/"manifest.json").write_text(json.dumps(r,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 return r
def main():
 p=argparse.ArgumentParser()
 for x in ("base","output","index-dir"):p.add_argument("--"+x,required=True)
 a=p.parse_args()
 print(js(build(a.base,a.output,a.index_dir)))
if __name__=="__main__":main()
