"""《开悟之门》第四章：分析判断、81组有序十干克应、多轨版本及三类应期。

Strictly additive to verified 21 Shenqi + 3 Kaiwu full SQLite. Original entire
chapter preserved by SHA; reprinted Shenqi cases ARE NOT new historical events.
All extracted rules are candidate-only; annotations are not outcome forecasts.
"""
from __future__ import annotations
import argparse,hashlib,json,re,sqlite3
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE_SHA="91aca58f7b30a577d9ca9dad231980604b718fe3d151b9ecba4086aea2ebd85f"
SOURCE_SHA="ce3203902f6fa2e129d13899e19ef4a3d02e8698f38eac3dbe7383ba550a2cf4"
SECTION="analysis_judgment_ch04"
CHAPTER="kaiwu/analysis_judgment_ch04/v1"
TRACK="kaiwu:source_v1:shijia_zhuanpan"
STEMS="戊乙丙丁己庚辛壬癸"
STEM_SET=set(STEMS)
BASE_NAME="WenguaApp_神奇之门21章_开悟之门3章_103案例_完整研究库.sqlite3"
NEW_NAME="WenguaApp_神奇之门21章_开悟之门4章_103案例_完整研究库.sqlite3"
SECTIONS={3:"yongshen_four_characteristics",41:"judgment_vertical_horizontal",
 169:"time_target_methods",238:"directional_stem_pairs_and_patterns",
 592:"decision_after_analysis"}
# Author explicitly groups 81, NOT full 100 ten-stem square; no fabricated missing pairs.
PAIR_RE=re.compile(r"^([戊乙丙丁己庚辛壬癸])/([戊乙丙丁己庚辛壬癸])，")
YONGSHEN_FEATURES=[(11,"64_symbols"),(19,"many_meanings"),
 (23,"multi_yongshen_for_same_event"),(37,"leading_usage_selection")]
YONGSHEN_COUNTS=[("ten_stems",10),("twelve_branches",12),("nine_stars",9),
 ("eight_doors",8),("eight_deities",8),("eight_trigrams",8),("nine_palaces",9)]
YONGSHEN_EXAMPLES=[("yi_body_neck",21),("yi_body_liver",21),
 ("yi_day_wonder",21),("yi_marriage_female",21),
 ("yi_health_doctor",21),("yi_health_herbal_medicine",21)]
YONGSHEN_SCOPE=[(27,"important_life_year_of_birth"),
 (29,"xingnian_original_two_methods"),(29,"xingnian_method_all_men_women"),
 (29,"xingnian_method_six_xun_starter_variations"),
 (33,"author_prefers_birth_year_not_xingnian"),
 (35,"birth_year_heaven_stem_palace_state"),
 (40,"day_stem_questioner_hour_stem_question"),
 (40,"weather_nine_stars_people_eight_doors_geo_palaces_kin_four_pillars")]
PREPARATION=[(47,"highlight_four_pillars_and_domain_specific_yongshen"),
 (65,"mark_xun_void_using_hour_as_default"),
 (66,"void_is_contextual_not_fixed_time"),
 (67,"mark_hourly_horse"),
 (78,"year_month_day_horse_normally_unused")]
HORSE=[(69,"申子辰","寅",8),(70,"寅午戌","申",2),
 (71,"巳酉丑","亥",6),(72,"亥卯未","巳",4)]
METHOD_TOPICS=[
 (82,"vertical_horizontal_inside_outside_month"),
 (88,"vertical_four_layer_horizontal_peripheral_and_time"),
 (91,"vertical_four_layer_personal_conditions"),
 (103,"heaven_guest_earth_host_stem_interactions"),
 (105,"separate_kenying_guest_host_on_solar_stem"),
 (107,"horizontal_related_palace_interactions"),
 (127,"horizontal_only_landed_palace_elements_not_symbol_elements"),
 (131,"day_hour_relation"),
 (133,"month_day_relation"),
 (135,"year_day_relation"),
 (137,"born_year_day_and_superiors_relation"),
 (139,"real_estate_value_door_and_life_door"),
 (141,"shopfront_open_door_as_secondary"),
 (143,"investment_wu_capital_and_life_door_profit_conditional"),
 (147,"inside_outside_and_fuyin_fanyin_distance_timing"),
 (149,"yang_inner_1_8_3_4_outer_9_2_7_6"),
 (151,"yin_inner_9_2_7_6_outer_1_8_3_4"),
 (153,"fuyin_near_slow_fanyin_far_fast_qualifier"),
 (155,"day_hour_both_inside_outside_or_split"),
 (161,"month_priority_for_strength_outcome"),
 (163,"month_strength_and_timing_source_claim"),
 (167,"case_speed_conflicting_evidence_provenance"),
 (171,"determine_success_failure_before_timing"),
 (173,"author_critiques_single_timing_method"),
 (175,"three_timing_class_system"),
 (210,"geng_obstruction_is_domain_dependent"),
 (212,"geng_for_stop_bad_event_is_conditional"),
 (214,"geng_interception_use"),
 (224,"geng_pattern_void_and_yi_geng_unavailable"),
 (228,"beijing_case_specific_timing_not_previously_forecast"),
 (232,"invoice_example_predicted_day_off_by_one"),
 (236,"prefers_civil_calendar_outcome_date"),
 (240,"heaven_stem_guest_earth_stem_host"),
 (246,"auspicious_from_who_perspective"),
 (430,"81_not_100_pairings_source_cardinality"),
 (432,"pair_apothegm_allegorical_not_literal"),
 (436,"auspicious_conditional_not_absolute"),
 (460,"nine_escape_limited_by_tomb_and_door_oppression"),
 (498,"three_tricks_five_guises_tomb_door_oppression"),
 (500,"inauspicious_conditions_not_automatic"),
 (526,"author_unverified_extended_striking_punishment_hypothesis"),
 (538,"three_wonders_controlled_requires_month"),
 (542,"hour_stem_tomb_versus_storehouse_month"),
 (550,"door_oppression_month_strength"),
 (566,"jia_hour_exception_to_fuyin"),
 (576,"fanyin_good_or_bad_depends_on_domain_and_illness_duration"),
 (582,"five_missed_hour_hour_stem_controls_day_same_yin_yang"),
 (588,"five_missed_hour_cast_time_not_unconditionally_bad"),
 (604,"urgent_follow_deity_slow_follow_door_guest_host"),
 (610,"urgent_deity_direction_author_claim_not_verified_safety"),
 (614,"slow_door_choosing_time_direction_source_context"),
 (624,"date_selection_author_acknowledges_superstition"),
 (626,"directional_selection_by_specific_context"),
 (640,"nine_guest_host_criteria")]
SUCCESS_LINES=list(range(181,189))
FAIL_LINES=list(range(197,203))
GENG_LINES=[218,220,222]
LIMITATION_LINES=[224,228,232]
TIMING_EXTRA=[
 (179,"success_prerequisite_before_success_timing"),
 (196,"failed_prerequisite_before_failed_timing"),
 (210,"geng_symbol_may_switch_role_by_question"),
 (216,"three_geng_methods_applicability_priority")]
FORMATION_SOURCE=[
 (442,"nine_escape:heaven"),(444,"nine_escape:earth"),
 (446,"nine_escape:human"),(448,"nine_escape:wind"),
 (450,"nine_escape:cloud"),(452,"nine_escape:dragon"),
 (454,"nine_escape:tiger"),(456,"nine_escape:deity"),
 (458,"nine_escape:ghost"),
 (464,"three_wonders_get_envoy"),(468,"jade_girl_defends_gate"),
 (472,"three_wonders_noble_rising:yi"),
 (474,"three_wonders_noble_rising:bing"),
 (476,"three_wonders_noble_rising:ding"),
 (482,"three_wonders_salary_palace"),(486,"heaven_revealing_jia_hour"),
 (492,"three_stratagems:true_yin"),(492,"three_stratagems:rest_liuhe"),
 (492,"three_stratagems:heavy_jiudi"),
 (496,"five_masks:heaven"),(496,"five_masks:earth"),
 (496,"five_masks:human"),(496,"five_masks:deity"),
 (496,"five_masks:ghost"),
 (502,"geng_annual_month_day_hour_obstruction"),
 (504,"year_month_day_hour_above_geng_reversal"),
 (510,"six_jia_punishment:jiazi_3"),(512,"six_jia_punishment:jiaxu_2"),
 (514,"six_jia_punishment:jiashen_8"),(516,"six_jia_punishment:jiawu_9"),
 (518,"six_jia_punishment:jiachen_4"),(520,"six_jia_punishment:jiayin_4"),
 (524,"stem_pair_to_pair_punishment_supplement"),
 (532,"three_wonders_tomb"),(538,"three_wonders_punished"),
 (542,"hour_stem_tomb_storehouse"),(548,"door_oppression"),
 (554,"bing_huo_betrayal_pattern"),
 (558,"star_door_fuyin"),(570,"star_door_fanyin"),
 (582,"five_missed_hour")]
DAYS_OF_SELECT=[(616,"day:restraint"),(616,"day:attack"),
 (616,"day:treasure"),(616,"day:righteousness"),(616,"day:harmony"),
 (618,"hour:five_yin_vs_five_yang")]
GUEST_HOST=[(642,"moving_guest"),(643,"first_guest"),
 (644,"active_guest"),(645,"attacker_guest"),
 (646,"far_guest"),(647,"outside_guest"),
 (648,"sky_guest_earth_host"),(649,"jia_to_wu_guest_ji_to_gui_host"),
 (650,"fanyin_guest_fuyin_host")]
# Mentioning another book's cases is a bibliographic source, not another event.
BOOK_REF_RE=re.compile(r"《神奇之门》")
PALACE_IDS=(4,9,2,3,5,7,8,1,6)
PALACE_LABELS=("巽四宫","离九宫","坤二宫","震三宫","中五宫","兑七宫","艮八宫","坎一宫","乾六宫")

def sha(data):return hashlib.sha256(data).hexdigest()
def encode(obj):return json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(",",":"))
def text_at(lines,a,b=None):
 b=a if b is None else b
 if not 1<=a<=b<=len(lines):raise ValueError(("Invalid source provenance",a,b))
 return "\n".join(lines[a-1:b])
def original_lines(data):
 if sha(data)!=SOURCE_SHA:raise ValueError("Original chapter SHA256 changed")
 lines=data.decode("utf-8").splitlines()
 if len(lines)!=656 or lines[0]!="第四章 如何分析判断奇门格局":
  raise ValueError("Source was truncated or title shifted")
 for line,word in SECTIONS.items():
  if not lines[line-1].startswith(("第一节","第二节","第三节","第四节","第五节")) or word is None:
   raise ValueError(("Chapter outline mismatch",line))
 if not lines[-1].endswith("取得预期的效果"):
  raise ValueError("Original ending incomplete")
 return lines

def ordered_pairs(lines):
 pairs=[];unique=set()
 for line in range(248,430):
  s=lines[line-1].strip();m=PAIR_RE.match(s)
  if not m:continue
  top,bottom=m.groups()
  if (top,bottom) in unique:raise ValueError(("Duplicate directed pair",top,bottom))
  unique.add((top,bottom))
  raw=text_at(lines,line)
  pairs.append({"top":top,"bottom":bottom,"pair_key":top+"/"+bottom,
   "reverse_key":bottom+"/"+top,"source_line":line,"source_original":raw,
   "excerpt_sha256":sha(raw.encode("utf-8")),
   "source_conditions_present":{x:x in raw for x in
      ("门迫","入墓","击刑","月令","吉门","凶门","如果","但","测婚","测病","求财","为主","为客")},
   "interpretation_type":"traditional_source_specific_candidate",
   "no_direct_universal_outcome":True,"review_status":"draft"})
 if len(pairs)!=81:
  raise ValueError(("Original is exactly 81 ordered pairs, not 100",len(pairs)))
 # Reverse order is a *different* author's interpretation, never swapped automatically.
 reverse=sum((b["bottom"],b["top"]) in unique for b in pairs)
 if reverse<50:raise ValueError(("Unexpected loss of asymmetric reverse pairs",reverse))
 return pairs

def references(lines):
 refs=[]
 for ln,s in enumerate(lines,1):
  if not BOOK_REF_RE.search(s):continue
  hit=re.search(r"《神奇之门》(?:一书)?(?:第)?(\d+(?:[~～\-]\d+)?)页",s)
  page=hit.group(1) if hit else "unspecified_in_source"
  role=("book_reference_not_new_event" if ln in (15,25,173,240,604)
      else "reprinted_original_case_not_independent_new_event" if ln in (47,93,129,157,159,165,167,190,192,204,206,226,230,232,234,628,630,632,654)
      else "book_source_interpretation_or_rule")
  if ln in (226,228):role="book_initial_timing_not_disclosed_then_retrospective_explanation"
  if ln==232:role="source_predictive_timing_one_day_off_preserve_error"
  refs.append({"source_line":ln,"cited_book":"shenqi","printed_page":page,
   "link_id":"kaiwu:analysis_ch04:shenqi_ref:"+str(ln),"relation_role":role,
   "not_new_event":True,"not_new_printed_chart":True,
   "not_independently_verified_case_match":True,
   "review_status":"draft"})
 if len(refs)!=25:raise ValueError(("Unexpected old-book references",len(refs)))
 return refs

def source_figures(lines):
 # Both images are printed as Unicode text. First reprises Shenqi's old
 # bank-case chart; second is elementary five-element geography (NOT cast).
 all_charts=[]
 for start,end,key,kind in [
    (49,61,"old_shenqi_bank_case_reprinted","crossbook_old_case_illustration"),
    (113,119,"palace_five_elements","didactic_five_element_palaces")]:
  segment=lines[start-1:end]
  borders=[(start+i,l) for i,l in enumerate(segment) if l.startswith(("┌","├","└"))]
  if len(borders)!=4:raise ValueError(("Original Unicode source diagram damaged",key))
  groups=[]
  for n in range(3):
   top,bottom=borders[n][0],borders[n+1][0]
   glyph_lines=[(ln,lines[ln-1]) for ln in range(top+1,bottom)]
   if not glyph_lines or not all(v.startswith("│") for _,v in glyph_lines):
    raise ValueError(("Damaged figure rows",key,n))
   groups.append(glyph_lines)
  cells=[]
  for row,group in enumerate(groups):
   for col in range(3):
    pal=PALACE_IDS[row*3+col]
    pieces=[(ln,part.strip()) for ln,line in group
            for part in [line.split("│")[col+1]] if part.strip()]
    if not pieces or PALACE_LABELS[row*3+col] not in pieces[0][1]:
     raise ValueError(("Original palace missing",key,pal,pieces))
    literal="\n".join(x for ln,x in pieces)
    cells.append({"palace":pal,"palace_label_raw":PALACE_LABELS[row*3+col],
     "source_start_line":pieces[0][0],"source_end_line":pieces[-1][0],
     "original_cell_text":literal,
     "original_cell_sha256":sha(literal.encode("utf-8")),
     "center_is_bare_original":pal==5,"not_new_historical_chart":True})
  all_charts.append({"figure_key":key,"caption":text_at(lines,47) if start==49 else text_at(lines,121),"source_caption_line":start,
   "source_end_line":end,"pedagogical_stage":kind,"example_key":"shenqi_referenced" if start==49 else None,
   "original_figure_sha256":sha(text_at(lines,start,end).encode("utf-8")),
   "cells":cells,"verified_against_engine":False,
   "not_new_independent_prediction":True})
 if len(all_charts)!=2 or sum(len(x["cells"]) for x in all_charts)!=18:
  raise ValueError("Two source figures 18 palace cells required")
 return all_charts

def timings(lines):
 out=[]
 for name,ls in [("successful_outcome",SUCCESS_LINES),("failed_outcome",FAIL_LINES),
                 ("interception_recovery",GENG_LINES),("limitation",LIMITATION_LINES)]:
  for seq,ln in enumerate(ls,1):
   original=text_at(lines,ln)
   if not original.strip():raise ValueError(("Empty timing original",ln))
   conditions={"after_success_failure_is_classified":name in ("successful_outcome","failed_outcome"),
    "geng_applies_to_stopping_recovery":name=="interception_recovery",
    "source_line":ln,"original_is_not_a_fully_specified_calendar_ephemeris":True,
    "no_blind_accuracy_claim":True}
   out.append({"category":name,"method_key":name+":"+str(seq),
    "source_line":ln,"original_text":original,
    "excerpt_sha256":sha(original.encode("utf-8")),"conditions":conditions})
 return out

def assertions(lines,pairs,refs,timing):
 out=[];seen=set()
 def add(cid,kind,ln,details=None,end=None,relation="clarifies",track=None):
  end=ln if end is None else end
  raw=text_at(lines,ln,end)
  if (cid,ln) in seen:raise ValueError(("Duplicate occurrence",cid,ln))
  seen.add((cid,ln))
  out.append({"concept_id":cid,"kind":kind,"source_start_line":ln,
   "source_end_line":end,"source_excerpt_sha256":sha(raw.encode("utf-8")),
   "track_id":track or TRACK+":"+kind,"relation_to_prior":relation,
   "normalized":details or {},"review_status":"draft",
   "positive_training_eligible":False})
 for ln,tag in SECTIONS.items():
  add("kaiwu:analysis:section:"+tag,"source_chapter_section",ln,
   {"heading":lines[ln-1],"source_book":"kaiwu","part":4})
 for ln,k in YONGSHEN_FEATURES:
  add("yongshen:feature:"+k,"yongshen_global_characteristic",ln,
   {"characteristic":k,"not_proven_true_world_prediction":True},"none" if False else None)
 for name,count in YONGSHEN_COUNTS:
  if name not in ("nine_palaces",) and not text_at(lines,15):
   raise ValueError("64 items source section absent")
  add("yongshen:symbol_family:"+name,"yongshen_64_taxonomy_family",15,
      {"family":name,"author_stated_quantity":count,
       "shared_concept_not_new_individual_symbols":True},relation="reaffirms",
      track=TRACK+":yongshen_symbol_taxonomy")
 if sum(count for _,count in YONGSHEN_COUNTS)!=64:raise ValueError("author count mismatch")
 for k,ln in YONGSHEN_EXAMPLES:
  add("stem:乙:context:"+k,"specific_yongshen_domain_interpretation",ln,
      {"stem":"乙","scope":k,"meaning_depends_on_question_person_or_stage":True},
      relation="extends",track=TRACK+":yi_multimeaning")
 for ln,k in YONGSHEN_SCOPE:
  add("yongshen:policy:"+k,"multivalent_yongshen_scope",ln,
      {"topic":k,"birth_year_vs_xingnian_separate_methods":ln in (29,33,35),
       "major_questions_need_birth_year_optional":ln in (27,33,35)},
       track=TRACK+":yongshen_policy")
 for ln,k in PREPARATION:
  add("casting:analysis_prep:"+k,"three_preparations_and_subconditions",ln,
      {"topic":k,"source_method_requires_question":True},
      track=TRACK+":analysis_preparation")
 for ln,triple,horse,pal in HORSE:
  if horse not in text_at(lines,ln):raise ValueError("Horse verse missing")
  add("branch:horsemanship:"+":".join(triple),"horse_branch_group",ln,
   {"hour_branch_options":list(triple),"horse_branch":horse,"horse_palace":pal,
    "hourly_default_year_month_day_not_normally_used":True},
   track=TRACK+":hourly_horse")
 for ln,k in METHOD_TOPICS:
  add("kaiwu:analysis:method:"+k,"four_layer_horizontal_timing_method",ln,
    {"topic":k,"month_and_domain_may_change_outcome":True,
     "do_not_treat_original_case_posthoc_as_new_trial":True},
    track=TRACK+":analysis_method")
 for r in timing:
  add("timing:"+r["category"]+":"+r["method_key"].split(":")[-1],
    "outcome_conditional_timing",r["source_line"],r["conditions"],
    track=TRACK+":timing_"+r["category"])
 for p in pairs:
  add("stem_pair:"+p["top"]+":"+p["bottom"],
   "directional_ten_stem_guest_host_combination",p["source_line"],
   {"heaven_guest":p["top"],"earth_host":p["bottom"],
    "reverse_pair_is_different":p["reverse_key"],
    "literal_condition_terms":p["source_conditions_present"],
    "source_apothegm_not_absolute":True},
   relation="reaffirms",track=TRACK+":directional_stem_pairs")
 for ln,k in FORMATION_SOURCE:
  add("formation:"+k,"conditional_formation_rule",ln,
      {"source_scope":k,"full_conditions_only_in_source_quote":True,
       "do_not_approve_without_specific_domain_and_yongshen":True},
      relation="clarifies",track=TRACK+":formations")
 for ln,k in DAYS_OF_SELECT:
  add("decision:"+k,"calendar_selection_source_claim",ln,
      {"rule":k,"modern_date_and_zone_not_verified":True,"avoid_realtime_safety_advice":True},
      track=TRACK+":date_choice")
 for ln,k in GUEST_HOST:
  add("guest_host:criterion:"+k,"action_role_conditional",ln,
      {"guest_versus_host":k,"not_absolute_outcome":True},
      relation="clarifies",track=TRACK+":guest_host_perspective")
 # Discrete author assertions about after-the-fact stories: preserve narrative sequence.
 for ln,kind in [(190,"discharge_book_outcome_recap"),
                 (192,"license_letter_book_outcome_recap"),
                 (204,"father_disease_recap_not_medical_fact"),
                 (206,"wartime_forecast_book_recap"),
                 (226,"bank_case_posthoc_geng_timing"),
                 (228,"bank_case_explicit_not_given_initial_timing"),
                 (230,"missing_daughter_book_recap"),
                 (232,"invoice_book_one_day_timing_error"),
                 (234,"missing_cash_book_recap"),
                 (628,"outside_hospital_case_recap"),
                 (630,"property_dispute_recap"),
                 (632,"publishing_case_recap"),
                 (654,"labor_dispute_recap")]:
  add("historical_citation:analysis:"+kind,
   "book_reuse_retrospective_with_phase",ln,
   {"book":"shenqi","source_line":ln,"verification":"not_independent",
    "initial_error_preserved":ln in (228,232),
    "never_new_event_family":True},relation="additional_exposition",
    track=TRACK+":retrospective_reference")
 if len(out)!=len({(x["concept_id"],x["source_start_line"]) for x in out}):
  raise ValueError("Duplicate assertion key")
 return out

def old_row_inclusion(old,db):
 # Every row of every previous table must remain byte/value-equal.
 for (table,) in old.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"):
  cols=[x[1] for x in old.execute('PRAGMA table_info("'+table+'")')]
  keys=",".join('"'+col+'"' for col in cols)
  previous=list(old.execute('SELECT '+keys+' FROM "'+table+'"'))
  newer=set(db.execute('SELECT '+keys+' FROM "'+table+'"'))
  if not all(r in newer for r in previous):
   raise ValueError("Old historical rows overwritten in "+table)

def build(base,source,output,index_dir):
 base,source,output,index_dir=map(Path,(base,source,output,index_dir))
 if output.exists():raise ValueError("Refuse overwrite of any old/new versioned database")
 if sha(base.read_bytes())!=BASE_SHA:raise ValueError("Wrong full 24-section base SQLite SHA")
 raw=source.read_bytes();ls=original_lines(raw)
 pairs=ordered_pairs(ls);links=references(ls);charts=source_figures(ls)
 time_methods=timings(ls);items=assertions(ls,pairs,links,time_methods)
 output.parent.mkdir(parents=True,exist_ok=True)
 migration=ROOT/"schema/migrations/019_kaiwu_analysis_stem_timing.sql"
 with sqlite3.connect("file:"+str(base)+"?mode=ro",uri=True) as old, sqlite3.connect(output) as db:
  old.backup(db)
  db.executescript(migration.read_text("utf-8"))
  db.execute("PRAGMA foreign_keys=ON")
  with db:
   if db.execute("SELECT count(*) FROM sections WHERE book_id='kaiwu'").fetchone()[0]!=3:
    raise ValueError("Prior Kaiwu 3 chapters missing")
   if db.execute("SELECT 1 FROM sections WHERE book_id='kaiwu' AND section_key=?",(SECTION,)).fetchone():
    raise ValueError("Same source key already imported")
   db.execute("""INSERT INTO sections(book_id,section_key,title,original_text,sha256,content_version,reviewed)
    VALUES ('kaiwu',?,?,?,?,1,0)""",(SECTION,ls[0],raw.decode("utf-8"),SOURCE_SHA))
   sid=db.execute("SELECT last_insert_rowid()").fetchone()[0]
   db.execute("""INSERT INTO chapter_knowledge(chapter_key,book_id,title,source_sha256,
    source_length_bytes,knowledge_version,review_status)
    VALUES (?,'kaiwu',?,?,?,'1','draft')""",(CHAPTER,ls[0],SOURCE_SHA,len(raw)))
   for x in items:
    ln=x["source_start_line"];end=x["source_end_line"]
    db.execute("""INSERT INTO semantic_assertions(chapter_key,concept_id,kind,relation,
      source_start_line,source_end_line,metadata_json,original_excerpt,review_status)
      VALUES (?,?,?,?,?,?,?,?,'draft')""",
     (CHAPTER,x["concept_id"],x["kind"],x["relation_to_prior"],
      ln,end,encode(x),text_at(ls,ln,end)))
    db.execute("""INSERT INTO cross_book_concept_tracks(chapter_key,concept_id,source_start_line,
      source_end_line,source_section_id,source_sha256,excerpt_sha256,track_id,
      relation_to_prior,comparison_state,normalized_json,review_status)
      VALUES (?,?,?,?,?,?,?,?,?,'candidate_not_human_verified',?,'draft')""",
     (CHAPTER,x["concept_id"],ln,end,sid,SOURCE_SHA,x["source_excerpt_sha256"],
      x["track_id"],x["relation_to_prior"],encode(x["normalized"])))
   for p in pairs:
    db.execute("""INSERT INTO kaiwu_ordered_stem_pair_occurrences(chapter_key,upper_stem,
      lower_stem,source_line,source_excerpt,source_excerpt_sha256,reverse_pair_key,
      source_conditions_json) VALUES (?,?,?,?,?,?,?,?)""",
     (CHAPTER,p["top"],p["bottom"],p["source_line"],p["source_original"],
      p["excerpt_sha256"],p["reverse_key"],encode(p["source_conditions_present"])))
   for tm in time_methods:
    db.execute("""INSERT INTO kaiwu_timing_source_methods(chapter_key,method_key,category,
      source_line,original_text,excerpt_sha256,method_metadata_json)
      VALUES (?,?,?,?,?,?,?)""",(CHAPTER,tm["method_key"],tm["category"],
      tm["source_line"],tm["original_text"],tm["excerpt_sha256"],encode(tm["conditions"])))
   for ref in links:
    db.execute("""INSERT INTO cross_book_example_references(source_chapter_key,
      source_line,target_book_id,target_printed_page,reference_key,metadata_json,
      verified_target_case_id) VALUES (?,?,'shenqi',?,?,?,NULL)""",
      (CHAPTER,ref["source_line"],ref["printed_page"],ref["link_id"],encode(ref)))
   for fig in charts:
    meta={k:v for k,v in fig.items() if k not in ("cells","caption")}
    db.execute("""INSERT INTO kaiwu_didactic_figures(chapter_key,figure_key,
      source_caption_line,source_end_line,caption_original,source_figure_sha256,
      pedagogical_stage,example_key,actual_historical_prediction,
      verified_against_research_engine,metadata_json)
      VALUES (?,?,?,?,?,?,?,?,0,0,?)""",
      (CHAPTER,fig["figure_key"],fig["source_caption_line"],fig["source_end_line"],
       fig["caption"],fig["original_figure_sha256"],fig["pedagogical_stage"],
       fig["example_key"],encode(meta)))
    for cell in fig["cells"]:
     db.execute("""INSERT INTO kaiwu_didactic_figure_cells(chapter_key,figure_key,palace,
       source_start_line,source_end_line,palace_label_raw,original_cell_text,
       original_cell_sha256,is_center_palace,original_center_has_no_independent_door,
       normalized_guess_for_missing_parts) VALUES (?,?,?,?,?,?,?,?,?,?,0)""",
       (CHAPTER,fig["figure_key"],cell["palace"],cell["source_start_line"],
        cell["source_end_line"],cell["palace_label_raw"],cell["original_cell_text"],
        cell["original_cell_sha256"],int(cell["palace"]==5),int(cell["palace"]==5)))
   db.execute("""INSERT INTO chapter_archival_versions(archive_label,baseline_sha256,
      new_db_sha256,contains_complete_private_copyright_source,snapshot_type,
      created_utc,repo_public_archive_policy)
      VALUES (?,?,NULL,1,'additive_multibook_source_with_directional_81_and_timing','2026-10-20',
      'user_authorized_public_full_sqlite_versions')""",
      ("shenqi21_kaiwu04_103_existing_cases",BASE_SHA))
  old_row_inclusion(old,db)
  if db.execute("PRAGMA integrity_check").fetchone()[0]!="ok" or db.execute("PRAGMA foreign_key_check").fetchall():
   raise ValueError("SQLite failed full integrity check")
  expected={"sections":25,"cases":103,"historical_case_reasoning":495,
   "historical_palace_standardization":1008,
   "semantic_assertions":1771+len(items),
   "cross_book_concept_tracks":514+len(items),
   "cross_book_example_references":16+len(links),
   "kaiwu_didactic_figures":14,
   "kaiwu_didactic_figure_cells":126,
   "kaiwu_ordered_stem_pair_occurrences":81,
   "kaiwu_timing_source_methods":len(time_methods)}
  actual={k:db.execute('SELECT count(*) FROM "'+k+'"').fetchone()[0] for k in expected}
  if actual!=expected:raise ValueError(("Wrong cumulative counts",actual,expected))
  if db.execute("SELECT count(*) FROM historical_case_book_verdicts WHERE verdict='author_book_error_explicit'").fetchone()[0]!=6:
   raise ValueError("Old six author-confirmed bad predictions lost")
  if db.execute("SELECT count(*) FROM cases WHERE case_id LIKE 'kaiwu.%'").fetchone()[0]:
   raise ValueError("Same-event source citations became fabricated historical cases")
  if db.execute("SELECT count(*) FROM historical_case_reasoning_trace WHERE positive_training_eligible=1").fetchone()[0]:
   raise ValueError("Training promoted without review")
  db.execute("VACUUM");db.commit()
  if db.execute("PRAGMA integrity_check").fetchone()[0]!="ok" or db.execute("PRAGMA foreign_key_check").fetchall():
   raise ValueError("Post vacuum inconsistency")
 index_dir.mkdir(parents=True,exist_ok=True)
 manifest={"schema":"wengua_multibook_source_chapter_v4","chapter_key":CHAPTER,
  "section_key":SECTION,"source_book":"kaiwu","source_title":ls[0],
  "source_sha256":SOURCE_SHA,"source_bytes":len(raw),"source_lines":len(ls),
  "five_book_sections":SECTIONS,"book_counts":{"shenqi":21,"kaiwu":4},
  "total_source_sections":25,"source_ordered_stem_pair_count":len(pairs),
  "unique_directional_pair_keys":len({x["pair_key"] for x in pairs}),
  "timing_method_counts":dict(Counter(x["category"] for x in time_methods)),
  "new_semantic_occurrences":len(items),"new_shenqi_bibliographic_links":len(links),
  "crossbook_reprinted_old_bank_chart_and_five_elements_chart":len(charts),
  "source_diagram_palace_cells":sum(len(x["cells"]) for x in charts),
  "new_independent_historical_cases":0,"new_historical_prediction_charts":0,
  "historical_cases_unchanged":103,"historical_charts_unchanged":112,
  "author_reasoning_unchanged":495,"all_previous_source_rows_preserved":True,
  "all_new_source_occurrences_draft":True,"positive_training_eligible":False,
  "author_acknowledges_missed_bank_timing_line":228,
  "invoice_prediction_one_day_early_result_line":232,
  "author_guesses_not_externally_verified":True,"baseline_sha256":BASE_SHA,
  "created_full_db_sha256":sha(output.read_bytes()),"counts":actual}
 def save(name,body):
  (index_dir/name).write_text(json.dumps(body,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 save("chapter_manifest.json",manifest)
 save("concept_tracks.json",{"chapter_key":CHAPTER,"source_sha256":SOURCE_SHA,"entries":items})
 save("ordered_stem_pairs.json",{"chapter_key":CHAPTER,"ordered_not_symmetric":True,"pairs":pairs})
 save("timing_methods.json",{"chapter_key":CHAPTER,"categories":[
  "successful_outcome","failed_outcome","interception_recovery","limitation"],
  "methods":time_methods})
 save("cross_book_links.json",{"chapter_key":CHAPTER,"author_case_source_not_independent_event":True,
    "references":links})
 save("figure_index.json",{"chapter_key":CHAPTER,"old_case_reprinted_not_new":True,
    "figures":charts})
 save("source_audit.json",{"source_sha256":SOURCE_SHA,"source_lines":656,
    "directional_pair_cardinality_not_100":81,"source_only_not_blind_validation":True,
    "author_says_apothegms_are_allegorical":True,
    "success_failure_interception_timing_are_separate":True,
    "geng_void_and_yi_geng_combine_may_disqualify_pattern":True,
    "five_missed_hour_input_vs_action_time_distinction":True,
    "yin_yang_inside_outside_opposite":True,
    "day_stem_guest_hour_stem_and_multi_yongshen_not_absolute":True,
    "source_stated64_sum_counts":64,
    "new_old_event_family_count":0,"review_status":"draft",
    "positive_training_eligible":False})
 return manifest

def main():
 p=argparse.ArgumentParser()
 for arg in ("base","source","output","index-dir"):
  p.add_argument("--"+arg,required=True)
 a=p.parse_args()
 print(json.dumps(build(a.base,a.source,a.output,a.index_dir),ensure_ascii=False,indent=2))
if __name__=="__main__":main()
