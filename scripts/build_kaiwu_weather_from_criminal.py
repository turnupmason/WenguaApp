"""Append Kaiwu weather 2 book events from the exact complete 161-case parent.

IMPORTANT: source lines 16..32 and 52..67 are flattened, spatially unresolvable
OCR fragments of two Qimen nine-palace boards, NOT recoverable original
nine-palace grids. Preserve ALL 33 raw lines/bytes and cited AUTHOR palace
claims separately. Never invent deity/gate/star original source cells.
No instrumental meteorological/hydrological external validation is claimed.
"""
from __future__ import annotations
import argparse,hashlib,json,re,sqlite3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE_SHA="70b31dbe6005aa1d24af5faf298796effe0d06a87b2c1faf0af55d461cb5a1b9"
SOURCE_SHA="5fbdc0cc88012934beabe8e9a13e656c4be72afa8706245649f8d11b8e5ffe1e"
BASE_NAME="WenguaApp_神奇之门21章_开悟之门15节_161案例_完整研究库.sqlite3"
NEW_NAME="WenguaApp_神奇之门21章_开悟之门16节_163案例_完整研究库.sqlite3"
CHAPTER="kaiwu/weather_prediction_ch02_section13/v1"
SECTION="weather_prediction_ch02_section13"
TITLE="第十三节 天时气象预测(共2例)"
CASES=[
 dict(key="wedding_weather_19990422",id="kaiwu.weather.case01",
 title="1999年4月24至26日石家庄婚礼及回门天气",
 begin=3,end=46,known=(12,14),calendar=14,chart=(16,32),
 steps=[36,38,40,42],first_answer=[42,43],feedback=[45],
 facets=["wedding_planning"],
 question_date="1999-04-22 08:30",
 target_date="1999-04-24/26",
 note="4/24 and 4/25 dry and sunny; book-reported rain on 4/26. Nearby friend moving Apr25 is only a separate mentioned choice, not another printed chart and lacks outcome feedback."),
 dict(key="yangtze_1998_flood_recession",id="kaiwu.weather.case02",
 title="1998年长江特大洪水退落的书内推演",
 begin=47,end=79,known=(47,50),calendar=50,chart=(52,67),
 steps=[71,73,75,77],first_answer=[78],feedback=[78],
 facets=["flood_disaster"],question_date="1998-08-19 midday",
 target_date="lunar_renxu_month_1998",
 note="Major Yangtze flooding already underway and known before prediction; book concludes retreat by lunar 壬戌月 and says 果验 without independent level/station/date measurements; six-yao also mentioned with no printed chart.")
]
GENERAL_RULE_LINES=[9,10,11,79]
CLAIMS=[
 (1,"two_wedding_days_dry",42,"book_reported_wedding_weather_match"),
 (1,"april26_rain",42,"book_reported_following_day_rain"),
 (1,"tianpeng_kan1_tianzhu_dui7",38,"author_named_palaces_not_resolved_OCR_grid"),
 (1,"tianying_li9",40,"author_named_palace_not_resolved_OCR_grid"),
 (2,"water_retreat_lunar_renxu",78,"book_only_guoyan_no_hydrology_series"),
 (2,"tianpeng_xiumen_xun4",71,"author_named_palace_not_resolved_OCR_grid"),
 (2,"xuanwu_xun4",73,"author_named_palace_not_resolved_OCR_grid"),
 (2,"qian6_recession_logic",77,"author_named_palace_not_resolved_OCR_grid")
]
def sha(b):return hashlib.sha256(b).hexdigest()
def js(o):return json.dumps(o,ensure_ascii=False,sort_keys=True,separators=(",",":"))
def literal(L,a,b=None):
 b=a if b is None else b
 if not 1<=a<=b<=len(L):raise ValueError(("Original source interval out of bounds",a,b))
 return "\n".join(L[a-1:b])
def validate(raw):
 if sha(raw)!=SOURCE_SHA or len(raw)!=6643 or not raw.endswith(b"\n"):
  raise ValueError("Source original SHA256, exact bytes or trailing newline mismatch")
 L=raw.decode("utf8").splitlines()
 if len(L)!=79 or L[0]!=TITLE:raise ValueError("Original full 79 lines not preserved")
 if [i for i,s in enumerate(L,1) if s.startswith("(例") ]!=[3,47]:
  raise ValueError("Two and only two original numbered weather events")
 if [i for i,s in enumerate(L,1) if s.startswith("┌") or s.startswith("+---")]:
  raise ValueError("The supplied OCR chart was FLATTENED; never infer a boxed nine-palace panel")
 if "上一次" in L[44]:raise ValueError("Did not expect altered additional moving-house event")
 if L[15]!="阴" or L[31]!="心丙" or L[51]!="武" or L[66]!="景  己 英  壬":
  raise ValueError("OCR dispersed original palace tokens have changed")
 if "4月26日" not in L[44] or "果验" not in L[77] or "壬戌月" not in L[77]:
  raise ValueError("Original weather and flood source feedback must be intact")
 if "玄武和天蓬星、休门均属水" not in L[72]:
  raise ValueError("Source author weather conditions missing")
 return L
def old_rows_unchanged(old,db):
 for (t,) in old.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"):
  cols=[x[1] for x in old.execute('PRAGMA table_info("'+t+'")')]
  query=",".join('"'+v+'"' for v in cols)
  existing=list(old.execute('SELECT '+query+' FROM "'+t+'"'))
  later=set(db.execute('SELECT '+query+' FROM "'+t+'"'))
  if not all(a in later for a in existing):
   raise ValueError("Old row modified while appending Kaiwu weather: "+t)
def phase(db,L,e,key,kind,a,b=None,extra=None):
 b=a if b is None else b;txt=literal(L,a,b)
 meta={"source_book":"kaiwu","book_case_user_accepted_without_individual_review":True,
 "source_report_not_external_instrument_weather_or_hydrology_validation":True,
 "later_knowledge_not_an_initial_forecast":True,**(extra or {})}
 db.execute("""INSERT INTO kaiwu_weather_chronology(chapter_key,case_id,phase_key,
 phase_kind,first_source_line,last_source_line,source_text,excerpt_sha256,metadata_json)
 VALUES (?,?,?,?,?,?,?,?,?)""",
 (CHAPTER,e["id"],key,kind,a,b,txt,sha(txt.encode("utf8")),js(meta)))
def add_semantic(db,L,sid,concept,kind,a,b,metadata):
 txt=literal(L,a,b)
 db.execute("""INSERT INTO semantic_assertions(chapter_key,concept_id,kind,relation,
 source_start_line,source_end_line,metadata_json,original_excerpt,review_status)
 VALUES (?,?,?,?,?,?,?,?,'draft')""",
 (CHAPTER,concept,kind,"additional_exposition",a,b,js(metadata),txt))
 db.execute("""INSERT INTO cross_book_concept_tracks(chapter_key,concept_id,
 source_start_line,source_end_line,source_section_id,source_sha256,excerpt_sha256,
 track_id,relation_to_prior,comparison_state,normalized_json,review_status)
 VALUES (?,?,?,?,?,?,?,?,?,'book_author_claim_no_independent_meteorological_verification',?,'draft')""",
 (CHAPTER,concept,a,b,sid,SOURCE_SHA,sha(txt.encode("utf8")),
 "kaiwu:weather:original_source_2026","additional_exposition",js(metadata)))
def add_case(db,L,e,sid):
 cid=e["id"]
 raw=literal(L,*e["chart"]);a,b=e["chart"]
 if len(raw.splitlines())!=b-a+1:raise ValueError("OCR original raw rows missing")
 known=literal(L,*e["known"])
 forecast="\n".join(literal(L,x) for x in e["first_answer"])
 report="\n".join(literal(L,x) for x in e["feedback"])
 steps="\n\n".join(literal(L,n) for n in e["steps"])
 info={"source_chapter_key":CHAPTER,"source_original_OCR_raw_lines":[a,b],
 "original_cast_complete_grid":False,"original_nine_palace_cells_verifiable":0,
 "do_not_derive_original_palaces_from_author_narrative":True,
 "full_source_book_accepted_without_case_by_case_approval":True,
 "source_outcome_not_independently_weather_verified":True,
 "historical_event_already_ongoing_at_question":cid.endswith("case02"),
 "separate_moving_day_not_another_event":cid.endswith("case01"),
 "note":e["note"]}
 db.execute("""INSERT INTO cases(case_id,section_id,event_family_id,domain_id,
 known_before,author_yongshen_steps,author_judgment,later_feedback,reviewed)
 VALUES (?,?,?,'weather_historical_source',?,?,?,?,1)""",
 (cid,sid,cid,known,steps,forecast,report))
 db.execute("""INSERT INTO historical_case_protocol(case_id,completeness,
 published_chart_verification,feedback_independently_verified,eligible_blind_test,
 case_source_sha256,metadata_json) VALUES
 (?,'complete_story_with_OCR_flattened_unmappable_chart',
 'book_fragment_original_only_no_nine_palace_normalization',0,0,?,?)""",
 (cid,SOURCE_SHA,js(info)))
 db.execute("""INSERT INTO historic_book_case_acceptance(case_id,source_book,
 source_chapter_key,source_documented_outcome,metadata_json)
 VALUES (?,'kaiwu',?,'book_source_report_not_external_instrument_observation',?)""",
 (cid,CHAPTER,js(info)))
 for domain in ["weather_historical_source"]+e["facets"]:
  db.execute("""INSERT INTO unified_case_domain_facets(case_id,domain_id,
 source_chapter_key,primary_domain,note) VALUES (?,?,?,?,?)""",
 (cid,domain,CHAPTER,int(domain=="weather_historical_source"),e["note"]))
 db.execute("""INSERT INTO historical_weather_cast_context(case_id,cast_strategy,
 question_date,forecast_target_date,printed_cast_line,
 alternative_techniques_not_printed_json,metadata_json,scientific_external_verification)
 VALUES (?,?,?,?,?,?,?,0)""",
 (cid,"source_question_time_fragment_only",e["question_date"],e["target_date"],a,
 js(["six_yao_mentioned_unprinted"] if cid.endswith("case02") else []),js(info)))
 db.execute("""INSERT INTO kaiwu_weather_raw_cast_fragments(chapter_key,case_id,
 cast_key,source_start_line,source_end_line,raw_original_text,raw_sha256,
 raw_line_count,source_status)
 VALUES (?,?,'primary',?,?,?,?,
 ?,'ocr_flattened_unresolvable_nine_palace')""",
 (CHAPTER,cid,a,b,raw,sha(raw.encode("utf8")),b-a+1))
 for n in range(a,b+1):
  piece=literal(L,n)
  db.execute("""INSERT INTO kaiwu_weather_raw_fragment_lines(chapter_key,case_id,
   cast_key,source_line,original_literal,line_sha256)
   VALUES (?,?,'primary',?,?,?)""",(CHAPTER,cid,n,piece,sha(piece.encode("utf8"))))
 phase(db,L,e,"known_before","question_and_preexisting_weather_context",*e["known"])
 phase(db,L,e,"complete_original_OCR","unmapped_unaltered_flattened_printed_cast",a,b,
  {"zero_certain_grid_positions":True,"all_OCR_tokens_preserved":True})
 for i,n in enumerate(e["steps"],1):
  phase(db,L,e,"author_step_"+str(i),"original_book_author_analytic_step",n)
 for i,n in enumerate(e["first_answer"],1):
  phase(db,L,e,"initial_forecast_"+str(i),"author_claim_source",n)
 for i,n in enumerate(e["feedback"],1):
  phase(db,L,e,"book_feedback_"+str(i),"book_reported_later_weather_event",n,
   {"no_instrumental_station_or_river_level_series":True})
 if cid.endswith("case01"):
  phase(db,L,e,"house_moving_mention","third_party_auspicious_date_only_no_weather_outcome",44,
   {"not_an_independent_complete_historical_weather_case":True})
 else:
  phase(db,L,e,"already_raging_flood","flood_is_publicly_known_at_1998_inquiry",47,50)
  phase(db,L,e,"six_yao_mention","separate_unprinted_method_not_another_Qimen_cast",48)
  phase(db,L,e,"book_self_report_guoyan","word_guoyan_only_no_precise_hydrological_proof",78)
 for k,n in enumerate(e["steps"],1):
  source_step=literal(L,n)
  meta={"source_book":"kaiwu","book_historical_report_accepted":True,
   "source_author_named_palaces_are_not_verified_printed_grid_cells":True,
   "original_printed_chart_spatial_OCR_unresolved":True,
   "positive_training_eligible":False,
   "no_external_scientific_weather_verification":True}
  db.execute("""INSERT INTO historical_case_reasoning(case_id,step_number,source_line,
   author_analysis_original,short_method_topic,metadata_json) VALUES (?,?,?,?,?,?)""",
   (cid,k,n,source_step,"weather_original_source_rule_not_proven_meteorology",js(meta)))
  db.execute("""INSERT INTO historical_case_reasoning_trace(case_id,step_number,
    source_line,evidence_json,review_status,positive_training_eligible)
    VALUES (?,?,?,?,'book_original_method_source_review_not_auto_positive',0)""",
   (cid,k,n,js(meta)))
  add_semantic(db,L,sid,f"weather:kaiwu:{e['key']}:step{k:02d}",
   "book_weather_historical_source_reasoning",n,n,meta)
 db.execute("""INSERT INTO historical_case_review_audit(case_id,original_steps,
  mechanical_step_trace,human_complete_step_chains,review_status,warning)
  VALUES (?,?,?,0,'book_case_accepted_no_manual_review',?)""",
  (cid,len(e["steps"]),len(e["steps"]),
   "OCR nine palaces unresolvable; author claims preserved without manufactured cells. "+e["note"]))
 db.execute("""INSERT INTO historical_case_book_verdicts(event_family_id,primary_case_id,
 verdict,explicit_source_correction,source_correction_lines_json,feedback_source_lines_json,
 independent_external_verification,app_output_protocol,evidence_review_status,note)
 VALUES (?,?,'author_book_success_default',0,'[]',?,'not_verified',
 'single_answer_for_one_cast','book_source_only_no_external_weather_gauges',?)""",
 (cid,cid,js(e["feedback"]),e["note"]))
def build(parent_path,source_path,out_path,index_dir):
 parent_path,source_path,out_path,index_dir=map(Path,(parent_path,source_path,out_path,index_dir))
 if out_path.exists():raise ValueError("Never overwrite any older complete SQLite")
 if sha(parent_path.read_bytes())!=BASE_SHA:raise ValueError("Parent must be exact final 161-case full archive SHA")
 raw=source_path.read_bytes();L=validate(raw)
 out_path.parent.mkdir(parents=True,exist_ok=True)
 with sqlite3.connect("file:"+str(parent_path)+"?mode=ro",uri=True) as old,sqlite3.connect(out_path) as db:
  old.backup(db)
  db.executescript((ROOT/"schema/migrations/031_kaiwu_weather_flattened_original_panels.sql").read_text("utf8"))
  db.execute("PRAGMA foreign_keys=ON")
  with db:
   if db.execute("SELECT count(*) FROM sections WHERE book_id='kaiwu'").fetchone()[0]!=15:
    raise ValueError("All previous 15 Kaiwu source sections required")
   db.execute("""INSERT INTO sections(book_id,section_key,title,original_text,
    sha256,content_version,reviewed) VALUES ('kaiwu',?,?,?,?,1,1)""",
    (SECTION,TITLE,raw.decode("utf8"),SOURCE_SHA))
   sid=db.execute("SELECT last_insert_rowid()").fetchone()[0]
   db.execute("""INSERT INTO chapter_knowledge(chapter_key,book_id,title,
    source_sha256,source_length_bytes,knowledge_version,review_status)
    VALUES (?,'kaiwu',?,?,?,'1','approved')""",
    (CHAPTER,TITLE,SOURCE_SHA,len(raw)))
   for e in CASES:add_case(db,L,e,sid)
   for line in GENERAL_RULE_LINES:
    meta={"book_id":"kaiwu","kind":"source_general_author_principle",
     "not_an_independent_event":True,"not_external_science":True,
     "user_book_source_acceptance_not_automatic_training_promotion":True}
    add_semantic(db,L,sid,f"weather:kaiwu:general:line{line}",
     "book_weather_general_condition",line,line,meta)
   for n,key,line,status in CLAIMS:
    e=CASES[n-1]
    db.execute("""INSERT INTO kaiwu_weather_source_claims(chapter_key,case_id,
     claim_key,source_line,source_literal,claim_type,verification_state,metadata_json)
     VALUES (?,?,?,?,?,?,?,?)""",
    (CHAPTER,e["id"],key,line,literal(L,line),
     "book_forecast_or_explicit_author_palace_claim",status,
     js({"source_book":"kaiwu","feedback_source_line":45 if n==1 else 78,
         "not_a_certain_original_chart_cell":True,
         "book_claim_accepted_without_external_instrumental_verification":True})))
   db.execute("""INSERT INTO chapter_archival_versions(archive_label,baseline_sha256,
    new_db_sha256,contains_complete_private_copyright_source,snapshot_type,
    created_utc,repo_public_archive_policy)
    VALUES (?,?,NULL,1,'kaiwu_weather_two_original_OCR_scattered_cast_texts_not_full_grids',
     '2026-10-20','user_authorized_public_full_sqlite_versions')""",
    ("shenqi21_kaiwu16_weather_163cases",BASE_SHA))
  old_rows_unchanged(old,db)
  if db.execute("PRAGMA integrity_check").fetchone()[0]!="ok" or db.execute("PRAGMA foreign_key_check").fetchall():
   raise ValueError("New full source SQLite failed integrity")
  expected={"sections":37,"cases":163,"historical_chart_cells":1440,
   "historical_case_additional_casts":19,"historical_case_additional_cast_cells":171,
   "historical_palace_standardization":1611,
   "historical_case_reasoning":834,"historical_case_reasoning_trace":834,
   "semantic_assertions":2512,"cross_book_concept_tracks":1255,
   "cross_book_example_references":48,"historic_book_case_acceptance":55,
   "unified_case_domain_facets":79,"historical_weather_cast_context":7,
   "kaiwu_weather_raw_cast_fragments":2,
   "kaiwu_weather_raw_fragment_lines":33,
   "kaiwu_weather_source_claims":8}
  got={t:db.execute('SELECT count(*) FROM "'+t+'"').fetchone()[0] for t in expected}
  if got!=expected:raise ValueError(("Complete parent plus new source counts",got,expected))
  actual={r[0] for r in db.execute("SELECT case_id FROM unified_weather_source_cases_across_books")}
  if not {f"shenqi.weather.case{i:02}" for i in range(1,6)}.union(
   {"kaiwu.weather.case01","kaiwu.weather.case02"}).issubset(actual):
   raise ValueError("Existing 5 Shenqi and new 2 Kaiwu weather cases must share domain")
  if db.execute("SELECT count(*) FROM historical_case_book_verdicts WHERE verdict='author_book_error_explicit'").fetchone()[0]!=10:
   raise ValueError("All ten earlier explicit author first errors modified")
  if db.execute("SELECT count(*) FROM kaiwu_weather_raw_fragment_lines").fetchone()[0]!=33:
   raise ValueError("OCR printed scattered source row not preserved")
  db.execute("VACUUM");db.commit()
  if db.execute("PRAGMA integrity_check").fetchone()[0]!="ok" or db.execute("PRAGMA foreign_key_check").fetchall():
   raise ValueError("Post-VACUUM full archive failed integrity")
 index_dir.mkdir(parents=True,exist_ok=True)
 doc={"schema":"kaiwu_weather_two_events_flattened_OCR_source_witness_v1",
  "source_title":TITLE,"source_sha256":SOURCE_SHA,
  "source_bytes":len(raw),"source_lines":len(L),
  "new_distinct_book_case_families":2,
  "new_casts_mentioned_and_OCR_text_printed":2,
  "new_recoverable_complete_original_nine_palace_grids":0,
  "new_source_recoverable_nine_palace_cells":0,
  "all_original_OCR_fragment_lines_stored":33,
  "author_explicit_pseudo_palace_claims_not_grid_normalizations":True,
  "new_original_numbered_analysis_units":8,"new_general_source_method_statements":4,
  "source_book_wedding_weather_24_25_dry_april26_rain":True,
  "source_book_yangtze_1998_flood_already_known_at_cast":True,
  "yangtze_source_only_guoyan_lunar_renxu_no_independent_river_levels":True,
  "third_party_move_date_no_new_independent_cast":True,
  "all_source_cases_accepted_without_individual_user_review":True,
  "all_old_original_chart_cells_untouched":True,
  "prior_explicit_original_case_errors_remain":10,
  "book_counts":{"shenqi":21,"kaiwu":16},
  "source_sections":37,"independent_historical_events":163,
  "previous_original_recoverable_complete_9_palace_casts":179,
  "new_OCR_flattened_unresolved_source_diagram_witnesses":2,
  "parent_sha256":BASE_SHA,"new_archive_sha256":sha(out_path.read_bytes()),
  "all_prior_sqlite_rows_unchanged":True,"counts":got}
 def write(name,x):(index_dir/name).write_text(json.dumps(x,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 write("chapter_manifest.json",doc)
 write("case_index.json",{"source_sha256":SOURCE_SHA,
  "cases":[{k:v for k,v in e.items() if k not in ("facets",)} for e in CASES]})
 write("raw_OCR_cast_fragments.json",{"source_sha256":SOURCE_SHA,
  "fragments":[{"case_id":e["id"],"source_lines":e["chart"],
    "original_raw_lines":[{"line":n,"literal":literal(L,n)} for n in range(e["chart"][0],e["chart"][1]+1)]}
   for e in CASES]})
 write("temporal_and_book_claim_audit.json",{"source_sha256":SOURCE_SHA,
  "no_fabricated_nine_palace_chart_cells":True,
  "wedding_weather_book_reported_24_25_sunny_26_rain":True,
  "third_party_moving_not_a_new_source_cast":True,
  "flood_already_occurred_at_question":True,
  "book_flood_retreat_guoyan_no_gauged_verification":True,
  "all_ten_previous_case_level_author_errors_kept":True,
  "all_parent_original_rows_including_chart_cells_identical":True})
 return doc
def main():
 ap=argparse.ArgumentParser()
 for n in ("base","source","output","index-dir"):ap.add_argument("--"+n,required=True)
 a=ap.parse_args()
 print(json.dumps(build(a.base,a.source,a.output,a.index_dir),ensure_ascii=False,indent=2))
if __name__=="__main__":main()
