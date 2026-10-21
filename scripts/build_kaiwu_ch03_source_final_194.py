"""Append final 571-line Kaiwu source to SHA-locked 181-case full SQLite.

A source episode, a person question, a chart, a retrospective explanation and
a book-outcome label are different units. One Kedi permit episode was already
archived; never count it twice. All OCR grid fragments remain uncertified.
"""
import argparse,hashlib,json,re,sqlite3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CFG=ROOT/"data/knowledge/kaiwu/final_ch03_source_anchors.json"
SOURCE=ROOT/"sources/kaiwu/kaiwu_ch03_questions_and_case_reviews.txt"
MIG=ROOT/"schema/migrations/037_kaiwu_final_method_and_error_provenance.sql"
PARENT="WenguaApp_神奇之门21章_开悟之门21节_181案例_完整研究库.sqlite3"
OUTPUT="WenguaApp_神奇之门21章_开悟之门22节_194案例_完整研究库.sqlite3"
SECTION="questions_answers_errors_and_methods_ch03"
CHAPTER="kaiwu/"+SECTION+"/v1"
TITLE="第三章 答疑解惑与错例剖析"
def digest(b):return hashlib.sha256(b).hexdigest()
def j(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(",",":"))
def source(L,start,end=None):
 end=start if end is None else end
 if not 1<=start<=end<=len(L):raise ValueError(("Source anchor outside original chapter",start,end))
 return "\n".join(L[start-1:end])
def cid(tag):return "kaiwu.final."+tag
def verify(raw,cfg):
 if digest(raw)!=cfg["source_sha256"] or len(raw)!=62625 or not raw.endswith(b"\n"):
  raise ValueError("Original final chapter exact bytes or SHA must match uploaded original")
 L=raw.decode("utf8").splitlines()
 if len(L)!=571 or L[0:2]!=["第三章","答疑解惑与错例剖析"]:
  raise ValueError("Final source must preserve all 571 supplied source lines")
 heads=[i for i,v in enumerate(L,1) if re.match(r"^\([一二三四五六七八九十]+\)",v)]
 if heads!=cfg["headings"]:raise ValueError(("14 final chapter subsections missing",heads))
 grids=[i for i,v in enumerate(L,1) if v.startswith("【九宫盘OCR原始转写")]
 if grids!=[c[1] for c in cfg["casts"]]:raise ValueError(("16 original OCR cast fragments missing",grids))
 for n,word in [(107,"测错了"),(146,"并未补选"),(202,"三次断错"),
  (251,"阴遁6局"),(284,"辛酉时"),(342,"尸体"),
  (385,"放之四海而皆准"),(451,"3:0"),(527,"三个人")]:
  if word not in L[n-1]:raise ValueError(("critical source error warning missing",n,word))
 if not L[-1].endswith("还得恢复一段时间"):
  raise ValueError("Do not manufacture the absent end of the final medical feedback")
 return L
def unchanged(old,db):
 for (name,) in old.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"):
  cols=[r[1] for r in old.execute('PRAGMA table_info("'+name+'")')]
  select=",".join('"'+s+'"' for s in cols)
  original=list(old.execute('SELECT '+select+' FROM "'+name+'"'))
  now=set(db.execute('SELECT '+select+' FROM "'+name+'"'))
  if any(item not in now for item in original):raise ValueError("Old original rows mutated: "+name)
def phase(db,L,who,key,kind,a,b,visible=0):
 original=source(L,a,b)
 meta={"original_case":who,"source_only":True,
  "future_feedback_hidden_initially":not bool(visible),
  "known_independently_from_real_world":False,
  "retrospective_if_posthoc":kind.startswith("posthoc")}
 db.execute("""INSERT INTO kaiwu_final_source_phases VALUES(?,?,?,?,?,?,?,?,?,?)""",
  (CHAPTER,who,key,kind,a,b,original,digest(original.encode()),visible,j(meta)))
def concept(db,section_id,key,line,text,meta):
 db.execute("""INSERT INTO semantic_assertions
  (chapter_key,concept_id,kind,relation,source_start_line,source_end_line,
   metadata_json,original_excerpt,review_status)
  VALUES (?,?, 'book_method_or_case','contextual_conditional_evidence',?,?,?,?,'draft')""",
  (CHAPTER,key,line,line,j(meta),text))
 db.execute("""INSERT INTO cross_book_concept_tracks
  (chapter_key,concept_id,source_start_line,source_end_line,source_section_id,
   source_sha256,excerpt_sha256,track_id,relation_to_prior,comparison_state,normalized_json,review_status)
  VALUES (?,?,?,?,?,?,?,?,?,'book_source_not_independent_validation',?,'draft')""",
  (CHAPTER,key,line,line,section_id,CURRENT_SHA,digest(text.encode()),
   "kaiwu:questions_errors_source_only","additional_exposition",j(meta)))
def step(db,L,section_id,who,line,period):
 val=source(L,line)
 meta={"source_role":period,"line":line,"one_book_family":who,
  "post_result_not_first_prediction":period!="first_case_reasoning",
  "methodological_and_chart_errors_retained":True,
  "historical_claims_not_independently_verified":True,
  "positive_training_eligible":False}
 idx=1+db.execute("SELECT count(*) FROM kaiwu_final_reasoning_units WHERE case_id=? AND chapter_key=?",
                  (who,CHAPTER)).fetchone()[0]
 db.execute("""INSERT INTO kaiwu_final_reasoning_units
  (chapter_key,case_id,unit_index,source_line,reasoner,reasoning_phase,
   original_text,source_sha256,evidence_json)
  VALUES (?,?,?,?,?,?,?,?,?)""",
  (CHAPTER,who,idx,line,"book_original" if period=="first_case_reasoning" else "book_later_review",
   period,val,digest(val.encode()),j(meta)))
 concept(db,section_id,"kaiwu:final:"+who+":step"+str(idx).zfill(2),line,val,meta)
 if period=="first_case_reasoning":
  st=1+db.execute("SELECT count(*) FROM historical_case_reasoning WHERE case_id=?",(who,)).fetchone()[0]
  db.execute("""INSERT INTO historical_case_reasoning
   (case_id,step_number,source_line,author_analysis_original,short_method_topic,metadata_json)
   VALUES(?,?,?,?,?,?)""",(who,st,line,val,"source_reasoning_needs_evidence_context",j(meta)))
  db.execute("""INSERT INTO historical_case_reasoning_trace
  (case_id,step_number,source_line,evidence_json,review_status,positive_training_eligible)
  VALUES(?,?,?,?,'draft_book_correction_sensitive',0)""",(who,st,line,j(meta)))
def error(db,L,who,name,axis,a,b):
 db.execute("""INSERT INTO kaiwu_final_error_audit(chapter_key,case_id,error_key,error_axis,
  prediction_line,correction_line,original_prediction,original_later_correction)
  VALUES(?,?,?,?,?,?,?,?)""",
  (CHAPTER,who,name,axis,a,b,source(L,a),source(L,b)))
def build(base,src,out,index_dir):
 base,src,out,index_dir=map(Path,(base,src,out,index_dir))
 cfg=json.loads(CFG.read_text("utf8"))
 if out.exists():raise ValueError("Never overwrite versioned full SQLite snapshots")
 if digest(base.read_bytes())!=cfg["parent_sha256"]:raise ValueError("Wrong immutable full-181 source parent")
 raw=src.read_bytes();L=verify(raw,cfg)
 out.parent.mkdir(parents=True,exist_ok=True)
 global CURRENT_SHA
 CURRENT_SHA=cfg["source_sha256"]
 oldk=cfg["old_kedi_case"]
 with sqlite3.connect("file:"+str(base.resolve())+"?mode=ro",uri=True) as old,sqlite3.connect(out) as db:
  old.backup(db);db.executescript(MIG.read_text("utf8"));db.execute("PRAGMA foreign_keys=ON")
  with db:
   if db.execute("SELECT count(*) FROM sections WHERE book_id='kaiwu'").fetchone()[0]!=21:
    raise ValueError("Missing previous twenty-one Kaiwu section source snapshots")
   if not db.execute("SELECT 1 FROM cases WHERE case_id=?",(oldk,)).fetchone():
    raise ValueError("Existing Kedi permit work case must be reused")
   db.execute("""INSERT INTO sections(book_id,section_key,title,original_text,sha256,content_version,reviewed)
    VALUES('kaiwu',?,?,?,?,1,1)""",(SECTION,TITLE,raw.decode("utf8"),CURRENT_SHA))
   sid=db.execute("SELECT last_insert_rowid()").fetchone()[0]
   db.execute("""INSERT INTO chapter_knowledge(chapter_key,book_id,title,source_sha256,
    source_length_bytes,knowledge_version,review_status)
    VALUES (?,'kaiwu',?,?,?,'1','draft')""",(CHAPTER,TITLE,CURRENT_SHA,len(raw)))
   heads=cfg["headings"]
   for idx,a in enumerate(heads):
    b=(heads[idx+1]-1) if idx+1<len(heads) else len(L)
    db.execute("INSERT INTO kaiwu_final_subsections VALUES(?,?,?,?,?,?)",
     (CHAPTER,idx+1,a,b,source(L,a),digest(source(L,a,b).encode())))
   for idx,(q,begin,end) in enumerate(cfg["question_answers"],1):
    qa=source(L,q);ans=source(L,begin,end)
    meta={"questioner_role_required":True,"no_absolute_auspiciousness":True,
     "unknown_context_not_assumed":True,"author_provisional_where_stated":True,
     "question_same_if_multiple_case_stories":False,"review_status":"draft"}
    db.execute("""INSERT INTO kaiwu_final_qa(chapter_key,qa_key,subsection_number,question_line,
     answer_start,answer_end,question_original,answer_original,question_sha256,
     answer_sha256,conditions_json)
     VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
    (CHAPTER,"qa"+str(idx).zfill(2),next((i+1 for i,h in enumerate(heads) if h<=q and (i==13 or heads[i+1]>q))),
     q,begin,end,qa,ans,digest(qa.encode()),digest(ans.encode()),j(meta)))
   for case in cfg["cases"]:
    tag,sec,domain,a,b,ka,kb,claims,feedback,first_steps,later,wrong=case
    who=cid(tag);known=source(L,ka,kb)
    initial="\n".join(source(L,i) for i in claims)
    outcome="\n".join(source(L,i) for i in feedback)
    note={"source_subsection":sec,"original_span":[a,b],
     "case_id_unique_across_two_books":True,"answer_order_protected":True,
     "first_error_explicit":bool(wrong),"shared_cast_distinct_person":sec in (11,14),
     "source_errors_and_unresolved_author_quotes_preserved":True,
     "not_independent_public_health_crime_weather_judicial_approval":True}
    db.execute("""INSERT INTO cases(case_id,section_id,event_family_id,domain_id,known_before,
     author_yongshen_steps,author_judgment,later_feedback,reviewed)
     VALUES (?,?,?,?,?,?,?,?,1)""",
     (who,sid,who,domain,known,
      "\n".join(source(L,i) for i in first_steps),initial,outcome))
    db.execute("""INSERT INTO historical_case_protocol
    (case_id,completeness,published_chart_verification,feedback_independently_verified,
     eligible_blind_test,case_source_sha256,metadata_json)
    VALUES (?,'complete_user_supplied_chapter_case_not_complete_printed_book',
     'flat_OCR_print_positions_not_certified',0,0,?,?)""",
     (who,CURRENT_SHA,j(note)))
    db.execute("""INSERT INTO historic_book_case_acceptance
    (case_id,source_book,source_chapter_key,source_documented_outcome,metadata_json)
    VALUES (?,'kaiwu',?,'source_book_only_not_independent_research_accuracy',?)""",
     (who,CHAPTER,j(note)))
    facets=[domain]
    if sec in (9,13):facets.append("competition_evaluation")
    if sec==14:facets.append("same_printed_cast_distinct_event")
    if sec==5:facets.append("administrative_approval")
    if sec==10:facets.append("missing_person")
    if sec==8:facets.append("official_document")
    for rank,d in enumerate(dict.fromkeys(facets)):
     db.execute("""INSERT INTO unified_case_domain_facets
     (case_id,domain_id,source_chapter_key,primary_domain,note) VALUES(?,?,?,?,?)""",
     (who,d,CHAPTER,int(rank==0),"Full source scope kept; not independent external truth."))
    db.execute("""INSERT INTO historical_case_review_audit
     (case_id,original_steps,mechanical_step_trace,human_complete_step_chains,review_status,warning)
     VALUES (?,?,?,0,'book_source_draft_accuracy_not_independently_verified',?)""",
     (who,len(first_steps),len(first_steps),"Original corrections and question-time information kept separate"))
    db.execute("""INSERT INTO historical_case_book_verdicts
    (event_family_id,primary_case_id,verdict,explicit_source_correction,
     source_correction_lines_json,feedback_source_lines_json,
     independent_external_verification,app_output_protocol,evidence_review_status,note)
    VALUES (?,?,?,?,?,?,'not_verified','single_answer_for_one_cast','book_source_draft',?)""",
    (who,who,"author_book_error_explicit" if wrong else "author_book_success_default",
     int(bool(wrong)),j(later[:2]) if wrong else "[]",j(feedback),
     "Original reported outcome and later reasoning are not independently verified"))
    passage=source(L,a,b)
    db.execute("""INSERT INTO kaiwu_final_event_witnesses
     VALUES (?,?,?,?,?,?,?,?,?,?)""",
     (CHAPTER,"source_"+tag,who,sec,a,b,"new_unique_event_once",
      passage,digest(passage.encode()),j(note)))
    phase(db,L,who,"question","known_input_at_question_time",ka,kb,1)
    for p,i in enumerate(claims,1):phase(db,L,who,"original_claim_"+str(p),"original_first_answer",i,i)
    for p,i in enumerate(feedback,1):phase(db,L,who,"reported_outcome_"+str(p),"reported_after_first_answer",i,i)
    for i in first_steps:step(db,L,sid,who,i,"first_case_reasoning")
    for i in later:step(db,L,sid,who,i,"posthoc_or_teacher_reasoning")
    if wrong:error(db,L,who,"main_explicit_miss","initial_pred_wrong_keep_original",claims[0],feedback[0])
   # Kedi 1999 Jun20/21/22 single old family with three wrong timing attempts.
   original=source(L,156,209)
   db.execute("""INSERT INTO kaiwu_final_event_witnesses VALUES(?,?,?,?,?,?,?,?,?,?)""",
    (CHAPTER,"same_prior_kedi_work_permit",oldk,7,156,209,"same_prior_question_no_new_family",
     original,digest(original.encode()),j({"matches_prior_kaiwu_business_case05":True,
      "same_1999_June_permit_time_result":True,"no_new_independent_event":True})))
   for name,kind,a,b in [
    ("kedi_original","first_prior_failed_forecast_reprinted",158,158),
    ("kedi_followup_21","new_information_at_second_cast",159,161),
    ("kedi_wrong22","second_wrong_june22_claim",183,183),
    ("kedi_followup_22","new_information_at_third_cast",184,186),
    ("kedi_wrong23","third_wrong_june23_claim",201,201),
    ("kedi_actual29","later_permit_report_only_partial_land",202,202),
    ("kedi_teacher","later_correction_of_source_selection",203,209)]:
    phase(db,L,oldk,name,kind,a,b)
   for i in (204,205,206,207,208,209):
    step(db,L,sid,oldk,i,"posthoc_or_teacher_reasoning")
   error(db,L,oldk,"second_wrong_target_day","additional_wrong_timing_existing_event",183,202)
   error(db,L,oldk,"third_wrong_target_day","additional_wrong_timing_existing_event",201,202)
   error(db,L,oldk,"changed_kai_to_jing","after_event_new_primary_document_symbol",183,206)
   for tag,a,b,links in cfg["casts"]:
    original=source(L,a,b)
    db.execute("""INSERT INTO kaiwu_final_raw_casts
     (chapter_key,cast_key,source_start,source_end,source_original,source_sha256)
     VALUES (?,?,?,?,?,?)""",(CHAPTER,tag,a,b,original,digest(original.encode())))
    for n in range(a,b+1):
     s=source(L,n)
     db.execute("""INSERT INTO kaiwu_final_raw_cast_lines VALUES(?,?,?,?,?)""",
      (CHAPTER,tag,n,s,digest(s.encode())))
    for identity in links:
     who=oldk if identity=="OLD_KEDI" else cid(identity)
     typ="teacher_after_result_not_source_original" if tag.endswith("edited") or tag.endswith("posthoc") else (
      "different_questioner_same_source_cast" if tag in ("marriage_shared","three_people") else "original_OCR_source_not_certified")
     db.execute("""INSERT INTO kaiwu_final_cast_case_links VALUES(?,?,?,?)""",
      (CHAPTER,tag,who,typ))
     phase(db,L,who,"printed_OCR_"+tag,"original_source_ocr_grid_spatially_unverified",a,b)
   for who,key,axis,a,b in [
    (cid("opera"),"wrong_hour_actual_right","wrong_cast_not_same_as_wrong_event",258,284),
    (cid("opera"),"contradictory_dun","source_teacher_says_yin2_but_written_yang2",284,285),
    (cid("license"),"wrong_calendar_dun","actual_cast_student_yang6_teacher_says_yin6",215,251),
    (cid("missing_daughter"),"after_death_reanalysis","posthoc_criminal_attribution_unverified",341,346),
    (cid("weather"),"prior_observed_rain","weather_source_retro_not_blind_forecast",418,443),
    (cid("football"),"two_wrong_predictions_one_match","planned_game_and_actual_start_both_wrong",474,502),
    (cid("exam"),"no_matriculation_record","score_cutoff_not_confirmed_full_admission",568,569)]:
    error(db,L,who,key,axis,a,b)
   for idx,ln in enumerate(cfg["method_lines"],1):
    original=source(L,ln)
    preconditions={"requires":["specific_domain","questioner_relationship","time_and_place",
      "relevant_primary_and_secondary_symbols","full_board_evidence","contrary_evidence_check"],
     "unknown":"do_not_write_definite_judgment",
     "avoid_repetitive_unconditional_388800_sentence_generation":True}
    limits={"book_source_only":True,"author_uncertain_or_corrected_elsewhere":True,
     "cannot_replace_modern_health_weather_legal_evidence":True,
     "first_wrong_forecasts_preserved":True,"positive_training_eligible":False}
    key="source_method_"+str(idx).zfill(2)
    db.execute("""INSERT INTO kaiwu_final_method_candidates
    (chapter_key,method_key,source_line,source_original,method_domain,preconditions_json,limitations_json)
    VALUES (?,?,?,?,?,?,?)""",(CHAPTER,key,ln,original,"traditional_cross_domain_conditional",
      j(preconditions),j(limits)))
    concept(db,sid,"kaiwu:final:source_method:"+str(idx).zfill(2),ln,original,
     {"prerequisites":preconditions,"limitations":limits})
   db.execute("""INSERT INTO chapter_archival_versions
    (archive_label,baseline_sha256,new_db_sha256,contains_complete_private_copyright_source,
     snapshot_type,created_utc,repo_public_archive_policy)
    VALUES (?, ?,NULL,1,'final_kaiwu_ch03_all_source_14_sections_15QA_13_unique_questions',
    '2026-10-21','user_authorized_public_full_sqlite_versions')""",
    ("shenqi21_kaiwu22_194cases_full_end_of_supplied_source",cfg["parent_sha256"]))
  unchanged(old,db)
  expected={"sections":43,"cases":194,"historic_book_case_acceptance":86,
   "historical_chart_cells":1440,"historical_case_additional_casts":19,
   "historical_case_additional_cast_cells":171,"historical_palace_standardization":1611,
   "kaiwu_final_subsections":14,"kaiwu_final_qa":15,
   "kaiwu_final_event_witnesses":14,"kaiwu_final_raw_casts":16,
   "kaiwu_final_raw_cast_lines":sum(x[2]-x[1]+1 for x in cfg["casts"]),
   "kaiwu_final_cast_case_links":sum(len(x[3]) for x in cfg["casts"]),
   "kaiwu_final_method_candidates":len(cfg["method_lines"])}
  actual={t:db.execute('SELECT COUNT(*) FROM "'+t+'"').fetchone()[0] for t in expected}
  if actual!=expected:raise ValueError(("Unexpected full archive source count",actual,expected))
  errors=db.execute("SELECT COUNT(*) FROM historical_case_book_verdicts WHERE verdict='author_book_error_explicit'").fetchone()[0]
  if errors!=19:raise ValueError(("Must retain original 11 and eight newly explicit errors",errors))
  if db.execute("PRAGMA integrity_check").fetchone()[0]!="ok" or db.execute("PRAGMA foreign_key_check").fetchall():
   raise ValueError("SQLite integrity or FK errors")
  db.execute("VACUUM");db.commit()
  counts={t:db.execute('SELECT COUNT(*) FROM "'+t+'"').fetchone()[0] for t in
   ["sections","cases","historical_chart_cells","historical_case_reasoning",
    "historical_case_reasoning_trace","semantic_assertions","cross_book_concept_tracks",
    "historic_book_case_acceptance","unified_case_domain_facets",
    "kaiwu_final_subsections","kaiwu_final_qa","kaiwu_final_event_witnesses",
    "kaiwu_final_raw_casts","kaiwu_final_raw_cast_lines","kaiwu_final_cast_case_links",
    "kaiwu_final_source_phases","kaiwu_final_reasoning_units",
    "kaiwu_final_error_audit","kaiwu_final_method_candidates"]}
 index_dir.mkdir(parents=True,exist_ok=True)
 meta={"schema":"kaiwu_final_two_books_source_194cases_v1",
  "source_title":TITLE,"source_path":str(src.relative_to(ROOT)) if src.is_relative_to(ROOT) else str(src),
  "source_sha256":CURRENT_SHA,"source_bytes":len(raw),"source_lines":len(L),
  "source_subsections":14,"method_question_answers":15,"new_independent_events":13,
  "same_1999_Kedi_permit_event":oldk,"all_new_OCR_fragments":len(cfg["casts"]),
  "source_OCR_rows":expected["kaiwu_final_raw_cast_lines"],
  "new_certain_original_nine_palace_source_cells":0,
  "one_board_three_distinct_people":True,"one_Kedi_event_three_recasts":True,
  "book_first_answer_errors_after":errors,
  "source_terminal_appears_to_continue_no_book_closing_section":True,
  "no_static_388800_phrase_artifacts_generated":True,
  "prior_full_archive_SHA256":cfg["parent_sha256"],"new_full_archive_SHA256":digest(out.read_bytes()),
  "all_historical_original_rows_unchanged":True,
  "positive_training_approved":0,"counts":counts}
 def write(name,obj):(index_dir/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n","utf8")
 write("chapter_manifest.json",meta)
 write("case_index.json",{"new_cases":[{"case_id":cid(c[0]),"section":c[1],
  "domain":c[2],"source_range":[c[3],c[4]],"predicted_at_lines":c[7],
  "outcomes_reported_at_lines":c[8],"initial_book_error_explicit":bool(c[11])}
  for c in cfg["cases"]],"cross_book_same_event_reused":oldk})
 write("source_qa_index.json",{"qa":cfg["question_answers"],"source_sha256":CURRENT_SHA})
 write("source_cast_index.json",{"all_16_OCR_fragments":cfg["casts"],
  "verified_source_original_palace_cells":0,"each_original_row_sha256":{
   tag:[digest(source(L,n).encode()) for n in range(a,b+1)] for tag,a,b,_ in cfg["casts"]}})
 write("method_index.json",{"source_lines":cfg["method_lines"],
  "all_draft_conditions":True,"no_fixed_388800_sentences_generated":True})
 return meta
def main():
 p=argparse.ArgumentParser()
 for k in ("base","source","output","index-dir"):p.add_argument("--"+k,required=True)
 a=p.parse_args();print(j(build(a.base,a.source,a.output,a.index_dir)))
if __name__=="__main__":main()
