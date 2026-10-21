"""Kaiwu 2nd chapter, section 9: original two criminal cases, two printed boards.

Share Shenqi criminal_case domain. Both pre-existing crimes were known BEFORE
these inquiries; no pre-crime warning claim. Preserve stage-by-stage classroom
questioning; the announced arrest in case1 has NO reported final outcome.
Case2 author's own correction: predicted 2-3 culprits, actual 1; predicted
丁丑月, later book report voluntary surrender 丁丑日 (Nov21). The separately
reported approx 3 victims vs 4 is kept as a claim-level discrepancy too.
An offense-time cast is mentioned without a printed chart: do not invent it.
All original source text and every old SQLite row remain immutable.
"""
from __future__ import annotations
import argparse,hashlib,json,re,sqlite3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE_SHA="aa48d1f492e398c3216e7be15eb80653ab2bc57482c73f29a8d293d06b0ad47a"
SOURCE_SHA="f7e7dd3790e56bd43ed73e72d30ca9554609343c10640840b247b665d5b18b50"
BASE_NAME="WenguaApp_神奇之门21章_开悟之门14节_159案例_完整研究库.sqlite3"
NEW_NAME="WenguaApp_神奇之门21章_开悟之门15节_161案例_完整研究库.sqlite3"
CHAPTER="kaiwu/criminal_case_prediction_ch02_section09/v1"
SECTION="criminal_case_prediction_ch02_section09"
TITLE="第二章 日常百事预测评析 / 第九节 刑事案件预测（共2例）"
PALACES=(4,9,2,3,5,7,8,1,6)
LABELS=("巽4","离9","坤2","震3","中5","兑7","艮8","坎1","乾6")
CASES=[
 {"key":"robbery_classroom","id":"kaiwu.criminal.case01",
  "title":"石家庄1996年张志春、杜新会研讨班抢劫案课堂逐步推断",
  "begin":5,"end":50,"calendar":12,"start":15,"question":(7,9),
  "steps":[31,35,39,43,45,49],"first_forecasts":[31,35,39,43,45,49],
  "book_responses":[33,37,41,45,47],
  "facets":["robbery"],
  "note":"1996-12-14 classroom already aware of earlier robbery; 7000 yuan, two offenders, woman loss confirmed by ongoing class dialogue; instructor's one-suspect eventual arrest forecast line49 has NO later arrest feedback in original"},
 {"key":"lanzhou_homicide","id":"kaiwu.criminal.case02",
  "title":"1999年兰州凶杀案问测、事后自首与人数时间初断错误",
  "begin":51,"end":100,"calendar":55,"start":58,"question":(53,55),
  "steps":[74,76,78,80,82,84,86],"first_forecasts":[74,76,78,80,82,84,86],
  "book_responses":[88,90],"facets":["homicide"],
  "note":"Homicide occurred Nov9 and was told to diviner Nov14; this printed Qimen board belongs to question-time verification, NOT unprinted incident-time cast. Initial offender count 2-3 vs book one; prediction 丁丑月 vs Nov21 丁丑日, author explicitly says both wrong. Book says approx three victims vs actual four; editor line98/100 post-case explanations only"}
]
CLAIMS=[
 (1,"cash_amount_7000",31,33,"book_dialogue_confirmed","In-class attendee agrees exact 7000 yuan; not externally audited"),
 (1,"two_robbers",35,37,"book_dialogue_confirmed","In-class source dialogue confirms two robbers"),
 (1,"victim_woman",43,45,"book_dialogue_confirmed","During class officer confirms victim woman"),
 (1,"arrest_one_robber",49,None,"unconfirmed_forecast","Source ends after forecast, gives no actual arrest outcome"),
 (2,"murderer_number_2to3_vs_one",78,88,"book_explicit_error","Author predicted two-to-three offenders; later book says only ONE; explicitly admits first error at line90"),
 (2,"victim_number_approx3_vs_four",74,88,"book_reported_difference","Predicted approx three victims; book reports four, keep approximation discrepancy; author does not explicitly label this error"),
 (2,"arrest_DingChou_month_vs_day",86,88,"book_explicit_error","Initial 丁丑月 forecast versus book-reported Nov21 丁丑日 confession; explicitly admitted as wrongly timed"),
 (2,"self_surrender_possible",84,88,"book_reported_match","Book says perpetrator voluntarily surrendered; distinct from incorrect month/day precision")
]
def h(b):return hashlib.sha256(b).hexdigest()
def j(o):return json.dumps(o,ensure_ascii=False,sort_keys=True,separators=(",",":"))
def source(L,a,b=None):
 b=a if b is None else b
 if not 1<=a<=b<=len(L):raise ValueError(("Original interval invalid",a,b))
 return "\n".join(L[a-1:b])
def check_source(b):
 if h(b)!=SOURCE_SHA or len(b)!=12565 or not b.endswith(b"\n"):
  raise ValueError("Source original exact bytes/sha must not change")
 L=b.decode("utf-8").splitlines()
 if len(L)!=100 or L[0]!="第二章 日常百事预测评析" or L[2]!="第九节 刑事案件预测（共2例）":
  raise ValueError("Source chapter incomplete")
 if [n for n,z in enumerate(L,1) if z.startswith("（例")]!=[5,51]:
  raise ValueError("Two original event families only")
 if [n for n,z in enumerate(L,1) if z.startswith("┌")]!=[15,58]:
  raise ValueError("Two literal source 3x3 charts only")
 if "案发时间起局" not in L[52] or "问测时间验证" not in L[52]:
  raise ValueError("Unprinted other casting must not become a source panel")
 if "凶犯人数及破案时间未断准" not in L[89] or "二至三人" not in L[97] or "丁丑日" not in L[99]:
  raise ValueError("Author's explicit two wrong original guesses and editor post-result corrections required")
 if "还能抓住" in L[48]: raise ValueError("Don't invent arrest result")
 return L
def parse_chart(L,start):
 if not L[start-1].startswith("┌") or not L[start+12-1].startswith("└"):
  raise ValueError(("13-line source board unclosed",start))
 out=[]
 for band in range(3):
  base=start+1+4*band
  rows=[]
  for z in range(3):
   line=L[base+z-1]
   if not (line.startswith("│") and line.endswith("│")):raise ValueError(("Panel line broken",base+z))
   a=[v.strip() for v in line.split("│")[1:-1]]
   if len(a)!=3:raise ValueError(("Must preserve three original cols",base+z))
   rows.append(a)
  if band<2 and not L[base+2].startswith("├"):
   raise ValueError("Original horizontal divider lost")
  for col in range(3):
   idx=band*3+col;pal=PALACES[idx];lab=LABELS[idx]
   head,door,star=[rows[z][col] for z in range(3)]
   if not (head==lab or head.startswith(lab+" ")):
    raise ValueError(("Palace label altered",start,pal,head))
   god="" if pal==5 else head[len(lab):].strip()
   if pal==5 and (god or star or not door):
    raise ValueError("Center source has one OCR-marked stem string, not ordinary triple")
   if pal!=5 and (not god or not door or not star):
    raise ValueError(("Outer source palace incomplete",start,pal))
   original="\n".join((head,door,star))
   out.append({"palace":pal,"line":base+col,"start":base,"end":base+2,
     "header":head,"label":lab,"god":god,"door":door,"star":star,
     "raw":original,"sha":h(original.encode("utf8")),
     "ocr":int(any(q in original for q in ("原OCR","未辨","缺字","待核")))})
 if sorted(x["palace"] for x in out)!=list(range(1,10)):
  raise ValueError("Original nine palaces missing/duplicate")
 return out
def validate_cases(L):
 cases=[]
 for i,e in enumerate(CASES,1):
  cells=parse_chart(L,e["start"])
  if i==1 and (next(x for x in cells if x["palace"]==4)["door"]!="庚；杜门 癸" or
               next(x for x in cells if x["palace"]==5)["door"]!="庚（原OCR中宫字符）"):
   raise ValueError("Do not correct the first original chart's unusual source notation")
  if i==2 and (next(x for x in cells if x["palace"]==2)["door"]!="伤门 丙（壬）" or
               next(x for x in cells if x["palace"]==8)["star"]!="天芮 丙、天禽 壬" or
               next(x for x in cells if x["palace"]==5)["door"]!="壬（原OCR中宫字符）"):
   raise ValueError("Preserve original hosted Tianqin and center-stem text verbatim")
  cases.append({**e,"cells":cells,"chart_sha":h(source(L,e["start"],e["start"]+12).encode("utf8")),"number":i})
 if sum(len(e["steps"]) for e in cases)!=13 or sum(len(e["cells"]) for e in cases)!=18:
  raise ValueError("13 source reasoning turns and 18 palaces")
 return cases
def compare_preexisting_rows(old,db):
 for (table,) in old.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"):
  cols=[v[1] for v in old.execute('PRAGMA table_info("'+table+'")')]
  q=",".join('"'+col+'"' for col in cols)
  prior=list(old.execute('SELECT '+q+' FROM "'+table+'"'))
  after=set(db.execute('SELECT '+q+' FROM "'+table+'"'))
  if not all(r in after for r in prior):
   raise ValueError("Prior historical record changed in "+table)
def phase(db,L,e,key,kind,a,b=None,meta=None):
 b=a if b is None else b;original=source(L,a,b)
 info={"source_book_case_accepted_without_manual_user_review":True,
       "book_report_not_independent_criminal_case_verification":True,
       "later_disclosure_not_included_in_earlier_inference":True,**(meta or {})}
 db.execute("""INSERT INTO kaiwu_criminal_source_phases(chapter_key,case_id,phase_key,phase_type,
   first_line,last_line,original_text,excerpt_sha256,timing_json) VALUES (?,?,?,?,?,?,?,?,?)""",
  (CHAPTER,e["id"],key,kind,a,b,original,h(original.encode("utf8")),j(info)))
def ingest_case(db,sid,L,e):
 case=e["id"];idx=e["number"];bad=int(idx==2)
 dialogue="\n".join(source(L,n) for n in e["first_forecasts"])
 feedback="\n".join(source(L,n) for n in e["book_responses"])
 author="\n\n".join(source(L,n) for n in e["steps"])
 meta={"book":"kaiwu","source_span":[e["begin"],e["end"]],
 "crime_occurred_before_first_cast":True,"source_case_accepted":True,
 "manual_user_review_required":False,"independent_police_or_court_confirmation":False,
 "case1_arrest_result_not_reported":idx==1,
 "case2_unprinted_crime_time_cast_mentioned":idx==2,
 "case2_explicit_suspect_count_and_calendar_granularity_errors":idx==2,
 "case2_editor_corrected_after_feedback_not_initial":idx==2,
 "book_report_scope":e["note"]}
 db.execute("""INSERT INTO cases(case_id,section_id,event_family_id,domain_id,
 known_before,author_yongshen_steps,author_judgment,later_feedback,reviewed)
 VALUES (?,?,?,'criminal_case',?,?,?,?,1)""",
 (case,sid,case,source(L,*e["question"]),author,dialogue,feedback))
 db.execute("""INSERT INTO historical_case_protocol(case_id,completeness,published_chart_verification,
 feedback_independently_verified,eligible_blind_test,case_source_sha256,metadata_json)
 VALUES (?,'original_case_one_complete_nine_palace_chart','source_OCR_not_recast',0,0,?,?)""",
 (case,SOURCE_SHA,j(meta)))
 db.execute("""INSERT INTO historic_book_case_acceptance(case_id,source_book,source_chapter_key,
 source_documented_outcome,source_has_explicit_initial_error,metadata_json)
 VALUES (?,'kaiwu',?,?,?,?)""",
 (case,CHAPTER,"source_mixed_dialogue_some_future_unknown" if idx==1 else
 "book_report_one_culprit_four_victims_DingChou_day_not_initial_month",bad,j(meta)))
 for facet in ["criminal_case"]+e["facets"]:
  db.execute("""INSERT INTO unified_case_domain_facets(case_id,domain_id,
    source_chapter_key,primary_domain,note) VALUES (?,?,?,?,?)""",
   (case,facet,CHAPTER,int(facet=="criminal_case"),e["note"]))
 phase(db,L,e,"source_question","question_when_crime_already_occurred",*e["question"])
 phase(db,L,e,"source_chart","original_OCR_chart",e["start"],e["start"]+12)
 if idx==1:
  # A live classroom conversation: each prediction is followed by newly
  # disclosed facts. Treat all utterances as successive stages, not blind prior
  # knowledge available to the 1996-12-14 initial student query.
  for i,n in enumerate(e["first_forecasts"],1):
   phase(db,L,e,"speaker_judgment_"+str(i),"live_dialogue_sequential_prediction",n,
    meta={"available_source_facts_only_before_this_turn":True,
          "arrest_not_reported" if n==49 else "speaker_context":"no_later_feedback"})
  for i,n in enumerate(e["book_responses"],1):
   phase(db,L,e,"officer_feedback_"+str(i),"live_answer_revealed_after_that_inference",n)
 else:
  phase(db,L,e,"already_known_homicide","murder_on_Nov9_known_to_caller_before_Nov14",53)
  for i,n in enumerate(e["first_forecasts"],1):
   phase(db,L,e,"analysis_initial_"+str(i),"book_reported_initial_case_analysis",n)
  phase(db,L,e,"later_book_case_details","nov21_surrender_result_reported_later",88)
  phase(db,L,e,"student_admits_errors","explicit_original_two_wrong_guesses",90)
  phase(db,L,e,"editor_comment","later_editor_after_result_not_original_guess",92,96)
  phase(db,L,e,"editor_culprit_count_reinterpretation","post_result_correction_only",98)
  phase(db,L,e,"editor_arrest_day_reinterpretation","post_result_correction_only",100)
  db.execute("""INSERT INTO kaiwu_criminal_unprinted_cast_mentions(chapter_key,case_id,
   reference_key,original_line,original_quote) VALUES (?,?,?,?,?)""",
   (CHAPTER,case,"incident_time_cast_sent_teacher_not_printed",53,source(L,53)))
 db.execute("""INSERT INTO kaiwu_criminal_source_casts(chapter_key,case_id,
 cast_key,original_chart_start,original_chart_end,source_sha256,calendar_source_line,
 calendar_original,original_cast_type)
 VALUES (?,?,'primary',?,?,?,?,?,?)""",
 (CHAPTER,case,e["start"],e["start"]+12,e["chart_sha"],e["calendar"],
  source(L,e["calendar"]),"1996_classroom_current_hour" if idx==1
  else "1999_Nov14_query_time_not_unprinted_Nov9_incident_cast"))
 for c in e["cells"]:
  center=c["palace"]==5;ocr=c["ocr"]
  db.execute("""INSERT INTO kaiwu_criminal_original_palaces(chapter_key,case_id,cast_key,
   palace,source_start_line,source_end_line,header_original,deity_original,
   door_original,star_original,full_literal_original,source_sha256,ocr_marked)
   VALUES (?,?,'primary',?,?,?,?,?,?,?,?,?,?)""",
   (CHAPTER,case,c["palace"],c["start"],c["end"],c["header"],
    c["god"],c["door"],c["star"],c["raw"],c["sha"],ocr))
  db.execute("""INSERT INTO historical_chart_cells(case_id,palace,source_line,
   palace_label_raw,deity_raw,door_position_raw,star_position_raw,source_status)
   VALUES (?,?,?,?,?,?,?,'source_original_literal_OCR_unknown_not_normalized')""",
   (case,c["palace"],c["line"],c["label"],c["god"],c["door"],c["star"]))
  db.execute("""INSERT INTO historical_palace_standardization(case_id,cast_key,palace,
   center_stem,source_of_center_stem,standard_deity,standard_door,standard_star,
   normalized_status,original_raw_integrity_checked,method_reference,
   derived_host_palace,derived_host_source)
   VALUES (?,'primary',?,?,?,?,?,?,?,1,?,?,?)""",
   (case,c["palace"],None if center else None,
    "source_mid5_OCR_token_only_not_clean_stem" if center else "not_center",
    None if center or ocr else c["god"],
    None if center or ocr else c["door"],
    None if center or ocr else c["star"],
    "original_mid5_OCR_unknown_no_regular_door_star_god" if center else
    "source_OCR_not_inferred" if ocr else "source_literal_only_not_recast",
    "kaiwu_criminal_book_original_panels",2 if center else None,
    "center_host_Kun_rule_not_original_printed" if center else None))
 for k,n in enumerate(e["steps"],1):
  original=source(L,n)
  metadata={"source_book":"kaiwu","case_id":case,"original_line":n,
    "speaker":"Zhang_and_Du_in_class" if idx==1 else "Zhou_Pinji",
    "book_user_approved":True,
    "no_hindsight_or_external_scientific_claim":True,
    "positive_training_eligible":False,
    "original_claim_has_explicit_errors":bad}
  db.execute("""INSERT INTO historical_case_reasoning(case_id,step_number,source_line,
   author_analysis_original,short_method_topic,metadata_json)
   VALUES (?,?,?,?,?,?)""",
   (case,k,n,original,"staged_live_crime_analysis" if idx==1 else
   "crime_case_original_numbered_analysis",j(metadata)))
  db.execute("""INSERT INTO historical_case_reasoning_trace(case_id,step_number,source_line,
    evidence_json,review_status,positive_training_eligible)
    VALUES (?,?,?,?,'user_accepted_book_claims_not_unqualified_correct',0)""",
   (case,k,n,j(metadata)))
  concept=f"criminal:kaiwu:case{idx:02}:source_step{k:02}"
  db.execute("""INSERT INTO semantic_assertions(chapter_key,concept_id,kind,relation,
    source_start_line,source_end_line,metadata_json,original_excerpt,review_status)
    VALUES (?,?,?,?,?,?,?,?,'draft')""",
   (CHAPTER,concept,"criminal_original_source_reasoning","additional_exposition",
    n,n,j(metadata),original))
  db.execute("""INSERT INTO cross_book_concept_tracks(chapter_key,concept_id,
    source_start_line,source_end_line,source_section_id,source_sha256,excerpt_sha256,
    track_id,relation_to_prior,comparison_state,normalized_json,review_status)
    VALUES (?,?,?,?,?,?,?,?,?,'book_accepted_not_external_case_verification',?,'draft')""",
   (CHAPTER,concept,n,n,sid,SOURCE_SHA,h(original.encode("utf8")),
    "kaiwu:criminal_case:original_author_steps_v1","additional_exposition",j(metadata)))
 db.execute("""INSERT INTO historical_case_review_audit(case_id,original_steps,
   mechanical_step_trace,human_complete_step_chains,review_status,warning)
   VALUES (?,?,?,0,'user_accepts_book_case_no_manual_approval',?)""",
   (case,len(e["steps"]),len(e["steps"]),e["note"]))
 db.execute("""INSERT INTO historical_case_book_verdicts(event_family_id,
   primary_case_id,verdict,explicit_source_correction,source_correction_lines_json,
   feedback_source_lines_json,independent_external_verification,app_output_protocol,
   evidence_review_status,note)
   VALUES (?,?,?,?,?,?,'not_verified','single_answer_for_one_cast',
   'claims_partially_confirmed_and_explicit_errors_preserved',?)""",
   (case,case,"author_book_error_explicit" if bad else "author_book_success_default",
    bad,j([90,94,98,100] if bad else []),
    j([88,90] if bad else [33,37,41,45,47]),e["note"]))
def build(base,source_path,out,index_dir):
 base,source_path,out,index_dir=map(Path,(base,source_path,out,index_dir))
 if out.exists():raise ValueError("Do not overwrite earlier versioned whole SQLite")
 if h(base.read_bytes())!=BASE_SHA:raise ValueError("Wrong full immutable 159-case parent")
 raw=source_path.read_bytes();L=check_source(raw);cases=validate_cases(L)
 out.parent.mkdir(parents=True,exist_ok=True)
 with sqlite3.connect("file:"+str(base)+"?mode=ro",uri=True) as old,sqlite3.connect(out) as db:
  old.backup(db)
  db.executescript((ROOT/"schema/migrations/030_kaiwu_criminal_shared_domain_two_cases.sql").read_text("utf8"))
  db.execute("PRAGMA foreign_keys=ON")
  with db:
   if db.execute("SELECT count(*) FROM sections WHERE book_id='kaiwu'").fetchone()[0]!=14:
    raise ValueError("All earlier Kaiwu sources must remain")
   db.execute("""INSERT INTO sections(book_id,section_key,title,original_text,
     sha256,content_version,reviewed) VALUES ('kaiwu',?,?,?,?,1,1)""",
     (SECTION,TITLE,raw.decode("utf8"),SOURCE_SHA))
   sid=db.execute("SELECT last_insert_rowid()").fetchone()[0]
   db.execute("""INSERT INTO chapter_knowledge(chapter_key,book_id,title,
      source_sha256,source_length_bytes,knowledge_version,review_status)
      VALUES (?,'kaiwu',?,?,?,'1','approved')""",(CHAPTER,TITLE,SOURCE_SHA,len(raw)))
   for e in cases:ingest_case(db,sid,L,e)
   for num,key,pred,result,state,details in CLAIMS:
    case=cases[num-1]
    db.execute("""INSERT INTO kaiwu_criminal_scoped_claims(chapter_key,case_id,
     claim_key,prediction_line,prediction_original,feedback_line,feedback_original,
     verdict,interpretation_json) VALUES (?,?,?,?,?,?,?,?,?)""",
     (CHAPTER,case["id"],key,pred,source(L,pred),result,
      source(L,result) if result else None,state,j({"source_only":True,
        "verdict_notes":details,"initial_claim_not_retrospectively_replaced":True})))
   db.execute("""INSERT INTO chapter_archival_versions(archive_label,
    baseline_sha256,new_db_sha256,contains_complete_private_copyright_source,
    snapshot_type,created_utc,repo_public_archive_policy)
    VALUES (?,?,NULL,1,'two_criminal_original_source_charts_and_timed_error_scopes',
    '2026-10-20','user_authorized_public_full_sqlite_versions')""",
    ("shenqi21_kaiwu15_criminal_161cases",BASE_SHA))
  compare_preexisting_rows(old,db)
  if db.execute("PRAGMA integrity_check").fetchone()[0]!="ok" or db.execute("PRAGMA foreign_key_check").fetchall():
   raise ValueError("SQLite integrity violation after append")
  expected={"sections":36,"cases":161,"historical_chart_cells":1440,
    "historical_case_additional_casts":19,"historical_case_additional_cast_cells":171,
    "historical_palace_standardization":1611,
    "historical_case_reasoning":826,"historical_case_reasoning_trace":826,
    "semantic_assertions":2500,"cross_book_concept_tracks":1243,
    "cross_book_example_references":48,"historic_book_case_acceptance":53,
    "unified_case_domain_facets":75,
    "kaiwu_criminal_source_casts":2,"kaiwu_criminal_original_palaces":18,
    "kaiwu_criminal_scoped_claims":8,"kaiwu_criminal_unprinted_cast_mentions":1}
  counts={tab:db.execute('SELECT count(*) FROM "'+tab+'"').fetchone()[0] for tab in expected}
  if counts!=expected:raise ValueError(("Unexpected old/new historical totals",counts,expected))
  expected_case_ids=[f"shenqi.criminal_case.case{i:02}" for i in range(1,6)]+[e["id"] for e in cases]
  matches=db.execute("SELECT case_id,domain_id FROM unified_criminal_cases_across_books").fetchall()
  covered={row[0] for row in matches}
  if not set(expected_case_ids).issubset(covered):
   raise ValueError(("All five older criminal book cases and two new ones must be in SAME shared domain",
                     expected_case_ids,matches))
  if db.execute("SELECT count(*) FROM historical_case_book_verdicts WHERE verdict='author_book_error_explicit'").fetchone()[0]!=10:
   raise ValueError("Nine earlier source initial errors plus new murderer/date errors must remain")
  if db.execute("SELECT count(*) FROM kaiwu_criminal_scoped_claims WHERE verdict='book_explicit_error'").fetchone()[0]!=2:
   raise ValueError("Preserve TWO specific explicitly admitted errors, not post-hoc success")
  if db.execute("SELECT count(*) FROM kaiwu_criminal_scoped_claims WHERE verdict='unconfirmed_forecast'").fetchone()[0]!=1:
   raise ValueError("No source proof of eventual robber arrest")
  db.execute("VACUUM");db.commit()
  if db.execute("PRAGMA integrity_check").fetchone()[0]!="ok" or db.execute("PRAGMA foreign_key_check").fetchall():
   raise ValueError("SQLite final integrity failure")
 index_dir.mkdir(parents=True,exist_ok=True)
 report={"schema":"wengua_kaiwu_two_criminal_cases_2026_source_unified_v1",
  "source_title":TITLE,"source_sha256":SOURCE_SHA,"source_bytes":len(raw),
  "source_lines":len(L),"new_accepted_source_cases":2,
  "new_independent_event_families":2,"new_real_original_source_charts":2,
  "new_original_palace_cells":18,"new_complete_source_author_analysis_turns":13,
  "new_claims_distinctly_scoped":8,
  "book_explicit_wrong_murderer_count_and_arrest_calendar_granularity":True,
  "other_approx_victim_count_discrepancy_also_preserved":True,
  "first_classroom_arrest_prediction_unverified":True,
  "first_staged_feedback_must_not_precede_each_guess":True,
  "second_unprinted_incident_hour_cast_reference_not_fabricated":True,
  "editor_reinterpretation_is_after_suspect_confession":True,
  "shared_with_old_shenqi_criminal_case_domain":True,
  "all_book_cases_accepted_without_per_case_review":True,
  "not_independently_verified_criminal_law_enforcement_claims":True,
  "book_counts":{"shenqi":21,"kaiwu":15},
  "total_source_sections":36,"total_independent_historical_cases":161,
  "total_genuinely_original_printed_historical_casts":179,
  "total_explicit_whole_case_original_errors":10,
  "parent_sha256":BASE_SHA,"new_full_database_sha256":h(out.read_bytes()),
  "all_prior_table_rows_unchanged":True,"counts":counts}
 def save(name,x):(index_dir/name).write_text(json.dumps(x,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 save("chapter_manifest.json",report)
 save("case_index.json",{"source_sha256":SOURCE_SHA,
   "cases":[{k:v for k,v in e.items() if k!="cells"} for e in cases]})
 save("source_original_palaces.json",{"source_sha256":SOURCE_SHA,
   "boards":[{"case_id":e["id"],"start":e["start"],"original_nine_palaces":e["cells"]} for e in cases]})
 save("claim_and_timing_audit.json",{"source_sha256":SOURCE_SHA,
   "case1_7000_robbery_cash_reported_live":True,
   "case1_two_perpetrators_reported_live":True,
   "case1_final_arrest_prediction_has_no_book_feedback":True,
   "case2_murder_already_occurred_when_inquired":True,
   "case2_first_unprinted_crime_time_cast_not_fabricated":True,
   "case2_actual_one_perpetrator_not_predicted_two_or_three":True,
   "case2_predicted_DingChou_month_not_actual_DingChou_day":True,
   "case2_reported_four_victims_vs_initial_approx_three":True,
   "case2_editor_reanalysis_after_book_result_separate":True,
   "two_book_accepted_historical_cases_not_forensic_external_proof":True})
 return report
def main():
 p=argparse.ArgumentParser()
 for key in ("base","source","output","index-dir"):p.add_argument("--"+key,required=True)
 a=p.parse_args()
 print(json.dumps(build(a.base,a.source,a.output,a.index_dir),ensure_ascii=False,indent=2))
if __name__=="__main__":main()
