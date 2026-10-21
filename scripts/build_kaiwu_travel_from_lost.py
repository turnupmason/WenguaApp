"""Append Kaiwu 出行、出国预测 source to WenguaApp complete case SQLite.

Only from the exact 153-case SHA-pinned full source database. Six book event
families, seven genuinely source-printed charts (same Canada applicant twice).
Flight accident is post-news retrospective ONLY; not an advance forecast or a
blind-test success. Canada report verifies interview pass only; not eventual
Canadian PR issuance. Two original Tong travel cases relate to the earlier
lost-motorcycle letter but are DISTINCT journeys, not duplicate loss cases.
Store every 4th/5th source band row and unresolved OCR literally.
"""
from __future__ import annotations
import argparse,hashlib,json,re,sqlite3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE_SHA="3e92bdf9a356edb0685bcb803122319ed56477ab97d0fd38b23a2f5c16fc2185"
SOURCE_SHA="b561f1d0a216ab9da83955112752164c4bf6558be15a0a7017f350e423d37f67"
BASE_NAME="WenguaApp_神奇之门21章_开悟之门13节_153案例_完整研究库.sqlite3"
NEW_NAME="WenguaApp_神奇之门21章_开悟之门14节_159案例_完整研究库.sqlite3"
CHAPTER="kaiwu/travel_abroad_prediction_ch02_section06/v1"
SECTION="travel_abroad_prediction_ch02_section06"
TITLE="第六节 出行、出国预测（共6例）"
PALACES=(4,9,2,3,5,7,8,1,6)
PAL_LABELS=("巽4宫","离9宫","坤2宫","震3宫","中5宫","兑7宫","艮8宫","坎1宫","乾6宫")
CASE_SPECS=[
 dict(id="kaiwu.travel.case01",key="flight_disaster_retrospective",
    label="1992年南京厦门航班事故新闻后复盘",bounds=(3,35),
    question=(4,6),original_forecast=[],reported=[5],
    boards=[(10,11,8,"post_news_retrospective",True)],
    steps=[31,32,33,34],facets=["aviation_accident"],
    note="Aug1 news before Qimen examination: NOT a pre-flight or pre-news warning; no postevent forecast success"),
 dict(id="kaiwu.travel.case02",key="hongkong_permanent_resident",
    label="上海母亲代儿问香港永久居留及春节返乡",bounds=(36,66),
    question=(37,39),original_forecast=[64],reported=[65],
    boards=[(41,42,39,"before_residency_result",False)],
    steps=[60,61,62,63],facets=["immigration_status","family_visit"],
    note="Book says Apr8 residency approved; preserve literal lunar parenthetical, not re-compute or correct; Spring Festival visit was a separate question"),
 dict(id="kaiwu.travel.case03",key="canada_immigration_two_consultations",
    label="广州男士加拿大技术移民两次问面试",bounds=(67,136),
    question=(68,72),original_forecast=[98,130],reported=[131],
    boards=[(74,75,72,"first_letter_19990616",False),
            (103,104,101,"second_phone_19991002",False)],
    steps=[94,95,96,97,123,124,125,126,127,128,133,134,135],
    facets=["immigration_status","immigration_interview"],
    note="Known 1998 prior failed interview; first June letter and Oct 2 reconsult one immigration application; two Qimen boards. Oct29 interview PASS reported, final residency issuance NOT reported; 10/2 contradictory use-deity analysis and post-result reread distinguish phases"),
 dict(id="kaiwu.travel.case04",key="france_passport_refused",
    label="赴法国讲学护照审批未获批准",bounds=(137,169),
    question=(138,141),original_forecast=[167],reported=[168],
    boards=[(143,144,141,"prior_to_official_refusal",False)],
    steps=[162,163,164,165,166],facets=["passport_application"],
    note="Book report: local departments permitted but culture authorities withheld; passports not issued"),
 dict(id="kaiwu.travel.case05",key="tong_outbound_train_20000810",
    label="佟安琪乘火车赴石家庄遭雨毁路基后换乘",bounds=(170,201),
    question=(170,173),original_forecast=[194,195,196,197,198,199],reported=[200],
    boards=[(175,176,172,"outbound_train",False)],
    steps=[194,195,196,197,198,199],facets=["transport_disruption"],
    note="Outbound 8/10: rain-washed rail foundation, changed to coach 8/11; same man referenced in earlier Kaiwu missing-motorcycle CASE but distinctly timed trip event"),
 dict(id="kaiwu.travel.case06",key="tong_return_train_20000818",
    label="佟安琪返程火车因停电延误约三小时",bounds=(202,230),
    question=(202,204),original_forecast=[225,226],reported=[227],
    boards=[(206,207,204,"return_train",False)],
    steps=[225,226],facets=["transport_delay"],
    note="Return train on 8/18, reported rail station power loss and 3h delay. Book's stated destination Shenyang versus return-time location Shijiazhuang is unchanged source text, not silently reconciled")
]
REPORTS=[
 (1,"news_post_accident",None,5,"retroactive_explanation_only"),
 (2,"hongkong_residency_approval",64,65,"book_reported_approval_Apr8"),
 (2,"spring_festival_homecoming",64,65,"book_reported_Shanghai_reunion"),
 (3,"first_june_interview_forecast",98,131,"book_reported_Oct29_interview_pass_only"),
 (3,"second_oct_interview_forecast",130,131,"book_reported_Oct29_interview_pass_only"),
 (4,"france_passport_unapproved",167,168,"book_reported_application_failed"),
 (5,"train_flood_damage_bus_transfer",197,200,"book_reported_train_delay_and_bus"),
 (6,"return_train_power_failure",225,227,"book_reported_about_three_hour_delay")
]
def digest(b):return hashlib.sha256(b).hexdigest()
def J(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(",",":"))
def span(L,a,b=None):
 b=a if b is None else b
 if not 1<=a<=b<=len(L):raise ValueError(("Invalid original source lines",a,b,len(L)))
 return "\n".join(L[a-1:b])
def validate(raw):
 if digest(raw)!=SOURCE_SHA or len(raw)!=28678 or not raw.endswith(b"\n"):
  raise ValueError("User exact original SHA/byte length differs")
 L=raw.decode("utf-8").splitlines()
 if len(L)!=230 or L[0]!=TITLE:raise ValueError("Wrong original chapter or incomplete source")
 if [n for n,s in enumerate(L,1) if re.match(r"^（例[一二三四五六]）",s)]!=[3,36,67,137,170,202]:
  raise ValueError("Six original historical event headings")
 if [n for n,s in enumerate(L,1) if s.startswith("奇门九宫格（起局盘第")]!=[10,41,74,103,143,175,206]:
  raise ValueError("Exactly seven original Qimen boards")
 if "事后" not in L[5] or "10月29日" not in L[130] or "6月16日上午11点40分" not in L[134]:
  raise ValueError("Book temporal information missing")
 if "出国手续停止下来" not in L[167] or "0点57分" not in L[226]:
  raise ValueError("Last source feedback missing")
 return L
def parse_panel(L,start):
 if not L[start-1].startswith("+"):raise ValueError(("Source chart original + border missing",start))
 groups=[];band=[];band_first=0
 for line_no in range(start+1,len(L)+1):
  value=L[line_no-1]
  if value.startswith("+"):
   if band:
    groups.append((band_first,band))
    band=[];band_first=0
   if len(groups)==3:break
  elif value.startswith("|"):
   cells=[x.strip() for x in value.split("|")[1:-1]]
   if len(cells)!=3:raise ValueError(("Source three original columns changed",start,line_no))
   if not band:band_first=line_no
   band.append(cells)
  else:raise ValueError(("Broken original Qimen source chart",start,line_no))
 else:raise ValueError("Original source Qimen board unclosed")
 if len(groups)!=3 or any(len(v[1]) not in (4,5) for v in groups):
  raise ValueError(("Nonstandard Qimen original band source length",start))
 out=[]
 for r,(first,layer) in enumerate(groups):
  for col in range(3):
   palace=PALACES[r*3+col]
   values=[a[col] for a in layer]
   label,god,door,star=values[:4];extra=values[4:]
   if label!=PAL_LABELS[r*3+col]:raise ValueError(("Original palace label changed",start,palace,label))
   if palace==5:
    if door or star or any(extra):raise ValueError("No invented ordinary god/gate/star fields at middle five")
   elif not god or not door or not star:
    raise ValueError(("Outer Qimen three source layers incomplete",start,palace))
   literal="\n".join(values)
   damaged=int(any(word in literal for word in ("原OCR","缺字","缺损","游离","待核","据正文")))
   out.append({"palace":palace,"line":first+col,"start":first,"end":first+len(layer)-1,
    "label":label,"god":god,"door":door,"star":star,"extra":extra,
    "literal":literal,"sha":digest(literal.encode("utf-8")),"damaged":damaged})
 if sorted(x["palace"] for x in out)!=list(range(1,10)):
  raise ValueError("Nonunique/missing original nine palaces")
 return line_no,out
def prepare_cases(L):
 out=[]
 for i,e in enumerate(CASE_SPECS,1):
  boards=[]
  for j,(caption,start,cal,role,known) in enumerate(e["boards"]):
   if not L[caption-1].startswith("奇门九宫格"):raise ValueError(("Original caption absent",caption))
   finish,cells=parse_panel(L,start)
   boards.append({"key":"primary" if j==0 else "additional_"+str(j),
    "caption":caption,"start":start,"end":finish,"cal":cal,"role":role,
    "outcome_known":known,"cells":cells,
    "sha":digest(span(L,start,finish).encode("utf-8"))})
  if not all(re.match(r"^（[1-9]）",L[n-1]) for n in e["steps"]):
   raise ValueError(("Book numbered reasoning steps incomplete",e["key"]))
  out.append({**e,"number":i,"boards":boards})
 if sum(len(e["steps"]) for e in out)!=34:raise ValueError("Original numbered author + postevent 34 units")
 if sum(len(e["boards"]) for e in out)!=7:raise ValueError("7 printed casts required")
 if sum(len(b["cells"]) for e in out for b in e["boards"])!=63:
  raise ValueError("63 literal original source palace cells required")
 if sum(bool(c["extra"] and any(c["extra"])) for e in out for b in e["boards"] for c in b["cells"])!=4:
  raise ValueError("Four exact special OCR extra source palace rows mandatory")
 if out[0]["boards"][0]["outcome_known"] is not True:
  raise ValueError("Flight incident must be retrospective, not first prediction")
 return out
def verify_all_old_rows(old,db):
 for (name,) in old.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"):
  cols=[x[1] for x in old.execute('PRAGMA table_info("'+name+'")')]
  query=",".join('"'+v+'"' for v in cols)
  prev=list(old.execute('SELECT '+query+' FROM "'+name+'"'))
  after=set(db.execute('SELECT '+query+' FROM "'+name+'"'))
  if not all(row in after for row in prev):
   raise ValueError("Older Shenqi/Kaiwu source row overwritten: "+name)
def add_phase(db,L,e,key,kind,a,b=None,extra=None):
 b=a if b is None else b
 excerpt=span(L,a,b)
 meta={"user_accepts_this_source_without_case_approval":True,
       "no_independent_external_validation_claimed":True,
       "later_book_feedback_does_not_belong_in_earlier_forecast":True,**(extra or {})}
 db.execute("""INSERT INTO kaiwu_travel_chronology(chapter_key,case_id,phase_key,
 phase_kind,source_start_line,source_end_line,source_literal,excerpt_sha256,timing_metadata_json)
 VALUES (?,?,?,?,?,?,?,?,?)""",(CHAPTER,e["id"],key,kind,a,b,excerpt,
 digest(excerpt.encode("utf-8")),J(meta)))
def insert_case(db,L,e,sid):
 case=e["id"];ix=e["number"]
 known=span(L,*e["question"])
 judgment="\n".join(span(L,n) for n in e["original_forecast"]) if e["original_forecast"] else span(L,6)
 feedback="\n".join(span(L,n) for n in e["reported"])
 reasoning="\n\n".join(span(L,n) for n in e["steps"])
 meta={"book_id":"kaiwu","source_lines":e["bounds"],"source_book_report_accepted":True,
       "source_first_prediction_exists":ix!=1,"flight_outcome_before_divination":ix==1,
       "case3_multiple_original_casts_one_applicant":ix==3,
       "case3_interview_pass_does_not_prove_final_canadian_residency":ix==3,
       "case3_post_feedback_explanations_not_original_1999_forecast":ix==3,
       "book_accepted_no_user_manual_case_approval":True,
       "not_independently_empirically_validated":True,"source_note":e["note"]}
 db.execute("""INSERT INTO cases(case_id,section_id,event_family_id,domain_id,
  known_before,author_yongshen_steps,author_judgment,later_feedback,reviewed)
  VALUES (?,?,?,'travel_abroad',?,?,?,?,1)""",
  (case,sid,case,known,reasoning,judgment,feedback))
 db.execute("""INSERT INTO historical_case_protocol(case_id,completeness,
  published_chart_verification,feedback_independently_verified,eligible_blind_test,
  case_source_sha256,metadata_json)
  VALUES (?,'full_original_book_case_with_all_genuine_casts',
  'original_source_OCR_not_recast_or_repaired',0,0,?,?)""",
  (case,SOURCE_SHA,J(meta)))
 db.execute("""INSERT INTO historic_book_case_acceptance(case_id,source_book,
  source_chapter_key,source_documented_outcome,metadata_json)
  VALUES (?,'kaiwu',?,'source_reports_as_written_not_independently_certified',?)""",
  (case,CHAPTER,J(meta)))
 for domain in ["travel_abroad"]+e["facets"]:
  db.execute("""INSERT INTO unified_case_domain_facets(case_id,domain_id,
   source_chapter_key,primary_domain,note)
   VALUES (?,?,?,?,?)""",(case,domain,CHAPTER,int(domain=="travel_abroad"),e["note"]))
 add_phase(db,L,e,"full_original_case","entire_source_case_context",*e["bounds"])
 add_phase(db,L,e,"prior_known","before_first_forecast_or_retrospective_known",*e["question"])
 for k,n in enumerate(e["original_forecast"],1):
  add_phase(db,L,e,f"original_judgment_{k}","pre_feedback_attributed_judgment",n,
   extra={"original_cast_index":k if ix==3 else 1})
 for k,n in enumerate(e["reported"],1):
  add_phase(db,L,e,f"reported_feedback_{k}","book_outcome_reported",n)
 if ix==1:
  add_phase(db,L,e,"prepublished_disaster_news","accident_known_before_this_cast",4,6,
            {"not_an_advance_prediction":True,"cannot_train_as_successful_forecast":True})
 if ix==2:
  add_phase(db,L,e,"lunar_source_literal","inconsistent_parenthetical_preserved_no_calendar_correction",65)
 if ix==3:
  add_phase(db,L,e,"known_1998_prior_failure","prior_real_world_failed_interview",69)
  add_phase(db,L,e,"second_consultation_request","new_consultation_same_applicant",99,101)
  add_phase(db,L,e,"contradictory_yongshen","original_second_chart_conflicting_principles",123,130)
  add_phase(db,L,e,"reassessment_after_interview","post_result_author_method_explanation",132,135)
  db.execute("""INSERT INTO kaiwu_travel_missing_cast_mentions(chapter_key,case_id,
    reference_key,source_line,original_literal) VALUES (?,?,?,?,?)""",
    (CHAPTER,case,"unprinted_1999_jun16_morning_call",135,span(L,135)))
 if ix==6:
  add_phase(db,L,e,"return_destination_literal_conflict",
    "source_literal_geography_do_not_silently_fix",202,227)
 if ix in (5,6):
  db.execute("""INSERT INTO kaiwu_travel_source_context_links(chapter_key,case_id,
   related_case_id,relation_type,new_source_line,previous_source_line,
   original_line,metadata_json) VALUES (?,?,?,?,?,?,?,?)""",
  (CHAPTER,case,"kaiwu.lost_property.case04",
   "same_Tong_Angqi_person_but_distinct_train_trip_event_from_motorcycle_loss",
   170 if ix==5 else 202,143 if ix==5 else 147,
   span(L,170 if ix==5 else 202),
   J({"same_person":True,"same_event":False,
      "older_lost_case_has_only_mention_no_printed_train_board":True,
      "new_full_original_train_chart_now_provided":True})))
 for board in e["boards"]:
  cast_key=board["key"]
  add_phase(db,L,e,"original_board_"+cast_key,"source_original_genuine_printed_cast",
   board["start"],board["end"],{"cast_phase":board["role"],
                                 "outcome_known_before_cast":board["outcome_known"]})
  db.execute("""INSERT INTO kaiwu_travel_source_casts(chapter_key,case_id,cast_key,
   caption_line,source_start_line,source_end_line,grid_source_sha256,
   calendar_source_line,calendar_original,source_time_phase,outcome_known_at_cast,
   cast_metadata_json) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
   (CHAPTER,case,cast_key,board["caption"],board["start"],board["end"],
    board["sha"],board["cal"],span(L,board["cal"]),board["role"],int(board["outcome_known"]),
    J({"source_case_number":ix,"source_text_sha256":SOURCE_SHA,
       "additional_cast_same_case":cast_key!="primary","exact_ocr_preserved":True})))
  if cast_key!="primary":
   db.execute("""INSERT INTO historical_case_additional_casts(case_id,cast_key,
    cast_datetime_description,calendar_date,hour_ganzhi,source_chart_start,notes)
    VALUES (?,?,?,?,?,?,?)""",
   (case,cast_key,"1999-10-02 18:55 Guangzhou caller's second consultation",
    "1999-10-02","己酉",board["start"],
    "Second book-printed cast, SAME Canada immigration application; NOT new event/case family"))
  for cell in board["cells"]:
   pal=cell["palace"];center=pal==5
   db.execute("""INSERT INTO kaiwu_travel_original_palaces(chapter_key,case_id,cast_key,
    palace,original_start_line,original_end_line,palace_header_raw,spirit_raw,gate_raw,
    star_raw,extra_rows_json,source_literal_text,source_literal_sha256,ocr_unresolved)
    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
    (CHAPTER,case,cast_key,pal,cell["start"],cell["end"],cell["label"],
     cell["god"],cell["door"],cell["star"],J(cell["extra"]),cell["literal"],
     cell["sha"],cell["damaged"]))
   if cast_key=="primary":
    db.execute("""INSERT INTO historical_chart_cells(case_id,palace,source_line,
    palace_label_raw,deity_raw,door_position_raw,star_position_raw,source_status)
    VALUES (?,?,?,?,?,?,?,'exact_book_OCR_with_extra_line_in_separate_source_witness')""",
    (case,pal,cell["line"],cell["label"],cell["god"],cell["door"],cell["star"]))
   else:
    db.execute("""INSERT INTO historical_case_additional_cast_cells(case_id,cast_key,
     palace,source_line,palace_label_raw,deity_raw,door_position_raw,star_position_raw)
    VALUES (?,?,?,?,?,?,?,?)""",
    (case,cast_key,pal,cell["line"],cell["label"],cell["god"],cell["door"],cell["star"]))
   c_raw=cell["god"] if center else None
   c_stem=c_raw if center and re.fullmatch(r"[甲乙丙丁戊己庚辛壬癸]",c_raw) else None
   db.execute("""INSERT INTO historical_palace_standardization(case_id,cast_key,
     palace,center_stem,source_of_center_stem,standard_deity,standard_door,standard_star,
     normalized_status,original_raw_integrity_checked,method_reference,
     derived_host_palace,derived_host_source)
     VALUES (?,?,?,?,?,?,?,?,?,1,?,?,?)""",
    (case,cast_key,pal,c_stem,
     "literal_source_center_only_stem" if c_stem else
     "source_mid5_OCR_unresolved_do_not_infer" if center else "not_center",
     None if center or cell["damaged"] else cell["god"],
     None if center or cell["damaged"] else cell["door"],
     None if center or cell["damaged"] else cell["star"],
     "center_original_not_regular_deity_gate_star" if center else
     "OCR_deficiency_all_four_five_literal_rows_retained" if cell["damaged"] else
     "original_source_only_unmodified",
     "kaiwu_travel_6events_7literal_original_casts",
     2 if center else None,
     "host_to_Kun_derived_not_original_print" if center else None))
 for step_index,n in enumerate(e["steps"],1):
  literal=span(L,n)
  explanation_type=("retrospective_after_news" if ix==1 else
      "post_pass_author_exposition" if ix==3 and n>=133 else
      "source_author_original_reasoning")
  info={"source_line":n,"reasoning_phase":explanation_type,
        "original_source":True,"model_positive_training_eligible":False,
        "book_case_accepted_without_manual_user_review":True,
        "no_external_scientific_validation":True}
  db.execute("""INSERT INTO historical_case_reasoning(case_id,step_number,source_line,
   author_analysis_original,short_method_topic,metadata_json) VALUES (?,?,?,?,?,?)""",
   (case,step_index,n,literal,explanation_type,J(info)))
  db.execute("""INSERT INTO historical_case_reasoning_trace(case_id,step_number,
    source_line,evidence_json,review_status,positive_training_eligible)
    VALUES (?,?,?,?,'source_book_accepted_do_not_automatically_promote',0)""",
    (case,step_index,n,J(info)))
  cid=f"travel:kaiwu:case{ix:02}:analysis_step{step_index:02}"
  db.execute("""INSERT INTO semantic_assertions(chapter_key,concept_id,kind,relation,
   source_start_line,source_end_line,metadata_json,original_excerpt,review_status)
   VALUES (?,?,?,?,?,?,?,?,'draft')""",
   (CHAPTER,cid,"original_travel_book_case_reasoning","additional_exposition",
    n,n,J(info),literal))
  db.execute("""INSERT INTO cross_book_concept_tracks(chapter_key,concept_id,source_start_line,
   source_end_line,source_section_id,source_sha256,excerpt_sha256,track_id,
   relation_to_prior,comparison_state,normalized_json,review_status)
   VALUES (?,?,?,?,?,?,?,?,?,'accepted_book_source_not_external_validation',?,'draft')""",
   (CHAPTER,cid,n,n,sid,SOURCE_SHA,digest(literal.encode("utf8")),
    "kaiwu:travel:author_source_6cases_v1","additional_exposition",J(info)))
 db.execute("""INSERT INTO historical_case_review_audit(case_id,original_steps,
  mechanical_step_trace,human_complete_step_chains,review_status,warning)
  VALUES (?,?,?,0,'book_original_accepted_no_user_manual_case_approval',?)""",
  (case,len(e["steps"]),len(e["steps"]),e["note"]))
 if ix!=1:
  db.execute("""INSERT INTO historical_case_book_verdicts(event_family_id,primary_case_id,
  verdict,explicit_source_correction,source_correction_lines_json,
  feedback_source_lines_json,independent_external_verification,app_output_protocol,
  evidence_review_status,note) VALUES (?,?,'author_book_success_default',0,'[]',?,
  'not_verified','single_answer_for_one_cast','book_report_not_empirically_verified',?)""",
  (case,case,J(e["reported"]),e["note"]))
def build(base,source,output,index_dir):
 base,source,output,index_dir=map(Path,(base,source,output,index_dir))
 if output.exists():raise ValueError("Never overwrite a prior complete immutable book database")
 if digest(base.read_bytes())!=BASE_SHA:raise ValueError("Parent full 153-case SQLite SHA mismatch")
 raw=source.read_bytes();L=validate(raw);items=prepare_cases(L)
 output.parent.mkdir(parents=True,exist_ok=True)
 with sqlite3.connect("file:"+str(base)+"?mode=ro",uri=True) as old,sqlite3.connect(output) as db:
  old.backup(db)
  db.executescript((ROOT/"schema/migrations/029_kaiwu_travel_two_casts_retrospective.sql").read_text("utf8"))
  db.execute("PRAGMA foreign_keys=ON")
  with db:
   if db.execute("SELECT count(*) FROM sections WHERE book_id='kaiwu'").fetchone()[0]!=13:
    raise ValueError("All 13 original prior Kaiwu chapters must remain")
   db.execute("""INSERT INTO sections(book_id,section_key,title,original_text,
    sha256,content_version,reviewed) VALUES ('kaiwu',?,?,?,?,1,1)""",
    (SECTION,TITLE,raw.decode("utf8"),SOURCE_SHA))
   sid=db.execute("SELECT last_insert_rowid()").fetchone()[0]
   db.execute("""INSERT INTO chapter_knowledge(chapter_key,book_id,title,source_sha256,
    source_length_bytes,knowledge_version,review_status)
    VALUES (?,'kaiwu',?,?,?,'1','approved')""",
    (CHAPTER,TITLE,SOURCE_SHA,len(raw)))
   for e in items:insert_case(db,L,e,sid)
   for num,q_key,pred,result,scope in REPORTS:
    e=items[num-1]
    if pred is None and num!=1:raise ValueError("Only post-event accident has no advance prediction")
    db.execute("""INSERT INTO kaiwu_travel_scoped_outcomes(chapter_key,case_id,
     question_key,prior_prediction_line,initial_prediction_original,
     book_feedback_line,book_feedback_original,book_report_scope,originally_retrospective)
     VALUES (?,?,?,?,?,?,?,?,?)""",
     (CHAPTER,e["id"],q_key,pred,span(L,pred) if pred else None,
      result,span(L,result),scope,int(num==1)))
   db.execute("""INSERT INTO chapter_archival_versions(archive_label,baseline_sha256,
    new_db_sha256,contains_complete_private_copyright_source,snapshot_type,
    created_utc,repo_public_archive_policy)
    VALUES (?,?,NULL,1,'6_travel_event_families_7_original_casts_one_postnews',
    '2026-10-20','user_authorized_public_full_sqlite_versions')""",
    ("shenqi21_kaiwu14_travel_159cases",BASE_SHA))
  verify_all_old_rows(old,db)
  if db.execute("PRAGMA integrity_check").fetchone()[0]!="ok" or db.execute("PRAGMA foreign_key_check").fetchall():
   raise ValueError("Complete SQLite integrity/foreign key failure before VACUUM")
  expected={"sections":35,"cases":159,"historical_chart_cells":1422,
    "historical_case_additional_casts":19,
    "historical_case_additional_cast_cells":171,
    "historical_palace_standardization":1593,
    "historical_case_reasoning":813,"historical_case_reasoning_trace":813,
    "semantic_assertions":2487,"cross_book_concept_tracks":1230,
    "cross_book_example_references":48,
    "historic_book_case_acceptance":51,"unified_case_domain_facets":71,
    "kaiwu_travel_source_casts":7,"kaiwu_travel_original_palaces":63,
    "kaiwu_travel_scoped_outcomes":8,
    "kaiwu_travel_source_context_links":2,"kaiwu_travel_missing_cast_mentions":1}
  got={n:db.execute('SELECT count(*) FROM "'+n+'"').fetchone()[0] for n in expected}
  if got!=expected:raise ValueError(("Wrong aggregate full parent+new source counts",got,expected))
  if db.execute("SELECT count(*) FROM cases WHERE domain_id='travel_abroad'").fetchone()[0]!=12:
   raise ValueError("6 old Shenqi+6 Kaiwu must use one travel domain")
  if db.execute("SELECT count(*) FROM kaiwu_travel_source_casts WHERE outcome_known_at_cast=1").fetchone()[0]!=1:
   raise ValueError("Air disaster retrospective must be visibly known at casting")
  if db.execute("SELECT count(*) FROM historical_case_book_verdicts WHERE verdict='author_book_error_explicit'").fetchone()[0]!=9:
   raise ValueError("Nine original source explicit errors were modified")
  if db.execute("SELECT 1 FROM historical_case_book_verdicts WHERE primary_case_id='kaiwu.travel.case01'").fetchone():
   raise ValueError("Retrospective airplane accident CANNOT be scored as successful forecast")
  if db.execute("SELECT count(*) FROM kaiwu_travel_original_palaces WHERE extra_rows_json!='[]'").fetchone()[0]!=12:
   raise ValueError("All OCR supplemental source palace rows must survive")
  db.execute("VACUUM");db.commit()
  if db.execute("PRAGMA integrity_check").fetchone()[0]!="ok" or db.execute("PRAGMA foreign_key_check").fetchall():
   raise ValueError("Final actual book sqlite verification failed")
 index_dir.mkdir(parents=True,exist_ok=True)
 report={"schema":"wengua_kaiwu_ch02_section06_travel_six_events_seven_literal_casts",
  "source_title":TITLE,"source_sha256":SOURCE_SHA,
  "source_bytes":len(raw),"source_lines":len(L),"new_source_cases":6,
  "new_genuine_source_casts":7,"new_literal_original_palaces":63,
  "new_author_numbered_steps_with_three_retrospective_exposition":34,
  "case01_airplane_accident_post_news_not_advance_prediction":True,
  "case03_canada_two_consultations_one_immigration_event":True,
  "case03_only_interview_pass_reported_not_final_PR":True,
  "case03_unprinted_jun16_morning_cast_mention_not_counted":True,
  "case03_post_result_reasoning_and_conflicting_first_judgments_retained":True,
  "case05_06_same_earlier_lost_motorbike_correspondent_distinct_train_events":True,
  "all_nonstandard_four_five_source_rows_preserved":True,
  "book_historical_cases_accepted_without_individual_approval":True,
  "not_independent_aviation_immigration_travel_verification":True,
  "book_counts":{"shenqi":21,"kaiwu":14},"total_source_sections":35,
  "total_distinct_historical_events":159,"total_original_historical_casts":177,
  "previous_nine_explicit_case_errors_unchanged":True,
  "parent_sha256":BASE_SHA,"new_database_sha256":digest(output.read_bytes()),
  "all_old_tables_and_rows_unchanged":True,"counts":got}
 def save(name,obj):
  (index_dir/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 save("chapter_manifest.json",report)
 save("case_index.json",{"source_sha256":SOURCE_SHA,
  "cases":[{k:v for k,v in e.items() if k!="boards"}|
   {"boards":[{k:v for k,v in b.items() if k!="cells"} for b in e["boards"]]} for e in items]})
 save("source_board_palaces.json",{"source_sha256":SOURCE_SHA,
  "boards":[{"case_id":e["id"],"cast_key":b["key"],"original_start":b["start"],
   "original_end":b["end"],"palaces":b["cells"]} for e in items for b in e["boards"]]})
 save("chronology_scope_audit.json",{"source_sha256":SOURCE_SHA,
   "flight_newscast_precedes_qimen_retro_analysis":True,
   "canada_two_genuine_casts_one_event_older_failure_already_known":True,
   "canada_oct_first_prediction_conflicted_day_hour_vs_birth_year":True,
   "canada_post_outcome_reinterpretation_not_initial_pre_report_reasoning":True,
   "canada_reported_interview_pass_not_final_immigration_document":True,
   "canada_extra_jun16_morning_cast_unprinted":True,
   "hongkong_lunar_parenthetical_verbatim_not_corrected":True,
   "outbound_train_weather_rain_washout_and_coach":True,
   "return_train_location_literals_not_silently_repaired":True,
   "all_previous_source_rows_identical":True,
   "all_user_book_cases_accepted_without_per_case_review":True})
 return report
def main():
 ap=argparse.ArgumentParser()
 for name in ("base","source","output","index-dir"):ap.add_argument("--"+name,required=True)
 a=ap.parse_args()
 print(json.dumps(build(a.base,a.source,a.output,a.index_dir),ensure_ascii=False,indent=2))
if __name__=="__main__":main()
