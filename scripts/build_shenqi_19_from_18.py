"""Add the nineteenth processed Shenqi source to the previous FULL immutable SQLite.

Historical geomancy is a book-source study, not engineering/geotechnical evidence.
Preserves both complete stories while forbidding invented charts and causal links.
"""
from __future__ import annotations
import argparse, hashlib, json, re, sqlite3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCE_SHA='c755e3879432b2f84329e0b9491eabdb48b865fa2f1cad96a0187f1bb7a3f5c1'
BASE_SHA='c20edf3611a71d31a241f45d10f9b4a175212081659ac05908b980fd8854c31c'
SECTION='geographic_environment_prediction_ch15'
CHAPTER='shenqi/geographic_environment_prediction_ch15/v1'
PALACES=('巽四宫','离九宫','坤二宫','震三宫','中五宫','兑七宫','艮八宫','坎一宫','乾六宫')
NUM=(4,9,2,3,5,7,8,1,6)
# Keep even unnumbered author stages; never inflate them to numbered author rules.
CASES=[
 {'number':1,'title':'三方案金融中心主楼艮位与建设资金时间','start':15,'end':49,'border':26,'question_lines':[17,18,19,20,21,22,23], 'step_lines':[41,44,45,46],'judgment_lines':[41,44,45,46],'feedback_lines':[47,48,49], 'date':'1997-08-27','hour':'甲午', 'prior_external_consensus':True},
 {'number':2,'title':'吴先生拟选辛山乙向墓地的使用权问答','start':51,'end':81,'border':61,'question_lines':[56,57,58], 'step_lines':[76,78],'judgment_lines':[76,78],'feedback_lines':[79,80,81], 'date':'1998-03-05','hour':'戊戌', 'prior_external_consensus':False}
]
METHODS=[
 (9,'day_person','日干代表求测之人'),
 (9,'hour_residence','时干代表住宅'),
 (9,'hour_strong_three_wonders_gives','时干临三奇吉门吉星吉神吉格旺相又生日干宫，传统判断最佳宅'),
 (9,'hour_good_otherwise','时干虽未遇三奇吉门但吉星吉神吉格旺相生日干，传统判断较好宅'),
 (9,'mixed_conditions','时干落宫吉凶混杂，传统判断一般宅'),
 (9,'hour_bad_controls_day','时干凶门凶星凶神凶格克日干宫，传统判断不利'),
 (9,'evaluate_star_door_palace','结合星、门、宫的具体生克关系而不只贴吉凶标签'),
 (10,'living_house_sheng_gate','阳宅以生门作房屋'),
 (10,'living_plot_si_gate','阳宅以死门作宅基地皮'),
 (10,'living_strength_day','阳宅生门死门需合旺相休囚与日干生克'),
 (10,'zhifu_new_home','值符作为新宅的专题用神'),
 (10,'zhishi_old_home','值使作为旧宅的专题用神'),
 (11,'grave_si_gate','阴宅以死门作主用神'),
 (11,'grave_ground_dead_heaven_living','阴宅死门宫地盘属死者、天盘属生者的专题关系'),
 (11,'grave_good_star_wonders_updown_generate','阴宅吉神吉星得三奇且上下相生的传统吉条件'),
 (11,'grave_bad_star_no_wonders_updown_control','阴宅凶神凶星不得三奇且上下相克的传统凶条件'),
 (11,'heaven_controls_ground_dead','阴宅天盘克地盘，传统解释对死者不利'),
 (11,'ground_controls_heaven_living','阴宅地盘克天盘，传统解释对生者不利'),
 (11,'grave_palace_top','阴宅死门落二五八九宫的传统优先级'),
 (11,'grave_palace_second','阴宅死门落六七宫的传统次级'),
 (11,'grave_palace_low','阴宅死门落一三四宫的传统不利'),
 (40,'site_survey_recommended','作者明确说勘察地理必须到现场，奇门只能与实地勘察对照'),
 (40,'invisible_field_author_claim','原书声称可推磁场生物场微波；未独立实测，不能作为科学事实或地质工程论据'),
]
STEP_TOPICS={1:[
 '作者将生门及九天同在艮八宫与事先专家第三方案共识对照（非独立盲断）',
 '作者宣称日干辛与甲午时同坎宫、太岁生助，伏吟导致工期拖延',
 '作者断项目1995年策划、最早2001年开业，未解释具体应期算法',
 '作者断八亿起投、十四亿完工及现金未到位，未解释数理取值算法'],
 2:[
 '王庆丰表示墓地形势优美但吴先生不能使用；原书没有解释对应的宫位组合',
 '王庆丰表示墓地已被他人占有，吴先生得不到；没有来源支持完整反证或用神路径']}

def canon(x): return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'))
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def seg(lines,a,b=None):
 b=a if b is None else b
 if not 1<=a<=b<=len(lines):raise ValueError('Invalid source line range')
 return '\n'.join(lines[a-1:b])
def lex(s):
 out=[]
 for x in '开休生伤杜景死惊':
  if x+'门' in s:out.append('door:'+x)
 for x in '蓬任冲辅英芮柱心禽':
  if '天'+x in s:out.append('star:'+x)
 for x in ('玄武','白虎','九天','九地','六合','太阴','螣蛇','值符'):
  if x in s:out.append('deity:'+x)
 for x in '乾坤震巽离坎艮兑':
  if x+'宫' in s:out.append('trigram:'+x)
 return sorted(set(out))
def parse_chart(lines,start):
 if not lines[start-1].startswith('┌'):raise ValueError(('Missing real printed chart',start))
 cells=[]
 for row in range(3):
  y=start+1+row*4;levels=[]
  for d in range(3):
   cols=[x.strip() for x in lines[y+d-1].split('│')[1:-1]]
   if len(cols)!=3:raise ValueError(('Expected three original columns',start,row,d))
   levels.append(cols)
  for col in range(3):
   position=row*3+col;pal=NUM[position]
   name,door,star=(levels[k][col] for k in range(3))
   if not name.startswith(PALACES[position]):raise ValueError(('Original source palace mismatch',name,start))
   if pal==5:
    if '八神：' in name or not door.startswith('原盘单字：') or star:raise ValueError('Center must remain as printed, with no star/door/deity invented')
    god='';door=door.split('：',1)[1].strip()
    if not re.fullmatch(r'[乙丙丁戊己庚辛壬癸]',door):raise ValueError('Unrecognized original center stem')
   else:
    if '八神：' not in name or not door.startswith('门位：') or not star.startswith('星位：'):
     raise ValueError(('Source outer palace lacks literal items',name,door,star))
    god=name.split('八神：',1)[1].strip();door=door.split('：',1)[1].strip();star=star.split('：',1)[1].strip()
   cells.append((pal,y+col,name,god,door,star))
 if sorted(z[0] for z in cells)!=list(range(1,10)):raise ValueError('Actual original nine-palace chart incomplete')
 return cells

def evidence(lines,num,index,line):
 s=seg(lines,line)
 if num==1 and index==1:
  observed='生门与九天位于艮八宫；先前专家已经一致倾向第三设计方案'
  support='作者据生门为房屋、九天为高大，将东北主楼与专家已有意见对照'
  contrast='专家意见在作者分析前已经公开，不是独立新盘盲测'
 elif num==1 and index==2:
  observed='日干辛与时干甲午时所遁辛在坎一宫；太岁丁在兑宫；盘面伏吟'
  support='作者结合同宫、太岁生扶及伏吟作项目能成但进度缓慢的判断'
  contrast='伏吟只属传统术数解释，并不证明工程工期；太岁生助需人工核原盘细节'
 elif num==1 and index==3:
  observed='书内给出1995年策划、2001年才能开业的时间断词'
  support='作者提供具体年份，但原文没有解释推导算法'
  contrast='后续原书没有证明2001年实际开业，不能把预测当成功已验证'
 elif num==1:
  observed='书内给出投资八亿及完全建成十四亿两个数额，资金未到位'
  support='作者报告了投资、总成本及资金缺口的断语；反馈只确认计划八亿元、未筹款'
  contrast='十四亿元完工规模未获来源结果验证；数字取法没有原书证据，不得补造'
 elif index==1:
  observed='吴先生新墓地辛山乙向兼戌辰；王庆丰看了地形图及唯一实际原盘'
  support='原书只报告王庆丰认为景观很优秀却不能使用，没有逐宫方法说明'
  contrast='**无作者实际给出的取用神、宫位、格局、生克、应期理由**；不可自行编造'
 else:
  observed='作者表示墓地被前辈占有，吴先生得不到'
  support='原书只记判断和吴先生惊讶，并未提供地权或外部档案'
  contrast='**不存在作者书面完整分析链**；不能因故事称赞而补出未说的九宫证据'
 return {'step_number':index,'source_line':line,'source_end_line':line,
  'source_phase':'author_book_analysis_before_feedback','topic':STEP_TOPICS[num][index-1],
  'claimed_or_recorded_observation':observed,'source_grounded_argument_or_explicit_gap':support,
  'counterevidence_and_limits':contrast,'related_existing_concept_candidates_lexical_only':lex(s),
  'specific_old_concept_ids_human_verified':False,'source_original_preserved_in_full_sqlite':True,
  'independent_real_world_confirmation':False,'positive_training_eligible':False,
  'review_status':'source_grounded_draft_not_approved',
  'no_unwritten_author_logic_fabricated':True}

def cases_index(lines):
 out=[]
 for spec in CASES:
  n=spec['number'];border=spec['border']
  if not lines[spec['start']-1].startswith('实例'):raise ValueError('Missing full original case')
  if len(parse_chart(lines,border))!=9:raise ValueError('Missing printed original chart')
  steps=[evidence(lines,n,i,line) for i,line in enumerate(spec['step_lines'],1)]
  case_id=f'shenqi.geography.case{n:02d}'
  v={'case_number':n,'case_id':case_id,'event_family_id':case_id,'title':spec['title'],
   'source_span':[spec['start'],spec['end']],'printed_chart_line':border,'original_palace_count':9,
   'initial_question_line_numbers':spec['question_lines'],'author_analysis_steps':steps,
   'author_judgment_line_numbers':spec['judgment_lines'],'later_feedback_line_numbers':spec['feedback_lines'],
   'first_case_previous_expert_conclusion_known':bool(spec['prior_external_consensus']),
   'source_is_literary_claim_not_independent_geotechnical_evidence':True,'full_case_preserved':True,
   'case_book_default_outcome_label':'author_book_success_default','human_full_causal_chain_reviewed':False,
   'independent_verification':False,'positive_training_eligible':False}
  if n==1:
   v['limitations']=['三图仅同一项目方案，不新增事件或奇门盘','专家先选择第三方案，作者不是独立盲判','只确认计划投资8亿元及融资不足；2001开业和最终14亿无事后核实','原书未给出2001和14亿元具体应期或数理过程']
  else:
   v['limitations']=['第54—55行先谈另一癸山丁向墓地（无奇门盘），是同一次会话背景，不新建事件及盘','唯一奇门盘用于吴先生随后拟选辛山乙向墓地','原文只写最终断语，没有具体用神、宫位证据和推理顺序；不得编造完整链','墓地所谓已被他人占有未有土地权属文件独立证明']
  out.append(v)
 return out

def phase(db,cid,lines,a,b,typ,initial=False,override=None):
 original=override if override is not None else seg(lines,a,b)
 db.execute('''INSERT INTO historical_case_phase_events
  (case_id,source_start_line,source_end_line,phase,original_excerpt,metadata_json,visible_to_initial_blind_test)
  VALUES (?,?,?,?,?,?,?)''',(cid,a,b,typ,original,canon({'source_chapter':CHAPTER,'initially_available':bool(initial)}),int(initial)))

def import_one(db,lines,sid,case):
 num=case['case_number'];spec=CASES[num-1];cid=case['case_id'];border=spec['border']
 initial=seg(lines,17,23) if num==1 else seg(lines,56,58)
 verdict='\n'.join(seg(lines,n) for n in spec['judgment_lines'])
 fb='\n'.join(seg(lines,n) for n in spec['feedback_lines'])
 steps='\n\n'.join(seg(lines,n) for n in spec['step_lines'])
 db.execute('''INSERT INTO cases(case_id,section_id,event_family_id,domain_id,known_before,author_yongshen_steps,author_judgment,later_feedback,reviewed)
 VALUES (?,?,?,?,?,?,?,?,0)''',(cid,sid,cid,'geography_environment_historical_source',initial,steps,verdict,fb))
 db.execute('''INSERT INTO historical_case_protocol(case_id,completeness,published_chart_verification,feedback_independently_verified,
 eligible_blind_test,case_source_sha256,metadata_json)
 VALUES (?,'whole_source_event_with_one_printed_chart','literal_book_txt_not_independently_recast',0,0,?,?)''',
 (cid,SOURCE_SHA,canon(case)))
 db.execute('''INSERT INTO historical_geography_source_context
 (case_id,source_chart_line,cast_calendar_date,cast_hour_ganzhi,comparison_preknown,other_subquestion_without_chart,
 author_causal_steps_available,missing_causal_reason_warning,metadata_json)
 VALUES (?,?,?,?,?,?,?,?,?)''',
 (cid,border,spec['date'],spec['hour'],int(num==1),int(num==2),int(num==1),
 'Second story has no author-provided palace or evidence path for key outcome' if num==2 else 'Funding and year numbers lack stated source calculation and independent complete outcome',canon(case)))
 for p,line,label,dev,door,star in parse_chart(lines,border):
  db.execute('''INSERT INTO historical_chart_cells
 (case_id,palace,source_line,palace_label_raw,deity_raw,door_position_raw,star_position_raw,source_status)
 VALUES (?,?,?,?,?,?,?,'literal_geography_source_not_independently_recast')''',(cid,p,line,label,dev,door,star))
  middle=p==5
  db.execute('''INSERT INTO historical_palace_standardization
 (case_id,cast_key,palace,center_stem,source_of_center_stem,standard_deity,standard_door,standard_star,
 normalized_status,original_raw_integrity_checked,method_reference,derived_host_palace,derived_host_source)
 VALUES (?,?,?,?,?,?,?,?,?,1,?,?,?)''',
 (cid,'primary',p,door if middle else None,'original_center_literal' if middle else 'not_center',
 None if middle else dev,None if middle else door,None if middle else star,
 'center_literal_no_unprinted_door_star_god' if middle else 'original_outer_literally_preserved',
 'geography_original_source+shijia_qiju',2 if middle else None,
 'shijia_qiju:五宫寄坤二宫' if middle else None))
 for e in case['author_analysis_steps']:
  i=e['step_number'];source_line=e['source_line'];literal=seg(lines,source_line)
  db.execute('''INSERT INTO historical_case_reasoning
 (case_id,step_number,source_line,author_analysis_original,short_method_topic,metadata_json)
 VALUES (?,?,?,?,?,?)''',(cid,i,source_line,literal,e['topic'],canon(e)))
  db.execute('''INSERT INTO historical_case_reasoning_trace
 (case_id,step_number,source_line,evidence_json,review_status,positive_training_eligible)
 VALUES (?,?,?,?,'source_grounded_draft_not_approved',0)''',(cid,i,source_line,canon(e)))
  db.execute('''INSERT INTO semantic_assertions
 (chapter_key,concept_id,kind,relation,source_start_line,source_end_line,metadata_json,original_excerpt,review_status)
 VALUES (?,?,?,?,?,?,?,?,?)''',(CHAPTER,f'geography:case{num:02d}:step{i:02d}',
 'geography_historical_worked_case','source_step_draft_not_approved',source_line,source_line,canon(e),literal,'draft'))
 # Time order and independent assertion limits: no later feedback in initial input.
 phase(db,cid,lines,17,23,'initial_question',True) if num==1 else phase(db,cid,lines,56,58,'initial_question',True)
 if num==1:
  phase(db,cid,lines,19,19,'cast_metadata',False)
  phase(db,cid,lines,41,46,'initial_judgment',False)
  phase(db,cid,lines,47,49,'book_feedback',False)
 else:
  phase(db,cid,lines,53,55,'cast_metadata',False)
  phase(db,cid,lines,76,78,'initial_judgment',False)
  phase(db,cid,lines,79,81,'book_feedback',False)
 db.execute('''INSERT INTO historical_case_book_verdicts
 (event_family_id,primary_case_id,verdict,explicit_source_correction,source_correction_lines_json,
 feedback_source_lines_json,independent_external_verification,app_output_protocol,evidence_review_status,note)
 VALUES (?,?,'author_book_success_default',0,'[]',?,'not_verified','single_answer_for_one_cast','book_source_only',?)''',
 (cid,cid,canon(spec['feedback_lines']),
 'Case one book has partial contemporaneous confirmation only; no opening-year/cost confirmation.' if num==1 else
 'The source presents praise but gives no explicit palace-level reasoning or independent property-rights evidence.'))
 db.execute('''INSERT INTO historical_case_review_audit
 (case_id,original_steps,mechanical_step_trace,human_complete_step_chains,review_status,warning)
 VALUES (?,?,?,0,'source_grounded_draft_not_approved',?)''',
 (cid,len(spec['step_lines']),len(spec['step_lines']),
 'No full expert causal review; article conclusion must not masquerade as independent engineering evidence.'))

def compare_legacy(old,now):
 """Full original rows of ALL old tables must remain intact; no destructive migrations."""
 tables=[row[0] for row in old.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")]
 for table in tables:
  cols=[row[1] for row in old.execute('PRAGMA table_info("'+table+'")')]
  if not cols:raise ValueError('Legacy table columns absent '+table)
  select=','.join('"'+col+'"' for col in cols)
  was=list(old.execute('SELECT '+select+' FROM "'+table+'"'))
  nowset=set(now.execute('SELECT '+select+' FROM "'+table+'"'))
  if not all(row in nowset for row in was):raise ValueError('Changed old book row in table '+table)

def build(base,source,output,index_dir,migration):
 if output.exists():raise ValueError('Refusing to overwrite existing source database')
 if digest(base)!=BASE_SHA:raise ValueError('Incorrect entire 18-chapter baseline SHA')
 raw=Path(source).read_bytes()
 if hashlib.sha256(raw).hexdigest()!=SOURCE_SHA:raise ValueError('Original geography source SHA mismatch')
 lines=raw.decode('utf8').splitlines()
 if len(lines)!=81 or lines[0]!='第十五章' or lines[2]!='地理环境预测' or lines[12]!='第二节 实例解析(2例)':
  raise ValueError('Unexpected geography chapter structure')
 cases=cases_index(lines)
 if len(cases)!=2 or sum(len(c['author_analysis_steps']) for c in cases)!=6:raise ValueError('Original event/author steps truncated')
 output=Path(output);index_dir=Path(index_dir);migration=Path(migration)
 output.parent.mkdir(parents=True,exist_ok=True)
 with sqlite3.connect('file:'+str(base)+'?mode=ro',uri=True) as old,sqlite3.connect(output) as db:
  old.backup(db)
  db.executescript(migration.read_text('utf8'))
  db.execute('PRAGMA foreign_keys=ON')
  with db:
   if db.execute('SELECT 1 FROM sections WHERE section_key=?',(SECTION,)).fetchone():raise ValueError('Already present')
   db.execute('''INSERT INTO sections(book_id,section_key,title,original_text,sha256,content_version,reviewed)
 VALUES ('shenqi',?,?,?,?,1,0)''',(SECTION,'地理环境预测',raw.decode('utf8'),SOURCE_SHA))
   sid=db.execute('SELECT last_insert_rowid()').fetchone()[0]
   db.execute('''INSERT INTO chapter_knowledge(chapter_key,book_id,title,source_sha256,source_length_bytes,knowledge_version,review_status)
 VALUES (?,'shenqi','地理环境预测',?,?,'1','draft')''',(CHAPTER,SOURCE_SHA,len(raw)))
   for n,key,description in METHODS:
    meta={'source_line':n,'conditional_summary':description,'approved':False,'review_status':'draft'}
    db.execute('''INSERT INTO semantic_assertions
 (chapter_key,concept_id,kind,relation,source_start_line,source_end_line,metadata_json,original_excerpt,review_status)
 VALUES (?,?,?,?,?,?,?,?,?)''',(CHAPTER,'geography:general:'+key,'geography_source_method','historical_claim_only',n,n,canon(meta),seg(lines,n),'draft'))
   for case in cases:import_one(db,lines,sid,case)
   db.execute('''INSERT INTO chapter_archival_versions
 (archive_label,baseline_sha256,new_db_sha256,contains_complete_private_copyright_source,snapshot_type,created_utc,repo_public_archive_policy)
 VALUES (?, ?,NULL,1,'incremental_source_preserving','2026-10-20','user_explicitly_authorized_public_full_archive')''',
 ('shenqi_19_sections_93_whole_events',BASE_SHA))
  if db.execute('PRAGMA integrity_check').fetchone()[0]!='ok' or db.execute('PRAGMA foreign_key_check').fetchall():
   raise ValueError('SQLite integrity or FK failure')
  compare_legacy(old,db)
  expected={'sections':19,'cases':93,'historical_chart_cells':837,
   'historical_case_additional_cast_cells':63,'historical_case_additional_casts':7,
   'historical_case_reasoning':417,'semantic_assertions':1093+len(METHODS)+6,
   'historical_case_reasoning_trace':417,'historical_palace_standardization':900,
   'historical_geography_source_context':2}
  counts={t:db.execute('SELECT count(*) FROM "'+t+'"').fetchone()[0] for t in expected}
  for table,count in expected.items():
   if counts[table]!=count:raise ValueError(('Wrong counts',table,count,counts[table]))
  middles=db.execute('''SELECT count(*) FROM historical_palace_standardization
 WHERE palace=5 AND derived_host_palace=2 AND standard_deity IS NULL AND standard_door IS NULL AND standard_star IS NULL''').fetchone()[0]
  if middles!=100:raise ValueError(('Missing original 100 center palace records',middles))
  if db.execute("SELECT count(*) FROM historical_case_book_verdicts WHERE verdict='author_book_error_explicit'").fetchone()[0]!=5:
   raise ValueError('Old explicit author error records were modified')
  if db.execute('SELECT count(*) FROM historical_case_reasoning_trace WHERE positive_training_eligible=1').fetchone()[0]:
   raise ValueError('Premature approval of unreviewed case')
  db.execute('PRAGMA page_size=2048');db.execute('VACUUM');db.commit()
  if db.execute('PRAGMA integrity_check').fetchone()[0]!='ok' or db.execute('PRAGMA foreign_key_check').fetchall():
   raise ValueError('Final database invalid')
 index_dir.mkdir(parents=True,exist_ok=True)
 newsha=digest(output)
 for name,obj in {
  'chapter_manifest.json':{'schema':'wengua_geography_source_manifest_v1','chapter_key':CHAPTER,'source_sha256':SOURCE_SHA,'source_bytes':len(raw),'source_lines':len(lines),'source_print_chapter':'第十五章',
    'whole_events':2,'actual_printed_charts':2,'literal_original_palace_cells':18,'author_source_steps':6,
    'general_conditional_methods':len(METHODS),'new_semantic_assertions':len(METHODS)+6,
    'prior_external_expert_conclusion_known_before_author_reading':True,
    'second_case_no_documented_detailed_reasoning':True,'no_fabricated_first_cemetery_chart':True,
    'human_verified_chains':0,'independent_engineering_or_ownership_validation':False,
    'baseline_sha256':BASE_SHA,'archive_sha256':newsha,'counts':counts,'old_source_rows_unchanged':True},
  'case_index.json':{'schema':'wengua_geography_complete_source_events_v1','chapter_key':CHAPTER,'source_sha256':SOURCE_SHA,'cases':cases},
  'method_index.json':{'schema':'wengua_geography_conditioned_workflow_v1','chapter_key':CHAPTER,'source_sha256':SOURCE_SHA,
    'methods':[{'concept_id':'geography:general:'+key,'source_line':line,'conditional_summary':description,'review_status':'draft'} for line,key,description in METHODS],
    'study_process':['确认阳宅还是阴宅、当事人及土地关系；不能跨领域随意互换取用','阳宅先核日干本人、时干住宅及生门房屋死门土地、值符新宅值使旧宅，结合实际盘旺衰生克','阴宅先取死门及地盘死者天盘生者、星门神干上下生克、吉凶宫位级别','实际九宫宫位的门星神干与古籍以前章节五行生克、空墓伏吟等交叉核对，明确反证','必须先区分作者是否已听取其他专家结论、是否使用地形图以及真实起盘何时','如书中没有推理，必须明确返回证据链缺失而不是猜出作者未说的规则','书内反馈、项目投资计划、未来工程结果与土地权属独立验证分离','这只研究传统术数文献，不代替建筑设计、地质勘探、工程审查或土地登记']},
  'author_reasoning_evidence_index.json':{'schema':'wengua_geography_source_step_draft_v1','source_sha256':SOURCE_SHA,'count':6,
    'human_complete_chains_verified':0,'cases':[{'case_id':c['case_id'],'steps':c['author_analysis_steps']} for c in cases]},
  'source_audit.json':{'schema':'wengua_geography_source_anomalies_v1','source_sha256':SOURCE_SHA,
    'case1':{'prior_external_expert_result_line':19,'original_chart_line':26,'author_matching_expert_claim_line':41,'source_financing_confirmation_line':47,
      'opening_year_2001_not_confirmed':True,'final_14_hundred_million_cost_not_confirmed':True,'one_board_for_three_designs':True,'geomagnetic_field_claim_line':40,'scientifically_unverified':True},
    'case2':{'first_cemetery_dialogue_unprinted_qimen_chart_lines':[54,55],
      'subsequent_own_grave_question_line':56,'actual_qimen_cast_line':61,'no_author_palace_explanation_lines':[76,78],
      'source_ownership_not_independently_verified':True},
    'review_status':'draft_needs_human_review','no_new_chart_from_earlier_unprinted_cemetery':True}
 }.items():
  (index_dir/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 print(json.dumps({'new_db':str(output),'sha256':newsha,'counts':counts,'new_whole_events':2,'new_printed_charts':2,
  'new_author_source_steps':6,'new_method_candidates':len(METHODS),'legacy_unchanged':True,'source_sha256':SOURCE_SHA},ensure_ascii=False,indent=2))
 return 0

def main(argv=None):
 p=argparse.ArgumentParser()
 p.add_argument('--base',type=Path,required=True);p.add_argument('--source',type=Path,required=True)
 p.add_argument('--output',type=Path,required=True);p.add_argument('--index-dir',type=Path,required=True)
 p.add_argument('--migration',type=Path,default=ROOT/'schema/migrations/014_geography_source_context.sql')
 a=p.parse_args(argv)
 return build(a.base,a.source,a.output,a.index_dir,a.migration)
if __name__=='__main__':raise SystemExit(main())
