"""Append the original 11 Kaiwu business/finance chapter events to the full SQLite.

Source book section five has 11 separate inquiries and 11 actual original boards;
a mining collapse belongs to industrial_safety, not profit. Keep all OCR/extra
rows, same-business-project relationships, retrospective analyses, and author's
explicitly wrong factory start-date forecast. The user accepts book historical
cases without individual review, not as independently verified predictions.
"""
from __future__ import annotations
import argparse,hashlib,json,re,sqlite3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE_SHA="9107e3e440a1448cce93fdef288a48c88a8440b3998c5adcf041e2f770172ae7"
SOURCE_SHA="10d777fe514315c8e56dbef6d6a5152300b79c0ed041b92ee10f15cccef18fdf"
BASE_NAME="WenguaApp_神奇之门21章_开悟之门11节_138案例_完整研究库.sqlite3"
NEW_NAME="WenguaApp_神奇之门21章_开悟之门12节_149案例_完整研究库.sqlite3"
CHAPTER="kaiwu/business_profit_prediction_ch02_section05/v1"
SECTION="business_profit_prediction_ch02_section05"
TITLE="第五节经营求财预测(共11例)"
PAL=(4,9,2,3,5,7,8,1,6)
PALLABEL=("巽4","离9","坤2","震3","中5","兑7","艮8","坎1","乾6")
# case, chart caption, calendar line, question-source line, first-reading lines,
# book-reported result lines, primary domain, related facets, special timing note
SPEC=[
 ("lottery_xu_1997",3,6,4,[24,26,28,30,32,34],[35],"business_profit",["prize_draw"],"Book first reported source winner and dream; 5不遇时 editorial analysis is later"),
 ("loan_liu_1997",46,59,52,[53],[54],"business_profit",["credit_borrowing"],"First consultation and failure occurred before later printed and analysed historical chart"),
 ("joint_factory_shi_1997",85,95,86,[87,89,91],[133],"business_profit",["joint_venture"],"1998 feedback 15万 original investment and 6万 loss, disputes with partner"),
 ("kedi_funding_1998",135,142,138,[171],[172],"business_profit",["project_financing"],"Same Kedi company as case05 but distinct Aug 1998 funding application; 3000万元 grant Dec1 and later 2000万元 bond loan"),
 ("kedi_permit_miss_1999",174,180,176,[200],[201,202],"business_profit",["administrative_permit"],"Explicit author mistake predicted Jun21/22; construction permit and actual start only Jun29; NEVER retrospectively mark advance success"),
 ("drugstore_tax_shi_1997",204,211,205,[205],[206,250],"business_profit",["tax_dispute"],"March 4 37500-yuan tax penalty; prior 1996 official dispute already existed"),
 ("taihe_mall_build_1999",252,258,254,[283],[284,286],"business_profit",["property_development"],"Taihe daily chemicals mall actual opening Jan8 2000; same mall as case08 but question different"),
 ("taihe_shop_purchase_1999",288,294,290,[321],[322,323,324],"business_profit",["property_investment"],"Different buyer, same Taihe mall project; advance first-quarter rent vs unverified long-term rental yield"),
 ("cake_water_issue_1999",334,342,337,[338],[339],"business_profit",["food_production"],"Author already heard cake troubles and privately cast before explaining to owner; warm water restored production by book report"),
 ("mine_rescue_liu_1999",366,379,373,[410,413,416],[411,414,418],"industrial_safety",["business_profit"],"Five trapped workers rescued at 19:10 without reported injuries; mine-safety life risk, NOT ordinary profit success or scientific safety certification"),
 ("lottery_he_2000",430,437,435,[456,458,460],[433,463],"business_profit",["prize_draw"],"One first prize of 9900 yuan; another boy's 100000 prize is a mention not extra question or new printed chart")
]
STEPS_RE=re.compile(r"^\([1-9]\)|^[A-F]、")
def digest(b):return hashlib.sha256(b).hexdigest()
def J(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(",",":"))
def span(L,a,b=None):
 b=a if b is None else b
 if not 1<=a<=b<=len(L):raise ValueError(("Invalid source line",a,b))
 return "\n".join(L[a-1:b])
def prepare(raw):
 if digest(raw)!=SOURCE_SHA:raise ValueError("The actual user-uploaded UTF8 exact SHA changed")
 L=raw.decode("utf8").splitlines()
 if len(L)!=467 or L[0]!=TITLE or not raw.endswith(b"\n"):
  raise ValueError("Full 467-line source missing or truncated")
 titles=[i for i,l in enumerate(L,1) if re.match(r"^\(例[一二三四五六七八九十]+\)",l)]
 if titles!=[x[1] for x in SPEC]:raise ValueError(("Original eleven section headings mismatch",titles))
 captions=[i for i,l in enumerate(L,1) if l.startswith("奇门九宫格（例")]
 if captions!=[x[2] for x in SPEC]:raise ValueError(("Exactly 11 original printed boards required",captions))
 if "此例断错" not in L[200] or "6月29日" not in L[201]:
  raise ValueError("Author explicitly incorrect date and later correction lost")
 if "7点10分" not in L[417] or "五个工人" not in L[410]:
  raise ValueError("Book's real reported five-worker rescue source lost")
 return L
def board(L,caption):
 if not L[caption].startswith("+"):raise ValueError(("Original ASCII source border absent",caption))
 bands=[];rows=[]
 for line_number in range(caption+1,len(L)+1):
  line=L[line_number-1]
  if line.startswith("+"):
   if rows:
    bands.append(rows);rows=[]
   if len(bands)==3:
    finish=line_number
    break
  elif line.startswith("|"):
   cells=[v.strip() for v in line.split("|")[1:-1]]
   if len(cells)!=3:raise ValueError(("Three source columns must remain",line_number))
   rows.append((line_number,cells))
  else:raise ValueError(("Original board interrupted",caption,line_number))
 else:raise ValueError("Missing closing original source border")
 if any(len(x) not in (3,4) for x in bands):raise ValueError(("Original optional OCR/host row damaged",caption))
 result=[]
 for band,lines in enumerate(bands):
  for col in range(3):
   palace=PAL[band*3+col]
   head,door,star=[lines[k][1][col] for k in range(3)]
   extra=lines[3][1][col] if len(lines)==4 else ""
   if palace==5:
    if not head.startswith("中5：") or door or star or extra:
     raise ValueError("Original center is source single raw stem only; never add regular deity/door/star")
   elif not head or not door or not star:
    raise ValueError(("Must preserve noncenter OCR cells as raw text, not blank/guessed",caption,palace))
   raw="\n".join(lines[n][1][col] for n in range(len(lines)))
   damaged=int(any(x in raw for x in ("OCR","缺字","缺损","游离")))
   result.append({"palace":palace,"start":lines[0][0],"end":lines[-1][0],
    "source_line":lines[0][0]+col,"label":PALLABEL[band*3+col],
    "head":head,"door":door,"star":star,"extra":extra,"raw":raw,
    "sha":digest(raw.encode("utf8")),"damaged":damaged})
 if len(result)!=9 or sorted(x["palace"] for x in result)!=list(range(1,10)):
  raise ValueError(("Exactly nine mapped original source columns needed",caption))
 return finish,result
def events(L):
 found=[]
 for idx,(key,heading,caption,question,initial,feedback,domain,facets,note) in enumerate(SPEC,1):
  end=SPEC[idx][1]-1 if idx<len(SPEC) else len(L)
  finish,cells=board(L,caption)
  steps=[p for p in range(heading,end+1) if STEPS_RE.match(L[p-1])]
  if not steps:raise ValueError(("No complete source reasoning headings",idx))
  if any(p>len(L) for p in initial+feedback):raise ValueError("Original source prediction/feedback line missing")
  cid=f"kaiwu.business.case{idx:02}"
  e={"key":key,"number":idx,"id":cid,"title":L[heading-1],
    "begin":heading,"end":end,"caption":caption,"chart_start":caption+1,
    "chart_end":finish,"chart_sha":digest(span(L,caption+1,finish).encode("utf8")),
    "question":question,"initial":initial,"feedback":feedback,
    "domain":domain,"facets":facets,"note":note,"steps":steps,"cells":cells}
  found.append(e)
 if sum(len(x["steps"]) for x in found)!=64:raise ValueError("All 64 original listed source analysis headings required")
 if sum(len(x["cells"]) for x in found)!=99:raise ValueError("11 original boards x nine palaces")
 if sum(x["damaged"] for e in found for x in e["cells"])<8:
  raise ValueError("Original OCR damaged palaces must remain uncertain, not filled")
 if found[4]["feedback"]!=[201,202]:raise ValueError("Author construction-date original error mandatory")
 if found[9]["domain"]!="industrial_safety":raise ValueError("Mine rescue is high-stakes workplace accident, not profit")
 return found
def previous_rows_identical(old,db):
 for (table,) in old.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"):
  columns=[p[1] for p in old.execute('PRAGMA table_info("'+table+'")')]
  select=",".join('"'+v+'"' for v in columns)
  original=list(old.execute('SELECT '+select+' FROM "'+table+'"'))
  current=set(db.execute('SELECT '+select+' FROM "'+table+'"'))
  if not all(row in current for row in original):
   raise ValueError("Source-preserving append-only policy violated for "+table)
def phase(db,L,e,name,kind,a,b=None,meta=None):
 b=a if b is None else b;original=span(L,a,b)
 facts={"case_user_approved_source_without_individual_review":True,
 "author_book_feedback_not_independent_verification":True,
 "cannot_leak_later_event_information_into_first_forecast":True,**(meta or {})}
 db.execute("""INSERT INTO kaiwu_business_case_phases(chapter_key,case_id,phase_key,
  phase_type,first_source_line,last_source_line,full_original_text,original_sha256,
  chronological_notes_json) VALUES (?,?,?,?,?,?,?,?,?)""",
 (CHAPTER,e["id"],name,kind,a,b,original,digest(original.encode("utf8")),J(facts)))
def insert_case(db,sid,L,e):
 cid=e["id"];i=e["number"]
 question=span(L,e["question"])
 if i==6:question=question.split("预测之后",1)[0]
 if i==11:question=span(L,435) # winner disclosed earlier: do not misrepresent as blind test
 raw_steps="\n\n".join(span(L,n) for n in e["steps"])
 forecast="\n".join(span(L,n) for n in e["initial"])
 outcome="\n".join(span(L,n) for n in e["feedback"])
 if i==5:outcome+="\n"+span(L,202)
 meta={"case_number":i,"source_start":e["begin"],"source_end":e["end"],
 "user_book_case_accepted_no_per_case_review":True,
 "book_report_not_empirically_verified":True,
 "source_chart_contains_OCR_gaps":any(c["damaged"] for c in e["cells"]),
 "explicit_first_prediction_error":i==5,
 "retrospective_analysis_present":i in (1,2,3,8,9,10,11),
 "safety_cannot_be_assessed_by_divination":i==10,
 "not_separate_award_winner_event":i==11,"note":e["note"]}
 db.execute("""INSERT INTO cases(case_id,section_id,event_family_id,domain_id,
  known_before,author_yongshen_steps,author_judgment,later_feedback,reviewed)
  VALUES (?,?,?,?,?,?,?,?,1)""",
 (cid,sid,cid,e["domain"],question,raw_steps,forecast,outcome))
 db.execute("""INSERT INTO historical_case_protocol(case_id,completeness,
  published_chart_verification,feedback_independently_verified,eligible_blind_test,
  case_source_sha256,metadata_json)
  VALUES (?,'full_book_original_case_and_one_printed_chart',
   'exact_book_source_not_recased_or_repaired',0,0,?,?)""",
 (cid,SOURCE_SHA,J(meta)))
 db.execute("""INSERT INTO historic_book_case_acceptance(case_id,source_book,
  source_chapter_key,source_documented_outcome,source_has_explicit_initial_error,metadata_json)
  VALUES (?,'kaiwu',?,?,?,?)""",
 (cid,CHAPTER,"author_initial_date_wrong_and_later_corrected" if i==5 else
 "original_book_historical_report_with_claim_scope",int(i==5),J(meta)))
 for facet in [e["domain"]]+e["facets"]:
  db.execute("""INSERT INTO unified_case_domain_facets(case_id,domain_id,
   source_chapter_key,primary_domain,note) VALUES (?,?,?,?,?)""",
 (cid,facet,CHAPTER,int(facet==e["domain"]),e["note"]))
 phase(db,L,e,"known_before","source_known_at_question",e["question"],meta={"prediction_interleaved_in_original":i==6})
 phase(db,L,e,"full_original_chart","original_unrepaired_source_cast",e["chart_start"],e["chart_end"])
 for k,line in enumerate(e["initial"],1):
  phase(db,L,e,"initial_judgment_"+str(k),"author_first_reported_judgment",line)
 for k,line in enumerate(e["feedback"],1):
  phase(db,L,e,"reported_feedback_"+str(k),"later_book_report_or_disclosure",line)
 if i==5:
  phase(db,L,e,"explicit_book_first_date_error","author_self_admitted_incorrect_initial_forecast",201,202,
    {"initial_june21_or22":True,"actual_permit_and_start_june29":True,
     "no_retroactive_success":True})
  db.execute("""INSERT INTO kaiwu_business_claim_verdicts(chapter_key,case_id,claim_key,
  original_prediction_line,original_prediction,reported_feedback_line,reported_feedback,
  verdict,scope) VALUES (?,?,?,?,?,?,?,?,?)""",
  (CHAPTER,cid,"factory_opening_day",200,span(L,200),202,span(L,201,202),
   "author_book_error_explicit","June21/22 advance opening wrong; June29 permit granted and opening occurred"))
 if i==8:
  db.execute("""INSERT INTO kaiwu_business_claim_verdicts(chapter_key,case_id,claim_key,
  original_prediction_line,original_prediction,reported_feedback_line,reported_feedback,
  verdict,scope) VALUES (?,?,?,?,?,?,?,?,?)""",
  (CHAPTER,cid,"first_quarter_rent_vs_long_term",321,span(L,321),324,span(L,323,324),
   "book_reported_partial_followup","First three-month rent prepaid; future multiyear profits NOT reported"))
 if i==10:
  db.execute("""INSERT INTO kaiwu_business_claim_verdicts(chapter_key,case_id,claim_key,
  original_prediction_line,original_prediction,reported_feedback_line,reported_feedback,
  verdict,scope) VALUES (?,?,?,?,?,?,?,?,?)""",
  (CHAPTER,cid,"mine_five_workers_rescued",416,span(L,416),418,span(L,418),
   "book_reported_match_only","Reported all five rescued unharmed 19:10; not independently verified; real mine safety must use emergency response"))
 if i==11:phase(db,L,e,"unrelated_other_jackpot","other_winner_not_an_extra_event",462)
 db.execute("""INSERT INTO kaiwu_business_source_casts(chapter_key,case_id,cast_key,
  source_grid_caption_line,source_grid_start,source_grid_end,source_grid_sha256,
  first_calendar_source_line,source_calendar_literal)
  VALUES (?,?,'primary',?,?,?,?,?,?)""",
 (CHAPTER,cid,e["caption"],e["chart_start"],e["chart_end"],e["chart_sha"],
 e["question"],span(L,e["question"])))
 for c in e["cells"]:
  mid=c["palace"]==5
  db.execute("""INSERT INTO kaiwu_business_literal_palaces(chapter_key,case_id,cast_key,
   palace,source_start_line,source_end_line,source_header,source_door,source_star,
   extra_row_raw,source_literal,source_literal_sha256,ocr_incomplete)
   VALUES (?,?,'primary',?,?,?,?,?,?,?,?,?,?)""",
 (CHAPTER,cid,c["palace"],c["start"],c["end"],c["head"],c["door"],c["star"],
 c["extra"],c["raw"],c["sha"],c["damaged"]))
  db.execute("""INSERT INTO historical_chart_cells(case_id,palace,source_line,
  palace_label_raw,deity_raw,door_position_raw,star_position_raw,source_status)
  VALUES (?,?,?,?,?,?,?,'exact_source_short_symbol_ocr_uncertainty_preserved')""",
 (cid,c["palace"],c["source_line"],c["label"],c["head"],c["door"],c["star"]))
  db.execute("""INSERT INTO historical_palace_standardization(case_id,cast_key,palace,
  center_stem,source_of_center_stem,standard_deity,standard_door,standard_star,
  normalized_status,original_raw_integrity_checked,method_reference,
  derived_host_palace,derived_host_source)
  VALUES (?,'primary',?,?,?,?,?,?,?,1,?,?,?)""",
  (cid,c["palace"],c["head"].split("：",1)[1] if mid else None,
   "source_mid5_literal_stem_no_regular_8god_door_star" if mid else "not_center",
   None if mid or c["damaged"] else c["head"],
   None if mid or c["damaged"] else c["door"],
   None if mid or c["damaged"] else c["star"],
   "source_middle_not_regular_triple" if mid else
   "ocr_missing_source_not_repaired" if c["damaged"] else
   "source_short_symbols_not_expanded_by_guess",
   "kaiwu_business_original_11_source_charts",
   2 if mid else None,"derived_center_host_to_kun_only_not_printed" if mid else None))
 for n,line in enumerate(e["steps"],1):
  original=span(L,line)
  phase_type=("post_outcome_explanation" if
   ((i==1 and line>=40) or (i==8 and line>=328) or
    (i==10 and line>=422) or (i==11 and line>=456) or
    (i==2 and line>=77) or (i==9 and line>=360))
   else "author_original_analysis")
  extra={"case_id":cid,"source_line":line,"analysis_time":phase_type,
   "book_case_user_accepted":True,"positive_training_eligible":False,
   "initial_date_wrong":i==5}
  db.execute("""INSERT INTO historical_case_reasoning(case_id,step_number,
  source_line,author_analysis_original,short_method_topic,metadata_json)
  VALUES (?,?,?,?,?,?)""",(cid,n,line,original,phase_type,J(extra)))
  db.execute("""INSERT INTO historical_case_reasoning_trace(case_id,step_number,
  source_line,evidence_json,review_status,positive_training_eligible)
  VALUES (?,?,?,?,'book_case_accepted_method_not_automatically_positive',0)""",
  (cid,n,line,J(extra)))
  concept=f"business:kaiwu:case{i:02}:original_step{n:02}"
  db.execute("""INSERT INTO semantic_assertions(chapter_key,concept_id,kind,relation,
  source_start_line,source_end_line,metadata_json,original_excerpt,review_status)
  VALUES (?,?,?,?,?,?,?,?,'draft')""",
  (CHAPTER,concept,"book_historical_case_analysis","additional_exposition",
   line,line,J(extra),original))
  db.execute("""INSERT INTO cross_book_concept_tracks(chapter_key,concept_id,
  source_start_line,source_end_line,source_section_id,source_sha256,excerpt_sha256,
  track_id,relation_to_prior,comparison_state,normalized_json,review_status)
  VALUES (?,?,?,?,?,?,?,?,?,'book_case_accepted_without_external_verification',?,'draft')""",
  (CHAPTER,concept,line,line,sid,SOURCE_SHA,digest(original.encode("utf8")),
   "kaiwu:business:author_original_v1","additional_exposition",J(extra)))
 db.execute("""INSERT INTO historical_case_review_audit(case_id,original_steps,
  mechanical_step_trace,human_complete_step_chains,review_status,warning)
  VALUES (?,?,?,0,'historical_original_book_accepted_no_per_case_manual_approval',?)""",
  (cid,len(e["steps"]),len(e["steps"]),e["note"]))
 db.execute("""INSERT INTO historical_case_book_verdicts(event_family_id,
  primary_case_id,verdict,explicit_source_correction,source_correction_lines_json,
  feedback_source_lines_json,independent_external_verification,app_output_protocol,
  evidence_review_status,note)
 VALUES (?,?,?,?,?,?,'not_verified','single_answer_for_one_cast',
  'book_source_only_preserve_specific_error',?)""",
 (cid,cid,"author_book_error_explicit" if i==5 else "author_book_success_default",
  int(i==5),J([201,202] if i==5 else []),J(e["feedback"]),e["note"]))
def build(base,source,output,index_dir):
 base,source,output,index_dir=map(Path,(base,source,output,index_dir))
 if output.exists():raise ValueError("Never overwrite a previous full SQLite archive")
 if digest(base.read_bytes())!=BASE_SHA:raise ValueError("Parent is not the latest genuine 138-case full SQLite")
 raw=source.read_bytes();L=prepare(raw);ev=events(L)
 output.parent.mkdir(parents=True,exist_ok=True)
 with sqlite3.connect("file:"+str(base)+"?mode=ro",uri=True) as old,sqlite3.connect(output) as db:
  old.backup(db)
  db.executescript((ROOT/"schema/migrations/027_kaiwu_business_mixed_domains_11cases.sql").read_text("utf8"))
  db.execute("PRAGMA foreign_keys=ON")
  with db:
   if db.execute("SELECT COUNT(*) FROM sections WHERE book_id='kaiwu'").fetchone()[0]!=11:
    raise ValueError("All 11 earlier Kaiwu source chapters must be present")
   db.execute("""INSERT INTO sections(book_id,section_key,title,original_text,
   sha256,content_version,reviewed) VALUES ('kaiwu',?,?,?,?,1,1)""",
   (SECTION,TITLE,raw.decode("utf8"),SOURCE_SHA))
   sid=db.execute("SELECT last_insert_rowid()").fetchone()[0]
   db.execute("""INSERT INTO chapter_knowledge(chapter_key,book_id,title,source_sha256,
    source_length_bytes,knowledge_version,review_status)
    VALUES (?,'kaiwu',?,?,?,'1','approved')""",(CHAPTER,TITLE,SOURCE_SHA,len(raw)))
   for e in ev:insert_case(db,sid,L,e)
   for a,b,relation,line in (
    (5,4,"same_Kedi_pharmaceuticals_separate_1998_fund_and_1999_permit_decisions",176),
    (8,7,"same_Taihe_mall_different_property_investor_and_1999_developer_questions",289)):
    ea,eb=ev[a-1],ev[b-1]
    db.execute("""INSERT INTO kaiwu_business_related_projects(chapter_key,case_id,
     related_case_id,association,same_project,same_question,source_evidence_line,
     source_evidence_literal) VALUES (?,?,?,?,1,0,?,?)""",
     (CHAPTER,ea["id"],eb["id"],relation,line,span(L,line)))
   db.execute("""INSERT INTO cross_book_example_references(source_chapter_key,
    source_line,target_book_id,target_printed_page,reference_key,metadata_json,
    verified_target_case_id) VALUES (?,433,'shenqi','unprinted_in_source',?,?,NULL)""",
    (CHAPTER,"kaiwu:lottery_ex11_reference_shenqi_charity_lottery",
     J({"quoted_book":"神奇之门","source_line":433,
       "old_prize_lottery_example_not_new_independent_event":True,
       "same_historical_event":False})))
   db.execute("""INSERT INTO chapter_archival_versions(archive_label,baseline_sha256,
     new_db_sha256,contains_complete_private_copyright_source,snapshot_type,
     created_utc,repo_public_archive_policy)
     VALUES (?,?,NULL,1,'kaiwu_11_source_real_charts_one_fatal_date_error_and_mine_safety',
      '2026-10-20','user_authorized_public_full_sqlite_versions')""",
     ("shenqi21_kaiwu12_business11_149cases",BASE_SHA))
  previous_rows_identical(old,db)
  if db.execute("PRAGMA integrity_check").fetchone()[0]!="ok" or db.execute("PRAGMA foreign_key_check").fetchall():
   raise ValueError("Original and new full SQLite integrity failed")
  expected={"sections":33,"cases":149,"historical_chart_cells":1332,
   "historical_case_additional_casts":18,"historical_case_additional_cast_cells":162,
   "historical_palace_standardization":1494,"historical_case_reasoning":754,
   "historical_case_reasoning_trace":754,"semantic_assertions":2428,
   "cross_book_concept_tracks":1171,"cross_book_example_references":47,
   "historic_book_case_acceptance":41,"unified_case_domain_facets":50,
   "kaiwu_business_source_casts":11,"kaiwu_business_literal_palaces":99,
   "kaiwu_business_related_projects":2,"kaiwu_business_claim_verdicts":3}
  got={t:db.execute('SELECT count(*) FROM "'+t+'"').fetchone()[0] for t in expected}
  if got!=expected:raise ValueError(("Full archive cumulative table count differs",got,expected))
  if db.execute("SELECT count(*) FROM cases WHERE domain_id='industrial_safety'").fetchone()[0]!=1:
   raise ValueError("Mine-collapse case must be independently retrievable as safety")
  if db.execute("SELECT count(*) FROM cases WHERE domain_id='business_profit'").fetchone()[0]<24:
   raise ValueError("Must reuse original Shenqi business cases in SAME domain")
  if db.execute("SELECT count(*) FROM historical_case_book_verdicts WHERE verdict='author_book_error_explicit'").fetchone()[0]!=9:
   raise ValueError("Prior 8 explicit first errors plus case5 author admission must remain")
  if db.execute("SELECT count(*) FROM kaiwu_business_literal_palaces WHERE extra_row_raw!=''").fetchone()[0]<8:
   raise ValueError("Raw original host/OCR supplementary rows have been lost")
  db.execute("VACUUM");db.commit()
  if db.execute("PRAGMA integrity_check").fetchone()[0]!="ok" or db.execute("PRAGMA foreign_key_check").fetchall():
   raise ValueError("Final after VACUUM SQLite integrity failure")
 index_dir.mkdir(parents=True,exist_ok=True)
 manifest={"schema":"wengua_kaiwu_11_business_cases_and_mine_safety_full_backup_v1",
  "source_title":TITLE,"source_sha256":SOURCE_SHA,"source_bytes":len(raw),
  "source_lines":len(L),"new_actual_independent_events":11,
  "new_actual_source_printed_charts":11,"new_literal_palace_cells":99,
  "numbered_and_A_F_author_analysis_units":64,
  "original_OCR_damage_in_source_palaces":sum(c["damaged"] for e in ev for c in e["cells"]),
  "supplemental_original_palace_rows":sum(bool(c["extra"]) for e in ev for c in e["cells"]),
  "new_related_same_project_distinct_question_links":2,
  "explicit_author_first_forecast_date_failure_case5":True,
  "industrial_rescue_primary_not_business_profit":True,
  "lottery_other_prize_winner_not_new_actual_cast":True,
  "all_book_cases_accepted_without_manual_review":True,
  "no_claim_of_independent_safety_or_financial_validation":True,
  "book_counts":{"shenqi":21,"kaiwu":12},"total_source_sections":33,
  "total_distinct_historical_events":149,"total_original_historical_casts":166,
  "total_old_explicit_error_cases_plus_new":9,
  "parent_sha256":BASE_SHA,"new_database_sha256":digest(output.read_bytes()),
  "all_prior_table_rows_unchanged":True,"cumulative_counts":got}
 def write(n,obj):
  (index_dir/n).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 write("chapter_manifest.json",manifest)
 write("case_index.json",{"source_sha256":SOURCE_SHA,
   "cases":[{k:v for k,v in e.items() if k!="cells"} for e in ev]})
 write("original_nine_palaces.json",{"source_sha256":SOURCE_SHA,
   "boards":[{"case_id":e["id"],"source_grid":e["chart_start"],"palaces":e["cells"]} for e in ev]})
 write("source_audit.json",{"source_sha256":SOURCE_SHA,
   "case05_first_advance_wrong_21_22_june_actual_29_june":True,
   "case04_and_05_one_company_two_dated_events":True,
   "case07_and_08_one_mall_two_different_respondents":True,
   "case10_five_trapped_miners_life_safety_source_only":True,
   "case11_unprinted_other_jackpot_only_book_reference":True,
   "eleven_actual_source_charts_no_fabrication":True,
   "center_palaces_not_auto_regularized":True,
   "unreadable_OCR_and_special_extra_source_rows_kept":True,
   "all_original_source_text_exact_and_all_previous_rows_untouched":True,
   "all_user_book_cases_no_individual_approval":True})
 return manifest
def main():
 ap=argparse.ArgumentParser()
 for option in ("base","source","output","index-dir"):
  ap.add_argument("--"+option,required=True)
 args=ap.parse_args()
 print(json.dumps(build(args.base,args.source,args.output,args.index_dir),ensure_ascii=False,indent=2))
if __name__=="__main__":main()
