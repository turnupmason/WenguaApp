"""Append two intact Kaiwu competitive/evaluation events to SHA-locked 179-case DB.

School principal Yuan: three time-separated cast mentions belong to ONE ongoing
school accreditation event. First July 1998 cast and precise date were LOST in
the book. Two later charts are spatially flattened original OCR; no fabricated
palace originals. Debate (1999): Xi'an Jiaotong won GROUP A and Egypt GROUP B;
the editor says some analysis was revised, so do not call all source material
uncorrected pre-result predictions.
"""
from __future__ import annotations
import argparse,hashlib,json,re,sqlite3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE_SHA='fc96be68917a5132f4499e06a61dbe13db54b282814e4d69aa1a84cb44608a35'
SOURCE_SHA='ef2f70119c7e4a1a12d42430b786f7aac6d921cc83b25bebcb0ef1dd9eec731b'
BASE_NAME='WenguaApp_神奇之门21章_开悟之门20节_179案例_完整研究库.sqlite3'
NEW_NAME='WenguaApp_神奇之门21章_开悟之门21节_181案例_完整研究库.sqlite3'
SECTION='competition_evaluation_ch02_section12'
CHAPTER='kaiwu/'+SECTION+'/v1'
TITLE='第十二节 竞争评比预测(共2例)'
CASES=[
 {'id':'kaiwu.competition.case01','name':'某市七中申报省重点与袁校长职务',
 'domain':'competition_evaluation','facets':['education_school_accreditation','employment'],
 'span':(3,73),'initial':(3,6),'steps':{'nov1998':[33,35,37,39],'jun1999':[67,69,71]},
 'judgment':[(7,7),(9,9),(40,40),(72,72)],
 'feedback':[(8,8),(41,41),(73,73)],
 'note':'One single continuing school accreditation; 1998 July no time and chart missing; Nov and June independent recasts do not become new event families'},
 {'id':'kaiwu.competition.case02','name':'1999国际大专辩论赛西安交大A组与埃及B组冠军',
 'domain':'sports_competition','facets':['competition_evaluation','education_scholastic_debate'],
 'span':(75,120),'initial':(75,77),'steps':{'debate1999':[100,102,104,106,108,110,112]},
 'judgment':[(102,113)],'feedback':[(114,116)],
 'note':'A-group Xi An Jiaotong winner and B-group Egypt winner, not a single overall champion. Teacher at line 120 says some author analysis was edited after the event.'}
]
CASTS=[
 ('kaiwu.competition.case01','jul1998_missing',(5,10),'1998-07 unknown day/hour','historical_original_lost',None),
 ('kaiwu.competition.case01','nov1998',(11,41),'1998-11-14 16:15','printed_OCR_flattened',(15,29)),
 ('kaiwu.competition.case01','jun1999',(42,73),'1999-06-06 19:40','printed_OCR_flattened',(46,63)),
 ('kaiwu.competition.case02','debate1999',(75,120),'1999-08-27 22:45','printed_OCR_flattened',(79,96))
]
# Preserve conditional, actor-specific source heuristics, not validated forecasts.
METHODS=[
 ('school_questioner_day','kaiwu.competition.case01',33,['school_principal_asking','day_stem_known'],'日干为校长,以惊门玄武等判断忧扰'),
 ('school_opponent_hour','kaiwu.competition.case01',35,['school_accreditation_dispute','hour_stem_known'],'时干代表原书所称对立者/告状者;月干为其他官员'),
 ('school_document_gate','kaiwu.competition.case01',35,['school_accreditation_dispute','jing_door_known'],'景门被用作报告与状纸，考量空亡等条件'),
 ('school_approval_gate','kaiwu.competition.case01',39,['school_rank_review','kai_gate_known'],'开门作学校或批准机关；必须结合实际问事角色'),
 ('school_gan_year_stem','kaiwu.competition.case01',69,['school_rank_review','day_time_year_stems_known'],'日干时干和太岁关系、开门生助仅属作者论证'),
 ('school_approval_timing','kaiwu.competition.case01',71,['school_review_pending','solar_term_date_and_clash_available'],'伏吟逢冲、乾宫批准与芒种夏至间的作者应期链'),
 ('debate_judge_zhifu','kaiwu.competition.case02',102,['academic_debate_competition','zhifu_known'],'竞赛用值符为裁判、景门为指导老师'),
 ('debate_home_away_stems','kaiwu.competition.case02',102,['academic_debate_competition','home_away_relationship_known'],'原书以地盘时干主队天盘时干客队且日干代表女儿学校'),
 ('debate_gold_xin','kaiwu.competition.case02',104,['academic_debate_competition','xin_symbol_known'],'辛对应书中金牌象，用神选择需来源限制'),
 ('debate_coach_jing','kaiwu.competition.case02',108,['academic_debate_competition','jing_door_and_day_palaces_known'],'景门指导老师、相生与螣蛇交互研判'),
 ('debate_opponent_month','kaiwu.competition.case02',112,['academic_debate_competition','month_stem_and_opponent_relation_known'],'月干壬为对手、惊门口才，分组第一与总体第一不可混淆'),
 ('debate_editor_revision','kaiwu.competition.case02',120,['later_editorial_review'], '张志春明言个别分析不当经过修改加工, 不可将编辑后文章全部视为原始未改预测')
]
def sha(raw):return hashlib.sha256(raw).hexdigest()
def js(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'))
def lit(L,a,b=None):
 b=a if b is None else b
 if not 1<=a<=b<=len(L):raise ValueError(('source line out of range',a,b))
 return '\n'.join(L[a-1:b])
def validate(raw):
 if sha(raw)!=SOURCE_SHA or len(raw)!=14348 or not raw.endswith(b'\n'):
  raise ValueError('Exact input SHA / UTF-8 length / trailing newline mismatched')
 L=raw.decode('utf8').splitlines()
 if len(L)!=120 or L[0]!=TITLE or not L[2].startswith('(例一)') or not L[74].startswith('(例二)'):
  raise ValueError('Two printed examples expected; other source layout not accepted')
 for n,word in [(10,'格局只好阙如'),(13,'阴6局'),(44,'阳9局'),
                (73,'6月10日'),(77,'阴一局'),(116,'A 组冠军'),(116,'B组的冠军'),(120,'修改加工')]:
  if word not in L[n-1]:raise ValueError(('critical source property lost',n,word))
 return L
def no_legacy_row_change(old,new):
 for (table,) in old.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"):
  cols=[r[1] for r in old.execute('PRAGMA table_info("'+table+'")')]
  columns=','.join('"'+x+'"' for x in cols)
  past=list(old.execute('SELECT '+columns+' FROM "'+table+'"'))
  current=set(new.execute('SELECT '+columns+' FROM "'+table+'"'))
  if any(row not in current for row in past):raise ValueError('Existing row changed in '+table)
def add_phase(db,L,cid,key,kind,a,b,visible=0,info=None):
 text=lit(L,a,b)
 db.execute("""INSERT INTO kaiwu_competition_source_phases
 (chapter_key,case_id,phase_key,phase_kind,source_start,source_end,
 source_original,sha256,initially_visible,metadata_json)
 VALUES (?,?,?,?,?,?,?,?,?,?)""",(CHAPTER,cid,key,kind,a,b,text,sha(text.encode()),visible,js(info or {'book_source_only':True,'post_event_not_initially_known':not bool(visible)})))
def add_step(db,L,sid,e,episode,k,n):
 cid=e['id'];text=lit(L,n)
 fact={'source_book':'kaiwu','episode':episode,'source_line':n,
  'original_question_event_family':cid,'original_author_analysis':True,
  'book_claim_no_external_observational_validation':True,
  'palace_claims_are_not_source_plate_cell_verifications':True,
  'eligible_positive_training':False,'pre_outcome_publication_unverified':True,
  'external_historical_result_unverified':True,
  'teacher_edited_source_case2':cid.endswith('case02'),
  'claim_lexical_gates':sorted(set(re.findall(r'[开休生伤杜景死惊]门',text))),
  'competing_evidence_should_not_be_removed':True}
 db.execute("""INSERT INTO kaiwu_competition_author_steps(
  chapter_key,case_id,episode_key,step_number,source_line,
  original_author_text,sha256,evidence_json) VALUES (?,?,?,?,?,?,?,?)""",
  (CHAPTER,cid,episode,k,n,text,sha(text.encode()),js(fact)))
 concept='competition:kaiwu:'+e['id'].split('.')[-1]+':'+episode+':step'+str(k).zfill(2)
 add_concept(db,sid,concept,n,text,fact,'original_book_analytic_step')
 step=db.execute('SELECT COUNT(*) FROM historical_case_reasoning WHERE case_id=?',(cid,)).fetchone()[0]+1
 db.execute("""INSERT INTO historical_case_reasoning(case_id,step_number,source_line,
  author_analysis_original,short_method_topic,metadata_json)
  VALUES (?,?,?,?,?,?)""",(cid,step,n,text,'historical_competition_source_evidence',js(fact)))
 db.execute("""INSERT INTO historical_case_reasoning_trace(case_id,step_number,
  source_line,evidence_json,review_status,positive_training_eligible)
  VALUES (?,?,?,?,'draft_book_source_no_independent_blind_validation',0)""",
  (cid,step,n,js(fact)))
def add_concept(db,sid,concept,n,source,meta,kind):
 db.execute("""INSERT INTO semantic_assertions(chapter_key,concept_id,kind,relation,
 source_start_line,source_end_line,metadata_json,original_excerpt,review_status)
 VALUES (?,?,?,'book_conditional_evidence_not_verified',?,?,?,?,'draft')""",
  (CHAPTER,concept,kind,n,n,js(meta),source))
 db.execute("""INSERT INTO cross_book_concept_tracks(chapter_key,concept_id,
 source_start_line,source_end_line,source_section_id,source_sha256,excerpt_sha256,
 track_id,relation_to_prior,comparison_state,normalized_json,review_status)
 VALUES (?,?,?,?,?,?,?,?,?,'book_candidate_not_world_validated',?,'draft')""",
 (CHAPTER,concept,n,n,sid,SOURCE_SHA,sha(source.encode()),
 'competition:evaluation_and_sports_shared_sources','additional_exposition',js(meta)))
def build(base,source,output,index_dir):
 base,source,output,index_dir=map(Path,(base,source,output,index_dir))
 if output.exists():raise ValueError('Never overwrite existing immutable source archive')
 if sha(base.read_bytes())!=BASE_SHA:raise ValueError('175-case was obsolete; exact 179 parent required')
 raw=source.read_bytes();L=validate(raw)
 output.parent.mkdir(parents=True,exist_ok=True)
 with sqlite3.connect('file:'+str(base.resolve())+'?mode=ro',uri=True) as old,sqlite3.connect(output) as db:
  old.backup(db)
  db.executescript((ROOT/'schema/migrations/036_kaiwu_competition_multicast_unprinted.sql').read_text('utf8'))
  db.execute('PRAGMA foreign_keys=ON')
  with db:
   if db.execute("SELECT COUNT(*) FROM sections WHERE book_id='kaiwu'").fetchone()[0]!=20:
    raise ValueError('Missing prior 20 Kaiwu sections')
   if db.execute("SELECT COUNT(*) FROM cases WHERE case_id LIKE 'shenqi.sports.case%'").fetchone()[0]!=7:
    raise ValueError('Preserve seven old Shenqi sports historical events')
   db.execute("""INSERT INTO sections(book_id,section_key,title,original_text,sha256,content_version,reviewed)
    VALUES ('kaiwu',?,?,?,?,1,1)""",(SECTION,TITLE,raw.decode('utf8'),SOURCE_SHA))
   sid=db.execute('SELECT last_insert_rowid()').fetchone()[0]
   db.execute("""INSERT INTO chapter_knowledge(chapter_key,book_id,title,source_sha256,
    source_length_bytes,knowledge_version,review_status)
    VALUES (?,'kaiwu',?,?,?,'1','draft')""",(CHAPTER,TITLE,SOURCE_SHA,len(raw)))
   for e in CASES:
    cid=e['id']
    steps='\n\n'.join(lit(L,n) for v in e['steps'].values() for n in v)
    judg='\n'.join(lit(L,*r) for r in e['judgment'])
    outcome='\n'.join(lit(L,*r) for r in e['feedback'])
    fact={'case_topic':e['name'],'source_span':e['span'],
      'one_event_with_separate_casts':cid.endswith('case01'),
      'dated_cast_original_lost':cid.endswith('case01'),
      'teacher_admits_editing_original_analytic_text':cid.endswith('case02'),
      'one_champion_per_group_not_overall':cid.endswith('case02'),
      'no_full_original_OCR_plate':True,
      'source_only_no_independent_educational_or_sports_verification':True}
    db.execute("""INSERT INTO cases(case_id,section_id,event_family_id,domain_id,
     known_before,author_yongshen_steps,author_judgment,later_feedback,reviewed)
     VALUES (?,?,?,?,?,?,?,?,1)""",
     (cid,sid,cid,e['domain'],lit(L,*e['initial']),steps,judg,outcome))
    db.execute("""INSERT INTO historical_case_protocol(
     case_id,completeness,published_chart_verification,feedback_independently_verified,
     eligible_blind_test,case_source_sha256,metadata_json)
     VALUES (?,'complete_book_event_multiple_cast_mentions_OCR_unresolved',
      'first_cast_lost_later_casts_flattened_OCR_unresolved',0,0,?,?)""",
     (cid,SOURCE_SHA,js(fact)))
    db.execute("""INSERT INTO historic_book_case_acceptance(case_id,source_book,
     source_chapter_key,source_documented_outcome,metadata_json)
     VALUES (?,'kaiwu',?,'book_author_report_only_with_timing_phase_split',?)""",
     (cid,CHAPTER,js(fact)))
    for i,domain in enumerate([e['domain']]+e['facets']):
     db.execute("""INSERT INTO unified_case_domain_facets(
      case_id,domain_id,source_chapter_key,primary_domain,note)
      VALUES (?,?,?,?,?)""",(cid,domain,CHAPTER,int(i==0),e['note']))
    db.execute("""INSERT INTO historical_case_review_audit(case_id,original_steps,
     mechanical_step_trace,human_complete_step_chains,review_status,warning)
     VALUES (?,?,?,0,'accepted_historical_book_case_methods_draft',?)""",
     (cid,sum(map(len,e['steps'].values())),sum(map(len,e['steps'].values())),e['note']))
    db.execute("""INSERT INTO historical_case_book_verdicts(
     event_family_id,primary_case_id,verdict,explicit_source_correction,
     source_correction_lines_json,feedback_source_lines_json,
     independent_external_verification,app_output_protocol,evidence_review_status,note)
     VALUES (?,?,'author_book_success_default',0,'[]',?,
      'not_verified','single_answer_for_one_cast','book_study_not_validated',?)""",
     (cid,cid,js([a for a,b in e['feedback']]),e['note']))
    add_phase(db,L,cid,'initial_event','question_as_known_before_first_cast',*e['initial'],visible=1)
    for j,(a,b) in enumerate(e['judgment'],1):
     add_phase(db,L,cid,'judgment_'+str(j),'printed_author_response_do_not_merge_with_later_feedback',a,b)
    for j,(a,b) in enumerate(e['feedback'],1):
     add_phase(db,L,cid,'feedback_'+str(j),'source_later_report_not_precast_input',a,b)
    if cid.endswith('case01'):
     for k,kind,a,b in [
      ('after_first_prediction','disclosure_at_first_meeting',8,8),
      ('lost_first_board','explicit_no_hour_no_chart_of_original_cast',10,10),
      ('nov_new_question','new_cast_question_not_new_event',11,13),
      ('nov_readout','second_cast_legal_position_question',40,41),
      ('jun_information','1999_precast_new_information',42,44),
      ('jun_readout','third_cast_approval_window',72,72),
      ('final_approval','result_of_one_continuing_event',73,73)]:
      add_phase(db,L,cid,k,kind,a,b)
    else:
     add_phase(db,L,cid,'group_A_B_outcome','different_group_champions_not_one_total_champion',116,116)
     add_phase(db,L,cid,'teacher_later_editing',
      'author_says_source_analysis_was_modified_after_original',119,120)
   for cid,episode,span,date,state,panel in CASTS:
    text=lit(L,*span)
    db.execute("""INSERT INTO kaiwu_competition_source_episodes
     (chapter_key,case_id,episode_key,first_source_line,last_source_line,
      date_claim,topic,cast_state,original_excerpt,sha256,metadata_json)
     VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
     (CHAPTER,cid,episode,*span,date,'school_evaluation' if cid.endswith('case01') else 'academic_debate',
      state,text,sha(text.encode()),js({'one_family_even_with_three_casts':cid.endswith('case01'),
       'source_only':True,'not_certified_spatial_board':True})))
    if panel is not None:
     rawpanel=lit(L,*panel)
     db.execute("""INSERT INTO kaiwu_competition_raw_casts(
      chapter_key,case_id,episode_key,source_start,source_end,original_OCR,source_sha256)
      VALUES (?,?,?,?,?,?,?)""",
      (CHAPTER,cid,episode,*panel,rawpanel,sha(rawpanel.encode())))
     for n in range(panel[0],panel[1]+1):
      piece=lit(L,n)
      db.execute("""INSERT INTO kaiwu_competition_raw_lines
       VALUES (?,?,?,?,?,?)""",(CHAPTER,cid,episode,n,piece,sha(piece.encode())))
     add_phase(db,L,cid,'panel_'+episode,
      'original_flat_OCR_no_fabricated_palace_positions',*panel)
   for e in CASES:
    for episode,nums in e['steps'].items():
     for k,n in enumerate(nums,1):
      add_step(db,L,sid,e,episode,k,n)
      add_phase(db,L,e['id'],'author_step_'+episode+'_'+str(k),
       'original_book_reasoning_not_independent_validation',n,n)
   for key,cid,n,conditions,summary in METHODS:
    text=lit(L,n)
    opts={'all':[{'fact':x,'required':True} for x in conditions],
     'unknown':'return_unresolved_not_a_positive_or_negative_verdict',
     'different_actor_roles_require_rebinding':True}
    limits={'book_source_only':True,'not_verified_against_live_results':True,
      'chapter_case':cid,'first_lost_chart_cannot_be_rebuilt':True,
      'debate_A_B_group_split_must_be_preserved':True}
    db.execute("""INSERT INTO kaiwu_competition_conditional_methods
     (chapter_key,method_id,case_id,original_line,source_original,
      preconditions_json,source_level_claim,limits_json)
     VALUES (?,?,?,?,?,?,?,?)""",
     (CHAPTER,key,cid,n,text,js(opts),summary,js(limits)))
    add_concept(db,sid,'competition:kaiwu:method:'+key,n,text,{'condition':opts,'limits':limits},
     'conditional_competition_book_method')
   db.execute("""INSERT INTO chapter_archival_versions(
    archive_label,baseline_sha256,new_db_sha256,contains_complete_private_copyright_source,
    snapshot_type,created_utc,repo_public_archive_policy)
    VALUES (?, ?,NULL,1,'kaiwu_competition_two_whole_events_three_printed_OCR_one_lost',
    '2026-10-21','user_authorized_public_full_sqlite_versions')""",
    ('shenqi21_kaiwu21_competition_181events',BASE_SHA))
  no_legacy_row_change(old,db)
  expected={'sections':42,'cases':181,'historical_chart_cells':1440,
   'historical_case_additional_casts':19,'historical_case_additional_cast_cells':171,
   'historical_palace_standardization':1611,'historical_case_reasoning':966,
   'historical_case_reasoning_trace':966,
   'semantic_assertions':2718,'cross_book_concept_tracks':1461,
   'historic_book_case_acceptance':73,'unified_case_domain_facets':125,
   'kaiwu_competition_source_episodes':4,'kaiwu_competition_raw_casts':3,
   'kaiwu_competition_raw_lines':51,'kaiwu_competition_author_steps':14,
   'kaiwu_competition_conditional_methods':12}
  got={t:db.execute('SELECT count(*) FROM "'+t+'"').fetchone()[0] for t in expected}
  if got!=expected:raise ValueError(('expected all old plus new exact table totals',got,expected))
  if db.execute("SELECT count(*) FROM historical_case_book_verdicts WHERE verdict='author_book_error_explicit'").fetchone()[0]!=11:
   raise ValueError('Eleven prior explicit author errors cannot be changed')
  if db.execute('PRAGMA integrity_check').fetchone()[0]!='ok' or db.execute('PRAGMA foreign_key_check').fetchall():
   raise ValueError('SQLite archive integrity or FK check failed')
  db.execute('VACUUM');db.commit()
 index_dir.mkdir(parents=True,exist_ok=True)
 result={'schema':'kaiwu_competition_two_whole_events_multicast_v1',
 'source_title':TITLE,'source_sha256':SOURCE_SHA,'source_bytes':len(raw),'source_lines':len(L),
 'book_whole_examples':2,'new_distinct_event_families':2,'school_recast_episodes_one_family':3,
 'first_1998_July_cast_lost_and_date_unknown':True,'actual_flattened_OCR_cast_fragments':3,
 'raw_OCR_line_count':51,'true_new_verified_original_nine_palaces':0,
 'source_author_step_count':14,'conditional_draft_method_candidates':12,
 'school_civil_service_issue_same_event':True,
 'debate_winners':{'A_group':'Xi_an_Jiaotong_University','B_group':'Egypt'},
 'teacher_mentions_editing_analyses_after_the_fact':True,
 'all_old_179_printed_complete_charts_preserved':True,
 'eleven_prior_explicit_initial_errors_unchanged':True,
 'all_prior_full_db_rows_unchanged':True,'positive_training_approved':0,
 'parent_sha256':BASE_SHA,'full_archive_sha256':sha(output.read_bytes()),'counts':got}
 def dump(name,obj):(index_dir/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n','utf8')
 dump('chapter_manifest.json',result)
 dump('case_index.json',{'source_sha256':SOURCE_SHA,'cases':[
  {'case_id':e['id'],'source_lines':e['span'],'question_lines':e['initial'],
   'analysis_episodes':e['steps'],'original_prediction_lines':e['judgment'],
   'result_lines':e['feedback'],'source_domain':e['domain'],
   'multi_cast_same_event':e['id'].endswith('case01'),'note':e['note']}
  for e in CASES]})
 dump('cast_provenance.json',{'source_sha256':SOURCE_SHA,'casts':[
  {'case_id':cid,'episode':ep,'source_span':span,'date_claim':date,
   'status':state,'exact_original_chart_OCR_span':panel,
   'line_hashes':[{'line':n,'sha256':sha(lit(L,n).encode())}
    for n in range(panel[0],panel[1]+1)] if panel else [],
   'not_original_verified_grid':True} for cid,ep,span,date,state,panel in CASTS]})
 dump('conditional_methods.json',{'source_sha256':SOURCE_SHA,'methods':[
  {'key':key,'case':cid,'source_line':ln,
   'conditions':conditions,'summary':summary,'review_status':'draft'}
  for key,cid,ln,conditions,summary in METHODS]})
 return result
def main():
 p=argparse.ArgumentParser()
 for x in ('base','source','output','index-dir'):p.add_argument('--'+x,required=True)
 a=p.parse_args()
 print(js(build(a.base,a.source,a.output,a.index_dir)))
if __name__=='__main__':main()
