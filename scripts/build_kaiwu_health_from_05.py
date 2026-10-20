"""Same-domain Kaiwu/Shenqi health event importer, preserving 6 distinct source boards.
Five new event families; sixth is a second book witness of Shenqi father case.
No diagnosis/clinical validity claims or training approval.
"""
from __future__ import annotations
import argparse,hashlib,json,sqlite3,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE_SHA="1c445680fa5bb4ea928b5154f7cc8c1f0957681cd94dc062e02ffb601461ba9e"
SOURCE_SHA="49809656b765f4ac858ce68187d911335dd416a2b809bfdfdbf3a3a26ef7303d"
BASE_NAME="WenguaApp_神奇之门21章_开悟之门5章_103案例_完整研究库.sqlite3"
NEW_NAME="WenguaApp_神奇之门21章_开悟之门6节_108案例_完整研究库.sqlite3"
CHAPTER="kaiwu/health_prediction_ch02_section01/v1"
SECTION="health_prediction_ch02_section01"
TITLE="第二章 日常百事预测评析 / 第一节 人体疾病预测(共6例)"
PALS=(4,9,2,3,5,7,8,1,6)
NAMES=("巽四宫","离九宫","坤二宫","震三宫","中五宫","兑七宫","艮八宫","坎一宫","乾六宫")
OLD_FATHER="shenqi.health.19960727.father_illness"
# key,case_id,title,first,last,question_start,end,chart_start,author_steps,
# initial_prediction_span,source_reported_feedback_span,editor_span,
# subdomain,cast_date,hour,source_note
DATA=[
 ("one","kaiwu.health.19960923.nasal_cancer","刘照桂鼻癌住院已知后占病期",
  5,44,7,9,11,[25,27,29,31],(25,31),(33,33),(35,43),
  "human_health","1996-09-23","辛酉",
  "Cancer diagnosis known before cast; reporter of later death is book only"),
 ("two_a","kaiwu.health.19950219.brother_paralysis","原学术论文转述弟病：事前断语未全文重印",
  49,63,49,51,53,[85,87,89],None,(81,81),(83,89),
  "human_health","1995-02-19","癸巳",
  "Prior scholarly-article results narrated before three after-result comparison steps"),
 ("two_b",OLD_FATHER,"与神奇之门1996-07-27测父病为同一事件",
  65,89,65,67,69,[],None,(81,81),(83,89),
  "human_health","1996-07-27","甲申",
  "Same querent daughter, father born 辛酉 1921, same yin7 乙丑/甲申; do not duplicate"),
 ("three_a","kaiwu.health.19980616.hen_illness","母鸡白痢，验看时已死",
  91,119,93,95,97,[111,113,115,117],(117,117),(119,119),(151,157),
  "animal_health","1998-06-16","己巳",
  "Hen already dead on checking at 10:05; exact actual death time unobserved"),
 ("three_b","kaiwu.health.19980621.rooster_illness","公鸡白痢，巽宫原书缺两处天干",
  121,157,121,123,125,[139,141,143,145],(145,145),(147,149),(151,157),
  "animal_health","1998-06-21","戊辰",
  "Two original slots 〔原文未载天干〕 never fill; author 日时 statement unreconciled"),
 ("four","kaiwu.health.19991020.wang_craniotomy","王连明拟开颅手术及次日会诊结果",
  159,211,161,169,171,[187,189,191,193,195,197],(201,201),(209,209),(211,211),
  "human_health","1999-10-20","甲申",
  "Doctors suspected tumour before cast; reported second-day imaging opinion book-only, never skip clinical care")
]
EDITOR=[(39,"health:critical_symbol_combo"),(41,"health:timing_clash_join_grave"),
 (43,"health:yongshen_news_time_day_stem"),
 (85,"health:comparative_inner_outer_yin_yang"),
 (87,"health:comparative_age_birth_year"),
 (89,"health:comparative_month_strength"),
 (153,"health:editor_animal_health_cultural_claim"),
 (155,"health:animal_day_stem_vs_hour_stem"),
 (157,"health:timing_extreme_strength_claim"),
 (185,"health:doctor_tianxin_yi_birth_year")]
def hx(b):return hashlib.sha256(b).hexdigest()
def js(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":"))
def text(lines,a,b=None):
 b=a if b is None else b
 if not 1<=a<=b<=len(lines):raise ValueError(("Invalid original line span",a,b))
 return "\n".join(lines[a-1:b])
def original(raw):
 if hx(raw)!=SOURCE_SHA:raise ValueError("Wrong exact uploaded health SHA")
 lines=raw.decode("utf-8").splitlines()
 if len(lines)!=211 or lines[0]!="第二章 日常百事预测评析" or lines[2]!="第一节 人体疾病预测(共6例)":
  raise ValueError("Missing six-case source section boundary")
 if not raw.endswith(b"\n") or not lines[-1].endswith("劲头也更足了。"):
  raise ValueError("Original final paragraph truncated")
 for n,k in ((5,"(例一)"),(45,"(例二)"),(49,"A、"),(65,"B、"),
             (91,"(例三)"),(93,"A、"),(121,"B、"),(159,"(例四)")):
  if not lines[n-1].startswith(k):raise ValueError(("Unexpected original case marker",n))
 return lines
def parse_chart(lines,start):
 cells=[]
 for row in range(3):
  b=start+row*4
  bands=[]
  for z in range(3):
   p=[x.strip() for x in lines[b+z-1].split("│")]
   if len(p)!=3:raise ValueError(("Grid is not three source palace columns",start,b+z))
   bands.append(p)
  if row<2 and "┼" not in lines[b+2]:
   raise ValueError(("Printed original grid separator missing",start,row))
  for col in range(3):
   j=row*3+col;pal=PALS[j];title=NAMES[j]
   hd=bands[0][col]
   if not hd.startswith(title):raise ValueError(("Palace name altered",start,pal))
   deity=hd[len(title):].strip();door=bands[1][col];star=bands[2][col]
   if pal==5 and (deity or star or not door):raise ValueError("Center cannot be inferred")
   if pal!=5 and (not door or not star):raise ValueError(("Peripheral original missing",pal,start))
   literal="\n".join([hd,door,star])
   cells.append({"palace":pal,"source_unique_line":b+col,"start_line":b,"end_line":b+2,
     "label":title,"deity":deity,"door":door,"star":star,
     "literal":literal,"sha":hx(literal.encode("utf-8")),
     "unknowns":literal.count("〔原文未载天干〕")})
 if sorted(x["palace"] for x in cells)!=list(range(1,10)):raise ValueError("Nonunique source palace")
 return cells
def scenarios(lines):
 out=[]
 for d in DATA:
  key,cid,title,begin,end,q1,q2,chart,steps,pred,feedback,editor,sub,date,hour,note=d
  cells=parse_chart(lines,chart)
  if key=="three_b":
   if sum(c["unknowns"] for c in cells)!=2:raise ValueError("Original two unknown stems lost")
  elif sum(c["unknowns"] for c in cells):raise ValueError("Unexpected unknown source text")
  if key=="three_a":
   if cells[8]["star"]!="逢戊" or cells[0]["deity"]!="虎" or cells[3]["deity"]!="虎":
    raise ValueError("Keep anomalous 逢戊 and source duplicate white tiger")
  out.append({"key":key,"id":cid,"title":title,"begin":begin,"end":end,
   "q":[q1,q2],"chart":chart,"chart_end":chart+10,
   "cells":cells,"chart_sha":hx(text(lines,chart,chart+10).encode("utf-8")),
   "steps":steps,"pred":pred,"feedback":feedback,"editor":editor,
   "subdomain":sub,"date":date,"hour":hour,"note":note,
   "existing":key=="two_b"})
 if len(out)!=6 or len({x["id"] for x in out})!=6:
  raise ValueError("Six source scenarios or event identities lost")
 return out
def scenario_phases(s,lines):
 def add(name,kind,a,b,blind=False):
  x=text(lines,a,b)
  return {"name":name,"kind":kind,"a":a,"b":b,"literal":x,
    "sha":hx(x.encode("utf-8")),"blind":int(blind)}
 p=[add("known","known_at_cast",*s["q"],blind=True),
   add("source_chart","original_printed_chart",s["chart"],s["chart_end"])]
 if s["steps"] and s["key"]!="two_a":
  p.append(add("reasoning","author_initial_analysis",s["steps"][0],s["steps"][-1]))
 if s["pred"]:p.append(add("initial_prediction","author_initial_prediction",*s["pred"]))
 p.append(add("reported_feedback","book_reported_feedback",*s["feedback"]))
 p.append(add("editor","source_retrospective_comparison" if s["key"].startswith("two_")
  else "post_feedback_editor_note",*s["editor"]))
 return p
def source_assertions(lines,sc):
 out=[];used=set()
 def insert(concept,kind,line,topic,case_id,relation):
  literal=text(lines,line)
  if not literal:raise ValueError(("Blank original source",line))
  if (concept,line) in used:raise ValueError(("Repeated concept occurrence",concept,line))
  used.add((concept,line))
  meta={"topic":topic,"source_case_id":case_id,"source_scope":"traditional health text",
    "medical_facts_not_independently_verified":True,
    "after_feedback_cannot_be_initial_prediction":topic=="retrospective_comparison",
    "positive_training_eligible":False}
  out.append({"concept_id":concept,"kind":kind,"line":line,"original":literal,
    "source_sha":hx(literal.encode("utf-8")),"meta":meta,
    "relation":relation,"track":f"kaiwu:health:v1:{kind}"})
 for sp in sc:
  if sp["existing"]:continue
  for index,ln in enumerate(sp["steps"],1):
   if not re.match(r"^\(\d+\)",lines[ln-1]):raise ValueError(("Author step number missing",ln))
   topic="retrospective_comparison" if sp["key"]=="two_a" else "prior_to_book_feedback"
   insert("health:"+sp["key"]+":step:"+str(index),"health_author_step",ln,topic,sp["id"],
    "additional_exposition")
 for line,cid in EDITOR:
  insert(cid,"health_editor_topic",line,
    "retrospective_comparison" if line in (85,87,89) else "author_posthoc_editorial",
    "health_book_source","clarifies")
 return out
def old_included(old,db):
 for (t,) in old.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"):
  cols=[x[1] for x in old.execute('PRAGMA table_info("'+t+'")')]
  sel=",".join('"'+x+'"' for x in cols)
  baseline=list(old.execute('SELECT '+sel+' FROM "'+t+'"'))
  now=set(db.execute('SELECT '+sel+' FROM "'+t+'"'))
  if not all(x in now for x in baseline):
   raise ValueError("Previous case/database original overwritten: "+t)
def insert_new(db,sid,lines,sp):
 cid=sp["id"];known=text(lines,*sp["q"])
 author="\n\n".join(text(lines,ln) for ln in sp["steps"])
 forecast=text(lines,*sp["pred"]) if sp["pred"] else None
 feedback=text(lines,*sp["feedback"])
 db.execute("""INSERT INTO cases(case_id,section_id,event_family_id,domain_id,
 known_before,author_yongshen_steps,author_judgment,later_feedback,reviewed)
 VALUES (?,?,?,'health',?,?,?,?,0)""",
 (cid,sid,cid,known,author,forecast,feedback))
 meta={"case_id":cid,"subdomain":sp["subdomain"],"source_open_line":sp["begin"],
  "event_date":sp["date"],"hour":sp["hour"],"real_initial_prediction_reproduced":bool(sp["pred"]),
  "source_line_chart":sp["chart"],"source_note":sp["note"],"source_status":"draft",
  "not_independent_prospective_test":True,"same_health_domain_as_shenqi":True}
 db.execute("""INSERT INTO historical_case_protocol(case_id,completeness,
 published_chart_verification,feedback_independently_verified,eligible_blind_test,
 case_source_sha256,metadata_json)
 VALUES (?,?,'source_book_chart_not_independently_recast',0,0,?,?)""",
 (cid,"comparator_chart_original_first_prediction_not_present" if not sp["pred"]
  else "full_source_book_case_with_chart_and_reported_feedback",SOURCE_SHA,js(meta)))
 for c in sp["cells"]:
  center=c["palace"]==5
  db.execute("""INSERT INTO historical_chart_cells(case_id,palace,source_line,
 palace_label_raw,deity_raw,door_position_raw,star_position_raw,source_status)
 VALUES (?,?,?,?,?,?,?,'exact_original_book_transcription_no_recast')""",
 (cid,c["palace"],c["source_unique_line"],c["label"],c["deity"],c["door"],c["star"]))
  db.execute("""INSERT INTO historical_palace_standardization(case_id,cast_key,palace,
 center_stem,source_of_center_stem,standard_deity,standard_door,standard_star,
 normalized_status,original_raw_integrity_checked,method_reference,
 derived_host_palace,derived_host_source)
 VALUES (?,'primary',?,?,?,?,?,?,?,1,?,?,?)""",
 (cid,c["palace"],c["door"][-1] if center else None,
  "literal_center_token_with_qin_prefix_in_original" if center and "禽" in c["door"]
  else "original_center_single_stem" if center else "not_center",
  None if center else c["deity"],None if center else c["door"],
  None if center else c["star"],
  "center_no_printed_star_door_deity" if center else
  "exact_original_missing_stems_no_fill" if c["unknowns"] else "raw_transcription_no_recast",
  "kaiwu_source_traditional_shijia",2 if center else None,
  "known_center_host_kun_is_separate_derivation" if center else None))
 for j,line in enumerate(sp["steps"],1):
  raw=text(lines,line)
  phase="post_feedback_comparison_not_original_prediction" if sp["key"]=="two_a" else "book_initial_analysis"
  step={"book":"kaiwu","phase":phase,"review_status":"draft",
   "condition":sp["note"],"source_line":line,"positive_training_eligible":False}
  db.execute("""INSERT INTO historical_case_reasoning(case_id,step_number,source_line,
 author_analysis_original,short_method_topic,metadata_json) VALUES (?,?,?,?,?,?)""",
 (cid,j,line,raw,phase,js(step)))
  db.execute("""INSERT INTO historical_case_reasoning_trace(case_id,step_number,source_line,
 evidence_json,review_status,positive_training_eligible)
 VALUES (?,?,?,?,'source_anchored_draft_requires_human_step_check',0)""",
 (cid,j,line,js(step)))
 db.execute("""INSERT INTO historical_case_review_audit(case_id,original_steps,mechanical_step_trace,
 human_complete_step_chains,review_status,warning)
 VALUES (?,?,?,0,'source_anchored_draft_requires_human_step_check',?)""",
 (cid,len(sp["steps"]),len(sp["steps"]),sp["note"]))
 # Only the four fully narrated forecast/feedback accounts receive a book
 # success-default. The brother's original initial forecast was not reproduced.
 if sp["pred"]:
  db.execute("""INSERT INTO historical_case_book_verdicts(event_family_id,primary_case_id,
  verdict,explicit_source_correction,source_correction_lines_json,feedback_source_lines_json,
  independent_external_verification,app_output_protocol,evidence_review_status,note)
  VALUES (?,?,'author_book_success_default',0,'[]',?,
  'not_verified','single_answer_for_one_cast','book_source_only',?)""",
  (cid,cid,js(sp["feedback"]),sp["note"]))
def insert_witness(db,sid,lines,sp):
 key=sp["key"];cid=sp["id"]
 db.execute("""INSERT INTO health_crossbook_case_witnesses(witness_key,section_id,
 book_id,chapter_key,case_id,event_family_id,subdomain,printed_group,source_open_line,
 source_chart_start,source_chart_end,full_source_sha256,printed_chart_sha256,
 witness_relationship,source_summary_json)
 VALUES (?,?,'kaiwu',?,?,?,?,?,?,?,?,?,?,?,?)""",
 (key,sid,CHAPTER,cid,cid,sp["subdomain"],sp["title"],sp["begin"],
  sp["chart"],sp["chart_end"],SOURCE_SHA,sp["chart_sha"],
  "same_prior_event_reprinted" if sp["existing"] else "new_event_source",
  js({"case_id":cid,"old_event":sp["existing"],"book_only_result":True,
      "source_note":sp["note"],"date":sp["date"],"hour":sp["hour"]})))
 for c in sp["cells"]:
  db.execute("""INSERT INTO health_crossbook_witness_palaces(witness_key,palace,
  source_start_line,source_end_line,palace_label_original,deity_original,
  door_original,star_original,source_cell_original,source_cell_sha256,
  has_explicit_missing_text,normalized_guess_not_printed)
  VALUES (?,?,?,?,?,?,?,?,?,?,?,0)""",
  (key,c["palace"],c["start_line"],c["end_line"],c["label"],c["deity"],c["door"],
   c["star"],c["literal"],c["sha"],int(c["unknowns"]>0)))
 for p in scenario_phases(sp,lines):
  db.execute("""INSERT INTO health_crossbook_case_phases(witness_key,phase_key,phase_type,
  source_start_line,source_end_line,original_text,excerpt_sha256,
  contemporaneous_evidence_independently_verified,eligible_for_blind_input)
  VALUES (?,?,?,?,?,?,?,0,?)""",
  (key,p["name"],p["kind"],p["a"],p["b"],p["literal"],p["sha"],p["blind"]))
 if key in ("two_a","two_b"):
  for n in (85,87,89):
   original=text(lines,n)
   db.execute("""INSERT INTO health_crossbook_comparison_steps(chapter_key,case_id,source_line,
    subject_chart_label,original_editor_comparison,source_excerpt_sha256,phase,report_json)
    VALUES (?,?,?,?,? ,?,'retrospective_editor_comparison_not_initial_prediction',?)""",
    (CHAPTER,cid,n,"A" if key=="two_a" else "B",original,
     hx(original.encode("utf-8")),js({"editor_1997_after_outcome":True,"book_source_only":True})))
def build(base,source,output,index_dir):
 base,source,output,index_dir=map(Path,(base,source,output,index_dir))
 if output.exists():raise ValueError("Never overwrite any prior full archive")
 if hx(base.read_bytes())!=BASE_SHA:raise ValueError("Wrong latest 26-source full DB parent SHA")
 raw=source.read_bytes();lines=original(raw);items=scenarios(lines);asserts=source_assertions(lines,items)
 output.parent.mkdir(parents=True,exist_ok=True)
 with sqlite3.connect("file:"+str(base)+"?mode=ro",uri=True) as old,sqlite3.connect(output) as db:
  old.backup(db)
  db.executescript((ROOT/"schema/migrations/021_health_crossbook_case_witnesses.sql").read_text("utf-8"))
  db.execute("PRAGMA foreign_keys=ON")
  with db:
   if db.execute("SELECT count(*) FROM sections WHERE book_id='kaiwu'").fetchone()[0]!=5:
    raise ValueError("Missing original five Kaiwu source sections")
   present=db.execute("""SELECT c.domain_id,s.book_id FROM cases c
    JOIN sections s ON s.section_id=c.section_id WHERE c.case_id=?""",(OLD_FATHER,)).fetchone()
   if present!=("health","shenqi"):raise ValueError("Cannot link same father historical event absent from Shenqi")
   if db.execute("SELECT 1 FROM sections WHERE book_id='kaiwu' AND section_key=?",(SECTION,)).fetchone():
    raise ValueError("Exact source section already imported")
   db.execute("""INSERT INTO sections(book_id,section_key,title,original_text,sha256,content_version,reviewed)
   VALUES ('kaiwu',?,?,?,?,1,0)""",(SECTION,TITLE,raw.decode("utf-8"),SOURCE_SHA))
   sid=db.execute("SELECT last_insert_rowid()").fetchone()[0]
   db.execute("""INSERT INTO chapter_knowledge(chapter_key,book_id,title,source_sha256,source_length_bytes,
   knowledge_version,review_status) VALUES (?,'kaiwu',?,?,?,'1','draft')""",
   (CHAPTER,TITLE,SOURCE_SHA,len(raw)))
   for sp in items:
    if not sp["existing"]:insert_new(db,sid,lines,sp)
    insert_witness(db,sid,lines,sp)
   for x in asserts:
    db.execute("""INSERT INTO semantic_assertions(chapter_key,concept_id,kind,relation,
    source_start_line,source_end_line,metadata_json,original_excerpt,review_status)
    VALUES (?,?,?,?,?,?,?,?,'draft')""",
    (CHAPTER,x["concept_id"],x["kind"],x["relation"],x["line"],x["line"],
     js(x["meta"]),x["original"]))
    db.execute("""INSERT INTO cross_book_concept_tracks(chapter_key,concept_id,
    source_start_line,source_end_line,source_section_id,source_sha256,excerpt_sha256,
    track_id,relation_to_prior,comparison_state,normalized_json,review_status)
    VALUES (?,?,?,?,?,?,?,?,?,'candidate_not_human_verified',?,'draft')""",
    (CHAPTER,x["concept_id"],x["line"],x["line"],sid,SOURCE_SHA,x["source_sha"],
     x["track"],x["relation"],js(x["meta"])))
   db.execute("""INSERT INTO cross_book_example_references(source_chapter_key,source_line,
   target_book_id,target_printed_page,reference_key,metadata_json,verified_target_case_id)
   VALUES (?,65,'shenqi','unspecified_in_source',?,?,?)""",
   (CHAPTER,"kaiwu:health:shared_19960727_father",
    js({"case":"例二B","event_id":OLD_FATHER,
        "matching_date":"1996-07-27","father_birth":"辛酉",
        "same_question_and_hour":True,"not_new_event":True}),OLD_FATHER))
   db.execute("""INSERT INTO chapter_archival_versions(archive_label,baseline_sha256,new_db_sha256,
   contains_complete_private_copyright_source,snapshot_type,created_utc,repo_public_archive_policy)
   VALUES (?,?,NULL,1,'same_domain_crossbook_health_cases_and_source_witnesses',
   '2026-10-20','user_authorized_public_full_sqlite_versions')""",
   ("shenqi21_kaiwu_health01_108cases",BASE_SHA))
  old_included(old,db)
  if db.execute("PRAGMA integrity_check").fetchone()[0]!="ok" or db.execute("PRAGMA foreign_key_check").fetchall():
   raise ValueError("SQL integrity failed")
  expected={"sections":27,"cases":108,"historical_chart_cells":972,
    "historical_case_additional_cast_cells":81,"historical_case_reasoning":516,
    "historical_case_reasoning_trace":516,"historical_palace_standardization":1053,
    "semantic_assertions":2159+len(asserts),"cross_book_concept_tracks":902+len(asserts),
    "cross_book_example_references":43,"health_crossbook_case_witnesses":6,
    "health_crossbook_witness_palaces":54,"health_crossbook_comparison_steps":6}
  got={t:db.execute('SELECT count(*) FROM "'+t+'"').fetchone()[0] for t in expected}
  if got!=expected:raise ValueError(("Unexpected inherited + new row counts",got,expected))
  if db.execute("SELECT count(*) FROM cases WHERE domain_id='health'").fetchone()[0]<11:
   raise ValueError("Five new cases must be in existing Shenqi health field")
  if db.execute("SELECT count(*) FROM cases c JOIN sections s ON c.section_id=s.section_id WHERE s.book_id='kaiwu' AND c.domain_id='health'").fetchone()[0]!=5:
   raise ValueError("New five cases must share health domain")
  if db.execute("SELECT count(*) FROM historical_case_book_verdicts WHERE verdict='author_book_error_explicit'").fetchone()[0]!=6:
   raise ValueError("Old six author-acknowledged wrong calls changed")
  if db.execute("SELECT count(*) FROM historical_case_reasoning_trace WHERE positive_training_eligible=1").fetchone()[0]:
   raise ValueError("Unchecked analysis eligible for training")
  if db.execute("SELECT count(*) FROM health_crossbook_witness_palaces WHERE normalized_guess_not_printed!=0").fetchone()[0]:
   raise ValueError("Source gaps filled without author text")
  db.execute("VACUUM");db.commit()
  if db.execute("PRAGMA integrity_check").fetchone()[0]!="ok" or db.execute("PRAGMA foreign_key_check").fetchall():
   raise ValueError("VACUUM integrity failure")
 index_dir.mkdir(parents=True,exist_ok=True)
 report={"schema":"wengua_health_across_books_v1","chapter_key":CHAPTER,"source_book":"kaiwu",
    "source_title":TITLE,"source_sha256":SOURCE_SHA,"source_bytes":len(raw),
    "source_lines":len(lines),"book_case_subexamples":6,"new_event_families":5,
    "shared_old_event_families":1,"old_father_case_id":OLD_FATHER,
    "all_six_printed_charts_retained_as_source_witnesses":True,
    "original_source_witness_palace_cells":54,"new_independent_historical_charts":5,
    "new_historical_chart_cells":45,"new_reasoning_steps":21,
    "new_source_semantic_occurrences":len(asserts),"health_case_domain":"health",
    "animal_health_is_subdomain_not_separate_case_collection":True,
    "total_historical_events":108,"total_historical_charts":117,
    "total_source_sections":27,"book_counts":{"shenqi":21,"kaiwu":6},
    "original_103_shenqi_cases_unchanged":True,
    "old_112_independent_charts_unchanged":True,
    "case_A_prior_original_prediction_absent":True,
    "hen_actual_death_time_not_observed":True,
    "rooster_2_source_missing_stems_kept":True,
    "professional_medical_evidence_independently_verified":False,
    "all_old_table_rows_preserved":True,"positive_training_eligible":0,
    "review_status":"draft","parent_sha256":BASE_SHA,
    "database_sha256":hx(output.read_bytes()),"cumulative_counts":got}
 def save(name,v):
  (index_dir/name).write_text(json.dumps(v,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 save("chapter_manifest.json",report)
 save("case_index.json",{"schema":"crossbook_health_six_source_stories_v1",
    "source_sha256":SOURCE_SHA,
    "cases":[{k:v for k,v in sp.items() if k!="cells"} for sp in items]})
 save("original_chart_witnesses.json",{"source_sha256":SOURCE_SHA,
    "charts":[{"key":sp["key"],"case_id":sp["id"],"start":sp["chart"],
        "palace_cells":sp["cells"]} for sp in items]})
 save("method_index.json",{"source_sha256":SOURCE_SHA,"entries":asserts})
 save("cross_book_links.json",{"source_sha256":SOURCE_SHA,
    "same_event_as_shenqi":{"case_id":OLD_FATHER,"this_book_group":"例二B",
      "source_line":65,"old_case_preserved":True},
    "original_academic_paper_A_not_full_initial_prediction":True})
 save("source_audit.json",{"source_sha256":SOURCE_SHA,
    "chapter_contains_six_printed_boards_one_prior_event":True,
    "author_1985_comparison":False,"posthoc_comparison_lines":[85,87,89],
    "ex1_diagnosis_known_before_cast":True,
    "hen_dead_on_check_at_10_05_exact_death_time_unknown":True,
    "rooster_original_missing_stems_count":2,
    "original_hen_charts_duplicate_white_tiger_and_yin_token_逢戊":True,
    "surgery_specialist_outcome_book_only":True,
    "no_medical_diagnosis_or_unsafe_treatment_recommendation":True,
    "cross_book_father_event_not_double_counted":True,
    "all_new_in_same_domain_health":True,
    "author_reasoning_draft_not_approved":True})
 return report
def main():
 p=argparse.ArgumentParser()
 for key in ("base","source","output","index-dir"):p.add_argument("--"+key,required=True)
 a=p.parse_args()
 print(json.dumps(build(a.base,a.source,a.output,a.index_dir),ensure_ascii=False,indent=2))
if __name__=="__main__":main()
