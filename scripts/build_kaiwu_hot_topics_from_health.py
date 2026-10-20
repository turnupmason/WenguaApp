"""《开悟之门》热门话题：跨书同领域，13事件/20原书盘，不按书拆领域。

Book historical stories/outcomes are accepted by user for this research corpus,
without a per-case human approval gate; the author's *explicit* historical
mistake remains an incorrect initial answer. This is not external validation.
Never feed later feedback or corrected birth years into an earlier cast.
"""
from __future__ import annotations
import argparse,hashlib,json,re,sqlite3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE_SHA="79b30135e42129f6596c66f09eec66496ae5d08afb8786f2831581f3fe7c6b05"
SOURCE_SHA="d85e880bd7e09af25b0db75ae995f0e072b2ff8501a9eb836c2b70748a5fd36d"
BASE_NAME="WenguaApp_神奇之门21章_开悟之门6节_108案例_完整研究库.sqlite3"
NEW_NAME="WenguaApp_神奇之门21章_开悟之门7节_121案例_完整研究库.sqlite3"
CHAPTER="kaiwu/hot_topics_prediction_ch01/v1"
SECTION="hot_topics_prediction_ch01"
TITLE="第一章 热门话题预测评析"
PAL=(4,9,2,3,5,7,8,1,6)
NAMES=("巽四宫","离九宫","坤二宫","震三宫","中五宫","兑七宫","艮八宫","坎一宫","乾六宫")
# A same historical event can appear in multiple numbered sections, contain
# several dated genuine Qimen printed boards, and receive later corrections.
# Primary domains intentionally REUSE Shenqi IDs where applicable.
EVENTS=[
 dict(key="clinton",n=["一"],title="克林顿弹劾与是否下台",domain="litigation",
  facets=["politics_elections","litigation"],ranges=[(5,100)],q=(7,19),
  charts=[(21,"1998-09-26","甲午"),(57,"1999-01-09","丁酉")],
  pred=[43,87],feedback=[47,99],posthoc=[91,93,95],notes="House impeachment proceedings occurred, but US Senate did not remove him; not identical propositions"),
 dict(key="nato",n=["二"],title="1999年北约空袭南联盟持续时间",domain="military_history_source",
  facets=["military_history_source","geopolitics"],ranges=[(101,170)],q=(103,107),
  charts=[(109,"1999-03-24","己卯"),(143,"1999-03-26","戊申")],
  pred=[137,167],feedback=[169],posthoc=[121],notes="Zhang expressly edited first correspondent's analysis after original; 79-day account is book reported, not two independent events"),
 dict(key="river_jump",n=["三"],title="朱朝辉摩托车飞越黄河",domain="sports_competition",
  facets=["sports_competition","dangerous_stunt"],ranges=[(171,254)],q=(177,185),
  charts=[(187,"1999-06-20","丁巳"),(227,"1999-06-20","戊午")],
  pred=[201,243,245,247],feedback=[215,217,251],posthoc=[253],
  notes="TV information about reschedule and bride in lines 215-217 occurs after first prediction but before second cast; do not leak"),
 dict(key="apocalypse",n=["四"],title="1999年8月18日世界末日传言",domain="weather_historical_source",
  facets=["weather_historical_source","world_affairs"],ranges=[(255,308)],q=(269,279),
  charts=[(281,"1999-07-25","庚申")],
  pred=[265,275,305],feedback=[307],posthoc=[295],
  notes="A book-authored rejection of the false doomsday rumor; no actual apocalypse event or meteorological chart validation implied"),
 dict(key="women_world_cup",n=["五"],title="1999年中国美国女足决赛",domain="sports_competition",
  facets=["sports_competition"],ranges=[(309,378)],q=(311,321),
  charts=[(323,"1999-07-10","庚申"),(351,"1999-07-11","丙寅")],
  pred=[343,345,347,365,367,369],feedback=[375],posthoc=[371,373,377],
  notes="Predicted host/guest outcome not unambiguously tied to named country BEFORE score; post-result identification of home USA is hindsight; preserve 0:0 and USA penalty 5:4"),
 dict(key="rail_xinle_1998",n=["六A"],title="1998年新乐两次铁路爆炸同一调查",domain="criminal_case",
  facets=["criminal_case","transport_security"],ranges=[(379,418)],q=(381,389),
  charts=[(391,"1998-03-18","戊戌")],pred=[415],feedback=[417],posthoc=[455],
  notes="Two attacks Mar4/14 are one investigation question; '未破' status only as of book writing, not an eternal claim"),
 dict(key="rail_xingtai_1999",n=["六B"],title="1999年邢台铁路爆炸调查",domain="criminal_case",
  facets=["criminal_case","transport_security"],ranges=[(419,456)],q=(419,423),
  charts=[(425,"1999-01-20","庚戌")],pred=[445],feedback=[451],posthoc=[455],
  notes="Separate attack/investigation from March 1998 case, reported suspect arrests with source citation"),
 dict(key="world_outlook_2000",n=["七"],title="2000年全球气候经济政治多领域年度展望",domain="world_affairs",
  facets=["world_affairs","weather_historical_source","business_profit","military_history_source","politics_elections"],
  ranges=[(457,498)],q=(459,475),charts=[],pred=[477,479,483,487,489],
  feedback=[],posthoc=[491,493,495],
  notes="No actual Qimen casting timestamp, printed chart, or postdated outcome evaluation in text; preserve as annual forecast dossier, not fabricate a printed chart"),
 dict(key="taiwan_2000",n=["八"],title="2000年台湾地区领导人选举",domain="politics_elections",
  facets=["politics_elections"],ranges=[(499,556)],q=(501,509),
  charts=[(511,"2000-02-13","己亥")],pred=[533],feedback=[541],
  posthoc=[543,545,547,549,551,553,555],
  explicit_error=True,notes="Original predicts Song first; actual Chen elected; author literally says 看来我测错了 and only AFTER result corrects supplied birth year 1950 to 1951; retain failure not retroactive success"),
 dict(key="beijing_2008",n=["九","十三"],title="北京申办2008年奥运会：2000初测及2001另测",domain="sports_competition",
  facets=["sports_competition","competitive_bidding"],ranges=[(557,604),(851,913)],
  q=(559,563),charts=[(565,"2000-05-09","庚戌"),(865,"2001-07-13","辛亥")],
  pred=[591,603,855,891,901],feedback=[857],posthoc=[905,907,909,911,913],
  notes="Same 2008 Olympic bid, two calendar-different published source forecasts; 2000 forecast explicitly qualified/ambiguous and 2001 forecast clear; 'six yao' of others is NOT a new Qimen cast"),
 dict(key="us_election_2000",n=["十"],title="2000年美国总统布什戈尔选举",domain="politics_elections",
  facets=["politics_elections","litigation"],ranges=[(605,740)],q=(611,615),
  charts=[(617,"2000-10-15","己亥"),(657,"2000-11-10","己酉"),(705,"2000-12-09","丁酉")],
  pred=[637,683,727],feedback=[729,731,733,735],posthoc=[737,739],
  notes="Three forecasts of same election, each with newly available Florida recount disclosures; distinct cast ≠ independent event/sample"),
 dict(key="israel_2001",n=["十一"],title="2001年以色列总理沙龙巴拉克选举",domain="politics_elections",
  facets=["politics_elections"],ranges=[(741,778)],q=(743,747),
  charts=[(749,"2001-02-06","乙酉")],pred=[775],feedback=[777],posthoc=[],
  notes="Author reports election news next day"),
 dict(key="shijiazhuang_2001",n=["十二"],title="2001年石家庄3.16爆炸案两候选时辰",domain="criminal_case",
  facets=["criminal_case"],ranges=[(779,850)],q=(781,785),
  charts=[(787,"2001-03-16","甲寅"),(801,"2001-03-16","乙卯")],
  pred=[825,835,837],feedback=[839,841,843,845],posthoc=[847,849],
  notes="Two alternative casts due to unknown 5AM precise boundary, not two crimes or independent forecasts; source reports arrest Mar23 and newspaper Mar24")
]
STARTS=[21,57,109,143,187,227,281,323,351,391,425,511,565,617,657,705,749,787,801,865]
ANNUAL_FORECAST=[(477,"weather_environment_health"),
                 (479,"macroeconomy"),(481,"industries_and_employment"),
                 (483,"international_conflict"),(485,"political_leadership"),
                 (487,"world_affairs"),(489,"weather_war_seasonality")]
def sha(b):return hashlib.sha256(b).hexdigest()
def j(x):return json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(",",":"))
def t(ls,a,b=None):
 b=a if b is None else b
 if not 1<=a<=b<=len(ls):raise ValueError(("Invalid source lines",a,b))
 return "\n".join(ls[a-1:b])
def validate_source(b):
 if sha(b)!=SOURCE_SHA:raise ValueError("Unexpected uploaded full source SHA")
 ls=b.decode("utf8").splitlines()
 if len(ls)!=913 or ls[:3]!=["第一章","","热门话题预测评析"]:
  raise ValueError("Wrong full source or truncated chapter")
 if not ls[-1].endswith("是需要我们研究、发展、改进的课题"):
  raise ValueError("Original book ending was lost")
 headers=[i for i,x in enumerate(ls,1) if re.match(r"^\([一二三四五六七八九十]+\)",x)]
 if headers!=[5,101,171,255,309,379,457,499,557,605,741,779,851]:
  raise ValueError(("Expected 13 numbered original topics",headers))
 charts=[i for i,x in enumerate(ls,1) if x.startswith("巽四宫") and "│" in x]
 if charts!=STARTS:raise ValueError(("20 genuine original chart starts must match",charts))
 return ls
def chart(ls,start):
 out=[]
 for row in range(3):
  line=start+row*4
  vals=[[x.strip() for x in ls[line+k-1].split("│")] for k in range(3)]
  if any(len(x)!=3 for x in vals):raise ValueError(("Original 3-column figure malformed",start,line))
  if row<2 and "┼" not in ls[line+2]:
   raise ValueError(("Original Unicode separator missing",start,row))
  for col in range(3):
   palace=PAL[row*3+col];name=NAMES[row*3+col]
   head=vals[0][col]
   if not head.startswith(name):raise ValueError(("Source palace label wrong",start,palace))
   god=head[len(name):].strip();door=vals[1][col];star=vals[2][col]
   if palace==5 and (god or star or not door):raise ValueError("Do not fill original center star/deity/door")
   if palace!=5 and (not door or not star):raise ValueError(("Missing literal source",start,palace))
   literal="\n".join((head,door,star))
   out.append({"palace":palace,"line":line+col,"start":line,"end":line+2,
    "name":name,"god":god,"door":door,"star":star,
    "literal":literal,"sha":sha(literal.encode("utf8"))})
 if sorted(x["palace"] for x in out)!=list(range(1,10)):raise ValueError("Not 9 palaces")
 return out
def parsed(ls):
 out=[];seen=[]
 for e in EVENTS:
  casts=[]
  for n,(start,date,hour) in enumerate(e["charts"]):
   cells=chart(ls,start)
   casts.append({"key":"primary" if not n else "additional_"+str(n),
    "source_line":start,"source_end_line":start+10,"date":date,"hour":hour,
    "source_hash":sha(t(ls,start,start+10).encode("utf8")),"cells":cells,
    "source_metadata_line":start-2})
   seen.append(start)
  num=[]
  for a,b in e["ranges"]:
   num += [i for i in range(a,b+1) if re.match(r"^\(\d+\)",ls[i-1])]
  out.append({**e,"id":"kaiwu.hot."+e["key"],"casts":casts,"steps":num})
 if sorted(seen)!=sorted(STARTS):raise ValueError(("Expected all 20 charts exactly once across event families",seen))
 if len(out)!=13 or sum(len(e["casts"]) for e in out)!=20:
  raise ValueError("Missing original same-event grouping")
 if sum(len(e["steps"]) for e in out)!=97:raise ValueError(("Author numbered steps changed",sum(len(e["steps"]) for e in out)))
 return out
def old_rows(old,db):
 for (table,) in old.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"):
  cols=[x[1] for x in old.execute('PRAGMA table_info("'+table+'")')]
  names=",".join('"'+c+'"' for c in cols)
  before=list(old.execute('SELECT '+names+' FROM "'+table+'"'))
  after=set(db.execute('SELECT '+names+' FROM "'+table+'"'))
  if not all(row in after for row in before):raise ValueError("Old historical source data changed: "+table)
def step_phase(e,line):
 if e["key"]=="taiwan_2000" and line>=543:return "source_retrospective_corrected_after_election"
 if e["key"]=="clinton" and line>=90:return "retrospective_editor_explanation"
 if e["key"]=="nato" and line<139:return "source_editor_revised_original_respondent_analysis"
 if e["key"]=="women_world_cup" and line>=377:return "post_feedback_subject_home_resolution"
 if e["key"]=="beijing_2008" and line>=903:return "post_feedback_editor_discussion"
 return "source_original_numbered_analysis"
def phase(db,ls,e,name,kind,a,b,meta=None):
 literal=t(ls,a,b)
 db.execute("""INSERT INTO hot_topic_source_phases(chapter_key,case_id,phase_key,
 phase,start_line,end_line,original_text,original_sha256,phase_metadata_json)
 VALUES (?,?,?,?,?,?,?,?,?)""",
 (CHAPTER,e["id"],name,kind,a,b,literal,sha(literal.encode("utf8")),
  j({"book_source_accepted_by_user":True,"phase_scope":kind,
     "cannot_use_future_feedback_as_earlier_context":True,**(meta or {})})))
def add(db,ls,sid,e):
 cid=e["id"];known=t(ls,*e["q"])
 forecasts="\n".join(t(ls,x) for x in e["pred"])
 feedback="\n".join(t(ls,x) for x in e["feedback"]) if e["feedback"] else ""
 reasoning="\n\n".join(t(ls,x) for x in e["steps"])
 no_chart=not e["casts"]
 db.execute("""INSERT INTO cases(case_id,section_id,event_family_id,domain_id,
 known_before,author_yongshen_steps,author_judgment,later_feedback,reviewed)
 VALUES (?,?,?,?,?,?,?,?,1)""",(cid,sid,cid,e["domain"],known,reasoning,forecasts,feedback))
 phase(db,ls,e,"original_known","initial_question",*e["q"])
 for ix,(n,x) in enumerate(zip(e["pred"],e["pred"])):
  phase(db,ls,e,"author_prediction_"+str(ix+1),"source_book_prediction",n,x,
   {"prior_correction":e["key"]!="taiwan_2000" or n<541})
 for ix,n in enumerate(e["feedback"]):
  phase(db,ls,e,"reported_outcome_"+str(ix+1),"book_reported_result",n,n)
 for ix,n in enumerate(e["posthoc"]):
  phase(db,ls,e,"post_feedback_note_"+str(ix+1),
   "editor_post_feedback_or_retrospective",n,n)
 for cast in e["casts"]:
  phase(db,ls,e,"chart_"+cast["key"],"original_printed_chart",
   cast["source_line"],cast["source_end_line"],
   {"cast_date":cast["date"],"hour":cast["hour"],"all_casts_one_event":True})
 # explicitly source-documented interim, arrived after first cast but before second
 if e["key"]=="river_jump":
  phase(db,ls,e,"later_information_before_second_cast","new_disclosure",215,217)
 if e["key"]=="us_election_2000":
  phase(db,ls,e,"florida_recount_update_before_second","new_disclosure",639,653)
  phase(db,ls,e,"later_judicial_news_before_third","new_disclosure",685,703)
 if e["key"]=="beijing_2008":
  phase(db,ls,e,"second_2001_bid_update","new_disclosure",853,863)
 p={"event_source_ranges":e["ranges"],"original_topic_numbers":e["n"],
  "real_printed_charts":len(e["casts"]),"source_notes":e["notes"],
  "book_source_accepted_by_user_without_individual_manual_review":True,
  "not_independently_verified_scientific_method":True,
  "original_initial_predictive_error_preserved":bool(e.get("explicit_error")),
  "cross_book_event_dedup_from_existing":False,
  "positive_data_must_obey_temporal_leakage_and_book_errors":True}
 db.execute("""INSERT INTO historical_case_protocol(case_id,completeness,
 published_chart_verification,feedback_independently_verified,
 eligible_blind_test,case_source_sha256,metadata_json)
 VALUES (?,?,'book_verbatim_not_independently_recast',0,?,?,?)""",
 (cid,"original_annual_forecast_no_cast_or_feedback" if no_chart else
  "all_verbatim_book_source_casts_and_story",int(bool(e["casts"]) and not e.get("explicit_error")),
  SOURCE_SHA,j(p)))
 db.execute("""INSERT INTO historic_book_case_acceptance(case_id,source_book,source_chapter_key,
 source_documented_outcome,source_has_explicit_initial_error,metadata_json)
 VALUES (?,'kaiwu',?,?,?,?)""",
 (cid,CHAPTER,"no_post_forecast_book_feedback" if not e["feedback"] else
  "author_explicit_initial_error_with_posthoc_correction" if e.get("explicit_error")
  else "book_reported_outcome_accepted",int(bool(e.get("explicit_error"))),j(p)))
 for facet in e["facets"]:
  db.execute("""INSERT INTO hot_topic_multifacet_domains(chapter_key,case_id,domain_id,domain_role,topic)
   VALUES (?,?,?,?,?)""",(CHAPTER,cid,facet,"primary" if facet==e["domain"] else "related",e["title"]))
 if e["domain"] not in e["facets"]:raise ValueError("Primary domain must appear among facets")
 for ic,cast in enumerate(e["casts"]):
  key=cast["key"];l=cast["source_line"]
  db.execute("""INSERT INTO hot_topic_event_source_witnesses(chapter_key,case_id,source_group_key,
    cast_key,source_chart_start,source_chart_end,source_chart_sha256,
    original_book_phase,original_cast_metadata,event_domain,event_facets_json,
    outcome_known_before_this_cast,note)
    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
    (CHAPTER,cid,"/".join(e["n"]),key,l,l+10,cast["source_hash"],
     "same_event_later_context" if ic else "first_book_cast",
     t(ls,cast["source_metadata_line"]),e["domain"],j(e["facets"]),0,e["notes"]))
  if ic:
   db.execute("""INSERT INTO historical_case_additional_casts(case_id,cast_key,
     cast_datetime_description,calendar_date,hour_ganzhi,source_chart_start,notes)
     VALUES (?,?,?,?,?,?,?)""",
     (cid,key,cast["date"]+" "+cast["hour"],cast["date"],cast["hour"],l,
      "Same event family, separate genuine printed Qimen chart; source no fabricated certainty"))
  for cell in cast["cells"]:
   pal=cell["palace"];center=pal==5
   db.execute("""INSERT INTO hot_topic_witness_palaces(chapter_key,case_id,cast_key,palace,
    source_start_line,source_end_line,palace_label,deity_raw,door_raw,
    star_raw,literal_original,literal_sha256)
    VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
    (CHAPTER,cid,key,pal,cell["start"],cell["end"],cell["name"],cell["god"],
     cell["door"],cell["star"],cell["literal"],cell["sha"]))
   if ic:
    db.execute("""INSERT INTO historical_case_additional_cast_cells(case_id,cast_key,
    palace,source_line,palace_label_raw,deity_raw,door_position_raw,star_position_raw)
    VALUES (?,?,?,?,?,?,?,?)""",
    (cid,key,pal,cell["line"],cell["name"],cell["god"],cell["door"],cell["star"]))
   else:
    db.execute("""INSERT INTO historical_chart_cells(case_id,palace,source_line,
    palace_label_raw,deity_raw,door_position_raw,star_position_raw,source_status)
    VALUES (?,?,?,?,?,?,?,'book_verbatim_political_sports_crime_not_recast')""",
    (cid,pal,cell["line"],cell["name"],cell["god"],cell["door"],cell["star"]))
   db.execute("""INSERT INTO historical_palace_standardization(case_id,cast_key,
    palace,center_stem,source_of_center_stem,standard_deity,standard_door,standard_star,
    normalized_status,original_raw_integrity_checked,method_reference,derived_host_palace,
    derived_host_source)
    VALUES (?,?,?,?,?,?,?,?,?,1,?,?,?)""",
    (cid,key,pal,cell["door"] if center else None,
     "literal_center_only" if center else "not_center",
     None if center else cell["god"],None if center else cell["door"],
     None if center else cell["star"],
     "original_center_without_fabricated_star_door_deity" if center else "literal_original_chart",
     "kaiwu_hot_topics_book_source",2 if center else None,
     "source_defined_shijia_center_host_kun_not_source_fields" if center else None))
 for ix,line in enumerate(e["steps"],1):
  src=t(ls,line);meta={"source_line":line,"phase":step_phase(e,line),
    "source_book_accepted_by_user":True,
    "first_predictive_error_not_to_be_relabelled":bool(e.get("explicit_error")),
    "modern_real_world_accuracy_not_independently_verified":True}
  db.execute("""INSERT INTO historical_case_reasoning(case_id,step_number,source_line,
  author_analysis_original,short_method_topic,metadata_json)
  VALUES (?,?,?,?,?,?)""",(cid,ix,line,src,meta["phase"],j(meta)))
  db.execute("""INSERT INTO historical_case_reasoning_trace(case_id,step_number,
  source_line,evidence_json,review_status,positive_training_eligible)
  VALUES (?,?,?,?,'book_source_user_accepted_no_individual_approval',0)""",
  (cid,ix,line,j(meta)))
  # Metadata conveys provenance; older common concept IDs remain untouched.
  cc="hot_topics:"+e["key"]+":step"+str(ix)
  db.execute("""INSERT INTO semantic_assertions(chapter_key,concept_id,kind,relation,
  source_start_line,source_end_line,metadata_json,original_excerpt,review_status)
  VALUES (?,?,?,?,?,?,?,?,?)""",
  (CHAPTER,cc,"source_case_reasoning","source_book_cited",line,line,j(meta),src,"draft"))
  db.execute("""INSERT INTO cross_book_concept_tracks(chapter_key,concept_id,
  source_start_line,source_end_line,source_section_id,source_sha256,excerpt_sha256,
  track_id,relation_to_prior,comparison_state,normalized_json,review_status)
  VALUES (?,?,?,?,?,?,?,?,?,'book_source_accepted_method_independent_validation_not_asserted',?,'draft')""",
  (CHAPTER,cc,line,line,sid,SOURCE_SHA,sha(src.encode("utf8")),
   "kaiwu:hot_topics:source_v1:"+e["domain"],"additional_exposition",j(meta)))
 db.execute("""INSERT INTO historical_case_review_audit(case_id,original_steps,
 mechanical_step_trace,human_complete_step_chains,review_status,warning)
 VALUES (?,?,?,0,'book_source_accepted_no_user_manual_gate',?)""",
 (cid,len(e["steps"]),len(e["steps"]),e["notes"]))
 if e.get("explicit_error"):
  original=t(ls,533);correction=t(ls,543,555)
  db.execute("""INSERT INTO hot_topic_correction_audits(chapter_key,case_id,
  initial_line,book_error_admission_line,book_correction_line,initial_source_prediction,
  correction_source_original) VALUES (?,?,533,543,545,?,?)""",
  (CHAPTER,cid,original,correction))
  db.execute("""INSERT INTO historical_case_book_verdicts(event_family_id,primary_case_id,
  verdict,explicit_source_correction,source_correction_lines_json,feedback_source_lines_json,
  independent_external_verification,app_output_protocol,evidence_review_status,note)
  VALUES (?,?,'author_book_error_explicit',1,?,?, 'not_verified',
  'single_answer_for_one_cast','book_source_user_accepted',?)""",
  (cid,cid,j([543,545,547]),j(e["feedback"]),e["notes"]))
 elif e["feedback"]:
  db.execute("""INSERT INTO historical_case_book_verdicts(event_family_id,primary_case_id,
  verdict,explicit_source_correction,source_correction_lines_json,feedback_source_lines_json,
  independent_external_verification,app_output_protocol,evidence_review_status,note)
  VALUES (?,?,'author_book_success_default',0,'[]',?,'not_verified',
  'single_answer_for_one_cast','book_source_user_accepted',?)""",
  (cid,cid,j(e["feedback"]),e["notes"]))
 if no_chart:
  for line,topic in ANNUAL_FORECAST:
   raw=t(ls,line)
   db.execute("""INSERT INTO hot_topic_annual_forecast_parts(chapter_key,case_id,
    source_line,forecast_domain,literal_original,source_sha256)
    VALUES (?,?,?,?,?,?)""",(CHAPTER,cid,line,topic,raw,sha(raw.encode("utf8"))))
def build(base,source,output,index_dir):
 base,source,output,index_dir=map(Path,(base,source,output,index_dir))
 if output.exists():raise ValueError("Refuse overwrite of full published database")
 if sha(base.read_bytes())!=BASE_SHA:raise ValueError("Wrong latest full parent SQLite SHA")
 raw=source.read_bytes();ls=validate_source(raw);items=parsed(ls)
 output.parent.mkdir(parents=True,exist_ok=True)
 with sqlite3.connect("file:"+str(base)+"?mode=ro",uri=True) as old,sqlite3.connect(output) as db:
  old.backup(db)
  db.executescript((ROOT/"schema/migrations/022_hot_topics_shared_domains.sql").read_text("utf8"))
  db.execute("PRAGMA foreign_keys=ON")
  with db:
   if db.execute("SELECT COUNT(*) FROM sections WHERE book_id='kaiwu'").fetchone()[0]!=6:
    raise ValueError("Expected precisely prior six Kaiwu sources")
   if db.execute("SELECT 1 FROM sections WHERE book_id='kaiwu' AND section_key=?",(SECTION,)).fetchone():
    raise ValueError("Chapter source already imported")
   db.execute("""INSERT INTO sections(book_id,section_key,title,original_text,sha256,
    content_version,reviewed) VALUES ('kaiwu',?,?,?,?,1,1)""",
    (SECTION,TITLE,raw.decode("utf8"),SOURCE_SHA))
   sid=db.execute("SELECT last_insert_rowid()").fetchone()[0]
   db.execute("""INSERT INTO chapter_knowledge(chapter_key,book_id,title,
    source_sha256,source_length_bytes,knowledge_version,review_status)
    VALUES (?,'kaiwu',?,?,?,'1','approved')""",(CHAPTER,TITLE,SOURCE_SHA,len(raw)))
   for e in items:add(db,ls,sid,e)
   db.execute("""INSERT INTO chapter_archival_versions(archive_label,baseline_sha256,new_db_sha256,
    contains_complete_private_copyright_source,snapshot_type,created_utc,repo_public_archive_policy)
    VALUES (?, ?,NULL,1,'user_accepted_book_cases_mixed_domain_multi_cast_preserved',
    '2026-10-20','user_authorized_public_full_sqlite_versions')""",
    ("shenqi21_kaiwu_hot_topics_121_historical_events",BASE_SHA))
  old_rows(old,db)
  if db.execute("PRAGMA integrity_check").fetchone()[0]!="ok" or db.execute("PRAGMA foreign_key_check").fetchall():
   raise ValueError("Failed full SQLite integrity check")
  expected={"sections":28,"cases":121,
    "historical_chart_cells":1080,
    "historical_case_additional_casts":17,
    "historical_case_additional_cast_cells":153,
    "historical_palace_standardization":1233,
    "historical_case_reasoning":613,"historical_case_reasoning_trace":613,
    "semantic_assertions":2287,"cross_book_concept_tracks":1030,
    "cross_book_example_references":43,
    "hot_topic_event_source_witnesses":20,"hot_topic_witness_palaces":180,
    "hot_topic_multifacet_domains":sum(len(e["facets"]) for e in items),
    "hot_topic_annual_forecast_parts":7,
    "hot_topic_correction_audits":1,
    "historic_book_case_acceptance":13}
  got={key:db.execute('SELECT COUNT(*) FROM "'+key+'"').fetchone()[0] for key in expected}
  if got!=expected:raise ValueError(("Unexpected source preservation counts",got,expected))
  if db.execute("SELECT COUNT(*) FROM historical_case_book_verdicts WHERE verdict='author_book_error_explicit'").fetchone()[0]!=7:
   raise ValueError("Original six older errors and Taiwan explicit new error must remain")
  if db.execute("SELECT COUNT(*) FROM cases WHERE domain_id='sports_competition' AND case_id LIKE 'kaiwu.hot.%'").fetchone()[0]!=3:
   raise ValueError("Sports same-domain consolidation lost")
  if db.execute("SELECT COUNT(*) FROM cases WHERE domain_id='criminal_case' AND case_id LIKE 'kaiwu.hot.%'").fetchone()[0]!=3:
   raise ValueError("Crime same-domain consolidation lost")
  if db.execute("SELECT COUNT(*) FROM cases WHERE case_id='kaiwu.hot.beijing_2008'").fetchone()[0]!=1:
   raise ValueError("Beijing two sections are the same event")
  if db.execute("SELECT COUNT(*) FROM historical_case_additional_casts WHERE case_id='kaiwu.hot.us_election_2000'").fetchone()[0]!=2:
   raise ValueError("USA 2000 three prints are one event")
  if db.execute("SELECT COUNT(*) FROM historical_chart_cells WHERE case_id='kaiwu.hot.world_outlook_2000'").fetchone()[0]:
   raise ValueError("Annual forecast has no printed board")
  db.execute("VACUUM");db.commit()
  if db.execute("PRAGMA integrity_check").fetchone()[0]!="ok" or db.execute("PRAGMA foreign_key_check").fetchall():
   raise ValueError("VACUUM final integrity failure")
 index_dir.mkdir(parents=True,exist_ok=True)
 manifest={"schema":"wengua_multibook_mixed_topic_source_archive_v1",
  "chapter_key":CHAPTER,"title":TITLE,"source_book":"kaiwu",
  "source_sha256":SOURCE_SHA,"source_utf8_bytes":len(raw),
  "source_lines":len(ls),"numbered_original_topics":13,
  "source_original_printed_casts":20,
  "new_distinct_historical_event_families":13,
  "new_historical_event_families_with_casts":12,
  "annual_forecast_without_any_printed_cast":1,
  "author_numbered_source_steps":97,
  "two_chapters_same_beijing_2008_event":True,
  "twenty_original_charts_independently_stored_under_correct_family":True,
  "explicit_source_initial_failure":1,
  "new_book_case_outcomes_accepted_by_user":True,
  "manual_case_by_case_user_approval_required":False,
  "reported_outcomes_are_book_source_not_external_validation":True,
  "book_counts":{"shenqi":21,"kaiwu":7},
  "total_source_sections":28,"total_historical_events":121,
  "total_historical_printed_casts":137,
  "source_original_nine_palace_cells_new":180,
  "all_old_rows_preserved":True,"baseline_sha256":BASE_SHA,
  "output_sha256":sha(output.read_bytes()),"cumulative_counts":got}
 def save(name,data):
  (index_dir/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 save("chapter_manifest.json",manifest)
 save("case_index.json",{"source_sha256":SOURCE_SHA,"cases":[
  {k:v for k,v in e.items() if k!="casts"}|
  {"casts":[{k:v for k,v in c.items() if k!="cells"} for c in e["casts"]]}
  for e in items]})
 save("figure_index.json",{"source_sha256":SOURCE_SHA,"cases":[
  {"case_id":e["id"],"domain_id":e["domain"],"figures":e["casts"]} for e in items]})
 save("topic_domains.json",{"source_sha256":SOURCE_SHA,"cases":[
  {"event_id":e["id"],"main_domain":e["domain"],"facets":e["facets"],
   "source_sections":e["n"],"same_event_multi_casts":len(e["casts"])} for e in items]})
 save("source_audit.json",{"source_sha256":SOURCE_SHA,
  "taiwan_initial_failure_lines":[533,541,543,545,547],
  "women_world_cup_home_team_disambiguated_post_result_line":377,
  "2000_annual_forecast_without_cast_or_feedback":True,
  "usa_2000_three_different_time_casts_same_event":True,
  "beijing_2008_two_sections_same_historical_bid":True,
  "nato_first_cast_analysis_revised_by_editor_line":121,
  "shijiazhuang_two_hour_boards_are_alternative_causality_not_two_events":True,
  "full_original_preserved_no_extrapolation_or_manual_case_gate":True,
  "all_previous_v1_source_rows_unchanged":True,
  "source_case_acceptance_is_not_independent_scientific_validation":True})
 return manifest
def main():
 a=argparse.ArgumentParser()
 for n in ("base","source","output","index-dir"):a.add_argument("--"+n,required=True)
 x=a.parse_args()
 print(json.dumps(build(x.base,x.source,x.output,x.index_dir),ensure_ascii=False,indent=2))
if __name__=="__main__":main()
