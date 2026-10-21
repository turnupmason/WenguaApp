"""Source-fidelity Kaiwu litigation ch2 s10: four genuinely new question families.

Important: user-supplied transcript renders four reconstructed OCR nine-palace grids.
Their spatial arrangement is already an editorial reconstruction, with explicit
missing, uncertain characters: never promote to historical_chart_cells or certify
original ancient nine-palace source. Typed cells are uncertain transcription ONLY.
Preserve speaker-specific initial prediction, real-time added information, later
book feedback and teacher's after-result analyses distinctly.
"""
from __future__ import annotations
import argparse,hashlib,json,re,sqlite3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE_SHA='ce0929cafce50d69c1782464cc7ef84de19da507c8ef268c8787493929efb0a0'
SOURCE_SHA='c80b016c5f0afb70819412017be7bb0beb3d53e8b8c71ea4adbacc12230b61d5'
BASE_NAME='WenguaApp_神奇之门21章_开悟之门19节_175案例_完整研究库.sqlite3'
NEW_NAME='WenguaApp_神奇之门21章_开悟之门20节_179案例_完整研究库.sqlite3'
SECTION='litigation_prediction_ch02_section10'
CHAPTER='kaiwu/'+SECTION+'/v1'
TITLE='第十节 官司诉讼预测（共4例）'
# all line anchors refer to the source upload; line count 203, no invented data
CASES=[
 dict(id='kaiwu.litigation.case01',name='科迪药业陈董事长石家庄开发区土地合同诉讼',
  span=(5,47),panel=(15,28),initial=(7,13),steps=[32,34,40,42],
  judge=[(36,36),(44,44)],feedback=[(38,38),(46,46)],
  teacher=[],intro=['property_purchase','civil_land_dispute'],
  after=[('interim_disclosure_investment',38,38)],
  note='Original questioner had not filed claim; first forecast said favorable, September 1998 victory only later in book. Amount 200万元 first revealed after author asked.'),
 dict(id='kaiwu.litigation.case02',name='孟女士丈夫因经济问题受查与五月释放',
  span=(48,103),panel=(59,72),initial=(50,51),steps=[78,80,82,86,88,90,94],
  judge=[(52,52)],feedback=[(54,54),(96,96)],teacher=[100,102],
  intro=['criminal_investigation','detention_release'],
  after=[('first_confirmation_only_economic_issue',54,54),('later_report_may_release',96,96)],
  note='First reply confirms economic allegation only; June interview reports release in lunar May. Teacher says original lunar-May method nonstandard, proposes 30-day reasoning after outcome.'),
 dict(id='kaiwu.litigation.case03',name='韩女士问丈夫贪污受羁押及定罪刑期',
  span=(104,161),panel=(121,134),initial=(106,109),steps=[140,144,148,152,154],
  judge=[(110,110),(114,114)],feedback=[(112,112),(116,116)],teacher=[158,160],
  intro=['criminal_investigation','sentence_duration'],
  after=[('later_same_inquiry_new_disclosure',112,112),('later_sentence_report',116,116)],
  note='Author predicts 3–5-year sentence; book reports original six years with one-year reduction resulting five. Teacher rejects original timing/foreign 六壬 numerical reasoning as nonstandard.'),
 dict(id='kaiwu.litigation.case04',name='兰州周品基孙某之子劫车案件',
  span=(162,203),panel=(168,181),initial=(164,166),steps=[185,187,189],
  judge=[(185,189)],feedback=[(191,191),(193,193)],teacher=[201,203],
  intro=['criminal_robbery','sentence_duration'],
  after=[('evening_revelation',191,191),('unasked_uncaught_later_family_death',193,193)],
  note='One questioner one cast: son robbery and later seven-year sentence. The unasked uncle death in August explicitly NOT predicted; teacher retrofits symbols only after death. Transcription chart source vs analysis palace contradicts itself.')
]
METHODS=[
 ('civil_day_person',1,32,['dispute_is_civil_land','day_stem_position_known'],'日干为当事人；合看伤门、空亡、螣蛇与买地受阻'),
 ('civil_hour_investment',1,34,['dispute_is_civil_land','hour_stem_position_known'],'时干与甲子戊资金、景门诉状同时取用'),
 ('civil_jing_petition',1,40,['formal_lawsuit_pending','jing_door_palace_known','court_kai_door_known'],'景门为诉状，开门为法院，比较双方关系'),
 ('civil_parties_court',1,42,['plaintiff_defendant_roles_known','zhifu_tianyi_kai_positions_known'],'值符为原告、天乙为被告、开门法院，按书内生克判断'),
 ('spouse_geng_relation',2,78,['asked_about_husband','geng_spouse_and_day_stem_known'],'乙庚夫妇用神、丙辛合问丈夫，结合值符'),
 ('spouse_financial_investigation',2,80,['asked_about_economic_offense','capital_stem_and_related_star_known'],'戊为财和天芮等条件组合；不作为现实有罪证据'),
 ('police_baihu',2,82,['asked_about_detainment','baihu_and_husband_positions_known'],'白虎传统代表公安，比较丈夫用神相冲克'),
 ('spouse_release_judge',2,86,['asked_about_release','geng_and_judge_kai_door_known'],'开门作为法官，结合夫星庚、值符、休门'),
 ('release_hour_stem',2,90,['asked_about_release','time_stem_and_other_door_known'],'时干与壬庚格局作为书内是否脱险线索'),
 ('teacher_lunar_month',2,102,['lunar_release_timing_asked','zhishi_gate_palace_known','large_case_day_timing_illogical'],'老师事后反评值使落3宫之3天不合事理，转约30天；不能当初断'),
 ('husband_year_stem',3,144,['asked_about_husband_criminal_case','husband_birth_year_known'],'年命及辛戊组合按原书取用'),
 ('law_timing_existing_offense',3,152,['existing_criminal_case','month_ganzhi_available'],'年支冲与月干庚作为书中结案时间判断'),
 ('teacher_sentence_duration',3,158,['sentencing_duration_asked','zhishi_or_hour_stem_palace_known'],'老师事后提供两种取刑期数法，不重写原分析'),
 ('son_question_hour',4,185,['parent_asking_about_son','hour_stem_palace_known'],'时干兼儿子和所问事件；按源书受问关系取用'),
 ('son_birth_year',4,187,['parent_asking_about_son','son_birth_stem_known'],'儿子年命丙为用神，书中判断劫车罪案'),
 ('duration_zhishi_six_seven',4,189,['criminal_sentencing_asked','zhishi_palace_known'],'书内原作者判六七年和冬月开庭，报告七年')
]
def sha(b):return hashlib.sha256(b).hexdigest()
def js(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'))
def part(L,a,b=None):
 b=a if b is None else b
 if not 1<=a<=b<=len(L):raise ValueError(('Bad original source line',a,b))
 return '\n'.join(L[a-1:b])
def validate(raw):
 if len(raw)!=19964 or sha(raw)!=SOURCE_SHA or not raw.endswith(b'\n'):
  raise ValueError('Original uploaded chapter bytes/SHA mismatch')
 L=raw.decode('utf8').splitlines()
 if len(L)!=203 or L[0]!='第二章 日常百事预测评析' or L[2]!=TITLE:
  raise ValueError('Original 203 lines chapter title mismatch')
 if [i for i,s in enumerate(L,1) if s.startswith('（例')]!=[5,48,104,162]:
  raise ValueError('Exactly four original complete source cases required')
 for n,phrase in [(15,'原OCR残缺'),(59,'依原OCR'),(121,'按原OCR'),(168,'由原OCR'),
  (102,'不够规范'),(158,'不规范'),(193,'未能看出'),(203,'难以穷尽')]:
  if phrase not in L[n-1]:raise ValueError(('Critical source caution missing',n,phrase))
 return L
NUMBERS=(4,9,2,3,5,7,8,1,6)
def transcribed_palaces(L,first,last):
 if last-first!=13:raise ValueError('Rendered OCR panel expected 14 lines')
 cols=[]
 for start in (first+2,first+6,first+10):
  lines=[L[start-1+j] for j in range(3)]
  parts=[x.split('│')[1:-1] for x in lines]
  if any(len(c)!=3 for c in parts):raise ValueError(('Rendering OCR columns broken',first,start))
  for pos in range(3):
   text='\n'.join(parts[row][pos].strip() for row in range(3))
   cols.append((NUMBERS[len(cols)],start,parts[0][pos].strip(),parts[1][pos].strip(),parts[2][pos].strip(),text))
 if len(cols)!=9 or sorted(x[0] for x in cols)!=list(range(1,10)):
  raise ValueError('Transcribed grid nine unique positions expected')
 # center was written as a single stem in the middle layer only; never append gods/gates/stars
 center=next(v for v in cols if v[0]==5)
 if center[4].strip() or not any(x in center[3] for x in '庚辛壬癸戊己乙丙丁'):
  raise ValueError('Middle palace lacks source-only single stem')
 return cols
def unchanged(old,new):
 for (t,) in old.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"):
  cols=[x[1] for x in old.execute('PRAGMA table_info("'+t+'")')]
  selection=','.join('"'+x+'"' for x in cols)
  oldrows=list(old.execute('SELECT '+selection+' FROM "'+t+'"'))
  newer=set(new.execute('SELECT '+selection+' FROM "'+t+'"'))
  if any(x not in newer for x in oldrows):raise ValueError('Previous sourced history mutated in '+t)
def phase(db,L,cid,name,kind,a,b,extra=None):
 text=part(L,a,b)
 db.execute("""INSERT INTO kaiwu_litigation_source_phases
  (chapter_key,case_id,phase_key,phase_type,first_line,last_line,source_original,excerpt_sha256,metadata_json)
  VALUES (?,?,?,?,?,?,?,?,?)""",
  (CHAPTER,cid,name,kind,a,b,text,sha(text.encode()),js(extra or {'source':'kaiwu','post_disclosure_not_initial':kind!='initial_known'})))
def author_step(db,L,sid,cid,e,k,n,speaker):
 txt=part(L,n)
 fact={'source_book':'kaiwu','speaker':speaker,
  'domain':'litigation','posthoc':speaker=='zhang_critic_after_feedback',
  'real_world_evidence_unverified':True,
  'lexical_portions_not_verified_plate_positions':True,
  'source_lexical_concepts':sorted(set(re.findall(r'(?:值符|天乙|开门|景门|日干|时干|伤门|六合|白虎|旬空)',txt))),
  'initial_questioner_role':'company' if e is CASES[0] else ('spouse' if e in CASES[1:3] else 'father_of_suspect'),
  'unknown_case_differences_not_silently_reconciled':True,
  'original_author_method_may_be_criticized':speaker=='zhang_critic_after_feedback',
  'positive_training_eligible':False,'case_topic':e['name']}
 db.execute("""INSERT INTO kaiwu_litigation_author_steps
  (chapter_key,case_id,step_number,speaker,first_line,last_line,original_text,excerpt_sha256,reasoning_json)
  VALUES (?,?,?,?,?,?,?,?,?)""",
  (CHAPTER,cid,k,speaker,n,n,txt,sha(txt.encode()),js(fact)))
 concept=f"litigation:kaiwu:case{CASES.index(e)+1:02d}:step{k:02d}"
 db.execute("""INSERT INTO semantic_assertions(chapter_key,concept_id,kind,relation,
  source_start_line,source_end_line,metadata_json,original_excerpt,review_status)
  VALUES (?,?,'litigation_historical_reasoning','source_specific_argument_no_scientific_validity',?,?,?,?,'draft')""",
  (CHAPTER,concept,n,n,js(fact),txt))
 db.execute("""INSERT INTO cross_book_concept_tracks(chapter_key,concept_id,
  source_start_line,source_end_line,source_section_id,source_sha256,excerpt_sha256,
  track_id,relation_to_prior,comparison_state,normalized_json,review_status)
  VALUES (?,?,?,?,?,?,?,?,?,'book_source_only_no_independent_verification',?,'draft')""",
  (CHAPTER,concept,n,n,sid,SOURCE_SHA,sha(txt.encode()),'litigation:author_evidence_conditions','additional_exposition',js(fact)))
 if speaker=='original_analyst':
  step=db.execute('SELECT COUNT(*) FROM historical_case_reasoning WHERE case_id=?',(cid,)).fetchone()[0]+1
  db.execute("""INSERT INTO historical_case_reasoning
   (case_id,step_number,source_line,author_analysis_original,short_method_topic,metadata_json)
   VALUES (?,?,?,?,?,?)""",(cid,step,n,txt,'litigation_source_evidence_chain',js(fact)))
  db.execute("""INSERT INTO historical_case_reasoning_trace(case_id,step_number,
   source_line,evidence_json,review_status,positive_training_eligible)
   VALUES (?,?,?,?,'draft_source_not_blind_or_professionally_verified',0)""",(cid,step,n,js(fact)))
def build(base,source,output,index):
 base,source,output,index=map(Path,(base,source,output,index))
 if output.exists():raise ValueError('Never overwrite old versioned SQLite snapshot')
 if sha(base.read_bytes())!=BASE_SHA:raise ValueError('Not the required true 175-event full baseline SHA')
 raw=source.read_bytes();L=validate(raw);output.parent.mkdir(parents=True,exist_ok=True)
 with sqlite3.connect('file:'+str(base.resolve())+'?mode=ro',uri=True) as old,sqlite3.connect(output) as db:
  old.backup(db)
  db.executescript((ROOT/'schema/migrations/035_kaiwu_litigation_four_source_ocr_panels.sql').read_text('utf8'))
  db.execute('PRAGMA foreign_keys=ON')
  with db:
   if db.execute("SELECT COUNT(*) FROM sections WHERE book_id='kaiwu'").fetchone()[0]!=19:
    raise ValueError('Previous Kaiwu count must be 19')
   for n in range(1,7):
    if not db.execute('SELECT 1 FROM cases WHERE case_id=?',(f'shenqi.litigation.case{n:02d}',)).fetchone():
     raise ValueError('Missing previous Shenqi litigation families; never replace')
   db.execute("""INSERT INTO sections(book_id,section_key,title,original_text,sha256,content_version,reviewed)
     VALUES ('kaiwu',?,?,?,?,1,1)""",(SECTION,TITLE,raw.decode('utf8'),SOURCE_SHA))
   sid=db.execute('SELECT last_insert_rowid()').fetchone()[0]
   db.execute("""INSERT INTO chapter_knowledge(chapter_key,book_id,title,source_sha256,
    source_length_bytes,knowledge_version,review_status)
    VALUES (?,'kaiwu',?,?,?,'1','draft')""",(CHAPTER,TITLE,SOURCE_SHA,len(raw)))
   for i,e in enumerate(CASES):
    cid=e['id'];rawpanel=part(L,*e['panel'])
    metadata={'source_original_span':e['span'],'source_uncertainty':True,
      'user_txt_is_reconstructed_OCR_not_external_original_grid':True,
      'not_a_trustworthy_certified_new_nine_palace':True,'book_case_accepted':True,
      'author_report_not_independent_criminal_or_civil_proof':True,
      'source_note':e['note']}
    original_steps='\n\n'.join(part(L,n) for n in e['steps'])
    judgments='\n'.join(part(L,*t) for t in e['judge'])
    feedback='\n'.join(part(L,*t) for t in e['feedback'])
    db.execute("""INSERT INTO cases(case_id,section_id,event_family_id,domain_id,
     known_before,author_yongshen_steps,author_judgment,later_feedback,reviewed)
     VALUES (?,?,?,'litigation',?,?,?,?,1)""",
     (cid,sid,cid,part(L,*e['initial']),original_steps,judgments,feedback))
    db.execute("""INSERT INTO historical_case_protocol(
     case_id,completeness,published_chart_verification,
     feedback_independently_verified,eligible_blind_test,case_source_sha256,metadata_json)
     VALUES (?,'complete_printed_story_with_uncertain_transcribed_OCR_panel',
     'editorially_reassembled_OCR_not_certified_original_chart',0,0,?,?)""",
     (cid,SOURCE_SHA,js(metadata)))
    db.execute("""INSERT INTO historic_book_case_acceptance(case_id,source_book,
     source_chapter_key,source_documented_outcome,metadata_json)
     VALUES (?,'kaiwu',?,'source_reported_outcome_not_independent_judicial_records',?)""",
     (cid,CHAPTER,js(metadata)))
    for n,dom in enumerate(['litigation']+e['intro']):
     db.execute("""INSERT INTO unified_case_domain_facets(
      case_id,domain_id,source_chapter_key,primary_domain,note)
      VALUES (?,?,?,?,?)""",(cid,dom,CHAPTER,int(n==0),e['note']))
    db.execute("""INSERT INTO kaiwu_litigation_source_panels
     (chapter_key,case_id,range_start,range_end,original_source_text,source_sha256,provenance_class)
     VALUES (?,?,?,?,?,?,'user_transcribed_OCR_reconstruction_uncertainties')""",
     (CHAPTER,cid,*e['panel'],rawpanel,sha(rawpanel.encode())))
    for n in range(e['panel'][0],e['panel'][1]+1):
     txt=part(L,n)
     db.execute("""INSERT INTO kaiwu_litigation_panel_lines VALUES (?,?,?,?,?)""",
      (CHAPTER,cid,n,txt,sha(txt.encode())))
    for pos,line,deity,door,star,whole in transcribed_palaces(L,*e['panel']):
     # These are positions AS RENDERED in user text; DO NOT insert historical_chart_cells.
     db.execute("""INSERT INTO kaiwu_litigation_transcribed_palaces
      (chapter_key,case_id,palace,deity_literal,door_literal,star_literal,
       printed_layer_line_start,source_cell_text,source_cell_sha256,provenance_class,
       center_unprinted_deity_door_star)
      VALUES (?,?,?,?,?,?,?,?,?,
       'structured_from_uncertain_user_transcription_not_verified_original_plate',?)""",
      (CHAPTER,cid,pos,deity,door,star,line,whole,sha(whole.encode()),int(pos==5)))
    phase(db,L,cid,'initial','initial_known_context_without_later_answers',*e['initial'])
    phase(db,L,cid,'chart','user_OCR_reconstructed_panel_not_true_original_plate',*e['panel'])
    for k,(a,b) in enumerate(e['judge'],1):
     phase(db,L,cid,'prediction_'+str(k),'original_book_pre_feedback_assertion',a,b)
    for k,(a,b) in enumerate(e['feedback'],1):
     phase(db,L,cid,'feedback_'+str(k),'book_reported_later_verification',a,b)
    for key,a,b in e['after']:
     phase(db,L,cid,key,'information_disclosed_after_previous_answer',a,b)
    for k,n in enumerate(e['steps']+e['teacher'],1):
     phase(db,L,cid,'author_step_'+str(k),
      'teacher_later_methodology_criticism' if n in e['teacher'] else 'original_analyst_arguments',n,n)
     author_step(db,L,sid,cid,e,k,n,
      'zhang_critic_after_feedback' if n in e['teacher'] else 'original_analyst')
    db.execute("""INSERT INTO historical_case_review_audit(case_id,original_steps,
     mechanical_step_trace,human_complete_step_chains,review_status,warning)
     VALUES (?,?,?,0,'accepted_book_source_causality_draft',?)""",
     (cid,len(e['steps']),len(e['steps']),e['note']))
    db.execute("""INSERT INTO historical_case_book_verdicts(
     event_family_id,primary_case_id,verdict,explicit_source_correction,
     source_correction_lines_json,feedback_source_lines_json,
     independent_external_verification,app_output_protocol,evidence_review_status,note)
     VALUES (?,?,'author_book_success_default',0,'[]',?,
      'not_verified','single_answer_for_one_cast','accepted_book_report_methods_draft',?)""",
     (cid,cid,js([x[0] for x in e['feedback']]),e['note']))
   for idx,ln,lines in [(2,102,[94]),(3,158,[152,154]),(3,160,[154])]:
    e=CASES[idx-1];t=part(L,ln)
    db.execute("""INSERT INTO kaiwu_litigation_source_timing_criticisms
     (chapter_key,case_id,critic_line,original_author_method_lines_json,
      teacher_original_text,source_sha256,scope)
     VALUES (?,?,?,?,?,?,?)""",
     (CHAPTER,e['id'],ln,js(lines),t,sha(t.encode()),
      'original_method_not_normative_teacher_after_outcome'))
   # Out-of-scope later death was not anticipated; do NOT raise the source event
   # legal forecast's wrong-label count. Preserve missed scope separately.
   phase(db,L,CASES[3]['id'],'missed_unasked_family_death',
    'book_explicitly_not_predicted_side_incident_not_first_legal_outcome_failure',193,193)
   phase(db,L,CASES[3]['id'],'teacher_after_death',
    'hindsight_only_cannot_be_prior_hazard_prediction',203,203)
   for e,key,a,b,kind in [
    (CASES[3],'case04_hour_stem_placement_conflict',185,170,'book_narrative_says_hour_stem_Kun_but_transcribed_panel_has_Lin_in_Xun'),
    (CASES[0],'case01_time_stem_underlying_stem_uncertainty',34,18,'author_says_wu_under_geng_but_reassembled_panel_ambiguous')]:
    l1=part(L,a);l2=part(L,b)
    db.execute("""INSERT INTO kaiwu_litigation_source_claim_conflicts
     (chapter_key,case_id,conflict_key,source_line_one,source_line_two,
      claim_one,claim_two,conflict_kind) VALUES (?,?,?,?,?,?,?,?)""",
      (CHAPTER,e['id'],key,a,b,l1,l2,kind))
   for key,n,ln,conditions,summary in METHODS:
    e=CASES[n-1];txt=part(L,ln)
    info={'all':[{'fact':x,'required':True} for x in conditions],
      'unknown':'insufficient_source_evidence_or_unknown_questioner_relationship',
      'disallowed_without_real_world_court_documentation':True}
    db.execute("""INSERT INTO kaiwu_litigation_conditional_methods
     (chapter_key,method_key,source_line,source_case_id,source_original,conditions_json,
      reasoning_summary,critical_limits_json)
     VALUES (?,?,?,?,?,?,?,?)""",
     (CHAPTER,key,ln,e['id'],txt,js(info),summary,
      js({'not_professionally_approved':True,'no_independent_judicial_validation':True,
          'different_questioner_person_role_requires_reselection':True})))
    meta={'source_original_line':ln,'source_case':e['id'],
     'method_conditions':info,'source_only_not_normative':True,
     'negative_evidence_not_silently_reconciled':True}
    concept='litigation:kaiwu:method:'+key
    db.execute("""INSERT INTO semantic_assertions
     (chapter_key,concept_id,kind,relation,source_start_line,source_end_line,
      metadata_json,original_excerpt,review_status)
     VALUES (?,?,'conditional_litigation_book_method',
      'draft_rule_requires_context_and_sources',?,?,?,?,'draft')""",
     (CHAPTER,concept,ln,ln,js(meta),txt))
    db.execute("""INSERT INTO cross_book_concept_tracks
     (chapter_key,concept_id,source_start_line,source_end_line,source_section_id,
      source_sha256,excerpt_sha256,track_id,relation_to_prior,comparison_state,normalized_json,review_status)
     VALUES (?,?,?,?,?,?,?,?,?,
      'source_not_independent_science_or_legal_truth',?,'draft')""",
     (CHAPTER,concept,ln,ln,sid,SOURCE_SHA,sha(txt.encode()),
      'litigation:conditional_method_shared_books','additional_exposition',js(meta)))
   db.execute("""INSERT INTO chapter_archival_versions(
    archive_label,baseline_sha256,new_db_sha256,contains_complete_private_copyright_source,
    snapshot_type,created_utc,repo_public_archive_policy)
    VALUES (?, ?,NULL,1,'kaiwu_litigation_four_events_OCR_uncertainty_preserving',
    '2026-10-21','user_authorized_public_full_sqlite_versions')""",
    ('shenqi21_kaiwu20_litigation_179cases',BASE_SHA))
  unchanged(old,db)
  exp={'sections':41,'cases':179,'historical_chart_cells':1440,
   'historical_case_additional_casts':19,'historical_case_additional_cast_cells':171,
   'historical_palace_standardization':1611,'historical_case_reasoning':952,
   'historical_case_reasoning_trace':952,
   'semantic_assertions':2692,'cross_book_concept_tracks':1435,
   'historic_book_case_acceptance':71,'unified_case_domain_facets':119,
   'kaiwu_litigation_source_panels':4,'kaiwu_litigation_panel_lines':56,
   'kaiwu_litigation_transcribed_palaces':36,
   'kaiwu_litigation_author_steps':25,
   'kaiwu_litigation_conditional_methods':16,
   'kaiwu_litigation_source_timing_criticisms':3,
   'kaiwu_litigation_source_claim_conflicts':2}
  got={t:db.execute('SELECT COUNT(*) FROM "'+t+'"').fetchone()[0] for t in exp}
  if got!=exp:raise ValueError(('Counts mismatch; cannot silently modify historic data',got,exp))
  if db.execute("""SELECT COUNT(*) FROM historical_case_book_verdicts
    WHERE verdict='author_book_error_explicit'""").fetchone()[0]!=11:
   raise ValueError('All 11 original explicitly wrong outcomes MUST remain; new out-of-scope miss is separate')
  if db.execute('PRAGMA integrity_check').fetchone()[0]!='ok' or db.execute('PRAGMA foreign_key_check').fetchall():
   raise ValueError('Failed SQLite foreign key or integrity')
  db.execute('VACUUM');db.commit()
 index.mkdir(parents=True,exist_ok=True)
 data={'schema':'kaiwu_litigation_four_events_ocr_renders_not_certified_v1',
  'source_title':TITLE,'source_sha256':SOURCE_SHA,'source_bytes':len(raw),'source_lines':len(L),
  'book_complete_events':4,'new_distinct_event_families':4,
  'matched_old_shenqi_litigation_events':0,'unified_domain':'litigation',
  'rendered_source_panels':4,'user_transcribed_uncertain_plate_cells':36,
  'true_new_certified_original_nine_palaces':0,'printed_panel_rows':56,
  'new_source_original_study_steps':25,'original_analyst_steps':19,
  'teacher_post_event_criticism_steps':6,'conditional_workflow_methods':len(METHODS),
  'initial_future_results_separated':True,
  'case4_unasked_relative_death_missed_and_teacher_hindsight_not_predicted':True,
  'case2_and_3_timing_methods_critiqued_after_outcome':True,
  'case3_initial_sentence_3_to_5_actual_after_adjustment_5':True,
  'case4_chart_narrative_conflict_retained':True,
  'existing_book_11_error_cases_preserved':True,
  'no_independent_court_case_or_guilt_verification':True,
  'parent_sha256':BASE_SHA,'new_database_sha256':sha(output.read_bytes()),
  'all_old_rows_preserved':True,'counts':got,'positive_training_approved':0}
 def dump(name,obj):(index/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n','utf8')
 dump('chapter_manifest.json',data)
 dump('case_index.json',{'source_sha256':SOURCE_SHA,'cases':[{
  'case_id':e['id'],'source_span':e['span'],'source_rendered_OCR_panel':e['panel'],
  'author_original_lines':e['steps'],'teacher_after_fact_lines':e['teacher'],
  'initial_prediction_lines':e['judge'],'later_feedback_lines':e['feedback'],
  'questioner_context_lines':e['initial'],'source_limitations':e['note'],
  'not_original_print_verified_nine_palace':True,'domain_facets':e['intro']} for e in CASES]})
 dump('conditioned_methods.json',{'source_sha256':SOURCE_SHA,'methods':[{
  'key':key,'source_case':CASES[n-1]['id'],'line':ln,
  'conditions':{'all':[{'fact':x,'required':True} for x in conditions],
  'unknown':'insufficient_evidence'},
  'book_author_summary':summary,'approved':False} for key,n,ln,conditions,summary in METHODS]})
 dump('source_audit.json',{'source_sha256':SOURCE_SHA,'ocr_rendered_panels':[
  {'case':e['id'],'original_span':e['panel'],
   'line_sha256':[{'line':n,'sha':sha(part(L,n).encode())}
    for n in range(e['panel'][0],e['panel'][1]+1)]} for e in CASES],
  'no_book_original_palace_certification':True,
  'first_prediction_and_post_feedback_separated':True,
  'teacher_after_released_date_analyses_not_initial_pred':True,
  'case4_relative_dead_unpredicted_not_case_success':True,
  'original_uncertain_OCR_gaps_not_filled':True})
 return data
def main():
 p=argparse.ArgumentParser()
 for key in ('base','source','output','index-dir'):p.add_argument('--'+key,required=True)
 a=p.parse_args();print(js(build(a.base,a.source,a.output,a.index_dir)))
if __name__=='__main__':main()
