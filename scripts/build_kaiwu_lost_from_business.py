"""《开悟之门》第二章第八节：钱物丢失预测（共4例）.

Original 180-line, 19588-byte source, four events/four full original ASCII-
bordered 9-palace OCR-rearranged charts. The *existing* Shenqi lost_property
domain remains shared by book sources. All prior 149 rows/versions untouched
via SHA-pinned sqlite3.backup(). Do not rewrite missing original OCR glyphs.
The fourth case's Aug 20 first forecast was SIX-YAO, and Qimen was learned
only AFTER the book purchase Aug 26; do not treat later Qimen explanation
as an August 20 blind Qimen prediction.
"""
from __future__ import annotations
import argparse,hashlib,json,re,sqlite3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE_SHA="cd1f9e1d4e352644b062bc048afb977dcc457c40bf76a5673a6e39ae93f21ac5"
SOURCE_SHA="fad699fbddf34f7bf4ff16849d4154d4633bce51c234db1cf0ecc4ff7eb8f554"
BASE_NAME="WenguaApp_神奇之门21章_开悟之门12节_149案例_完整研究库.sqlite3"
NEW_NAME="WenguaApp_神奇之门21章_开悟之门13节_153案例_完整研究库.sqlite3"
CHAPTER="kaiwu/lost_property_prediction_ch02_section08/v1"
SECTION="lost_property_prediction_ch02_section08"
TITLE="第二章 日常百事预测评析 / 第八节 钱物丢失预测（共4例）"
PAL=(4,9,2,3,5,7,8,1,6)
LABEL=("巽4","离9","坤2","震3","中5","兑7","艮8","坎1","乾6")
HEADING_RE=re.compile(r"^(?:（[1-9][0-9]*）|[A-D]、)")
SPEC=[
 dict(key="briefcase_cash_missed",case_id="kaiwu.lost_property.case01",
  title="田风良摩托车公文包及现金丢失",start=5,end=45,caption=15,grid=16,
  question=7,calendar=13,first=9,feedback=11,
  analyze=(31,44),reason_end=44,facets=["monetary_loss"],
  notes="1997-10-12 pouch recovered sixth evening; ¥4,300 cash missing, others returned; not established that collector stole cash",
  chronology="1997-10-12 evening inquiry, 1997-10-18 morning reported return",
  issue="bag_returned_but_cash_missing",theft=False),
 dict(key="stolen_motorbike_police_recovered",case_id="kaiwu.lost_property.case02",
  title="石建国自测摩托车失窃与警方追回",start=46,end=88,caption=56,grid=57,
  question=48,calendar=54,first=50,feedback=52,
  analyze=(72,87),reason_end=87,facets=["criminal_theft"],
  notes="1997-07-24 three thieves, police chase and accident, court compensation 990 yuan; reported in book only",
  chronology="night 1997-07-24 theft, next-morning police report, post-case account",
  issue="motorbike_stolen_recovered_police_prosecution",theft=True),
 dict(key="mislaid_earring_at_home",case_id="kaiwu.lost_property.case03",
  title="王夕强测耳环误以为外出丢失",start=89,end=124,caption=96,grid=97,
  question=91,calendar=94,first=117,feedback=123,
  analyze=(112,114),reason_end=114,facets=[],
  notes="A lost earring was found on the bed at home 17:30; not a crime; original says forgotten/mislaid, not stolen",
  chronology="1999-06-11 13:40 cast, 17:30 reported found at home",
  issue="mislaid_earring_recovered_same_day",theft=False),
 dict(key="tong_motorbike_later_qimen",case_id="kaiwu.lost_property.case04",
  title="佟安琪1999年摩托车失窃追回与后学奇门回顾",start=125,end=180,caption=155,grid=156,
  question=139,calendar=153,first=139,feedback=180,
  analyze=(171,178),reason_end=178,facets=["criminal_theft"],
  notes="Initial Aug 20 forecast by 六爻, not Qimen; bought 神奇之门 on Aug26, learned chart seven days later; Sep17 recovery, original precise day reading is retrospectively recounted without documented contemporaneous timing",
  chronology="1999-08-20 phone/six-yao, 08-26 book purchase, early Sep Qimen learned, 09-17 found, 2000-08-27 letter",
  issue="motorbike_stolen_recovered_28_days",theft=True)
]
def h(data):return hashlib.sha256(data).hexdigest()
def j(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":"))
def src(lines,a,b=None):
 b=a if b is None else b
 if not (1<=a<=b<=len(lines)):raise ValueError(("Invalid source interval",a,b))
 return "\n".join(lines[a-1:b])
def prepare(raw):
 if h(raw)!=SOURCE_SHA:raise ValueError("Exact user original bytes changed")
 L=raw.decode("utf-8").splitlines()
 if len(L)!=180 or len(raw)!=19588 or not raw.endswith(b"\n"):
  raise ValueError("Must store the full exact newline-terminated source")
 if L[0]!="第二章 日常百事预测评析" or L[2]!="第八节 钱物丢失预测（共4例）":
  raise ValueError("Wrong source heading")
 if [i for i,x in enumerate(L,1) if re.match(r"^（例[一二三四]）",x)]!=[5,46,89,125]:
  raise ValueError("Four full user-supplied examples required")
 if [i for i,x in enumerate(L,1) if x.startswith("┌") ]!=[16,57,97,156]:
  raise ValueError("Exactly four actual printed OCR-rearranged source boards")
 if "六爻卦" not in L[138] or "8月26日" not in L[140] or "七天后" not in L[140]:
  raise ValueError("Six-yao first and later Qimen chronology missing")
 if "原OCR" not in L[25] or "缺损" not in L[25] or "原OCR" not in L[26]:
  raise ValueError("Source incomplete original palace tokens missing")
 if "九百九十元" not in L[51] or "下午5点30分" not in L[122]:
  raise ValueError("Partial returns/compensation feedback missing")
 return L
def panel(L,start):
 if not L[start-1].startswith("┌") or not L[start+12-1].startswith("└"):
  raise ValueError(("Original 13-line Qimen panel altered",start))
 out=[]
 for r in range(3):
  base=start+1+r*4
  layer=[]
  for shift in range(3):
   line=L[base+shift-1]
   if not (line.startswith("│") and line.endswith("│")):
    raise ValueError(("Missing original box cell row",base+shift))
   values=[v.strip() for v in line.split("│")[1:-1]]
   if len(values)!=3:raise ValueError(("Not three original palace columns",base+shift))
   layer.append(values)
  if r<2 and not L[base+2].startswith("├"):
   raise ValueError("Original horizontal chart divider missing")
  for col in range(3):
   idx=r*3+col;p=PAL[idx];label=LABEL[idx]
   header,door,star=[layer[z][col] for z in range(3)]
   if not header.startswith(label):raise ValueError(("Printed palace label mismatch",label,header))
   if p==5:
    if header!="中5" or not door or star:
     raise ValueError("Center contains a literal original stem only; no fake god, door or star")
   elif not header or not door or not star:
    raise ValueError(("Original outer-palace row unprinted",p))
   literal="\n".join((header,door,star))
   corrupted=int(p!=5 and any(s in literal for s in ("原OCR","缺损","缺字","未辨")))
   out.append({"palace":p,"label":label,"header":header,"door":door,"star":star,
    "start":base,"end":base+2,"source_line_unique":base+col,
    "literal":literal,"sha":h(literal.encode("utf8")),"ocr_incomplete":corrupted})
 if sorted(v["palace"] for v in out)!=list(range(1,10)):
  raise ValueError("Each of nine source palaces must appear exactly once")
 return out
def events(L):
 out=[]
 for i,s in enumerate(SPEC,1):
  if not L[s["start"]-1].startswith("（例"):raise ValueError("Lost original case heading")
  cells=panel(L,s["grid"])
  steps=[x for x in range(s["analyze"][0],s["analyze"][1]+1) if HEADING_RE.match(L[x-1])]
  if len(steps)!=[5,12,3,5][i-1]:raise ValueError(("Missing original A-D/numbered reasoning",i,steps))
  out.append({**s,"number":i,"steps":steps,"cells":cells,
    "chart_sha":h(src(L,s["grid"],s["grid"]+12).encode("utf8"))})
 if sum(len(x["steps"]) for x in out)!=25 or len(out)!=4:raise ValueError("Four events 25 source step heads")
 if sum(v["ocr_incomplete"] for e in out for v in e["cells"])<2:raise ValueError("Original OCR source gaps lost")
 return out
def preserved_old_rows(old,con):
 for (name,) in old.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"):
  cols=[c[1] for c in old.execute('PRAGMA table_info("'+name+'")')]
  selector=",".join('"'+c+'"' for c in cols)
  former=list(old.execute('SELECT '+selector+' FROM "'+name+'"'))
  current=set(con.execute('SELECT '+selector+' FROM "'+name+'"'))
  if not all(row in current for row in former):
   raise ValueError("Old complete historical source row changed: "+name)
def add_phase(con,L,e,key,kind,a,b=None,info=None):
 b=a if b is None else b;literal=src(L,a,b)
 details={"original_book_case_user_accepted":True,"outside_verified":False,
  "later_knowledge_not_prior_prediction":True,**(info or {})}
 con.execute("""INSERT INTO kaiwu_lost_chronological_phases(chapter_key,case_id,phase_key,
  phase_kind,source_start_line,source_end_line,source_literal,excerpt_sha256,
  temporal_guard_json) VALUES (?,?,?,?,?,?,?,?,?)""",
  (CHAPTER,e["case_id"],key,kind,a,b,literal,h(literal.encode("utf8")),j(details)))
def add_case(con,L,e,sid):
 cid=e["case_id"];i=e["number"]
 known=src(L,e["question"])
 judgment=src(L,e["first"])
 feedback=src(L,e["feedback"])
 # The later, retrospectively explained Qimen forecast is NOT the same as
 # the contemporary 8/20 six-yao answer or a fresh independent historic case.
 if i==4:judgment=src(L,139)+"\n"+src(L,175,178)
 reasoning="\n\n".join(src(L,a,b) for a,b in e["reasoning_spans"])
 context={"source_book":"kaiwu","source_sha256":SOURCE_SHA,
   "case_num":i,"source_event_span":[e["start"],e["end"]],
   "historical_report_user_accepted_no_case_review":True,
   "independent_validation_claimed":False,
   "thief_reported":e["theft"],
   "case_4_aug20_original_was_six_yao_not_qimen":i==4,
   "case_4_later_qimen_day_explanation_cannot_be_aug20_prediction":i==4,
   "source_OCR_uncertain_not_filled":any(x["ocr_incomplete"] for x in e["cells"]),
   "report_scope":e["notes"]}
 con.execute("""INSERT INTO cases(case_id,section_id,event_family_id,domain_id,
 known_before,author_yongshen_steps,author_judgment,later_feedback,reviewed)
 VALUES (?,?,?,'lost_property',?,?,?,?,1)""",
 (cid,sid,cid,known,reasoning,judgment,feedback))
 con.execute("""INSERT INTO historical_case_protocol(case_id,completeness,
  published_chart_verification,feedback_independently_verified,eligible_blind_test,
  case_source_sha256,metadata_json)
 VALUES (?,'one_literal_full_source_chart_and_book_event',
  'source_original_no_inferred_uncertain_OCR',0,0,?,?)""",
 (cid,SOURCE_SHA,j(context)))
 con.execute("""INSERT INTO historic_book_case_acceptance(case_id,source_book,
  source_chapter_key,source_documented_outcome,metadata_json)
 VALUES (?,'kaiwu',?,'historical_book_reports_and_chronological_differences',?)""",
 (cid,CHAPTER,j(context)))
 for domain in ["lost_property"]+e["facets"]:
  con.execute("""INSERT INTO unified_case_domain_facets(case_id,domain_id,
  source_chapter_key,primary_domain,note) VALUES (?,?,?,?,?)""",
  (cid,domain,CHAPTER,int(domain=="lost_property"),e["notes"]))
 con.execute("""INSERT INTO kaiwu_lost_source_charts(chapter_key,case_id,cast_key,
 original_caption_line,source_board_start,source_board_end,raw_chart_sha256,
 original_cast_calendar_line,original_cast_calendar_text)
 VALUES (?,?,'primary',?,?,?,?,?,?)""",
 (CHAPTER,cid,e["caption"],e["grid"],e["grid"]+12,e["chart_sha"],
  e["calendar"],src(L,e["calendar"])))
 add_phase(con,L,e,"question_known_before","information_initially_available",e["question"])
 add_phase(con,L,e,"original_book_grid","original_OCR_rearranged_nine_palace",e["grid"],e["grid"]+12)
 add_phase(con,L,e,"initial_book_judgment","book_original_prediction_attributed",e["first"],
           info={"initial_method":"six_yao_not_qimen" if i==4 else "qimen"})
 add_phase(con,L,e,"reported_book_feedback","later_report_not_preexisting",e["feedback"])
 add_phase(con,L,e,"all_original_analysis","original_source_numbered_analysis",*e["analyze"])
 if i==4:
  add_phase(con,L,e,"pre_qimen_aug20_sixyao","initial_six_yao_not_qimen",139)
  add_phase(con,L,e,"aug26_purchase_learning","later_method_acquisition",141)
  add_phase(con,L,e,"2000_letter_narrative","retrospective_letter_written_2000",127,149)
  add_phase(con,L,e,"claimed_exact_day_reading","later_Qimen_explanation_pre_result_timing_not_independently_dated",175,178)
  for key,a,b,why in (
    ("six_yao_versus_qimen",139,141,"Aug20 judgement was six-yao; actual Qimen learning began after Aug26; cannot reassign Qimen details to original Aug20"),
    ("exact_sep17_date_source_uncertain",175,180,"Exact date appears in explanation reported after outcome; source does not independently timestamp precise Qimen forecast before recovery"),
    ("travel_train_unprinted",143,147,"Additional outgoing and return train casts are mentioned but no Qimen source nine-palace diagram is printed: never fabricate extra complete historical case cast")):
   con.execute("""INSERT INTO kaiwu_lost_temporal_caveats(chapter_key,case_id,
   caveat_key,original_source_start,original_source_end,original_quote,
   interpretation_not_in_original_earlier_prediction) VALUES (?,?,?,?,?,?,?)""",
   (CHAPTER,cid,key,a,b,src(L,a,b),why))
 if i==1:
  con.execute("""INSERT INTO kaiwu_lost_temporal_caveats(chapter_key,case_id,
   caveat_key,original_source_start,original_source_end,original_quote,
   interpretation_not_in_original_earlier_prediction)
   VALUES (?,?, 'cash_missing_not_verified_theft',11,11,?,?)""",
   (CHAPTER,cid,src(L,11),"Recovered bag minus 4300 yuan; collector denies ever receiving cash. Do not label identified person as proved thief"))
 for v in e["cells"]:
  mid=v["palace"]==5
  deity="" if mid else v["header"][len(v["label"]):].strip()
  con.execute("""INSERT INTO kaiwu_lost_source_palaces(chapter_key,case_id,cast_key,
  palace,source_start_line,source_end_line,original_label,original_header,
  original_door,original_star,literal_text,literal_sha256,ocr_incomplete)
 VALUES (?,?,'primary',?,?,?,?,?,?,?,?,?,?)""",
  (CHAPTER,cid,v["palace"],v["start"],v["end"],v["label"],v["header"],
   v["door"],v["star"],v["literal"],v["sha"],v["ocr_incomplete"]))
  con.execute("""INSERT INTO historical_chart_cells(case_id,palace,source_line,
  palace_label_raw,deity_raw,door_position_raw,star_position_raw,source_status)
  VALUES (?,?,?,?,?,?,?,'verbatim_original_OCR_not_patched')""",
  (cid,v["palace"],v["source_line_unique"],v["label"],deity,v["door"],v["star"]))
  con.execute("""INSERT INTO historical_palace_standardization(case_id,cast_key,
  palace,center_stem,source_of_center_stem,standard_deity,standard_door,standard_star,
  normalized_status,original_raw_integrity_checked,method_reference,
  derived_host_palace,derived_host_source)
  VALUES (?,'primary',?,?,?,?,?,?,?,1,?,?,?)""",
  (cid,v["palace"],v["door"] if mid else None,
   "source_literal_only_center_stem_no_regular_god_door_star" if mid else "not_center",
   None if mid or v["ocr_incomplete"] else deity,
   None if mid or v["ocr_incomplete"] else v["door"],
   None if mid or v["ocr_incomplete"] else v["star"],
   "center_from_source_only" if mid else "OCR_missing_not_reconstructed" if v["ocr_incomplete"]
   else "original_source_verbatim_not_altered",
   "kaiwu_ch02_s08_original_OCR_rearranged_source",2 if mid else None,
   "center_host_derived_not_printed" if mid else None))
 for index,((a,b),n) in enumerate(zip(e["reasoning_spans"],e["steps"]),1):
  literal=src(L,a,b)
  info={"source_lines":[a,b],"book_historical_case_accepted":True,
   "later_hindsight_not_first_initial_guess":i==4,
   "positive_training_eligible":False,"source_reasoning_not_externally_proven":True}
  con.execute("""INSERT INTO historical_case_reasoning(case_id,step_number,source_line,
  author_analysis_original,short_method_topic,metadata_json)
  VALUES (?,?,?,?,?,?)""",
  (cid,index,n,literal,"source_author_reasoning_chronology_guarded",j(info)))
  con.execute("""INSERT INTO historical_case_reasoning_trace(case_id,step_number,
  source_line,evidence_json,review_status,positive_training_eligible)
  VALUES (?,?,?,?,'user_accepts_source_no_manual_approval',0)""",
  (cid,index,n,j(info)))
  concept=f"lost_property:kaiwu:case{i:02}:source_step{index:02}"
  con.execute("""INSERT INTO semantic_assertions(chapter_key,concept_id,kind,relation,
  source_start_line,source_end_line,metadata_json,original_excerpt,review_status)
  VALUES (?,?,?,?,?,?,?,?,'draft')""",
  (CHAPTER,concept,"source_author_case_reasoning","additional_exposition",a,b,j(info),literal))
  con.execute("""INSERT INTO cross_book_concept_tracks(chapter_key,concept_id,
  source_start_line,source_end_line,source_section_id,source_sha256,
  excerpt_sha256,track_id,relation_to_prior,comparison_state,normalized_json,review_status)
  VALUES (?,?,?,?,?,?,?,?,?,'book_original_source_without_scientific_validation',?,'draft')""",
  (CHAPTER,concept,a,b,sid,SOURCE_SHA,h(literal.encode("utf8")),
   "kaiwu:lost_property:case_source_step_v1","additional_exposition",j(info)))
 con.execute("""INSERT INTO historical_case_review_audit(case_id,original_steps,
  mechanical_step_trace,human_complete_step_chains,review_status,warning)
  VALUES (?,?,?,0,'user_original_book_case_accepted_no_manual_approval',?)""",
  (cid,len(e["steps"]),len(e["steps"]),e["notes"]))
 con.execute("""INSERT INTO historical_case_book_verdicts(event_family_id,primary_case_id,
  verdict,explicit_source_correction,source_correction_lines_json,
  feedback_source_lines_json,independent_external_verification,app_output_protocol,
  evidence_review_status,note)
  VALUES (?,?,'author_book_success_default',0,'[]',?,'not_verified',
  'single_answer_for_one_cast','source_report_acceptance_not_external_verification',?)""",
  (cid,cid,j([e["feedback"]]),e["notes"]))
 con.execute("""INSERT INTO kaiwu_lost_issue_outcomes(chapter_key,case_id,
  issue_key,prediction_source_line,prediction_original,
  feedback_source_line,feedback_original,reported_result_scope,is_criminal_theft)
  VALUES (?,?,?,?,?,?,?,?,?)""",
  (CHAPTER,cid,e["issue"],e["first"],src(L,e["first"]),
   e["feedback"],src(L,e["feedback"]),e["notes"],int(e["theft"])))
def build(base,source,output,index_dir):
 base,source,output,index_dir=map(Path,(base,source,output,index_dir))
 if output.exists():raise ValueError("Never overwrite an older entire historical SQLite archive")
 if h(base.read_bytes())!=BASE_SHA:raise ValueError("Must begin from precise 149-event FULL parent SQLite SHA")
 raw=source.read_bytes();L=prepare(raw);found=events(L)
 for e in found:
  if e["number"]==1:ends=[33,36,39,42,44]
  elif e["number"]==2:ends=[72,73,74,76,77,78,80,83,84,85,86,87]
  elif e["number"]==3:ends=[112,113,114]
  else:ends=[171,172,173,174,178]
  e["reasoning_spans"]=list(zip(e["steps"],ends))
  if any(a>b for a,b in e["reasoning_spans"]):raise ValueError("Original analysis unit boundary incorrect")
 output.parent.mkdir(parents=True,exist_ok=True)
 with sqlite3.connect("file:"+str(base)+"?mode=ro",uri=True) as old,sqlite3.connect(output) as db:
  old.backup(db)
  db.executescript((ROOT/"schema/migrations/028_kaiwu_lost_property_crossbook_four_cases.sql").read_text("utf8"))
  db.execute("PRAGMA foreign_keys=ON")
  with db:
   if db.execute("SELECT count(*) FROM sections WHERE book_id='kaiwu'").fetchone()[0]!=12:
    raise ValueError("All prior 12 Kaiwu sections must exist")
   db.execute("""INSERT INTO sections(book_id,section_key,title,original_text,
     sha256,content_version,reviewed) VALUES ('kaiwu',?,?,?,?,1,1)""",
     (SECTION,TITLE,raw.decode("utf8"),SOURCE_SHA))
   sid=db.execute("SELECT last_insert_rowid()").fetchone()[0]
   db.execute("""INSERT INTO chapter_knowledge(chapter_key,book_id,title,
     source_sha256,source_length_bytes,knowledge_version,review_status)
     VALUES (?,'kaiwu',?,?,?,'1','approved')""",
     (CHAPTER,TITLE,SOURCE_SHA,len(raw)))
   for e in found:add_case(db,L,e,sid)
   db.execute("""INSERT INTO cross_book_example_references(source_chapter_key,
     source_line,target_book_id,target_printed_page,reference_key,
     metadata_json,verified_target_case_id)
     VALUES (?,141,'shenqi','not_specified_in_source',?,?,NULL)""",
     (CHAPTER,"kaiwu:lost:buyer_found_shenqi_on_aug_26",
      j({"source_quote":src(L,141),"book_reference_only":True,
         "same_historical_event_as_prior_book_case":False,
         "not_a_second_complete_Qimen_chart":True})))
   db.execute("""INSERT INTO chapter_archival_versions(archive_label,
    baseline_sha256,new_db_sha256,contains_complete_private_copyright_source,
    snapshot_type,created_utc,repo_public_archive_policy)
    VALUES (?,?,NULL,1,'kaiwu_ch02_s08_four_lost_property_cases_four_printed_original_charts',
    '2026-10-20','user_authorized_public_full_sqlite_versions')""",
    ("shenqi21_kaiwu13_lost_property_153cases",BASE_SHA))
  preserved_old_rows(old,db)
  if db.execute("PRAGMA integrity_check").fetchone()[0]!="ok" or db.execute("PRAGMA foreign_key_check").fetchall():
   raise ValueError("Historical database integrity/foreign keys failed")
  expected={"sections":34,"cases":153,"historical_chart_cells":1368,
   "historical_palace_standardization":1530,
   "historical_case_additional_casts":18,
   "historical_case_additional_cast_cells":162,
   "historical_case_reasoning":779,"historical_case_reasoning_trace":779,
   "semantic_assertions":2453,"cross_book_concept_tracks":1196,
   "cross_book_example_references":48,"historic_book_case_acceptance":45,
   "unified_case_domain_facets":57,
   "kaiwu_lost_source_charts":4,"kaiwu_lost_source_palaces":36,
   "kaiwu_lost_issue_outcomes":4,"kaiwu_lost_temporal_caveats":4}
  counts={k:db.execute('SELECT count(*) FROM "'+k+'"').fetchone()[0] for k in expected}
  if counts!=expected:raise ValueError(("Parent/new record count mismatch",counts,expected))
  if db.execute("SELECT count(*) FROM cases WHERE domain_id='lost_property'").fetchone()[0]!=12:
   raise ValueError("Must join existing 8 Shenqi lost cases with 4 new Kaiwu cases")
  if db.execute("SELECT count(*) FROM historical_case_book_verdicts WHERE verdict='author_book_error_explicit'").fetchone()[0]!=9:
   raise ValueError("All nine earlier explicit first-answer failures must remain")
  if db.execute("SELECT count(*) FROM kaiwu_lost_source_palaces WHERE ocr_incomplete=1").fetchone()[0]<2:
   raise ValueError("Source damaged original must not be normalized")
  if db.execute("SELECT count(*) FROM kaiwu_lost_issue_outcomes WHERE is_criminal_theft=1").fetchone()[0]!=2:
   raise ValueError("Distinguish two thefts from the other two lost/mislaid events")
  db.execute("VACUUM");db.commit()
  if db.execute("PRAGMA integrity_check").fetchone()[0]!="ok" or db.execute("PRAGMA foreign_key_check").fetchall():
   raise ValueError("Final full SQLite integrity check failure")
 index_dir.mkdir(parents=True,exist_ok=True)
 report={"schema":"kaiwu_lost_four_crossbook_unified_original_v1",
  "source_title":TITLE,"source_sha256":SOURCE_SHA,
  "source_bytes":len(raw),"source_lines":len(L),
  "new_original_cases":4,"new_source_printed_nine_palace_charts":4,
  "new_raw_palace_cells":36,"new_full_source_analysis_units":25,
  "new_criminal_theft_cases":2,"new_not_proven_theft_lost_or_mislaid_cases":2,
  "fourth_first_consultation_method_sixyao_not_qimen":True,
  "fourth_qimen_studied_after_first_loss":True,
  "fourth_precise_calendar_reading_dated_only_in_later_account":True,
  "fourth_other_train_divinations_unprinted_not_extra_cases":True,
  "original_unreadable_source_labels_unrepaired":True,
  "all_cases_user_accepted_no_manual_case_review":True,
  "no_independent_forensic_or_scientific_verification_claimed":True,
  "total_source_sections":34,"book_counts":{"shenqi":21,"kaiwu":13},
  "total_distinct_historical_events":153,
  "total_actual_source_original_charts":170,
  "prior_explicit_case_level_first_answer_errors_retained":9,
  "source_immutable_parent_sha256":BASE_SHA,
  "actual_new_db_sha256":h(output.read_bytes()),
  "all_previous_rows_verbatim_unchanged":True,"counts":counts}
 def write(name,data):
  (index_dir/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 write("chapter_manifest.json",report)
 write("case_index.json",{"source_sha256":SOURCE_SHA,
  "cases":[{k:v for k,v in e.items() if k!="cells"} for e in found]})
 write("original_nine_palace_witnesses.json",{"source_sha256":SOURCE_SHA,
  "charts":[{"case_id":e["case_id"],"start":e["grid"],"original_palaces":e["cells"]} for e in found]})
 write("chronology_audit.json",{"source_sha256":SOURCE_SHA,
  "case01_lost_cash_no_collector_theft_as_proven_fact":True,
  "case02_stolen_motorbike_police_report_and_court":True,
  "case03_earring_mislaid_home_no_criminal_theft":True,
  "case04_initial_aug20_sixyao_not_qimen":True,
  "case04_Qimen_learned_after_aug26_book_purchase":True,
  "case04_precise_sep17_in_retrospective_text_unverified_as_original_aug20_prediction":True,
  "case04_train_travel_book_mentions_without_original_nine_palace_panels":True,
  "all_four_source_original_panels_untouched_and_old_rows_identical":True})
 return report
def main():
 ap=argparse.ArgumentParser()
 for name in ("base","source","output","index-dir"):
  ap.add_argument("--"+name,required=True)
 a=ap.parse_args()
 print(json.dumps(build(a.base,a.source,a.output,a.index_dir),ensure_ascii=False,indent=2))
if __name__=="__main__":main()
