"""Kaiwu Chapter Two Section Three: 3 exam cases, 3 printed casts, 4 candidates.

Append-only from the SHA-pinned 130-event full SQLite. Merge with Shenqi
education domain; preserve source grades, school direction partial misses, and
self-funded vs formal admission. No per-case user review required.
"""
from __future__ import annotations
import argparse,hashlib,json,re,sqlite3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE_SHA="ff1e066f53674abcfed14e0bdaeafcb1fe4613e88122a43f8375ba6b3157f5a2"
SOURCE_SHA="8c72fe2fa37efdd422510b9c762c6890b3ce0116ee3ed3b72c5a19f1b63f3b05"
BASE_NAME="WenguaApp_神奇之门21章_开悟之门9节_130案例_完整研究库.sqlite3"
NEW_NAME="WenguaApp_神奇之门21章_开悟之门10节_133案例_完整研究库.sqlite3"
CHAPTER="kaiwu/education_prediction_ch02_section03/v1"
SECTION="education_prediction_ch02_section03"
TITLE="第二章 日常百事预测评析 / 第三节 求学考试预测(共3例)"
PL=(4,9,2,3,5,7,8,1,6)
LABELS=("巽4","离9","坤2","震3","中5","兑7","艮8","坎1","乾6")
SPECS=[
 {"key":"pan_son","id":"kaiwu.education.19990717.pan_son",
  "title":"潘副所长儿子第三次高考与学校志愿",
  "source":(5,60),"q":[7,15],"chart":29,"calendar":27,"before":(7,21),
  "prediction":[13,17,21],"feedback":[23],"reasoning":[(45,47),(49,55),(57,59)],
  "after":[(25,27)],"date":"1999-07-17","hour":"壬午",
  "context":"Estimated 540 and reported exactly 540; author admits imprecision in school-direction reasoning after result; old Shenqi Dai-surname child is a reference, not this event"},
 {"key":"wang_daughter","id":"kaiwu.education.19990702.wang_daughter",
  "title":"王亚萍女儿美术生文化课高考及学校方向",
  "source":(61,118),"q":[63],"chart":69,"calendar":67,"before":(63,97),
  "prediction":[83,87,95],"feedback":[99,101,103,105,107],
  "reasoning":[(111,111),(113,113),(115,115),(117,117)],
  "after":[(109,109)],"date":"1999-07-02","hour":"辛巳",
  "context":"Predicted about 350; book reports 342 and formal admission to Hebei University north of Shijiazhuang, explicitly admits earlier south prediction wrong"},
 {"key":"sisters","id":"kaiwu.education.20000711.zhang_sisters",
  "title":"苏恩两名女儿同一次问事：普通录取与自费入学",
  "source":(119,151),"q":[121],"chart":125,"calendar":123,"before":(121,123),
  "prediction":[143,147,149],"feedback":[151],"reasoning":[(141,143),(145,147)],
  "after":[],"date":"2000-07-11","hour":"壬午",
  "context":"Two different sisters evaluated by the ONE actual printed historical chart; elder failed normal admission but self-financed university; younger formally admitted; street diviner is not a second printed Qimen chart"}
]
CANDIDATES=[
 ("pan_son","pan_son","1978 戊午",21,23,"exam_540_university_offered"),
 ("wang_daughter","wang_daughter","1981 辛酉",87,103,"approx_350_actual_342_formal_art_admission"),
 ("sisters","elder_daughter","1978 戊午",143,151,"ordinary_exam_not_admitted_self_funded_college"),
 ("sisters","younger_daughter","1981 辛酉",147,151,"ordinary_formal_college_admission")
]
CLAIMS=[
 ("pan_son","score_540","score",21,23,"book_reported_match"),
 ("pan_son","direction_after_result","college_location_direction",21,59,"book_explicit_partial_error"),
 ("wang_daughter","score_350_342","score_approximation",87,103,"book_reported_match"),
 ("wang_daughter","wrong_south_college","college_location_direction",95,107,"book_explicit_partial_error"),
 ("sisters","elder_normal_vs_self_funded","ordinary_versus_paid_admission",143,151,"book_reported_match"),
 ("sisters","younger_formal_admitted","formal_admission",147,151,"book_reported_match")
]
def digest(b):return hashlib.sha256(b).hexdigest()
def js(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(",",":"))
def span(L,a,b=None):
 b=a if b is None else b
 if not 1<=a<=b<=len(L):raise ValueError(("Invalid source lines",a,b))
 return "\n".join(L[a-1:b])
def read_original(raw):
 if digest(raw)!=SOURCE_SHA:raise ValueError("Original chapter sha256 mismatch")
 L=raw.decode("utf-8").splitlines()
 if len(L)!=151 or L[0]!="第二章 日常百事预测评析" or L[2]!="第三节 求学考试预测(共3例)" or not raw.endswith(b"\n"):
  raise ValueError("Original source truncated")
 if [i for i,x in enumerate(L,1) if x.startswith("(例") ]!=[5,61,119]:raise ValueError("Unexpected example boundaries")
 if [i for i,x in enumerate(L,1) if x.startswith("┌") ]!=[29,69,125]:raise ValueError("Must be 3 printed source charts")
 if not "判断得不够准确" in L[58] or "录取学校的方向就没测准" not in L[106]:
  raise ValueError("Book's two admitted partial school-direction errors lost")
 if not "二女儿被内蒙古工业大学" in L[150]:raise ValueError("Last feedback missing")
 return L
def chart(L,start):
 if not L[start-1].startswith("┌") or not L[start+12-1].startswith("└"):raise ValueError(("Panel corrupt",start))
 rows=[]
 for band in range(3):
  base=start+1+band*4
  layer=[]
  for z in range(3):
   line=L[base+z-1]
   if not (line.startswith("│") and line.endswith("│")):raise ValueError(("Source line boundary",base+z))
   parts=[v.strip() for v in line.split("│")[1:-1]]
   if len(parts)!=3:raise ValueError(("Not 3 original columns",base+z))
   layer.append(parts)
  if band<2 and not L[base+2].startswith("├"):raise ValueError("Original horizontal separator missing")
  for col in range(3):
   i=band*3+col;pal=PL[i];head=layer[0][col];label=LABELS[i]
   if not head.startswith(label):raise ValueError(("Palace label changed",pal,head))
   god=head[len(label):].strip();door=layer[1][col];star=layer[2][col]
   if pal==5 and (god or not door or star):raise ValueError("Central printed stem not regular star/gate/god")
   if pal!=5 and (not god or not door or not star):raise ValueError(("Original side-palace missing",pal))
   literal="\n".join((head,door,star))
   rows.append({"palace":pal,"start":base,"end":base+2,
    "unique_line":base+col,"label":label,"god":god,"door":door,"star":star,
    "original":literal,"sha":digest(literal.encode("utf-8"))})
 if len(rows)!=9 or sorted(p["palace"] for p in rows)!=list(range(1,10)):raise ValueError("Not nine literal palaces")
 return rows
def events(L):
 out=[]
 for s in SPECS:
  cells=chart(L,s["chart"])
  if s["key"]=="sisters":
   if next(c for c in cells if c["palace"]==4)["star"]!="禽芮丙":
    raise ValueError("Do not alter original joined Tianqin/Tianrui expression")
  out.append({**s,"cells":cells,"grid_sha":digest(span(L,s["chart"],s["chart"]+12).encode("utf-8"))})
 if len(out)!=3 or sum(len(e["reasoning"]) for e in out)!=9:raise ValueError("Three cases/nine source reasoning groups")
 return out
def compare_old(old,db):
 for (table,) in old.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"):
  cols=[col[1] for col in old.execute('PRAGMA table_info("'+table+'")')]
  sql=",".join('"'+name+'"' for name in cols)
  prior=list(old.execute('SELECT '+sql+' FROM "'+table+'"'))
  current=set(db.execute('SELECT '+sql+' FROM "'+table+'"'))
  if not all(x in current for x in prior):raise ValueError("Old book source row changed: "+table)
def add_phase(db,L,e,key,kind,a,b,meta=None):
 original=span(L,a,b)
 db.execute("""INSERT INTO education_crossbook_source_phases(chapter_key,case_id,phase_key,
  phase_kind,source_start,source_end,original_text,sha256,metadata_json)
  VALUES (?,?,?,?,?,?,?,?,?)""",(CHAPTER,e["id"],key,kind,a,b,original,
   digest(original.encode("utf-8")),js({"source_is_accepted_book":True,
   "after_feedback_cannot_be_first_prediction":kind.startswith("after_"),
   "external_validation_claimed":False,**(meta or {})})))
def insert_case(db,sid,L,e):
 cid=e["id"]
 known=span(L,e["q"][0],e["q"][-1])
 steps="\n\n".join(span(L,*item) for item in e["reasoning"])
 judgments="\n".join(span(L,n) for n in e["prediction"])
 feedback="\n".join(span(L,n) for n in e["feedback"])
 proto={"source_chapter":CHAPTER,"source_case":e["key"],"casting_date":e["date"],"hour":e["hour"],
   "separate_issues_same_cast":e["key"]=="sisters",
   "source_note":e["context"],"user_accepts_book_record_no_manual_review":True,
   "book_source_not_independently_proven":True,
   "direction_partial_error":e["key"]!="sisters",
   "source_analysis_was_explained_after_feedback":e["key"]!="sisters"}
 db.execute("""INSERT INTO cases(case_id,section_id,event_family_id,domain_id,known_before,
 author_yongshen_steps,author_judgment,later_feedback,reviewed)
 VALUES (?,?,?,'education',?,?,?,?,1)""",(cid,sid,cid,known,steps,judgments,feedback))
 db.execute("""INSERT INTO historical_case_protocol(case_id,completeness,published_chart_verification,
 feedback_independently_verified,eligible_blind_test,case_source_sha256,metadata_json)
 VALUES (?,'full_original_three_row_9_palace_book_story','book_literal_no_recast',0,1,?,?)""",
 (cid,SOURCE_SHA,js(proto)))
 db.execute("""INSERT INTO historic_book_case_acceptance(case_id,source_book,
  source_chapter_key,source_documented_outcome,source_has_explicit_initial_error,metadata_json)
  VALUES (?,'kaiwu',?,'mixed_claim_level_results_preserve_partial_school_direction_error',?,?)""",
 (cid,CHAPTER,int(e["key"]!="sisters"),js(proto)))
 db.execute("""INSERT INTO unified_case_domain_facets(case_id,domain_id,
  source_chapter_key,primary_domain,note) VALUES (?,'education',?,1,?)""",
 (cid,CHAPTER,e["context"]))
 db.execute("""INSERT INTO education_crossbook_source_casts(chapter_key,case_id,
  source_start_line,source_end_line,source_sha256,calendar_line,original_calendar)
 VALUES (?,?,?,?,?,?,?)""",
 (CHAPTER,cid,e["chart"],e["chart"]+12,e["grid_sha"],e["calendar"],span(L,e["calendar"])))
 add_phase(db,L,e,"question","known_before_book_prediction",e["q"][0],e["q"][-1])
 add_phase(db,L,e,"original_chart","printed_original_cast",e["chart"],e["chart"]+12)
 for i,n in enumerate(e["prediction"],1):
  add_phase(db,L,e,f"prediction_{i}","book_initial_prediction",n,n)
 for i,n in enumerate(e["feedback"],1):
  add_phase(db,L,e,f"feedback_{i}","book_reported_result",n,n)
 for i,(a,b) in enumerate(e["reasoning"],1):
  add_phase(db,L,e,f"analysis_{i}","after_outcome_author_explanation" if e["key"]!="sisters"
    else "book_author_numbered_explanation",a,b)
 if e["key"]=="sisters":
  add_phase(db,L,e,"street_fortune_teller","other_person_divination_not_an_original_qimen_cast",121,121)
  add_phase(db,L,e,"two_student_outcome","two_people_one_qimen_cast",151,151,
    {"elder_self_funded_vs_younger_normal":True})
 for c in e["cells"]:
  center=c["palace"]==5
  db.execute("""INSERT INTO education_crossbook_source_palaces(chapter_key,case_id,palace,
   source_start_line,source_end_line,header_raw,god_raw,door_raw,star_raw,original_text,source_sha256)
   VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
   (CHAPTER,cid,c["palace"],c["start"],c["end"],c["label"],c["god"],c["door"],c["star"],c["original"],c["sha"]))
  db.execute("""INSERT INTO historical_chart_cells(case_id,palace,source_line,palace_label_raw,
   deity_raw,door_position_raw,star_position_raw,source_status)
   VALUES (?,?,?,?,?,?,?,'literal_book_education_chart_not_recast')""",
   (cid,c["palace"],c["unique_line"],c["label"],c["god"],c["door"],c["star"]))
  db.execute("""INSERT INTO historical_palace_standardization(case_id,cast_key,palace,
   center_stem,source_of_center_stem,standard_deity,standard_door,standard_star,
   normalized_status,original_raw_integrity_checked,method_reference,derived_host_palace,derived_host_source)
   VALUES (?,'primary',?,?,?,?,?,?,?,1,?,?,?)""",
   (cid,c["palace"],c["door"] if center else None,
    "source_center_only_original_stem" if center else "not_center",
    None if center else c["god"],None if center else c["door"],None if center else c["star"],
    "center_original_no_regular_god_door_star" if center else "literal_original_education_source",
    "kaiwu_education_book_exact_cast",2 if center else None,
    "host_kun2_rule_derived_not_printed_center" if center else None))
 for ix,(a,b) in enumerate(e["reasoning"],1):
  literal=span(L,a,b)
  meta={"source_book":"kaiwu","kind":"source_author_numbered_explanation",
   "source_before_after":"retrospective_after_feedback" if e["key"]!="sisters" else "book_author_explanation",
   "case_id":cid,"book_case_accepted":True,"not_independent_empirical_validation":True}
  db.execute("""INSERT INTO historical_case_reasoning(case_id,step_number,source_line,
   author_analysis_original,short_method_topic,metadata_json) VALUES (?,?,?,?,?,?)""",
   (cid,ix,a,literal,meta["kind"],js(meta)))
  db.execute("""INSERT INTO historical_case_reasoning_trace(case_id,step_number,source_line,
   evidence_json,review_status,positive_training_eligible) VALUES (?,?,?,?,
   'user_accepted_book_case_preserve_source_claim_boundaries',0)""",(cid,ix,a,js(meta)))
  concept=f"education:kaiwu:{e['key']}:reasoning:{ix}"
  db.execute("""INSERT INTO semantic_assertions(chapter_key,concept_id,kind,relation,
   source_start_line,source_end_line,metadata_json,original_excerpt,review_status)
   VALUES (?,?,?,?,?,?,?,?,'draft')""",
   (CHAPTER,concept,"book_education_numbered_reasoning","additional_exposition",
    a,b,js(meta),literal))
  db.execute("""INSERT INTO cross_book_concept_tracks(chapter_key,concept_id,source_start_line,
   source_end_line,source_section_id,source_sha256,excerpt_sha256,track_id,relation_to_prior,
   comparison_state,normalized_json,review_status)
   VALUES (?,?,?,?,?,?,?,?,?,'accepted_book_case_claim_without_external_validation',?,'draft')""",
   (CHAPTER,concept,a,b,sid,SOURCE_SHA,digest(literal.encode("utf-8")),
    "kaiwu:education:book_v1:author_reasoning","additional_exposition",js(meta)))
 db.execute("""INSERT INTO historical_case_review_audit(case_id,original_steps,mechanical_step_trace,
  human_complete_step_chains,review_status,warning)
  VALUES (?,?,?,0,'user_accepts_book_case_without_manual_approval',?)""",
  (cid,len(e["reasoning"]),len(e["reasoning"]),e["context"]))
 db.execute("""INSERT INTO historical_case_book_verdicts(event_family_id,primary_case_id,verdict,
   explicit_source_correction,source_correction_lines_json,feedback_source_lines_json,
   independent_external_verification,app_output_protocol,evidence_review_status,note)
   VALUES (?,?,'author_book_success_default',?,? ,?,'not_verified','single_answer_for_one_cast',
   'user_accepted_book_mixed_claims',?)""",
   (cid,cid,int(e["key"]!="sisters"),
    js([59] if e["key"]=="pan_son" else [107,117] if e["key"]=="wang_daughter" else []),
    js(e["feedback"]),e["context"]))
def add_candidate(db,L,events,key,who,birth,pred,feedback,result):
 cid=next(e["id"] for e in events if e["key"]==key)
 info={"user_book_case_accepted":True,"same_cast_two_candidates":key=="sisters",
 "ordinary_and_self_funded_distinct":key=="sisters","source_not_external_validation":True}
 db.execute("""INSERT INTO education_crossbook_candidates(chapter_key,case_id,candidate_key,
   birth_year_original,prediction_line,source_prediction,feedback_line,source_reported_outcome,
   result_class,metadata_json) VALUES (?,?,?,?,?,?,?,?,?,?)""",
   (CHAPTER,cid,who,birth,pred,span(L,pred),feedback,span(L,feedback),result,js(info)))
def add_claim(db,L,events,key,claim,kind,pred,report,status):
 cid=next(e["id"] for e in events if e["key"]==key)
 db.execute("""INSERT INTO education_crossbook_book_claims(chapter_key,case_id,claim_key,
  claim_type,initial_prediction_line,initial_original,later_report_line,later_original,source_verdict)
  VALUES (?,?,?,?,?,?,?,?,?)""",
  (CHAPTER,cid,claim,kind,pred,span(L,pred),report,span(L,report),status))
def build(base,source,output,index_dir):
 base,source,output,index_dir=map(Path,(base,source,output,index_dir))
 if output.exists():raise ValueError("Never overwrite a prior full immutable database")
 if digest(base.read_bytes())!=BASE_SHA:raise ValueError("Parent must be latest 30-source SHA-pinned full database")
 raw=source.read_bytes();L=read_original(raw);es=events(L)
 output.parent.mkdir(parents=True,exist_ok=True)
 with sqlite3.connect("file:"+str(base)+"?mode=ro",uri=True) as old,sqlite3.connect(output) as db:
  old.backup(db)
  db.executescript((ROOT/"schema/migrations/025_kaiwu_education_shared_domain.sql").read_text("utf-8"))
  db.execute("PRAGMA foreign_keys=ON")
  with db:
   if db.execute("SELECT COUNT(*) FROM sections WHERE book_id='kaiwu'").fetchone()[0]!=9:raise ValueError("Missing 9 prior Kaiwu source sections")
   db.execute("""INSERT INTO sections(book_id,section_key,title,original_text,sha256,content_version,reviewed)
    VALUES ('kaiwu',?,?,?,?,1,1)""",(SECTION,TITLE,raw.decode("utf-8"),SOURCE_SHA))
   sid=db.execute("SELECT last_insert_rowid()").fetchone()[0]
   db.execute("""INSERT INTO chapter_knowledge(chapter_key,book_id,title,source_sha256,
     source_length_bytes,knowledge_version,review_status)
    VALUES (?,'kaiwu',?,?,?,'1','approved')""",(CHAPTER,TITLE,SOURCE_SHA,len(raw)))
   for e in es:insert_case(db,sid,L,e)
   for row in CANDIDATES:add_candidate(db,L,es,*row)
   for row in CLAIMS:add_claim(db,L,es,*row)
   db.execute("""INSERT INTO cross_book_example_references(source_chapter_key,source_line,
    target_book_id,target_printed_page,reference_key,metadata_json,verified_target_case_id)
    VALUES (?,11,'shenqi','not_specified_in_source',?,?,NULL)""",
    (CHAPTER,"kaiwu:education:old_dai_son_reference",
     js({"source_phrase":span(L,11),"candidate_old_case":"shenqi.education.father_son_university",
       "unverified_same_person_not_duplicate_new_event":True})))
   db.execute("""INSERT INTO chapter_archival_versions(archive_label,baseline_sha256,new_db_sha256,
    contains_complete_private_copyright_source,snapshot_type,created_utc,repo_public_archive_policy)
    VALUES (?,?,NULL,1,'three_education_events_four_students_three_source_casts_mixed_claims',
     '2026-10-20','user_authorized_public_full_sqlite_versions')""",
    ("shenqi21_kaiwu_education03_133cases",BASE_SHA))
  compare_old(old,db)
  if db.execute("PRAGMA integrity_check").fetchone()[0]!="ok" or db.execute("PRAGMA foreign_key_check").fetchall():
   raise ValueError("New sqlite before VACUUM has integrity failure")
  expected={"sections":31,"cases":133,"historical_chart_cells":1188,
    "historical_palace_standardization":1341,
    "historical_case_additional_casts":17,"historical_case_additional_cast_cells":153,
    "historical_case_reasoning":661,"historical_case_reasoning_trace":661,
    "semantic_assertions":2335,"cross_book_concept_tracks":1078,
    "cross_book_example_references":45,"historic_book_case_acceptance":25,
    "unified_case_domain_facets":18,"education_crossbook_source_casts":3,
    "education_crossbook_source_palaces":27,"education_crossbook_candidates":4,
    "education_crossbook_book_claims":6}
  actual={t:db.execute('SELECT COUNT(*) FROM "'+t+'"').fetchone()[0] for t in expected}
  if actual!=expected:raise ValueError(("Unexpected parent/new counts",actual,expected))
  if db.execute("SELECT COUNT(*) FROM cases WHERE domain_id='education'").fetchone()[0]<8:
   raise ValueError("All Shenqi five and new Kaiwu three must share education domain")
  if db.execute("SELECT count(*) FROM historical_case_book_verdicts WHERE verdict='author_book_error_explicit'").fetchone()[0]!=8:
   raise ValueError("Previous 8 fully explicit erroneous cases lost")
  if db.execute("SELECT COUNT(*) FROM education_crossbook_book_claims WHERE source_verdict='book_explicit_partial_error'").fetchone()[0]!=2:
   raise ValueError("Two partial source college direction errors must remain")
  if db.execute("SELECT COUNT(*) FROM education_crossbook_candidates WHERE case_id='kaiwu.education.20000711.zhang_sisters'").fetchone()[0]!=2:
   raise ValueError("Two sisters one event must have two outcome subrecords")
  db.execute("VACUUM");db.commit()
  if db.execute("PRAGMA integrity_check").fetchone()[0]!="ok" or db.execute("PRAGMA foreign_key_check").fetchall():
   raise ValueError("Final VACUUM SQLite integrity failure")
 index_dir.mkdir(parents=True,exist_ok=True)
 manifest={"schema":"wengua_kaiwu_shared_education_cases_v1","source_title":TITLE,
  "source_sha256":SOURCE_SHA,"source_bytes":len(raw),"source_lines":len(L),
  "new_source_cases":3,"new_independent_events":3,"new_source_printed_casts":3,
  "new_source_palace_cells":27,"new_numbered_author_explanations":9,
  "new_student_candidate_outcomes":4,"candidate_sisters_one_cast":True,
  "reported_partial_school_direction_errors":2,
  "new_complete_first_prediction_case_errors":0,"previous_global_book_errors_preserved":8,
  "score_case1_predicted_540_actual_540":True,
  "score_case2_predicted_350_actual_342":True,
  "third_older_paid_younger_standard_admission_kept_separate":True,
  "old_shenqi_dai_son_reference_not_new_duplicate":True,
  "user_accepts_all_original_cases_no_individual_review":True,
  "not_external_scientific_verification":True,
  "total_source_sections":31,"book_counts":{"shenqi":21,"kaiwu":10},
  "total_distinct_event_families":133,"total_original_printed_historical_casts":149,
  "parent_sha256":BASE_SHA,"new_database_sha256":digest(output.read_bytes()),
  "all_old_source_rows_unchanged":True,"counts":actual}
 def save(name,x):(index_dir/name).write_text(json.dumps(x,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 save("chapter_manifest.json",manifest)
 save("case_index.json",{"source_sha256":SOURCE_SHA,
  "cases":[{k:v for k,v in e.items() if k!="cells"} for e in es]})
 save("literal_source_palaces.json",{"source_sha256":SOURCE_SHA,
  "charts":[{"case_id":e["id"],"source_grid_start":e["chart"],"nine_literal_palaces":e["cells"]} for e in es]})
 save("candidate_outcomes.json",{"source_sha256":SOURCE_SHA,"four_candidates":[
  {"case_id":next(e["id"] for e in es if e["key"]==key),"key":who,"birth_year":birth,
   "prediction_line":p,"outcome_line":f,"result":result}
  for key,who,birth,p,f,result in CANDIDATES]})
 save("claim_audit.json",{"source_sha256":SOURCE_SHA,
  "source_claims":[{"case":key,"claim_key":claim,"topic":kind,
   "initial_line":p,"report_line":f,"source_verdict":v}
   for key,claim,kind,p,f,v in CLAIMS],
  "two_directional_errors_not_rewriting_true_score_predictions":True,
  "one_parent_one_original_cast_two_students":True,
  "street_diviner_not_additional_qimen_source_chart":True,
  "initial_prediction_distinguished_from_later_explanations":True,
  "no_user_manual_case_approval_required":True,
  "all_parent_database_rows_unchanged":True})
 return manifest
def main():
 ap=argparse.ArgumentParser()
 for n in ("base","source","output","index-dir"):ap.add_argument("--"+n,required=True)
 o=ap.parse_args()
 print(json.dumps(build(o.base,o.source,o.output,o.index_dir),ensure_ascii=False,indent=2))
if __name__=="__main__":main()
