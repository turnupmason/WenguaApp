"""Incremental immutable-history sports chapter archive builder (stdlib only).

The traditional divination in the source is historical text, not validated
sports prediction. Never use later match results to enrich initial inputs.
"""
from __future__ import annotations
import argparse, hashlib, json, lzma, re, sqlite3
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
SOURCE_HASH='784f49224b8a540850dde469a0fe720d23ee4ab551fa9600dca6137eb4fb5a2b'
BASE_HASH='44efe2ed11023c763558f3eabd4cc98f55c515482515d89a78a7641cdb1fde4e'
SECTION='sports_competition_prediction_ch12'
CHAPTER='shenqi/sports_competition_prediction_ch12/v1'
PALACES=('巽四宫','离九宫','坤二宫','震三宫','中五宫','兑七宫','艮八宫','坎一宫','乾六宫')
NUM=(4,9,2,3,5,7,8,1,6)
# Start, end, chart border, all original author's analysis steps, known-before, predicted, feedback.
CASES=[
 (11,47,22,[38,40,42],[13,15,17,19],[44],[46],'1995世界乒乓女团中国韩国决赛'),
 (48,88,61,[56,77,79,81,83],[50,52,54],[56,85],[87],'1995世界乒乓男团中国瑞典决赛'),
 (89,135,98,[114,116,118,120,122,124,126,128,130,132],[91,93,95],[132],[134],'1995世乒男子单打孔令辉刘国良号码比较'),
 (136,166,145,[161,163],[138,140,142],[163],[165],'1996亚特兰大奥运会中国队金牌数'),
 (167,203,178,[194,196,198],[169,171,173,175],[200],[202],'1998巴西荷兰世界杯半决赛'),
 (204,238,213,[229,231,233],[206,208,210],[235],[237],'1998法国克罗地亚世界杯半决赛'),
 (239,276,248,[264,266,268,270,272,274],[241,243,245],[270,272,274],[276],'1998法国巴西世界杯决赛'),
]
METHODS=[
 (7,'referee_zhifu','值符代表裁判'),
 (7,'athlete_day_hour','日干或时干可作运动员候选，依问事明确选择'),
 (7,'home_ground_day_hour','主队取地盘日干或时干，不能无条件假设任一方为主队'),
 (7,'away_heaven_day_hour','客队取天盘日干或时干，必须先说明主客依据'),
 (7,'palace_strength','比较用神落宫旺相休囚与时令'),
 (7,'auspicious_patterns','比较双方格局吉凶，不能单凭一门断胜负'),
 (7,'mutual_promotion_restriction','分析主客落宫五行相生相克'),
 (7,'equipment_geng','庚为比赛器械'),
 (7,'medal_xin','辛为金牌'),
 (7,'coach_jing','景门为技术指导'),
 (7,'multi_evidence','应综合值符、门星神、时令与干加干及金牌多个证据'),
]
TOPICS=[
 ['主队以地盘时壬艮宫，裁判、教练、天英星与巳月加权','客队以天盘时壬兑宫，门星助强但巳月克金','金牌辛天地盘宫克比较判主队'],
 ['甲戌时星门伏吟比和判9点前势均力敌；只有文字未印原盘','乙亥时地盘乙主中国队离宫值符开门吉，兼看月令','乙亥时天盘乙客瑞典巽宫受惊门九天及乙辛凶格','金牌辛地盘天盘宫比和，另用门神取舍','技术指导景门与主客宫关系、时令比较'],
 ['两名中国选手无法分传统主客，以背号113、114取宫数候选','宫数3和4五行比和；旧格门星神多冲突仍难定胜负','改以伤门孔令辉、杜门刘国良为八门候选','伤门兑宫与丁戊青龙转光评估孔令辉','杜门乾宫庚乙太白逢星评估刘国良','八门二宫比和反吟仍不分胜负','改以天冲星孔令辉、天辅星刘国良取九星','孔令辉天冲星坤宫生门九地奇诈结构','刘国良天辅星兑宫伤门九天与丁戊','结合巳月火旺生坤土克兑金，九星候选偏孔令辉'],
 ['地盘时干主中国队坎宫见金牌辛开门值符，天任相反','坎水一六数给十枚或十六枚双候选'],
 ['海外中立场地须按距离确定荷兰主巴西客','荷兰主地盘辛艮宫值符但入墓天蓬衰与失球数候选','巴西客天盘辛震宫休门九天及木克土得胜'],
 ['法国东道主取地盘时壬兑宫，值符但伤门被宫克','客克罗地亚天盘时壬坎宫景门火入水乡','作者初断兑金生坎水并取兑二坎一数给客胜2比1'],
 ['法国东道主与巴西客队身份区分','法国地盘时丙兑宫值符休门','巴西天盘时丙震宫白虎景门','未月主兑金旺克震木休囚，断主法国胜','天柱星与天冲星宫克、木数三推3比0','金牌辛地盘与天盘对主客生克，推卫冕失败'],
]
assert sum(len(c[3]) for c in CASES)==sum(len(x) for x in TOPICS)==32

def sj(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'))
def segment(lines,a,b=None):
 b=b or a
 if not 1<=a<=b<=len(lines):raise ValueError(('out_of_source',a,b))
 return '\n'.join(lines[a-1:b])
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def chart(lines,start):
 if not lines[start-1].startswith('┌'):raise ValueError(('chart_start_missing',start))
 ans=[]
 for row in range(3):
  head=start+1+4*row
  triple=[]
  for delta in range(3):
   fields=[v.strip() for v in lines[head+delta-1].split('│')[1:-1]]
   if len(fields)!=3:raise ValueError(('chart_column_incomplete',start,row,delta))
   triple.append(fields)
  for col in range(3):
   k=row*3+col;no=NUM[k]
   name,door,star=(triple[z][col] for z in range(3))
   if not name.startswith(PALACES[k]):raise ValueError(('palace_wrong',start,name,PALACES[k]))
   if no==5:
    if '八神：' in name or not door.startswith('中宫原字：') or star:
     raise ValueError(('center_not_literal',start,door))
    deity='';door=door.split('：',1)[1]
    if not re.fullmatch('[乙丙丁戊己庚辛壬癸]',door):raise ValueError('Unclear centre stem')
   else:
    if '八神：' not in name or not door.startswith('门位：') or not star.startswith('星位：'):
     raise ValueError(('peripheral_incomplete',start,name,door,star))
    deity=name.split('八神：',1)[1].strip();door=door.split('：',1)[1].strip();star=star.split('：',1)[1].strip()
   ans.append((no,head+col,name,deity,door,star))
 if sorted(x[0] for x in ans)!=list(range(1,10)):raise ValueError('palace_duplicate')
 return ans

def lex(s):
 a=[]
 for n in '开休生伤杜景死惊':
  if n+'门' in s:a.append('door:'+n)
 for n in '蓬任冲辅英芮柱心禽':
  if '天'+n in s:a.append('star:'+n)
 for n in ('玄武','白虎','九天','九地','六合','太阴','螣蛇','值符'):
  if n in s:a.append('deity:'+n)
 for n in '乾坤震巽坎离艮兑':
  if n+'宫' in s:a.append('trigram:'+n)
 return sorted(set(a))

def phase_for(i,n):
 if i==2 and n==56:return 'unprinted_initial_cast_author_judgment'
 if i==3 and n in (114,116):return 'candidate_palace_number'
 if i==3 and n in (118,120,122,124):return 'candidate_eight_gates'
 if i==3 and n in (126,128,130,132):return 'final_nine_stars_choice'
 return 'initial_original_author_analysis'

def candidate_trace(lines,i,k,n,topic):
 t=lines[n-1]
 clauses=[x.strip() for x in re.split('[，；。]',t) if x.strip()]
 valid=[x for x in clauses if any(v in x for v in ('宫','门','星','干','时令','值符','克','生','伏吟','反吟','比和','旺','凶','吉','辛','庚'))]
 contra=[x for x in clauses if any(v in x for v in ('但','却','不过','不利','难分','凶','反','未必','虽然','仍不'))]
 return {'step_number':k,'source_line':n,'topic':topic,'stage':phase_for(i,n),
 'source_claimed_evidence_fragments':valid,'source_claimed_counterevidence_fragments':contra,
 'cross_chapter_lexical_concepts_unverified':lex(t),
 'actual_author_step_in_private_original':True,'full_causal_chain_human_reviewed':False,
 'printed_source_recast_independently_verified':False,'positive_training_eligible':False}

def make_indexes(lines):
 cases=[];steps=[]
 for i,(start,end,chartline,stepnums,question,judgment,feedback,title) in enumerate(CASES,1):
  if not lines[start-1].startswith('实例'):raise ValueError(('missing_story',i,start))
  chart(lines,chartline)
  a=[]
  for k,n in enumerate(stepnums,1):
   if not (lines[n-1].startswith('(') or (i==2 and n==56) or i==3 or i==7):raise ValueError(('not_author_analysis',i,n))
   item={'step_number':k,'source_line':n,'topic':TOPICS[i-1][k-1],
     'stage':phase_for(i,n),'prior_concept_candidate_ids':lex(lines[n-1]),'review_status':'source_anchored_draft',
     'positive_training_eligible':False}
   a.append(item);steps.append(item)
  cid=f'shenqi.sports.case{i:02d}'
  item={'case_number':i,'case_id':cid,'event_family_id':cid,'title':title,'original_chapter_source_span':[start,end],
  'printed_chart_start':chartline,'only_source_printed_charts':1,'source_author_analysis_lines':stepnums,
  'source_question_lines':question,'source_original_prediction_lines':judgment,'source_feedback_lines':feedback,
  'author_source_steps':a,'book_outcome':'author_book_error_explicit' if i==6 else 'author_book_success_default',
  'independent_sports_prediction_verified':False,'source_printed_original_independently_recast':False,'whole_case_unsplit':True}
  if i==2:item['unprinted_first_cast']={'time':'1995-05-08 甲戌时','line_mention':54,'author_first_judgment_line':56,'actual_printed_chart':False,'printed_follow_up_hour':'乙亥时','printed_chart_line':61}
  if i==3:item['method_competition']={'palace_number':[114,116],'eight_gates':[118,120,122,124],'nine_stars':[126,128,130,132], 'all_candidates_preserved':True}
  if i==5:item['score_definition']={'90_minute':'1:1','after_extra_time':'1:1','post_penalty_total_reported':'5:3','winner':'Brazil','prohibition':'do_not_claim_five_three_regulation_time'}
  if i==6:item['error_and_correction']={'first_prediction_line':235,'later_result_and_self_correction_line':237,'original_predicted_winner':'Croatia','actual_winner_in_book':'France','score_digits_same_but_winner_reversed':True,'after_result_reason_not_initial':True,'training_error_negative':True}
  if i==7:item['last_step_unnumbered_style']='⑥'
  if i==5:item['literal_chart_warning']={'source_line':181,'palace':'离九宫','source_literal':'铺庚','may_be_OCR_of':'辅庚','do_not_silently_correct':True}
  cases.append(item)
 return cases,steps

PHASES={
 1:[(13,19,'initial_question',1),(44,44,'initial_judgment',0),(46,46,'book_feedback',0)],
 2:[(50,54,'initial_question',1),(56,56,'initial_judgment',0),(58,58,'cast_metadata',0),(85,85,'continued_judgment',0),(87,87,'book_feedback',0)],
 3:[(91,95,'initial_question',1),(114,116,'cast_metadata',0),(118,124,'cast_metadata',0),(126,132,'continued_judgment',0),(134,134,'book_feedback',0)],
 4:[(138,142,'initial_question',1),(163,163,'initial_judgment',0),(165,165,'book_feedback',0)],
 5:[(169,175,'initial_question',1),(200,200,'initial_judgment',0),(202,202,'book_feedback',0)],
 6:[(206,210,'initial_question',1),(235,235,'initial_judgment',0),(237,237,'book_feedback',0),(237,237,'editor_posthoc_correction',0)],
 7:[(241,245,'initial_question',1),(270,274,'initial_judgment',0),(276,276,'book_feedback',0)],
}

def assert_baseline_unchanged(base,out):
 # No old row may be modified/deleted; snapshot is additive only.
 names=['books','sections','cases','historical_chart_cells','historical_case_additional_casts',
 'historical_case_additional_cast_cells','historical_case_reasoning','semantic_assertions',
 'historical_case_book_verdicts','historical_case_disclosures','historical_palace_standardization',
 'historical_case_reasoning_trace','historical_case_review_audit','historical_case_phase_events',
 'historical_case_reasoning_corrections','historical_outcome_reclassification_audit']
 for table in names:
  cols=[x[1] for x in base.execute('PRAGMA table_info("'+table+'")')]
  if not cols:raise ValueError('Baseline schema missing '+table)
  cl=','.join('"'+c+'"' for c in cols)
  original=list(base.execute('SELECT '+cl+' FROM "'+table+'"'))
  new=set(out.execute('SELECT '+cl+' FROM "'+table+'"'))
  if not all(row in new for row in original):raise ValueError('Prior table changed '+table)

def insert_case(db,lines,raw,sid,item):
 i=item['case_number'];cid=item['case_id'];_,_,start,steps,initial,judgment,feedback,title=CASES[i-1]
 known='\n'.join(segment(lines,n) for n in initial)
 if any(v in known for v in ('结果，','结果：','事后检查','结果第二天')):raise ValueError('known_before contaminated by later feedback')
 prior_steps='\n\n'.join(segment(lines,n) for n in steps)
 first_pred='\n'.join(segment(lines,n) for n in judgment)
 result='\n'.join(segment(lines,n) for n in feedback)
 db.execute('''INSERT INTO cases(case_id,section_id,event_family_id,domain_id,known_before,author_yongshen_steps,author_judgment,later_feedback,reviewed) VALUES (?,?,?,?,?,?,?,?,0)''',(cid,sid,cid,'sports_competition',known,prior_steps,first_pred,result))
 db.execute('''INSERT INTO historical_case_protocol(case_id,completeness,published_chart_verification,feedback_independently_verified,eligible_blind_test,case_source_sha256,metadata_json) VALUES (?,'complete_original_story','source_txt_only_not_independently_recast',0,0,?,?)''',(cid,SOURCE_HASH,sj(item)))
 for palace,anchor,label,deity,door,star in chart(lines,start):
  db.execute('''INSERT INTO historical_chart_cells(case_id,palace,source_line,palace_label_raw,deity_raw,door_position_raw,star_position_raw,source_status) VALUES (?,?,?,?,?,?,?,'literal_source_transcription_only')''',(cid,palace,anchor,label,deity,door,star))
  is5=palace==5
  db.execute('''INSERT INTO historical_palace_standardization(case_id,cast_key,palace,center_stem,source_of_center_stem,standard_deity,standard_door,standard_star,normalized_status,original_raw_integrity_checked,method_reference,derived_host_palace,derived_host_source) VALUES (?,?,?,?,?,?,?,?,?,1,?,?,?)''',
    (cid,'primary',palace,door if is5 else None,'original_center_literal' if is5 else 'not_center',None if is5 else deity,None if is5 else door,None if is5 else star,'center_not_applicable_sanshu_three_fields' if is5 else 'peripheral_literal_verified','sports_source+shijia_qiju',2 if is5 else None,'shijia_qiju:五宫寄坤二宫' if is5 else None))
 for step in item['author_source_steps']:
  n=step['source_line'];k=step['step_number'];original=segment(lines,n)
  db.execute('''INSERT INTO historical_case_reasoning(case_id,step_number,source_line,author_analysis_original,short_method_topic,metadata_json) VALUES (?,?,?,?,?,?)''',(cid,k,n,original,step['topic'],sj(step)))
  evidence=candidate_trace(lines,i,k,n,step['topic'])
  db.execute('''INSERT INTO historical_case_reasoning_trace(case_id,step_number,source_line,evidence_json,review_status,positive_training_eligible) VALUES (?,?,?,?,'source_anchor_only_needs_full_manual_evidence_chain',0)''',(cid,k,n,sj(evidence)))
  db.execute('''INSERT INTO semantic_assertions(chapter_key,concept_id,kind,relation,source_start_line,source_end_line,metadata_json,original_excerpt,review_status) VALUES (?,?,?,?,?,?,?,?,?)''',(CHAPTER,f'sports:case{i:02d}:step{k:02d}','sports_worked_example','original_step_not_approved',n,n,sj(step),original,'draft'))
 for (a,b,phase,vis) in PHASES[i]:
  original=segment(lines,a,b)
  db.execute('''INSERT INTO historical_case_phase_events(case_id,source_start_line,source_end_line,phase,original_excerpt,metadata_json,visible_to_initial_blind_test) VALUES (?,?,?,?,?,?,?)''',(cid,a,b,phase,original,sj({'same_event':True,'source_sha256':SOURCE_HASH,'initial_blind_model_must_not_see_results':True}),vis))
  if phase in ('book_feedback','editor_posthoc_correction'):
   db.execute('''INSERT OR IGNORE INTO historical_case_disclosures(case_id,source_line,phase,fact_type,original_statement) VALUES (? ,?,'later_than_initial',?,?)''',(cid,a,phase,original))
  if phase=='editor_posthoc_correction':
   db.execute('''INSERT INTO historical_case_source_segments(case_id,segment_kind,source_start_line,source_end_line,original_text,metadata_json) VALUES (?,?,?,?,?,?)''',(cid,'sports_explicit_self_correction',a,b,original,sj({'initial_predicted_winner_wrong':True,'retrospective':True})))
 if i==6:
  db.execute('''INSERT INTO historical_case_reasoning_corrections(case_id,source_line,original_step_number,correction_kind,corrected_yongshen_policy,original_analysis_is_positive_training,source_review_status,rationale_original) VALUES (?,237,3,'sports_author_admits_wrong_winner_and_month_weighting','月令未土生兑金克坎水、天地盘干生克须复核',0,'source_documented_needs_professional_review',?)''',(cid,segment(lines,237)))
 if i==5:
  db.execute('''INSERT INTO historical_source_literal_anomalies(case_id,source_line,palace,source_literal,possible_variant,interpretation_status,original_retained) VALUES (?,181,9,'铺庚','辅庚','unverified_OCR_variant_do_not_rewrite',1)''',(cid,))
 if i==2:
  db.execute('''INSERT INTO historical_sports_cast_qualification(case_id,source_line,kind,original_text,metadata_json) VALUES (?,54,'unprinted_initial_cast',?,?)''',(cid,segment(lines,54,56),sj({'initial_hour':'甲戌时','next_hour':'乙亥时','did_not_print_first_chart':True})))
 if i==5:
  db.execute('''INSERT INTO historical_sports_cast_qualification(case_id,source_line,kind,original_text,metadata_json) VALUES (?,202,'score_scope',?,?)''',(cid,segment(lines,202),sj({'regulation':'1:1','after_extra_time':'1:1','post_penalty_total_reported':'5:3','winner':'Brazil'})))
 for ln in feedback:
  if not db.execute('SELECT 1 FROM historical_case_disclosures WHERE case_id=? AND source_line=?',(cid,ln)).fetchone():
   db.execute('''INSERT INTO historical_case_disclosures(case_id,source_line,phase,fact_type,original_statement) VALUES (?,?,'later_book_feedback','validation_information',?)''',(cid,ln,segment(lines,ln)))
 errors=[237] if i==6 else []
 db.execute('''INSERT INTO historical_case_book_verdicts(event_family_id,primary_case_id,verdict,explicit_source_correction,source_correction_lines_json,feedback_source_lines_json,independent_external_verification,app_output_protocol,evidence_review_status,note) VALUES (?,?,?,?,?,?,'not_verified','single_answer_for_one_cast','book_source_only',?)''',
    (cid,cid,'author_book_error_explicit' if i==6 else 'author_book_success_default',int(i==6),sj(errors),sj(feedback),'Correct score digits, wrong winning side; self-corrected after the match' if i==6 else 'Historical book claim only, not independent sports evidence'))
 db.execute('''INSERT INTO historical_case_review_audit(case_id,original_steps,mechanical_step_trace,human_complete_step_chains,review_status,warning) VALUES (?,?,?,0,'source_anchor_only_needs_full_manual_evidence_chain',?)''',(cid,len(steps),len(steps),'Initial 甲戌时 chart unprinted' if i==2 else 'Source initial wrong, hindsight isolated' if i==6 else 'Needs human method and chart verification'))

def build(base,source,output,index_dir,migration):
 if output.exists():raise ValueError('Output exists; do not overwrite previous archives')
 if digest(base)!=BASE_HASH:raise ValueError('Full 15 chapter archive SHA mismatch: refused')
 raw=source.read_bytes()
 if hashlib.sha256(raw).hexdigest()!=SOURCE_HASH:raise ValueError('Sports original TXT sha differs from verified version')
 lines=raw.decode('utf8').splitlines()
 if len(lines)!=276 or lines[0]!='第十二章' or lines[2]!='体育竞赛预测' or lines[8]!='第二节 实例解析（7例）':raise ValueError('Unexpected chapter source boundaries')
 entries,_=make_indexes(lines)
 output.parent.mkdir(parents=True,exist_ok=True)
 with sqlite3.connect('file:'+str(base)+'?mode=ro',uri=True) as previous, sqlite3.connect(output) as db:
  previous.backup(db)
  db.executescript(migration.read_text(encoding='utf8'))
  db.execute('PRAGMA foreign_keys=ON')
  with db:
   if db.execute('SELECT 1 FROM sections WHERE section_key=?',(SECTION,)).fetchone():raise ValueError('Chapter already imported')
   db.execute('''INSERT INTO sections(book_id,section_key,title,original_text,sha256,content_version,reviewed) VALUES ('shenqi',?,?,?,?,1,0)''',(SECTION,'体育竞赛预测',raw.decode('utf8'),SOURCE_HASH))
   section_id=db.execute('SELECT last_insert_rowid()').fetchone()[0]
   db.execute('''INSERT INTO chapter_knowledge(chapter_key,book_id,title,source_sha256,source_length_bytes,knowledge_version,review_status) VALUES (?,'shenqi','体育竞赛预测',?,?,'1','draft')''',(CHAPTER,SOURCE_HASH,len(raw)))
   for ln,key,meaning in METHODS:
    meta={'sports_domain':True,'source_line':ln,'concept_id':key,'summary':meaning,'source_supported_not_proven':True}
    db.execute('''INSERT INTO semantic_assertions(chapter_key,concept_id,kind,relation,source_start_line,source_end_line,metadata_json,original_excerpt,review_status) VALUES (?,?,?,?,?,?,?,?,?)''',(CHAPTER,'sports:general:'+key,'sports_condition','conditional_source',ln,ln,sj(meta),segment(lines,ln),'draft'))
   for entry in entries:insert_case(db,lines,raw,section_id,entry)
   db.execute('''INSERT INTO chapter_archival_versions(archive_label,baseline_sha256,new_db_sha256,contains_complete_private_copyright_source,snapshot_type,created_utc,repo_public_archive_policy) VALUES (?, ?,NULL,1,'incremental_source_preserving','2026-10-20T07:28:00-04:00','user_explicitly_authorized_public_full_archive')''',('shenqi_16_sections_84_whole_events',BASE_HASH))
  if db.execute('PRAGMA integrity_check').fetchone()[0]!='ok' or db.execute('PRAGMA foreign_key_check').fetchall():raise ValueError('Broken SQLite integrity or FK')
  assert_baseline_unchanged(previous,db)
  expected={'sections':16,'cases':84,'historical_chart_cells':756,'historical_case_additional_cast_cells':45,'historical_case_reasoning':376,'semantic_assertions':990,'historical_case_reasoning_trace':376,'historical_palace_standardization':801}
  counts={table:db.execute('SELECT count(*) FROM '+table).fetchone()[0] for table in expected}
  for t,num in expected.items():
   if counts[t]!=num:raise ValueError(('Count mismatch',t,num,counts[t]))
  centers=db.execute('SELECT count(*) FROM historical_palace_standardization WHERE palace=5 AND derived_host_palace=2 AND standard_deity IS NULL AND standard_star IS NULL AND standard_door IS NULL').fetchone()[0]
  if centers!=89:raise ValueError(('Historic centre corruption',centers))
  if db.execute("SELECT count(*) FROM historical_case_book_verdicts WHERE verdict='author_book_error_explicit'").fetchone()[0]!=5:raise ValueError('Sport error must become fifth source-explicit initial error')
  # Baseline has 82 real charts and no new additional cast; all 7 new cases are one per event.
  if db.execute("SELECT count(*) FROM historical_case_additional_casts").fetchone()[0]!=5:raise ValueError('Past additional casts lost')
  if db.execute('SELECT count(*) FROM historical_source_literal_anomalies').fetchone()[0]!=1:raise ValueError('OCR issue lost')
  if db.execute('SELECT count(*) FROM historical_sports_cast_qualification').fetchone()[0]!=2:raise ValueError('Missing unprinted cast/penalty scope record')
  db.execute('PRAGMA page_size=2048');db.execute('VACUUM');db.commit()
  if db.execute('PRAGMA integrity_check').fetchone()[0]!='ok' or db.execute('PRAGMA foreign_key_check').fetchall():raise ValueError('Final sqlite check failed')
 index_dir.mkdir(parents=True,exist_ok=True)
 sha=digest(output)
 manifest={'schema':'wengua_sports_prediction_manifest_v1','source_chapter':'体育竞赛预测','source_chapter_number_printed':'第十二章','processed_section_count':16,
 'chapter_key':CHAPTER,'source_sha256':SOURCE_HASH,'source_bytes':len(raw),'source_lines':len(lines),'events':7,'printed_charts':7,'printed_palace_literals':63,
 'author_analysis_steps':32,'general_conditional_method_candidates':len(METHODS),'case_analysis_candidate_entries':32,'new_semantic_assertions':len(METHODS)+31,
 'book_case_error_explicit':[6],'first_unprinted_cast_case':2,'different_source_reading_methods_case':3,
 'score_penalty_not_regulation_case':5,'source_anomaly_case':5,'human_professional_approved_steps':0,'source_predictions_independent_validity':False,
 'full_archive_baseline_sha256':BASE_HASH,'full_archive_sha256':sha,'actual_count':counts,'centres_with_source_paired_host':centers,'archive_from_sqlite_backup':True}
 method_index={'schema':'wengua_sports_methods_v1','chapter_key':CHAPTER,'source_sha256':SOURCE_HASH,'methods':[{'concept_id':'sports:general:'+id,'source_line':ln,'conditional_summary':desc,'review_status':'draft'} for ln,id,desc in METHODS],
 'workflow':['选择具体问事：胜负/金牌数/比分、明确比赛场地和主客依据','以地盘日时为主、天盘日时为客，分别验证对号与当前时辰','保留比赛首个只有叙述、未印出的时辰，绝不伪造九宫','不同候选方法如宫数/八门/九星须保留全部尝试和不分胜负阶段','读取真实九宫天盘地盘及门星神值符、旬空格局、庚器械辛金牌景门技术','结合时令五行旺衰与宫生克，明确支持与反证的条件链','应期或比分数象只记作者原说，区分常规赛、加时、点球','隔离首次错误结论与事后修正，任何故事不可当独立现实预测验证']}
 source_audit={'schema':'wengua_sports_source_audit_v1','source_sha256':SOURCE_HASH,'printed_charts':[x[2] for x in CASES],
 'case2_unprinted':{'line':54,'author_first_judgment':56,'later_printed_chart':61,'missing_chart_not_generated':True},
 'case3_alternative_methods':{'palace_number':[114,116],'eight_gates':[118,120,122,124],'nine_stars':[126,128,130,132]},
 'case5_ocr':{'line':181,'palace':'离九宫','raw':'铺庚','candidate':'辅庚','not_corrected_without_original_print':True},
 'case5_score':{'line':202,'regulation':'1:1','extra_time':'1:1','post_penalty_total_reported':'5:3'},
 'case6_author_initial_error':{'line':235,'incorrect_winner':'Croatia','later_true_winner':'France','score_order_same_digits':'2:1','retrospective_correction_line':237,'do_not_train_first_wrong_judgment_as_success':True}}
 evidence={'schema':'wengua_sports_source_step_evidence_v1','chapter_key':CHAPTER,'source_sha256':SOURCE_HASH,'author_source_steps':32,'human_verified_complete_reasoning':0,
 'cases':[{'case_id':c['case_id'],'steps':[candidate_trace(lines,i,step['step_number'],step['source_line'],step['topic']) for step in c['author_source_steps']]} for i,c in enumerate(entries,1)]}
 for filename,obj in [('chapter_manifest.json',manifest),('case_index.json',{'schema':'wengua_sports_whole_cases_v1','chapter_key':CHAPTER,'source_sha256':SOURCE_HASH,'cases':entries}),('method_index.json',method_index),('source_audit.json',source_audit),('author_reasoning_evidence_index.json',evidence)]:
  (index_dir/filename).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 result={'source_sha256':SOURCE_HASH,'archive_sha256':sha,'baseline_sha256':BASE_HASH,'events':7,'counts':counts,'centres':centers,'prior_complete_rows_unmodified':True,'archive_size':output.stat().st_size}
 print(json.dumps(result,ensure_ascii=False,indent=2));return result

def main(argv=None):
 p=argparse.ArgumentParser()
 p.add_argument('--base',type=Path,required=True)
 p.add_argument('--source',type=Path,required=True)
 p.add_argument('--output',type=Path,required=True)
 p.add_argument('--index-dir',type=Path,required=True)
 p.add_argument('--migration',type=Path,default=Path(__file__).resolve().parents[1]/'schema/migrations/011_sports_source_qualification.sql')
 a=p.parse_args(argv);build(a.base,a.source,a.output,a.index_dir,a.migration)
if __name__=='__main__':main()
