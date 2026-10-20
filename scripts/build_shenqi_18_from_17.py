"""Full 18-section immutable SQLite snapshot from the authoritative 17-section GitHub archive.
Traditional weather divination source study is not scientific meteorology or a replacement for forecasts.
"""
from __future__ import annotations
import argparse, hashlib, json, re, sqlite3
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SOURCE_SHA='6093f9a89bd2eb889c392242892528a9022c6d9565f74be8912e2a8724663697'
BASE_SHA='d29cfc5cd0779cf0a334b168a48c07f7145d51f0fe1424c5c0954b76e1133867'
SECTION='weather_prediction_ch14'
CHAPTER='shenqi/weather_prediction_ch14/v1'
PALACES=('巽四宫','离九宫','坤二宫','震三宫','中五宫','兑七宫','艮八宫','坎一宫','乾六宫')
NUM=(4,9,2,3,5,7,8,1,6)
# first, end, chart start, numbered source lines, initial source, judgment, book feedback, topic
CASES=[
 (17,43,24,[40,41],[19,20],42,42,'1993秦王湖景区开业典礼阴天无雨'),
 (44,72,51,[67,68,69],[46,47],70,71,'1994提前八天预测5月11日天气'),
 (73,101,79,[95,96,97,98],[75],99,100,'1996学校揭牌仪式前后降雨'),
 (102,129,109,[125,126],[104,105],127,128,'1998邢台移动网络露天开通仪式天气'),
 (130,156,137,[153,154],[132,133],155,156,'1998保定移动网络开通无雨及小风'),
]
STEP_TOPICS=[
 ['震3天柱、离9天蓬均无壬癸，组合推不会下雨','坎1天英火入水乡乘玄武休门，与未月辰日旺相反证，推阴云'],
 ['天英值符兑7空亡、巳月火旺酉日填实，综合晴天','景门值使坎1得乙奇、柱星太阴与时令反证推晚间云彩','壬离9水入火乡、癸坤2入墓与辅星入墓，排雨风'],
 ['甲辰壬艮8与开门生水、蓬兑7玄武、辰库冲刑推甲辰时雨','乙巳时乙泄壬、巳火制水的时辰转换','震3天英旺相与休门螣蛇冲突，取雨停之象','天柱离9不落137雨势被制，综合揭牌时雨停'],
 ['蓬艮8不带壬癸为少雨，柱乾6带癸及太阴克制交叉推小雨','辅离9旺、伤门玄武的风象合取三四级风'],
 ['柱震3无壬癸、蓬离9带壬但景门火，英坎1水乡取阴云少雨','癸巳时癸坤2入墓受土克排雨，白虎风象作反证'],
]
assert sum(len(x) for x in STEP_TOPICS)==13
# Conditional research methods, not scientifically validated forecasting.
METHODS=[
 (7,'primary_nine_stars','天气以九星为主，兼看天干、门、神及其落宫'),
 (8,'ying_sun','天英为火神主晴'),(8,'fu_wind','天辅为风伯主风'),
 (8,'zhu_rain','天柱为雨师主雨'),(8,'peng_rain','天蓬为水神主雨'),
 (8,'chong_thunder','天冲为雷公主雷'),(8,'winter_xin_zhu_snow','冬季天心天柱主雪'),
 (8,'jing_sun','景门晴'),(8,'kai_shang_thunder','开伤二门雷'),
 (8,'xiu_cloud_rain','休门云雨'),(8,'sheng_wind','生门风'),
 (8,'du_lightning','杜门电'),(8,'jingrainbow','惊门虹霓'),
 (8,'jia_yi_wind','甲乙风'),(8,'bing_ding_fire','丙丁火晴'),
 (8,'wu_ji_cloud','戊己阴云'),(8,'geng_xin_snow','庚辛冰雪'),
 (8,'ren_gui_rain_size','壬癸雨水，壬大雨癸小雨'),
 (8,'jiutian_sunny_jiudi_cloud','九天晴九地阴'),
 (8,'liuhe_sunny_wind_baihu_wind','六合风和日丽白虎风'),
 (8,'xuanwu_rain_taiyin_cloud','玄武雨、太阴阴云霜雪'),
 (8,'tengshe_lightning_rainbow','螣蛇闪电虹霓'),
 (9,'ying_strength_location','天英旺相落三四宫或克日时干主晴'),
 (9,'fu_strength_position','天辅旺相落离9或克宫、日时干主风晴'),
 (10,'peng_zhu_water_137','蓬柱乘壬癸到一三七宫主雨'),
 (10,'wind_rain_lightning_combo','英辅天盘干克地盘干兼蓬柱雨象，风雨雷电候选'),
 (11,'distance_to_zhifu_timing','与值符近雨速远雨迟'),
 (11,'rain_cloud_kun2','蓬柱携壬癸游坤2密云不雨'),
 (11,'no_water_stem_no_rain','蓬柱无壬癸即使在一三七宫也不下雨'),
 (12,'winter_dry_metal_snow','冬天心柱带壬癸在乾兑宫主雪'),
 (13,'river_peng_xiu','河水涨落以蓬星休门为用神'),
 (13,'flood_strong_three_wonders','水旺得三奇虽涨不泛滥'),
 (13,'flood_geng_pattern','旺水得庚格原书指壅塞泛滥'),
 (13,'flood_jiachen_ren_tengshe','甲辰壬螣蛇合庚格主洪水风险'),
 (13,'flood_earth_palaces','蓬或休落二五八宫土克水洪水可消'),
 (13,'flood_no_geng_ren','无庚格或甲辰壬则虽涨无决堤'),
]
assert len(METHODS)==36

def canon(o):return json.dumps(o,ensure_ascii=False,sort_keys=True,separators=(',',':'))
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def seg(lines,a,b=None):
 b=a if b is None else b
 if not 1<=a<=b<=len(lines):raise ValueError(('Invalid source span',a,b))
 return '\n'.join(lines[a-1:b])
def parse_chart(lines,start):
 if not lines[start-1].startswith('┌'):raise ValueError(('No printed chart',start))
 entries=[]
 for row in range(3):
  y=start+1+row*4
  levels=[]
  for d in range(3):
   p=[z.strip() for z in lines[y+d-1].split('│')[1:-1]]
   if len(p)!=3:raise ValueError(('Malformed source chart',start,row,d))
   levels.append(p)
  for col in range(3):
   pos=row*3+col;pal=NUM[pos]
   name,door,star=(levels[k][col] for k in range(3))
   if not name.startswith(PALACES[pos]):raise ValueError(('Wrong source palace',start,name))
   if pal==5:
    if '八神：' in name or not door.startswith('原盘单字：') or star:
     raise ValueError(('Center palace must preserve literal only',start,door,star))
    deity='';door=door.split('：',1)[1].strip()
    if not re.fullmatch(r'[乙丙丁戊己庚辛壬癸]',door):raise ValueError('Missing genuine center stem')
   else:
    if '八神：' not in name or not door.startswith('门位：') or not star.startswith('星位：'):
     raise ValueError(('Unfaithful outer source palace',start,name,door,star))
    deity=name.split('八神：',1)[1].strip()
    door=door.split('：',1)[1].strip();star=star.split('：',1)[1].strip()
   entries.append((pal,y+col,name,deity,door,star))
 if sorted(z[0] for z in entries)!=list(range(1,10)):raise ValueError('Original board lacks distinct nine palaces')
 return entries

def lex(text):
 ids=[]
 for k in '开休生伤杜景死惊':
  if k+'门' in text:ids.append('door:'+k)
 for k in '蓬任冲辅英芮柱心禽':
  if '天'+k in text:ids.append('star:'+k)
 for k in ('玄武','白虎','九天','九地','六合','太阴','螣蛇','值符'):
  if k in text:ids.append('deity:'+k)
 for k in '乾坤巽离震兑艮坎':
  if k+'宫' in text:ids.append('trigram:'+k)
 return sorted(set(ids))

def source_evidence(lines,case_no,step_number,source_line,topic):
 text=seg(lines,source_line)
 clauses=[z.strip() for z in re.split('[，；。]',text) if z.strip()]
 return {'step_number':step_number,'source_line':source_line,'topic':topic,
  'author_claimed_observation_fragments':[z for z in clauses if any(t in z for t in ('星','门','宫','时','月','旺','墓','壬','癸','晴','雨','风','生','克'))],
  'author_expressed_counterevidence':[z for z in clauses if any(t in z for t in ('虽然','但是','但','即使','却','不带','不落','受制'))],
  'existing_symbol_lexical_concept_candidates':lex(text),
  'phase':'author_first_analysis', 'author_original_is_private_sqlite':True,
  'weather_scientific_validation':False,'cross_chapter_semantic_rules_human_verified':False,
  'positive_training_eligible':False,'review_status':'source_anchor_draft_requires_human_per_step_verification'}

def cases_index(lines):
 out=[]
 for i,(start,end,border,steps,known,pred,feedback,title) in enumerate(CASES,1):
  if not lines[start-1].startswith('实例'):raise ValueError(('No case at',start))
  cells=parse_chart(lines,border)
  for s in steps:
   if not re.match(r'^\(\d+\)',lines[s-1]):raise ValueError(('No original numbered reasoning',i,s))
  cid=f'shenqi.weather.case{i:02d}'
  item={'case_number':i,'case_id':cid,'event_family_id':cid,'case_title':title,
   'source_whole_story_lines':[start,end],'printed_original_cast_line':border,'actual_printed_nine_palaces':9,
   'initial_question_lines':known,'source_author_numbered_analysis_lines':steps,
   'source_judgment_line':pred,'source_feedback_line':feedback,
   'author_step_index':[source_evidence(lines,i,j,s,STEP_TOPICS[i-1][j-1]) for j,s in enumerate(steps,1)],
   'original_book_outcome':'author_book_success_default','independent_meteorological_truth_verified':False,
   'printed_chart_independently_recast':False,'positive_training_eligible':False,'whole_story_unsplit':True}
  if i==1:item['embedded_verdict_and_outcome_same_line']={'line':42,'separator':'结果，','split_required':True}
  if i==2:item['other_divination_not_qimen']={'source_line':46,'hexagram_methods':3,'extra_qimen_charts_printed':0,
     'hexagram_results_do_not_belong_in_first_blind_input':True}
  if i==3:item['same_event_subhour_phase']={'source_line':95,'甲辰时':'雨象','乙巳时':'雨停转弱、揭牌窗口',
    'late_10am_book_feedback':100,'additional_printed_chart':False}
  if i==4:item['reused_cast_for_different_question']={'source_line':105,'original_context':'世界杯巴西荷兰球赛',
     'separate_weather_question':True,'do_not_duplicate_sports_event_family':True}
  if i==5:item['cast_strategy']={'source_line':133,'type':'planned_event_datetime','question_asked_previous_day':True}
  out.append(item)
 return out

def known_text(lines,i,known):
 if i==2:
  # This paragraph includes the outcomes of the author's THREE non-Qimen hexagrams.
  return seg(lines,46).split('三个卦都表明',1)[0].rstrip('，。 ')+'\n'+seg(lines,47)
 return '\n'.join(seg(lines,n) for n in known)

def expected_outcome(lines,i,pred):
 if i==1:
  t=seg(lines,42)
  if '结果，' not in t:raise ValueError('Case 1 prediction and outcome separator lost')
  return t.split('结果，',1)[0].strip()
 return seg(lines,pred)

def feedback_text(lines,i,fb):
 if i==1:return '结果，'+seg(lines,42).split('结果，',1)[1]
 return seg(lines,fb)

def phase(db,cid,lines,a,b,kind,first_visible=False,original_override=None):
 text=original_override if original_override is not None else seg(lines,a,b)
 db.execute('''INSERT INTO historical_case_phase_events
 (case_id,source_start_line,source_end_line,phase,original_excerpt,metadata_json,visible_to_initial_blind_test)
 VALUES (?,?,?,?,?,?,?)''',(cid,a,b,kind,text,canon({'source_chapter':CHAPTER,'post_feedback_not_available_to_initial':not first_visible}),int(first_visible)))
 if kind in ('new_disclosure','book_feedback','editor_posthoc_correction'):
  db.execute('''INSERT OR IGNORE INTO historical_case_disclosures(case_id,source_line,phase,fact_type,original_statement)
   VALUES (?,?,'later_than_initial',?,?)''',(cid,a,kind,text))

def import_one(db,lines,section_id,case):
 i=case['case_number'];cid=case['case_id'];start,end,border,steps,known,pred,feedback,title=CASES[i-1]
 prior=known_text(lines,i,known)
 if i==2 and '三个卦都表明' in prior:raise ValueError('Already-known hexagram result contaminated initial facts')
 original='\n\n'.join(seg(lines,s) for s in steps)
 response=expected_outcome(lines,i,pred);back=feedback_text(lines,i,feedback)
 db.execute('''INSERT INTO cases(case_id,section_id,event_family_id,domain_id,known_before,author_yongshen_steps,author_judgment,later_feedback,reviewed)
 VALUES (?,?,?,?,?,?,?,?,0)''',(cid,section_id,cid,'weather_historical_source',prior,original,response,back))
 db.execute('''INSERT INTO historical_case_protocol(case_id,completeness,published_chart_verification,feedback_independently_verified,
 eligible_blind_test,case_source_sha256,metadata_json)
 VALUES (?,'whole_source_story_and_one_printed_chart','book_literal_not_independently_recast',0,0,?,?)''',
 (cid,SOURCE_SHA,canon(case)))
 db.execute('''INSERT INTO historical_weather_cast_context
 (case_id,cast_strategy,question_date,forecast_target_date,printed_cast_line,alternative_techniques_not_printed_json,
 metadata_json,scientific_external_verification)
 VALUES (?,?,?,?,?,?,?,0)''',(
 cid,'planned_event_time' if i in (1,3,5) else 'question_time_reused_sports_cast' if i==4 else 'question_time',
 ['1993-07-26','1994-05-03','1996-06-24','1998-07-07','1998-07-27'][i-1],
 ['1993-08-03','1994-05-11','1996-06-24','1998-07-08','1998-07-28'][i-1],border,
 canon({'non_qimen_hexagrams':3,'no_printed_qimen_charts':True}) if i==2 else '[]',
 canon({'source_line_metadata':known,'source_source_sha':SOURCE_SHA,
 'event_questions_independent_of_sports_case':i==4,
 'case3_hourly_transition':i==3,'first_judgment_and_result_embedded':i==1})))
 for pal,anchor,label,deity,door,star in parse_chart(lines,border):
  db.execute('''INSERT INTO historical_chart_cells
  (case_id,palace,source_line,palace_label_raw,deity_raw,door_position_raw,star_position_raw,source_status)
  VALUES (?,?,?,?,?,?,?,'literal_weather_source_not_independently_recast')''',
  (cid,pal,anchor,label,deity,door,star))
  is5=pal==5
  db.execute('''INSERT INTO historical_palace_standardization
   (case_id,cast_key,palace,center_stem,source_of_center_stem,standard_deity,standard_door,standard_star,
    normalized_status,original_raw_integrity_checked,method_reference,derived_host_palace,derived_host_source)
   VALUES (?,?,?,?,?,?,?,?,?,1,?,?,?)''',
   (cid,'primary',pal,door if is5 else None,'original_center_literal' if is5 else 'not_center',
    None if is5 else deity,None if is5 else door,None if is5 else star,
    'center_literal_with_no_unprinted_deity_door_star' if is5 else 'peripheral_literal_verified',
    'weather_original_txt+shijia_qiju',2 if is5 else None,
    'shijia_qiju:五宫寄坤二宫' if is5 else None))
 for entry in case['author_step_index']:
  n=entry['source_line'];k=entry['step_number'];original=seg(lines,n)
  db.execute('''INSERT INTO historical_case_reasoning
  (case_id,step_number,source_line,author_analysis_original,short_method_topic,metadata_json)
  VALUES (?,?,?,?,?,?)''',(cid,k,n,original,entry['topic'],canon(entry)))
  db.execute('''INSERT INTO historical_case_reasoning_trace
  (case_id,step_number,source_line,evidence_json,review_status,positive_training_eligible)
  VALUES (?,?,?,?,'source_anchor_only_needs_full_manual_evidence_chain',0)''',(cid,k,n,canon(entry)))
  db.execute('''INSERT INTO semantic_assertions
  (chapter_key,concept_id,kind,relation,source_start_line,source_end_line,metadata_json,original_excerpt,review_status)
  VALUES (?,?,?,?,?,?,?,?,?)''',(CHAPTER,f'weather:case{i:02d}:step{k:02d}',
   'weather_historical_worked_example','source_step_not_approved',n,n,canon(entry),original,'draft'))
 # Separate first known facts from author decision and later feedback.
 if i==2:
  phase(db,cid,lines,46,47,'initial_question',True,prior)
  # Source actually recounts three other divinations with their RESULTS already known to the author.
  phase(db,cid,lines,46,46,'cast_metadata',False,seg(lines,46))
 else:
  phase(db,cid,lines,known[0],known[-1],'initial_question',True)
 if i==1:
  phase(db,cid,lines,42,42,'initial_judgment',False,response)
  phase(db,cid,lines,42,42,'book_feedback',False,back)
 else:
  phase(db,cid,lines,pred,pred,'initial_judgment',False)
  phase(db,cid,lines,feedback,feedback,'book_feedback',False)
 if i==3:
  # The two subhours are in the same source chart, not two fabricated boards.
  phase(db,cid,lines,95,96,'cast_metadata',False)
 if i==4:
  # Same chart initially raised by football question, repurposed as a new weather question.
  phase(db,cid,lines,105,106,'cast_metadata',False)
 db.execute('''INSERT INTO historical_case_book_verdicts
   (event_family_id,primary_case_id,verdict,explicit_source_correction,source_correction_lines_json,
    feedback_source_lines_json,independent_external_verification,app_output_protocol,evidence_review_status,note)
   VALUES (?,?,'author_book_success_default',0,'[]',?,'not_verified','single_answer_for_one_cast','book_source_only',?)''',
   (cid,cid,canon([feedback]),'Only source retrospective claimed weather match; no external instrumental weather validation.'))
 db.execute('''INSERT INTO historical_case_review_audit
  (case_id,original_steps,mechanical_step_trace,human_complete_step_chains,review_status,warning)
  VALUES (?,?,?,0,'source_anchor_only_needs_full_manual_evidence_chain',?)''',
  (cid,len(steps),len(steps),'Historical book weather claim not independent meteorological validation'))

def compare_legacy(old,updated):
 """Every row from every old table must remain identical in its original columns."""
 previous_tables=[r[0] for r in old.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")]
 for table in previous_tables:
  cols=[r[1] for r in old.execute('PRAGMA table_info("'+table+'")')]
  if not cols:raise ValueError('Baseline table has no columns')
  expression=','.join('"'+x+'"' for x in cols)
  oldrows=list(old.execute('SELECT '+expression+' FROM "'+table+'"'))
  newrows=set(updated.execute('SELECT '+expression+' FROM "'+table+'"'))
  if not all(row in newrows for row in oldrows):raise ValueError('Legacy table changed: '+table)

def build(base,source,output,index_dir,migration):
 if output.exists():raise ValueError('Refusing to overwrite existing versioned database')
 if digest(base)!=BASE_SHA:raise ValueError('Wrong 17-chapter complete SQLite baseline SHA')
 raw=source.read_bytes()
 if hashlib.sha256(raw).hexdigest()!=SOURCE_SHA:raise ValueError('Weather source is not approved original SHA')
 lines=raw.decode('utf8').splitlines()
 if len(lines)!=156 or lines[0]!='天时气象预测' or lines[14]!='第二节 实例解析(5例)':
  raise ValueError('Unexpected chapter source boundaries')
 cases=cases_index(lines)
 if len(cases)!=5 or sum(len(x['author_step_index']) for x in cases)!=13:raise ValueError('Missing case source steps')
 output.parent.mkdir(parents=True,exist_ok=True)
 with sqlite3.connect('file:'+str(base)+'?mode=ro',uri=True) as previous, sqlite3.connect(output) as db:
  previous.backup(db)
  db.executescript(migration.read_text(encoding='utf8'))
  db.execute('PRAGMA foreign_keys=ON')
  with db:
   if db.execute('SELECT 1 FROM sections WHERE section_key=?',(SECTION,)).fetchone():raise ValueError('Source was imported already')
   db.execute('''INSERT INTO sections(book_id,section_key,title,original_text,sha256,content_version,reviewed)
   VALUES ('shenqi',?,?,?,?,1,0)''',(SECTION,'天时气象预测',raw.decode('utf8'),SOURCE_SHA))
   sid=db.execute('SELECT last_insert_rowid()').fetchone()[0]
   db.execute('''INSERT INTO chapter_knowledge(chapter_key,book_id,title,source_sha256,source_length_bytes,knowledge_version,review_status)
   VALUES (?,'shenqi','天时气象预测',?,?,'1','draft')''',(CHAPTER,SOURCE_SHA,len(raw)))
   for n,key,desc in METHODS:
    meta={'source_line':n,'method':'weather:'+key,'summary':desc,'source_claim_only':True,'review_status':'draft'}
    db.execute('''INSERT INTO semantic_assertions
     (chapter_key,concept_id,kind,relation,source_start_line,source_end_line,metadata_json,original_excerpt,review_status)
     VALUES (?,?,?,?,?,?,?,?,?)''',
     (CHAPTER,'weather:general:'+key,'weather_conditions_from_book','conditional_source_study',n,n,canon(meta),seg(lines,n),'draft'))
   for case in cases:import_one(db,lines,sid,case)
   db.execute('''INSERT INTO chapter_archival_versions
     (archive_label,baseline_sha256,new_db_sha256,contains_complete_private_copyright_source,snapshot_type,created_utc,repo_public_archive_policy)
     VALUES (?, ?,NULL,1,'incremental_source_preserving','2026-10-20','user_explicitly_authorized_public_full_archive')''',
     ('shenqi_18_sections_91_whole_events',BASE_SHA))
  if db.execute('PRAGMA integrity_check').fetchone()[0]!='ok' or db.execute('PRAGMA foreign_key_check').fetchall():
   raise ValueError('Broken SQLite integrity or foreign keys')
  compare_legacy(previous,db)
  expected={'sections':18,'cases':91,'historical_chart_cells':819,
     'historical_case_additional_cast_cells':63,'historical_case_additional_casts':7,
     'historical_case_reasoning':411,'semantic_assertions':1044+len(METHODS)+13,
     'historical_case_reasoning_trace':411,'historical_palace_standardization':882,
     'historical_weather_cast_context':5}
  counts={k:db.execute('SELECT count(*) FROM "'+k+'"').fetchone()[0] for k in expected}
  for table,total in expected.items():
   if counts[table]!=total:raise ValueError(('Expected table count',table,total,counts[table]))
  n=db.execute('''SELECT count(*) FROM historical_palace_standardization
    WHERE palace=5 AND derived_host_palace=2 AND standard_deity IS NULL AND standard_door IS NULL AND standard_star IS NULL''').fetchone()[0]
  if n!=98:raise ValueError(('Source centre normalization failed',n))
  if db.execute("SELECT count(*) FROM historical_case_book_verdicts WHERE verdict='author_book_error_explicit'").fetchone()[0]!=5:
   raise ValueError('Historical five explicit error labels changed')
  if db.execute('SELECT count(*) FROM historical_case_reasoning_trace WHERE positive_training_eligible=1').fetchone()[0]:
   raise ValueError('Unapproved historical source reasoning exposed to positive training')
  db.execute('PRAGMA page_size=2048');db.execute('VACUUM');db.commit()
  if db.execute('PRAGMA integrity_check').fetchone()[0]!='ok' or db.execute('PRAGMA foreign_key_check').fetchall():
   raise ValueError('Final SQLite checks failed')
 index_dir.mkdir(parents=True,exist_ok=True)
 archive_hash=digest(output)
 manifest={'schema':'wengua_weather_source_manifest_v1','source_title':'天时气象预测',
  'source_sha256':SOURCE_SHA,'source_bytes':len(raw),'source_lines':len(lines),'chapter_key':CHAPTER,
  'whole_events':5,'actual_printed_charts':5,'original_nine_palace_cells':45,'author_numbered_steps':13,
  'general_condition_candidates':len(METHODS),'new_semantic_assertions':len(METHODS)+13,
  'retrospective_book_only':True,'external_instrumental_weather_verification':False,
  'baseline_sha256':BASE_SHA,'archive_sha256':archive_hash,'counts':counts,
  'historic_centres_normalized_without_invented_stars_doors_gods':n,
  'human_expert_author_reasoning_approved':0,'all_prior_chapter_rows_preserved':True}
 evidence={'schema':'wengua_weather_author_source_step_drafts_v1','source_sha256':SOURCE_SHA,
  'whole_events':5,'author_source_steps':13,'human_verified_causal_chains':0,
  'cases':[{'case_id':x['case_id'],'steps':x['author_step_index']} for x in cases]}
 methods={'schema':'wengua_weather_domain_workflow_v1','source_sha256':SOURCE_SHA,
  'methods':[{'concept_id':'weather:general:'+k,'source_line':n,'conditional_summary':v,'review_status':'draft'} for n,k,v in METHODS],
  'workflow':['确定预测所用问时还是指定事件时，不偷用事后气象结果',
   '九星为主并结合门、神、干和真实宫位，区分晴、阴、风、大小雨、雪、河水涨落',
   '以天柱天蓬是否带壬癸、所在宫及五行月令旺衰核验雨象',
   '逐宫比较天英景门火晴、天辅生门风及螣蛇/太阴/玄武等反证',
   '按问事小时与目标小时分析当时雨势变化而不是拆成不同历史成功事件',
   '严格隔离书内后验结果，不伪造六爻未印盘，不与同时间体育问事合并',
   '原九宫中五仅照录单干，寄坤独立为派生标注',
   '初断与结果、支持反证和限制可追溯，文献学习并非科学气象预报']}
 audit={'schema':'wengua_weather_source_audit_v1','source_sha256':SOURCE_SHA,
   'case1':{'prediction_and_result_same_source_line':42,'must_split_by':'结果，'},
   'case2':{'source_line':46,'hexagram_methods_not_qimen':3,'original_extra_qimen_charts':0,
      'non_qimen_results_are_author_prior_knowledge_not_initial_blind_input':True},
   'case3':{'source_lines':[95,96,97,98,99,100],'chen_hour_rain_vs_si_hour_pause':True,
      'ten_am_rain_resume_is_book_feedback':True,'multiple_printed_boards':False},
   'case4':{'source_lines':[104,105],'same_hour_came_from_football_chart':True,
      'different_question_and_event_family':True,'do_not_double_count_weather_board':False},
   'case5':{'source_lines':[132,133,134],'forecast_by_planned_event_hour':True},
   'source_weather_successes_scientifically_verified':False}
 for filename,data in [('chapter_manifest.json',manifest),('case_index.json',{'schema':'wengua_weather_whole_events_v1','source_sha256':SOURCE_SHA,'cases':cases}),('author_reasoning_evidence_index.json',evidence),('method_index.json',methods),('source_audit.json',audit)]:
  (index_dir/filename).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 print(json.dumps({'new_archive':str(output),'sha256':archive_hash,'counts':counts,'original_source_sha256':SOURCE_SHA,'human_approved':0,'baseline_immutable':True},ensure_ascii=False,indent=2))
 return 0

def main(argv=None):
 p=argparse.ArgumentParser()
 p.add_argument('--base',type=Path,required=True)
 p.add_argument('--source',type=Path,required=True)
 p.add_argument('--output',type=Path,required=True)
 p.add_argument('--index-dir',type=Path,required=True)
 p.add_argument('--migration',type=Path,default=ROOT/'schema/migrations/013_weather_case_time.sql')
 args=p.parse_args(argv)
 return build(args.base,args.source,args.output,args.index_dir,args.migration)
if __name__=='__main__':raise SystemExit(main())
