"""Incremental, source-exact Kaiwu lifetime section 16; NEVER rewrite 163 historical events.

The first 苏女士 source is the existing shenqi.life.case05, not another case.
All five source figures are OCR-flattened and must be stored literally as witnesses,
not fabricated as nine verified source palaces. The other four birth-time studies
are written with historical outcome already known and are NOT blind predictions.
"""
from __future__ import annotations
import argparse,hashlib,json,sqlite3,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE_SHA='72cba2eea151a4a515e2a3739243c2f6e73489ca0b7fd4845df19bf23dd8e74c'
SOURCE_SHA='f81d0c9e74923e39dff6a2ef04a8a303b851acb4fee1345b99a4e46c08728f01'
BASE_NAME='WenguaApp_神奇之门21章_开悟之门16节_163案例_完整研究库.sqlite3'
NEW_NAME='WenguaApp_神奇之门21章_开悟之门17节_167案例_完整研究库.sqlite3'
SECTION='lifetime_fate_prediction_ch02_section16'
CHAPTER='kaiwu/'+SECTION+'/v1'
TITLE='第十六节 人生终身命运预测(共5例)'
CASES=[
 {'id':'shenqi.life.case05','name':'苏女士1942出生盘后书19条补解','span':(3,83),'chart':(7,21),
  'known':(4,5),'heads':[26,28,31,34,37,40,43,46,49,52,55,58,61,64,67,70,73,77,80],
  'end':81,'same_prior':True,'editorial':[(82,82)]},
 {'id':'kaiwu.life.case02','name':'邵阳双胞胎姐姐既成车祸出生盘事后解析','span':(84,123),'chart':(88,104),
  'known':(85,86),'heads':[108,110,112,114,116,118],'end':118,'editorial':[(120,122)]},
 {'id':'kaiwu.life.case03','name':'河北吕玉兰出生盘事后生平分析','span':(124,181),'chart':(127,144),
  'known':(125,125),'heads':[148,150,152,154,156,158],'end':158,
  'years':list(range(161,181)),'editorial':[(160,160)]},
 {'id':'kaiwu.life.case04','name':'毛泽东出生盘事后历史分析','span':(182,236),'chart':(186,202),
  'known':(183,184),'heads':[206,208,210,212,214,216,218,220,222],'end':222,
  'years':list(range(225,236)),'editorial':[(224,224)]},
 {'id':'kaiwu.life.case05','name':'蒋介石出生盘及历史生平事后分析','span':(237,266),'chart':(241,258),
  'known':(238,239),'heads':[262,264,266],'end':266,'editorial':[]}
]
def sh(b):return hashlib.sha256(b).hexdigest()
def js(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'))
def lit(L,a,b=None):
 b=a if b is None else b
 if a<1 or b>len(L) or a>b:raise ValueError(('bad source anchor',a,b))
 return '\n'.join(L[a-1:b])
def validate(raw):
 if sh(raw)!=SOURCE_SHA or len(raw)!=26715 or not raw.endswith(b'\n'):
  raise ValueError('Original full UTF-8 file SHA/bytes/newline mismatch')
 L=raw.decode('utf8').splitlines()
 if len(L)!=266 or L[0]!=TITLE:raise ValueError('Incorrect original title or 266 source lines')
 if [i for i,s in enumerate(L,1) if s.startswith('(例')]!=[3,84,124,182,237]:
  raise ValueError('Original must contain five printed author example headings')
 if '此例在《神奇之门》一书中未做解析' not in L[3]:raise ValueError('Cross-book prior-event reference missing')
 if '1994年就是1995年' not in L[51] or '1996年病故' not in L[54]:
  raise ValueError('Original explicit initial wrong-year and later correction missing')
 if '局限性也是很大的' not in L[121]:raise ValueError('Twin author warning cannot be dropped')
 if '中风' not in L[178] or '文化大革命' not in L[233]:raise ValueError('Historical retrospective paragraphs missing')
 for e in CASES:
  if e['heads'][-1]>e['end']:raise ValueError('Invalid source steps')
 return L
def get_steps(L,e):
 h=e['heads'];out=[]
 for j,n in enumerate(h):
  stop=(h[j+1]-1 if j+1<len(h) else e['end'])
  while stop>n and not L[stop-1].strip():stop-=1
  out.append((n,stop,'book_author_numbered_analysis'))
 for n in e.get('years',[]):out.append((n,n,'retrospective_year_after_outcome_known'))
 return out
def append_source_step(db,L,w,e,sid,k,a,b,kind):
 t=lit(L,a,b)
 lexical=[f'{name}:{v}' for name,rgx in [('door',r'([开休生伤杜景死惊])门'),('star',r'天([蓬任冲辅英芮柱心禽])星'),('deity',r'(值符|玄武|白虎|六合|九天|九地|螣蛇|太阴)')]
  for v in sorted(set(re.findall(rgx,t)))]
 note={'source_book':'kaiwu','reused_prior_event':e.get('same_prior',False),
  'birth_time_post_outcome_retrospective':not e.get('same_prior',False),
  'source_keywords_only_not_verified_palace_links':lexical,
  'full_original_step_preserved':True,'author_book_case_accepted_without_individual_review':True,
  'positive_training_eligible':False,
  'independent_medical_historical_or_political_validity':False,
  'no_source_original_nine_palace_position_inference':True}
 db.execute("""INSERT INTO kaiwu_life_author_step_witnesses(
  witness_key,step_index,first_source_line,last_source_line,author_original_text,
  excerpt_sha256,phase_kind,evidence_json)
  VALUES (?,?,?,?,?,?,?,?)""",(w,k,a,b,t,sh(t.encode()),kind,js(note)))
 concept=f'life:kaiwu:section16:{e["id"].replace(".","_")}:step{k:02}'
 db.execute("""INSERT INTO semantic_assertions(chapter_key,concept_id,kind,relation,
  source_start_line,source_end_line,metadata_json,original_excerpt,review_status)
  VALUES (?,?,'book_source_lifetime_reasoning','additional_source_witness',?,?,?,?,'draft')""",
  (CHAPTER,concept,a,b,js(note),t))
 db.execute("""INSERT INTO cross_book_concept_tracks(chapter_key,concept_id,
  source_start_line,source_end_line,source_section_id,source_sha256,excerpt_sha256,
  track_id,relation_to_prior,comparison_state,normalized_json,review_status)
  VALUES (?,?,?,?,?,?,?,?,?,'source_retrospective_or_book_analysis_not_external_verification',?,'draft')""",
  (CHAPTER,concept,a,b,sid,SOURCE_SHA,sh(t.encode()),
   'kaiwu:lifetime:historical_birthtime_exposition', 
   'additional_exposition',js(note)))
 if not e.get('same_prior'):
  db.execute("""INSERT INTO historical_case_reasoning(
   case_id,step_number,source_line,author_analysis_original,short_method_topic,metadata_json)
   VALUES (?,?,?,?,?,?)""",(e['id'],k,a,t,'birth_time_historical_retrospective_not_forecast',js(note)))
  db.execute("""INSERT INTO historical_case_reasoning_trace(
   case_id,step_number,source_line,evidence_json,review_status,positive_training_eligible)
   VALUES (?,?,?,?,'draft_not_blind_prediction',0)""",(e['id'],k,a,js(note)))
def save_phase(db,L,w,key,kind,a,b):
 t=lit(L,a,b)
 db.execute("""INSERT INTO kaiwu_life_source_phases(
  witness_key,phase_key,phase_kind,source_start_line,source_end_line,
  exact_original_text,excerpt_sha256) VALUES (?,?,?,?,?,?,?)""",
  (w,key,kind,a,b,t,sh(t.encode())))
def old_rows_unchanged(old,now):
 for (tbl,) in old.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"):
  cols=[r[1] for r in old.execute('PRAGMA table_info("'+tbl+'")')]
  select=','.join('"'+c+'"' for c in cols)
  before=list(old.execute('SELECT '+select+' FROM "'+tbl+'"'))
  after=set(now.execute('SELECT '+select+' FROM "'+tbl+'"'))
  if any(x not in after for x in before):raise ValueError('Previous historical source row changed: '+tbl)
def build(base,source,output,index):
 base,source,output,index=map(Path,(base,source,output,index))
 if output.exists():raise ValueError('Never overwrite existing chapter archive')
 if sh(base.read_bytes())!=BASE_SHA:raise ValueError('Not the required full 163-event parent')
 raw=source.read_bytes();L=validate(raw)
 output.parent.mkdir(parents=True,exist_ok=True)
 with sqlite3.connect('file:'+str(base.resolve())+'?mode=ro',uri=True) as old,sqlite3.connect(output) as db:
  old.backup(db)
  db.executescript((ROOT/'schema/migrations/032_kaiwu_lifetime_crossbook_retrospectives.sql').read_text('utf8'))
  db.execute('PRAGMA foreign_keys=ON')
  with db:
   if db.execute("SELECT count(*) FROM sections WHERE book_id='kaiwu'").fetchone()[0]!=16:
    raise ValueError('Missing previous Kaiwu sections')
   if not db.execute("SELECT 1 FROM cases WHERE case_id='shenqi.life.case05' AND domain_id='life_opportunity_book_study'").fetchone():
    raise ValueError('Missing original Su woman event; must NOT double count')
   db.execute("""INSERT INTO sections(book_id,section_key,title,original_text,sha256,content_version,reviewed)
     VALUES ('kaiwu',?,?,?,?,1,1)""",(SECTION,TITLE,raw.decode('utf8'),SOURCE_SHA))
   sid=db.execute('SELECT last_insert_rowid()').fetchone()[0]
   db.execute("""INSERT INTO chapter_knowledge(chapter_key,book_id,title,source_sha256,
    source_length_bytes,knowledge_version,review_status)
    VALUES (?,'kaiwu',?,?,?,'1','draft')""",(CHAPTER,TITLE,SOURCE_SHA,len(raw)))
   for e in CASES:
    cid=e['id'];w=CHAPTER+'/'+cid;steps=get_steps(L,e)
    meta={'source_original_ocr_pane':e['chart'],'same_prior_event_id':'shenqi.life.case05' if e.get('same_prior') else None,
     'already_known_historical_outcomes_before_book_analysis':not e.get('same_prior',False),
     'historical_source_book_accepted_without_individual_review':True,
     'source_original_not_an_independently_verified_nine_palace_grid':True,'historical_fatality_and_political_claims_not_external_scientific_evidence':True}
    if not e.get('same_prior'):
     known=lit(L,*e['known']);analytic='\n\n'.join(lit(L,a,b) for a,b,_ in steps)
     db.execute("""INSERT INTO cases(case_id,section_id,event_family_id,domain_id,known_before,
      author_yongshen_steps,author_judgment,later_feedback,reviewed)
      VALUES (?,?,?,'life_opportunity_book_study',?,?,NULL,?,1)""",
      (cid,sid,cid,known,analytic,lit(L,*e['span'])))
     db.execute("""INSERT INTO historical_case_protocol(case_id,completeness,
      published_chart_verification,feedback_independently_verified,eligible_blind_test,
      case_source_sha256,metadata_json)
      VALUES (?,'complete_source_retrospective_story_flattened_OCR_witness',
      'original_source_OCR_fragment_not_certified_nine_palaces',0,0,?,?)""",
      (cid,SOURCE_SHA,js(meta)))
     db.execute("""INSERT INTO historic_book_case_acceptance(case_id,source_book,
      source_chapter_key,source_documented_outcome,metadata_json)
      VALUES (?,'kaiwu',?,'retrospective_lifetime_book_analysis_not_an_initial_prediction',?)""",
      (cid,CHAPTER,js(meta)))
     db.execute("""INSERT INTO unified_case_domain_facets(case_id,domain_id,source_chapter_key,primary_domain,note)
      VALUES (?,'life_opportunity_book_study',?,1,'One source event, known biography; no independent forecasting claim')""",
      (cid,CHAPTER))
     db.execute("""INSERT INTO historical_life_case_context(case_id,source_chart_line,cast_strategy,
      initial_context_json,retrospective_case,original_book_explicit_year_error,
      original_book_initial_years_json,source_revealed_year,source_method_missing_for_claims,
      scientific_independent_verification,metadata_json)
      VALUES (? ,?,'birth_time_post_outcome',?,1,0,'[]',NULL,1,0,?)""",
      (cid,e['chart'][0],js(e['known']),js(meta)))
     db.execute("""INSERT INTO historical_case_review_audit(case_id,original_steps,mechanical_step_trace,
      human_complete_step_chains,review_status,warning)
      VALUES (?,?,?,0,'book_source_accepted_no_positive_training',
      'Source states outcome before chart: retrospective interpretation, NOT a blind future prediction')""",
      (cid,len(steps),len(steps)))
    chart=lit(L,*e['chart'])
    db.execute("""INSERT INTO kaiwu_life_source_witnesses(witness_key,chapter_key,section_id,case_id,
     source_book,source_start_line,source_end_line,printed_chart_first_line,printed_chart_last_line,
     original_raw_chart,original_raw_chart_sha256,original_chart_spatial_status,witness_relationship,metadata_json)
     VALUES (?,?,?,?,'kaiwu',?,?,?, ?,? ,?,'flattened_OCR_no_source_position_certification',?,?)""",
     (w,CHAPTER,sid,cid,*e['span'],*e['chart'],chart,sh(chart.encode()),
      'same_prior_event_new_author_explanation' if e.get('same_prior') else 'new_retrospective_birth_time_study',js(meta)))
    for n in range(e['chart'][0],e['chart'][1]+1):
     one=lit(L,n)
     db.execute("""INSERT INTO kaiwu_life_original_chart_lines(witness_key,source_line,source_original,excerpt_sha256)
      VALUES (?,?,?,?)""",(w,n,one,sh(one.encode())))
    save_phase(db,L,w,'context','known_person_and_birth_context_not_new_forecast',*e['known'])
    save_phase(db,L,w,'raw_source_figure','original_flattened_OCR_no_certified_palace_positions',*e['chart'])
    for a,b in e.get('editorial',[]):save_phase(db,L,w,'editorial_line_'+str(a),
       'post_event_author_commentary_or_general_limitations',a,b)
    for k,(a,b,kind) in enumerate(steps,1):append_source_step(db,L,w,e,sid,k,a,b,kind)
    if e.get('same_prior'):
     save_phase(db,L,w,'explicit_wrong_1994_1995_and_1996_correction',
       'old_author_initial_error_reexamined_after_outcome_known',52,56)
     if db.execute("""SELECT verdict FROM historical_case_book_verdicts
      WHERE primary_case_id='shenqi.life.case05'""").fetchone()[0]!='author_book_error_explicit':
      raise ValueError('Previously admitted wrong death year is immutable')
    elif cid.endswith('case02'):
     save_phase(db,L,w,'twin_editor_limitations','author_warns_same_birth_chart_different_lives',120,122)
   db.execute("""INSERT INTO chapter_archival_versions(archive_label,baseline_sha256,new_db_sha256,
    contains_complete_private_copyright_source,snapshot_type,created_utc,repo_public_archive_policy)
    VALUES (?, ?,NULL,1,'kaiwu_lifetime_four_new_retrospective_events_one_shenqi_crossbook_source',
    '2026-10-20','user_authorized_public_full_sqlite_versions')""",
    ('shenqi21_kaiwu17_lifetime_167cases',BASE_SHA))
  old_rows_unchanged(old,db)
  expect={'sections':38,'cases':167,'historical_chart_cells':1440,
   'historical_case_additional_casts':19,'historical_case_additional_cast_cells':171,
   'historical_palace_standardization':1611,
   'historical_case_reasoning':889,'historical_case_reasoning_trace':889,
   'semantic_assertions':2586,'cross_book_concept_tracks':1329,
   'historic_book_case_acceptance':59,'unified_case_domain_facets':83,
   'kaiwu_life_source_witnesses':5,'kaiwu_life_author_step_witnesses':74,
   'kaiwu_life_original_chart_lines':85}
  got={t:db.execute('SELECT count(*) FROM "'+t+'"').fetchone()[0] for t in expect}
  if got!=expect:raise ValueError(('Invalid old+new counts',got,expect))
  if db.execute("SELECT count(*) FROM historical_case_book_verdicts WHERE verdict='author_book_error_explicit'").fetchone()[0]!=10:
   raise ValueError('Prior ten explicitly wrong initial source events altered')
  if db.execute("SELECT count(*) FROM cases WHERE case_id='shenqi.life.case05'").fetchone()[0]!=1:
   raise ValueError('Cross-book Su case was counted twice')
  if db.execute('PRAGMA integrity_check').fetchone()[0]!='ok' or db.execute('PRAGMA foreign_key_check').fetchall():
   raise ValueError('Archive failed SQLite integrity')
  db.execute('VACUUM');db.commit()
 index.mkdir(parents=True,exist_ok=True)
 out={'schema':'kaiwu_lifetime_5_source_witnesses_4_new_retrospective_birth_events_v1',
  'source_title':TITLE,'source_sha256':SOURCE_SHA,'source_lines':len(L),'source_bytes':len(raw),
  'five_book_examples':5,'new_unique_events':4,'reprinted_prior_event':'shenqi.life.case05',
  'total_independent_event_families':167,'prior_nine_palace_sources_unchanged':179,
  'new_source_printed_OCR_fragments':5,'new_original_palace_positions_certified':0,
  'source_OCR_rows_exact':85,'author_steps_full_original':74,
  'old_explicit_original_errors_retained':10,'first_case_year_error':{'initial':[1994,1995],'book_actual':1996,'not_corrected_as_initial_hit':True},
  'all_four_new_birth_time_studies_retrospective':True,
  'twins_same_birth_chart_different_outcomes_author_limitations_preserved':True,
  'author_political_claims_retained_as_source_not_adopted_as_verified_history':True,
  'independent_professional_validation':0,'approved_professional_rule_templates':0,
  'parent_sha256':BASE_SHA,'new_archive_sha256':sh(output.read_bytes()),
  'all_prior_rows_unchanged':True,'counts':got,'source_training_candidates_approved':0}
 def dump(n,x):(index/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf8')
 dump('chapter_manifest.json',out)
 dump('case_index.json',{'source_sha256':SOURCE_SHA,'cases':[
  {'case_id':e['id'],'label':e['name'],'source_span':e['span'],
   'source_OCR_chart_lines':e['chart'],'numbered_author_reasoning_lines':e['heads'],
   'historical_years_source_lines':e.get('years',[]),'new_event':not e.get('same_prior',False),
   'not_a_blind_prediction':True,'author_steps':len(get_steps(L,e))} for e in CASES]})
 dump('source_audit.json',{'source_sha256':SOURCE_SHA,
  'OCR_chart_rows':[{ 'case_id':e['id'],'range':e['chart'],
    'line_sha256':[sh(lit(L,n).encode()) for n in range(e['chart'][0],e['chart'][1]+1)]} for e in CASES],
  'no_fabricated_source_palace_cells':True,'first_case_reprint_not_second_independent_case':True,
  'book_retrospective_not_future_predictive_proof':True,'error_and_limitation_anchors':[55,56,120,121,122]})
 return out
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--base',required=True)
 ap.add_argument('--source',required=True);ap.add_argument('--output',required=True)
 ap.add_argument('--index-dir',required=True)
 a=ap.parse_args()
 print(js(build(a.base,a.source,a.output,a.index_dir)))
if __name__=='__main__':main()
