"""Add source-complete miscellaneous Shenqi history as five unsplit event families.

Preserves: real seven printed boards, all per-chart author steps, source phase chronology,
non-Qimen six-yao technique exclusion, after-the-fact reconstruction, unresolved claims.
Never mistake book correspondence for independent validation or human-reviewed reasoning.
"""
from __future__ import annotations
import argparse,hashlib,json,lzma,re,sqlite3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCE_SHA='8494bbf569b9bb18f8f505fb36a52d6ff327093f27b30240cf64ed455a89da93'
BASE_SHA='1332fe460c1e73bd74939760c59a376980c888bb8d9e41c3b7416fadd4bbdaa3'
SECTION='miscellaneous_prediction_ch17'
CHAPTER='shenqi/miscellaneous_prediction_ch17/v1'
PAL_NAMES=('巽4','离9','坤2','震3','中5','兑7','艮8','坎1','乾6')
PAL_NUM=(4,9,2,3,5,7,8,1,6)
# Each book example is ONE event. Three date/time charts for Olympic bid remain ONE event.
CASES=[
 {'n':1,'begin':5,'end':109,'title':'北京申办2000奥运会三时辰比较','initial':[7,7],
  'casts':[{'key':'primary','line':25,'date':'1993-03-07','hour':'庚戌','metadata':21,'steps':[44,46,48,50,52]},
           {'key':'bid_1993_09_23','line':56,'date':'1993-09-23','hour':'乙巳','metadata':54,'steps':[75,77,79]},
           {'key':'vote_1993_09_24','line':83,'date':'1993-09-24','hour':'癸丑','metadata':81,'steps':[102,104,106,108]}],
  'judgment':[9,52,79,108],'feedback':[15],'notes':'May28 letter used the SIX-YAO method; source gives no independent contemporaneous proof that three later Qimen readings were publicly committed before vote result.'},
 {'n':2,'begin':110,'end':142,'title':'黄永国写信询问学会、大楼与四月运气','initial':[112,114],
  'casts':[{'key':'primary','line':116,'date':'1996-05-16','hour':'丙辰','metadata':114,'steps':[135,137,139]}],
  'judgment':[135,137,139],'feedback':[141],'notes':'Society registration in March already happened by May question; other predictions must preserve incomplete feedback and prospective warning.'},
 {'n':3,'begin':143,'end':181,'title':'学术会议出席人数与会议组织','initial':[145,149],
  'casts':[{'key':'primary','line':151,'date':'1997-05-20','hour':'庚戌','metadata':149,'steps':[170,172,174,176]}],
  'judgment':[170,172,174,176],'feedback':[178,180],'notes':'110 participants already present at intermediate feedback line178; final 138+2 reported line180; do not leak intermediate into initial question.'},
 {'n':4,'begin':182,'end':248,'title':'餐桌高夫人临场判断及事后解盘','initial':[186,194],
  'casts':[{'key':'primary','line':218,'date':'1997-05-22','hour':'癸酉','metadata':216,'steps':[196,200,204,237,241,245]}],
  'judgment':[196,200,204],'feedback':[198,202,206],'notes':'Three in-person answers were before detailed source explanations. Sections 237-247 are explanations written after immediate responses; face-reading by another person is NOT this Qimen cast.'},
 {'n':5,'begin':249,'end':280,'title':'胡洪清听爆炸后预测原因与后果','initial':[251,253],
  'casts':[{'key':'primary','line':255,'date':'1997-11-03','hour':'辛未','metadata':253,'steps':[274,276]}],
  'judgment':[274,276],'feedback':[278],'notes':'Fatality and relationship allegations are a book account only, not verified police/medical evidence. Editor evaluation line280 is post outcome.'}
]
METHODS=[
(44,'chair_and_committee','申请选举按首领值符与值使官员分角色，不能无条件套到其他领域'),
(44,'home_earth_foreign_heaven','申奥以地盘时干为北京、天盘时干为外国城市，仅针对作者该案例'),
(46,'earth_chair_support','地盘时干与值符同宫，作者取领导支持作为证据'),
(48,'heaven_chair_and_members','天盘时干宫生值符、克值使宫与月令共同判断主客优势'),
(50,'fanyin_momentum','八门反吟与天盘地盘旺衰并用判断半途不利'),
(75,'earth_yi_tomb','第二盘地盘乙在坤入墓且与值使对冲，尽管同值符仍需保留不利'),
(77,'heaven_yi_in_season','第二盘天盘乙旺相并受值符值使生助，取多证据优劣'),
(102,'third_board_home','第三盘癸地盘在艮，与值符比和但酉月休地'),
(104,'third_board_guest','第三盘癸天盘在兑当旺，值使虽然克但月令使克弱'),
(106,'ticket_ding','第三盘以丁奇为选票，结合天盘/地盘时干克丁宫的不同关系'),
(135,'association_star','大事以九星值符兼螣蛇生门取象，但学会已注册属当时已知历史'),
(137,'building_open_door','楼宇建设以开门取用，检查入墓空亡、格局与时干事体'),
(139,'monthly_caution','近期以日月干、支宫、惊门及出空推作者提示时间，未证实的警告不能记应验'),
(170,'attendance_hour_open','开门为大会、时干为参会人，月令旺相和宫数合参人数'),
(172,'host_support_issues','东道主日干结合值符、庚阻隔、门克宫及反吟判断支持与阻力'),
(174,'leader_support_void','年干领导虽生东道主，但空亡惊门提示仅口头支持'),
(176,'documents_ding','会议材料取丁奇，空亡丁癸雀投江和宫数推待办文件'),
(239,'seller_rain_liquor','日干甲子戊财、休门与空亡开门辨离职经商，坎水丁火取烟酒'),
(243,'inventory_profit','资本戊、利息生门、时干货物、杜门伏吟组合判断亏损积压'),
(247,'seat_personal_event','坐震宫、伤门及丁癸与已知昨天癸亥共同形成传统眼泪类象'),
(274,'blast_tianchong','偶发爆炸依震动类象以天冲为用神，连同震坤、门神、干格解析'),
(276,'fatality_dead_gate','死门为死者，乾六宫、星门神与丁奇推原书关系；不可认定犯罪事实'),
(280,'flexible_selection_editor','作者事后评语鼓励按象数理灵活选用神，须标记是后验编辑按语')
]

def canon(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'))
def segment(lines,a,b=None):
 b=a if b is None else b
 if not 1<=a<=b<=len(lines):raise ValueError('Source line out of bounds')
 return '\n'.join(lines[a-1:b])
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def parse_chart(lines,start):
 """Genuine original four-layer compact table, not later 3-layer normalized format."""
 if not lines[start-1].startswith('┌'):raise ValueError('Not an actually printed board')
 result=[]
 for row in range(3):
  y=start+1+row*5
  layers=[]
  for z in range(4):
   vals=[v.strip() for v in lines[y+z-1].split('│')[1:-1]]
   if len(vals)!=3:raise ValueError(('Not three original palace columns',start,row,z))
   layers.append(vals)
  for col in range(3):
   idx=row*3+col;pal=PAL_NUM[idx]
   name,deity,door,star=[lay[col] for lay in layers]
   if name!=PAL_NAMES[idx]:raise ValueError(('Original palace label wrong',start,name,PAL_NAMES[idx]))
   if pal==5:
    if deity or star or not re.fullmatch('[乙丙丁戊己庚辛壬癸]',door):
     raise ValueError(('Center literal cannot be fabricated',start,door))
   elif not deity or not door or not star:
    raise ValueError('Missing ORIGINAL peripheral text')
   result.append((pal,y+col,name,deity,door,star))
 if sorted(x[0] for x in result)!=list(range(1,10)):raise ValueError('Not 9 distinct source palaces')
 return result

def lexical(t):
 ids=[]
 for x in '开休生伤杜景死惊':
  if x+'门' in t or any(x==t[i] for i in range(len(t)) if i+1<len(t) and t[i+1] in '庚辛壬癸戊己乙丙丁'):
   ids.append('door:'+x)
 for x in '蓬任冲辅英芮柱心禽':
  if '天'+x in t:ids.append('star:'+x)
 for x in ['玄武','白虎','九天','九地','六合','太阴','螣蛇','值符']:
  if x in t:ids.append('deity:'+x)
 for x in '乾坤巽离震兑艮坎':
  if x+'宫' in t or x in ('巽','艮') and x+'4' in t:ids.append('trigram:'+x)
 return sorted(set(ids))

def case_index(lines):
 items=[]
 for spec in CASES:
  n=spec['n'];cid=f'shenqi.misc.case{n:02d}'
  if not lines[spec['begin']-1].startswith('实例'):raise ValueError(('Missing story',n))
  casts=[];steps=[]
  for cast in spec['casts']:
   cells=parse_chart(lines,cast['line'])
   for s in cast['steps']:
    is_numbered=bool(re.match(r'^（\d+）',lines[s-1]))
    if not is_numbered and not (n==1 and s in [52,79,108] or n==4 and s in [196,200,204,237,241,245]):
     raise ValueError(('Unexpected nonnumbered step',n,s))
    phase=('Qimen_retrospective_as_book_explanation_not_contemporaneous_proof' if n==1 else
      'post_feedback_explanatory_analysis' if n==4 and s in [237,241,245] else
      'initial_live_prediction' if n==4 else 'source_authored_step')
    end_line=s+2 if n==4 and s in [237,241,245] else s
    original=segment(lines,s,end_line)
    step={'source_end_line':end_line,'step_number':len(steps)+1,'source_line':s,'cast_key':cast['key'],'phase':phase,
     'author_method_claim':original[:95] if is_numbered else original[:75],
     'source_claimed_observations':[v.strip() for v in re.split('[，；。]',original) if any(y in v for y in ('宫','星','门','生','克','值符','时干','日干','月令','九宫'))][:9],
     'source_counterevidence':[v.strip() for v in re.split('[，；。]',original) if any(y in v for y in ('虽然','但是','但','不','休','空亡','反吟'))][:8],
     'prior_concept_lexical_candidates_only':lexical(original),
     'causal_relation_human_validated':False,'author_original_in_full_sqlite':True,
     'positive_training_eligible':False,'review_status':'source_anchored_draft_requires_human_step_check'}
    if n==2 and s==135:step['prior_historical_result_within_source_step']=True
    steps.append(step)
   casts.append({'key':cast['key'],'source_chart_line':cast['line'],'date':cast['date'],
     'hour':cast['hour'],'source_cast_metadata_line':cast['metadata'],
     'source_analysis_lines':cast['steps'],'real_original_cells':len(cells)})
  item={'case_number':n,'case_id':cid,'event_family_id':cid,'title':spec['title'],
   'whole_original_story_line_span':[spec['begin'],spec['end']],'source_casts':casts,
   'source_analysis_steps':steps,'initial_question_source_lines':spec['initial'],
   'judgment_lines':spec['judgment'],'feedback_lines':spec['feedback'],
   'source_note':spec['notes'],'professionally_approved':False,'positive_training_eligible':False}
  if n==1:item['six_yao_claim_not_qimen_cast']={'book_lines':[7,9,19], 'other_technique':True,
    'author_book_only_says_later_qimen_analysis':True,'no_proof_contemporaneous_qimen_prediction':True,
    'one_event_three_separate_real_printed_qimen_casts':True}
  if n==2:item['three_questions_one_event']=True
  if n==3:item['interim_known_participants_at_line178']=True
  if n==4:item['live_predictions_before_written_reconstruction']={'initial_lines':[196,200,204],
    'explanation_after_revealed_feedback':[239,243,247],'another_person_face_reading_not_qimen':True}
  if n==5:item['teacher_retrospective_commentary_line']=280
  items.append(item)
 return items

def phase(db,cid,lines,a,b,kind,visible=False,text=None,cast_key='primary'):
 raw=text if text is not None else segment(lines,a,b)
 db.execute('''INSERT INTO historical_case_phase_events
 (case_id,source_start_line,source_end_line,phase,original_excerpt,metadata_json,visible_to_initial_blind_test)
 VALUES (?,?,?,?,?,?,?)''',(cid,a,b,kind,raw,canon({'cast_key':cast_key,'source_chapter':CHAPTER,'source_only':True}),int(visible)))

def add_case(db,lines,sid,item):
 n=item['case_number'];spec=CASES[n-1];cid=item['case_id']
 known='\n'.join(segment(lines,a) for a in spec['initial'])
 if n==1:known=segment(lines,7)  # do NOT leak line9's already-claimed six-yao prediction into question
 if n==3:known=segment(lines,145,149)
 if n==4:known=segment(lines,186,194)  # spouse identity disclosed before three in-person claims
 # No result in initial stimulus. Later teacher/editor outcome must remain separate.
 first_steps='\n\n'.join(segment(lines,s['source_line'],s['source_end_line']) for s in item['source_analysis_steps'])
 judgment='\n'.join(segment(lines,x) for x in spec['judgment'])
 feedback='\n'.join(segment(lines,x) for x in spec['feedback'])
 db.execute('''INSERT INTO cases(case_id,section_id,event_family_id,domain_id,known_before,
 author_yongshen_steps,author_judgment,later_feedback,reviewed) VALUES (?,?,?,?,?,?,?,?,0)''',
 (cid,sid,cid,'miscellaneous_historical_source',known,first_steps,judgment,feedback))
 db.execute('''INSERT INTO historical_case_protocol(case_id,completeness,published_chart_verification,
 feedback_independently_verified,eligible_blind_test,case_source_sha256,metadata_json)
 VALUES (?,'complete_book_story_all_real_printed_charts','book_literal_not_independently_recast',0,0,?,?)''',
 (cid,SOURCE_SHA,canon(item)))
 for ci,cast in enumerate(spec['casts']):
  key=cast['key']
  if ci:
   db.execute('''INSERT INTO historical_case_additional_casts(case_id,cast_key,
   cast_datetime_description,calendar_date,hour_ganzhi,source_chart_start,notes)
   VALUES (?,?,?,?,?,?,?)''',(cid,key,cast['date']+' '+cast['hour'],cast['date'],cast['hour'],cast['line'],
    'A genuinely printed original Qimen board of the SAME Olympic bid event, not a separate success sample'))
  db.execute('''INSERT INTO historical_misc_cast_context(case_id,cast_key,source_chart_line,
  case_phase,original_question_and_method,retrospective_qimen_provenance_unverified,
  additional_non_qimen_casts_count,metadata_json)
  VALUES (?,?,?,?,?,?,?,?)''',(cid,key,cast['line'],
   'narrated_multi_time_history' if n==1 else 'single_book_study_board',
   'six-yao discussion plus later Qimen explanation' if n==1 else 'original source case',
   int(n==1),3 if n==1 else 0,canon(item['source_casts'][ci])))
  for pal,ln,label,god,door,star in parse_chart(lines,cast['line']):
   if not ci:
    db.execute('''INSERT INTO historical_chart_cells(case_id,palace,source_line,palace_label_raw,
     deity_raw,door_position_raw,star_position_raw,source_status)
     VALUES (?,?,?,?,?,?,?,'book_literally_printed_not_recast')''',(cid,pal,ln,label,god,door,star))
   else:
    db.execute('''INSERT INTO historical_case_additional_cast_cells(case_id,cast_key,palace,
     source_line,palace_label_raw,deity_raw,door_position_raw,star_position_raw)
     VALUES (?,?,?,?,?,?,?,?)''',(cid,key,pal,ln,label,god,door,star))
   center=pal==5
   db.execute('''INSERT INTO historical_palace_standardization(case_id,cast_key,palace,center_stem,
    source_of_center_stem,standard_deity,standard_door,standard_star,normalized_status,
    original_raw_integrity_checked,method_reference,derived_host_palace,derived_host_source)
    VALUES (?,?,?,?,?,?,?,?,?,1,?,?,?)''',(
    cid,key,pal,door if center else None,'original_center_literal' if center else 'not_center',
    None if center else god,None if center else door,None if center else star,
    'original_compact_center_without_fabricated_deity_door_star' if center else 'source_literal_compact_chart',
    'miscellaneous_source+shijia_qiju',2 if center else None,
    'shijia_qiju:五宫寄坤二宫' if center else None))
 for step in item['source_analysis_steps']:
  nstep=step['step_number'];ln=step['source_line'];literal=segment(lines,ln,step['source_end_line'])
  db.execute('''INSERT INTO historical_case_reasoning(case_id,step_number,source_line,
   author_analysis_original,short_method_topic,metadata_json) VALUES (?,?,?,?,?,?)''',
   (cid,nstep,ln,literal,step['phase'],canon(step)))
  db.execute('''INSERT INTO historical_case_reasoning_trace(case_id,step_number,source_line,
   evidence_json,review_status,positive_training_eligible)
   VALUES (?,?,?,?,'source_anchored_draft_requires_human_step_check',0)''',
   (cid,nstep,ln,canon(step)))
  db.execute('''INSERT INTO semantic_assertions(chapter_key,concept_id,kind,relation,
   source_start_line,source_end_line,metadata_json,original_excerpt,review_status)
   VALUES (?,?,?,?,?,?,?,?,?)''',
   (CHAPTER,f'misc:case{n:02d}:step{nstep:02d}','misc_historical_worked_case',
    'book_source_analysis_not_approved',ln,step['source_end_line'],canon(step),literal,'draft'))
 phase(db,cid,lines,spec['initial'][0],spec['initial'][-1],'initial_question',n!=1,text=known)
 if n==1:
  phase(db,cid,lines,9,9,'cast_metadata',False,cast_key='non_qimen_sixyao_letter')
  phase(db,cid,lines,15,15,'book_feedback')
  for cast in spec['casts']:
   phase(db,cid,lines,cast['metadata'],cast['metadata'],'cast_metadata',False,cast_key=cast['key'])
   phase(db,cid,lines,cast['steps'][-1],cast['steps'][-1],'retrospective_author_explanation',False,cast_key=cast['key'])
 elif n==2:
  phase(db,cid,lines,135,139,'initial_judgment')
  phase(db,cid,lines,141,141,'book_feedback')
 elif n==3:
  phase(db,cid,lines,170,176,'initial_judgment')
  phase(db,cid,lines,178,178,'new_disclosure')
  phase(db,cid,lines,180,180,'book_feedback')
 elif n==4:
  for ln in [196,200,204]:phase(db,cid,lines,ln,ln,'initial_judgment')
  for ln in [198,202,206]:phase(db,cid,lines,ln,ln,'book_feedback')
  for ln in [237,241,245]:phase(db,cid,lines,ln,ln+2,'retrospective_author_explanation')
 else:
  phase(db,cid,lines,274,276,'initial_judgment')
  phase(db,cid,lines,278,278,'book_feedback')
  phase(db,cid,lines,280,280,'editor_posthoc_correction')
 verdict='author_book_success_default'
 db.execute('''INSERT INTO historical_case_book_verdicts(event_family_id,primary_case_id,verdict,
  explicit_source_correction,source_correction_lines_json,feedback_source_lines_json,
  independent_external_verification,app_output_protocol,evidence_review_status,note)
  VALUES (?,?,'author_book_success_default',0,'[]',?,'not_verified','single_answer_for_one_cast','book_source_only',?)''',
  (cid,cid,canon(spec['feedback']),
   'Book literary account only; cannot independently certify election/Qimen prediction' if n==1 else
   'Forecast and prior feedback are source assertions only; partial outcomes do not validate all predictions'))
 db.execute('''INSERT INTO historical_case_review_audit(case_id,original_steps,mechanical_step_trace,
 human_complete_step_chains,review_status,warning)
 VALUES (?,?,?,0,'source_anchored_draft_requires_human_step_check',?)''',
 (cid,len(item['source_analysis_steps']),len(item['source_analysis_steps']),spec['notes']))

def compare_legacy(old,updated):
 for (table,) in old.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"):
  cols=[c[1] for c in old.execute('PRAGMA table_info("'+table+'")')]
  names=','.join('"'+c+'"' for c in cols)
  old_rows=list(old.execute('SELECT '+names+' FROM "'+table+'"'))
  new_rows=set(updated.execute('SELECT '+names+' FROM "'+table+'"'))
  if not all(row in new_rows for row in old_rows):raise ValueError('Old table source changed: '+table)

def build(base,source,output,index_dir,migration):
 base=Path(base);source=Path(source);output=Path(output);index_dir=Path(index_dir);migration=Path(migration)
 if output.exists():raise ValueError('Never overwrite a previously archived SQLite snapshot')
 if sha(base)!=BASE_SHA:raise ValueError('Wrong complete 20 chapter SQLite baseline SHA')
 raw=source.read_bytes()
 if hashlib.sha256(raw).hexdigest()!=SOURCE_SHA:raise ValueError('Wrong original miscellaneous source SHA')
 lines=raw.decode('utf8').splitlines()
 if len(lines)!=280 or lines[0]!='第十七章 其他杂项预测' or lines[2]!='第一节 实例解析（5例）':raise ValueError('Original chapter changed')
 items=case_index(lines)
 if len(items)!=5 or sum(len(x['source_casts']) for x in items)!=7 or sum(len(x['source_analysis_steps']) for x in items)!=27:
  raise ValueError('Case family / printed chart / author step lost')
 output.parent.mkdir(parents=True,exist_ok=True)
 with sqlite3.connect('file:'+str(base)+'?mode=ro',uri=True) as old,sqlite3.connect(output) as db:
  old.backup(db);db.executescript(migration.read_text('utf8'));db.execute('PRAGMA foreign_keys=ON')
  with db:
   if db.execute('SELECT 1 FROM sections WHERE section_key=?',(SECTION,)).fetchone():raise ValueError('Duplicate original book section')
   db.execute('''INSERT INTO sections(book_id,section_key,title,original_text,sha256,content_version,reviewed)
   VALUES ('shenqi',?,?,?,?,1,0)''',(SECTION,'其他杂项预测',raw.decode('utf8'),SOURCE_SHA))
   sid=db.execute('SELECT last_insert_rowid()').fetchone()[0]
   db.execute('''INSERT INTO chapter_knowledge(chapter_key,book_id,title,source_sha256,
    source_length_bytes,knowledge_version,review_status)
    VALUES (?,'shenqi','其他杂项预测',?,?,'1','draft')''',(CHAPTER,SOURCE_SHA,len(raw)))
   for ln,key,description in METHODS:
    m={'source_line':ln,'conditional_method':description,
       'source_specific_restriction':'No universal miscellaneous yongshen; case by case role and topic',
       'positive_training_eligible':False}
    db.execute('''INSERT INTO semantic_assertions(chapter_key,concept_id,kind,relation,
    source_start_line,source_end_line,metadata_json,original_excerpt,review_status)
    VALUES (?,?,?,?,?,?,?,?,?)''',
    (CHAPTER,'misc:method:'+key,'topic_specific_source_method','book_only_conditional_study',
     ln,ln,canon(m),segment(lines,ln),'draft'))
   for item in items:add_case(db,lines,sid,item)
   db.execute('''INSERT INTO chapter_archival_versions(archive_label,baseline_sha256,new_db_sha256,
   contains_complete_private_copyright_source,snapshot_type,created_utc,repo_public_archive_policy)
   VALUES (?, ?,NULL,1,'incremental_source_preserving','2026-10-20','user_explicitly_authorized_public_full_archive')''',
   ('shenqi_21_sections_103_whole_events',BASE_SHA))
  if db.execute('PRAGMA integrity_check').fetchone()[0]!='ok' or db.execute('PRAGMA foreign_key_check').fetchall():raise ValueError('New archive integrity problem')
  compare_legacy(old,db)
  expected={'sections':21,'cases':103,'historical_chart_cells':927,
   'historical_case_additional_cast_cells':81,'historical_case_additional_casts':9,
   'historical_case_reasoning':495,'historical_case_reasoning_trace':495,
   'historical_palace_standardization':1008,'semantic_assertions':1207+len(METHODS)+27,
   'historical_misc_cast_context':7}
  actual={table:db.execute('SELECT count(*) FROM "'+table+'"').fetchone()[0] for table in expected}
  if actual!=expected:raise ValueError(('Unexpected historical source counts',actual,expected))
  centers=db.execute('''SELECT count(*) FROM historical_palace_standardization WHERE palace=5 AND
  derived_host_palace=2 AND standard_deity IS NULL AND standard_door IS NULL AND standard_star IS NULL''').fetchone()[0]
  if centers!=112:raise ValueError(('Missing or fabricated source center fields',centers))
  if db.execute("SELECT count(*) FROM historical_case_book_verdicts WHERE verdict='author_book_error_explicit'").fetchone()[0]!=6:
   raise ValueError('Old source explicit error verdict reclassified')
  if db.execute('SELECT count(*) FROM historical_case_reasoning_trace WHERE positive_training_eligible=1').fetchone()[0]:
   raise ValueError('Training gate violated')
  db.execute('PRAGMA page_size=2048');db.execute('VACUUM');db.commit()
  if db.execute('PRAGMA integrity_check').fetchone()[0]!='ok' or db.execute('PRAGMA foreign_key_check').fetchall():raise ValueError('Final SQLite corrupt')
 index_dir.mkdir(parents=True,exist_ok=True)
 doc={'schema':'wengua_misc_full_source_archive_v1','chapter_key':CHAPTER,'source_title':'其他杂项预测',
 'source_sha256':SOURCE_SHA,'source_bytes':len(raw),'source_lines':len(lines),
 'book_original_chapter_number':17,'project_chapter_count':21,'event_families':5,'real_printed_charts':7,
 'source_palace_cells':63,'source_analysis_and_judgment_units':27,'conditional_method_candidates':len(METHODS),
 'new_semantic_candidates':len(METHODS)+27,'independent_author_proof_of_predictions':False,
 'human_complete_reasoning_approved':0,'all_previous_source_rows_preserved':True,
 'base_sha256':BASE_SHA,'database_sha256':sha(output),'counts':actual,
 'unique_issue_olympic_same_event_three_qimen_boards':True,
 'other_method_sixyao_book_letter_not_contemporaneous_qimen_proof':True,
 'case4_predictions_before_posthoc_explanation':True,'case5_post_event_editor_comment_separate':True}
 (index_dir/'chapter_manifest.json').write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 (index_dir/'case_index.json').write_text(json.dumps({'schema':'wengua_misc_cases_v1','source_sha256':SOURCE_SHA,'cases':items},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 (index_dir/'method_index.json').write_text(json.dumps({'schema':'wengua_misc_topic_methods_v1','source_sha256':SOURCE_SHA,
   'methods':[{'source_line':ln,'concept_id':'misc:method:'+key,'conditional_summary':desc,'review_status':'draft'} for ln,key,desc in METHODS]},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 (index_dir/'source_audit.json').write_text(json.dumps({'schema':'wengua_misc_source_phase_audit_v1','source_sha256':SOURCE_SHA,
  'case1_original_1993_letter_is_sixyao_not_three_contemporaneous_qimen_proven':True,
  'case1_three_qimen_cast_lines':[25,56,83],'case2_multiple_questions_not_multiple_cases':True,
  'case3_meeting_attendance_book_result_138_plus_2_not_verified_outside_book':True,
  'case4_interviewer_identity_known_before_prediction':True,'case4_unwritten_explanations_after_feedback':True,
  'case5_retrospective_commentary_line':280,'zero_independently_validated_causal_chains':True,
  'all_positive_training_forbidden':True},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 return doc

def main():
 p=argparse.ArgumentParser();p.add_argument('--base',required=True);p.add_argument('--source',required=True)
 p.add_argument('--output',required=True);p.add_argument('--index-dir',required=True)
 p.add_argument('--migration',default=str(ROOT/'schema/migrations/016_misc_cast_context.sql'))
 a=p.parse_args();print(json.dumps(build(a.base,a.source,a.output,a.index_dir,a.migration),ensure_ascii=False,indent=2))
if __name__=='__main__':main()
