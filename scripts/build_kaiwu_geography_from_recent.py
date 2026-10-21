"""No-loss append of Kaiwu Fengshui: old Wu cemetery = shenqi.geography.case02.

The new chapter gives FIVE missing author steps to an existing complete event.
The two remaining episodes are different complete book events, not validated
science of geomancy, property ownership, historical suicide or engineering.
Three flattened OCR diagrams are only exact literal witnesses, never mapped cells.
"""
from __future__ import annotations
import argparse,hashlib,json,re,sqlite3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE_SHA='31f0ec9382dbe5adf4f254b732b473e163a15e7ff3ae2e482797c966a7ec78f3'
SOURCE_SHA='612c64b12172ffc50378323a1035da5d55eda3913f73bc408392da82c48a72d3'
BASE_NAME='WenguaApp_神奇之门21章_开悟之门18节_173案例_完整研究库.sqlite3'
NEW_NAME='WenguaApp_神奇之门21章_开悟之门19节_175案例_完整研究库.sqlite3'
SECTION='fengshui_geography_ch02_section14'
CHAPTER='kaiwu/'+SECTION+'/v1'
TITLE='第十四节 地理风水预测(共3例)'
CASES=[
 {'id':'shenqi.geography.case02','label':'吴先生拟选墓地与王庆丰原案后书五条新解','span':(3,35),
  'panel':(8,22),'initial':(3,6),'steps':[26,28,30,32,34],
  'feedback':None,'judgment':None,'same_old':True,'geo_type':'burial_plot',
  'facets':[], 'note':'same 1998-03-05 19:20 戊戌 Wu cemetery from Shenqi. Preserve old initial result, new five author reasonings'},
 {'id':'kaiwu.geography.case02','label':'石家庄东龙花园商品楼适居与20万元购房咨询','span':(36,73),
  'panel':(42,54),'initial':(37,40),'steps':[58,60,62,64,66,68,70],
  'feedback':(71,72),'judgment':(58,70),'same_old':False,
  'geo_type':'living_home','facets':['real_estate_purchase'],
  'note':'The book reports actual 20万元 quote and signed pre-sale agreement while house was not yet built; no later residence-quality outcome'},
 {'id':'kaiwu.geography.case03','label':'贾双萍北京昌平宅基地订金与归还纠纷咨询','span':(74,103),
  'panel':(83,95),'initial':(75,81),'steps':[99,101],
  'feedback':(103,103),'judgment':(102,102),'same_old':False,
  'geo_type':'residential_land','facets':['real_estate_purchase'],
  'note':'Reported historical death stories and loss of 10000-yuan deposit are book testimony, no independent ownership/suicide records; not engineering proof'}
]
# Every candidate is tied to a specific authored statement; never create
# an unconditional universal fengshui verdict or positive-training rule.
METHODS=[
 ('burial_si_door',1,26,'burial_plot',['question_is_burial_plot','death_door_palace_known'],'Traditional burial plot: use 死门 and conditionally inspect strength, month and door/star/stem.'),
 ('burial_time_stem',1,28,'burial_plot',['question_is_burial_plot','hour_stem_palace_known'],'Also check 时干 representing the specific grave plot.'),
 ('burial_questioner_relation',1,32,'burial_plot',['question_is_burial_plot','day_stem_and_hour_stem_palaces_known'],'Consider questioner day stem in relation to grave and hour-stem palace.'),
 ('burial_locks_metaphor',1,34,'burial_plot',['question_is_burial_plot','source_literary_deity_and_door_claims_known'],'Book analogies of lock, metal pins and clandestine ownership; not property title evidence.'),
 ('home_day_hour',2,62,'living_home',['question_is_residential_purchase','day_hour_stem_relationship_known'],'Day stem=person, hour stem=residence, check mutual palace relation.'),
 ('home_sheng_gate',2,64,'living_home',['question_is_residential_purchase','sheng_door_and_star_deity_known'],'Conditionally use 生门 to evaluate book-described residential environment.'),
 ('home_year_life',2,66,'living_home',['question_is_residential_purchase','person_year_stem_branch_known'],'Source adds 年命 and 地支 for occupant when provided.'),
 ('home_price_capital',2,70,'living_home',['question_is_residential_purchase','capital_symbol_available'],'Source book chooses 戊寄坤二 and 土囚 as number 2; no general numeric pricing rule.'),
 ('land_si_door',3,99,'residential_land',['question_is_land_building_plot','death_door_and_palace_known'],'Use 死门 for宅基地 and additional 格局/星/击刑, not infer real death from symbols.'),
 ('land_hour_stem',3,101,'residential_land',['question_is_land_building_plot','hour_stem_palace_known'],'Check 时干 and specific secondary signs; literal book claim, no verified death evidence.'),
 ('land_onsite_confirmation',3,102,'residential_land',['question_is_land_building_plot','on_site_evidence_unknown'],'Book advises field investigation before decision; independently verify factual claims.')
]
def sha(b):return hashlib.sha256(b).hexdigest()
def js(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'))
def literal(L,a,b=None):
 b=a if b is None else b
 if not 1<=a<=b<=len(L):raise ValueError(('Source span bounds',a,b,len(L)))
 return '\n'.join(L[a-1:b])
def validate(raw):
 if len(raw)!=7161 or sha(raw)!=SOURCE_SHA or not raw.endswith(b'\n'):
  raise ValueError('Uploaded 7161 bytes and SHA, exact newline required')
 L=raw.decode('utf8').splitlines()
 if len(L)!=103 or L[0]!=TITLE:raise ValueError('Original 103 lines/title mismatch')
 if [i for i,s in enumerate(L,1) if s.startswith('(例')]!=[3,36,74]:
  raise ValueError('Source must have exactly 3 old/new full cases')
 if '《神奇之门》书中测阴宅的一个实例' not in L[3]:raise ValueError('Prior event provenance missing')
 if '1998年3月5日19点20分' not in L[4] or '戊戌时' not in L[5]:raise ValueError('Old Wu event identity does not match')
 if '预售房合同' not in L[71] or '房屋尚未盖好' not in L[71]:
  raise ValueError('Unfinished presale residence phase important')
 if '实地调查' not in L[101] or '一万元订金' not in L[102]:raise ValueError('Building plot time-order missing')
 if L[53]!='开  乙 心 ，乙':raise ValueError('Unusual exact source OCR punctuation must be preserved')
 return L
def old_rows_unchanged(old,new):
 for (t,) in old.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"):
  cols=[r[1] for r in old.execute('PRAGMA table_info("'+t+'")')]
  s=','.join('"'+v+'"' for v in cols)
  before=list(old.execute('SELECT '+s+' FROM "'+t+'"'))
  after=set(new.execute('SELECT '+s+' FROM "'+t+'"'))
  if any(r not in after for r in before):raise ValueError('Historical original row overwritten: '+t)
def phase(db,L,w,key,kind,a,b,meta=None):
 txt=literal(L,a,b)
 db.execute("""INSERT INTO kaiwu_geography_source_phases(
  witness_key,phase_key,phase_kind,source_start_line,source_end_line,original_text,excerpt_sha256,metadata_json)
  VALUES (?,?,?,?,?,?,?,?)""",(w,key,kind,a,b,txt,sha(txt.encode()),js(meta or {'source_only':True})))
def add_author_step(db,L,sid,e,w,num,ln):
 txt=literal(L,ln)
 fields={'source_book':'kaiwu','book_case_accepted_without_individual_review':True,
  'original_author_step_not_added_event':e['same_old'],
  'original_OCR_spatially_unresolved':True,
  'claimed_palaces_not_original_printed_palace_cells':True,
  'domain_track':e['geo_type'],
  'conditional_observations_as_source_only':True,
  'positive_training_eligible':False,'independent_engineering_or_land_title_verification':False,
  'source_lexical_palace_candidates':sorted(set(re.findall(r'[乾坤震巽离坎艮兑][1-9]宫',txt))),
  'source_lexical_door_candidates':sorted(set(re.findall(r'[开休生伤杜景死惊]门',txt))),
  'contrary_evidence':'Author claim vs title/field verification unresolved; do not treat metaphoric inference as documented land fact'}
 db.execute("""INSERT INTO kaiwu_geography_author_steps(witness_key,step_index,
  first_line,last_line,original_author_text,excerpt_sha256,evidence_json,source_stage)
  VALUES (?,?,?,?,?,?,?,'book_author_post_event_explanation' )""",
  (w,num,ln,ln,txt,sha(txt.encode()),js(fields)))
 key=f"geography:kaiwu:{'reprint_wu' if e['same_old'] else e['id'].split('.')[-1]}:step{num:02d}"
 db.execute("""INSERT INTO semantic_assertions(chapter_key,concept_id,kind,relation,
  source_start_line,source_end_line,metadata_json,original_excerpt,review_status)
  VALUES (?,?, 'geography_source_analytic_step','distinct_later_book_witness',?,?,?,?,'draft')""",
  (CHAPTER,key,ln,ln,js(fields),txt))
 db.execute("""INSERT INTO cross_book_concept_tracks(chapter_key,concept_id,
  source_start_line,source_end_line,source_section_id,source_sha256,excerpt_sha256,
  track_id,relation_to_prior,comparison_state,normalized_json,review_status)
  VALUES (?,?,?,?,?,?,?,?,?,'source_traditional_not_independent_science',?,'draft')""",
  (CHAPTER,key,ln,ln,sid,SOURCE_SHA,sha(txt.encode()),'kaiwu:geography:'+e['geo_type'],
   'clarifies' if e['same_old'] else 'additional_exposition',js(fields)))
 if not e['same_old']:
  cid=e['id']
  db.execute("""INSERT INTO historical_case_reasoning(case_id,step_number,source_line,
   author_analysis_original,short_method_topic,metadata_json)
   VALUES (?,?,?,?,?,?)""",(cid,num,ln,txt,'geography_conditional_source_only',js(fields)))
  db.execute("""INSERT INTO historical_case_reasoning_trace(case_id,step_number,source_line,
   evidence_json,review_status,positive_training_eligible)
   VALUES (?,?,?,?,'book_source_draft_no_geotechnical_validation',0)""",(cid,num,ln,js(fields)))
def build(parent,source,out,index):
 parent,source,out,index=map(Path,(parent,source,out,index))
 if out.exists():raise ValueError('Never overwrite snapshot database')
 if sha(parent.read_bytes())!=BASE_SHA:raise ValueError('Exact 173-case full-parent SHA required')
 raw=source.read_bytes();L=validate(raw)
 out.parent.mkdir(parents=True,exist_ok=True)
 with sqlite3.connect('file:'+str(parent.resolve())+'?mode=ro',uri=True) as old,sqlite3.connect(out) as db:
  old.backup(db)
  db.executescript((ROOT/'schema/migrations/034_kaiwu_geography_crossbook_fengshui.sql').read_text('utf8'))
  db.execute('PRAGMA foreign_keys=ON')
  with db:
   if db.execute("SELECT count(*) FROM sections WHERE book_id='kaiwu'").fetchone()[0]!=18:
    raise ValueError('All 18 previous Kaiwu source chapters required')
   if not db.execute("""SELECT 1 FROM cases WHERE case_id='shenqi.geography.case02'
    AND domain_id='geography_environment_historical_source'""").fetchone():
    raise ValueError('Missing original Wu cemetery case: must be same prior event, NOT new')
   db.execute("""INSERT INTO sections(book_id,section_key,title,original_text,sha256,content_version,reviewed)
    VALUES ('kaiwu',?,?,?,?,1,1)""",(SECTION,TITLE,raw.decode(),SOURCE_SHA))
   sid=db.execute('SELECT last_insert_rowid()').fetchone()[0]
   db.execute("""INSERT INTO chapter_knowledge(chapter_key,book_id,title,source_sha256,
    source_length_bytes,knowledge_version,review_status)
    VALUES (?,'kaiwu',?,?,?,'1','draft')""",(CHAPTER,TITLE,SOURCE_SHA,len(raw)))
   for e in CASES:
    cid=e['id'];w=CHAPTER+'/'+cid
    info={'source_span':e['span'],'source_type':e['geo_type'],
     'cross_book_duplicate_event':e['same_old'],'new_unique_event':not e['same_old'],
     'source_only_not_professional_validation':True,'no_invented_chart_positions':True,
     'note':e['note']}
    if not e['same_old']:
     db.execute("""INSERT INTO cases(case_id,section_id,event_family_id,domain_id,
      known_before,author_yongshen_steps,author_judgment,later_feedback,reviewed)
      VALUES (?,?,?,'geography_environment_historical_source',?,?,?,?,1)""",
      (cid,sid,cid,literal(L,*e['initial']),
       '\n\n'.join(literal(L,n) for n in e['steps']),
       literal(L,*e['judgment']),literal(L,*e['feedback'])))
     db.execute("""INSERT INTO historical_case_protocol(case_id,completeness,
      published_chart_verification,feedback_independently_verified,eligible_blind_test,
      case_source_sha256,metadata_json)
      VALUES (?,'complete_book_story_with_unresolvable_printed_OCR',
       'no_certifiable_complete_source_nine_palace',0,0,?,?)""",
      (cid,SOURCE_SHA,js(info)))
     db.execute("""INSERT INTO historic_book_case_acceptance(case_id,source_book,source_chapter_key,
      source_documented_outcome,metadata_json)
      VALUES (?,'kaiwu',?,'book_report_only_not_independently_verified',?)""",
      (cid,CHAPTER,js(info)))
     for i,d in enumerate(['geography_environment_historical_source']+e['facets']):
      db.execute("""INSERT INTO unified_case_domain_facets(case_id,domain_id,
       source_chapter_key,primary_domain,note) VALUES (?,?,?,?,?)""",
       (cid,d,CHAPTER,int(i==0),e['note']))
     db.execute("""INSERT INTO historical_case_book_verdicts(event_family_id,primary_case_id,verdict,
      explicit_source_correction,source_correction_lines_json,feedback_source_lines_json,
      independent_external_verification,app_output_protocol,evidence_review_status,note)
      VALUES (?,?,'author_book_success_default',0,'[]',?,'not_verified',
      'single_answer_for_one_cast','source_report_not_external_ground_truth',?)""",
      (cid,cid,js([e['feedback'][0]]),e['note']))
     db.execute("""INSERT INTO historical_case_review_audit(
      case_id,original_steps,mechanical_step_trace,human_complete_step_chains,review_status,warning)
      VALUES (?,?,?,0,'book_case_accepted_methods_draft',?)""",
      (cid,len(e['steps']),len(e['steps']),e['note']))
    raw_panel=literal(L,*e['panel'])
    db.execute("""INSERT INTO kaiwu_geography_source_witnesses(
     witness_key,chapter_key,section_id,case_id,witness_relationship,initial_context_first_line,
     source_first_line,source_last_line,raw_panel_first_line,raw_panel_last_line,
     raw_panel_source,raw_panel_sha256,printed_palace_positions_status,metadata_json)
     VALUES (?,?,?,? ,?,?,?,?,?,?,?,?,'flattened_OCR_unresolved_no_certified_palaces',?)""",
     (w,CHAPTER,sid,cid,'same_shenqi_event_new_explanation' if e['same_old'] else 'new_geography_event',
      e['initial'][0],*e['span'],*e['panel'],raw_panel,sha(raw_panel.encode()),js(info)))
    for n in range(e['panel'][0],e['panel'][1]+1):
     t=literal(L,n)
     db.execute("""INSERT INTO kaiwu_geography_raw_lines(
      witness_key,source_line,original_line,excerpt_sha256) VALUES (?,?,?,?)""",
      (w,n,t,sha(t.encode())))
    phase(db,L,w,'initial_known','initial_question_or_crossbook_identity',*e['initial'],meta=info)
    phase(db,L,w,'printed_OCR','uncertain_spatial_source_raw_panel',*e['panel'])
    for i,n in enumerate(e['steps'],1):
     phase(db,L,w,'author_step_'+str(i),'new_book_original_author_analysis',n,n)
     add_author_step(db,L,sid,e,w,i,n)
    if e['feedback']:
     phase(db,L,w,'original_author_conclusion','book_initial_conclusion',*e['judgment'])
     phase(db,L,w,'book_feedback','later_report_not_initial_input',*e['feedback'])
     if cid.endswith('case02'):
      phase(db,L,w,'contract_not_occupied','presale_purchase_not_lived_in_success',71,72)
     if cid.endswith('case03'):
      phase(db,L,w,'field_research','author_advises_independent_on_site_checks',102,102)
      phase(db,L,w,'uncorroborated_third_party_tragedy','source_report_of_third_party_history_not_external_truth',103,103)
    else:
     phase(db,L,w,'later_book_reanalysis','new_analytic_witness_of_old_shenqi_case',26,34)
   for key,idx,ln,domain,conditions,scope in METHODS:
    e=CASES[idx-1];txt=literal(L,ln)
    db.execute("""INSERT INTO kaiwu_geography_method_candidates(chapter_key,method_key,
     source_first_line,source_last_line,domain_track,conditions_json,conclusion_scope,
     original_source,evidence_limitations_json)
     VALUES (?,?,?,?,?,?,?,?,?)""",
     (CHAPTER,key,ln,ln,domain,js({'all':[{'fact':v,'required':True} for v in conditions],
      'unknown':'insufficient_evidence_no_unconditional_verdict','independent_proof':False}),
      scope,txt,js({'book_source_only':True,'counterevidence_required':True,
        'must_verify_real_world_property_legal_or_engineering_claims':True,
        'corresponding_event_id':e['id'],'original_source_line':ln})))
   db.execute("""INSERT INTO chapter_archival_versions(
    archive_label,baseline_sha256,new_db_sha256,contains_complete_private_copyright_source,
    snapshot_type,created_utc,repo_public_archive_policy)
    VALUES (?, ?,NULL,1,'kaiwu_fengshui_one_old_source_witness_and_two_new_events_OCR',
    '2026-10-20','user_authorized_public_full_sqlite_versions')""",
    ('shenqi21_kaiwu19_geography_175events',BASE_SHA))
  old_rows_unchanged(old,db)
  expected={'sections':40,'cases':175,'historical_chart_cells':1440,
   'historical_case_additional_casts':19,'historical_case_additional_cast_cells':171,
   'historical_palace_standardization':1611,'historical_case_reasoning':933,
   'historical_case_reasoning_trace':933,'semantic_assertions':2651,
   'cross_book_concept_tracks':1394,'historic_book_case_acceptance':69,
   'unified_case_domain_facets':107,'kaiwu_geography_source_witnesses':3,
   'kaiwu_geography_raw_lines':41,'kaiwu_geography_author_steps':14,
   'kaiwu_geography_method_candidates':11}
  got={t:db.execute('SELECT count(*) FROM "'+t+'"').fetchone()[0] for t in expected}
  if got!=expected:raise ValueError(('Full archive counts mismatch',got,expected))
  if db.execute("SELECT count(*) FROM historical_case_book_verdicts WHERE verdict='author_book_error_explicit'").fetchone()[0]!=11:
   raise ValueError('Original eleven clear author errors changed')
  if db.execute("SELECT count(*) FROM cases WHERE case_id='shenqi.geography.case02'").fetchone()[0]!=1:
   raise ValueError('Duplicated old Wu event family')
  if db.execute('PRAGMA integrity_check').fetchone()[0]!='ok' or db.execute('PRAGMA foreign_key_check').fetchall():
   raise ValueError('Corrupt appended archive')
  db.execute('VACUUM');db.commit()
 index.mkdir(parents=True,exist_ok=True)
 manifest={'schema':'kaiwu_geography_three_source_witnesses_two_new_events_v1',
  'source_title':TITLE,'source_sha256':SOURCE_SHA,'source_bytes':len(raw),
  'source_lines':len(L),'book_examples':3,'new_unique_historical_events':2,
  'reprinted_prior_event_id':'shenqi.geography.case02',
  'new_source_OCR_panels':3,'new_certified_complete_original_nine_palaces':0,
  'original_flattened_panel_lines':41,'author_source_steps':14,
  'additive_new_case_author_steps':9,'reprinted_event_new_explanatory_steps':5,
  'conditional_source_method_candidates':len(METHODS),
  'old_179_complete_nine_palace_source_charts_retained':True,
  'new_live_in_residence_outcome_not_proven':True,
  'third_party_deaths_not_independently_documented':True,
  'source_for_Wu_cemetery_has_no_new_independent_prediction':True,
  'no_independent_geotechnical_or_property_rights_verification':True,
  'prior_11_explicit_author_errors_preserved':True,
  'parent_sha256':BASE_SHA,'new_archive_sha256':sha(out.read_bytes()),
  'all_prior_rows_unchanged':True,'counts':got,
  'professionally_approved_positive_training_cases':0}
 def dump(name,x):(index/name).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 dump('chapter_manifest.json',manifest)
 dump('case_index.json',{'source_sha256':SOURCE_SHA,'cases':[
  {'case_id':e['id'],'source_span':e['span'],'source_OCR_panel_lines':e['panel'],
   'source_analysis_step_lines':e['steps'],'same_event_in_old_shenqi':e['same_old'],
   'geo_type':e['geo_type'],'feedback_lines':e['feedback'],
   'book_claim_caveat':e['note'],'no_independent_real_world_validation':True} for e in CASES]})
 dump('method_candidates.json',{'source_sha256':SOURCE_SHA,'conditional_candidates':[
  {'method_key':k,'case_id':CASES[idx-1]['id'],'source_line':ln,'domain':domain,
   'conditions_json':{'all':[{'fact':v,'required':True} for v in cond],
    'unknown':'insufficient_evidence_no_unconditional_verdict'},
   'scope':scope,'source_original':literal(L,ln),'review_status':'draft'}
   for k,idx,ln,domain,cond,scope in METHODS]})
 dump('source_audit.json',{'source_sha256':SOURCE_SHA,
  'source_panels':[{'case_id':e['id'],'start_end':e['panel'],
   'row_hashes':[{'line':n,'sha256':sha(literal(L,n).encode())}
    for n in range(e['panel'][0],e['panel'][1]+1)]} for e in CASES],
  'source_middle_palace_not_assumed':True,'presale_without_living_feedback':True,
  'historical_ownership_claims_not_title_verification':True,
  'cross_book_same_event_not_new_case':True,'no_fabricated_original_chart_cells':True})
 return manifest
def main():
 p=argparse.ArgumentParser()
 for x in ('base','source','output','index-dir'):p.add_argument('--'+x,required=True)
 a=p.parse_args()
 print(js(build(a.base,a.source,a.output,a.index_dir)))
if __name__=='__main__':main()
