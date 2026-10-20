"""《开悟之门》第二章第二节：恋爱婚姻6例，与神奇之门共用marriage领域.

Additive sqlite3.backup() full 28-source/121-event parent; every old row preserved.
Six real printed boards (54 literal palace cells); two described omitted casts
in sixth case MUST NOT be completed. Case2 & case3 same woman but distinct
question times and event families. Sixth initial reading explicitly wrong.
Original source is accepted by user without individual approval, NOT external
scientific/clinical verification. Sexual orientation is not a disorder.
"""
from __future__ import annotations
import argparse,hashlib,json,re,sqlite3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE_SHA="6dfe4337697e64a100f63de0b9d5144ad00e3b2e3fa818d9d314ea304a92a10d"
SOURCE_SHA="4df9dfe432daec759df4f0e01449bc4a2381eb4251e1290a0d99d199e467fa01"
BASE_NAME="WenguaApp_神奇之门21章_开悟之门7节_121案例_完整研究库.sqlite3"
NEW_NAME="WenguaApp_神奇之门21章_开悟之门8节_127案例_完整研究库.sqlite3"
CHAPTER="kaiwu/marriage_prediction_ch02_section02/v1"
SECTION="marriage_prediction_ch02_section02"
TITLE="第二章 日常百事预测评析 / 第二节 恋爱婚姻预测(共6例)"
PAL=(4,9,2,3,5,7,8,1,6)
NAMES=("巽4","离9","坤2","震3","中5","兑7","艮8","坎1","乾6")
SPEC=[
 dict(key="mother_son_marriage_1998",title="王大妈问儿子婚期",
  start=5,end=46,chart=15,meta=13,question=(7,11),step=[39,41,43],
  predictions=[31,35],feedback=[33,45],extra_phases=[],
  facets=["marriage"],date="1998-11-09",hour="丁亥",
  nuance="1997 year prior prediction is referenced but its original complete chart is not printed here; registration Dec16 and wedding Jan17 separately"),
 dict(key="daughter_divorce_1997",title="石建国预测女儿1998年离婚",
  start=47,end=94,chart=57,meta=53,question=(49,55),step=[73,77,81,89],
  predictions=[73,77,81,89],feedback=[93],extra_phases=[],
  facets=["marriage"],date="1997-02-23",hour="乙未",
  nuance="Mother's June4 1998 report is retrospective; domestic violence documented verbatim only in book"),
 dict(key="daughter_courtship_1998",title="同一女儿离婚后另择对象",
  start=95,end=136,chart=105,meta=103,question=(97,103),step=[123,125,127,129],
  predictions=[121,131,133],feedback=[135],extra_phases=[],
  facets=["marriage"],date="1998-06-04",hour="辛亥",
  nuance="Same woman as case2 but NEW casting date/question; two rejected 1998 suitors, separate successful new 1999 suitor"),
 dict(key="wang_xiqiang_courtship_job",title="王夕强女青年恋爱工作失财",
  start=137,end=182,chart=143,meta=141,question=(139,141),step=[173,175,177,179,181],
  predictions=[159,163,165],feedback=[161,167],extra_phases=[(169,169,"conversation_conclusion")],
  facets=["marriage","employment","lost_property"],date="1999-06-27",hour="乙酉",
  nuance="Known-before breakup, later job prediction for lunar month seven has no reported fulfillment in this source; money loss confirmed by querent"),
 dict(key="wang_xiqiang_remarriage_business",title="王夕强妇女家庭复婚和生意",
  start=183,end=250,chart=195,meta=193,question=(185,193),step=[211,217,223,229,235,241],
  predictions=[213,219,225,231,237,243],feedback=[215,221,227,233,239,245],
  extra_phases=[(247,249,"author_postscript")],
  facets=["marriage","business_profit"],date="1999-07-08",hour="癸巳",
  nuance="Past divorce/poor sales confirmed in dialogue; future remarriage and business recovery NOT followed up by book"),
 dict(key="letter_male_same_sex_love_2000",title="青年来信测情感困扰与首次错断",
  start=251,end=305,chart=265,meta=263,question=(259,263),step=[283,285,287,289],
  predictions=[293,295],feedback=[297,299,301],
  extra_phases=[(253,257,"author_prior_policy_not_guess_intent"),
                (303,303,"retrospective_author_secondary_cast_unprinted"),
                (305,305,"post_disclosure_author_reply_not_initial_guess")],
  facets=["marriage"],date="2000-08-27",hour="庚子",
  explicit_error=True,
  nuance="Initial letter guessed infatuation with a woman and user explicitly rejected it; later revealed same-sex attraction in 2000-09-21 private letter; sexuality is NOT disease, different answer cannot be counted as first-time success")
]
def h(b):return hashlib.sha256(b).hexdigest()
def j(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":"))
def src(L,a,b=None):
 b=a if b is None else b
 if not 1<=a<=b<=len(L):raise ValueError(("bad source range",a,b))
 return "\n".join(L[a-1:b])
def parse_original(b):
 if h(b)!=SOURCE_SHA:raise ValueError("Uploaded complete exact source SHA differs")
 L=b.decode("utf-8").splitlines()
 if len(L)!=305 or L[0]!="第二章 日常百事预测评析" or L[2]!="第二节 恋爱婚姻预测(共6例)":
  raise ValueError("Wrong/missing full original section")
 if not b.endswith(b"\n") or not L[-1].endswith("正常起来的。"):
  raise ValueError("Missing original last reply")
 if [i for i,x in enumerate(L,1) if re.match(r"^\(例[一二三四五六]\)",x)]!=[5,47,95,137,183,251]:
  raise ValueError("Six complete original source examples required")
 if [i for i,x in enumerate(L,1) if x.startswith("┌") ]!=[15,57,105,143,195,265]:
  raise ValueError("Exactly six actual literal printed nine-palace boards required")
 if "准确度应该说是极低的" not in L[296] or "所测与所问大相径庭" not in L[296]:
  raise ValueError("Original author's acknowledged incorrect reading source missing")
 if "具体格局略" not in L[302] or "出生时间局在此省略" not in L[260]:
  raise ValueError("Two unprinted additional boards must remain absent")
 return L
def board(L,start):
 if not L[start-1].startswith("┌") or not L[start+12-1].startswith("└"):
  raise ValueError(("Not complete 13-line original panel",start))
 out=[]
 for row in range(3):
  b=start+1+row*4
  parts=[]
  for shift in range(3):
   line=L[b+shift-1]
   if not line.startswith("│") or not line.endswith("│"):
    raise ValueError(("Malformed original grid source",start,b+shift))
   cells=[z.strip() for z in line.split("│")[1:-1]]
   if len(cells)!=3:raise ValueError(("Expected exactly three original column cells",start))
   parts.append(cells)
  if row<2 and not L[b+2].startswith("├"):
   raise ValueError(("Original chart separator missing",start))
  for col in range(3):
   idx=row*3+col;pal=PAL[idx];name=NAMES[idx];header=parts[0][col]
   if not header.startswith(name):raise ValueError(("Source palace label mismatch",start,pal))
   deity=header[len(name):].strip();door=parts[1][col];star=parts[2][col]
   if pal==5 and (deity or star or not door):raise ValueError("Center original must have no standard deity/star/door")
   if pal!=5 and (not door or not star):raise ValueError(("Source side palace empty",start,pal))
   literal="\n".join((header,door,star))
   out.append({"palace":pal,"start_line":b,"end_line":b+2,
     "source_line_unique":b+col,"palace_label":name,
     "deity":deity,"door":door,"star":star,"literal":literal,
     "sha256":h(literal.encode("utf-8"))})
 if len(out)!=9 or sorted(p["palace"] for p in out)!=list(range(1,10)):
  raise ValueError("Only original nine palaces admissible")
 return out
def parsed(L):
 events=[]
 for n,s in enumerate(SPEC,1):
  if not L[s["start"]-1].startswith("(例"):raise ValueError(("Missing original case title",n))
  assert all(re.match(r"^\(\d+\)",L[z-1]) for z in s["step"])
  if s["key"]=="letter_male_same_sex_love_2000":
   assert "他英俊" in L[300] and "我爱上了他" in L[300]
  ev={**s,"number":n,"id":f"kaiwu.marriage.case{n:02}",
      "cells":board(L,s["chart"]),
      "chart_end":s["chart"]+12,
      "chart_sha256":h(src(L,s["chart"],s["chart"]+12).encode("utf-8"))}
  events.append(ev)
 if len(events)!=6 or sum(len(x["step"]) for x in events)!=26:
  raise ValueError("Missing 6 full cases and 26 source-numbered author steps")
 return events
def all_prior_rows_preserved(old,db):
 for (table,) in old.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"):
  cols=[q[1] for q in old.execute('PRAGMA table_info("'+table+'")')]
  sel=",".join('"'+x+'"' for x in cols)
  past=list(old.execute('SELECT '+sel+' FROM "'+table+'"'))
  now=set(db.execute('SELECT '+sel+' FROM "'+table+'"'))
  if not all(z in now for z in past):
   raise ValueError("Source-preserved prior SQLite row altered: "+table)
def add_phase(db,L,e,name,kind,a,b,extra=None):
 literal=src(L,a,b)
 data={"question_event":e["id"],"phase":kind,
  "source_is_an_accepted_book_case":True,
  "not_externally_validated":True,
  "later_disclosure_must_not_be_in_initial_prompt":True,
  **(extra or {})}
 db.execute("""INSERT INTO crossbook_relationship_case_phases(chapter_key,case_id,
  phase_key,phase,start_line,end_line,original_text,source_sha256,chronology_json)
  VALUES (?,?,?,?,?,?,?,?,?)""",
  (CHAPTER,e["id"],name,kind,a,b,literal,h(literal.encode("utf-8")),j(data)))
def add_event(db,L,sid,e):
 cid=e["id"]
 before=src(L,*e["question"])
 original_reason="\n\n".join(src(L,n) for n in e["step"])
 forecast="\n".join(src(L,n) for n in e["predictions"])
 outcome="\n".join(src(L,n) for n in e["feedback"])
 db.execute("""INSERT INTO cases(case_id,section_id,event_family_id,domain_id,
  known_before,author_yongshen_steps,author_judgment,later_feedback,reviewed)
  VALUES (?,?,?,'marriage',?,?,?,?,1)""",
  (cid,sid,cid,before,original_reason,forecast,outcome))
 proto={"source_sha256":SOURCE_SHA,"source_example_number":e["number"],
  "book_source_accepted_without_individual_review":True,
  "question_time":[e["date"],e["hour"]],"source_span":[e["start"],e["end"]],
  "source_chart_line":e["chart"],"case_notes":e["nuance"],
  "source_fields_verbatim":True,"external_validation_not_claimed":True,
  "sexual_orientation_not_pathology":True if e["number"]==6 else None,
  "source_emphatic_initial_miss":bool(e.get("explicit_error")),
  "old_same_person_case_not_same_event":True if e["number"] in (2,3) else False}
 db.execute("""INSERT INTO historical_case_protocol(case_id,completeness,
  published_chart_verification,feedback_independently_verified,
  eligible_blind_test,case_source_sha256,metadata_json)
  VALUES (?,'source_original_story_and_full_printed_board',
  'book_exact_original_not_independently_recast',0,?,?,?)""",
  (cid,int(not e.get("explicit_error")),SOURCE_SHA,j(proto)))
 db.execute("""INSERT INTO historic_book_case_acceptance(case_id,source_book,
  source_chapter_key,source_documented_outcome,source_has_explicit_initial_error,
  metadata_json) VALUES (?,'kaiwu',?,?,?,?)""",
  (cid,CHAPTER,"book_explicit_initial_error_and_later_disclosure" if e.get("explicit_error")
   else "book_reported_verbatim_partial_or_full_outcome",
   int(bool(e.get("explicit_error"))),j(proto)))
 for domain in e["facets"]:
  db.execute("""INSERT INTO unified_case_domain_facets(case_id,domain_id,
   source_chapter_key,primary_domain,note) VALUES (?,?,?,?,?)""",
   (cid,domain,CHAPTER,int(domain=="marriage"),e["nuance"]))
 db.execute("""INSERT INTO crossbook_relationship_cast_witnesses(chapter_key,
  case_id,cast_key,printed_chart_start,printed_chart_end,raw_chart_sha256,
  source_cast_header_line,source_header_original,note)
  VALUES (?,?,'primary',?,?,?,?,?,?)""",
  (CHAPTER,cid,e["chart"],e["chart_end"],e["chart_sha256"],e["meta"],
   src(L,e["meta"]),e["nuance"]))
 add_phase(db,L,e,"known_at_cast","known_before",*e["question"])
 add_phase(db,L,e,"first_complete_book_chart","original_printed_chart",e["chart"],e["chart_end"])
 for z,line in enumerate(e["predictions"],1):
  add_phase(db,L,e,f"author_prediction_{z:02}","author_first_reading",line,line)
 for z,line in enumerate(e["feedback"],1):
  add_phase(db,L,e,f"reported_feedback_{z:02}","book_subject_report_or_outcome",line,line)
 for z,(a,b,kind) in enumerate(e["extra_phases"],1):
  add_phase(db,L,e,f"extra_{z:02}",kind,a,b)
 if e["number"]==6:
  add_phase(db,L,e,"user_explicitly_rejects_initial","initial_prediction_rejected",297,299,
    {"misidentified_crush_as_woman":True,"not_positive_training_example":True})
  add_phase(db,L,e,"later_private_disclosure","information_first_available_later",301,301,
    {"person_reports_attraction_to_man":True,"sexual_orientation_not_medical_diagnosis":True})
  db.execute("""INSERT INTO crossbook_relationship_source_errors(chapter_key,case_id,
    initial_prediction_line,explicit_user_rejection_line,later_user_disclosure_line,
    retrospective_author_response_line,initial_original,explicit_rejection_original,
    later_disclosure_original,later_reinterpretation_original)
    VALUES (?,?,293,297,301,305,?,?,?,?)""",
    (CHAPTER,cid,src(L,293,295),src(L,297,299),src(L,301),src(L,305)))
  for key,line,explanation in (
    ("birth_time_chart_omitted",261,"Only mentions separate birth-time chart; no printed palace fields"),
    ("followup_2000_09_22_chart_omitted",303,"Full second letter night cast explicitly says 格局略")):
   db.execute("""INSERT INTO crossbook_relationship_missing_casts(chapter_key,
    case_id,cast_key,source_line,original_source_claim) VALUES (?,?,?,?,?)""",
    (CHAPTER,cid,key,line,src(L,line)))
 for pc in e["cells"]:
  central=pc["palace"]==5
  db.execute("""INSERT INTO crossbook_relationship_literal_palaces(chapter_key,
   case_id,cast_key,palace,line_start,line_end,palace_label_original,
   deity_original,door_original,star_original,literal_original,literal_sha256)
   VALUES (?,?,'primary',?,?,?,?,?,?,?,?,?)""",
   (CHAPTER,cid,pc["palace"],pc["start_line"],pc["end_line"],pc["palace_label"],
    pc["deity"],pc["door"],pc["star"],pc["literal"],pc["sha256"]))
  db.execute("""INSERT INTO historical_chart_cells(case_id,palace,source_line,
   palace_label_raw,deity_raw,door_position_raw,star_position_raw,source_status)
   VALUES (?,?,?,?,?,?,?,'exact_original_marriage_book_not_recast')""",
   (cid,pc["palace"],pc["source_line_unique"],pc["palace_label"],
    pc["deity"],pc["door"],pc["star"]))
  db.execute("""INSERT INTO historical_palace_standardization(case_id,cast_key,
   palace,center_stem,source_of_center_stem,standard_deity,standard_door,
   standard_star,normalized_status,original_raw_integrity_checked,method_reference,
   derived_host_palace,derived_host_source)
   VALUES (?,'primary',?,?,?,?,?,?,?,1,?,?,?)""",
   (cid,pc["palace"],pc["door"] if central else None,
    "literal_center_single_stem_only" if central else "not_center",
    None if central else pc["deity"],
    None if central else pc["door"],None if central else pc["star"],
    "center_is_original_stem_no_deity_door_star" if central
     else "exact_three_row_source_original",
    "kaiwu_marriage_source_no_guessed_elements",
    2 if central else None,
    "traditional_center_kun2_derived_not_printed" if central else None))
 for z,line in enumerate(e["step"],1):
  literal=src(L,line)
  phase=("author_original_reasoning_with_initial_miss" if e["number"]==6 else
   "book_author_source_reasoning")
  meta={"source_line":line,"phase":phase,
    "book_case_accepted_no_user_manual_check":True,
    "source_error_cannot_be_positive_example":bool(e.get("explicit_error")),
    "source_case_id":cid,"external_verification_not_claimed":True}
  db.execute("""INSERT INTO historical_case_reasoning(case_id,step_number,source_line,
   author_analysis_original,short_method_topic,metadata_json)
   VALUES (?,?,?,?,?,?)""",(cid,z,line,literal,phase,j(meta)))
  db.execute("""INSERT INTO historical_case_reasoning_trace(case_id,step_number,
   source_line,evidence_json,review_status,positive_training_eligible)
   VALUES (?,?,?,?,'book_case_accepted_preserve_original_result',0)""",
   (cid,z,line,j(meta)))
  concept=f"marriage:kaiwu:case{e['number']:02}:reasoning{z:02}"
  db.execute("""INSERT INTO semantic_assertions(chapter_key,concept_id,kind,
   relation,source_start_line,source_end_line,metadata_json,
   original_excerpt,review_status) VALUES (?,?,?,?,?,?,?,?,?)""",
   (CHAPTER,concept,"case_author_original_reasoning","book_source_accepted",
    line,line,j(meta),literal,"draft"))
  db.execute("""INSERT INTO cross_book_concept_tracks(chapter_key,concept_id,
   source_start_line,source_end_line,source_section_id,source_sha256,excerpt_sha256,
   track_id,relation_to_prior,comparison_state,normalized_json,review_status)
   VALUES (?,?,?,?,?,?,?,?,?,'book_case_accepted_not_external_scientific_test',?,'draft')""",
   (CHAPTER,concept,line,line,sid,SOURCE_SHA,h(literal.encode("utf-8")),
    "kaiwu:marriage:source_v1:author_reasoning","additional_exposition",j(meta)))
 db.execute("""INSERT INTO historical_case_review_audit(case_id,original_steps,
  mechanical_step_trace,human_complete_step_chains,review_status,warning)
  VALUES (?,?,?,0,'user_accepts_original_book_case_no_per_case_review',?)""",
  (cid,len(e["step"]),len(e["step"]),e["nuance"]))
 if e.get("explicit_error"):
  db.execute("""INSERT INTO historical_case_book_verdicts(event_family_id,
   primary_case_id,verdict,explicit_source_correction,source_correction_lines_json,
   feedback_source_lines_json,independent_external_verification,app_output_protocol,
   evidence_review_status,note)
   VALUES (?,?,'author_book_error_explicit',1,?,?, 'not_verified',
    'single_answer_for_one_cast','user_accepts_historical_book_error',?)""",
   (cid,cid,j([299,301,303,305]),j(e["feedback"]),e["nuance"]))
 else:
  db.execute("""INSERT INTO historical_case_book_verdicts(event_family_id,
   primary_case_id,verdict,explicit_source_correction,source_correction_lines_json,
   feedback_source_lines_json,independent_external_verification,app_output_protocol,
   evidence_review_status,note)
   VALUES (?,?,'author_book_success_default',0,'[]',?,
    'not_verified','single_answer_for_one_cast',
    'user_accepts_historical_book_outcome_with_scope',?)""",
   (cid,cid,j(e["feedback"]),e["nuance"]))
def build(base,source,output,index_dir):
 base,source,output,index_dir=map(Path,(base,source,output,index_dir))
 if output.exists():raise ValueError("Never overwrite already published full SQLite")
 if h(base.read_bytes())!=BASE_SHA:raise ValueError("Must use exactly prior full 28-section archive")
 raw=source.read_bytes();L=parse_original(raw);events=parsed(L)
 output.parent.mkdir(parents=True,exist_ok=True)
 with sqlite3.connect("file:"+str(base)+"?mode=ro",uri=True) as old,sqlite3.connect(output) as db:
  old.backup(db)
  db.executescript((ROOT/"schema/migrations/023_kaiwu_marriage_unified_case_provenance.sql").read_text("utf-8"))
  db.execute("PRAGMA foreign_keys=ON")
  with db:
   if db.execute("SELECT COUNT(*) FROM sections WHERE book_id='kaiwu'").fetchone()[0]!=7:
    raise ValueError("All seven previous Kaiwu source sections missing")
   if db.execute("SELECT 1 FROM sections WHERE book_id='kaiwu' AND section_key=?",(SECTION,)).fetchone():
    raise ValueError("Source section already imported")
   db.execute("""INSERT INTO sections(book_id,section_key,title,original_text,
    sha256,content_version,reviewed) VALUES ('kaiwu',?,?,?,?,1,1)""",
    (SECTION,TITLE,raw.decode("utf-8"),SOURCE_SHA))
   sid=db.execute("SELECT last_insert_rowid()").fetchone()[0]
   db.execute("""INSERT INTO chapter_knowledge(chapter_key,book_id,title,
    source_sha256,source_length_bytes,knowledge_version,review_status)
    VALUES (?,'kaiwu',?,?,?,'1','approved')""",(CHAPTER,TITLE,SOURCE_SHA,len(raw)))
   for e in events:add_event(db,L,sid,e)
   # Different subject question/datetime for SAME woman: source says previous
   # marriage court verdict was verified before June 4 courtship inquiry.
   db.execute("""INSERT INTO crossbook_relationship_event_links(chapter_key,
    case_id,related_case_id,relationship,evidence_original,evidence_source_line)
    VALUES (?,?,?,?,?,97)""",
    (CHAPTER,"kaiwu.marriage.case03","kaiwu.marriage.case02",
     "same_daughter_and_parent_different_dated_marital_questions",src(L,97)))
   db.execute("""INSERT INTO cross_book_example_references(source_chapter_key,
    source_line,target_book_id,target_printed_page,reference_key,metadata_json,
    verified_target_case_id)
    VALUES (?,259,'shenqi','unspecified_in_source',?,?,NULL)""",
    (CHAPTER,"kaiwu:marriage:reader_wrote_after_shenqi_book",
     j({"source_line":259,"type":"general_readership_not_specific_prior_case",
        "new_historical_event":False,"user_book_case_accepted":True})))
   db.execute("""INSERT INTO chapter_archival_versions(archive_label,
    baseline_sha256,new_db_sha256,contains_complete_private_copyright_source,
    snapshot_type,created_utc,repo_public_archive_policy)
    VALUES (?,?,NULL,1,'unified_marriage_six_cases_6_charts_and_explicit_initial_error',
    '2026-10-20','user_authorized_public_full_sqlite_versions')""",
    ("shenqi21_kaiwu_marriage02_127_book_cases",BASE_SHA))
  all_prior_rows_preserved(old,db)
  if db.execute("PRAGMA integrity_check").fetchone()[0]!="ok" or db.execute("PRAGMA foreign_key_check").fetchall():
   raise ValueError("New book source foreign key/integrity failed")
  expected={"sections":29,"cases":127,
    "historical_chart_cells":1134,
    "historical_case_additional_casts":17,
    "historical_case_additional_cast_cells":153,
    "historical_palace_standardization":1287,
    "historical_case_reasoning":639,
    "historical_case_reasoning_trace":639,
    "semantic_assertions":2313,
    "cross_book_concept_tracks":1056,
    "cross_book_example_references":44,
    "historic_book_case_acceptance":19,
    "crossbook_relationship_cast_witnesses":6,
    "crossbook_relationship_literal_palaces":54,
    "crossbook_relationship_event_links":1,
    "crossbook_relationship_missing_casts":2,
    "crossbook_relationship_source_errors":1,
    "unified_case_domain_facets":sum(len(x["facets"]) for x in events)}
  got={k:db.execute('SELECT COUNT(*) FROM "'+k+'"').fetchone()[0] for k in expected}
  if got!=expected:raise ValueError(("Unexpected copied + new counts",got,expected))
  if db.execute("SELECT COUNT(*) FROM historical_case_book_verdicts WHERE verdict='author_book_error_explicit'").fetchone()[0]!=8:
   raise ValueError("New original error plus old seven errors must remain")
  if db.execute("SELECT COUNT(*) FROM cases c JOIN sections s ON c.section_id=s.section_id WHERE c.domain_id='marriage' AND s.book_id='kaiwu'").fetchone()[0]!=6:
   raise ValueError("All six must share existing Shenqi marriage domain")
  if db.execute("SELECT COUNT(*) FROM cases WHERE domain_id='marriage'").fetchone()[0]<12:
   raise ValueError("Must merge same category six Shenqi old + six Kaiwu new")
  if db.execute("SELECT COUNT(*) FROM crossbook_relationship_missing_casts WHERE must_never_backfill=1").fetchone()[0]!=2:
   raise ValueError("Keep author's unprinted birth and follow-up panels absent")
  if db.execute("SELECT COUNT(*) FROM historical_case_reasoning_trace WHERE positive_training_eligible=1").fetchone()[0]!=0:
   raise ValueError("No auto promotion of author interpretation causality")
  db.execute("VACUUM");db.commit()
  if db.execute("PRAGMA integrity_check").fetchone()[0]!="ok" or db.execute("PRAGMA foreign_key_check").fetchall():
   raise ValueError("Final version SQLite integrity failed")
 index_dir.mkdir(parents=True,exist_ok=True)
 manifest={"schema":"wengua_kaiwu_marriage_unified_domain_book_case_v1",
  "source_title":TITLE,"book_id":"kaiwu","chapter_key":CHAPTER,
  "source_sha256":SOURCE_SHA,"source_bytes":len(raw),
  "source_lines":len(L),"source_numbered_cases":6,
  "new_unique_historical_events":6,"new_actual_printed_qimen_casts":6,
  "all_literal_new_past_palace_cells":54,"new_author_original_steps":26,
  "existing_shenqi_domain_id":"marriage",
  "same_woman_different_case_link_count":1,
  "new_cross_domain_facets":sum(len(x["facets"]) for x in events),
  "case6_omitted_original_casts":2,
  "case6_original_first_prediction_error":True,
  "case6_homosexuality_not_a_disease":True,
  "new_accepted_book_cases_without_manual_approval":6,
  "prior_seven_explicit_author_errors_retained":True,
  "total_explicit_author_book_prediction_errors":8,
  "book_counts":{"shenqi":21,"kaiwu":8},
  "total_source_sections":29,"total_historical_cases":127,
  "total_original_historical_printed_casts":143,
  "total_historical_palace_standardization":1287,
  "total_historical_author_reasoning_steps":639,
  "all_prior_table_rows_unchanged":True,
  "source_accepted_not_external_scientific_validation":True,
  "parent_sha256":BASE_SHA,
  "output_sha256":h(output.read_bytes()),
  "counts":got}
 def write(p,value):
  (index_dir/p).write_text(json.dumps(value,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 write("chapter_manifest.json",manifest)
 write("case_index.json",{"schema":"unified_shenqi_kaiwu_marriage_cases_v1",
  "source_sha256":SOURCE_SHA,
  "same_person_not_same_event":["kaiwu.marriage.case02","kaiwu.marriage.case03"],
  "cases":[{k:v for k,v in e.items() if k!="cells"} for e in events]})
 write("original_palace_witnesses.json",{"source_sha256":SOURCE_SHA,
  "charts":[{"case_id":e["id"],"start":e["chart"],"printed_palaces":e["cells"]}
            for e in events]})
 write("domain_facets.json",{"source_sha256":SOURCE_SHA,
  "cases":[{"case_id":e["id"],"primary_domain":"marriage",
            "facets":e["facets"],"same_person_linked_not_merged":e["number"] in (2,3)}
            for e in events]})
 write("source_audit.json",{"source_sha256":SOURCE_SHA,
  "case6_first_incorrect_guess_source_lines":[293,295,297,299],
  "case6_later_disclosure_and_reinterpretation_lines":[301,303,305],
  "case6_published_one_chart_two_additional_charts_unprinted":True,
  "case6_orientation_never_treated_as_disease":True,
  "case2_3_same_person_but_different_dated_question":True,
  "case4_future_job_time_not_followed_up":True,
  "case5_future_remarriage_business_not_followed_up":True,
  "all_cases_user_accepted_no_manual_review":True,
  "prior_version_source_history_and_all_book_errors_intact":True,
  "none_book_results_independently_medically_verified":True})
 return manifest
def main():
 p=argparse.ArgumentParser()
 for key in ("base","source","output","index-dir"):p.add_argument("--"+key,required=True)
 a=p.parse_args();print(json.dumps(build(a.base,a.source,a.output,a.index_dir),ensure_ascii=False,indent=2))
if __name__=="__main__":main()
