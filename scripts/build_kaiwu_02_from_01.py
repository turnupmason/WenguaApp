"""Add Kaiwu Part 2 to the immutable multibook archive.

Source-preserving, append-only, candidate-only. Shared concept IDs do not replace
Shenqi V1, Kaiwu part 1, error cases, or any earlier provenance. Textual didactic
figures and later references to Shenqi are not Qimen case charts or new cases.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE_SHA = "e245f90fadba5a9af8fb2c14220cc38a7de82659c5c22aeb0bf441a2b9de313a"
SOURCE_SHA = "6310246fdaff6dad6516e5ae173b26beac9d9eb563d0044b620cbf3c0e5cab83"
SECTION = "four_factors_ch02"
CHAPTER = "kaiwu/four_factors_ch02/v1"
TRACK = "kaiwu:source_v1:shijia_zhuanpan"
BASE_ARCHIVE = "WenguaApp_神奇之门21章_开悟之门1篇_103案例_完整研究库.sqlite3"
NEW_ARCHIVE = "WenguaApp_神奇之门21章_开悟之门2章_103案例_完整研究库.sqlite3"
STAGES = ("长生","沐浴","冠带","临官","帝旺","衰","病","死","墓","绝","胎","养")
BRANCHES = "子丑寅卯辰巳午未申酉戌亥"
STEM_SOURCE = {"甲":79,"乙":91,"丙":103,"丁":115,"戊":127,"己":127,
               "庚":129,"辛":141,"壬":153,"癸":165}
# Source's own author-given sequences, stage order = STAGES. Derived rows are checked
# against the literal line containing the full twelve-stage enumeration.
STEM_SEQUENCE = {
 "甲":"亥子丑寅卯辰巳午未申酉戌",
 "乙":"午巳辰卯寅丑子亥戌酉申未",
 "丙":"寅卯辰巳午未申酉戌亥子丑",
 "丁":"酉申未午巳辰卯寅丑子亥戌",
 "戊":"寅卯辰巳午未申酉戌亥子丑",
 "己":"酉申未午巳辰卯寅丑子亥戌",
 "庚":"巳午未申酉戌亥子丑寅卯辰",
 "辛":"子亥戌酉申未午巳辰卯寅丑",
 "壬":"申酉戌亥子丑寅卯辰巳午未",
 "癸":"卯寅丑子亥戌酉申未午巳辰"}
BRANCH_PALACE = {"子":1,"丑":8,"寅":8,"卯":3,"辰":4,"巳":4,
 "午":9,"未":2,"申":2,"酉":7,"戌":6,"亥":6}
STARS = [
 ("天蓬星",1,"水",36),("天芮星",2,"土",37),("天冲星",3,"木",38),
 ("天辅星",4,"木",39),("天禽星",5,"土",40),("天心星",6,"金",41),
 ("天柱星",7,"金",42),("天任星",8,"土",43),("天英星",9,"火",44)]
DOORS = [("开",6,201),("休",1,202),("生",8,203),("死",2,204),
 ("惊",7,205),("伤",3,206),("杜",4,207),("景",9,208)]
DEITIES = [("值符",231),("螣蛇",232),("太阴",233),("六合",234),
           ("白虎",235),("玄武",236),("九地",237),("九天",238)]
SIX_JIA = [("甲子","戊",11),("甲戌","己",12),("甲申","庚",13),
           ("甲午","辛",14),("甲辰","壬",15),("甲寅","癸",16)]
SHENQI_CITES = [27,40,42,43,44,180,182,188,199]
METHODS = [
 ("jia_two_meanings",9,"history_of_jia_military_and_stem"),
 ("nine_visible_stems",10,"six_instruments_three_wonders_not_visible_jia"),
 ("six_jia_generation",17,"five_element_sequence_military_flags"),
 ("three_wonders_origin",19,"three_cherished_symbols_as_book_allegory"),
 ("three_wonders_sun_moon_star",20,"yi_bing_ding_three_rare_attributes"),
 ("main_versus_guest_war",22,"jia_defender_geng_attacker_conditional"),
 ("three_wonders_counter_geng",23,"different_allegorical_strategies_and_ding_ding"),
 ("three_wonders_roles",25,"military_advisor_bodyguard_logistics_context"),
 ("fixed_nine_symbol_cycle",27,"wujigengxinrenguidingbingyi_casting_cycle"),
 ("four_factor_roles",34,"heaven_place_people_deity_four_noninterchangeable_layers"),
 ("heaven_stars_context",35,"nine_star_role_weather_social_and_individual"),
 ("star_yinyang_relative",39,"tianfu_polarity_depends_on_reference_frame"),
 ("center_no_ninth_gate",40,"tianqin_center_lodges_kun_with_tianrui_distinct_stems"),
 ("star_fuyin_fanyin",45,"star_return_home_vs_opposite_palace"),
 ("star_follow_hour_stem",56,"on_duty_star_rotates_with_hour_stem"),
 ("ordinary_wuxing_seasons",57,"earthly_element_wang_xiang_xiu_qiu_si"),
 ("heaven_star_not_earthly_cycle",58,"nine_star_wang_xiang_xiu_qiu_fei"),
 ("star_interaction_order",59,"star_to_palace_element_effect"),
 ("star_month_example",60,"tianpeng_month_as_secondary_context"),
 ("star_palace_priority",61,"palace_primary_month_secondary"),
 ("earth_advantage_yongshen",76,"heavenly_stem_palace_twelve_states"),
 ("twelve_growth_stages",77,"twelve_growth_stage_order"),
 ("heavenly_yang_forward_yin_backward",78,"different_from_branch_element_cycle"),
 ("heavenly_stem_vs_branch_cycle",128,"stems_yang_yin_split_branches_only_clockwise"),
 ("growth_stages_symbolism",177,"stages_describe_analogies_not_clinical"),
 ("advantage_stage_groups",178,"five_growth_five_decline_two_gestation"),
 ("grave_versus_storehouse",179,"in_grave_when_unfavorable_month_storehouse_when_favorable"),
 ("age_stage_old_young_claim",181,"traditional_age_explanation_not_approved"),
 ("people_eight_doors",187,"door_as_human_factor"),
 ("three_good_doors",189,"open_rest_life_default"),
 ("three_unfavorable_doors",190,"death_fright_injury_default"),
 ("neutral_doors",191,"du_jing_conditional"),
 ("door_context_overrides",192,"no_unconditional_door_auspiciousness"),
 ("open_door_conditional",193,"surgery_or_disclosure_not_universal_benefit"),
 ("missing_person_door_context",194,"life_door_delay_unfavorable_gate_may_return"),
 ("death_door_context",195,"funerals_and_hunting_context"),
 ("hurt_door_context",196,"debt_pursuit_competition_context"),
 ("context_specificity",197,"domain_specific_before_valence"),
 ("door_palace_interactions",198,"he_ yi_ po_ zhi_with_month"),
 ("door_open_ended_context",220,"do_not_expand_as_hardcoded_universal_rule"),
 ("deities_symbolic_not_proof",225,"historical_symbolic_tradition"),
 ("deities_role",229,"deity_support_requires_context"),
 ("deities_eight",230,"eight_not_ninth_center"),
 ("deities_dynamic_rotation",239,"deities_follow_zhifu_yang_shun_yin_ni")
]
DOOR_CONDITIONS = [
 ("open_with_white_tiger",193,"开",("白虎",),"health_or_pregnancy_surgery_possible"),
 ("open_discloses_secrecy",193,"开",("保密",),"disclosed_not_guaranteed"),
 ("life_missing_delays",194,"生",("行人走失",),"may_temporarily_delay_return"),
 ("death_fright_hurt_missing",194,"死惊伤",("行人走失",),"may_prompt_return_not_guaranteed"),
 ("death_funeral_or_fishing",195,"死",("吊丧埋葬打猎钓鱼",),"may_be_favorable_in_this_context"),
 ("hurt_debt_or_competition",196,"伤",("索债竞争捕盗渔猎",),"may_be_suitable_in_this_context"),
 ("auspicious_door_generates_palace",198,"吉门",("门生宫",),"auspicious_can_be_strengthened"),
 ("inauspicious_door_generates_palace",198,"凶门",("门生宫",),"unfavorable_can_be_strengthened"),
 ("door_controls_palace",198,"门克宫",("迫",),"judgment_requires_door_valence"),
 ("palace_controls_door",198,"宫克门",("制",),"judgment_requires_door_valence")
]
FIGURE_SPANS = {
 23:(47,54),24:(64,71),25:(81,88),26:(93,100),27:(105,112),
 28:(117,124),29:(131,138),30:(143,150),31:(155,162),32:(167,174),
 33:(211,218)
}

def hash_bytes(raw): return hashlib.sha256(raw).hexdigest()
def canon(x): return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":"))
def text_of(lines,a,b=None):
 b=a if b is None else b
 if not 1<=a<=b<=len(lines):raise ValueError(("Invalid original source span",a,b))
 return "\n".join(lines[a-1:b])
def source_lines(raw):
 if hash_bytes(raw)!=SOURCE_SHA:raise ValueError("Wrong complete Kaiwu chapter-2 SHA256")
 lines=raw.decode("utf-8").splitlines()
 if len(lines)!=239 or lines[:3]!=["第二章","","关乎事物成败的四大要素"]:
  raise ValueError("Unexpected second chapter title and source line boundary")
 required={7:"第一节 十天干与九宫八卦阵",29:"第二节 天时、地利、人和、神助四大要素",
          31:"(一) 天时——九星",73:"(二) 地利——十天干落宫状态",
          184:"(三) 人和——八门",222:"(四) 神助——八神"}
 for ln,name in required.items():
  if lines[ln-1]!=name:raise ValueError(("Changed historical source heading",ln,name))
 return lines

def figures(lines):
 out=[]
 for number,(start,end) in FIGURE_SPANS.items():
  if "图"+str(number) not in text_of(lines,end):
   raise ValueError(("Source figure end missing",number))
  figure=text_of(lines,start,end)
  if number!=24 and number not in (23,33) and "宫" not in figure:
   raise ValueError(("Source status chart missing",number))
  out.append({"figure":number,"source_start_line":start,"source_end_line":end,
              "figure_type":"didactic_nine_star_month_example" if number==24 else
                 "didactic_symbol_and_twelve_stage_table",
              "printed_actual_qimen_cast":False,
              "excerpt_sha256":hash_bytes(figure.encode("utf-8"))})
 return out

def extract(lines):
 out=[];seen=set()
 def add(concept,kind,line,details,relation="clarifies",track=None,end=None):
  stop=end or line
  literal=text_of(lines,line,stop)
  if not literal.strip():raise ValueError(("Missing original cited passage",line))
  key=(concept,line)
  if key in seen:raise ValueError(("Same concept occurrence key repeated",key))
  seen.add(key)
  out.append({"concept_id":concept,"kind":kind,"source_start_line":line,
   "source_end_line":stop,"source_excerpt_sha256":hash_bytes(literal.encode("utf-8")),
   "track_id":track or TRACK+":"+kind,"relation_to_prior":relation,
   "normalized":details,"review_status":"draft","positive_training_eligible":False})
 def historical(ln):
  return {"source_subject":"author_historical_symbolic_interpretation",
          "source_line":ln,"not_independent_scientific_validation":True}

 for jia,flag,line in SIX_JIA:
  literal=text_of(lines,line)
  if jia not in literal or flag not in literal:raise ValueError(("Six-Jia flag mismatch",line))
  add("six_jia:"+jia,"six_jia_hidden_instrument",line,
      {"jia":jia,"hidden_flag":flag,"military_metaphor":True},relation="reaffirms",
      track=TRACK+":six_jia_flags")
 for wonder,line,meaning in (("乙",20,"日奇"),("丙",20,"月奇"),("丁",20,"星奇")):
  if meaning not in text_of(lines,line):raise ValueError(("Wonder source missing",wonder))
  add("wonder:"+wonder,"three_wonders_solar_metaphor",line,
      {"stem":wonder,"author_claimed_name":meaning,"not_astronomical_causation":True},
      relation="clarifies",track=TRACK+":three_wonders")

 for star,palace,element,line in STARS:
  assert star in text_of(lines,line)
  add("star:"+star,"nine_star_original_palace",line,
      {"star":star,"home_palace":palace,"element":element,
       "conditional_auspiciousness":True,"not_static_forecast":True,
       "center_tianqin_not_ninth_gate":star=="天禽星"},
      relation="clarifies",track=TRACK+":nine_star_original_palace")
  add("star:"+star+":scope","nine_star_context_interpretation",line,
      {"source_line_full_original_required":True,
       "polarity_depends_on_interpretation_frame":star in ("天辅星","天心星"),
       "not_direct_personal_accusation_or_medical_diagnosis":True,
       "author_cultural_assertion":True},relation="extends",
      track=TRACK+":nine_star_application_scope")

 for stem,line in STEM_SOURCE.items():
  original=text_of(lines,line)
  sequence=STEM_SEQUENCE[stem]
  if len(sequence)!=12 or len(set(sequence))!=12:raise ValueError(("Bad stem states",stem))
  if stem in ("戊","己"):
   # This manuscript explicitly equates 戊 with 丙 and 己 with 丁, not with
   # the Earth-branch water/soil cycle explained on the NEXT line.
   if ("戊土" not in original or "己土" not in original or "丙火" not in original
       or "丁火" not in original):
    raise ValueError("Stem earth-fire shared cycle is missing")
  for stage,branch in zip(STAGES,sequence):
   if stage+"在"+branch not in original:
    raise ValueError(("Original author stem/stage cannot be located",stem,stage,branch,line))
   add("stem:"+stem+":stage:"+stage,"heavenly_stem_twelve_state",line,
       {"stem":stem,"stage":stage,"branch":branch,"palace":BRANCH_PALACE[branch],
        "same_palace_may_contain_two_distinct_branches":True,
        "yang_forward_yin_reverse":True,
        "is_heavenly_stem_not_branch_cycle":True,
        "earth_stem_follows_fire_stem":stem in ("戊","己")},
        relation="reaffirms",track=TRACK+":heavenly_stem_life_cycle")
  add("stem:"+stem,"heavenly_stem_twelve_state_summary",line,
      {"stem":stem,"state_to_branch":dict(zip(STAGES,sequence)),
       "birth_palace":BRANCH_PALACE[sequence[0]],
       "graceful_conflict_handling":"do_not_replace_prior_source"},
      relation="clarifies",track=TRACK+":heavenly_stem_life_cycle_summary")
 # Conditional seasonal rule: 5 states based on STAR's element vs palace element.
 for condition,state,reason in [
  ("star_element_generates_palace","旺","我生之宫"),
  ("star_element_equals_palace","相","与我五行相同"),
  ("star_element_controls_palace","休","我克之宫"),
  ("palace_element_generates_star","废","生我之宫"),
  ("palace_element_controls_star","囚","克我之宫")]:
  add("star:seasonal:"+state,"nine_star_wang_xiang_xiu_qiu_fei",59,
      {"if":condition,"then":state,"author_category":reason,
       "priority":"palace_first_and_month_secondary",
       "not_ordinary_earthly_wang_xiang_xiu_qiu_si":True},
      relation="clarifies",track=TRACK+":heavenly_star_energy")
 for d,p,ln in DOORS:
  if d+"门" not in text_of(lines,ln):raise ValueError(("Missing door",d,ln))
  add("door:"+d,"eight_door_domain_roles",ln,
      {"door":d,"fixed_original_palace":p,
       "contextual_roles_are_in_complete_source_passage":True,
       "do_not_apply_all_roles_in_one_question":True},
      relation="extends",track=TRACK+":eight_door_domains")
 for deity,ln in DEITIES:
  if deity not in text_of(lines,ln):raise ValueError(("Missing eight deity",deity))
  add("deity:"+deity,"eight_deity_contextual_symbol",ln,
      {"deity":deity,"source_is_cultural_symbolism":True,
       "not_actual_proof_of_crime_illness_or_fate":True,
       "may_have_both_favorable_and_unfavorable_contexts":True},
      relation="extends",track=TRACK+":eight_deity_domains")
 for key,line,description in METHODS:
  add("kaiwu:four_factors:method:"+key,"conditional_source_method",line,
      {"method_topic":description,"requires_domain_and_full_source_conditions":True,
       "unverified_human_rule":True},
      relation="clarifies",track=TRACK+":conditional_method")
 for key,line,door,preconditions,conclusion in DOOR_CONDITIONS:
  add("door:conditional:"+key,"door_palace_domain_exception",line,
      {"door_or_relation":door,"additional_conditions":preconditions,
       "author_qualified_effect":conclusion,
       "actual_outcome_not_verified":True},
      relation="extends",track=TRACK+":domain_conditional_door")
 return out

def references(lines):
 out=[]
 for ln in SHENQI_CITES:
  passage=text_of(lines,ln)
  m=re.search(r"《神奇之门》第(\d+(?:[~～-]\d+)?)页",passage)
  if not m:raise ValueError(("Cannot locate author cross-book printed citation",ln))
  topic=("prior_explicit_error_and_retrospective_correction" if ln in (180,199)
     else "former_book_case_with_book_only_narrative" if ln in (40,182)
     else "former_book_rule_or_example_not_new_independent_case")
  out.append({"source_line":ln,"target_book":"shenqi",
              "cited_printed_page":m.group(1),
              "ref_id":"kaiwu:four_factors:shenqi_reference:"+str(ln),
              "reference_role":topic,"new_event_family":False,
              "new_qimen_cast":False,"verified_old_event_id":None,
              "source_only_does_not_independently_validate_prediction":True,
              "review_status":"draft"})
 return out

def compare_legacy(old,new):
 for (table,) in old.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"):
  columns=[x[1] for x in old.execute('PRAGMA table_info("'+table+'")')]
  expr=",".join('"'+c+'"' for c in columns)
  rows=set(new.execute('SELECT '+expr+' FROM "'+table+'"'))
  if not all(row in rows for row in old.execute('SELECT '+expr+' FROM "'+table+'"')):
   raise ValueError("Prior database altered source rows: "+table)

def build(base,source,output,index_dir):
 base,source,output,index_dir=map(Path,(base,source,output,index_dir))
 if output.exists():raise ValueError("No overwrite of earlier SQLite version")
 if hash_bytes(base.read_bytes())!=BASE_SHA:raise ValueError("Wrong current complete V1 baseline")
 raw=source.read_bytes()
 lines=source_lines(raw);entries=extract(lines);figs=figures(lines);links=references(lines)
 if len(STEM_SOURCE)!=10 or len([x for x in entries if x["kind"]=="heavenly_stem_twelve_state"])!=120:
  raise ValueError("All 120 source stages must be recorded")
 if len(figs)!=11 or len(links)!=9:
  raise ValueError("Full diagram and crossreference audit required")
 output.parent.mkdir(parents=True,exist_ok=True)
 with sqlite3.connect("file:"+str(base)+"?mode=ro",uri=True) as old,sqlite3.connect(output) as db:
  old.backup(db)
  db.execute("PRAGMA foreign_keys=ON")
  with db:
   if db.execute("SELECT 1 FROM sections WHERE book_id='kaiwu' AND section_key=?",(SECTION,)).fetchone():
    raise ValueError("Already imported Kaiwu part2; no duplicate")
   if db.execute("SELECT count(*) FROM sections WHERE book_id='kaiwu'").fetchone()[0]!=1:
    raise ValueError("First Kaiwu source is missing")
   db.execute("""INSERT INTO sections(book_id,section_key,title,original_text,sha256,content_version,reviewed)
    VALUES ('kaiwu',?,?,?,?,1,0)""",(SECTION,lines[2],raw.decode("utf-8"),SOURCE_SHA))
   sid=db.execute("SELECT last_insert_rowid()").fetchone()[0]
   db.execute("""INSERT INTO chapter_knowledge(chapter_key,book_id,title,source_sha256,
    source_length_bytes,knowledge_version,review_status)
    VALUES (?,'kaiwu',?,?,'1','draft')""",(CHAPTER,lines[2],SOURCE_SHA,len(raw)))
   for item in entries:
    line=item["source_start_line"];end=item["source_end_line"];cid=item["concept_id"]
    metadata={k:v for k,v in item.items() if k not in ("source_start_line","source_end_line","concept_id","kind")}
    db.execute("""INSERT INTO semantic_assertions
     (chapter_key,concept_id,kind,relation,source_start_line,source_end_line,
     metadata_json,original_excerpt,review_status)
     VALUES (?,?,?,?,?,?,?,?,'draft')""",
     (CHAPTER,cid,item["kind"],item["relation_to_prior"],line,end,
      canon(metadata),text_of(lines,line,end)))
    db.execute("""INSERT INTO cross_book_concept_tracks
     (chapter_key,concept_id,source_start_line,source_end_line,source_section_id,source_sha256,
     excerpt_sha256,track_id,relation_to_prior,comparison_state,normalized_json,review_status)
     VALUES (?,?,?,?,?,?,?,?,?,'candidate_not_human_verified',?,'draft')""",
     (CHAPTER,cid,line,end,sid,SOURCE_SHA,item["source_excerpt_sha256"],
      item["track_id"],item["relation_to_prior"],canon(item["normalized"])))
   for ref in links:
    db.execute("""INSERT INTO cross_book_example_references
     (source_chapter_key,source_line,target_book_id,target_printed_page,reference_key,
     metadata_json,verified_target_case_id)
     VALUES (?,?,'shenqi',?,?,?,NULL)""",
     (CHAPTER,ref["source_line"],ref["cited_printed_page"],ref["ref_id"],canon(ref)))
   db.execute("""INSERT INTO chapter_archival_versions
      (archive_label,baseline_sha256,new_db_sha256,contains_complete_private_copyright_source,
       snapshot_type,created_utc,repo_public_archive_policy)
      VALUES (?,?,NULL,1,'additive_multibook_source_version','2026-10-20',
       'user_authorized_public_full_sqlite_versions')""",
      ("shenqi21_kaiwu02_103_existing_cases",BASE_SHA))
  compare_legacy(old,db)
  if db.execute("PRAGMA integrity_check").fetchone()[0]!="ok" or db.execute("PRAGMA foreign_key_check").fetchall():
   raise ValueError("Database failed SQLite integrity")
  expected={"sections":23,"cases":103,"historical_case_reasoning":495,
     "historical_palace_standardization":1008,
     "semantic_assertions":1465+len(entries),
     "cross_book_concept_tracks":208+len(entries),
     "cross_book_example_references":6+len(links)}
  actual={table:db.execute('SELECT count(*) FROM "'+table+'"').fetchone()[0] for table in expected}
  if actual!=expected:raise ValueError(("Unexpected cumulative totals",actual,expected))
  if db.execute("SELECT count(*) FROM historical_case_reasoning_trace WHERE positive_training_eligible=1").fetchone()[0]:
   raise ValueError("No unchecked historical author chains may be promoted")
  if db.execute("SELECT count(*) FROM historical_case_book_verdicts WHERE verdict='author_book_error_explicit'").fetchone()[0]!=6:
   raise ValueError("Historical author-confirmed wrong answers changed")
  if db.execute("SELECT count(*) FROM cases WHERE case_id LIKE 'kaiwu.%'").fetchone()[0]:
   raise ValueError("Old-book references must not become fabricated Kaiwu events")
  db.execute("VACUUM")
  db.commit()
  if db.execute("PRAGMA integrity_check").fetchone()[0]!="ok" or db.execute("PRAGMA foreign_key_check").fetchall():
   raise ValueError("Final version corrupted")
 index_dir.mkdir(parents=True,exist_ok=True)
 counts={"six_jia":6,"three_wonders":3,"nine_star_profiles":9,"twelve_stem_stage_assertions":120,
  "doors":8,"eight_deities":8,"conditional_method_passages":len(METHODS),
  "door_context_exceptions":len(DOOR_CONDITIONS)}
 doc={"schema":"wengua_multibook_source_chapter_v2","source_book":"kaiwu","section_key":SECTION,
      "chapter_key":CHAPTER,"book_chapter_number":2,"source_sha256":SOURCE_SHA,
      "source_bytes":len(raw),"source_lines":len(lines),"source_title":lines[2],
      "source_sections":{"first_section":7,"second_section":29,"heaven_stars":31,
       "earth_advantage":73,"human_doors":184,"deities":222},
      "source_tables":len(figs),"source_figures":list(FIGURE_SPANS),
      "source_ends_without_terminal_punctuation":not lines[-1].rstrip().endswith(("。",".","！","!","？","?")),
      "source_scope_warning":"exact supplied file only; do not invent continuation if book has additional pages",
      "book_counts":{"shenqi":21,"kaiwu":2},"total_source_sections":23,
      "new_concept_occurrences":len(entries),"new_cross_book_citations":len(links),
      "new_independent_event_families":0,"new_original_qimen_charts":0,
      "total_event_families":103,"total_historical_qimen_charts":112,
      "all_previous_source_rows_preserved":True,
      "source_record_type_counts":counts,"cumulative_semantic_assertions":expected["semantic_assertions"],
      "cumulative_author_steps":495,"review_status":"draft",
      "positive_training_eligible":False,
      "draft_only_not_independent_scientific_proof":True,
      "baseline_sha256":BASE_SHA,"produced_db_sha256":hash_bytes(output.read_bytes()),
      "counts":actual}
 def save(name,payload):
  (index_dir/name).write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 save("chapter_manifest.json",doc)
 save("concept_tracks.json",{"schema":"wengua_kaiwu_second_source_occurrences_v1",
       "chapter_key":CHAPTER,"source_sha256":SOURCE_SHA,"entries":entries})
 save("cross_book_links.json",{"schema":"wengua_cross_book_references_v2",
       "source_sha256":SOURCE_SHA,"links":links,"no_new_case_or_chart":True})
 save("figure_index.json",{"source_sha256":SOURCE_SHA,
       "didactic_not_historical_cast":True,"figures":figs})
 save("source_audit.json",{"source_sha256":SOURCE_SHA,"boundary_source_line":239,
      "source_tail_may_be_incomplete":doc["source_ends_without_terminal_punctuation"],
      "star_state_priority":"palace_first_month_secondary",
      "not_equivalent_to_earthly_wang_xiang_xiu_qiu_si":True,
      "tianqin_lodged_kun_2_without_fabricated_center_door":True,
      "heaven_stem_soil_follows_fire_but_branch_soil_follows_water":True,
      "grave_vs_storehouse_requires_month_status":True,
      "former_error_examples_lines":[180,199],
      "no_backfilling_old_errors_as_initial_correct_calls":True,
      "positive_training_eligible":False,"independent_realworld_validation":False})
 return doc

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--base",required=True);p.add_argument("--source",required=True)
 p.add_argument("--output",required=True);p.add_argument("--index-dir",required=True)
 a=p.parse_args()
 print(json.dumps(build(a.base,a.source,a.output,a.index_dir),
                  ensure_ascii=False,indent=2))
if __name__=="__main__":main()
