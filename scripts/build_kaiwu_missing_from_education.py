"""Kaiwu missing persons: five historical inquiries, six genuinely printed source charts.

One woman has TWO historical casts, one event. Two abducted waitresses are
two subjects in ONE inquiry. OCR damage is copied verbatim and never guessed.
Merge with existing Shenqi missing_person cases; all old SQLite rows immutable.
Book-reported narratives accepted by user without case-by-case approval, not
independent modern missing-person safety assessments.
"""
from __future__ import annotations
import argparse,hashlib,json,re,sqlite3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE_SHA="320347f0c25ccd050171b391611d7188f8e822d99f3d1dbd67d98688b03431dc"
SOURCE_SHA="193e1eb8438a83e1408efa804daf66ea43e64f36155e221be23c9de53215ab71"
BASE_NAME="WenguaApp_神奇之门21章_开悟之门10节_133案例_完整研究库.sqlite3"
NEW_NAME="WenguaApp_神奇之门21章_开悟之门11节_138案例_完整研究库.sqlite3"
CHAPTER="kaiwu/missing_person_prediction_ch02_section07/v1"
SECTION="missing_person_prediction_ch02_section07"
TITLE="第七节 行人走失预测（共5例）"
PALACES=(4,9,2,3,5,7,8,1,6)
LABELS=("巽4宫","离9宫","坤2宫","震3宫","中5宫","兑7宫","艮8宫","坎1宫","乾6宫")
EVENTS=[
 {"key":"niece_1998","id":"kaiwu.missing.19980409.zhao_niece","title":"1998赵经理外甥女失踪",
  "bounds":(3,60),"question":(4,6),
  "charts":[(9,6,"1998-04-09","壬辰","inquiry_time"),
            (36,33,"1998-02-28","戊戌","known_disappearance_time")],
  "steps":[27,28,29,30,54,55,56,57,58],"pred":[30,58],
  "feedback":[59],"editor":[],"facets":["missing_person","relationship"],
  "notes":"One woman, two source chart times; disappearance Feb28, found May5 after 66 days; first query-time cast and second disappearance-time cast are not independent event successes"},
 {"key":"student_1998","id":"kaiwu.missing.19980802.zhao_student","title":"1998江苏大学生离家出走",
  "bounds":(61,95),"question":(62,64),
  "charts":[(67,64,"1998-07-02","辛巳","known_disappearance_time")],
  "steps":[85,86,87,88],"pred":[90],"feedback":[91],"editor":[93,94],
  "facets":["missing_person","education"],
  "notes":"Predicted Aug16 return and within 20 days; actual Aug17, one-day timing miss, author corrects rigid year/month/day/hour rule after outcome"},
 {"key":"waitresses_1998","id":"kaiwu.missing.19980826.two_waitresses","title":"1998湖南两名女服务员被带走",
  "bounds":(96,128),"question":(97,98),
  "charts":[(101,98,"1998-08-26","甲申","disappearance_time")],
  "steps":[119,120,121,122,123],"pred":[119,121,122,123],
  "feedback":[124,125],"editor":[127],
  "facets":["missing_person","criminal_case"],
  "notes":"One hotel request, two missing waitresses; Aug31 contact/location learned, Sep10 both physically located; editor modified student's original narration in book"},
 {"key":"taxi_male_1999","id":"kaiwu.missing.19990309.hao_male_taxi","title":"1999郝星立测男性出租车司机遇害",
  "bounds":(129,167),"question":(130,135),
  "charts":[(138,135,"1999-03-09","乙酉","inquiry_time")],
  "steps":[156,157,158,159,160,161],"pred":[131,132,160,161],
  "feedback":[133,162],"editor":[164,165,166],
  "facets":["missing_person","criminal_case"],
  "notes":"Male taxi driver 1979, reported homicide and hijacked car; NOT older Shenqi case10 female driver Ma Lande; note older book reference only"},
 {"key":"college_girl_2000","id":"kaiwu.missing.20000811.zhou_female_student","title":"2000周平测女大学生失踪",
  "bounds":(168,200),"question":(169,171),
  "charts":[(174,171,"2000-08-07","己酉","departure_time")],
  "steps":[193,194,195,196,197],"pred":[193,194,195,196,197],
  "feedback":[198],"editor":[200],
  "facets":["missing_person","criminal_case"],
  "notes":"Original chart has extra damaged OCR row under first band; preserve source extra row; report states safe Aug15 return, not externally verified"}
]
def sha(x):return hashlib.sha256(x).hexdigest()
def js(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":"))
def span(L,a,b=None):
 b=a if b is None else b
 if not 1<=a<=b<=len(L):raise ValueError(("Out-of-range source line",a,b))
 return "\n".join(L[a-1:b])
def validate_source(b):
 if sha(b)!=SOURCE_SHA:raise ValueError("Exact original SHA256 wrong")
 L=b.decode("utf-8").splitlines()
 if len(L)!=200 or not b.endswith(b"\n") or L[0]!=TITLE or not L[-1].endswith("肯定会有效果的。"):
  raise ValueError("Full original was truncated")
 markers=[i for i,x in enumerate(L,1) if re.match(r"^（例[一二三四五]）",x)]
 if markers!=[3,61,96,129,168]:raise ValueError(("Original five distinct case boundaries",markers))
 starts=[i for i,x in enumerate(L,1) if x.startswith("奇门九宫格（起局盘第")]
 if starts!=[8,35,66,100,137,173]:raise ValueError(("Six original board captions",starts))
 for n in (17,39,40,79,141,142,177,179):
  if not any(s in L[n-1] for s in ("原OCR","未辨","缺损")):
   raise ValueError(("Book OCR-damage marker missing",n,L[n-1]))
 return L
def parse_board(L,start):
 if not L[start-1].startswith("+"):raise ValueError(("Missing original ASCII board",start))
 groups=[];part=[]
 for ix in range(start-1,len(L)):
  value=L[ix]
  if value.startswith("+"):
   if part:
    groups.append((ix-len(part)+1,part))
    part=[]
   if len(groups)==3:break
  elif value.startswith("|"):
   parts=[v.strip() for v in value.split("|")[1:-1]]
   if len(parts)!=3:raise ValueError(("Original three-column source changed",ix+1))
   part.append(parts)
  else:raise ValueError(("Original ASCII grid incomplete",ix+1))
 if len(groups)!=3 or any(len(rows) not in (4,5) for _,rows in groups):
  raise ValueError(("Three original bands with at least four rows",start,[(a,len(b)) for a,b in groups]))
 cells=[]
 for row,(first,lines) in enumerate(groups):
  for col in range(3):
   palace=PALACES[row*3+col]
   header,spirit,door,star=[z[col] for z in lines[:4]]
   if header!=LABELS[row*3+col]:raise ValueError(("Palace header must stay literal",start,header))
   extra=lines[4][col] if len(lines)==5 else ""
   if palace==5 and (spirit!="中五宫" or star or not door):
    raise ValueError("Source center five has no fabricated eight-god/gate/star triple")
   if palace!=5 and (not spirit or not door or not star):
    raise ValueError("Missing source cell must be explicitly preserved, not filled")
   literal="\n".join([header,spirit,door,star]+([extra] if len(lines)==5 else []))
   damaged=int(any(x in literal for x in ("原OCR","未辨","缺损","残字")))
   cells.append({"palace":palace,"start":first,"end":first+len(lines)-1,
    "line":first+col,"header":header,"spirit":spirit,"door":door,"star":star,
    "extra":extra,"raw":literal,"sha":sha(literal.encode("utf-8")),"damaged":damaged})
 if sorted(p["palace"] for p in cells)!=list(range(1,10)):
  raise ValueError("Not all unique original palaces")
 return cells
def parse(L):
 out=[]
 for s in EVENTS:
  casts=[]
  for k,(start,calendar,date,hour,kind) in enumerate(s["charts"]):
   cells=parse_board(L,start)
   last=start+15+(1 if start==174 else 0)
   # Source last ASCII border is at start+15 for 4-row bands; 5-row first band
   # shifts last border down one line.
   if not L[last-1].startswith("+"):raise ValueError(("Last source border invalid",start,last))
   casts.append({"key":"primary" if k==0 else "additional_"+str(k),
    "start":start,"end":last,"calendar":calendar,"date":date,"hour":hour,
    "kind":kind,"cells":cells,"sha":sha(span(L,start,last).encode("utf-8"))})
  out.append({**s,"casts":casts})
 if sum(len(e["steps"]) for e in out)!=29 or sum(len(e["casts"]) for e in out)!=6:
  raise ValueError("Must have 29 numbered source steps and 6 genuine charts")
 if sum(c["damaged"] for e in out for ca in e["casts"] for c in ca["cells"])<4:
  raise ValueError("OCR missing/incomplete data must be preserved")
 if next(c for c in out[3]["casts"][0]["cells"] if c["palace"]==2)["door"]!="原OCR：乙／己／冲 丙":
  raise ValueError("Never normalize original missing taxi chart text")
 if next(c for c in out[4]["casts"][0]["cells"] if c["palace"]==2)["extra"]!="原OCR：庚 辛":
  raise ValueError("Original special fifth OCR row must remain")
 return out
def old_rows_untouched(old,db):
 for (table,) in old.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"):
  cols=[x[1] for x in old.execute('PRAGMA table_info("'+table+'")')]
  names=",".join('"'+v+'"' for v in cols)
  oldrows=list(old.execute('SELECT '+names+' FROM "'+table+'"'))
  newset=set(db.execute('SELECT '+names+' FROM "'+table+'"'))
  if not all(z in newset for z in oldrows):
   raise ValueError("Previous Shenqi/Kaiwu historical source altered: "+table)
def phase(db,L,e,key,kind,a,b=None,extra=None):
 b=a if b is None else b
 raw=span(L,a,b)
 meta={"source_case_accepted_without_individual_approval":True,
  "reported_story_not_independent_police_confirmation":True,
  "later_book_feedback_excluded_from_initial_prediction":True,**(extra or {})}
 db.execute("""INSERT INTO missing_crossbook_phases(chapter_key,case_id,phase_key,phase_type,
  first_line,last_line,original,source_sha256,chronology_json)
 VALUES (?,?,?,?,?,?,?,?,?)""",
 (CHAPTER,e["id"],key,kind,a,b,raw,sha(raw.encode("utf-8")),js(meta)))
def insert_event(db,sid,L,e):
 cid=e["id"];known=span(L,*e["question"])
 author="\n\n".join(span(L,z) for z in e["steps"])
 predicted="\n".join(span(L,z) for z in e["pred"])
 feedback="\n".join(span(L,z) for z in e["feedback"])
 db.execute("""INSERT INTO cases(case_id,section_id,event_family_id,domain_id,
 known_before,author_yongshen_steps,author_judgment,later_feedback,reviewed)
 VALUES (?,?,?,'missing_person',?,?,?,?,1)""",
 (cid,sid,cid,known,author,predicted,feedback))
 meta={"source_book":"kaiwu","case_key":e["key"],"case_lines":e["bounds"],
  "reported_results_user_accepted":True,"no_individual_approval":True,
  "multiple_real_casts_one_event":len(e["casts"])>1,
  "original_printed_charts":len(e["casts"]),
  "book_reported_story_not_external_verification":True,"note":e["notes"]}
 db.execute("""INSERT INTO historical_case_protocol(case_id,completeness,
 published_chart_verification,feedback_independently_verified,eligible_blind_test,
 case_source_sha256,metadata_json)
 VALUES (?,'original_printed_source_with_reported_feedback',
 'book_source_not_independently_recast',0,1,?,?)""",
 (cid,SOURCE_SHA,js(meta)))
 db.execute("""INSERT INTO historic_book_case_acceptance(case_id,source_book,source_chapter_key,
 source_documented_outcome,metadata_json)
 VALUES (?,'kaiwu',?,'source_book_report_accepted_without_individual_user_review',?)""",
 (cid,CHAPTER,js(meta)))
 for facet in e["facets"]:
  db.execute("""INSERT INTO unified_case_domain_facets(case_id,domain_id,
 source_chapter_key,primary_domain,note) VALUES (?,?,?,?,?)""",
 (cid,facet,CHAPTER,int(facet=="missing_person"),e["notes"]))
 phase(db,L,e,"initial_question","before_prediction",*e["question"])
 for z,n in enumerate(e["pred"],1):
  phase(db,L,e,f"original_judgment_{z}","original_book_initial_judgment",n)
 for z,n in enumerate(e["feedback"],1):
  phase(db,L,e,f"book_reported_feedback_{z}","book_reported_later_result",n)
 for z,n in enumerate(e["editor"],1):
  phase(db,L,e,f"editor_comment_{z}","after_feedback_editor_revision",n)
 for cast in e["casts"]:
  key=cast["key"];p=cast["start"]
  phase(db,L,e,"printed_chart_"+key,"original_printed_chart",p,cast["end"],
        {"cast_type":cast["kind"],"not_independent_new_case":key!="primary"})
  db.execute("""INSERT INTO missing_crossbook_casts(chapter_key,case_id,cast_key,
    grid_start,grid_end,source_sha256,calendar_line,original_calendar,context)
  VALUES (?,?,?,?,?,?,?,?,?)""",
  (CHAPTER,cid,key,p,cast["end"],cast["sha"],cast["calendar"],
   span(L,cast["calendar"]),cast["kind"]))
  if key!="primary":
   db.execute("""INSERT INTO historical_case_additional_casts(case_id,cast_key,
    cast_datetime_description,calendar_date,hour_ganzhi,source_chart_start,notes)
   VALUES (?,?,?,?,?,?,?)""",
   (cid,key,cast["date"]+" "+cast["hour"],cast["date"],cast["hour"],p,
    "Same lost niece, original disappearance-time historical chart, not new event"))
  for cell in cast["cells"]:
   pc=cell["palace"];middle=pc==5
   db.execute("""INSERT INTO missing_crossbook_palaces(chapter_key,case_id,cast_key,
   palace,source_line_start,source_line_end,header,spirit,door,star,
   extra_source_row,literal,source_sha256,ocr_deficient)
   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
   (CHAPTER,cid,key,pc,cell["start"],cell["end"],cell["header"],cell["spirit"],
    cell["door"],cell["star"],cell["extra"],cell["raw"],cell["sha"],cell["damaged"]))
   if key=="primary":
    db.execute("""INSERT INTO historical_chart_cells(case_id,palace,source_line,
    palace_label_raw,deity_raw,door_position_raw,star_position_raw,source_status)
    VALUES (?,?,?,?,?,?,?,'original_OCR_damage_preserved_no_recast')""",
    (cid,pc,cell["line"],cell["header"],cell["spirit"],cell["door"],cell["star"]))
   else:
    db.execute("""INSERT INTO historical_case_additional_cast_cells(case_id,cast_key,
    palace,source_line,palace_label_raw,deity_raw,door_position_raw,star_position_raw)
    VALUES (?,?,?,?,?,?,?,?)""",
    (cid,key,pc,cell["line"],cell["header"],cell["spirit"],cell["door"],cell["star"]))
   db.execute("""INSERT INTO historical_palace_standardization(case_id,cast_key,palace,
    center_stem,source_of_center_stem,standard_deity,standard_door,standard_star,
    normalized_status,original_raw_integrity_checked,method_reference,
    derived_host_palace,derived_host_source)
    VALUES (?,?,?,?,?,?,?,?,?,1,?,?,?)""",
    (cid,key,pc,cell["door"] if middle else None,
     "center_raw_OCR_token_no_deity_door_star" if middle else "not_center",
     None if middle or cell["damaged"] else cell["spirit"],
     None if middle or cell["damaged"] else cell["door"],
     None if middle or cell["damaged"] else cell["star"],
     "source_center_not_regular_triple" if middle else
     "OCR_deficient_no_standard_values_inferred" if cell["damaged"] else
     "literal_source_not_recast",
     "kaiwu_missing_people_OCR_provenance",
     2 if middle else None,
     "center_host_Kun_derivation_not_original_column" if middle else None))
 for ix,n in enumerate(e["steps"],1):
  raw=span(L,n)
  step={"case_id":cid,"source_line":n,"source_kind":"author_numbered_step",
    "book_story_accepted":True,"no_external_verification":True,
    "editor_later_correction_separate":bool(e["editor"])}
  db.execute("""INSERT INTO historical_case_reasoning(case_id,step_number,source_line,
    author_analysis_original,short_method_topic,metadata_json)
    VALUES (?,?,?,?,?,?)""",
   (cid,ix,n,raw,"book_source_analysis_not_empirical_validation",js(step)))
  db.execute("""INSERT INTO historical_case_reasoning_trace(case_id,step_number,
   source_line,evidence_json,review_status,positive_training_eligible)
  VALUES (?,?,?,?,'book_case_accepted_source_original',0)""",
   (cid,ix,n,js(step)))
  concept=f"missing:kaiwu:{e['key']}:step:{ix}"
  db.execute("""INSERT INTO semantic_assertions(chapter_key,concept_id,kind,relation,
    source_start_line,source_end_line,metadata_json,original_excerpt,review_status)
  VALUES (?,?,?,?,?,?,?,?,'draft')""",
  (CHAPTER,concept,"original_missing_person_step","additional_exposition",n,n,js(step),raw))
  db.execute("""INSERT INTO cross_book_concept_tracks(chapter_key,concept_id,
   source_start_line,source_end_line,source_section_id,source_sha256,excerpt_sha256,
   track_id,relation_to_prior,comparison_state,normalized_json,review_status)
  VALUES (?,?,?,?,?,?,?,?,?,'book_source_accepted_not_externally_verified',?,'draft')""",
  (CHAPTER,concept,n,n,sid,SOURCE_SHA,sha(raw.encode("utf-8")),
   "kaiwu:missing_person:source_step_v1","additional_exposition",js(step)))
 db.execute("""INSERT INTO historical_case_review_audit(case_id,original_steps,
    mechanical_step_trace,human_complete_step_chains,review_status,warning)
 VALUES (?,?,?,0,'original_book_case_accepted_no_manual_user_approval',?)""",
 (cid,len(e["steps"]),len(e["steps"]),e["notes"]))
 db.execute("""INSERT INTO historical_case_book_verdicts(event_family_id,primary_case_id,
  verdict,explicit_source_correction,source_correction_lines_json,
  feedback_source_lines_json,independent_external_verification,app_output_protocol,
  evidence_review_status,note)
 VALUES (?,?,'author_book_success_default',0,'[]',?,'not_verified',
  'single_answer_for_one_cast','book_claims_with_partial_timing_error_retained',?)""",
 (cid,cid,js(e["feedback"]),e["notes"]))
def build(base,source,output,index_dir):
 base,source,output,index_dir=map(Path,(base,source,output,index_dir))
 if output.exists():raise ValueError("No overwrite of prior immutable SQLite")
 if sha(base.read_bytes())!=BASE_SHA:raise ValueError("Not the latest complete 133-case SQLite SHA")
 raw=source.read_bytes();L=validate_source(raw);cases=parse(L)
 output.parent.mkdir(parents=True,exist_ok=True)
 with sqlite3.connect("file:"+str(base)+"?mode=ro",uri=True) as old,sqlite3.connect(output) as db:
  old.backup(db)
  db.executescript((ROOT/"schema/migrations/026_kaiwu_missing_crossbook_ocr_multicast.sql").read_text("utf8"))
  db.execute("PRAGMA foreign_keys=ON")
  with db:
   if db.execute("SELECT COUNT(*) FROM sections WHERE book_id='kaiwu'").fetchone()[0]!=10:
    raise ValueError("Must preserve all previous 10 Kaiwu sections")
   db.execute("""INSERT INTO sections(book_id,section_key,title,original_text,sha256,content_version,reviewed)
   VALUES ('kaiwu',?,?,?,?,1,1)""",(SECTION,TITLE,raw.decode("utf8"),SOURCE_SHA))
   sid=db.execute("SELECT last_insert_rowid()").fetchone()[0]
   db.execute("""INSERT INTO chapter_knowledge(chapter_key,book_id,title,source_sha256,
   source_length_bytes,knowledge_version,review_status) VALUES (?,'kaiwu',?,?,?,'1','approved')""",
   (CHAPTER,TITLE,SOURCE_SHA,len(raw)))
   for e in cases:insert_event(db,sid,L,e)
   for who in ("waitress_A","waitress_B"):
    e=cases[2];info={"two_subjects_one_event":True,"book_confirmed_phone_19980831":True,
       "both_located_19980910":True}
    db.execute("""INSERT INTO missing_crossbook_subjects(chapter_key,case_id,subject_key,
     source_relation,outcome_original,outcome_line,metadata_json) VALUES (?,?,?,?,?,?,?)""",
     (CHAPTER,e["id"],who,"same_hotel_two_missing_waitresses_one_original_board",
      span(L,124,125),125,js(info)))
   e=cases[1]
   db.execute("""INSERT INTO missing_crossbook_claim_checks(chapter_key,case_id,
     claim_key,predicted_date_original,feedback_date_original,source_prediction_line,
     source_feedback_line,status,original_qualified_context)
     VALUES (?,?,?,?,?,?,?,'one_day_timing_error',?)""",
     (CHAPTER,e["id"],"return_1998_august","8月16日","8月17日",88,91,span(L,88,94)))
   db.execute("""INSERT INTO cross_book_example_references(source_chapter_key,source_line,
      target_book_id,target_printed_page,reference_key,metadata_json,verified_target_case_id)
   VALUES (?,164,'shenqi','unspecified_in_source',?,?,?)""",
   (CHAPTER,"kaiwu:male_taxi_vs_shenqi_MaLande_female_taxi",
    js({"different_person":"male_driver_v_female_driver",
        "source_quote":span(L,164),"reference_only_not_same_event":True,
        "related_old_case_index_reference":"shenqi.missing.case10",
        "same_historical_event":False}),None))
   db.execute("""INSERT INTO chapter_archival_versions(archive_label,baseline_sha256,new_db_sha256,
     contains_complete_private_copyright_source,snapshot_type,created_utc,repo_public_archive_policy)
     VALUES (?,?,NULL,1,'shared_missing_five_events_six_source_panels_including_damaged_OCR',
       '2026-10-20','user_authorized_public_full_sqlite_versions')""",
     ("shenqi21_kaiwu_missing07_138cases",BASE_SHA))
  old_rows_untouched(old,db)
  if db.execute("PRAGMA integrity_check").fetchone()[0]!="ok" or db.execute("PRAGMA foreign_key_check").fetchall():
   raise ValueError("SQLite integrity failure after original-book ingestion")
  expected={"sections":32,"cases":138,
    "historical_chart_cells":1233,"historical_case_additional_casts":18,
    "historical_case_additional_cast_cells":162,
    "historical_palace_standardization":1395,
    "historical_case_reasoning":690,"historical_case_reasoning_trace":690,
    "semantic_assertions":2364,"cross_book_concept_tracks":1107,
    "cross_book_example_references":46,
    "historic_book_case_acceptance":30,"unified_case_domain_facets":28,
    "missing_crossbook_casts":6,"missing_crossbook_palaces":54,
    "missing_crossbook_subjects":2,"missing_crossbook_claim_checks":1}
  got={key:db.execute('SELECT COUNT(*) FROM "'+key+'"').fetchone()[0] for key in expected}
  if got!=expected:raise ValueError(("Wrong copy+new source counts",got,expected))
  if db.execute("SELECT COUNT(*) FROM cases WHERE domain_id='missing_person'").fetchone()[0]<15:
   raise ValueError("Old Shenqi 10 and Kaiwu 5 must share missing_person")
  if db.execute("SELECT COUNT(*) FROM historical_case_book_verdicts WHERE verdict='author_book_error_explicit'").fetchone()[0]!=8:
   raise ValueError("All eight old explicit source initial errors must be preserved")
  if db.execute("SELECT COUNT(*) FROM missing_crossbook_palaces WHERE ocr_deficient=1").fetchone()[0]<4:
   raise ValueError("Actual four-plus original OCR damaged palaces were lost")
  if db.execute("SELECT COUNT(*) FROM missing_crossbook_casts WHERE case_id='kaiwu.missing.19980409.zhao_niece'").fetchone()[0]!=2:
   raise ValueError("One niece must have exactly two genuinely source-printed boards")
  db.execute("VACUUM");db.commit()
  if db.execute("PRAGMA integrity_check").fetchone()[0]!="ok" or db.execute("PRAGMA foreign_key_check").fetchall():
   raise ValueError("VACUUM final SQLite integrity failure")
 index_dir.mkdir(parents=True,exist_ok=True)
 manifest={"schema":"wengua_kaiwu_missing_crossbook_ocr_6source_charts",
  "source_title":TITLE,"chapter_key":CHAPTER,"source_sha256":SOURCE_SHA,
  "source_bytes":len(raw),"source_lines":len(L),"source_numbered_cases":5,
  "new_unique_historical_events":5,"new_original_printed_charts":6,
  "new_literal_source_palaces":54,"new_source_author_steps":29,
  "two_women_one_hotel_inquiry":True,"first_case_two_genuine_casts_one_event":True,
  "one_day_return_timing_miss_source_reported":True,
  "all_OCR_damage_retained_verbatim":True,
  "male_taxi_and_old_female_taxi_only_crossbook_reference":True,
  "user_accepts_original_book_cases_without_case_by_case_approval":True,
  "reported_results_not_external_forensic_validation":True,
  "book_counts":{"shenqi":21,"kaiwu":11},"total_sections":32,
  "total_event_families":138,"total_original_historical_casts":155,
  "parent_sha256":BASE_SHA,"new_database_sha256":sha(output.read_bytes()),
  "all_old_table_rows_identical":True,"cumulative_counts":got}
 def write(name,obj):
  (index_dir/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 write("chapter_manifest.json",manifest)
 write("case_index.json",{"source_sha256":SOURCE_SHA,
  "cases":[{k:v for k,v in e.items() if k!="casts"}|
  {"casts":[{k:v for k,v in cast.items() if k!="cells"} for cast in e["casts"]]}
   for e in cases]})
 write("literal_charts.json",{"source_sha256":SOURCE_SHA,
  "charts":[{"case_id":e["id"],"cast_key":cast["key"],"original_grid_start":cast["start"],
    "cells":cast["cells"]} for e in cases for cast in e["casts"]]})
 write("source_audit.json",{"source_sha256":SOURCE_SHA,
  "new_original_source_charts":6,"new_distinct_cases":5,
  "first_case_second_chart_same_person":True,"hotel_two_subjects_one_case":True,
  "student_return_predicted_aug16_actual_aug17":True,
  "first_case_ocr_undeciphered_7th_palace_retained":True,
  "fifth_case_five_row_first_band_special_extra_OCR_retained":True,
  "old_Shenqi_female_taxi_case_is_distinct_history":True,
  "real_missing_person_cases_are_user_accepted_not_independent_validation":True})
 return manifest
def main():
 p=argparse.ArgumentParser()
 for name in ("base","source","output","index-dir"):p.add_argument("--"+name,required=True)
 a=p.parse_args()
 print(json.dumps(build(a.base,a.source,a.output,a.index_dir),ensure_ascii=False,indent=2))
if __name__=="__main__":main()
