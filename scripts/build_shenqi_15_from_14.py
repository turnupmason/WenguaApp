"""Losslessly derive the user's next *versioned* original-source SQLite archive.

Run: python scripts/build_shenqi_15_from_14.py --base <14.sqlite3> --source <litigation.txt> --output <15.sqlite3> --index-dir <metadata_dir>
Never use an earlier chapter result as the current chapter source. A successful
build asserts the entire old source/case/chart/analysis data is unchanged.

Historical divination interpretations are source claims, NOT usable legal advice
or evidence about anyone's guilt, custody or likely court outcome.
"""
from __future__ import annotations
import argparse, collections, hashlib, json, re, sqlite3
from pathlib import Path

EXPECTED_SHA='a0cf2a05700bfb832420d3318b2982d25f6150e7a5c5e8c5ecc1ae07f5c810d2'
BASE_SHA='bcffc72c0801dfd46ea0fffad3b67550a4aa533764a0bf2d46373031912a8dd2'
CHAPTER='shenqi/litigation_prediction_ch11/v1'
SECTION='litigation_prediction_ch11'
PALACE=('巽四宫','离九宫','坤二宫','震三宫','中五宫','兑七宫','艮八宫','坎一宫','乾六宫')
NUM=(4,9,2,3,5,7,8,1,6)

# [case first line, final line, printed chart start, author-analysis paragraph lines,
#  initial known story lines, first judgment lines, validation lines, topical focus]
CASE_SPECS=[
 (19,59,30,[46,48,50,52,54],[21,25,27],[46,48,50,52,54],[56,58],'代女问父亲受检察院传讯与释放'),
 (60,92,67,[83,85,87,89],[62,64],[83,85,87,89],[91],'代问同事因经济问题拘留及是否判刑'),
 (93,133,104,[120,122,124,126,128],[95,97,99,101],[120,122,124,126,128],[132],'房产纠纷的起诉、证据、调解、法官倾向及搬迁'),
 (134,178,145,[161,163,165,167,169],[136,138,140,142],[161,163,165,167,169],[173,175,177],'亲属问一男一女被控抱走儿童、判刑或缓刑'),
 (179,223,188,[204,206,208,214],[181,183,185],[210,216],[218],'学生李文达用乙奇误取被告、老师后纠正'),
 (224,267,245,[263,267],[226,228],[228,232],[236,238],'劳动仲裁原告被告用神与主客被动策略')
]
# Topic labels align one-to-one with every author's original paragraph; no invisible inferences.
STEP_LABELS=[
 ['问女儿的父亲取年干乙,入墓及乙庚格以判拘押','天盘庚和父亲乙宫生克,推举报来源','景门举报信震宫空亡,作者断举报不实','开门检察院坤宫生父亲乙宫,作者断放回','地盘乙上临丙己及阳遁内盘定己日'],
 ['同事取月干戊,钱财与戊己戊壬官司格','甲午辛为罪人辅助,与法官开门及吉门判可保释','月干戊与天蓬旺相及宫数推需退钱金额','甲午辛地盘戊与子午冲推戊子月放出'],
 ['值符作为原告、天乙为被告;取被告须值符落宫地盘之星','值符与天乙、开门三宫生克判断原告愿调解、法官偏原告','景门诉状与六合证据逢空亡,判断证据不足','甲子戊房租数,生门房屋,调解款及可能搬迁','开门不逢庚与律师惊门宫关系推不会立判'],
 ['值符原告、天乙被告;和值符空亡生被告看可调解','天乙被告临乙庚下辛,乙辛格相反组合判可能释放','开门法官入墓;证据不足且开门宫生被告判偏有利','惊门律师与原告法官被告的宫生克','开门临白虎但不逢庚,推不会当庭立判'],
 ['日干丁同甲子戊、白虎与开死门推纠纷','时干辛伏吟自刑、杜加辛推词讼打斗','甲子戊与日干同宫判断经济争议','学生错误取乙奇为被告;后来作者第220-222行明确纠正'],
 ['值符原告与开门仲裁机关同震宫,天乙天冲星被告坤宫;克制推胜','日干时干天盘地盘主客相克,以利主推被动策略']
]
assert sum(map(len,STEP_LABELS))==25
# 31 conditional source candidates (do not promote to universal verified rules).
CONDITIONS=[
 (5,'plaintiff_zhifu','值符为原告'),(5,'defendant_tianyi_ground_star','天乙是值符落宫的地盘之星，不等于乙奇'),
 (5,'judge_open_gate','开门为法官'),(5,'witness_liuhe','六合为证人证据'),(5,'petition_jing_gate','景门为诉状'),
 (5,'summons_ding','丁奇为传票'),(5,'lawyer_jingmen','惊门为律师'),(5,'unconditional_yiqi_rejected','不能通用乙奇代替天乙'),
 (7,'plaintiff_suppresses_defendant','原告有气兼克被告则原告可能胜'),
 (7,'defendant_suppresses_plaintiff','被告有气兼克原告则被告可能胜'),
 (7,'palaces_equal','二宫比和可能和解'),(7,'plaintiff_generates_defendant','值符宫生天乙宫可能原告主动和解'),
 (7,'defendant_generates_plaintiff','天乙宫生值符宫可能被告主动和解'),
 (9,'judge_suppresses_both','开门克二者候选公平审判'),(9,'judge_generates_plaintiff','开门生值符偏向原告'),
 (9,'judge_generates_defendant','开门生天乙偏向被告'),(9,'judge_tomb','开门入墓司法判断困难'),
 (9,'judge_void','开门空亡可能不予审理'),(9,'judge_reverse','开门反吟有换审判者之说'),
 (11,'petition_accepted','景门旺相吉格且不受开门冲克可受理'),
 (11,'petition_rejected','景门受开门宫冲克可不受理'),
 (11,'petition_void_xuanwu_tengshe','景门空亡乘玄武螣蛇原书指不实'),
 (11,'evidence_liuhe_void','六合空亡原书指证据不足'),
 (13,'crime_jiawu_xin_ren_gui','甲午辛临壬癸原书指有牢狱风险'),
 (13,'crime_xin_ding_escape','罪人用神临三奇丁奇可能释放'),
 (13,'crime_and_judge_relation','判刑须结合开门法官宫生克'),
 (15,'relative_role_selection','本人及家属求测可用日干六亲关系取用'),
 (15,'prison_stem_xin_below','用神下临辛为天狱'),
 (15,'net_ren_gui','用神临壬癸天罗地网候选'),
 (15,'net_ren_gui_above_xin','天盘壬癸下临地盘辛可能长囚'),
 (15,'subject_void_prison','用神宫空亡原书称不会囚禁')
]
assert len(CONDITIONS)==31

def canon(o):return json.dumps(o,ensure_ascii=False,sort_keys=True,separators=(',',':'))
def seg(lines,a,b=None):
 b=a if b is None else b
 if not (1<=a<=b<=len(lines)):raise ValueError((a,b,'source span invalid'))
 return '\n'.join(lines[a-1:b])
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def source_chart(lines,start):
 if not lines[start-1].startswith('┌'):raise ValueError('Chart boundary missing at %d'%start)
 out=[]
 for row in range(3):
  y=start+1+4*row
  triple=[]
  for k in range(3):
   parts=[v.strip() for v in lines[y+k-1].split('│')[1:-1]]
   if len(parts)!=3:raise ValueError((start,y,k,'not three columns'))
   triple.append(parts)
  for k in range(3):
   idx=row*3+k;n=NUM[idx]
   name,door,star=(x[k] for x in triple)
   if not name.startswith(PALACE[idx]):raise ValueError((name,PALACE[idx]))
   if n==5:
    if not door.startswith('中宫原字：') or star or '八神：' in name:
     raise ValueError((start,'unfaithful centre palace',name,door,star))
    deity=''; door=door.split('：',1)[1]
   else:
    if '八神：' not in name or not door.startswith('门位：') or not star.startswith('星位：'):
     raise ValueError((start,name,door,star,'missing external palace source'))
    deity=name.split('八神：',1)[1].strip()
    door=door.split('：',1)[1].strip();star=star.split('：',1)[1].strip()
   out.append((n,y+k,name,deity,door,star))
 if sorted(c[0] for c in out)!=list(range(1,10)):raise ValueError('Duplicate source palace')
 return out

def lex(t):
 items=[]
 for n in '开休生伤杜景死惊':
  if n+'门' in t:items.append('door:'+n)
 for n in '蓬任冲辅英芮柱心禽':
  if '天'+n in t:items.append('star:'+n)
 for n in ('玄武','白虎','九天','九地','六合','太阴','螣蛇','值符'):
  if n in t:items.append('deity:'+n)
 for n in '乾坤震巽坎离艮兑':
  if n+'宫' in t:items.append('trigram:'+n)
 return sorted(set(items))

def evidence_draft(lines,line,topic,stage,case_number,step_number):
    """Source-literal clause suggestions, never certified cause/effect or chart recast."""
    literal=lines[line-1]
    segments=[x.strip() for x in re.split(r'[，；。]',literal) if x.strip()]
    relevant=[x for x in segments if any(k in x for k in ('宫','门','星','奇','格','空','墓','冲','克','生','刑','伏吟','反吟'))]
    contrasted=[x for x in segments if any(k in x for k in ('但','虽然','相反','幸','然而','反受','未必','却','如果'))]
    timed=[x for x in segments if any(k in x for k in ('何时','应期','放回','放出','戊子月','己日','甲日','当庭','短期'))]
    return {'case_number':case_number,'step_number':step_number,'source_line':line,
      'literal_original_in_private_historical_case_reasoning':True,
      'author_workflow_topic':topic,'source_literal_supporting_clauses':relevant,
      'literal_counterevidence_clauses_or_unknown':contrasted if contrasted else [],
      'literal_timing_clauses_or_unknown':timed if timed else [],
      'prior_chapter_concept_mentions_unverified':lex(literal),
      'author_step_stage':stage,'source_derived_not_recast':True,
      'author_logic_human_complete_review':'not_completed',
      'original_chart_star_door_god_independently_verified':False,
      'positive_training_eligible':False}

def build_metadata(lines):
 cases=[]; steps=[]
 for i,(start,end,chart,step_lines,initial,original_judgment,feedback,topic) in enumerate(CASE_SPECS,1):
  assert lines[start-1].startswith('实例'),(i,start)
  source_chart(lines,chart)
  step_entries=[]
  for j,loc in enumerate(step_lines,1):
   if not re.match(r'^\(\d+\)',lines[loc-1]) and not(i==6 and loc in (263,267)):
    raise ValueError((i,loc,'missing author step'))
   phase='after_subquestion_disclosure' if i==5 and loc==214 else 'retrospective_explanation_after_book_feedback' if i==6 else 'author_source_step'
   if i==5 and loc==214:phase='author_method_explicitly_corrected_later'
   step_entries.append({'step_number':j,'source_line':loc,'topic':STEP_LABELS[i-1][j-1],
     'author_literal_located_in_private_sqlite':True,'lexical_cross_chapter_ids_only':lex(lines[loc-1]),
     'phase':phase,'evidence_chain_manual_review':'required_not_completed',
     'specific_palace_mentions':re.findall(r'(?:[一二三四五六七八九]|[1-9])宫',lines[loc-1]),
     'positive_training_eligible':False})
  c={'case_number':i,'case_id':f'shenqi.litigation.case{i:02d}','event_family_id':f'shenqi.litigation.case{i:02d}',
    'source_span':[start,end],'original_chart_start':chart,'nine_real_source_palaces':9,
    'topic':topic,'initial_context_lines':initial,'numbered_step_lines':step_lines,
    'analysis':step_entries,'initial_or_source_judgment_lines':original_judgment,
    'book_feedback_lines':feedback,'source_sha256':EXPECTED_SHA,
    'source_printed_chart_independently_verified':False,
    'book_outcome_label':'author_book_success_default',
    'independent_external_verification':'not_verified','whole_event_unsplit':True}
  if i==5:c['explicit_wrong_yongshen']={'student_line':214,'editor_correction_lines':[220,222],
    'student_uses':'乙奇为被告','author_prefers':'天乙＝值符落宫地盘之星',
    'outcome_note':'Book claims successful collection; initial student METHOD explicitly wrong, but book does not say court outcome initially wrong.'}
  if i==6:c['source_chronology_exception']={'first_judgment_embedded_in':228,'new_disclosure_lines':[230,232],
   'book_outcome_precedes_printed_chart':[236,238],'printed_chart_start':245,
   'analysis_paragraphs_written_after_result':[263,267],'blind_test_must_not_see_book_outcome':True}
  if i==3:c['source_chronology_exception']={'older_prior_forecasts_mentioned_at':95,'unprinted_earlier_casts_not_invented':True}
  cases.append(c);steps.extend(step_entries)
 return {'schema':'wengua_shenqi_litigation_cases_v1','chapter_key':CHAPTER,
         'source_sha256':EXPECTED_SHA,'whole_event_families':6,'supplied_actual_casts':6,
         'complete_nine_palace_cells':54,'actual_author_analyses':25,'cases':cases},steps

# Fine-grained phase ranges, not simply all book lines before chart treated as first known.
PHASES={
 1:[(21,21,'initial_question',1),(23,27,'cast_metadata',0),(56,58,'book_feedback',0)],
 2:[(62,64,'initial_question',1),(91,91,'book_feedback',0)],
 3:[(95,97,'initial_question',1),(99,101,'cast_metadata',0),(130,130,'continued_judgment',0),(132,132,'book_feedback',0)],
 4:[(136,142,'initial_question',1),(171,171,'initial_judgment',0),(173,177,'book_feedback',0)],
 5:[(181,185,'initial_question',1),(210,210,'initial_judgment',0),(212,212,'new_disclosure',0),
     (216,216,'continued_judgment',0),(218,218,'book_feedback',0),
     (220,222,'editor_posthoc_correction',0)],
 6:[(226,226,'initial_question',1),(228,228,'initial_judgment',0),
     (230,232,'new_disclosure',0),(232,232,'continued_judgment',0),
     (234,234,'new_disclosure',0),(236,238,'book_feedback',0),
     (240,242,'cast_metadata',0),(263,267,'retrospective_author_explanation',0)]
}

def import_to(db,lines,raw):
    db.execute('PRAGMA foreign_keys=ON')
    existing=db.execute('SELECT section_id FROM sections WHERE section_key=?',(SECTION,)).fetchone()
    if existing:raise ValueError('Chapter has been imported already; refusing duplicate')
    db.execute("INSERT INTO sections(book_id,section_key,title,original_text,sha256,content_version,reviewed) VALUES('shenqi',?,?,?,?,1,0)",(SECTION,'官司诉讼预测',raw.decode('utf8'),EXPECTED_SHA))
    sid=db.execute('SELECT last_insert_rowid()').fetchone()[0]
    db.execute("INSERT INTO chapter_knowledge(chapter_key,book_id,title,source_sha256,source_length_bytes,knowledge_version,review_status) VALUES (?,'shenqi',?,?,?,'1','draft')",(CHAPTER,'官司诉讼预测',EXPECTED_SHA,len(raw)))
    data,steps=build_metadata(lines)
    for ln,id,desc in CONDITIONS:
      meta={'domain':'litigation','source_line':ln,'condition_id':id,'summary':desc,'source_status':'draft',
         'not_scientific_law_or_crime_evidence':True}
      db.execute('''INSERT INTO semantic_assertions(chapter_key,concept_id,kind,relation,source_start_line,source_end_line,metadata_json,original_excerpt,review_status) VALUES (?,?,?,?,?,?,?,?,?)''',
         (CHAPTER,'litigation:general:'+id,'litigation_condition','conditional_source',ln,ln,canon(meta),seg(lines,ln),'draft'))
    for x in data['cases']:
      i=x['case_number'];cid=x['case_id'];info=CASE_SPECS[i-1]
      _,_,chart,steplines,initial,judgment,feedback,_=info
      if i==6:
       rawline=lines[227];
       # Must cut immediately before the author's first answer.
       marker='便拿出笔记本，起好局，对李说：'
       if marker not in rawline:raise ValueError('Case6 prospective context separator missing')
       known=seg(lines,226)+'\n'+rawline.split(marker,1)[0].strip()
      elif i==5:
       known='\n'.join(seg(lines,n) for n in initial)
      else:known='\n'.join(seg(lines,n) for n in initial)
      if '结果' in known or '张志春按' in known:raise ValueError('Hindsight leakage in initial question')
      original_steps='\n\n'.join(seg(lines,n) for n in steplines)
      prediction='\n'.join(seg(lines,n) for n in judgment)
      feedback_literal='\n'.join(seg(lines,n) for n in feedback)
      db.execute('''INSERT INTO cases(case_id,section_id,event_family_id,domain_id,known_before,author_yongshen_steps,author_judgment,later_feedback,reviewed) VALUES (?,?,?,?,?,?,?,?,0)''',
        (cid,sid,cid,'litigation',known,original_steps,prediction,feedback_literal))
      db.execute('''INSERT INTO historical_case_protocol(case_id,completeness,published_chart_verification,feedback_independently_verified,eligible_blind_test,case_source_sha256,metadata_json) VALUES (?,'whole_original_case','original_txt_only_not_independently_recast',0,0,?,?)''',(cid,EXPECTED_SHA,canon(x)))
      for palace,anchor,label,deity,door,star in source_chart(lines,chart):
       db.execute('''INSERT INTO historical_chart_cells(case_id,palace,source_line,palace_label_raw,deity_raw,door_position_raw,star_position_raw,source_status) VALUES (?,?,?,?,?,?,?,'literal_original_txt_not_recast')''',(cid,palace,anchor,label,deity,door,star))
       norm= re.findall(r'[乙丙丁戊己庚辛壬癸]',door) if palace==5 else []
       center=norm[0] if len(norm)==1 else None
       if palace==5 and center is None:raise ValueError('Unrecoverable centre stem')
       db.execute('''INSERT INTO historical_palace_standardization
        (case_id,cast_key,palace,center_stem,source_of_center_stem,standard_deity,standard_door,standard_star,
        normalized_status,original_raw_integrity_checked,method_reference,derived_host_palace,derived_host_source)
        VALUES (?,?,?,?,?,?,?,?,?,1,?,?,?)''',
        (cid,'primary',palace,center,'original_center_literal' if palace==5 else 'not_center',
          None if palace==5 else deity,None if palace==5 else door,None if palace==5 else star,
          'center_not_applicable_sanshu_three_fields' if palace==5 else 'peripheral_literal_verified',
          'original_litigation_txt+shijia_qiju',2 if palace==5 else None,'shijia_qiju:五宫寄坤二宫' if palace==5 else None))
      for step in x['analysis']:
       n=step['source_line'];k=step['step_number'];layer=step['phase']
       db.execute('''INSERT INTO historical_case_reasoning(case_id,step_number,source_line,author_analysis_original,short_method_topic,metadata_json)
         VALUES (?,?,?,?,?,?)''',(cid,k,n,seg(lines,n),step['topic'],canon(step)))
       draft=evidence_draft(lines,n,step['topic'],layer,i,k)
       db.execute('''INSERT INTO historical_case_reasoning_trace(case_id,step_number,source_line,evidence_json,review_status,positive_training_eligible)
         VALUES (?,?,?,?,'source_anchor_only_needs_full_manual_evidence_chain',0)''',
         (cid,k,n,canon(draft)))
       db.execute('''INSERT INTO semantic_assertions(chapter_key,concept_id,kind,relation,source_start_line,source_end_line,metadata_json,original_excerpt,review_status)
         VALUES (?,?,?,?,?,?,?,?,?)''',
         (CHAPTER,f'litigation:case{i:02d}:step{k:02d}','litigation_worked_example',
          'source_example_not_approved',n,n,canon(step),seg(lines,n),'draft'))
      phase_seen=set()
      for a,b,phase,initial_visible in PHASES[i]:
       if (a,phase) in phase_seen:raise ValueError('Duplicate source phase')
       phase_seen.add((a,phase))
       original=seg(lines,a,b)
       db.execute('''INSERT INTO historical_case_phase_events(case_id,source_start_line,source_end_line,phase,original_excerpt,metadata_json,visible_to_initial_blind_test)
          VALUES (?,?,?,?,?,?,?)''',(cid,a,b,phase,original,canon({'event_family_id':cid,'book_source_sha256':EXPECTED_SHA,'stage_not_equivalent_to_training_validity':True}),initial_visible))
       if phase in ('book_feedback','new_disclosure','editor_posthoc_correction'):
        db.execute('''INSERT OR IGNORE INTO historical_case_disclosures(case_id,source_line,phase,fact_type,original_statement)
          VALUES (?,?,?,?,?)''',(cid,a,'later_than_initial',phase,original))
       if phase in ('editor_posthoc_correction','retrospective_author_explanation'):
        db.execute('''INSERT INTO historical_case_source_segments(case_id,segment_kind,source_start_line,source_end_line,original_text,metadata_json)
          VALUES (?,?,?,?,?,?)''',(cid,'litigation_'+phase,a,b,original,canon({'before_first_judgment':False,'do_not_use_for_blind_study':True})))
      if i==5:
       # The STUDENT method is demonstrably wrong per the author. Result is still
       # the source's successful collection; don't conflate correctness of two levels.
       for n in (220,222):
        db.execute('''INSERT INTO historical_case_reasoning_corrections(case_id,source_line,original_step_number,correction_kind,corrected_yongshen_policy,original_analysis_is_positive_training,source_review_status,rationale_original)
           VALUES (?,?,4,'explicit_author_rejects_student_乙奇_as_defendant','天乙＝值符落宫地盘之星',0,'source_documented_needs_professional_review',?)''',(cid,n,seg(lines,n)))
      for ln in feedback:
       if not db.execute('SELECT 1 FROM historical_case_disclosures WHERE case_id=? AND source_line=?',(cid,ln)).fetchone():
        db.execute('''INSERT INTO historical_case_disclosures(case_id,source_line,phase,fact_type,original_statement) VALUES (?,?,'later_book_feedback','validation_information',?)''',(cid,ln,seg(lines,ln)))
      db.execute('''INSERT INTO historical_case_book_verdicts
       (event_family_id,primary_case_id,verdict,explicit_source_correction,source_correction_lines_json,
       feedback_source_lines_json,independent_external_verification,app_output_protocol,evidence_review_status,note)
       VALUES (?,?,'author_book_success_default',? ,?,?,'not_verified','single_answer_for_one_cast','book_source_only',?)''',
       (cid,cid,int(i==5),canon([220,222] if i==5 else []),canon(feedback),
        'Student defendant selection explicitly criticized, but outcome reported favorable' if i==5 else
        'Source feedback not independently verified; outcome is not legal evidence'))
      db.execute('''INSERT INTO historical_case_review_audit(case_id,original_steps,mechanical_step_trace,human_complete_step_chains,review_status,warning)
        VALUES (?,?,?,0,'source_anchor_only_needs_full_manual_evidence_chain',?)''',
        (cid,len(steplines),len(steplines),
         'Case6 explanation printed after outcome' if i==6 else
         'Case5 student wrong-yongshen kept as negative example' if i==5 else
         'No verified real-world legal predictive validity; draft only'))
    return data

def assert_legacy_unchanged(baseline,updated):
    legacy=['sections','cases','historical_chart_cells','historical_case_additional_casts',
    'historical_case_additional_cast_cells','historical_case_reasoning','semantic_assertions',
    'historical_case_book_verdicts','historical_case_disclosures','historical_palace_standardization',
    'historical_case_reasoning_trace','historical_case_review_audit']
    changes=[]
    for t in legacy:
       names=[r[1] for r in baseline.execute('PRAGMA table_info('+t+')')]
       cols=','.join('"'+v+'"' for v in names)
       old=list(baseline.execute('SELECT '+cols+' FROM '+t))
       # Every old row is intact (including all original multiline source text).
       newset=set(updated.execute('SELECT '+cols+' FROM '+t))
       if not all(x in newset for x in old):changes.append(t)
    if changes:raise ValueError('Legacy data changed: '+', '.join(changes))

def main(argv=None):
 p=argparse.ArgumentParser()
 p.add_argument('--base',type=Path,required=True)
 p.add_argument('--source',type=Path,required=True)
 p.add_argument('--output',type=Path,required=True)
 p.add_argument('--index-dir',type=Path,required=True)
 p.add_argument('--migration',type=Path,default=Path(__file__).resolve().parent.parent/'schema/migrations/010_litigation_event_phase.sql')
 a=p.parse_args(argv)
 if not a.base.exists() or not a.source.exists():raise ValueError('Missing required source or baseline')
 if sha(a.base)!=BASE_SHA:raise ValueError('Baseline full archive SHA256 mismatch; refusing to rebuild older cases')
 raw=a.source.read_bytes()
 if hashlib.sha256(raw).hexdigest()!=EXPECTED_SHA:raise ValueError('Original litigation chapter SHA mismatch')
 lines=raw.decode('utf8').splitlines()
 if len(lines)!=267 or lines[0]!='官司诉讼预测' or lines[16]!='第二节 实例解析（6例）':
  raise ValueError('Source boundaries unexpected')
 if a.output.exists():raise ValueError('Archive version already exists; refusing overwrite')
 a.output.parent.mkdir(parents=True,exist_ok=True)
 metadata,_=build_metadata(lines)
 with sqlite3.connect('file:'+str(a.base)+'?mode=ro',uri=True) as base, sqlite3.connect(a.output) as db:
  base.backup(db)
  db.executescript(a.migration.read_text(encoding='utf8'))
  db.execute('PRAGMA foreign_keys=ON')
  with db:
   import_to(db,lines,raw)
  if db.execute('PRAGMA integrity_check').fetchone()[0]!='ok':raise ValueError('SQLite integrity failure')
  if db.execute('PRAGMA foreign_key_check').fetchall():raise ValueError('FK failure')
  assert_legacy_unchanged(base,db)
  names=['sections','cases','historical_chart_cells','historical_case_additional_cast_cells',
         'historical_case_reasoning','semantic_assertions','historical_case_reasoning_trace',
         'historical_palace_standardization','historical_case_phase_events',
         'historical_case_reasoning_corrections']
  cnt={n:db.execute('SELECT count(*) FROM '+n).fetchone()[0] for n in names}
  expected=dict(sections=15,cases=77,historical_chart_cells=693,historical_case_additional_cast_cells=45,
                historical_case_reasoning=344,semantic_assertions=947,historical_case_reasoning_trace=344,
                historical_palace_standardization=738)
  for k,v in expected.items():
   if cnt[k]!=v:raise ValueError('Expected %s=%d; got %s'%(k,v,cnt[k]))
  if cnt['historical_case_phase_events']<20 or cnt['historical_case_reasoning_corrections']!=2:
   raise ValueError('Author correction and chronology phases incomplete')
  # Exactly one faithful centre in each of the 82 printed chart variants.
  centres=db.execute('SELECT count(*) FROM historical_palace_standardization WHERE palace=5 AND derived_host_palace=2 AND standard_door IS NULL AND standard_star IS NULL AND standard_deity IS NULL').fetchone()[0]
  if centres!=82:raise ValueError('All historic centre hosts must remain complete')
  all_old_content=base.execute('SELECT section_key,sha256 FROM sections ORDER BY section_id').fetchall()
  after_old_content=db.execute('SELECT section_key,sha256 FROM sections WHERE section_key!=? ORDER BY section_id',(SECTION,)).fetchall()
  if all_old_content!=after_old_content:raise ValueError('Old book section hashes changed')
  db.execute('''INSERT INTO chapter_archival_versions(archive_label,baseline_sha256,new_db_sha256,contains_complete_private_copyright_source,snapshot_type,created_utc,repo_public_archive_policy) VALUES (?,?,NULL,1,'incremental_source_preserving','2026-10-19T23:30:00-04:00','user_explicitly_authorized_public_full_archive')''',('shenqi_15_sections_77_whole_events',BASE_SHA))
  db.commit()
  # Compact safely WITHOUT losing schema, data or indexes. This stays a normal
  # uncompressed SQLite database, but smaller pages allow binary Git blob transfer.
  db.execute('PRAGMA page_size=2048')
  db.execute('VACUUM')
  db.commit()
  # Row-count and SQLite checks after page-size-only serialization change.
  if db.execute('PRAGMA integrity_check').fetchone()[0]!='ok' or db.execute('PRAGMA foreign_key_check').fetchall():raise ValueError('Final DB integrity error')
 a.index_dir.mkdir(parents=True,exist_ok=True)
 digest=sha(a.output)
 overview={'schema':'wengua_litigation_chapter_manifest_v1','book':'神奇之门','source_chapter':'官司诉讼预测',
 'chapter_key':CHAPTER,'chapter_source_sha256':EXPECTED_SHA,'source_utf8_bytes':len(raw),'source_lines':len(lines),
 'source_actual_original_charts':6,'original_palace_cells':54,'whole_case_families':6,
 'original_reasoning_paragraphs':25,'source_legal_domain_conditions':31,'case_specific_source_example_candidates':25,
 'draft_source_knowledge_total':56,'author_method_corrected_case':5,'post_outcome_explanation_case':6,
 'original_source_print_independently_verified':False,'approved_reasoning_chains':0,
 'original_book_outcomes_independently_verified':0,'archive_data_count':cnt,'full_15_section_archive_sha256':digest,
 'archival_baseline_sha256':BASE_SHA}
 sources={'schema':'wengua_litigation_conditional_method_v1','chapter_key':CHAPTER,'source_sha256':EXPECTED_SHA,
  'domain_workflow':['识别民事诉讼、拘留量刑、劳动仲裁与问事人亲属关系，明确已知阶段',
   '主辅用神：值符原告、天乙被告（值符落宫地盘之星）、开门法官、六合证据、景门诉状、惊门律师、丁奇传票',
   '按当事人关系另选年干/月干/日干；不能误将乙奇固定为被告',
   '观察原九宫与中宫寄坤二宫的来源分层，比较原被告及开门宫生克旺衰',
   '检验景门起诉书、六合证据与空亡、墓、反吟，不能单项断胜负',
   '结合犯罪疑问的甲午辛、壬癸网牢及丁奇等，区分个人官司与刑事问事',
   '处理作者支持证据与相反证据，推应期仅据原文可用条件',
   '严格隔离事后反馈、学生误断、老师纠正及案例6结果后成文分析，一次完整有条件输出'],
  'methods':[{'concept_id':'litigation:general:'+key,'source_line':line,'conditional_summary':meaning,
  'source_review_status':'draft','cross_chapter_rule_link':'candidate_needs_verified_source_alignment'} for line,key,meaning in CONDITIONS]}
 step_evidence={'schema':'wengua_litigation_step_evidence_source_draft_v1','source_sha256':EXPECTED_SHA,'chapter_key':CHAPTER,'author_source_steps':25,'human_professional_complete_chains':0,'cases':[{'case_id':item['case_id'],'steps':[evidence_draft(lines,s['source_line'],s['topic'],s['phase'],item['case_number'],s['step_number']) for s in item['analysis']]} for item in metadata['cases']]}
 auditing={'schema':'wengua_litigation_source_audit_v1','source_sha256':EXPECTED_SHA,
 'event_families':6,'actual_charts':[x[2] for x in CASE_SPECS],
 'case5_wrong_student_yongshen':{'author_analysis_source_line':214,'teacher_review_lines':[220,222],
 'student_original_wrong_choice':'乙奇为被告','author_correction':'天乙为被告，取值符落宫地盘之星',
 'book_result_vs_method_correctness':'book_result_default_success_but_wrong_method_negative_example'},
 'case6_order':{'initial_excerpt_line':228,'later_disclosure':[230,232],
 'book_feedback_before_printed_chart':[236,238], 'printed_chart_start':245,
 'post_result_explanation':[263,267], 'blind_initial_context_only':True},
 'case3_previous_forecasts_without_printed_charts':'do_not_invent_missing_charts',
 'center_promotion':'all_82_centres_carry_original_stem_and_derived_kun_host_but_no_invented_god_door_star',
 'real_world_legal_evidence':False}
 for name,value in [('chapter_manifest.json',overview),('case_index.json',metadata),('method_index.json',sources),('source_audit.json',auditing),('author_reasoning_evidence_index.json',step_evidence)]:
  (a.index_dir/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 print(json.dumps({'archive':str(a.output),'archive_sha256':digest,'counts':cnt,'centres':centres,
 'source_bytes':len(raw),'source_lines':len(lines),'source_sha256':EXPECTED_SHA,
 'previous_rows_untouched':True,'source_cases':6,'author_steps':25,'method_candidates':56},ensure_ascii=False,indent=2))
 return 0
if __name__=='__main__':raise SystemExit(main())
