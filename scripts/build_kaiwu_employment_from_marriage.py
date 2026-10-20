"""《开悟之门》第二章第四节：工作就业（3例、3原盘、1局双事项）。

Shared Shenqi employment domain, same event/source once even when two predicted
matters have two separately indexed outcomes. Original undeciphered stems and
unusual center palace are kept literally. Case3's post-accident exact-day
deduction is NEVER a 1997 advance exact-day prediction.
All full previous SQLite rows survive via sqlite3.backup.
"""
from __future__ import annotations
import argparse,hashlib,json,re,sqlite3
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE_SHA="64a01b16828dff326e1d0a2bd759147032fb8ef30869aa595be7aae04d492339"
SOURCE_SHA="eeaaa79d23528dfc608282f6ab0b120620a7c44d67588145a9166a9bd03c733e"
BASE_NAME="WenguaApp_神奇之门21章_开悟之门8节_127案例_完整研究库.sqlite3"
NEW_NAME="WenguaApp_神奇之门21章_开悟之门9节_130案例_完整研究库.sqlite3"
SECTION="employment_prediction_ch02_section04"
CHAPTER="kaiwu/employment_prediction_ch02_section04/v1"
TITLE="第四节 工作就业预测（共3例）"
PALACES=(4,9,2,3,5,7,8,1,6)
PALACE_LABELS=("巽4宫","离9宫","坤2宫","震3宫","中5宫","兑7宫","艮8宫","坎1宫","乾6宫")

SPECS=[
 dict(id="kaiwu.employment.19960514.publisher_wife_transfer",key="wife_transfer",
 title="出版社负责人问妻子跨社调动",source=(3,35),chart=9,header=7,question=[5,7],
 steps=[28,30,32],pred=[30,32],feedback=[34],editor=[],
 facets=["employment"],dun="阳",ju=5,datetime="1996-05-14 afternoon",hour="丙申",
 note="Uses 置闰法 explicitly; original 坎1 palace door/star report undeciphered stems, not inferred"),
 dict(id="kaiwu.employment.1998.supply_cooperative_director",key="director_appointment",
 title="县供销社新主任人选与宣布时间",source=(37,76),chart=43,header=41,question=[39,41],
 steps=[62,64,66],pred=[60,62,64,66],feedback=[68,70],editor=[74],
 facets=["employment","organizational_appointment"],dun="阳",ju=2,
 datetime="1998 lunar first month sixteenth 18:00",hour="乙酉",
 note="Director appointment winner and Feb25 癸卯 published date are from one cast; 值使杜门落5寄2, preserve center raw"),
 dict(id="kaiwu.employment.19971218.zhang_application_and_accident",key="application_accident",
 title="张伟国入党申请与1999年交通事故预警",source=(77,150),chart=101,header=99,question=[79],
 steps=[122,124,126,128,134,136,138],pred=[81],feedback=[87,97],
 editor=[144,146,148,150],facets=["employment","organizational_membership","transport_accident"],
 dun="阳",ju=1,datetime="1997-12-18 19:00",hour="甲戌",
 note="1997 predicted party application failure and possible 1999 lunar February crash; post-fatality exact day is NOT part of initial prediction; chart text prints 日甲午 but numbered analysis says 日干辛: retain discrepancy")
]
ISSUES=[
 ("wife_transfer","work_transfer", "employment",30,34,
  "Known both spouses work at one publishing house; initial says transfer will fail; report says remained there through autumn 1997"),
 ("director_appointment","director_appointment","organizational_appointment",60,68,
  "Reported director selection, direction and age and announcement on 癸卯 1998-02-25"),
 ("application_accident","party_membership_application","organizational_membership",81,87,
  "Party applicant's 1997 request for admission; next-day vote did not include his application"),
 ("application_accident","road_accident_1999_warning","transport_accident",81,97,
  "Original 1997 warning only 1999 lunar February and eastward Shijiazhuang crash; day 23 decided in 1999 AFTER partial death report (lines89-95)")
]
def dig(data):return hashlib.sha256(data).hexdigest()
def j(value):return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(",",":"))
def span(lines,a,b=None):
 b=a if b is None else b
 if not 1<=a<=b<=len(lines):raise ValueError(("Bad source line span",a,b))
 return "\n".join(lines[a-1:b])
def parse_source(raw):
 if dig(raw)!=SOURCE_SHA:raise ValueError("Unexpected source original bytes/SHA")
 L=raw.decode("utf-8").splitlines()
 if len(L)!=150 or L[0]!=TITLE or not raw.endswith(b"\n"):
  raise ValueError("Incomplete original work/employment chapter")
 if [i for i,x in enumerate(L,1) if x.startswith("（例") ]!=[3,37,77]:
  raise ValueError("Wrong count of book historical numbered case opens")
 if [i for i,x in enumerate(L,1) if x.startswith("┌") ]!=[9,43,101]:
  raise ValueError("Original three figures must be exactly 3")
 if L[149].find("二月二十三日辛卯")<0:
  raise ValueError("Author postscript must remain complete")
 if L[21].find("原文未辨干")<0 or L[22].find("原文未辨干")<0:
  raise ValueError("Printed undeciphered stems must remain explicitly unknown")
 if "明天" not in L[80] or "1999年阴历二月" not in L[80]:
  raise ValueError("Missing 1997 dated original prediction")
 if "前几天死了一个人" not in L[88] or "二月二十三日" not in L[90]:
  raise ValueError("Missing 1999 retrospective details timing")
 return L
def parse_grid(L,start):
 if not L[start-1].startswith("┌") or not L[start+15-1].startswith("└"):
  raise ValueError(("Sixteen-line original grid truncated",start))
 out=[]
 for band in range(3):
  base=start+1+band*5
  rows=[]
  for offset in range(4):
   line=L[base+offset-1]
   if not line.startswith("│") or not line.endswith("│"):
    raise ValueError(("Source grid field not pipe-delimited",start,base+offset))
   cells=[x.strip() for x in line.split("│")[1:-1]]
   if len(cells)!=3:raise ValueError(("Original 3 columns required",start,base+offset))
   rows.append(cells)
  if band<2 and not L[base+3].startswith("├"):
   raise ValueError(("Original palace separator incorrect",start,band))
  for col in range(3):
   n=band*3+col
   pal=PALACES[n];label=PALACE_LABELS[n]
   if rows[0][col]!=label:raise ValueError(("Literal palace ID changed",start,pal,rows[0][col]))
   god,door,star=rows[1][col],rows[2][col],rows[3][col]
   if pal==5 and (not god or door or star):
    raise ValueError("Middle palace prints only central original stem; do NOT invent deity, door or star")
   if pal!=5 and (not god or not door or not star):
    raise ValueError(("Incomplete noncenter historical source",start,pal))
   original="\n".join([label,god,door,star])
   out.append({"palace":pal,"source_line_unique":base+col,
    "original_start_line":base,"original_end_line":base+3,
    "original_palace_label":label,"original_spirit":god,"original_door":door,
    "original_star":star,"literal":original,"sha256":dig(original.encode("utf-8")),
    "undeciphered_stems":original.count("原文未辨干")})
 if sorted(c["palace"] for c in out)!=list(range(1,10)):raise ValueError("Nonunique source palace")
 return out
def parse_events(L):
 items=[]
 for ix,sp in enumerate(SPECS):
  if not L[sp["source"][0]-1].startswith("（例"):raise ValueError(("Example start mismatch",ix))
  if not L[sp["chart"]-1].startswith("┌"):raise ValueError("No original chart")
  cells=parse_grid(L,sp["chart"])
  if ix==0:
   kan=next(x for x in cells if x["palace"]==1)
   if kan["undeciphered_stems"]!=2:raise ValueError("Do not fill two undeciphered Kan stems")
  elif any(c["undeciphered_stems"] for c in cells):
   raise ValueError("Unexpected undeciphered printed stems")
  if ix==2:
   kun=next(x for x in cells if x["palace"]==2)
   if kun["original_star"]!="天禽、天芮 己":raise ValueError("Keep mixed original star literally")
  for line in sp["steps"]:
   if not re.match(r"^（[0-9]+）",L[line-1]):
    raise ValueError(("Original author enumerated step absent",ix,line))
  items.append({**sp,"cells":cells,"chart_end":sp["chart"]+15,
     "chart_sha256":dig(span(L,sp["chart"],sp["chart"]+15).encode("utf-8"))})
 if len(items)!=3 or sum(len(e["steps"]) for e in items)!=13:
  raise ValueError("Three one-chart book historical cases and 13 source reasoning steps required")
 return items
def ensure_old_rows(old,db):
 for (tab,) in old.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"):
  cols=[x[1] for x in old.execute('PRAGMA table_info("'+tab+'")')]
  sel=",".join('"'+q+'"' for q in cols)
  former=list(old.execute('SELECT '+sel+' FROM "'+tab+'"'))
  present=set(db.execute('SELECT '+sel+' FROM "'+tab+'"'))
  if not all(z in present for z in former):raise ValueError("Existing Shenqi/Kaiwu source overwritten: "+tab)
def add_phase(db,L,e,key,phase,a,b=None,extra=None):
 b=a if b is None else b
 original=span(L,a,b)
 details={"book_case_accepted_without_individual_user_review":True,
  "source_independently_verified_externally":False,
  "initial_information_boundary_respected":True,
  **(extra or {})}
 db.execute("""INSERT INTO crossbook_employment_source_phases
 (chapter_key,case_id,phase_key,phase_name,source_start_line,source_end_line,
 original_literal,excerpt_sha256,chronological_metadata_json)
 VALUES (?,?,?,?,?,?,?,?,?)""",(CHAPTER,e["id"],key,phase,a,b,original,
 dig(original.encode("utf-8")),j(details)))
def add_case(db,sid,L,e):
 cid=e["id"]
 question="\n".join(span(L,ln) for ln in e["question"])
 author="\n\n".join(span(L,ln) for ln in e["steps"])
 prediction="\n".join(span(L,ln) for ln in e["pred"])
 feedback="\n".join(span(L,ln) for ln in e["feedback"])
 db.execute("""INSERT INTO cases(case_id,section_id,event_family_id,domain_id,
  known_before,author_yongshen_steps,author_judgment,later_feedback,reviewed)
  VALUES (?,?,?,'employment',?,?,?,?,1)""",
  (cid,sid,cid,question,author,prediction,feedback))
 metadata={"cast_day":e["datetime"],"hour_ganzhi":e["hour"],"dun":e["dun"],"ju":e["ju"],
  "source_lines":e["source"],"source_grid":e["chart"],"source_note":e["note"],
  "new_historical_event":True,"user_accepts_book_case_without_manual_approval":True,
  "source_only_not_independent_historical_verification":True,
  "case3_same_cast_two_issues":e["key"]=="application_accident",
  "post_outcome_exact_date_not_advance_prediction":e["key"]=="application_accident"}
 db.execute("""INSERT INTO historical_case_protocol(case_id,completeness,
  published_chart_verification,feedback_independently_verified,eligible_blind_test,
  case_source_sha256,metadata_json)
  VALUES (?,'literal_complete_one_nine_palace_chart',
   'exact_user_supplied_source_not_independently_recast',0,1,?,?)""",
  (cid,SOURCE_SHA,j(metadata)))
 db.execute("""INSERT INTO historic_book_case_acceptance(case_id,source_book,
  source_chapter_key,source_documented_outcome,metadata_json)
  VALUES (?,'kaiwu',?,'book_reported_initial_prediction_and_later_outcome',?)""",
  (cid,CHAPTER,j(metadata)))
 for facet in e["facets"]:
  db.execute("""INSERT INTO unified_case_domain_facets(case_id,domain_id,
    source_chapter_key,primary_domain,note) VALUES (?,?,?,?,?)""",
    (cid,facet,CHAPTER,int(facet=="employment"),e["note"]))
 db.execute("""INSERT INTO crossbook_employment_source_charts(chapter_key,case_id,cast_key,
  original_grid_start,original_grid_end,original_grid_sha256,
  casting_description_line,original_casting_description)
  VALUES (?,?,'primary',?,?,?,?,?)""",
  (CHAPTER,cid,e["chart"],e["chart_end"],e["chart_sha256"],e["header"],span(L,e["header"])))
 add_phase(db,L,e,"question_and_cast_context","known_before_prediction",e["question"][0])
 add_phase(db,L,e,"printed_original_board","source_original_chart",e["chart"],e["chart_end"])
 for ix,line in enumerate(e["pred"],1):
  add_phase(db,L,e,f"initial_prediction_{ix}","book_first_prediction",line)
 for ix,line in enumerate(e["feedback"],1):
  add_phase(db,L,e,f"reported_result_{ix}","book_later_feedback",line)
 for ix,line in enumerate(e["editor"],1):
  add_phase(db,L,e,f"editor_comment_{ix}","post_feedback_editorial",line)
 if e["key"]=="application_accident":
  # These facts were not known on 1997-12-18, especially the day of fatality.
  add_phase(db,L,e,"fatality_report_1999","new_information_arrived_1999",89)
  add_phase(db,L,e,"retro_exact_day_deduction","post_new_information_day_deduction_1999",91,95,
    {"not_a_1997_exact_day_prediction":True,"warning_month_is_original":True})
  add_phase(db,L,e,"traffic_fatality_book_feedback","fatal_accident_reported",97)
  db.execute("""INSERT INTO crossbook_employment_source_caveats
    (chapter_key,case_id,caveat_key,source_line,original_quote,explanation)
    VALUES (?,?, 'day_only_after_death_news',91,?,?)""",
    (CHAPTER,cid,span(L,91),
     "Original 1997 prophecy specified month, not 23rd day; precise date inferred in 1999 after reporter already said someone had died"))
  db.execute("""INSERT INTO crossbook_employment_source_caveats
    (chapter_key,case_id,caveat_key,source_line,original_quote,explanation)
    VALUES (?,?, 'narrative_day_stem_mismatch',122,?,?)""",
    (CHAPTER,cid,span(L,122),
     "Original casting header 日甲午 (line99) versus reasoning 日干辛 (line122) differ; retain both, no invented correction"))
 if e["key"]=="wife_transfer":
  db.execute("""INSERT INTO crossbook_employment_source_caveats
    (chapter_key,case_id,caveat_key,source_line,original_quote,explanation)
    VALUES (? ,?,'undeciphered_kan_stems',22,?,?)""",
    (CHAPTER,cid,span(L,22,23),
     "The original Kan-1 door/star say 原文未辨干; do not calculate or backfill guessed stems"))
  db.execute("""INSERT INTO crossbook_employment_source_caveats
    (chapter_key,case_id,caveat_key,source_line,original_quote,explanation)
    VALUES (? ,?,'original_zhirun_casting_method',7,?,?)""",
    (CHAPTER,cid,span(L,7),
     "Author explicitly calls the 1996 阳5局 originally set by 置闰法; do not recast by 拆补"))
 for c in e["cells"]:
  center=c["palace"]==5
  db.execute("""INSERT INTO crossbook_employment_source_palaces(chapter_key,case_id,
   cast_key,palace,original_start_line,original_end_line,original_palace_label,
   original_spirit_text,original_door_text,original_star_text,source_literal_text,
   source_literal_sha256,undeciphered_source_stem_count)
   VALUES (?,?,'primary',?,?,?,?,?,?,?,?,?,?)""",
   (CHAPTER,cid,c["palace"],c["original_start_line"],c["original_end_line"],
    c["original_palace_label"],c["original_spirit"],c["original_door"],
    c["original_star"],c["literal"],c["sha256"],c["undeciphered_stems"]))
  db.execute("""INSERT INTO historical_chart_cells(case_id,palace,source_line,
    palace_label_raw,deity_raw,door_position_raw,star_position_raw,source_status)
    VALUES (?,?,?,?,?,?,?,'book_literal_four_row_original_not_recast')""",
    (cid,c["palace"],c["source_line_unique"],c["original_palace_label"],
     c["original_spirit"],c["original_door"],c["original_star"]))
  db.execute("""INSERT INTO historical_palace_standardization(case_id,cast_key,
    palace,center_stem,source_of_center_stem,standard_deity,standard_door,
    standard_star,normalized_status,original_raw_integrity_checked,method_reference,
    derived_host_palace,derived_host_source)
    VALUES (?,'primary',?,?,?,?,?,?,?,1,?,?,?)""",
    (cid,c["palace"],c["original_spirit"] if center else None,
     "source_center_column_single_stem_not_deity" if center else "not_center",
     None if center else c["original_spirit"],
     None if center else c["original_door"],
     None if center else c["original_star"],
     "center_original_untouched_blank_door_star" if center else
      "original_undeciphered_stems_no_guess" if c["undeciphered_stems"] else
      "book_verbatim_source_four_rows",
     "kaiwu_work_original_source_no_recast",
     2 if center else None,
     "five_center_host_to_kun_is_derived_not_source_print" if center else None))
 for index,line in enumerate(e["steps"],1):
  literal=span(L,line)
  category="source_original_party_application_analysis" if e["key"]=="application_accident" and line<132 else "source_original_accident_warning_analysis" if e["key"]=="application_accident" else "source_original_employment_analysis"
  meta={"source_line":line,"source_original":True,"aspect":category,
    "initial_day_fatality_not_predicted":e["key"]=="application_accident",
    "book_case_user_accepted":True,"later_outcome_excluded_from_original_prediction":True}
  db.execute("""INSERT INTO historical_case_reasoning(case_id,step_number,source_line,
   author_analysis_original,short_method_topic,metadata_json)
   VALUES (?,?,?,?,?,?)""",(cid,index,line,literal,category,j(meta)))
  db.execute("""INSERT INTO historical_case_reasoning_trace(case_id,step_number,
   source_line,evidence_json,review_status,positive_training_eligible)
   VALUES (?,?,?,?,'book_case_source_accepted_without_manual_review',0)""",
   (cid,index,line,j(meta)))
  concept=f"employment:kaiwu:{e['key']}:source_step:{index:02}"
  db.execute("""INSERT INTO semantic_assertions(chapter_key,concept_id,kind,relation,
    source_start_line,source_end_line,metadata_json,original_excerpt,review_status)
    VALUES (?,?,?,?,?,?,?,?,'draft')""",
    (CHAPTER,concept,"source_historical_author_reasoning",
     "separate_context" if e["key"]=="application_accident" and line>=134 else "additional_exposition",
     line,line,j(meta),literal))
  db.execute("""INSERT INTO cross_book_concept_tracks(chapter_key,concept_id,
    source_start_line,source_end_line,source_section_id,source_sha256,excerpt_sha256,
    track_id,relation_to_prior,comparison_state,normalized_json,review_status)
    VALUES (?,?,?,?,?,?,?,?,?,'book_case_accepted_source_provenance',?,'draft')""",
    (CHAPTER,concept,line,line,sid,SOURCE_SHA,dig(literal.encode("utf-8")),
     "kaiwu:employment:source_v1:author_steps",
     "separate_context" if e["key"]=="application_accident" and line>=134 else "additional_exposition",
     j(meta)))
 db.execute("""INSERT INTO historical_case_review_audit(case_id,original_steps,
   mechanical_step_trace,human_complete_step_chains,review_status,warning)
   VALUES (?,?,?,0,'user_book_case_accepted_no_individual_approval',?)""",
   (cid,len(e["steps"]),len(e["steps"]),e["note"]))
 db.execute("""INSERT INTO historical_case_book_verdicts(event_family_id,primary_case_id,
   verdict,explicit_source_correction,source_correction_lines_json,
   feedback_source_lines_json,independent_external_verification,app_output_protocol,
   evidence_review_status,note)
   VALUES (?,?,'author_book_success_default',0,'[]',?,'not_verified',
    'single_answer_for_one_cast','accepted_book_report_not_external_validation',?)""",
    (cid,cid,j(e["feedback"]),e["note"]))
def insert_issue(db,L,items,key,issue,facet,preline,outcome_line,note):
 e=next(x for x in items if x["key"]==key)
 if key=="application_accident":
  pre=span(L,79)
 else:
  pre=span(L,e["question"][0])
 original=span(L,preline);actual=span(L,outcome_line)
 info={"book_source_accepted_without_user_manual_review":True,
   "issue_and_event_are_distinct_identity_layers":True,
   "not_real_world_externally_validated":True,"source_chronology_caveat":note,
   "prediction_initial_source_line":preline,"feedback_source_line":outcome_line,
   "original_exact_crash_day_known_pre_accident":False if issue=="road_accident_1999_warning" else None}
 db.execute("""INSERT INTO crossbook_employment_case_issues(chapter_key,case_id,issue_key,
   domain_facet,known_before_original,original_prediction,book_reported_outcome,
   original_prediction_source_line,outcome_source_line,metadata_json)
   VALUES (?,?,?,?,?,?,?,?,?,?)""",
   (CHAPTER,e["id"],issue,facet,pre,original,actual,preline,outcome_line,j(info)))
def build(base,source,output,index_dir):
 base,source,output,index_dir=map(Path,(base,source,output,index_dir))
 if output.exists():raise ValueError("Never overwrite full prior archive")
 if dig(base.read_bytes())!=BASE_SHA:raise ValueError("Parent must be latest pinned full 29-section SQLite")
 raw=source.read_bytes();L=parse_source(raw);items=parse_events(L)
 output.parent.mkdir(parents=True,exist_ok=True)
 with sqlite3.connect("file:"+str(base)+"?mode=ro",uri=True) as old,sqlite3.connect(output) as db:
  old.backup(db)
  db.executescript((ROOT/"schema/migrations/024_kaiwu_employment_shared_domain_multi_issue.sql").read_text("utf8"))
  db.execute("PRAGMA foreign_keys=ON")
  with db:
   if db.execute("SELECT COUNT(*) FROM sections WHERE book_id='kaiwu'").fetchone()[0]!=8:
    raise ValueError("Expected exactly old Kaiwu 8 source sections")
   if db.execute("SELECT 1 FROM sections WHERE book_id='kaiwu' AND section_key=?",(SECTION,)).fetchone():
    raise ValueError("Chapter already imported")
   db.execute("""INSERT INTO sections(book_id,section_key,title,original_text,
     sha256,content_version,reviewed) VALUES ('kaiwu',?,?,?,?,1,1)""",
     (SECTION,TITLE,raw.decode("utf8"),SOURCE_SHA))
   sid=db.execute("SELECT last_insert_rowid()").fetchone()[0]
   db.execute("""INSERT INTO chapter_knowledge(chapter_key,book_id,title,
     source_sha256,source_length_bytes,knowledge_version,review_status)
     VALUES (?,'kaiwu',?,?,?,'1','approved')""",
     (CHAPTER,TITLE,SOURCE_SHA,len(raw)))
   for e in items:add_case(db,sid,L,e)
   for args in ISSUES:insert_issue(db,L,items,*args)
   for e in items:
    for i,line in enumerate(e["editor"],1):
     add_phase(db,L,e,f"editor_postscript_{i}","post_feedback_editor_commentary",line)
   db.execute("""INSERT INTO chapter_archival_versions(archive_label,
     baseline_sha256,new_db_sha256,contains_complete_private_copyright_source,
     snapshot_type,created_utc,repo_public_archive_policy)
     VALUES (?, ?,NULL,1,'kaiwu_employment_shared_domain_three_original_casts_two_issues_one_cast',
      '2026-10-20','user_authorized_public_full_sqlite_versions')""",
     ("shenqi21_kaiwu_work_section04_130cases",BASE_SHA))
  ensure_old_rows(old,db)
  if db.execute("PRAGMA integrity_check").fetchone()[0]!="ok" or db.execute("PRAGMA foreign_key_check").fetchall():
   raise ValueError("Failed after full backup/new provenance before VACUUM")
  expected={
   "sections":30,"cases":130,"historical_chart_cells":1161,
   "historical_case_additional_casts":17,"historical_case_additional_cast_cells":153,
   "historical_palace_standardization":1314,
   "historical_case_reasoning":652,"historical_case_reasoning_trace":652,
   "semantic_assertions":2326,"cross_book_concept_tracks":1069,
   "cross_book_example_references":44,
   "historic_book_case_acceptance":22,
   "unified_case_domain_facets":15,
   "crossbook_employment_source_charts":3,
   "crossbook_employment_source_palaces":27,
   "crossbook_employment_case_issues":4,
   "crossbook_employment_source_caveats":4}
  counts={table:db.execute('SELECT COUNT(*) FROM "'+table+'"').fetchone()[0] for table in expected}
  if counts!=expected:raise ValueError(("Parent+new historic source count mismatch",counts,expected))
  if db.execute("SELECT COUNT(*) FROM cases c JOIN sections s ON c.section_id=s.section_id WHERE s.book_id='kaiwu' AND c.domain_id='employment'").fetchone()[0]!=3:
   raise ValueError("All three must be in existing Shenqi employment domain")
  if db.execute("SELECT COUNT(*) FROM cases WHERE domain_id='employment'").fetchone()[0]<8:
   raise ValueError("Unified employment domain must include old Shenqi five+Kaiwu three")
  if db.execute("SELECT COUNT(*) FROM historical_case_book_verdicts WHERE verdict='author_book_error_explicit'").fetchone()[0]!=8:
   raise ValueError("All eight previously documented book errors must survive")
  if db.execute("SELECT COUNT(*) FROM crossbook_employment_source_palaces WHERE undeciphered_source_stem_count>0").fetchone()[0]!=1:
   raise ValueError("One kan source palace must retain 2 undeciphered stems")
  if db.execute("SELECT SUM(undeciphered_source_stem_count) FROM crossbook_employment_source_palaces").fetchone()[0]!=2:
   raise ValueError("Both original undeciphered Kan stems must remain absent")
  if db.execute("SELECT COUNT(*) FROM crossbook_employment_case_issues WHERE case_id=?",
     ("kaiwu.employment.19971218.zhang_application_and_accident",)).fetchone()[0]!=2:
   raise ValueError("One 1997 first cast must keep two separately evidenced issues")
  db.execute("VACUUM");db.commit()
  if db.execute("PRAGMA integrity_check").fetchone()[0]!="ok" or db.execute("PRAGMA foreign_key_check").fetchall():
   raise ValueError("Final SQLite integrity failed")
 index_dir.mkdir(parents=True,exist_ok=True)
 report={"schema":"wengua_kaiwu_employment_crossbook_shared_cases_v1",
  "source_title":TITLE,"source_sha256":SOURCE_SHA,
  "source_bytes":len(raw),"source_lines":len(L),
  "source_original_cases":3,"source_original_printed_charts":3,
  "new_independent_event_families":3,
  "new_source_published_palace_cells":27,
  "new_author_numbered_reasoning_steps":13,
  "post_feedback_editorial_numbered_steps":4,
  "case3_two_issues_one_historical_event_one_chart":True,
  "case3_first_forecast_not_exact_day":True,
  "case3_exact_day_inferred_after_news":True,
  "case1_undeciphered_kan_stems":2,
  "all_user_book_cases_accepted_without_individual_approval":True,
  "unified_employment_domain":"employment",
  "new_issue_rows":4,"new_multidomain_facet_rows":6,
  "old_eight_book_errors_retained":True,
  "new_author_book_errors":0,
  "total_source_sections":30,"total_event_families":130,
  "total_actual_historical_printed_charts":146,
  "total_historical_palace_standardization":1314,
  "total_historical_author_reasoning":652,
  "book_counts":{"shenqi":21,"kaiwu":9},
  "all_prior_table_rows_unchanged":True,
  "no_external_verification_claimed":True,
  "parent_sha256":BASE_SHA,"output_sha256":dig(output.read_bytes()),
  "cumulative_counts":counts}
 def write(name,data):
  (index_dir/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 write("chapter_manifest.json",report)
 write("case_index.json",{"schema":"crossbook_unified_employment_3_cases_v1",
  "source_sha256":SOURCE_SHA,"cases":[{k:v for k,v in e.items() if k!="cells"} for e in items]})
 write("original_chart_palaces.json",{"source_sha256":SOURCE_SHA,
  "source_palace_cells":[{"case_id":e["id"],"source_start":e["chart"],
                          "palaces":e["cells"]} for e in items]})
 write("issue_index.json",{"source_sha256":SOURCE_SHA,"issues":[
  {"case_id":next(e["id"] for e in items if e["key"]==key),"issue_key":issue,
   "related_domain":facet,"original_prediction_line":p,"outcome_line":r,
   "chronology":note} for key,issue,facet,p,r,note in ISSUES]})
 write("source_audit.json",{"source_sha256":SOURCE_SHA,
  "case3_original_initial_warns_only_month_and_location":True,
  "case3_post_accident_specific_date_deduction_not_pre_crash":True,
  "case3_single_cast_multiple_matters_no_fake_extra_case":True,
  "case3_day_pillar_canonicalization_prohibited":True,
  "case1_unknown_stems_both_preserved_as_printed":True,
  "case1_explicit_zhirun_cast_no_forced_chaibu_recast":True,
  "case2_original_du_men_witness_five_to_two_host":True,
  "all_old_source_rows_unchanged":True,
  "all_cases_accepted_without_individual_review":True,
  "no_historical_predictions_independently_proven":True})
 return report
def main():
 p=argparse.ArgumentParser()
 for name in ("base","source","output","index-dir"):p.add_argument("--"+name,required=True)
 a=p.parse_args()
 print(json.dumps(build(a.base,a.source,a.output,a.index_dir),ensure_ascii=False,indent=2))
if __name__=="__main__":main()
