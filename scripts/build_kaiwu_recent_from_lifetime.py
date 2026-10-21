"""Source-faithful six Kaiwu recent-fortune events appended to the SHA-pinned 167-event full archive."""
import argparse,hashlib,json,re,sqlite3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE_SHA='17e25c0bf612636e9223d2691339b6859188ee07ab337a6aec1bb6b597c8e1d3'
SOURCE_SHA='f5c2f65f0781eed540aec048c1a734a978bc35c6a9b01aee6b75baec3902e619'
BASE_NAME='WenguaApp_神奇之门21章_开悟之门17节_167案例_完整研究库.sqlite3'
NEW_NAME='WenguaApp_神奇之门21章_开悟之门18节_173案例_完整研究库.sqlite3'
SECTION='recent_life_fortune_ch02_section15';CHAPTER='kaiwu/'+SECTION+'/v1'
TITLE='第十五节 人生近期运气预测(共6例)'
# First answer, feedback, teacher correction, and post-feedback retrospective are NOT interchangeable.
CASES=[
 dict(tag='restaurant_divorce',p=(3,56),chart=(9,22),known=(4,4),steps=[26,29,32,35,38],last=39,
  teacher=[45,47,49,51,53],tlast=53,initial=[(5,5)],feedback=[(6,6)],
  extra=[('teacher_commentary',(42,43)),('teacher_conclusion',(54,55))],
  facets=['marriage','business_profit'],retro=True,
  note='1999 question about previously completed 1996-98 years; retrospective not blind'),
 dict(tag='reported_robbery',p=(57,106),chart=(74,87),known=(69,72),steps=[89,90,92,93,94,96,98],last=98,
  teacher=[104,105],tlast=105,initial=[(90,90),(94,94),(96,96),(98,98)],feedback=[(91,91),(99,100)],
  extra=[('later_route_disclosure',(92,92)),('followup_questions',(95,97))],
  facets=['criminal_case'],retro=True,
  note='Event was already past; do not make two unrelated unprinted introductory anecdotes new complete events'),
 dict(tag='phone_and_road',p=(107,158),chart=(118,130),known=(108,110),steps=[134,138,141,143,146],last=147,
  teacher=[151,153,154,155,156,157],tlast=157,initial=[(111,111),(113,114)],feedback=[(112,112),(115,115)],
  extra=[('second_issue_same_cast',(113,115))],facets=['lost_property','travel_domestic'],retro=True,
  note='One questioner and one chart reused for a missing phone and a prior traffic incident; no new second chart'),
 dict(tag='wrong_cast_correct_result',p=(159,213),chart=(167,183),known=(164,165),steps=[195,197,199,201,203,205,207],last=208,
  teacher=[211,212],tlast=212,initial=[(187,191)],feedback=[(208,208)],
  extra=[('explicit_wrong_source_cast',(212,212))],facets=['employment','lost_property','health'],retro=True,
  note='Teacher explicitly states 庚申日巳时应辛巳, mistaken 丁巳 and 甲寅旬; original chart retained unchanged'),
 dict(tag='self_1996',p=(214,245),chart=(217,229),known=(215,215),steps=[233,235,237,239,241],last=241,
  teacher=[],tlast=None,initial=[(233,241)],feedback=[(244,244)],
  extra=[('underestimated_severe_ulcers',(244,244)),('yearly_review_methods',(242,243))],
  facets=['employment','health','marriage'],retro=False,
  note='Author explicitly did not predict severity and workplace mechanism until after year; scoped initial miss'),
 dict(tag='self_1997',p=(246,284),chart=(249,261),known=(247,247),steps=[265,267,269,271,273,275],last=276,
  teacher=[284],tlast=284,initial=[(265,276)],feedback=[(277,281)],
  extra=[('dated_feedback',(277,281))],facets=['employment','health','housing'],retro=False,
  note='Initial Feb 1997 year-outlook kept separate from later father-death and housing/workplace account')
]
def sha(b):return hashlib.sha256(b).hexdigest()
def js(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'))
def literal(L,a,b=None):
 b=a if b is None else b
 if not 1<=a<=b<=len(L):raise ValueError(('Invalid source interval',a,b))
 return '\n'.join(L[a-1:b])
def validate(raw):
 if len(raw)!=29172 or sha(raw)!=SOURCE_SHA or not raw.endswith(b'\n'):
  raise ValueError('Original whole-upload SHA/length/newline mismatch')
 L=raw.decode('utf8').splitlines()
 if len(L)!=284 or L[0]!=TITLE:raise ValueError('Incorrect title or line count')
 if [i for i,x in enumerate(L,1) if x.startswith('(例')]!=[3,57,107,159,214,246]:
  raise ValueError('Exactly six original heading cases required')
 for line,word in [(212,'错局正断'),(212,'辛巳'),(156,'测不准是绝对的'),
                   (244,'没有预测到这么严重'),(278,'父亲于1997年7月20日')]:
  if word not in L[line-1]:raise ValueError(('Critical source evidence missing',line,word))
 return L
def intervals(heads,last):
 return [(n,min(last,heads[i+1]-1 if i+1<len(heads) else last)) for i,n in enumerate(heads)]
def old_unchanged(old,new):
 for (table,) in old.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"):
  cols=[x[1] for x in old.execute('PRAGMA table_info("'+table+'")')]
  q=','.join('"'+x+'"' for x in cols);prev=list(old.execute('SELECT '+q+' FROM "'+table+'"'))
  next_rows=set(new.execute('SELECT '+q+' FROM "'+table+'"'))
  if any(row not in next_rows for row in prev):raise ValueError('Previous full-archive row mutated in '+table)
def phase(db,L,cid,key,kind,a,b):
 txt=literal(L,a,b)
 db.execute("""INSERT INTO kaiwu_recent_source_phases VALUES (?,?,?,?,?,?,?,?,?)""",
 (CHAPTER,cid,key,kind,a,b,txt,sha(txt.encode()),js({'original_source_stage':kind,'book_source_only':True,'no_post_result_leak':True})))
def add_step(db,L,sid,e,cid,k,a,b,speaker):
 txt=literal(L,a,b)
 meta={'source_book':'kaiwu','speaker':speaker,'source_phase':'teacher_later' if speaker=='zhang' else 'case_author_analysis',
       'retrospective_known_incident':e['retro'],'original_OCR_source_chart_not_reconstructed':True,
       'positive_training_eligible':False,'not_external_verification':True,
       'lexical_only_door_candidates':sorted(set(re.findall('([开休生伤杜景死惊])门',txt))),
       'source_note':e['note']}
 db.execute("""INSERT INTO kaiwu_recent_author_steps
  (chapter_key,case_id,step,speaker,first_line,last_line,original_text,sha256,evidence_json)
  VALUES (?,?,?,?,?,?,?,?,?)""",(CHAPTER,cid,k,speaker,a,b,txt,sha(txt.encode()),js(meta)))
 concept='life:recent:kaiwu:'+e['tag']+':step'+str(k).zfill(2)
 db.execute("""INSERT INTO semantic_assertions(chapter_key,concept_id,kind,relation,
  source_start_line,source_end_line,metadata_json,original_excerpt,review_status)
  VALUES (?,?,'source_recent_fortune_reasoning','original_author_conditional_method',?,?,?,?,'draft')""",
  (CHAPTER,concept,a,b,js(meta),txt))
 db.execute("""INSERT INTO cross_book_concept_tracks(chapter_key,concept_id,
  source_start_line,source_end_line,source_section_id,source_sha256,excerpt_sha256,
  track_id,relation_to_prior,comparison_state,normalized_json,review_status)
  VALUES (?,?,?,?,?,?,?,?,?,'unvalidated_original_book_method',?,'draft')""",
  (CHAPTER,concept,a,b,sid,SOURCE_SHA,sha(txt.encode()),'kaiwu:recent:domain_methods','additional_exposition',js(meta)))
 if speaker=='original':
  n=db.execute('SELECT count(*) FROM historical_case_reasoning WHERE case_id=?',(cid,)).fetchone()[0]+1
  db.execute("""INSERT INTO historical_case_reasoning(case_id,step_number,source_line,
   author_analysis_original,short_method_topic,metadata_json) VALUES (?,?,?,?,?,?)""",
   (cid,n,a,txt,'multi_domain_recent_fortune',js(meta)))
  db.execute("""INSERT INTO historical_case_reasoning_trace(case_id,step_number,source_line,
   evidence_json,review_status,positive_training_eligible)
   VALUES (?,?,?,?,'book_source_draft_not_blind',0)""",(cid,n,a,js(meta)))
def build(parent,chapter,out,index):
 parent,chapter,out,index=map(Path,(parent,chapter,out,index))
 if out.exists():raise ValueError('No archive overwrites')
 if sha(parent.read_bytes())!=BASE_SHA:raise ValueError('Must use verified 167-event entire parent')
 raw=chapter.read_bytes();L=validate(raw)
 out.parent.mkdir(parents=True,exist_ok=True)
 with sqlite3.connect('file:'+str(parent.resolve())+'?mode=ro',uri=True) as old,sqlite3.connect(out) as db:
  old.backup(db)
  db.executescript((ROOT/'schema/migrations/033_kaiwu_recent_fortune_six_cases.sql').read_text('utf8'))
  db.execute('PRAGMA foreign_keys=ON')
  with db:
   if db.execute("SELECT count(*) FROM sections WHERE book_id='kaiwu'").fetchone()[0]!=17:
    raise ValueError('Parent 17 Kaiwu source sections missing')
   db.execute("""INSERT INTO sections(book_id,section_key,title,original_text,sha256,content_version,reviewed)
    VALUES ('kaiwu',?,?,?,?,1,1)""",(SECTION,TITLE,raw.decode('utf8'),SOURCE_SHA))
   sid=db.execute('SELECT last_insert_rowid()').fetchone()[0]
   db.execute("""INSERT INTO chapter_knowledge(chapter_key,book_id,title,source_sha256,
    source_length_bytes,knowledge_version,review_status) VALUES (?,'kaiwu',?,?,?,'1','draft')""",
    (CHAPTER,TITLE,SOURCE_SHA,len(raw)))
   for i,e in enumerate(CASES,1):
    cid='kaiwu.recent_fortune.case'+str(i).zfill(2)
    primary=intervals(e['steps'],e['last']);edit=intervals(e['teacher'],e['tlast']) if e['teacher'] else []
    info={'chapter':CHAPTER,'source_span':e['p'],'original_OCR':e['chart'],
     'source_current_retro':e['retro'],'not_an_independent_blind_test':True,'book_case_user_accepted':True,
     'note':e['note']}
    db.execute("""INSERT INTO cases(case_id,section_id,event_family_id,domain_id,
     known_before,author_yongshen_steps,author_judgment,later_feedback,reviewed)
     VALUES (?,?,?,'life_opportunity_book_study',?,?,?,?,1)""",
     (cid,sid,cid,literal(L,*e['known']),
      '\n\n'.join(literal(L,a,b) for a,b in primary),
      '\n'.join(literal(L,a,b) for a,b in e['initial']),
      '\n'.join(literal(L,a,b) for a,b in e['feedback'])))
    db.execute("""INSERT INTO historical_case_protocol(case_id,completeness,
     published_chart_verification,feedback_independently_verified,eligible_blind_test,
     case_source_sha256,metadata_json)
     VALUES (?,'complete_source_narrative_flattened_OCR',
     'no_positionally_verifiable_original_nine_palace',0,0,?,?)""",
     (cid,SOURCE_SHA,js(info)))
    db.execute("""INSERT INTO historic_book_case_acceptance(case_id,source_book,
     source_chapter_key,source_documented_outcome,metadata_json)
     VALUES (?,'kaiwu',?,'original_book_feedback_not_independently_validated',?)""",
     (cid,CHAPTER,js(info)))
    for n,domain in enumerate(['life_opportunity_book_study']+e['facets']):
     db.execute("""INSERT INTO unified_case_domain_facets(case_id,domain_id,
      source_chapter_key,primary_domain,note) VALUES (?,?,?,?,?)""",
      (cid,domain,CHAPTER,int(n==0),e['note']))
    panel=literal(L,*e['chart'])
    db.execute("""INSERT INTO kaiwu_recent_panels VALUES (?,?,?,?,? ,?,'OCR_flattened_unresolved',?)""",
     (CHAPTER,cid,*e['chart'],panel,sha(panel.encode()),js(info)))
    for line in range(e['chart'][0],e['chart'][1]+1):
     token=literal(L,line)
     db.execute("""INSERT INTO kaiwu_recent_panel_lines VALUES (?,?,?,?,?)""",
      (CHAPTER,cid,line,token,sha(token.encode())))
    phase(db,L,cid,'known','first_known_input_no_later_feedback',*e['known'])
    phase(db,L,cid,'printed_raw','literal_printed_OCR_grid_unresolved',*e['chart'])
    for n,(a,b) in enumerate(e['initial'],1):phase(db,L,cid,'initial_'+str(n),'initial_book_claim',a,b)
    for n,(a,b) in enumerate(e['feedback'],1):phase(db,L,cid,'feedback_'+str(n),'after_forecast_book_report',a,b)
    for n,(key,(a,b)) in enumerate(e['extra'],1):phase(db,L,cid,key,'later_information_or_editorial',a,b)
    for n,(a,b) in enumerate(primary+edit,1):
     sp='original' if n<=len(primary) else 'zhang'
     add_step(db,L,sid,e,cid,n,a,b,sp)
    for n,(a,b) in enumerate(primary,1):phase(db,L,cid,'author_step_'+str(n),'source_author_analysis_not_new_event',a,b)
    for n,(a,b) in enumerate(edit,1):phase(db,L,cid,'editor_step_'+str(n),'post_source_teacher_review_not_initial_answer',a,b)
    db.execute("""INSERT INTO historical_case_review_audit
     (case_id,original_steps,mechanical_step_trace,human_complete_step_chains,review_status,warning)
     VALUES (?,?,?,0,'source_study_draft_no_professional_blind_verification',?)""",
     (cid,len(primary),len(primary),e['note']))
    # Source author explicitly admits a partial initial miss in case05. Bad chart in
    # case04 is a separate method/cast error, not an invented failed outcome.
    ismiss=(i==5)
    db.execute("""INSERT INTO historical_case_book_verdicts(
     event_family_id,primary_case_id,verdict,explicit_source_correction,
     source_correction_lines_json,feedback_source_lines_json,
     independent_external_verification,app_output_protocol,evidence_review_status,note)
     VALUES (?,?,?,?,?,?,'not_verified','single_answer_for_one_cast','book_report_only_draft',?)""",
     (cid,cid,'author_book_error_explicit' if ismiss else 'author_book_success_default',
      int(ismiss),js([241,244]) if ismiss else '[]',
      js([a for a,b in e['feedback']]),e['note']))
   # Two brief Q&A reports without Qimen cast belong to case02 as mentioned source,
   # NOT additional event families or additional full printed panels.
   for key,a,b in [('son_prison',61,63),('daughter_in_law_absent',65,67)]:
    cid='kaiwu.recent_fortune.case02';txt=literal(L,a,b)
    db.execute("""INSERT INTO kaiwu_recent_unprinted_anecdotes
     (chapter_key,case_id,anecdote_key,first_line,last_line,source_text,sha256)
     VALUES (?,?,?,?,?,?,?)""",(CHAPTER,cid,key,a,b,txt,sha(txt.encode())))
   for cid,a,b,kind in [
    ('kaiwu.recent_fortune.case04',165,212,'teacher_confirms_wrong_hour_stem_and_xun_head'),
    ('kaiwu.recent_fortune.case05',241,244,'author_admits_missed_severe_health_outcome')]:
    db.execute("""INSERT INTO kaiwu_recent_source_corrections(
     chapter_key,case_id,correction_kind,initial_line,correction_line,original_initial,original_correction)
     VALUES (?,?,?,?,?,?,?)""",(CHAPTER,cid,kind,a,b,literal(L,a),literal(L,b)))
   db.execute("""INSERT INTO chapter_archival_versions(archive_label,baseline_sha256,
    new_db_sha256,contains_complete_private_copyright_source,snapshot_type,created_utc,
    repo_public_archive_policy) VALUES (?, ?,NULL,1,
    'kaiwu_recent_fortune_six_original_events_two_source_error_types',
    '2026-10-20','user_authorized_public_full_sqlite_versions')""",
    ('shenqi21_kaiwu18_recent_173cases',BASE_SHA))
  old_unchanged(old,db)
  expected={'sections':39,'cases':173,'historical_chart_cells':1440,
    'historical_case_additional_casts':19,'historical_case_additional_cast_cells':171,
    'historical_palace_standardization':1611,'historical_case_reasoning':924,
    'historical_case_reasoning_trace':924,'semantic_assertions':2637,
    'cross_book_concept_tracks':1380,'historic_book_case_acceptance':65,
    'unified_case_domain_facets':103,'kaiwu_recent_panels':6,'kaiwu_recent_panel_lines':84,
    'kaiwu_recent_author_steps':51,'kaiwu_recent_unprinted_anecdotes':2,
    'kaiwu_recent_source_corrections':2}
  got={k:db.execute('SELECT count(*) FROM "'+k+'"').fetchone()[0] for k in expected}
  if got!=expected:raise ValueError(('Expected exact full archive counts',got,expected))
  if db.execute("SELECT count(*) FROM historical_case_book_verdicts WHERE verdict='author_book_error_explicit'").fetchone()[0]!=11:
   raise ValueError('Old ten plus author newly admitted partial severity miss required')
  if db.execute('PRAGMA integrity_check').fetchone()[0]!='ok' or db.execute('PRAGMA foreign_key_check').fetchall():
   raise ValueError('SQLite source archive integrity failed')
  db.execute('VACUUM');db.commit()
 index.mkdir(parents=True,exist_ok=True)
 doc={'schema':'kaiwu_recent_six_historical_source_events_v1','source_title':TITLE,
  'source_sha256':SOURCE_SHA,'source_lines':len(L),'source_bytes':len(raw),
  'new_independent_source_events':6,'new_source_panels_as_OCR_raw':6,
  'new_verified_full_original_nine_palace_charts':0,'original_OCR_chart_lines':84,
  'all_179_previous_complete_source_charts_unchanged':True,
  'original_and_teacher_authored_analysis_units':51,'original_case_analyst_steps':35,
  'no_second_independent_event_for_phone_and_old_car_breakdown':True,
  'unprinted_intro_anecdotes_2_not_counted_as_full_cases':True,
  'teacher_explicit_wrong_chart_in_fourth':True,
  'self_report_1996_missed_severe_ulcers_in_fifth':True,
  'all_old_10_explicit_initial_error_cases_preserved':True,
  'total_explicit_initial_error_cases':11,
  'parent_sha256':BASE_SHA,'new_archive_sha256':sha(out.read_bytes()),
  'all_old_tables_rows_unchanged':True,'counts':got,'positive_training_approved':0}
 write=lambda name,x:(index/name).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 write('chapter_manifest.json',doc)
 write('case_index.json',{'source_sha256':SOURCE_SHA,'cases':[
  {'case_id':'kaiwu.recent_fortune.case'+str(i).zfill(2),'original_source_span':e['p'],
  'original_OCR_chart_lines':e['chart'],'author_analysis_step_lines':e['steps'],
  'teacher_later_step_lines':e['teacher'],'first_book_claim_source':e['initial'],
  'book_feedback_spans':e['feedback'],'previously_known_events':e['retro'],
  'domain_facets':['life_opportunity_book_study']+e['facets'],
  'original_source_note':e['note']} for i,e in enumerate(CASES,1)]})
 write('source_audit.json',{'source_sha256':SOURCE_SHA,
  'source_ocr_lines_hashed':[{'case_id':'kaiwu.recent_fortune.case'+str(i).zfill(2),
    'first':e['chart'][0],'last':e['chart'][1],
    'line_digests':[sha(literal(L,n).encode()) for n in range(e['chart'][0],e['chart'][1]+1)]}
     for i,e in enumerate(CASES,1)],
  'no_invented_original_nine_palace_cells':True,'wrong_chart_author_original_line':212,
  'cannot_correct_printed_board_in_place':True,
  'book_first_prediction_and_later_feedback_separately_hashed':True})
 return doc
def main():
 ap=argparse.ArgumentParser()
 for arg in ['base','source','output','index-dir']:ap.add_argument('--'+arg,required=True)
 a=ap.parse_args();print(js(build(a.base,a.source,a.output,a.index_dir)))
if __name__=='__main__':main()
