"""Safely derive the seventeenth COMPLETE SQLite archive, with every previous byte of source content intact.

Military divination is the historical AUTHOR'S source interpretation, not reliable
conflict intelligence, predictive capability, or operational military advice.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import lzma
import re
import sqlite3
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SOURCE_SHA='d8b369785de0110cc20376191332eef31b04e749d8ed764d7a1a155ae6c19c05'
BASE_SHA='a3573b3b147c24b2eb149fb43f6c6582d7a10a722c25f6c863571f4d4a29efb9'
SECTION='military_events_prediction_ch13'
CHAPTER='shenqi/military_events_prediction_ch13/v1'
PALACES=('巽四宫','离九宫','坤二宫','震三宫','中五宫','兑七宫','艮八宫','坎一宫','乾六宫')
NUM=(4,9,2,3,5,7,8,1,6)
CASE_SPECS=[
  {'number':1,'start':29,'end':71,'title':'1937年德方声明与二战进程事后对照研究',
   'source_casts':[{'key':'primary','border':38,'date':'1937-04-20','hour':'己酉','status':'retrospective_from_known_WWII_outcome',
      'question_lines':[31,33,35],'analysis_lines':[54,56,58,60,62,64,66,68,70]}],
   'feedback_lines':[31],'independent_prospective_prediction':False},
  {'number':2,'start':72,'end':183,'title':'1998年美国伊拉克危机三次实际起盘',
   'source_casts':[
     {'key':'primary','border':89,'date':'1998-01-29','hour':'己亥','status':'first_prospective_source_study',
       'question_lines':[74,78,80,82,84,86], 'analysis_lines':[105,107,109,113,115,117]},
     {'key':'cast02','border':126,'date':'1998-02-07','hour':'癸未','status':'same_crisis_second_prospective_question_after_business',
       'question_lines':[119,123], 'analysis_lines':[142,144,146,148,150]},
     {'key':'cast03','border':161,'date':'1998-02-22','hour':'丙戌','status':'same_crisis_third_prospective_question_after_news_update',
       'question_lines':[152,154,156,158], 'analysis_lines':[177,179]}
   ],
   'feedback_lines':[183], 'independent_prospective_prediction':True}
]
# Article level each anchored to its actual original source. Conditional source notes remain draft.
METHODS=[
 (11,'zhifu_is_defensive_main','值符落宫作主方、守方，六庚落宫作客方、攻方'),
 (11,'symbol_jia_geng_opposition','六甲遁六仪；庚克甲是书内选用神依据'),
 (13,'main_controls_geng','值符宫克庚宫原书说主胜'),
 (13,'geng_controls_main','庚宫克值符宫原书说客胜'),
 (13,'month_strength','值符和六庚各宫旺相休囚作为条件'),
 (13,'jing_jing_gates','景门惊门与主客宫相生及战阵人事关系'),
 (13,'both_auspicious_with_equal_power','两方旺相与门条件相等可能不战而退'),
 (13,'geng_as_zhifu_same_palace','六庚为值符时主客同宫，不宜机械决定胜负'),
 (13,'opposing_palaces_generate','主客相生可候选和解'),
 (13,'day_over_geng','日干加庚在书内倾向主胜'),
 (13,'geng_over_day','庚加日干在书内倾向客胜'),
 (13,'day_hour_roles','日干与时干可作额外两方取用，须交代角色'),
 (15,'military_intelligence_jing','景门作军事信息用神，需结合旺相与三奇'),
 (15,'intel_auspicious_true','景门旺相得奇书内称实信'),
 (15,'intel_no_qi_rumor','景门无奇原书称诈信'),
 (15,'intel_void_weak','景门空亡休囚原书称谣言'),
 (17,'deployment_zhifu_open_geng','值符为上级、开门为官长、庚为对方'),
 (17,'deployment_open_weak','开门受克加休囚墓，原书推部署失当'),
 (17,'deployment_open_supported','值符生开门且克庚，原书推部署得当'),
 (19,'enemy_in_out_palaces','庚在内四宫/外四宫作来去取象，须区分未入境与已入境'),
 (19,'tai_bai_ying','太白入荧或荧入太白两格分别有来去解释'),
 (19,'geng_with_palace_element','庚宫与落宫克制关系判断进退的传统说法'),
 (19,'geng_with_xuanwu_star','庚受玄武天蓬白虎等条件，原书说战斗趋势'),
 (19,'geng_with_jiutian_jiudi','九天与九地给攻方气势象义候选'),
 (19,'geng_below_stem_for_time','庚下之干作为来去应期候选'),
 (21,'attack_geng_tianqin','攻城以庚攻、天禽守，不与一般战争混用'),
 (21,'attack_open_center','庚旺相乘星兼开门入中宫传统城攻条件'),
 (21,'defender_tianqin_strength','地盘天禽吉门旺相作为守将状况候选'),
 (23,'defense_tianqin','守城以天禽守、天蓬和六庚攻'),
 (23,'defense_four_gates_bing','守方休生杜景旺相及丙的守城组合'),
 (23,'defense_invading_center','天蓬庚加中宫与开门组合的失守条件'),
 (25,'commander_birthday_stem','选将需要比较众将年命干与开门冲关系，不能不带现实约束'),
]
STEP_TOPICS={
  1:['守方值符艮土与攻方庚坎水月令生克的事后对照',
     '九星反吟作为战事结局的事后象义解释',
     '日干丁取希特勒、乾宫惊门九地解释当时声明及长久',
     '辰月乾金时令与马星回述初期强弱',
     '逐年天干戊己庚辛壬癸甲乙事后归因的推演',
     '沿八门顺序回溯战事兴衰的作者解释',
     '地支宫位映射1937至1945年的事后时间线',
     '值使死门兑七宫结合七、九年两种应期候选',
     '乾金与震巽木对立及甲乙木年的事后结论'],
  2:['主客兵阵以值符守庚攻而非日常民事取用',
     '首盘值符兑7为伊拉克并结合辛己死门状态',
     '首盘庚巽4伤门的好战征象兼玄武空亡反证，含续段111',
     '首盘兑金对巽木、六合调解、月癸朋友宫综合阻战',
     '先动为客、后动为主与天地盘干角色条件',
     '首盘天日丙地癸与天时己地壬，比较两种相反生克及月令',
     '第二盘值符坎1伊拉克休门伏吟背景',
     '第二盘庚乾6美国九天与己庚官符格',
     '第二盘乾金生坎水且八门伏吟，作为不战证据',
     '第二盘六合巽4联合国调解及寅月克制限制',
     '第二盘天地盘日乙壬和时癸辛相生的另组主客证据',
     '第三盘值符庚同巽4、六合兑7和景门文书综合推谈判达成',
     '第三盘庚下丙与丙下癸主克客的补充条件']
}
assert len(STEP_TOPICS[1])==9 and len(STEP_TOPICS[2])==13

# Continued paragraphs are attached to their parent numbered analysis, never dropped or counted twice.
STEP_SPANS={109:(109,111)}

def canon(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def segment(lines,a,b=None):
 b=a if b is None else b
 if not (1<=a<=b<=len(lines)):raise ValueError('Bad source line range')
 return '\n'.join(lines[a-1:b])
def lex(s):
 ids=[]
 for n in '开休生伤杜景死惊':
  if n+'门' in s:ids.append('door:'+n)
 for n in '蓬任冲辅英芮柱心禽':
  if '天'+n in s:ids.append('star:'+n)
 for n in ('玄武','白虎','九天','九地','六合','太阴','螣蛇','值符'):
  if n in s:ids.append('deity:'+n)
 for n in '乾坤震巽坎离艮兑':
  if n+'宫' in s:ids.append('trigram:'+n)
 return sorted(set(ids))
def parse_chart(lines,start):
 if not lines[start-1].startswith('┌'):raise ValueError(('Missing chart',start))
 out=[]
 for row in range(3):
  first=start+1+row*4
  triple=[]
  for delta in range(3):
   parts=[t.strip() for t in lines[first+delta-1].split('│')[1:-1]]
   if len(parts)!=3:raise ValueError(('Chart incomplete',start,row,delta))
   triple.append(parts)
  for col in range(3):
   idx=row*3+col;number=NUM[idx]
   name,door,star=(triple[k][col] for k in range(3))
   if not name.startswith(PALACES[idx]):raise ValueError(('Wrong palace',start,name))
   if number==5:
    if '八神：' in name or not door.startswith('中宫原字：') or star:raise ValueError('Source center differs')
    deity='';door=door.split('：',1)[1]
    if not re.fullmatch('[乙丙丁戊己庚辛壬癸]',door):raise ValueError('Unknown original center stem')
   else:
    if '八神：' not in name or not door.startswith('门位：') or not star.startswith('星位：'):
     raise ValueError(('Incomplete outer palace',start,name,door,star))
    deity=name.split('八神：',1)[1].strip();door=door.split('：',1)[1];star=star.split('：',1)[1]
   out.append((number,first+col,name,deity,door,star))
 if sorted(z[0] for z in out)!=list(range(1,10)):raise ValueError('Repeated palace')
 return out

def source_stage(case_number,cast,step_line):
 if case_number==1:return 'retrospective_on_known_result_no_blind_test'
 if cast['key']=='cast03':return 'third_cast_separate_known_news_update'
 if cast['key']=='cast02':return 'second_cast_after_new_question'
 return 'first_cast_source_study_claim_only'

def step_evidence(lines,number,cast,line,topic,step_no):
 first,last=STEP_SPANS.get(line,(line,line));t=segment(lines,first,last)
 pieces=[p.strip() for p in re.split('[，；。]',t) if p.strip()]
 support=[p for p in pieces if any(q in p for q in ('宫','门','星','干','值符','庚','冲','月令','伏吟','反吟','生','克','旺','囚'))]
 contrast=[p for p in pieces if any(q in p for q in ('但是','虽然','但','却','反','难以','不动','也不','似乎','然而'))]
 return {'step_number':step_no,'source_line':first,'source_end_line':last,'source_cast':cast['key'],'phase':source_stage(number,cast,line),
  'domain_method_topic':topic,'source_support_fragments_draft':support,'source_counterevidence_fragments_draft':contrast,
  'cross_chapter_lexical_candidates_unverified':lex(t),'source_original_kept_in_sqlite':True,
  'claimed_prediction_independently_historically_verified':False,'completed_human_expert_causal_review':False,
  'author_reconstruction_status':'source_anchored_draft_needs_full_evidence_chain_review','positive_training_eligible':False}

def prepare(lines):
 if len(lines)!=183 or lines[0]!='第十三章' or lines[2]!='军事事件预测' or lines[26]!='第二节 实例解析（2例）':
  raise ValueError('Unexpected book source structure')
 out=[]
 for spec in CASE_SPECS:
  if not lines[spec['start']-1].startswith('实例'):raise ValueError('Event source boundary missing')
  allsteps=[];casts=[]
  for cast in spec['source_casts']:
   parse_chart(lines,cast['border'])
   for line in cast['analysis_lines']:
    if not re.match(r'^\(\d+\)',lines[line-1]):raise ValueError(('Not numbered author analysis',line))
    allsteps.append((line,cast))
   casts.append(dict(cast,verified_nine_palaces=9,source_original_stem_center=True,
     independent_real_world_confirmation=False,approved_rule_status='draft'))
  if len(allsteps)!=len(STEP_TOPICS[spec['number']]):raise ValueError('Lost author step')
  steps=[step_evidence(lines,spec['number'],cast,line,STEP_TOPICS[spec['number']][k-1],k)
    for k,(line,cast) in enumerate(allsteps,1)]
  cid=f'shenqi.military.case{spec["number"]:02d}'
  item={'case_number':spec['number'],'case_id':cid,'event_family_id':cid,'topic':spec['title'],
    'whole_story_lines':[spec['start'],spec['end']],'actual_printed_casts':casts,
    'original_author_steps':steps,'original_author_analysis_lines':[x[0] for x in allsteps],
    'original_book_outcome':'author_book_success_default','historical_external_verification':'not_verified',
    'source_type':'retrospective_after_actual_war' if spec['number']==1 else 'three_separate_questions_about_one_crisis',
    'method_provenance_status':'source_only_draft_needs_human_validation','positive_training_eligible':False}
  if spec['number']==1:
   item['source_historical_inaccuracy_caution']={'line':31,'issue':'Book asserts 1937 Hitler announcement caused WWII; historical date/sequence requires independent verification. The text is not a validated causal chronology.',
      'book_analyzes_known_1945_outcome':True,'not_prospective_forecast':True}
  else:
   item['event_scope_caution']={'not_three_independent_cases':True,'cast_dates':['1998-01-29','1998-02-07','1998-02-22'],
    'no_new_world_history_assertions_from_book_conclusion':True,'source_later_feedback_line':183}
  out.append(item)
 return out

def assert_legacy_unchanged(base,out):
 # Each older row, in its original column order, must survive fully unchanged.
 tables=['books','sections','cases','historical_chart_cells','historical_case_additional_casts',
 'historical_case_additional_cast_cells','historical_case_reasoning','semantic_assertions','historical_case_book_verdicts',
 'historical_case_disclosures','historical_palace_standardization','historical_case_reasoning_trace',
 'historical_case_review_audit','historical_case_phase_events','historical_case_reasoning_corrections',
 'historical_outcome_reclassification_audit','historical_source_literal_anomalies','historical_sports_cast_qualification']
 for table in tables:
  cols=[a[1] for a in base.execute(f'PRAGMA table_info("{table}")')]
  if not cols:raise ValueError('Expected existing table absent: '+table)
  fmt=','.join('"'+c+'"' for c in cols)
  prev=list(base.execute(f'SELECT {fmt} FROM "{table}"'))
  revised=set(out.execute(f'SELECT {fmt} FROM "{table}"'))
  if not all(row in revised for row in prev):raise ValueError('Original data overwritten: '+table)

def phase_insert(db,cid,lines,a,b,phase,visible=False,cast_key='primary'):
 txt=segment(lines,a,b)
 db.execute('''INSERT INTO historical_case_phase_events
 (case_id,source_start_line,source_end_line,phase,original_excerpt,metadata_json,visible_to_initial_blind_test)
 VALUES (?,?,?,?,?,?,?)''',(cid,a,b,phase,txt,canon({'cast_key':cast_key,'first_event_family_continues':True,
  'was_source_known_at_first_question':bool(visible),'retrospective_explanation_not_blind_eligible':True}),int(visible)))
 if phase in ('new_disclosure','book_feedback','editor_posthoc_correction'):
  db.execute('''INSERT OR IGNORE INTO historical_case_disclosures(case_id,source_line,phase,fact_type,original_statement)
   VALUES (?,?,'later_than_initial',?,?)''',(cid,a,phase,txt))

def import_case(db,lines,sid,spec,case):
 num=spec['number'];cid=case['case_id'];casts=spec['source_casts']
 initial= ('Historical WWII events are ALREADY KNOWN before the retrospective reading; '
     + '\n'.join(segment(lines,z) for z in casts[0]['question_lines'])) if num==1 else \
    '\n'.join(segment(lines,z) for z in casts[0]['question_lines'])
 if num==2 and any(term in initial for term in ('1998年2月7','1998年2月22','后来，事实证明')):
  raise ValueError('First question contaminated by later casts')
 step_text='\n\n'.join(segment(lines,s['source_line'],s['source_end_line']) for s in case['original_author_steps'])
 pred=('Retrospective account only: no true prospective prediction of the 1937-1945 outcome.' if num==1
       else 'At each dated source cast the author concluded there would not be an immediate second Gulf War escalation; keep dates distinct.')
 feedback=segment(lines,spec['feedback_lines'][0])
 db.execute('''INSERT INTO cases(case_id,section_id,event_family_id,domain_id,known_before,author_yongshen_steps,author_judgment,later_feedback,reviewed)
  VALUES (?,?,?,?,?,?,?,?,0)''',(cid,sid,cid,'military_history_source',initial,step_text,pred,feedback))
 db.execute('''INSERT INTO historical_case_protocol(case_id,completeness,published_chart_verification,feedback_independently_verified,
  eligible_blind_test,case_source_sha256,metadata_json)
  VALUES (?,'all_original_source_casts','literal_book_txt_not_independently_recast',0,0,?,?)''',
  (cid,SOURCE_SHA,canon(case)))
 for c in casts:
  ckey=c['key'];cells=parse_chart(lines,c['border'])
  if ckey!='primary':
   db.execute('''INSERT INTO historical_case_additional_casts
     (case_id,cast_key,cast_datetime_description,calendar_date,hour_ganzhi,source_chart_start,notes)
     VALUES (?,?,?,?,?,?,?)''',(cid,ckey,c['date']+' '+c['hour'],c['date'],c['hour'],c['border'],
       'Same long-running source question; new independently PRINTED historical board, not a new event or post-outcome fabricated board'))
  db.execute('''INSERT INTO historical_military_cast_protocol(case_id,cast_key,cast_date,hour_ganzhi,source_chart_line,
    event_phase,source_initial_lines_json,original_analysis_lines_json,is_retrospective,is_prospective_blind_test_approved)
    VALUES (?,?,?,?,?,?,?,?,?,0)''',
    (cid,ckey,c['date'],c['hour'],c['border'],c['status'],canon(c['question_lines']),canon(c['analysis_lines']),int(num==1)))
  for palace,anchor,label,deity,door,star in cells:
   if ckey=='primary':
    db.execute('''INSERT INTO historical_chart_cells
      (case_id,palace,source_line,palace_label_raw,deity_raw,door_position_raw,star_position_raw,source_status)
      VALUES (?,?,?,?,?,?,?,'literal_original_military_book_unverified_recast')''',
      (cid,palace,anchor,label,deity,door,star))
   else:
    db.execute('''INSERT INTO historical_case_additional_cast_cells
      (case_id,cast_key,palace,source_line,palace_label_raw,deity_raw,door_position_raw,star_position_raw)
      VALUES (?,?,?,?,?,?,?,?)''',(cid,ckey,palace,anchor,label,deity,door,star))
   middle=palace==5
   db.execute('''INSERT INTO historical_palace_standardization(case_id,cast_key,palace,center_stem,source_of_center_stem,
    standard_deity,standard_door,standard_star,normalized_status,original_raw_integrity_checked,method_reference,
    derived_host_palace,derived_host_source) VALUES (?,?,?,?,?,?,?,?,?,1,?,?,?)''',
    (cid,ckey,palace,door if middle else None,'original_center_literal' if middle else 'not_center',
     None if middle else deity,None if middle else door,None if middle else star,
     'center_not_applicable_sanshu_three_fields' if middle else 'peripheral_literal_verified',
     'military_original_source+shijia_qiju',2 if middle else None,
     'shijia_qiju:五宫寄坤二宫' if middle else None))
 for step in case['original_author_steps']:
  k=step['step_number'];n=step['source_line'];e=step['source_end_line'];orig=segment(lines,n,e)
  db.execute('''INSERT INTO historical_case_reasoning
    (case_id,step_number,source_line,author_analysis_original,short_method_topic,metadata_json)
    VALUES (?,?,?,?,?,?)''',(cid,k,n,orig,step['domain_method_topic'],canon(step)))
  db.execute('''INSERT INTO historical_case_reasoning_trace
    (case_id,step_number,source_line,evidence_json,review_status,positive_training_eligible)
    VALUES (?,?,?,?,'source_anchor_only_needs_full_manual_evidence_chain',0)''',
    (cid,k,n,canon(step)))
  db.execute('''INSERT INTO semantic_assertions
     (chapter_key,concept_id,kind,relation,source_start_line,source_end_line,metadata_json,original_excerpt,review_status)
     VALUES (?,?,?,?,?,?,?,?,?)''',
    (CHAPTER,f'military:case{num:02d}:step{k:02d}','military_source_worked_example','not_approved_historical_method',
     n,e,canon(step),orig,'draft'))
 if num==1:
  phase_insert(db,cid,lines,31,33,'retrospective_author_explanation',False)
  phase_insert(db,cid,lines,54,70,'retrospective_author_explanation',False)
  db.execute('''INSERT INTO historical_military_source_caveat(case_id,source_line,caveat_kind,source_literal,review_status,note)
   VALUES (?,?,?,?,'unverified_historical_claim','Do not silently treat retrospective Hitler-war 1937 event sequence as a verified real-world date')''',
   (cid,31,'historical_chronology_dispute',segment(lines,31)))
 else:
  phase_insert(db,cid,lines,78,86,'initial_question',True)
  phase_insert(db,cid,lines,105,117,'initial_judgment',False)
  phase_insert(db,cid,lines,119,123,'new_disclosure',False,'cast02')
  phase_insert(db,cid,lines,140,150,'continued_judgment',False,'cast02')
  phase_insert(db,cid,lines,152,158,'new_disclosure',False,'cast03')
  phase_insert(db,cid,lines,175,181,'continued_judgment',False,'cast03')
  phase_insert(db,cid,lines,183,183,'book_feedback',False,'cast03')
  # Preserve actual prospective Q/A time as source-time, without retro-labeling earlier casts as known result.
 for n in spec['feedback_lines']:
  if not db.execute('SELECT 1 FROM historical_case_disclosures WHERE case_id=? AND source_line=?',(cid,n)).fetchone():
   db.execute('''INSERT INTO historical_case_disclosures(case_id,source_line,phase,fact_type,original_statement)
    VALUES (?,?,'later_than_initial','historical_book_account',?)''',(cid,n,segment(lines,n)))
 db.execute('''INSERT INTO historical_case_book_verdicts
   (event_family_id,primary_case_id,verdict,explicit_source_correction,source_correction_lines_json,
    feedback_source_lines_json,independent_external_verification,app_output_protocol,evidence_review_status,note)
    VALUES (?,?,'author_book_success_default',0,'[]',?,'not_verified','single_answer_for_one_cast','book_source_only',?)''',
    (cid,cid,canon(spec['feedback_lines']),
     'Retrospective source only; no valid blind-test first judgment' if num==1 else
     'Three source-time casts, one crisis; source book says no immediate second war but is not independent scientific validation'))
 db.execute('''INSERT INTO historical_case_review_audit
  (case_id,original_steps,mechanical_step_trace,human_complete_step_chains,review_status,warning)
  VALUES (?,?,?,0,'source_anchor_only_needs_full_manual_evidence_chain',?)''',
  (cid,len(case['original_author_steps']),len(case['original_author_steps']),
   'Entire case 1 is retrospective after WWII outcome' if num==1 else
   'All 3 actual source boards belong to one story; no answer or later news in first prompt'))

def build(base,source,output,index_dir,migration):
 if not base.exists() or not source.exists():raise ValueError('Missing input archive or original source')
 if output.exists():raise ValueError('Immutable version already exists, refusing overwrite')
 if sha(base)!=BASE_SHA:raise ValueError('Full 16-section baseline SHA256 mismatch')
 raw=source.read_bytes()
 if hashlib.sha256(raw).hexdigest()!=SOURCE_SHA:raise ValueError('Original chapter SHA mismatch')
 lines=raw.decode('utf8').splitlines()
 cases=prepare(lines)
 if len(cases)!=2 or sum(len(x['actual_printed_casts']) for x in cases)!=4 or sum(len(x['original_author_steps']) for x in cases)!=22:
  raise ValueError('Incomplete event, cast or author-step source')
 output.parent.mkdir(parents=True,exist_ok=True)
 with sqlite3.connect('file:'+str(base)+'?mode=ro',uri=True) as previous,sqlite3.connect(output) as db:
  previous.backup(db)
  db.executescript(migration.read_text('utf8'))
  db.execute('PRAGMA foreign_keys=ON')
  with db:
   if db.execute('SELECT 1 FROM sections WHERE section_key=?',(SECTION,)).fetchone():raise ValueError('Already in baseline')
   db.execute('''INSERT INTO sections(book_id,section_key,title,original_text,sha256,content_version,reviewed)
    VALUES ('shenqi',?,?,?,?,1,0)''',(SECTION,'军事事件预测',raw.decode('utf8'),SOURCE_SHA))
   sid=db.execute('SELECT last_insert_rowid()').fetchone()[0]
   db.execute('''INSERT INTO chapter_knowledge(chapter_key,book_id,title,source_sha256,source_length_bytes,knowledge_version,review_status)
     VALUES (?,'shenqi','军事事件预测',?,?,'1','draft')''',(CHAPTER,SOURCE_SHA,len(raw)))
   for line,key,description in METHODS:
    meta={'domain':'military_historical_source','source_line':line,'conditional_summary':description,
      'author_view_not_verified_military_prediction':True,'review_status':'draft'}
    db.execute('''INSERT INTO semantic_assertions(chapter_key,concept_id,kind,relation,source_start_line,source_end_line,metadata_json,original_excerpt,review_status)
     VALUES (?,?,?,?,?,?,?,?,?)''',(CHAPTER,'military:general:'+key,'military_historical_method','conditional_book_claim',line,line,
      canon(meta),segment(lines,line),'draft'))
   for spec,case in zip(CASE_SPECS,cases):import_case(db,lines,sid,spec,case)
   db.execute('''INSERT INTO chapter_archival_versions
     (archive_label,baseline_sha256,new_db_sha256,contains_complete_private_copyright_source,
      snapshot_type,created_utc,repo_public_archive_policy)
     VALUES (?, ?,NULL,1,'incremental_source_preserving','2026-10-20','user_explicitly_authorized_public_full_archive')''',
     ('shenqi_17_sections_86_whole_events',BASE_SHA))
  if db.execute('PRAGMA integrity_check').fetchone()[0]!='ok' or db.execute('PRAGMA foreign_key_check').fetchall():
   raise ValueError('Initial SQLite integrity / FK failure')
  assert_legacy_unchanged(previous,db)
  expected={'sections':17,'cases':86,'historical_chart_cells':774,
   'historical_case_additional_cast_cells':63,'historical_case_reasoning':398,
   'semantic_assertions':990+len(METHODS)+22,'historical_case_reasoning_trace':398,
   'historical_palace_standardization':837,'historical_case_additional_casts':7,
   'historical_military_cast_protocol':4,'historical_military_source_caveat':1}
  counts={table:db.execute('SELECT count(*) FROM "'+table+'"').fetchone()[0] for table in expected}
  for table,total in expected.items():
   if counts[table]!=total:raise ValueError((table,total,counts[table]))
  centres=db.execute('''SELECT count(*) FROM historical_palace_standardization WHERE palace=5 AND derived_host_palace=2
   AND standard_deity IS NULL AND standard_door IS NULL AND standard_star IS NULL''').fetchone()[0]
  if centres!=93:raise ValueError('Existing or new real center palace altered')
  if db.execute("SELECT count(*) FROM historical_case_book_verdicts WHERE verdict='author_book_error_explicit'").fetchone()[0]!=5:
   raise ValueError('Historical error labels unexpectedly altered')
  if db.execute("SELECT count(*) FROM historical_case_phase_events WHERE case_id='shenqi.military.case02'").fetchone()[0]!=7:
   raise ValueError('Chronology phases missing')
  db.execute('PRAGMA page_size=2048');db.execute('VACUUM');db.commit()
  if db.execute('PRAGMA integrity_check').fetchone()[0]!='ok' or db.execute('PRAGMA foreign_key_check').fetchall():
   raise ValueError('Final SQLite failed integrity check')
 index_dir.mkdir(parents=True,exist_ok=True)
 new_hash=sha(output)
 manifests={'schema':'wengua_military_source_chapter_manifest_v1','source_title':'军事事件预测',
  'source_print_chapter':'第十三章','source_sha256':SOURCE_SHA,'source_bytes':len(raw),'source_lines':len(lines),
  'chapter_key':CHAPTER,'whole_event_families':2,'real_book_printed_casts':4,
  'first_case_post_event_only':True,'second_case_three_source_time_casts':True,
  'real_palace_literally_printed':36,'original_author_step_units':22,'general_method_candidates':len(METHODS),
  'author_step_candidate_entries':22,'new_semantic_assertions':len(METHODS)+22,
  'original_source_print_independently_verified':False,'professional_complete_reasoning_approved':0,
  'historical_accuracy_independently_researched':False,'source_retrospective_analysis_separate_from_prospective':True,
  'baseline_sha256':BASE_SHA,'archive_sha256':new_hash,'archive_counts':counts,
  'faithfully_separate_derived_middle_palace':centres,'sqlite_full_backup_preserved':True}
 methods={'schema':'wengua_military_domain_research_workflow_v1','chapter_key':CHAPTER,'source_sha256':SOURCE_SHA,
  'methods':[{'concept_id':'military:general:'+key,'source_line':line,'conditional_summary':description,
     'source_is_historical_author_opinion':True,'review_status':'draft'} for line,key,description in METHODS],
  'study_workflow':['确定是不是军事历史事后对照研究，或当时真实问事；事后研究绝不能当初断',
   '按作者领域方法选择守方值符、攻方六庚，必要时用日干/时干与天地盘主客作为另组证据',
   '按实际起盘时辰和所印九宫绑定真实门星神、五行时令、格局和旬空，五宫寄坤另记推导',
   '值符宫与庚宫生克相互证据、旺衰、景惊门、六合调解、伏反吟，区分多个相反条件',
   '按时间顺序复原案例二的三个不同日时提问、已知新增事实、前三次证据，避免后验泄漏',
   '区分初始预测、逐步过程、候选应期、事实反馈；独立标记有历史争议的源断言',
   '全部知识和案例未经独立事实验证、不得作为现实军事决策或可操作情报']}
 audit={'schema':'wengua_military_source_audit_v1','source_sha256':SOURCE_SHA,
  'case1':{'type':'retrospective_lookback_after_WWII_outcome','source_known_history_line':31,
    'author_analysis_step_lines':CASE_SPECS[0]['source_casts'][0]['analysis_lines'],
    'chronology_flag':'1937 Hitler WWII declaration / sequence is a source historical claim, not externally verified here',
    'prospective_blind_evaluation_allowed':False},
  'case2':{'same_event_family_with_three_actual_casts':True,
    'source_board_border_lines':[89,126,161], 'actual_cast_dates':['1998-01-29','1998-02-07','1998-02-22'],
    'step_continuation_109_includes_line111':True,
    'source_known_new_facts_case2_c02':[119,123], 'source_known_news_before_c03':[152,154,156,158],
    'no_relabel_as_three_independent_correct_predictions':True,'source_after_episode_feedback_line':183},
  'methodological_guard':'Historical divination is not validated geopolitical or military intelligence; no use for military action planning.'}
 idx={'schema':'wengua_military_whole_events_v1','chapter_key':CHAPTER,'source_sha256':SOURCE_SHA,'cases':cases}
 traces={'schema':'wengua_military_author_step_candidates_v1','chapter_key':CHAPTER,'source_sha256':SOURCE_SHA,
  'author_step_count':22,'human_verified_complete_causal_chains':0,
  'cases':[{'case_id':x['case_id'],'steps':x['original_author_steps']} for x in cases]}
 for filename,obj in [('chapter_manifest.json',manifests),('case_index.json',idx),
   ('method_index.json',methods),('source_audit.json',audit),('author_reasoning_evidence_index.json',traces)]:
  (index_dir/filename).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 print(json.dumps({'new_archive':str(output),'new_archive_sha256':new_hash,'counts':counts,
  'source_sha256':SOURCE_SHA,'events':2,'charts':4,'palaces':36,'author_steps':22,'new_semantic':len(METHODS)+22,
  'historical_previous_rows_untouched':True,'all_centres_source_preserved':centres},ensure_ascii=False,indent=2))
 return 0

def main(argv=None):
 p=argparse.ArgumentParser()
 p.add_argument('--base',type=Path,required=True)
 p.add_argument('--source',type=Path,required=True)
 p.add_argument('--output',type=Path,required=True)
 p.add_argument('--index-dir',type=Path,required=True)
 p.add_argument('--migration',type=Path,default=ROOT/'schema/migrations/012_military_event_provenance.sql')
 a=p.parse_args(argv)
 return build(a.base,a.source,a.output,a.index_dir,a.migration)
if __name__=='__main__':raise SystemExit(main())
