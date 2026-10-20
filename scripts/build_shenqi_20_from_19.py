"""Immutable chapter 20 whole-story importer: traditional '人生机遇预测'.

Book-claimed outcomes are NOT scientific validation of life expectancy, health,
accident risk or career. Later disclosures and retrospective analysis never join
first-attempt training observations. Existing 19 complete chapters remain untouched.
"""
from __future__ import annotations
import argparse, hashlib, json, re, sqlite3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCE_SHA='92de6590ebf88698d9bf0137e8ecdb780b8f1ff1f66765faf0a69eb3d7eac507'
BASE_SHA='9412c314a10827b34f6d2e1930124b672f389156d86692d58db1ffdff5ada4b0'
SECTION='life_opportunity_prediction_ch16'
CHAPTER='shenqi/life_opportunity_prediction_ch16/v1'
PALACES=('巽四宫','离九宫','坤二宫','震三宫','中五宫','兑七宫','艮八宫','坎一宫','乾六宫')
NUM=(4,9,2,3,5,7,8,1,6)
CASES=[
 dict(n=1,start=30,end=81,chart=37,steps=[53,54,56,59,62,65,68,70,73,75,78],known=[32,34],forecast=[53,54,57,60,63,66,71,73,76,79],feedback=[55,58,61,64,67,69,72,74,77,80],title='县干部近况、家庭与上级变化',strategy='inquiry_time'),
 dict(n=2,start=83,end=156,chart=92,steps=[108,111,114,119,124,127,134,136,138,140,142,144,147,150,155],known=[85,89],forecast=[109,112,115,120,125,128,130,134,136,138,140,142,145,148,150,156],feedback=[110,113,116,121,123,126,129,131,135,137,139,141,143,146,149,151],title='研讨班学员多轮问运、官司、亲属及办厂',strategy='inquiry_time'),
 dict(n=3,start=158,end=191,chart=164,steps=[180,181,182,183,184,185,190],known=[160,161],forecast=[186,188],feedback=[189],title='赵某新年风险与事后车祸应期复盘',strategy='inquiry_time'),
 dict(n=4,start=193,end=221,chart=201,steps=[217,218,219,220,221],known=[195,198],forecast=[217,218,219,220],feedback=[195,196],title='已知女童溺亡后的出生局回顾分析',strategy='birth_time_post_outcome'),
 dict(n=5,start=223,end=273,chart=231,steps=[246,248,250,252,254,257,259,261,263,265,267,269,271],known=[225,228],forecast=[246,248,250,252,254,257,259,261,263,265,267,269,271],feedback=[247,249,251,253,256,258,260,262,264,268,270],title='外籍华人医生出生局终身问答与年份误断',strategy='birth_time_inquiry'),
]
# Domain methods: exact source line + conditional abstraction. The classical poem is
# conditional source material, not a verified scientific prediction dataset.
METHODS=[
(10,'birth_time_long_term','先天素质与长期机遇使用出生时起局，日干为本人'),
(10,'family_year_parent','家庭领域年干为父母，需关联合干及个人资料'),
(10,'family_month_siblings','家庭领域月干代表兄弟姐妹'),
(10,'family_hour_children','家庭领域时干代表子女'),
(10,'society_year_superior','社会领域年干为领导上级'),
(10,'society_month_colleagues','社会领域月干为同事朋友'),
(10,'society_hour_subordinates','社会领域时干为下级群众'),
(10,'stars_time','九星对应作者所谓天时，需要时令强弱'),
(10,'doors_human','八门对应人事关系'),
(10,'palaces_location','九宫为方向与空间条件'),
(10,'deities_symbol','八神为传统象意，非可测能量场科学事实'),
(10,'strength_patterns','旺相休囚及格局生克合参，不能据单象断命'),
(11,'question_time_recent','近期机遇用问测时间起局'),
(11,'day_plus_birthyear','近期以日干本人兼年命落宫综合'),
(11,'visitor_seat','必要时结合来人坐宫，前提事实不可泄漏'),
(13,'poem_body_parts','宫位可作传统身体部位象意，不得据此诊断疾病'),
(14,'spouse_wife_yi_ding','妻妾取乙丁须结合身份/问题，不机械套用'),
(14,'spouse_husband_geng_bing','夫君取庚丙须识别关系与合干'),
(14,'fortune_condition_strength','富贵判断需旺相得奇及具体条件，非无条件定论'),
(15,'pattern_weighting','古籍强调格局分轻重与孤虚旺相先判断'),
(16,'property_sheng_door','生门关联产业，须合三奇旺衰与日干相生克'),
(16,'inner_outer_migration','人宫及生门内外区分祖业/迁居类象'),
(17,'day_hour_loneliness','日时孤虚/空墓条件为古籍孤独类象而非现实定数'),
(18,'star_job_profession','按九星强弱及奇门判断职业只是古籍类象'),
(19,'gate_job_profession','按八门与吉格职业取象需符合问事实际'),
(20,'door_star_joint_profession','八门和对应九星五行须联合解释'),
(21,'star_strong_vs_weak','不同九星旺弱改变传统职业类象'),
(22,'heaven_earth_stem_patterns','干加干与青龙返首/飞鸟跌穴等按原格局条件解释'),
(22,'geng_wu_crosspalace','庚戊与戊庚格局的成败、地点与人物差异条件'),
(23,'xin_ren_gui_classical','辛壬癸象意须看环境旺弱，禁无条件人格贬损'),
(24,'avoid_void_tomb','吉凶格遇空亡墓绝需减益与反证分析'),
(24,'fanyin_fuyin','反吟伏吟依具体事体和月令综合，不套一条绝对规则'),
(25,'source_explicit_caution','作者自言古籍片面绝对，只可综合变通参考'),
(26,'classical_not_science','传统命运推断尚无科学验证，严禁发布死亡疾病确定性预测'),
]
STEP_NOTES={
 (1,11):'原书未编号的领导换职分析，保留而不假装编号',
 (2,1):'同一步同时给吉凶格并驳回既有死亡断言；这是安全相关的源书声称，不是医学证明',
 (2,4):'原告被告要根据问者刚披露的法律角色选用神；第117-118行属于新信息',
 (2,5):'第126行资本已追回但利息未回收，是断语后披露，必须时序隔离',
 (2,15):'第154行新问办厂；第156行未来办成的应期未获书内后续实际证明',
 (3,7):'第190行为事故已知后的作者复盘，不能作为原先精确日期的成功预测',
 (4,1):'本案第195行已给出女童溺亡，所有217-221分析纯属后验研究，绝不可盲测',
 (4,5):'第221行作者自己提出同局不同命、结果非必然的明确限制',
 (5,6):'第257行先断死亡为1994或1995，第258行明确纠正实际1996年；局部年份错误，不可成功训练',
 (5,7):'第259行1957等之外的丈夫干支与1996已由第258行披露，是后验分析不是初断',
}
CASE5_STEP_PHASE={1:'first_attempt',2:'first_attempt',3:'first_attempt',4:'first_attempt',5:'first_attempt',6:'first_attempt_year_error',7:'after_disclosure',8:'after_disclosure',9:'after_disclosure',10:'after_disclosure',11:'after_disclosure',12:'after_disclosure',13:'after_disclosure'}

def canon(obj):return json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(',',':'))
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def seg(lines,a,b=None):
 b=a if b is None else b
 if not 1<=a<=b<=len(lines):raise ValueError('source line not found')
 return '\n'.join(lines[a-1:b])
def parse_chart(lines,start):
 if not lines[start-1].startswith('┌'):raise ValueError(('No actual chart',start))
 out=[]
 for row in range(3):
  y=start+1+row*4
  layers=[]
  for delta in range(3):
   cols=[z.strip() for z in lines[y+delta-1].split('│')[1:-1]]
   if len(cols)!=3:raise ValueError(('Chart lacks 3 columns',start,row,delta))
   layers.append(cols)
  for col in range(3):
   loc=row*3+col;pal=NUM[loc]
   name,door,star=[layers[d][col] for d in range(3)]
   if not name.startswith(PALACES[loc]):raise ValueError(('Palace labels do not agree',start,loc))
   if pal==5:
    if '八神' in name or not door.startswith('原盘单字：') or star:raise ValueError('Center must have only literal stem')
    deity='';door=door.split('：',1)[1]
    if not re.fullmatch('[乙丙丁戊己庚辛壬癸]',door):raise ValueError('Nonexistent center stem')
   else:
    if '八神：' not in name or not door.startswith('门位：') or not star.startswith('星位：'):
     raise ValueError(('Peripheral original source missing',start,name,door,star))
    deity=name.split('八神：',1)[1].strip();door=door.split('：',1)[1].strip();star=star.split('：',1)[1].strip()
   out.append((pal,y+col,name,deity,door,star))
 if sorted(x[0] for x in out)!=list(range(1,10)):raise ValueError('Incomplete source nine palace chart')
 return out

def lexical(source):
 ids=[]
 for g in '开休生伤杜景死惊':
  if g+'门' in source:ids.append('door:'+g)
 for g in '蓬任冲辅英芮柱心禽':
  if '天'+g in source:ids.append('star:'+g)
 for x in ('玄武','白虎','九天','九地','六合','太阴','螣蛇','值符'):
  if x in source:ids.append('deity:'+x)
 for x in '乾坤巽离震兑艮坎':
  if x+'宫' in source:ids.append('trigram:'+x)
 return sorted(set(ids))

def reasoning(lines,n,k,line):
 original=seg(lines,line)
 phase=('retrospective_after_result' if n==4 or (n==3 and line==190) else
  CASE5_STEP_PHASE[k] if n==5 else 'author_before_next_disclosure')
 fragments=[x.strip() for x in re.split('[，；。]',original) if x.strip()]
 is_result_only=(n==5 or (n==1 and k==11))
 return {'step_number':k,'source_line':line,'source_end_line':line,'source_step_original_in_complete_sqlite':True,
  'step_kind':'unexplained_author_prediction' if n==5 else 'author_reasoning_claim',
  'case_progress_phase':phase,'source_observed_clause_candidates':[] if is_result_only else [s for s in fragments if any(y in s for y in ('宫','门','星','神','月','日干','时干','年命','生','克','空亡','值符','格','年干'))],
  'source_counterevidence_clause_candidates':[s for s in fragments if any(y in s for y in ('但','又','虽然','未','不','仍','如果','可能'))],
  'old_concept_lexical_candidate_ids':lexical(original),'old_concept_semantic_links_human_approved':False,
  'source_causal_link_gap':bool(is_result_only), 'additional_caveat':STEP_NOTES.get((n,k)),
  'independent_book_result_confirmed':False,'positive_training_eligible':False,
  'review_status':'source_anchored_needs_stepwise_human_verification'}

def indices(lines):
 out=[]
 for case in CASES:
  n=case['n'];source_steps=case['steps']
  if not lines[case['start']-1].startswith('实例'):raise ValueError(('Original case not found',n))
  cells=parse_chart(lines,case['chart'])
  for k,line in enumerate(source_steps,1):
   if not (re.match(r'^\(\d+\)',lines[line-1]) or (n==1 and line==78) or (n==3 and line==190) or (n==4 and line==221) or n==5):
    raise ValueError(('Expected source analysis step missing',n,line))
  cid=f'shenqi.life.case{n:02d}'
  e={'case_number':n,'case_id':cid,'event_family_id':cid,'source_span':[case['start'],case['end']],
    'original_chart_start':case['chart'],'nine_palaces':9,'cast_strategy':case['strategy'],
    'source_step_lines':source_steps,'author_step_evidence':[reasoning(lines,n,k,line) for k,line in enumerate(source_steps,1)],
    'initial_source_lines':case['known'],'book_claim_judgment_lines':case['forecast'],'book_response_lines':case['feedback'],
    'source_verified_independent_real_world':False,'human_complete_reasoning_approved':False,'positive_training_eligible':False}
  if n==2:e['multiple_subquestions_same_event']=True;e['new_disclosure_lines']=[116,118,121,123,126,129,131,135,137,139,141,143,146,149,151,154];e['future_plan_not_outcome_lines']=[139,156]
  if n==3:e['missed_precise_timing']={'author_initial_prediction_lines':[186,188], 'result_line':189,'later_reconstruction_line':190}
  if n==4:e['known_fatal_outcome_precedes_cast']=True;e['eligible_blind_test']=False
  if n==5:e['explicit_year_mistake']={'initial_line':257,'corrected_by_subject_line':258,'first_year_choices':[1994,1995],'reported_year':1996};e['post_feedback_source_lines']=[259,261,263,265,267,269,271]
  out.append(e)
 return out

def phase(db,cid,lines,a,b,kind,visible=False,text=None):
 raw=text if text is not None else seg(lines,a,b)
 db.execute('''INSERT INTO historical_case_phase_events
 (case_id,source_start_line,source_end_line,phase,original_excerpt,metadata_json,visible_to_initial_blind_test)
 VALUES (?,?,?,?,?,?,?)''',(cid,a,b,kind,raw,canon({'source_chapter':CHAPTER,'before_feedback':visible}),int(visible)))

def add_one(db,lines,sid,c):
 n=c['case_number'];spec=CASES[n-1];cid=c['case_id']
 # Crucial: the initial question is not the whole event narration.
 known=seg(lines,*spec['known'])
 if n==4: known=seg(lines,195,198) # already contains known outcome, retrospective ONLY
 if n==5: known=seg(lines,225,228)
 judge='\n'.join(seg(lines,k) for k in spec['forecast'])
 # Full authored replies and post-discussion remain in section.original_text;
 # later_feedback must never appear in known_before.
 feedback='\n'.join(seg(lines,k) for k in spec['feedback'])
 original='\n\n'.join(seg(lines,k) for k in spec['steps'])
 db.execute('''INSERT INTO cases (case_id,section_id,event_family_id,domain_id,known_before,
 author_yongshen_steps,author_judgment,later_feedback,reviewed)
 VALUES (?,?,?,?,?,?,?,?,0)''',(cid,sid,cid,'life_opportunity_book_study',known,original,judge,feedback))
 db.execute('''INSERT INTO historical_case_protocol
 (case_id,completeness,published_chart_verification,feedback_independently_verified,eligible_blind_test,case_source_sha256,metadata_json)
 VALUES (?,'complete_source_event_one_genuine_chart','book_text_transcription_not_recast',0,0,?,?)''',
 (cid,SOURCE_SHA,canon(c)))
 db.execute('''INSERT INTO historical_life_case_context
 (case_id,source_chart_line,cast_strategy,initial_context_json,retrospective_case,
 original_book_explicit_year_error,original_book_initial_years_json,source_revealed_year,
 source_method_missing_for_claims,scientific_independent_verification,metadata_json)
 VALUES (?,?,?,?,?,?,?,?,?,?,?)''',(
 cid,c['original_chart_start'],c['cast_strategy'],canon(c['initial_source_lines']),int(n==4),int(n==5),
 canon([1994,1995]) if n==5 else '[]',1996 if n==5 else None,int(n==5),0,canon(c)))
 for pal,source_line,label,god,door,star in parse_chart(lines,c['original_chart_start']):
  db.execute('''INSERT INTO historical_chart_cells
 (case_id,palace,source_line,palace_label_raw,deity_raw,door_position_raw,star_position_raw,source_status)
 VALUES (?,?,?,?,?,?,?,'original_life_text_not_independently_recast')''',(cid,pal,source_line,label,god,door,star))
  center=pal==5
  db.execute('''INSERT INTO historical_palace_standardization
 (case_id,cast_key,palace,center_stem,source_of_center_stem,standard_deity,standard_door,standard_star,
 normalized_status,original_raw_integrity_checked,method_reference,derived_host_palace,derived_host_source)
 VALUES (?,?,?,?,?,?,?,?,?,1,?,?,?)''',(
 cid,'primary',pal,door if center else None,'original_center_literal' if center else 'not_center',
 None if center else god,None if center else door,None if center else star,
 'center_literal_no_unsupported_door_star_deity' if center else 'original_peripheral_literal',
 'life_opportunity_source+shijia_qiju',2 if center else None,
 'shijia_qiju:五宫寄坤二宫' if center else None))
 for step in c['author_step_evidence']:
  k=step['step_number'];ln=step['source_line'];literal=seg(lines,ln)
  db.execute('''INSERT INTO historical_case_reasoning
 (case_id,step_number,source_line,author_analysis_original,short_method_topic,metadata_json)
 VALUES (?,?,?,?,?,?)''',(cid,k,ln,literal,step['step_kind'],canon(step)))
  db.execute('''INSERT INTO historical_case_reasoning_trace
 (case_id,step_number,source_line,evidence_json,review_status,positive_training_eligible)
 VALUES (?,?,?,?,'source_anchored_needs_stepwise_human_verification',0)''',(cid,k,ln,canon(step)))
  db.execute('''INSERT INTO semantic_assertions
 (chapter_key,concept_id,kind,relation,source_start_line,source_end_line,metadata_json,original_excerpt,review_status)
 VALUES (?,?,?,?,?,?,?,?,?)''',(
 CHAPTER,f'life:case{n:02d}:step{k:02d}','life_historical_author_step',
 'source_claim_draft_not_approved',ln,ln,canon(step),literal,'draft'))
 phase(db,cid,lines,spec['known'][0],spec['known'][-1],'initial_question',n not in (4,),text=known)
 if n==1:
  phase(db,cid,lines,53,54,'initial_judgment')
  phase(db,cid,lines,78,79,'continued_judgment')
  phase(db,cid,lines,55,55,'book_feedback')
  phase(db,cid,lines,80,81,'book_feedback')
 elif n==2:
  phase(db,cid,lines,108,109,'initial_judgment')
  for k in (116,118,121,123,126,129,131,135,137,139,141,143,146,149,151,154):
   phase(db,cid,lines,k,k,'new_disclosure')
  phase(db,cid,lines,119,120,'continued_judgment')
  phase(db,cid,lines,155,156,'continued_judgment')
  phase(db,cid,lines,110,110,'book_feedback')
 elif n==3:
  phase(db,cid,lines,186,188,'initial_judgment')
  phase(db,cid,lines,189,189,'book_feedback')
  phase(db,cid,lines,190,191,'retrospective_author_explanation')
 elif n==4:
  phase(db,cid,lines,195,198,'cast_metadata')
  phase(db,cid,lines,217,220,'retrospective_author_explanation')
  phase(db,cid,lines,221,221,'retrospective_author_explanation')
 else:
  phase(db,cid,lines,246,246,'initial_judgment')
  phase(db,cid,lines,256,256,'new_disclosure')
  phase(db,cid,lines,257,257,'continued_judgment')
  phase(db,cid,lines,258,258,'new_disclosure')
  phase(db,cid,lines,259,259,'editor_posthoc_correction')
  for ln in (261,263,265,267,269,271):phase(db,cid,lines,ln,ln,'continued_judgment')
  phase(db,cid,lines,260,260,'book_feedback')
  db.execute('''INSERT INTO historical_case_reasoning_corrections
 (case_id,source_line,original_step_number,correction_kind,corrected_yongshen_policy,
 original_analysis_is_positive_training,source_review_status,rationale_original)
 VALUES (?,?,?,'incorrect_year_reported','1994/1995 predicted; informant corrected actual death year to 1996',0,
 'source_documented_needs_professional_review',?)''',(
 cid,258,6,seg(lines,257,258)))
 db.execute('''INSERT INTO historical_life_source_error_segments
 (case_id,source_line,error_kind,original_statement,subsequent_evidence,eligible_positive_training)
 VALUES (?,?,?,?,?,0)''',(cid,257,'explicit_wrong_death_year',seg(lines,257),seg(lines,258)))
 verdict='author_book_error_explicit' if n==5 else 'author_book_success_default' # Explicit case5 wrong year remains a negative step; preserve all other source responses.
 db.execute('''INSERT INTO historical_case_book_verdicts
 (event_family_id,primary_case_id,verdict,explicit_source_correction,source_correction_lines_json,
 feedback_source_lines_json,independent_external_verification,app_output_protocol,evidence_review_status,note)
 VALUES (?,?,?,?,?,?,'not_verified','single_answer_for_one_cast','source_study_draft',?)''',(
 cid,cid,verdict,int(n==5),canon([257,258]) if n==5 else '[]',canon(spec['feedback']),
 'Case5 explicitly wrong year 1994/1995 vs 1996; cannot train error as success' if n==5 else
 'Retrospective known death; not valid blind prediction' if n==4 else
 'Book claimed result, not independently verified'))
 db.execute('''INSERT INTO historical_case_review_audit
 (case_id,original_steps,mechanical_step_trace,human_complete_step_chains,review_status,warning)
 VALUES (?,?,?,0,'source_anchored_needs_stepwise_human_verification',?)''',(
 cid,len(spec['steps']),len(spec['steps']),
 'Known fatal result, no blind test' if n==4 else 'Subquestion chronology / partial-error review required' if n in (2,3,5) else 'Author causal links not human verified'))

def compare_legacy(old,updated):
 """All columns and every row of EVERY old source table must remain identical."""
 for (name,) in old.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"):
  cols=[x[1] for x in old.execute('PRAGMA table_info("'+name+'")')]
  cols_str=','.join('"'+x+'"' for x in cols)
  original=list(old.execute('SELECT '+cols_str+' FROM "'+name+'"'))
  newer=set(updated.execute('SELECT '+cols_str+' FROM "'+name+'"'))
  if not all(row in newer for row in original):raise ValueError('Legacy database changed '+name)

def build(base,source,output,index_dir,migration):
 base=Path(base);source=Path(source);output=Path(output);index_dir=Path(index_dir);migration=Path(migration)
 if output.exists():raise ValueError('Do not overwrite any prior complete SQLite version')
 if sha(base)!=BASE_SHA:raise ValueError('Wrong 19-chapter GitHub full binary SHA')
 raw=source.read_bytes()
 if hashlib.sha256(raw).hexdigest()!=SOURCE_SHA:raise ValueError('Source SHA256 differs')
 lines=raw.decode('utf8').splitlines()
 if len(lines)!=273 or lines[2]!='人生机遇预测' or '实例解析(5例)' not in lines[27]:raise ValueError('Chapter boundaries changed')
 cases=indices(lines)
 if len(cases)!=5 or sum(len(c['source_step_lines']) for c in cases)!=51:raise ValueError('Any author-source step missing')
 output.parent.mkdir(parents=True,exist_ok=True)
 with sqlite3.connect('file:'+str(base)+'?mode=ro',uri=True) as old,sqlite3.connect(output) as db:
  old.backup(db)
  db.executescript(migration.read_text('utf8'));db.execute('PRAGMA foreign_keys=ON')
  with db:
   if db.execute('SELECT 1 FROM sections WHERE section_key=?',(SECTION,)).fetchone():raise ValueError('This section already exists')
   db.execute('''INSERT INTO sections(book_id,section_key,title,original_text,sha256,content_version,reviewed)
   VALUES ('shenqi',?,?,?,?,1,0)''',(SECTION,'人生机遇预测',raw.decode('utf8'),SOURCE_SHA))
   sid=db.execute('SELECT last_insert_rowid()').fetchone()[0]
   db.execute('''INSERT INTO chapter_knowledge(chapter_key,book_id,title,source_sha256,source_length_bytes,knowledge_version,review_status)
   VALUES (?,'shenqi','人生机遇预测',?,?,'1','draft')''',(CHAPTER,SOURCE_SHA,len(raw)))
   for line,key,description in METHODS:
    d={'line':line,'conditional_source_summary':description,'professionally_approved':False}
    db.execute('''INSERT INTO semantic_assertions
    (chapter_key,concept_id,kind,relation,source_start_line,source_end_line,metadata_json,original_excerpt,review_status)
    VALUES (?,?,?,?,?,?,?,?,?)''',(
    CHAPTER,'life:general:'+key,'domain_book_conditional_method','source_claim_not_empirical_prediction',line,line,canon(d),seg(lines,line),'draft'))
   for c in cases:add_one(db,lines,sid,c)
   db.execute('''INSERT INTO chapter_archival_versions
   (archive_label,baseline_sha256,new_db_sha256,contains_complete_private_copyright_source,snapshot_type,created_utc,repo_public_archive_policy)
   VALUES (?, ?,NULL,1,'incremental_source_preserving','2026-10-20','user_explicitly_authorized_public_full_archive')''',
   ('shenqi_20_sections_98_whole_events',BASE_SHA))
  if db.execute('PRAGMA integrity_check').fetchone()[0]!='ok' or db.execute('PRAGMA foreign_key_check').fetchall():raise ValueError('Broken SQLite before finalizing')
  compare_legacy(old,db)
  expected={'sections':20,'cases':98,'historical_chart_cells':882,
    'historical_case_additional_cast_cells':63,'historical_case_additional_casts':7,
    'historical_case_reasoning':468,'semantic_assertions':1122+len(METHODS)+51,
    'historical_case_reasoning_trace':468,'historical_palace_standardization':945,
    'historical_life_case_context':5,'historical_life_source_error_segments':5}
  counts={name:db.execute('SELECT count(*) FROM "'+name+'"').fetchone()[0] for name in expected}
  if counts!=expected:raise ValueError(('Unexpected count change',counts,expected))
  center=db.execute('''SELECT count(*) FROM historical_palace_standardization
   WHERE palace=5 AND derived_host_palace=2 AND standard_deity IS NULL AND standard_door IS NULL AND standard_star IS NULL''').fetchone()[0]
  if center!=105:raise ValueError('Center rule corrupted')
  if db.execute("SELECT count(*) FROM historical_case_book_verdicts WHERE verdict='author_book_error_explicit'").fetchone()[0]!=6:
   raise ValueError('Historical 5 plus the explicit new wrong-year case must equal 6')
  if db.execute('SELECT count(*) FROM historical_case_reasoning_trace WHERE positive_training_eligible=1').fetchone()[0]:raise ValueError('Draft not allowed to train')
  db.execute('PRAGMA page_size=2048');db.execute('VACUUM');db.commit()
  if db.execute('PRAGMA integrity_check').fetchone()[0]!='ok' or db.execute('PRAGMA foreign_key_check').fetchall():raise ValueError('Final database invalid')
 index_dir.mkdir(parents=True,exist_ok=True)
 m={'schema':'wengua_life_chapter_full_source_v1','chapter_key':CHAPTER,'title':'人生机遇预测',
 'source_sha256':SOURCE_SHA,'source_utf8_bytes':len(raw),'source_lines':len(lines),
 'case_families':5,'actual_printed_charts':5,'source_palace_cells':45,
 'author_source_step_units':51,'general_domain_method_candidates':len(METHODS),
 'new_semantic_candidates':len(METHODS)+51,'cast_strategy_counts':{'birth_time':2,'inquiry_time':3},
 'book_failure_details':{'case5_wrong_spouse_death_year':True,'case3_missed_precise_time_then_retroactive':True},
 'retrospective_literary_only_case4':True,'independent_professional_reviews':0,'training_approved':0,
 'database_sha256':sha(output),'baseline_sha256':BASE_SHA,'cumulative_counts':counts,
 'source_limits':'Book narratives have no independent medical, death, financial or criminal verification; never offer fatality forecasts'}
 (index_dir/'chapter_manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 (index_dir/'case_index.json').write_text(json.dumps({'schema':'wengua_life_whole_source_cases_v1','source_sha256':SOURCE_SHA,'cases':cases},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 (index_dir/'method_index.json').write_text(json.dumps({'schema':'wengua_life_domain_conditional_rules_v1','source_sha256':SOURCE_SHA,'methods':[{'source_line':n,'concept_id':'life:general:'+key,'conditional_summary':desc,'review_status':'draft'} for n,key,desc in METHODS]},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 (index_dir/'source_audit.json').write_text(json.dumps({'schema':'wengua_life_source_chronology_v1','source_sha256':SOURCE_SHA,
 'case1_unnumbered_leadership_step':78,'case2_multisubquestion_not_15_cases':True,
 'case3_true_outcome_known_before_step_190':True,'case4_birth_cast_after_known_death':True,
 'case5_wrong_year_initial':257,'case5_informant_correction':258,'case5_after_year_disclosed':259,
 'human_complete_reasoning_verified':0,'positive_training_eligible':False},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 return m

def main():
 p=argparse.ArgumentParser();p.add_argument('--base',required=True);p.add_argument('--source',required=True);p.add_argument('--output',required=True);p.add_argument('--index-dir',required=True)
 p.add_argument('--migration',default=str(ROOT/'schema/migrations/015_life_case_phase.sql'));a=p.parse_args()
 print(json.dumps(build(a.base,a.source,a.output,a.index_dir,a.migration),ensure_ascii=False,indent=2))
if __name__=='__main__':main()
