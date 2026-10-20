"""Append Kaiwu chapter 3 casting lessons to the immutable 23-source WenguaApp V1.

This is SOURCE research, not astronomical validation or approved divination.
Twelve literal figures (108 cells) and four worked educational board examples
are stored OUTSIDE historical cases/charts. Missing center fields are never filled.
"""
from __future__ import annotations
import argparse,hashlib,json,re,sqlite3
from pathlib import Path
from collections import Counter
from src.wengua.casting_shenqi import layout_from_explicit_bureau

ROOT=Path(__file__).resolve().parents[1]
BASE_SHA="7b6cbd1d82cb87175d5610aec4f21409658e8fa872ae9f5985a1627ae66a2726"
SOURCE_SHA="12250805624a0074858412fa5d5b0ee66c5b0a31d77dac16b7152005429d49c0"
BASE_NAME="WenguaApp_神奇之门21章_开悟之门2章_103案例_完整研究库.sqlite3"
NEW_NAME="WenguaApp_神奇之门21章_开悟之门3章_103案例_完整研究库.sqlite3"
CHAPTER="kaiwu/paper_grid_casting_ch03/v1"
SECTION="paper_grid_casting_ch03"
TRACK="kaiwu:source_v1:shijia_zhuanpan"
PALACE_SEQ=(4,9,2,3,5,7,8,1,6)
PALACE_LABELS=("巽4","离9","坤2","震3","中5","兑7","艮8","坎1","乾6")
FIGURES={
 27:("yin5_earth","earth_plate","yin5_jia_shen"),
 43:("yin5_value_star","heaven_star_partial","yin5_jia_shen"),
 55:("yin5_heaven_fuyin","heaven_plate","yin5_jia_shen"),
 69:("yin5_human_fuyin","door_plate","yin5_jia_shen"),
 81:("yin5_ding_hai_door","door_only","yin5_ding_hai"),
 92:("yang_counterfactual_ding_hai_door","door_only","yang5_ding_hai_counterfactual"),
 108:("yin5_deity_plate","four_layer_intermediate","yin5_jia_shen"),
 122:("yang5_deity_counterfactual","four_layer_intermediate","yang5_jia_shen_counterfactual"),
 139:("yin5_jia_shen_four_layer","complete_four_layer","yin5_jia_shen"),
 151:("yin5_ding_hai_four_layer","complete_four_layer","yin5_ding_hai"),
 168:("yin5_gui_wei_incomplete","simplified_chart_no_deities","yin5_gui_wei"),
 180:("yang2_gui_hai_incomplete","simplified_chart_no_deities","yang2_gui_hai"),
}
# Didactic examples are SOURCE printouts, not historical successes.
WORKED={
 "yin5_jia_shen":("yin",5,"甲申",139,"乙卯","2001-08-20",True,"甲申",3,3),
 "yin5_ding_hai":("yin",5,"丁亥",151,"乙卯","2001-08-20",True,"甲申",8,9),
 "yin5_gui_wei":("yin",5,"癸未",168,"乙卯","2001-08-20",False,"甲戌",9,4),
 "yang2_gui_hai":("yang",2,"癸亥",180,"戊申",None,False,"甲寅",7,7),
}
# Nonhistorical counterfactual diagrams are deliberately not added to WORKED.
STEPS=[(1,3,19,"ganzhi_conversion"),(2,21,22,"solar_term_futou_and_bureau"),
       (3,24,34,"nine_instruments_earth_plate"),(4,36,38,"xun_head_zhifu_zhishi"),
       (5,40,63,"value_star_follow_stem_and_star_ring"),
       (6,65,102,"value_door_nine_position_count_then_eight_ring"),
       (7,104,132,"eight_deities_follow_star_dun_direction")]
FIVE_MOUSE=[("甲己","甲",9),("乙庚","丙",9),("丙辛","戊",10),
 ("丁壬","庚",10),("戊癸","壬",11)]
EARTH={4:"己",9:"癸",2:"辛",3:"庚",5:"戊",7:"丙",8:"丁",1:"壬",6:"乙"}
HOME_STARS={1:"天蓬星",2:"天芮星",3:"天冲星",4:"天辅星",5:"天禽星",
            6:"天心星",7:"天柱星",8:"天任星",9:"天英星"}
HOME_DOORS={1:"休门",2:"死门",3:"伤门",4:"杜门",6:"开门",7:"惊门",8:"生门",9:"景门"}
DEITIES=("值符","螣蛇","太阴","六合","白虎","玄武","九地","九天")
RULES=[
 ("hour_ganzhi_with_five_mouse",13,15,"five_mouse_from_day_stem","depends_on_trusted_date"),
 ("jieqi_boundary_not_lunar_day_one",5,5,"annual_month_jieqi","not_precise_device_calendar"),
 ("futou_and_mid_yuan",22,22,"futou_jia_yin_middle","example_specific_2001_08_20"),
 ("yin_earth_sequence",25,25,"jiazi_wu_in_5_negative_palace_sequence","depends_on_bureau"),
 ("xun_zhifu_zhishi",36,37,"xun_hidden_instrument_source_palace","center_host_boundary"),
 ("nine_star_ring",40,40,"star_perimeter_clockwise_both_yin_yang","center_tianqin_hosts_kun"),
 ("value_star_with_hour_stem",40,41,"move_value_star_to_hour_symbol_earth_palace","with_hidden_stem_for_jia"),
 ("star_fuyin_on_jia",52,53,"jia_xun_head_example_returns_home","not_general_cause_validation"),
 ("door_fuyin_on_jia",66,67,"jia_shen_example_returns_home","not_general_cause_validation"),
 ("timed_zhishi_nine_palace_steps",66,66,"zhishi_count_nine_numbers_dun_direction","not_eight_ring"),
 ("yin_zhishi_three_to_nine",79,79,"shen_to_hai_three_steps_negative","known_examples_only"),
 ("door_perimeter_after_target",79,79,"rotate_all_doors_on_eight_outer_palaces","independent_of_nine_count"),
 ("zhuanpan_not_feipan",90,90,"rotary_vs_jump_palace_rule","school_shijia_zhuanpan"),
 ("yang_zhishi_three_to_six",101,101,"shen_to_hai_three_steps_positive","counterfactual_example"),
 ("door_two_distinct_algorithms",102,102,"nine_for_value_and_eight_for_other_doors","no_blind_nine_number_rotation"),
 ("deity_follow_zhifu_star",104,106,"small_zhifu_follows_value_star","not_value_door"),
 ("yin_deity_counterclockwise",105,106,"yin_deities_counterclockwise","eight_outer_palaces_only"),
 ("yang_deity_clockwise",105,120,"yang_deities_clockwise","eight_outer_palaces_only"),
 ("shijia_four_layer_finished",134,137,"earth_heaven_human_deity","no_commercial_reading_approval"),
 ("all_jia_hours_source_fuyin",163,163,"author_says_star_door_both_fuyin","center_host_not_exhaustively_tested"),
 ("all_gui_hours_door_source_fuyin",164,166,"author_says_door_fuyin_not_necessarily_star","center_host_not_exhaustively_tested"),
 ("wu_gui_days_gui_hai_both_fuyin",177,178,"wu_or_gui_day_at_gui_hai_both","book_claim_not_externally_validated"),
 ("keep_original_center_stem",139,147,"no_independent_center_door_or_deity","five_center_host_derived_only"),
 ("calendar_independent_ephemeris_required",3,6,"never_infer_solar_term_from_unverified_time","real_year_month_day_must_be_validated"),
]
def digest(raw):return hashlib.sha256(raw).hexdigest()
def canon(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(",",":"))
def extract(lines,a,b=None):
 b=a if b is None else b
 if not 1<=a<=b<=len(lines):raise ValueError(("Source line bounds",a,b,len(lines)))
 return "\n".join(lines[a-1:b])
def original_lines(raw):
 if digest(raw)!=SOURCE_SHA:raise ValueError("Exact chapter source SHA mismatch")
 ls=raw.decode("utf-8").splitlines()
 if len(ls)!=189 or ls[0]!="纸上井字格起局法的步骤" or not ls[188].startswith("在奇门起局中"):
  raise ValueError("Original source chapter boundaries changed")
 for step,a,b,term in STEPS:
  if not ls[a-1].startswith("第"+("一二三四五六七"[step-1])+"步"):
   raise ValueError(("Seven ordered original method steps invalid",step,a))
 return ls
def read_figures(lines):
 """Parse exactly 12 genuine 3x3 printed TEXT figures with source row spans.

 Each center is stored as printed (a bare stem or "(无门)"); never add layers.
 Multiline palace text is joined from the same printed cell, no inferred values.
 """
 result=[]
 for caption_ln,(key,kind,sample_key) in FIGURES.items():
  caption=lines[caption_ln-1]
  if not caption.startswith("（") or not caption.endswith("）"):
   raise ValueError(("Original caption mismatch",caption_ln,caption))
  start=caption_ln+1
  if not lines[start-1].startswith("+"):
   raise ValueError(("Original chart border mismatch",caption_ln))
  rows=[];current=[];i=start
  while i<=len(lines) and (lines[i-1].startswith("+") or lines[i-1].startswith("|")):
   line=lines[i-1]
   if line.startswith("+"):
    if current:rows.append(current);current=[]
   else:
    cells=[v.strip() for v in line.split("|")[1:-1]]
    if len(cells)!=3:raise ValueError(("Chart must have three columns",caption_ln,i))
    current.append((i,cells))
   i+=1
  if current:rows.append(current)
  if len(rows)!=3:raise ValueError(("Chart should have three row bands",caption_ln,len(rows)))
  all_cells=[]
  for row_num,physical in enumerate(rows):
   for col in range(3):
    palace=PALACE_SEQ[row_num*3+col]
    label=PALACE_LABELS[row_num*3+col]
    snippets=[(source_ln,arr[col]) for source_ln,arr in physical if arr[col]]
    if not snippets or not snippets[0][1].startswith(label):
     raise ValueError(("Wrong original palace label",caption_ln,palace,snippets))
    raw="\n".join(q for _,q in snippets)
    if palace==5:
     if any(x in raw for x in ("／","天芮","天禽","神盘","值符／")):
      raise ValueError(("Center cannot be fabricated",caption_ln,raw))
    all_cells.append({"palace":palace,"palace_label_raw":label,
      "source_start_line":snippets[0][0],"source_end_line":snippets[-1][0],
      "original_cell_text":raw,"original_cell_sha256":digest(raw.encode("utf-8")),
      "source_is_center_bare_or_no_door":palace==5})
  if len(all_cells)!=9:raise ValueError("Missing literal nine text cells")
  figure_original=extract(lines,caption_ln,i-1)
  result.append({"figure_key":key,"caption":caption,"caption_line":caption_ln,
   "source_end_line":i-1,"original_figure_sha256":digest(figure_original.encode("utf-8")),
   "pedagogical_stage":kind,"example_key":sample_key,
   "actual_historical_prediction":False,"cells":all_cells,
   "complete_deity_information":kind=="complete_four_layer",
   "source_chart_is_not_case_from_book":True})
 if len(result)!=12 or sum(len(f["cells"]) for f in result)!=108:
  raise ValueError("All twelve source tables / 108 cells required")
 return result

def source_engine_consistency(figures):
 """Do not assert 'verified' calendar; compare all 8 peripheral cells with the
 existing RESEARCH layout from supplied explicit dun/ju/hour, not wall clock.
 Two end-chapter diagrams have no deity fields and are not filled in.
 """
 by_key={x["caption_line"]:x for x in figures}
 reports=[]
 for sample_key,(dun,ju,hour,ln,day,date,full,head,value_star_p,value_door_p) in WORKED.items():
  board=layout_from_explicit_bureau(dun=dun,ju=ju,hour_ganzhi=hour)
  if (board["xun_shou"],board["value_star_palace"],board["value_door_palace"])!=(head,value_star_p,value_door_p):
   raise ValueError(("Value star or door disagree with book",sample_key))
  fig=by_key[ln]
  checked=0
  for cell in fig["cells"]:
   pal=cell["palace"]
   if pal==5:
    # Source retains only its literal stem. Derived host not printed there.
    if board["palaces"]["5"]["earth_stem"] not in cell["original_cell_text"]:
     raise ValueError(("Center literal stem differs",sample_key))
    continue
   state=board["palaces"][str(pal)]
   source_body=cell["original_cell_text"].replace("\n","")
   short_door=state["door"][0]+state["heaven_stars"][0]["carried_stem"]
   short_star=state["heaven_stars"][0]["star"][1]+state["earth_stem"]
   if short_door not in source_body or short_star not in source_body:
    raise ValueError(("Peripheral source/engine discrepancy",sample_key,pal,short_door,short_star,source_body))
   if full and state["deity"] not in source_body:
    raise ValueError(("Missing printed deity",sample_key,pal,state["deity"]))
   checked+=1
  if checked!=8:raise ValueError("Expected eight peripheral matched cells")
  reports.append({"example_key":sample_key,"source_caption_line":ln,
   "day_ganzhi":day,"source_civil_date":date,"dun":dun,"ju":ju,"hour_ganzhi":hour,
   "xun_shou":head,"value_star_palace":value_star_p,
   "value_door_palace":value_door_p,"checked_peripheral_palaces":8,
   "original_center_stem_unmodified":True,
   "original_deities_present":full,
   "consistency":"source_text_matches_existing_explicit_bureau_layout",
   "not_astronomical_calendar_verification":True,
   "not_independent_historical_prediction":True})
 return reports

def source_assertions(lines,figure_list):
 out=[];seen=set()
 def add(cid,kind,line,end=None,conditions=None,relation="clarifies",track=None):
  end=line if end is None else end
  raw=extract(lines,line,end)
  key=(cid,line)
  if key in seen:raise ValueError(("Source occurrence collision",key))
  if not raw.strip():raise ValueError("Blank excerpt")
  seen.add(key)
  out.append({"concept_id":cid,"kind":kind,"source_start_line":line,
   "source_end_line":end,"source_excerpt_sha256":digest(raw.encode("utf-8")),
   "track_id":track or TRACK+":"+kind,"relation_to_prior":relation,
   "conditions":conditions or {},"review_status":"draft",
   "positive_training_eligible":False,"author_causal_chain_approved":False})
 for number,first,last,topic in STEPS:
  add("casting:paper_grid:step:"+str(number),"source_algorithm_step",first,last,
    {"step_order":number,"topic":topic,"school":"shijia_zhuanpan",
     "external_calendar_still_requires_validation":number in (1,2)},relation="reaffirms",
    track=TRACK+":algorithm_steps")
 for pair,start,ln in FIVE_MOUSE:
  if start+"子" not in extract(lines,13):
   raise ValueError(("Five mouse origin ungrounded",pair,start))
  add("casting:day_to_hour:"+pair,"five_mouse_day_stem_origin",13,
    conditions={"day_stem_group":list(pair),"start_at_zi_hour":start+"子",
                "source_verse_lines":[9,11],"external_date_required":True},
    relation="reaffirms",track=TRACK+":hour_stem")
 for stem in "戊己庚辛壬癸丁丙乙":
  source_line=next((c["source_start_line"] for f in figure_list
    if f["caption_line"]==27 for c in f["cells"]
    if c["original_cell_text"]==c["palace_label_raw"]+"宫："+stem),None)
  if source_line is None:raise ValueError(("Original earth stem missing",stem))
  palace=next(c["palace"] for f in figure_list if f["caption_line"]==27
     for c in f["cells"] if c["original_cell_text"].endswith("："+stem))
  add("stem:"+stem,"original_earth_stem_layout",source_line,
      conditions={"dun":"yin","ju":5,"palace":palace,"stem":stem,
                  "not_unconditional_palace_for_any_bureau":True},
      relation="reaffirms",track=TRACK+":yin5_earth_plate")
 for p,star in HOME_STARS.items():
  add("star:"+star,"star_source_rotation",40,52,
      {"home_palace":p,"center_host_kun":p==5,
       "source_provenance":"teacher_casting_explanation",
       "not_a_claim_that_center_printed_all_star_fields":True},
      relation="clarifies",track=TRACK+":star_rotation")
 for p,door in HOME_DOORS.items():
  add("door:"+door[0],"door_source_rotation",66,79,
      {"original_palace":p,"no_center_door":True,
       "nine_palace_count_for_value_door_only":True,
       "eight_palace_ring_after_value_door":True},
      relation="clarifies",track=TRACK+":door_rotation")
 for deity in DEITIES:
  add("deity:"+deity,"eight_deity_source_rotation",105,106,
      {"deity":deity,"yang_clockwise":True,"yin_counterclockwise":True,
       "lead_deity_follows_value_star_not_value_door":True},
      relation="clarifies",track=TRACK+":eight_deity_order")
 for key,line,end,topic,condition in RULES:
  add("casting:paper_grid:rule:"+key,"conditional_source_method",line,end,
      {"topic":topic,"application_condition":condition,
       "source_only_not_independent_validation":True},
      relation="clarifies",track=TRACK+":method_rules")
 for sample,(_,ju,hour,ln,day,date,full,head,star_target,door_target) in WORKED.items():
  add("casting:teaching_sample:"+sample,"pedagogical_cast_example",ln,
    conditions={"ju":ju,"hour":hour,"day":day,"source_date":date,
                "complete_deities_in_source":full,"old_historical_case":False,
                "xun_shou":head,"value_star_palace":star_target,
                "value_door_palace":door_target},
    relation="additional_exposition",track=TRACK+":example_not_event")
 return out

def compare_old(old,new):
 # Exact old data rows, not mere counts. New tables and rows may only be added.
 for (table,) in old.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"):
  cols=[x[1] for x in old.execute('PRAGMA table_info("'+table+'")')]
  sel=",".join('"'+x+'"' for x in cols)
  prior=list(old.execute('SELECT '+sel+' FROM "'+table+'"'))
  later=set(new.execute('SELECT '+sel+' FROM "'+table+'"'))
  if not all(r in later for r in prior):raise ValueError("Old historical source rows changed in "+table)

def build(base,source,output,index_dir,migration=None):
 base,source,output,index_dir=map(Path,(base,source,output,index_dir))
 migration=Path(migration or ROOT/"schema/migrations/018_kaiwu_didactic_casting_figures.sql")
 if output.exists():raise ValueError("Never overwrite a previously versioned SQLite snapshot")
 if digest(base.read_bytes())!=BASE_SHA:raise ValueError("Wrong full 23-source version baseline")
 raw=source.read_bytes();lines=original_lines(raw)
 figures=read_figures(lines);checks=source_engine_consistency(figures)
 assertions=source_assertions(lines,figures)
 output.parent.mkdir(parents=True,exist_ok=True)
 with sqlite3.connect("file:"+str(base)+"?mode=ro",uri=True) as old,sqlite3.connect(output) as db:
  old.backup(db)
  db.executescript(migration.read_text("utf-8"));db.execute("PRAGMA foreign_keys=ON")
  with db:
   if db.execute("SELECT 1 FROM sections WHERE book_id='kaiwu' AND section_key=?",(SECTION,)).fetchone():
    raise ValueError("Same chapter exists already; never duplicate or replace")
   if db.execute("SELECT count(*) FROM sections WHERE book_id='kaiwu'").fetchone()[0]!=2:
    raise ValueError("Prior Kaiwu two-source base required")
   db.execute("""INSERT INTO sections(book_id,section_key,title,original_text,sha256,content_version,reviewed)
     VALUES ('kaiwu',?,?,?,?,1,0)""",(SECTION,lines[0],raw.decode("utf-8"),SOURCE_SHA))
   sid=db.execute("SELECT last_insert_rowid()").fetchone()[0]
   db.execute("""INSERT INTO chapter_knowledge(chapter_key,book_id,title,source_sha256,
     source_length_bytes,knowledge_version,review_status)
     VALUES (?,'kaiwu',?,?,?,'1','draft')""",(CHAPTER,lines[0],SOURCE_SHA,len(raw)))
   for record in assertions:
    cid=record["concept_id"];ln=record["source_start_line"];end=record["source_end_line"]
    summary={k:v for k,v in record.items() if k not in
      ("concept_id","kind","source_start_line","source_end_line")}
    literal=extract(lines,ln,end)
    db.execute("""INSERT INTO semantic_assertions
      (chapter_key,concept_id,kind,relation,source_start_line,source_end_line,
       metadata_json,original_excerpt,review_status)
      VALUES (?,?,?,?,?,?,?,?,'draft')""",
      (CHAPTER,cid,record["kind"],record["relation_to_prior"],
       ln,end,canon(summary),literal))
    db.execute("""INSERT INTO cross_book_concept_tracks
     (chapter_key,concept_id,source_start_line,source_end_line,source_section_id,source_sha256,
      excerpt_sha256,track_id,relation_to_prior,comparison_state,normalized_json,review_status)
     VALUES (?,?,?,?,?,?,?,?,?,'candidate_not_human_verified',?,'draft')""",
     (CHAPTER,cid,ln,end,sid,SOURCE_SHA,record["source_excerpt_sha256"],
      record["track_id"],record["relation_to_prior"],canon(record["conditions"])))
   verified_keys={d["example_key"] for d in checks}
   for figure in figures:
    checked=int(figure["example_key"] in verified_keys and
                figure["pedagogical_stage"] in ("complete_four_layer","simplified_chart_no_deities"))
    meta={k:v for k,v in figure.items() if k not in ("cells","caption")}
    db.execute("""INSERT INTO kaiwu_didactic_figures
      (chapter_key,figure_key,source_caption_line,source_end_line,caption_original,
       source_figure_sha256,pedagogical_stage,example_key,actual_historical_prediction,
       verified_against_research_engine,metadata_json)
      VALUES (?,?,?,?,?,?,?,?,0,?,?)""",
      (CHAPTER,figure["figure_key"],figure["caption_line"],figure["source_end_line"],
       figure["caption"],figure["original_figure_sha256"],figure["pedagogical_stage"],
       figure["example_key"],checked,canon(meta)))
    for cell in figure["cells"]:
     db.execute("""INSERT INTO kaiwu_didactic_figure_cells
      (chapter_key,figure_key,palace,source_start_line,source_end_line,palace_label_raw,
       original_cell_text,original_cell_sha256,is_center_palace,
       original_center_has_no_independent_door,normalized_guess_for_missing_parts)
      VALUES (?,?,?,?,?,?,?,?,?,?,0)""",
      (CHAPTER,figure["figure_key"],cell["palace"],
       cell["source_start_line"],cell["source_end_line"],
       cell["palace_label_raw"],cell["original_cell_text"],cell["original_cell_sha256"],
       int(cell["palace"]==5),int(cell["source_is_center_bare_or_no_door"])))
   db.execute("""INSERT INTO cross_book_example_references
     (source_chapter_key,source_line,target_book_id,target_printed_page,reference_key,
      metadata_json,verified_target_case_id)
     VALUES (?,134,'shenqi','unspecified_in_source',?, ?,NULL)""",
     (CHAPTER,"kaiwu:ch03:reference:shenqi_casting_style",
      canon({"chapter_key":CHAPTER,"source_line":134,
             "reference_role":"earlier_book_printed_cast_format_not_case",
             "printed_page_not_given":True,"new_independent_case":False,
             "historical_case_match":None,"review_status":"draft"})))
   db.execute("""INSERT INTO chapter_archival_versions
    (archive_label,baseline_sha256,new_db_sha256,contains_complete_private_copyright_source,
     snapshot_type,created_utc,repo_public_archive_policy)
    VALUES (?, ?,NULL,1,'incremental_source_and_didactic_casts','2026-10-20',
    'user_authorized_public_full_sqlite_versions')""",
    ("shenqi21_kaiwu03_103_historical_cases",BASE_SHA))
  compare_old(old,db)
  if db.execute("PRAGMA integrity_check").fetchone()[0]!="ok" or db.execute("PRAGMA foreign_key_check").fetchall():
   raise ValueError("Bad new DB integration")
  expected={"sections":24,"cases":103,"historical_case_reasoning":495,
   "historical_palace_standardization":1008,"semantic_assertions":1697+len(assertions),
   "cross_book_concept_tracks":440+len(assertions),"cross_book_example_references":16,
   "kaiwu_didactic_figures":12,"kaiwu_didactic_figure_cells":108}
  actual={t:db.execute('SELECT count(*) FROM "'+t+'"').fetchone()[0] for t in expected}
  if actual!=expected:raise ValueError(("Unexpected totals",actual,expected))
  if db.execute("SELECT count(*) FROM historical_case_book_verdicts WHERE verdict='author_book_error_explicit'").fetchone()[0]!=6:
   raise ValueError("Six original wrong book calls were altered")
  if db.execute("SELECT count(*) FROM historical_case_reasoning_trace WHERE positive_training_eligible=1").fetchone()[0]:
   raise ValueError("Prematurely approved training examples")
  if db.execute("SELECT count(*) FROM kaiwu_didactic_figures WHERE actual_historical_prediction!=0").fetchone()[0]:
   raise ValueError("Didactic diagram is not actual event")
  db.execute("VACUUM");db.commit()
  if db.execute("PRAGMA integrity_check").fetchone()[0]!="ok" or db.execute("PRAGMA foreign_key_check").fetchall():
   raise ValueError("Database integrity lost after vacuum")
 index_dir.mkdir(parents=True,exist_ok=True)
 manifest={"schema":"wengua_multibook_source_chapter_v3","source_book":"kaiwu",
  "section_key":SECTION,"chapter_key":CHAPTER,"book_chapter_number_from_filename":3,
  "original_title":lines[0],"source_sha256":SOURCE_SHA,"source_bytes":len(raw),
  "source_lines":len(lines),"seven_explicit_casting_steps":7,
  "source_figure_count":len(figures),"source_figure_palace_text_cells":108,
  "worked_educational_casts":len(checks),"fully_layered_casts":2,
  "simplified_casts_missing_deities":2,"existing_historical_case_family_count":103,
  "new_historical_event_families":0,"new_historical_prediction_charts":0,
  "actual_original_historical_charts_unchanged":112,
  "new_concept_occurrences":len(assertions),"new_cross_book_format_references":1,
  "chapter_source_not_published_calendar_proof":True,
  "book_counts":{"shenqi":21,"kaiwu":3},"total_source_sections":24,
  "crossbook_track_status":"draft_candidate",
  "all_previous_source_rows_preserved":True,"positive_training_eligible":False,
  "human_verified_causal_chains":0,"source_origin_unmodified":True,
  "baseline_sha256":BASE_SHA,"produced_db_sha256":digest(output.read_bytes()),
  "cumulative_counts":actual}
 def save(path,obj):
  (index_dir/path).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 save("chapter_manifest.json",manifest)
 save("concept_tracks.json",{"schema":"wengua_kaiwu_caster_multitrack_v1",
   "chapter_key":CHAPTER,"source_sha256":SOURCE_SHA,"entries":assertions})
 save("figure_index.json",{"schema":"wengua_source_printed_didactic_cast_tables_v1",
   "source_sha256":SOURCE_SHA,"figures":figures})
 save("worked_cast_checks.json",{"schema":"wengua_source_text_layout_consistency_only_v1",
   "source_sha256":SOURCE_SHA,"no_astronomical_or_outcome_validation":True,
   "checked_examples":checks})
 save("source_audit.json",{"source_sha256":SOURCE_SHA,
   "figure_count":12,"literal_palace_cells":108,
   "school":"shijia_zhuanpan",
   "nine_palace_numerical_zhishi_timing_not_eight_ring":True,
   "eight_door_rotation_only_after_zhishi_position_fixed":True,
   "source_2001_08_07_19_34_jieqi_not_independently_checked":True,
   "futou_middle_yuan_assumed_from_book":True,
   "six_jia_star_and_door_fuyin_study_claim":True,
   "six_gui_door_fuyin_study_claim":True,
   "special_wu_gui_days_gui_hai_star_door_fuyin_claim":True,
   "missing_deity_info_in_two_full_schematic_examples":True,
   "center_has_no_source_door_deity_synthetic_value":True,
   "historical_case_labels_unchanged":True,
   "no_new_success_claims":True,"candidate_rules_review_status":"draft"})
 return manifest

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--base",required=True);p.add_argument("--source",required=True)
 p.add_argument("--output",required=True);p.add_argument("--index-dir",required=True)
 p.add_argument("--migration",default=None)
 a=p.parse_args()
 print(json.dumps(build(a.base,a.source,a.output,a.index_dir,a.migration),
                  ensure_ascii=False,indent=2))
if __name__=="__main__":main()
