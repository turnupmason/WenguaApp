"""Append 《开悟之门》第五章 without losing any prior book, V1, or error case.

12 literal classical verses and 12 independent author commentaries are preserved
separately. Verse search fragments and evidence-anchored contextual readings are
source DRAFTS; no verified prediction cases or user-level life diagnoses arise.
"""
from __future__ import annotations
import argparse,hashlib,json,re,sqlite3
from pathlib import Path
from collections import Counter

ROOT=Path(__file__).resolve().parents[1]
BASE_SHA="eeb1a6ee67e49eb76bb3f982c44c78db830d8eaf827316860c519e687497507d"
SOURCE_SHA="0a40f638a61bafcdb0a215925a348e3b5da0aa3586d79d952fb72a63f1e5ffa2"
BASE_NAME="WenguaApp_神奇之门21章_开悟之门4章_103案例_完整研究库.sqlite3"
NEW_NAME="WenguaApp_神奇之门21章_开悟之门5章_103案例_完整研究库.sqlite3"
CHAPTER="kaiwu/classical_fate_exposition_ch05/v1"
SECTION="classical_fate_exposition_ch05"
TRACK="kaiwu:source_v1:traditional_fate"
VERSES=("第一","第二","第三","第四","第五","第六","第七","第八","第九","第十","第十一","第十二")
FATE_SCOPE={1:"bureaus_and_palace_body_correspondence",
 2:"family_spouse_and_workplace_yongshen",
 3:"void_clash_and_directional_stem_claims",
 4:"life_gate_property_and_inside_outside",
 5:"void_opposite_twelve_stages",
 6:"nine_stars_auspicious_conditions",
 7:"eight_doors_domain_careers",
 8:"eight_doors_stars_weak_vs_strong",
 9:"nine_star_seasonal_conditions",
 10:"directed_stem_combinations_in_fate_readings",
 11:"spouse_symbols_high_low_net_and_guest_host",
 12:"void_fuyin_fanyin_and_interpretive_caveats"}
# Each literal phrase below must exist on the exact original verse/commentary
# line; these are NOT generated outcomes, validated claims, or rewritten classics.
MOTIFS=[
 (1,"commentary","我提倡用拆补法定局","casting:bureau:chaibu_preferred","casting_method"),
 (1,"commentary","用置闰法定局","casting:bureau:zhirun_super_spirit","casting_method"),
 (1,"commentary","离9宫代表一个人的头部和面部","palace:9:body_head_face","palace_body"),
 (1,"commentary","乾6宫和艮8宫","palace:6:8:body_legs","palace_body"),
 (1,"commentary","坤2宫和巽4宫","palace:2:4:shoulder_ear","palace_body"),
 (1,"commentary","震3宫和兑7宫","palace:3:7:chest","palace_body"),
 (1,"commentary","坎1宫代表男女的阴部和肾","palace:1:urogenital","palace_body"),
 (1,"commentary","中5宫代表一个人的心脏和腹部","palace:5:heart_abdomen","palace_body"),
 (2,"verse","年干父母，月干兄弟，日干本身，时干子女","yongshen:family:four_pillars","family_role"),
 (2,"commentary","年干为上级领导","yongshen:work:year_superior","workplace_role"),
 (2,"commentary","以值符为顶头上司","yongshen:work:zhifu_boss","workplace_role"),
 (2,"commentary","以月干为同事","yongshen:work:month_colleague","workplace_role"),
 (2,"commentary","时干为下级","yongshen:work:hour_subordinate","workplace_role"),
 (2,"verse","乙丁之落宫","yongshen:relationship:yi_ding","relationship_role"),
 (2,"verse","庚丙二干","yongshen:relationship:geng_bing","relationship_role"),
 (2,"commentary","以求测之人的“日干”相合之干","yongshen:spouse:day_stem_combination","relationship_role"),
 (2,"commentary","男女双方的年命落宫","yongshen:spouse:both_birth_year","relationship_role"),
 (3,"commentary","用神逢空亡为孤，落空亡对冲之宫为虚","fate:solitary:void_and_opposite","void_opposite"),
 (3,"commentary","庚落乾宫","fate:geng:palace6_father_claim","symbolic_kin_claim"),
 (3,"commentary","庚落坤宫","fate:geng:palace2_mother_claim","symbolic_kin_claim"),
 (3,"commentary","庚落入月干所在的宫位","fate:geng:month_sibling_claim","symbolic_kin_claim"),
 (3,"commentary","乙+庚，庚+乙均为刑格","fate:yi_geng:ordered_pair_punishment","directional_stem_context"),
 (3,"commentary","时干加庚，或庚加时干","fate:hour_geng:children_claim","directional_stem_context"),
 (4,"commentary","生门代表一个人一生的财运和产业","door:生:fortune_wealth_property","wealth_context"),
 (4,"commentary","生门临庚落宫冲克日干之宫","fate:fortune:life_gate_geng_overcomes_day","conditional_palace_relation"),
 (4,"commentary","日干冲克生门与庚的落宫","fate:fortune:day_overcomes_life_geng","conditional_palace_relation"),
 (4,"commentary","生门落在外盘，而日干本身落在内盘","fate:fortune:life_outer_day_inner","inside_outside"),
 (4,"commentary","日干本身落在外盘，而生门落在内盘","fate:fortune:day_outer_life_inner","inside_outside"),
 (4,"commentary","日干本身与生门二者都落在内盘宫","fate:fortune:day_life_both_inner","inside_outside"),
 (4,"commentary","日干本身和生门都落在外盘宫","fate:fortune:day_life_both_outer","inside_outside"),
 (5,"verse","日值孤，时值虚","fate:time:void_day_opposite_hour","void_opposite"),
 (5,"verse","时落孤，日落虚","fate:time:void_hour_opposite_day","void_opposite"),
 (5,"verse","命被冲克","fate:birth_year:palace_clash","birth_year"),
 (5,"verse","日临墓绝","fate:day:grave_extinction","twelve_state"),
 (6,"commentary","戊+丙","stem_pair:戊:丙","career_guest_host"),
 (6,"commentary","丙+戊","stem_pair:丙:戊","career_guest_host"),
 (6,"commentary","天辅星落宫或月令旺相","star:天辅星:career_condition","star_profession"),
 (6,"commentary","日干临天冲星","star:天冲星:career_condition","star_profession"),
 (6,"commentary","天禽星本是位镇中宫之星","star:天禽星:center_host_career","star_profession"),
 (6,"commentary","日干如果临天柱星","star:天柱星:career_condition","star_profession"),
 (6,"commentary","日干如果临天心星","star:天心星:career_condition","star_profession"),
 (6,"commentary","日干临天任星","star:天任星:career_condition","star_profession"),
 (6,"commentary","天芮星是颗凶星","star:天芮星:career_condition","star_profession"),
 (6,"commentary","日干临天蓬星","star:天蓬星:career_condition","star_profession"),
 (7,"verse","开门有奇","door:开:career_with_wonder","door_profession"),
 (7,"verse","伤门得令","door:伤:career_in_season","door_profession"),
 (7,"verse","生门得奇","door:生:career_with_wonder","door_profession"),
 (7,"verse","景门合局","door:景:career_matching_chart","door_profession"),
 (7,"verse","惊门入式","door:惊:career_matches_pattern","door_profession"),
 (7,"verse","休门合奇","door:休:career_with_wonder","door_profession"),
 (7,"verse","杜门得地","door:杜:career_palace","door_profession"),
 (7,"verse","死门得奇","door:死:career_with_wonder","door_profession"),
 (8,"verse","开门、心星皆是金","door_star:开:天心:metal","door_star_strength"),
 (8,"verse","休门、天蓬同是水","door_star:休:天蓬:water","door_star_strength"),
 (8,"verse","生门、天任是土宿","door_star:生:天任:earth","door_star_strength"),
 (8,"verse","伤门、天冲皆为木","door_star:伤:天冲:wood","door_star_strength"),
 (8,"verse","杜门、天辅亦是木","door_star:杜:天辅:wood","door_star_strength"),
 (8,"verse","景门、天英为火宿","door_star:景:天英:fire","door_star_strength"),
 (8,"verse","死门、天芮俱是土","door_star:死:天芮:earth","door_star_strength"),
 (8,"verse","惊门、天柱同属金","door_star:惊:天柱:metal","door_star_strength"),
 (8,"commentary","在失局的前提下","fate:occupation:overall_chart_weakness_required","qualification"),
 (8,"commentary","处在休或衰、病、胎、养状态","fate:occupation:some_vitality","qualification"),
 (8,"commentary","死、囚、墓、绝状态","fate:occupation:extreme_weakness","qualification"),
 (9,"commentary","九星也必须分析其旺相休囚废","star:five_states:heavenly_vs_earthly","star_seasonal_method"),
 (9,"verse","天蓬乘时","star:天蓬星:career_seasonal","star_seasonal_method"),
 (9,"verse","天任得地","star:天任星:career_seasonal","star_seasonal_method"),
 (9,"verse","天冲有气者","star:天冲星:career_seasonal","star_seasonal_method"),
 (9,"verse","天辅为文昌","star:天辅星:career_seasonal","star_seasonal_method"),
 (9,"verse","天英火司南离","star:天英星:career_seasonal","star_seasonal_method"),
 (9,"verse","天芮本是黑星","star:天芮星:career_seasonal","star_seasonal_method"),
 (9,"verse","七赤天柱","star:天柱星:career_seasonal","star_seasonal_method"),
 (9,"verse","天心原是六白","star:天心星:career_seasonal","star_seasonal_method"),
 (10,"commentary","戊+丙","stem_pair:戊:丙","fate_directional_stem_pattern"),
 (10,"commentary","丙+戊","stem_pair:丙:戊","fate_directional_stem_pattern"),
 (10,"commentary","丁+戊","stem_pair:丁:戊","fate_directional_stem_pattern"),
 (10,"commentary","戊+丁","stem_pair:戊:丁","fate_directional_stem_pattern"),
 (10,"commentary","辛+乙","stem_pair:辛:乙","fate_directional_stem_pattern"),
 (10,"commentary","乙+辛","stem_pair:乙:辛","fate_directional_stem_pattern"),
 (10,"commentary","丁+癸","stem_pair:丁:癸","fate_directional_stem_pattern"),
 (10,"commentary","癸+丁","stem_pair:癸:丁","fate_directional_stem_pattern"),
 (10,"commentary","庚+丙","stem_pair:庚:丙","fate_directional_stem_pattern"),
 (10,"commentary","丙+庚","stem_pair:丙:庚","fate_directional_stem_pattern"),
 (10,"commentary","庚+戊","stem_pair:庚:戊","fate_directional_stem_pattern"),
 (10,"commentary","戊+庚","stem_pair:戊:庚","fate_directional_stem_pattern"),
 (10,"commentary","庚+乙","stem_pair:庚:乙","fate_directional_stem_pattern"),
 (10,"commentary","乙+庚","stem_pair:乙:庚","fate_directional_stem_pattern"),
 (10,"commentary","丁+庚","stem_pair:丁:庚","fate_directional_stem_pattern"),
 (10,"commentary","庚+丁","stem_pair:庚:丁","fate_directional_stem_pattern"),
 (10,"commentary","庚+癸","stem_pair:庚:癸","fate_directional_stem_pattern"),
 (10,"commentary","庚+壬","stem_pair:庚:壬","fate_directional_stem_pattern"),
 (11,"commentary","落入六、七、八、九宫为网高","fate:gui:high_net_huagai","high_low_palace_conditional"),
 (11,"commentary","落入一、二、三、四宫","fate:gui:low_net","high_low_palace_conditional"),
 (11,"commentary","乙奇落乾6宫入戌墓","fate:spouse:yi_tomb_6","tomb_condition"),
 (11,"commentary","乙奇在天盘、丁奇在地盘","fate:marriage:yi_guest_ding_host","directional_guest_host"),
 (11,"commentary","丁奇在天盘、乙奇在地盘","fate:marriage:ding_guest_yi_host","directional_guest_host"),
 (11,"commentary","玉女守门虽然是吉格","fate:marriage:jade_guard_context_exception","domain_override"),
 (12,"verse","诸格忌落空亡","fate:void:good_or_bad_pattern","void_conditional"),
 (12,"commentary","吉格逢空亡","fate:void:good_reduced","void_conditional"),
 (12,"commentary","凶格逢空亡","fate:void:bad_stronger","void_conditional"),
 (12,"commentary","八门反吟的格局","fate:doors:opposite_palace","fuyin_fanyin_conditional"),
 (12,"commentary","伏吟的格局","fate:doors:home_palace","fuyin_fanyin_conditional"),
]
def digest(b):return hashlib.sha256(b).hexdigest()
def jsonstr(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(",",":"))
def get_lines(b):
 if digest(b)!=SOURCE_SHA:raise ValueError("Kaiwu 5 uploaded source SHA256 mismatch")
 s=b.decode("utf-8")
 lines=s.splitlines()
 if len(lines)!=73 or lines[0]!="第五章 人生命运预测古文详解" or not s.endswith("\n"):
  raise ValueError("Original source chapter incomplete")
 if lines[-1].endswith("取得预期的效果。") is False:raise ValueError("Source ending mismatch")
 return lines

def pairs(lines):
 result=[]
 for n in range(1,13):
  head=3+(n-1)*6
  if lines[head-1]!=f"古文{VERSES[n-1]}段：" or lines[head+2]!="解说：":
   raise ValueError(("Ancient verse/commentary six-line marker broken",n,head))
  verse=lines[head];commentary=lines[head+3]
  if not verse or not commentary:raise ValueError("Verse or author explanation missing")
  result.append({"number":n,"topic":FATE_SCOPE[n],
    "verse_marker_line":head,"verse_source_line":head+1,"verse_original":verse,
    "verse_sha256":digest(verse.encode("utf-8")),
    "commentary_marker_line":head+3,"commentary_source_line":head+4,
    "commentary_original":commentary,
    "commentary_sha256":digest(commentary.encode("utf-8"))})
 return result

def evidence(lines,ps):
 records=[];used=set();occ=[]
 def add(concept,kind,ln,quote,track,metadata,relation):
  if quote not in lines[ln-1] or not quote:raise ValueError(("Source quote not present",concept,ln,quote))
  key=(concept,ln)
  if key in used:raise ValueError(("Duplicate concept-source key",key))
  used.add(key)
  records.append({"concept_id":concept,"source_start_line":ln,"source_end_line":ln,
    "original_excerpt":quote,"source_excerpt_sha256":digest(quote.encode("utf-8")),
    "kind":kind,"track_id":track,"relation_to_prior":relation,
    "normalized":metadata,"review_status":"draft","positive_training_eligible":False})
 for x in ps:
  n=x["number"]
  for layer,line,name in [("ancient_verse",x["verse_source_line"],"verse_original"),
                          ("author_explanation",x["commentary_source_line"],"commentary_original")]:
   add("kaiwu:fate:part:"+str(n)+":"+layer,
     "original_classical_text" if layer=="ancient_verse" else "author_separate_explanation",
     line,x[name],TRACK+":"+layer,
     {"verse_number":n,"original_layer":layer,"topic":x["topic"],
       "not_proven_as_real_life_outcome":True,"not_a_new_prediction_case":True},
     "additional_exposition")
 for i,(verse_number,layer,quote,cid,domain) in enumerate(MOTIFS,1):
  p=ps[verse_number-1]
  ln=p["verse_source_line"] if layer=="verse" else p["commentary_source_line"]
  if quote not in lines[ln-1]:
   raise ValueError(("Missing literal motif in author's layer",i,verse_number,quote))
  meta={"verse_number":verse_number,"layer":layer,"domain":domain,
    "author_claim_requires_entire_original_commentary_context":True,
    "current_fate_book_scope_not_universal":True,
    "not_externally_validated":True,
    "do_not_infer_character_crime_wealth_illness_from_symbol_alone":True}
  track=TRACK+":"+layer+":"+domain
  add(cid,"classical_fate_contextual_motif",ln,quote,track,meta,
      "extends" if cid.startswith(("stem_pair:","star:","door:","palace:","yongshen:","casting:")) else "additional_exposition")
  occ.append({"motif_key":f"kaiwu:fate:{verse_number}:motif:{i:03d}",
      "concept_id":cid,"source_line":ln,
      "verse_number":verse_number,"layer":"ancient_verse" if layer=="verse" else "author_explanation",
      "source_excerpt":quote,"excerpt_sha256":digest(quote.encode("utf-8")),
      "track_id":track,"condition":meta})
 if len(occ)!=len(MOTIFS):raise ValueError("All original motifs must be source-backed")
 return records,occ

def legacy_rows_intact(old,new):
 # Guaranteed full rowwise inclusion, not merely matching summary counts.
 for (table,) in old.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"):
  cols=[x[1] for x in old.execute('PRAGMA table_info("'+table+'")')]
  expr=",".join('"'+x+'"' for x in cols)
  old_rows=list(old.execute('SELECT '+expr+' FROM "'+table+'"'))
  present=set(new.execute('SELECT '+expr+' FROM "'+table+'"'))
  if not all(row in present for row in old_rows):
   raise ValueError("Previously archived rows changed: "+table)

def build(base,source,output,index_dir):
 base,source,output,index_dir=map(Path,(base,source,output,index_dir))
 if output.exists():raise ValueError("Do not overwrite any existing SQLite archive")
 if digest(base.read_bytes())!=BASE_SHA:raise ValueError("Wrong full 25-source historical base")
 raw=source.read_bytes();lines=get_lines(raw)
 ps=pairs(lines);items,motifs=evidence(lines,ps)
 if len([i for i,l in enumerate(lines,1) if "《神奇之门》" in l])!=1 or "《神奇之门》" not in lines[18]:
  raise ValueError("Cross-book citation count changed; do not invent page or cases")
 output.parent.mkdir(parents=True,exist_ok=True)
 with sqlite3.connect("file:"+str(base)+"?mode=ro",uri=True) as old,sqlite3.connect(output) as db:
  old.backup(db)
  db.executescript((ROOT/"schema/migrations/020_kaiwu_classical_fate_parallel_verses.sql").read_text("utf-8"))
  db.execute("PRAGMA foreign_keys=ON")
  with db:
   if db.execute("SELECT count(*) FROM sections WHERE book_id='kaiwu'").fetchone()[0]!=4:
    raise ValueError("Prior four Kaiwu chapters not present")
   if db.execute("SELECT 1 FROM sections WHERE book_id='kaiwu' AND section_key=?",(SECTION,)).fetchone():
    raise ValueError("This original source already imported")
   db.execute("""INSERT INTO sections(book_id,section_key,title,original_text,sha256,content_version,reviewed)
     VALUES ('kaiwu',?,?,?,?,1,0)""",(SECTION,lines[0],raw.decode("utf-8"),SOURCE_SHA))
   sid=db.execute("SELECT last_insert_rowid()").fetchone()[0]
   db.execute("""INSERT INTO chapter_knowledge(chapter_key,book_id,title,source_sha256,source_length_bytes,
      knowledge_version,review_status) VALUES (?,'kaiwu',?,?,?,'1','draft')""",
      (CHAPTER,lines[0],SOURCE_SHA,len(raw)))
   for x in ps:
    db.execute("""INSERT INTO kaiwu_classical_verse_explanations(chapter_key,verse_number,verse_marker_line,
       verse_source_line,verse_original_text,verse_source_sha256,commentary_marker_line,
       commentary_source_line,commentary_original_text,commentary_source_sha256)
       VALUES (?,?,?,?,?,?,?,?,?,?)""",(CHAPTER,x["number"],x["verse_marker_line"],x["verse_source_line"],
       x["verse_original"],x["verse_sha256"],x["commentary_marker_line"],
       x["commentary_source_line"],x["commentary_original"],x["commentary_sha256"]))
   for x in items:
    ln=x["source_start_line"]
    db.execute("""INSERT INTO semantic_assertions(chapter_key,concept_id,kind,relation,
      source_start_line,source_end_line,metadata_json,original_excerpt,review_status)
      VALUES (?,?,?,?,?,?,?,?,'draft')""",
      (CHAPTER,x["concept_id"],x["kind"],x["relation_to_prior"],
       ln,ln,jsonstr(x),x["original_excerpt"]))
    db.execute("""INSERT INTO cross_book_concept_tracks(chapter_key,concept_id,source_start_line,
      source_end_line,source_section_id,source_sha256,excerpt_sha256,track_id,
      relation_to_prior,comparison_state,normalized_json,review_status)
      VALUES (?,?,?,?,?,?,?,?,?,'candidate_not_human_verified',?,'draft')""",
      (CHAPTER,x["concept_id"],ln,ln,sid,SOURCE_SHA,x["source_excerpt_sha256"],
       x["track_id"],x["relation_to_prior"],jsonstr(x["normalized"])))
   for x in motifs:
    db.execute("""INSERT INTO kaiwu_classical_fate_motifs(chapter_key,motif_key,verse_number,
      source_line,layer,source_excerpt,excerpt_sha256,track_id,canonical_concept_id,
      normalized_conditions_json) VALUES (?,?,?,?,?,?,?,?,?,?)""",
      (CHAPTER,x["motif_key"],x["verse_number"],x["source_line"],x["layer"],
       x["source_excerpt"],x["excerpt_sha256"],x["track_id"],x["concept_id"],
       jsonstr(x["condition"])))
   db.execute("""INSERT INTO cross_book_example_references(source_chapter_key,source_line,
     target_book_id,target_printed_page,reference_key,metadata_json,verified_target_case_id)
     VALUES (?,19,'shenqi','unspecified_in_source',?,?,NULL)""",
     (CHAPTER,"kaiwu:fate:chapter5:prior_book_context",
     jsonstr({"source_line":19,"type":"general_author_reference_no_historical_case",
      "printed_page":None,"new_case":False,"verified_target_case_id":None,"review_status":"draft"})))
   db.execute("""INSERT INTO chapter_archival_versions(archive_label,baseline_sha256,
     new_db_sha256,contains_complete_private_copyright_source,snapshot_type,created_utc,
     repo_public_archive_policy) VALUES (?, ?,NULL,1,'additive_classical_verse_author_parallel','2026-10-20',
     'user_authorized_public_full_sqlite_versions')""",
     ("shenqi21_kaiwu05_103_existing_cases",BASE_SHA))
  legacy_rows_intact(old,db)
  if db.execute("PRAGMA integrity_check").fetchone()[0]!="ok" or db.execute("PRAGMA foreign_key_check").fetchall():
   raise ValueError("SQLite integrity after full backup failed")
  expected={"sections":26,"cases":103,"historical_case_reasoning":495,
    "historical_palace_standardization":1008,
    "semantic_assertions":2034+len(items),
    "cross_book_concept_tracks":777+len(items),
    "cross_book_example_references":42,
    "kaiwu_didactic_figures":14,"kaiwu_didactic_figure_cells":126,
    "kaiwu_ordered_stem_pair_occurrences":81,"kaiwu_timing_source_methods":20,
    "kaiwu_classical_verse_explanations":12,
    "kaiwu_classical_fate_motifs":len(motifs)}
  actual={key:db.execute('SELECT count(*) FROM "'+key+'"').fetchone()[0] for key in expected}
  if actual!=expected:raise ValueError(("Unexpected cumulative count",actual,expected))
  if db.execute("SELECT count(*) FROM historical_case_book_verdicts WHERE verdict='author_book_error_explicit'").fetchone()[0]!=6:
   raise ValueError("Historical wrong original predictions must survive")
  if db.execute("SELECT count(*) FROM historical_case_reasoning_trace WHERE positive_training_eligible=1").fetchone()[0]:
   raise ValueError("Unreviewed causal chains made eligible")
  if db.execute("SELECT count(*) FROM cases WHERE case_id LIKE 'kaiwu.%'").fetchone()[0]:
   raise ValueError("A new historical case was fabricated from classical text")
  db.execute("VACUUM");db.commit()
  if db.execute("PRAGMA integrity_check").fetchone()[0]!="ok" or db.execute("PRAGMA foreign_key_check").fetchall():
   raise ValueError("Final SQLite consistency failed")
 index_dir.mkdir(parents=True,exist_ok=True)
 manifest={"schema":"wengua_multibook_source_chapter_v5",
   "source_book":"kaiwu","chapter_key":CHAPTER,"section_key":SECTION,
   "source_title":lines[0],"source_sha256":SOURCE_SHA,"source_bytes":len(raw),
   "source_lines":len(lines),"original_verse_commentary_pairs":12,
   "original_classical_verses":12,"original_author_commentaries":12,
   "contextual_source_motifs":len(motifs),
   "new_semantic_source_occurrences":len(items),
   "book_counts":{"shenqi":21,"kaiwu":5},"total_source_sections":26,
   "only_general_reference_to_prior_book":1,"new_historical_event_families":0,
   "new_original_qimen_case_charts":0,
   "historical_cases_unchanged":103,"historical_printed_charts_unchanged":112,
   "historical_palace_cells_unchanged":1008,"author_reasoning_unchanged":495,
   "source_has_no_new_printed_chart":True,
   "ancient_text_distinguished_from_modern_author":True,
   "multiple_casting_bureau_methods_remain_distinct":True,
   "all_previous_rows_unchanged":True,"all_new_rules_draft":True,
   "positive_training_eligible":False,"human_verified_causal_chains":0,
   "source_fate_claims_not_independent_validation":True,
   "parent_sha256":BASE_SHA,"output_sha256":digest(output.read_bytes()),
   "counts":actual}
 def write(name,value):
  (index_dir/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 write("chapter_manifest.json",manifest)
 write("classical_verses_and_author_explanations.json",
    {"schema":"wengua_kaiwu_separate_verse_commentary_v1","source_sha256":SOURCE_SHA,
    "chapter_key":CHAPTER,"pairs":ps})
 write("concept_tracks.json",{"chapter_key":CHAPTER,"source_sha256":SOURCE_SHA,"entries":items})
 write("fate_motifs.json",{"chapter_key":CHAPTER,"source_sha256":SOURCE_SHA,
    "motifs":motifs,"not_predictive_rules_approved":True})
 write("cross_book_links.json",{"chapter_key":CHAPTER,
    "links":[{"source_line":19,"target_book":"shenqi","page":None,
      "relation":"general_prior_book_reference_not_repeated_case",
      "verified_independent_case":False}]})
 write("source_audit.json",{"source_sha256":SOURCE_SHA,
    "verses":12,"distinct_explanations":12,"new_predicted_case_families":0,
    "no_question_cast_charts":True,"author_casting_chaibu_not_overwriting_zhirun":True,
    "face_body_kinship_and_wealth_symbols_not_scientific_medical_or_legal_facts":True,
    "same_stem_pair_guest_host_order_preserved":True,
    "older_book_original_source_unchanged":True,
    "candidate_training_permission":False})
 return manifest
def main():
 p=argparse.ArgumentParser()
 for key in ("base","source","output","index-dir"):p.add_argument("--"+key,required=True)
 x=p.parse_args()
 print(json.dumps(build(x.base,x.source,x.output,x.index_dir),ensure_ascii=False,indent=2))
if __name__=="__main__":main()
