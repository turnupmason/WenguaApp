from __future__ import annotations
from pathlib import Path
import sqlite3,hashlib,json,shutil,re,collections,datetime
import argparse
parser=argparse.ArgumentParser(description="Rebuild source-provenance SQLite from real original 12-chapter baseline")
parser.add_argument("--baseline",required=True,type=Path)
parser.add_argument("--lost-source",required=True,type=Path)
parser.add_argument("--criminal-source",required=True,type=Path)
parser.add_argument("--output",required=True,type=Path)
a=parser.parse_args()
BASE=a.baseline;LOST=a.lost_source;CRIME=a.criminal_source;OUT=a.output
ROOT=OUT.parent;WORK=ROOT
if OUT.exists(): raise FileExistsError("Refuse to overwrite existing archival snapshot: " + str(OUT))
PAL=['巽四宫','离九宫','坤二宫','震三宫','中五宫','兑七宫','艮八宫','坎一宫','乾六宫']; PNUM=[4,9,2,3,5,7,8,1,6]
def J(o):return json.dumps(o,ensure_ascii=False,sort_keys=True,separators=(',',':'))
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def S(lines,n,m=None):return '\n'.join(lines[n-1:(n if m is None else m)])
def validate_integrity(c):
 assert c.execute('PRAGMA integrity_check').fetchone()[0]=='ok', 'bad SQLite integrity'
 assert not c.execute('PRAGMA foreign_key_check').fetchall(), 'foreign key violations'
def cells(L,start):
 assert L[start-1].startswith('┌'),(start,'not printed chart')
 out=[]
 for rr in range(3):
  row=start+1+rr*4
  v=[]
  for k in range(3):
   a=[q.strip() for q in L[row-1+k].split('│')[1:-1]]
   assert len(a)==3,(start,row,k,a)
   v.append(a)
  for col in range(3):
   i=rr*3+col; name,door,star=[q[col] for q in v];assert name.startswith(PAL[i]),(start,name,PAL[i]);n=PNUM[i]
   if n==5:
    assert name.startswith('中五宫'),(start,name)
    deity=''
    # 中五宫真原字段中不存在普通八神、门、星。将中宫原字保持原始字符。
    assert door.startswith('中宫原字：'),(start,door)
    door=door.partition('：')[2]
    assert not star,(start,star)
   else:
    assert '八神：' in name and door.startswith('门位原字：') and star.startswith('星位原字：'),(start,i,name,door,star)
    deity=name.split('八神：',1)[1].strip();door=door.partition('：')[2];star=star.partition('：')[2]
   out.append((n,row+col,name,deity,door,star))
 assert len(out)==9 and {x[0] for x in out}==set(range(1,10))
 return out

LOST_CASES=[
 dict(start=16,stop=49,chart=25,initial=(18,18),steps=[41,43,45],judgment=[41,45],feedback=[47],topic='发票'),
 dict(start=50,stop=89,chart=61,initial=(52,54),steps=[77,79,81,83,85],judgment=[77,85],feedback=[87],topic='身份证'),
 dict(start=90,stop=123,chart=99,initial=(92,92),steps=[113,117],judgment=[119],feedback=[121],topic='皮衣'),
 dict(start=124,stop=161,chart=133,initial=(126,126),steps=[149,151,153,155,157],judgment=[149,153,157],feedback=[159],topic='BP机'),
 dict(start=162,stop=199,chart=171,initial=(164,164),steps=[187,189,191,193,195],judgment=[187,195],feedback=[197],topic='现金'),
 dict(start=200,stop=255,chart=211,initial=(202,202),steps=[227,229,233,237,243],judgment=[245],feedback=[251],topic='重要文件',segments=[(253,'author_explicit_unpredicted_car_location')],disclosures=[231,235,239,247,249,253]),
 dict(start=256,stop=309,chart=265,initial=(260,260),steps=[281,283,285,295,299,303],judgment=[287,297,301,303],feedback=[305],topic='旅行后身份证',segments=[(307,'post_outcome_author_commentary')],disclosures=[293,307]),
 dict(start=310,stop=355,chart=319,initial=(312,312),steps=[335,337,339,345,349],judgment=[343,351],feedback=[353],topic='汽车被盗')]
CRIME_CASES=[
 dict(start=29,stop=63,chart=36,initial=(31,31),steps=[52,54,56,58],judgment=[60],feedback=[62],topic='报社现金被盗'),
 dict(start=64,stop=112,chart=71,initial=(66,66),steps=[87,89,91,93,95,97],judgment=[101,105,109],feedback=[103,107,111],topic='服装被盗',disclosures=[99,103,107]),
 dict(start=113,stop=149,chart=122,initial=(115,117),steps=[138,140,142,144],judgment=[140,142,144],feedback=[146],topic='持枪抢劫'),
 dict(start=150,stop=228,chart=159,extra=193,initial=(152,154),steps=[175,177,179,181,183,209,211,213,215,217,219],judgment=[175,181,183],feedback=[185],topic='银行运钞车抢劫',error=True,posthoc=[187,189,191,221,223,225,227],disclosures=[185,187,189,191,221,223,225,227]),
 dict(start=229,stop=261,chart=235,initial=(231,231),steps=[251,253,255,257],judgment=[251,255,257],feedback=[259],topic='发现尸块的刑案',posthoc=[261])]
LOST_SHA='ed3c80f32c213563bf35d9f9790e330ea04e4def404f6e6ca904006a94a9eaf9';CRIME_SHA='289465c220a0701545b9f093b4b91d041d600a4c9da67bf58e33a10ece0f0ea9'
GENERAL_CRIME=[('玄武小盗轻微犯罪',5),('天蓬重大暴力经济犯罪',5),('甲午辛罪人辅助用神',5),('旺衰与罪犯外貌职业性格',7),('临庚惯犯特殊类象',7),('临辛惯犯旧案',7),('临壬癸逃犯类象',7),('伤门及车辆',9),('景门及火器',9),('庚辛及金属器械',9),('巽螣蛇及绳索',9),('甲乙伤杜及木器',9),('伏吟内盘与本地',11),('反吟外盘流窜',11),('六合逃犯杜门藏身',13),('死门尸首代表',15),('死门临戊动机类象',15),('死门诸干桃花类象',15),('伤门白虎庚值使为捕盗',17),('捕盗宫克贼宫',17),('伏吟与反吟破案判断',17),('庚格与破案',17),('杜门干格与破案',17),('庚格年内',19),('庚格月内',19),('庚格日内',19),('庚格时辰',19),('两个庚格叠加',19),('阴日看庚上阳日庚下',19),('阴阳星选庚上下',19),('旬空出空马星值使定期',19),('死门加壬自讼',21),('壬临坤宫自首类象',21),('不可代替刑事取证',25)]
GENERAL_LOST=[('日时同宫寻回',5),('时干生日干',5),('反吟可寻',5),('时干空亡墓绝难寻',5),('日时内盘近处',7),('日时外盘远处',7),('日内时外',7),('时内日外',7),('时干玄武丢失盗或忘',9),('玄武克时宫盗',9),('天蓬克时宫盗',9),('玄武乘阴阳星',9),('玄武旺衰年龄',9),('时干生日干应期',11),('阴干庚上应期',11),('阳干庚下应期',11),('入库冲出应期',11),('旬空填实应期',11)]

DDL='''
CREATE TABLE IF NOT EXISTS historical_case_reasoning_trace(case_id TEXT NOT NULL,step_number INTEGER NOT NULL,source_line INTEGER NOT NULL,evidence_json TEXT NOT NULL CHECK(json_valid(evidence_json)),review_status TEXT NOT NULL DEFAULT 'source_anchored_candidate_needs_full_manual_audit',positive_training_eligible INTEGER NOT NULL DEFAULT 0 CHECK(positive_training_eligible IN(0,1)),PRIMARY KEY(case_id,step_number),FOREIGN KEY(case_id,step_number) REFERENCES historical_case_reasoning(case_id,step_number));
CREATE TABLE IF NOT EXISTS historical_palace_standardization(case_id TEXT NOT NULL,cast_key TEXT NOT NULL,palace INTEGER NOT NULL CHECK(palace BETWEEN 1 AND 9),center_stem TEXT,source_of_center_stem TEXT NOT NULL,standard_deity TEXT,standard_door TEXT,standard_star TEXT,normalized_status TEXT NOT NULL,original_raw_integrity_checked INTEGER NOT NULL DEFAULT 1,method_reference TEXT NOT NULL,derived_host_palace INTEGER CHECK(derived_host_palace=2 OR derived_host_palace IS NULL),derived_host_source TEXT,PRIMARY KEY(case_id,cast_key,palace));
CREATE TABLE IF NOT EXISTS historical_case_review_audit(case_id TEXT PRIMARY KEY REFERENCES cases(case_id),original_steps INTEGER NOT NULL,mechanical_step_trace INTEGER NOT NULL,human_complete_step_chains INTEGER NOT NULL DEFAULT 0,review_status TEXT NOT NULL,warning TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS chapter_archival_versions(archive_label TEXT PRIMARY KEY,baseline_sha256 TEXT NOT NULL,new_db_sha256 TEXT,contains_complete_private_copyright_source INTEGER NOT NULL,snapshot_type TEXT NOT NULL,created_utc TEXT NOT NULL,repo_public_archive_policy TEXT NOT NULL);
'''

def lex(t):
 out=[]
 for n in '开休生伤杜景死惊':
  if n+'门' in t:out.append('door:'+n)
 for n in '蓬任冲辅英芮柱心禽':
  if '天'+n in t:out.append('star:'+n)
 for n in ('玄武','白虎','九天','九地','六合','太阴','螣蛇','值符'):
  if n in t:out.append('deity:'+n)
 for n in '乾坤震巽坎离艮兑':
  if n+'宫' in t:out.append('trigram:'+n)
 return sorted(set(out))

def import_chapter(c,src,sha,ckey,key,cases,general,domain):
 raw=src.read_bytes();assert digest(src)==sha;L=raw.decode('utf8').splitlines();assert L[0]==('钱物丢失预测' if domain=='lost_property' else '刑事案件预测');
 assert len(L)==(362 if domain=='lost_property' else 261),(domain,len(L))
 title=L[0];assert c.execute('select 1 from sections where section_key=?',(key,)).fetchone() is None,'reimported source!'
 c.execute('INSERT INTO sections(book_id,section_key,title,original_text,sha256,content_version,reviewed) VALUES (?,?,?,?,?,1,0)',('shenqi',key,title,raw.decode('utf8'),sha))
 sid=c.execute('SELECT last_insert_rowid()').fetchone()[0]
 c.execute("INSERT INTO chapter_knowledge(chapter_key,book_id,title,source_sha256,source_length_bytes,knowledge_version,review_status) VALUES (?,'shenqi',?,?,?,'1','draft')",(ckey,title,sha,len(raw)))
 for j,(name,line) in enumerate(general,1):
  m=dict(topic=name,source_line=line,conditional=True,category='general',source_status='draft')
  c.execute('INSERT INTO semantic_assertions(chapter_key,concept_id,kind,relation,source_start_line,source_end_line,metadata_json,original_excerpt,review_status) VALUES (?,?,?,?,?,?,?,?,?)',(ckey,f'{domain}:general:{j:02}',domain+'_general','conditional_source',line,line,J(m),S(L,line),'draft'))
 summary=[]
 for i,x in enumerate(cases,1):
  assert L[x['start']-1].startswith('实例'),(i,L[x['start']-1]); id=f'shenqi.{domain}.case{i:02}';cc=cells(L,x['chart']);
  initial=S(L,*x['initial']);
  # Don't permit hindsight text in known_before.
  assert '结果' not in initial and '张志春按' not in initial,(domain,id)
  body='\n\n'.join(S(L,n) for n in x['steps']); judgment='\n'.join(S(L,n) for n in x['judgment']);feedback='\n'.join(S(L,n) for n in x['feedback']);
  c.execute('INSERT INTO cases(case_id,section_id,event_family_id,domain_id,known_before,author_yongshen_steps,author_judgment,later_feedback,reviewed) VALUES (?,?,?,?,?,?,?,?,0)',(id,sid,id,domain,initial,body,judgment,feedback))
  proto=dict(source_sha256=sha,source_span=[x['start'],x['stop']],original_chart_start=x['chart'],additional_chart_start=x.get('extra'),initial_lines=list(x['initial']),numbered_analysis_lines=x['steps'],author_judgment_lines=x['judgment'],feedback_lines=x['feedback'],event_family_id=id,source_document_not_verified_against_print=True,source_case_topics=x['topic'],negative_timing_result=bool(x.get('error')))
  c.execute("INSERT INTO historical_case_protocol(case_id,completeness,published_chart_verification,feedback_independently_verified,eligible_blind_test,case_source_sha256,metadata_json) VALUES (?,'whole_original_source','provided_transcription_not_independently_recast',0,0,?,?)",(id,sha,J(proto)))
  for pc in cc:
   c.execute("INSERT INTO historical_chart_cells(case_id,palace,source_line,palace_label_raw,deity_raw,door_position_raw,star_position_raw,source_status) VALUES (?,?,?,?,?,?,?,'original_source_panel_unverified_print')",(id,*pc))
  if 'extra' in x:
   c.execute("INSERT INTO historical_case_additional_casts(case_id,cast_key,cast_datetime_description,calendar_date,hour_ganzhi,source_chart_start,notes) VALUES (?,?,'Same event, later alternative casting method: 拆补法','1996-06-03','壬辰',?,'Post-event retrospective recast: DO NOT treat as prospective forecast')",(id,'chai_bu_analytic_recast',x['extra']))
   for pc in cells(L,x['extra']):
    c.execute('INSERT INTO historical_case_additional_cast_cells(case_id,cast_key,palace,source_line,palace_label_raw,deity_raw,door_position_raw,star_position_raw) VALUES (?,?,?,?,?,?,?,?)',(id,'chai_bu_analytic_recast',*pc))
  for k,n in enumerate(x['steps'],1):
   literal=S(L,n); assert literal.startswith('（') or(domain=='lost_property' and i==3 and n in (113,117)),(id,n,literal[:30]);
   phase='retrospective_alternative_cast_with_known_outcome' if domain=='criminal_case' and i==4 and n>=209 else 'initial_source_analysis';
   if domain=='criminal_case' and i==4 and n==183: phase='explicit_author_wrong_yingqi_negative_example'
   if domain=='lost_property' and i==7 and n>=295:phase='later_question_disclosure_subtopic'
   data=dict(phase=phase,original_source_line=n,original_book_sha256=sha,source_anchor_for_case=x['start'],source_cast_start=x.get('extra') if n>=209 and i==4 and domain=='criminal_case' else x['chart']);
   c.execute('INSERT INTO historical_case_reasoning(case_id,step_number,source_line,author_analysis_original,short_method_topic,metadata_json) VALUES (?,?,?,?,?,?)',(id,k,n,literal,phase,J(data)))
   c.execute('INSERT INTO semantic_assertions(chapter_key,concept_id,kind,relation,source_start_line,source_end_line,metadata_json,original_excerpt,review_status) VALUES (?,?,?,?,?,?,?,?,?)',(ckey,f'{domain}:case{i:02}:step{k:02}',domain+'_worked_step','source_example_not_approved_rule',n,n,J(data),literal,'draft'))
  disclosure_map={}
  for n in x['feedback']:
   disclosure_map[n]=('book_feedback','outcome')
  for n in x.get('disclosures',[]):
   if n not in disclosure_map:disclosure_map[n]=('post_initial_known','new_fact_or_retrospective_comment')
  for n,(phase,kind) in sorted(disclosure_map.items()):
   c.execute('INSERT INTO historical_case_disclosures(case_id,source_line,phase,fact_type,original_statement) VALUES (?,?,?,?,?)',(id,n,phase,kind,S(L,n)))
  for n,kind in x.get('segments',[]):
   c.execute('INSERT INTO historical_case_source_segments(case_id,segment_kind,source_start_line,source_end_line,original_text,metadata_json) VALUES (?,?,?,?,?,?)',(id,kind,n,n,S(L,n),J({'posthoc':True})))
  if i==4 and domain=='criminal_case':
   for n in x.get('posthoc',[]):
    c.execute('INSERT INTO historical_case_source_segments(case_id,segment_kind,source_start_line,source_end_line,original_text,metadata_json) VALUES (?,?,?,?,?,?)',(id,'retrospective_unprinted_or_author_annotation',n,n,S(L,n),J({'available_before_initial_cast':False})))
  for n in x.get('posthoc',[]) if not(i==4 and domain=='criminal_case') else []:
   c.execute('INSERT INTO historical_case_source_segments(case_id,segment_kind,source_start_line,source_end_line,original_text,metadata_json) VALUES (?,?,?,?,?,?)',(id,'post_outcome_author_commentary',n,n,S(L,n),J({'posthoc':True})))
  if domain=='lost_property' and i==3:
   c.execute("INSERT INTO historical_case_disclosures(case_id,source_line,phase,fact_type,original_statement) VALUES (?,115,'after_initial_unknown_question','question_disclosed',?)",(id,S(L,115)))
  if domain=='lost_property' and i==6:
   for n in [231,235,239,247,249,253]:
    if n in disclosure_map:continue
    c.execute('INSERT INTO historical_case_disclosures(case_id,source_line,phase,fact_type,original_statement) VALUES (?,?,?,?,?)',(id,n,'post_initial_question','new_fact_or_location_omission',S(L,n)))
  verdict='author_book_error_explicit' if x.get('error') else 'author_book_success_default'
  corrections=[187,209,211,213,215,217,219,223] if x.get('error') else []
  c.execute("INSERT INTO historical_case_book_verdicts(event_family_id,primary_case_id,verdict,explicit_source_correction,source_correction_lines_json,feedback_source_lines_json,independent_external_verification,app_output_protocol,evidence_review_status,note) VALUES (?,?,?,?,?,?,'not_verified','single_answer_for_one_cast','book_source_only',?)",(id,id,verdict,int(bool(x.get('error'))),J(corrections),J(x['feedback']),'Case4 original timing explicitly admitted inaccurate; later alternative casting method is hindsight' if x.get('error') else 'Book claim only; NOT law-enforcement evidence'))
  summary.append(dict(case_id=id,title=x['topic'],numbered_steps=len(x['steps']),source_span=[x['start'],x['stop']],chart_starts=[x['chart']]+([x['extra']] if x.get('extra') else []),book_outcome_label=verdict))
 return dict(chapter=ckey,source_sha256=sha,bytes=len(raw),lines=len(L),cases=len(cases),source_casts=sum(1+int('extra' in x) for x in cases),author_steps=sum(len(x['steps']) for x in cases),general_methods=len(general),case_details=summary)

SOURCE_CHAPTERS={}
with sqlite3.connect('file:'+str(BASE)+'?mode=ro',uri=True) as source, sqlite3.connect(OUT) as dst:
 source.backup(dst)
 dst.executescript(DDL);dst.execute('PRAGMA foreign_keys=ON')
 with dst:
  SOURCE_CHAPTERS['13']=import_chapter(dst,LOST,LOST_SHA,'shenqi/lost_money_property_prediction_ch09/v1','lost_money_property_prediction_ch09',LOST_CASES,GENERAL_LOST,'lost_property')
  SOURCE_CHAPTERS['14']=import_chapter(dst,CRIME,CRIME_SHA,'shenqi/criminal_case_prediction_ch10/v1','criminal_case_prediction_ch10',CRIME_CASES,GENERAL_CRIME,'criminal_case')
 # Align ALL 71 primary nine-palace charts and 5 supplementary nine-palace boards, without changing the original literal tables.
 with dst:
  problems=[]
  for t,ck in [('historical_chart_cells','primary'),('historical_case_additional_cast_cells','extra')]:
   rows=dst.execute('SELECT case_id,'+('cast_key,' if ck=='extra' else '')+'palace,palace_label_raw,deity_raw,door_position_raw,star_position_raw FROM '+t).fetchall()
   for row in rows:
    if ck=='extra':cid,cast,pal,lab,deity,door,star=row
    else:cid,pal,lab,deity,door,star=row;cast='primary'
    if pal==5:
     data=' '.join(str(x) for x in (lab,deity,door,star) if x)
     tokens=re.findall('[乙丙丁戊己庚辛壬癸]',data)
     normalized=tokens[0] if len(set(tokens))==1 else (tokens[0] if len(tokens)==1 else None)
     if normalized is None:problems.append((cid,cast,data))
     # 避免将中宫硬补八门八神，唯一落地事实为原书记录的中宫原字/六仪。
     fields=(cid,cast,5,normalized, 'original_center_literal' if normalized else 'unresolved_original_center',None,None,None,'center_not_applicable_sanshu_three_fields' if normalized else 'center_stem_unresolved',1,'keep original centre stem; no fake god/door/star; 寄坤二宫 based on shijia_qiju',2,'shijia_qiju:五宫寄坤二宫')
    else:
     assert deity.strip() and door.strip() and star.strip(),(cid,cast,pal,lab,deity,door,star)
     fields=(cid,cast,pal,None,'not_a_center',deity,door,star,'original_outer_palace_literal',1,'existing source chart fields unchanged',None,None)
    dst.execute('INSERT INTO historical_palace_standardization(case_id,cast_key,palace,center_stem,source_of_center_stem,standard_deity,standard_door,standard_star,normalized_status,original_raw_integrity_checked,method_reference,derived_host_palace,derived_host_source) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)',fields)
  # Rebuild source-anchored candidates for EVERY historical step, actual palace mentions and lexical cross-chapter IDs; no speculative author explanations.
  allsteps=dst.execute('SELECT case_id,step_number,source_line,author_analysis_original,short_method_topic,metadata_json FROM historical_case_reasoning ORDER BY case_id,step_number').fetchall()
  for cid,k,n,txt,topic,meta in allsteps:
   existing=dst.execute('SELECT 1 FROM historical_case_reasoning_trace WHERE case_id=? AND step_number=?',(cid,k)).fetchone()
   if existing:continue
   cast='primary'
   m=json.loads(meta)
   if isinstance(m,dict) and m.get('source_cast_start')==193 and cid=='shenqi.criminal_case.case04':cast='chai_bu_analytic_recast'
   # Citations are only lexical candidates unless chart binding is unambiguously observed; preserve author reasoning text separately.
   mentions=sorted(set(int(x) for x in re.findall(r'(?<!\d)([1-9])宫',txt)))
   nameToP={'巽':4,'离':9,'坤':2,'震':3,'中':5,'兑':7,'艮':8,'坎':1,'乾':6}
   for name,num in nameToP.items():
    if name+'宫' in txt:mentions.append(num)
   real=dst.execute('SELECT palace FROM historical_palace_standardization WHERE case_id=? AND cast_key=?',(cid,cast)).fetchall()
   known={q[0] for q in real}
   assert set(mentions).issubset(known),(cid,n,mentions,known)
   negative=('error' in topic or 'incorrect' in topic or 'retrospect' in topic or 'posthoc' in topic)
   evidence={'original_source_case':cid,'source_line':n,'step_number':k,'source_author_text_is_saved_in_private_table':True,
       'source_mentioned_palace_candidates':sorted(set(mentions)),'cast_key':cast,'cross_chapter_concept_lexical_candidates':lex(txt),
       'method_topic_from_source':topic,'stage':m.get('phase') or m.get('reasoning_layer') or topic,
       'reasoning_verified_by_human':False,'author_full_condition_chain_verified':False,'positive_training_eligible':False,
       'potential_retrospective_negative_or_error':negative,'hallucinated_missing_facts_prohibited':True}
   dst.execute("INSERT INTO historical_case_reasoning_trace(case_id,step_number,source_line,evidence_json,review_status,positive_training_eligible) VALUES (?,?,?,?,'source_anchored_candidate_needs_full_manual_audit',0)",(cid,k,n,J(evidence)))
  for cid, in dst.execute('SELECT case_id FROM cases').fetchall():
   ct=dst.execute('SELECT count(*) FROM historical_case_reasoning WHERE case_id=?',(cid,)).fetchone()[0]
   traced=dst.execute('SELECT count(*) FROM historical_case_reasoning_trace WHERE case_id=?',(cid,)).fetchone()[0]
   assert ct==traced
   dst.execute("INSERT INTO historical_case_review_audit(case_id,original_steps,mechanical_step_trace,human_complete_step_chains,review_status,warning) VALUES (?,?,?,0,'source_anchor_only_needs_full_manual_evidence_chain','All original steps indexed; author full reasoning and independent validation still require review')",(cid,ct,traced))
  dst.execute("INSERT INTO chapter_archival_versions(archive_label,baseline_sha256,contains_complete_private_copyright_source,snapshot_type,created_utc,repo_public_archive_policy) VALUES (?,?,1,'full_private_sqlite',?,?)",('shenqi_14_chapters_71_cases',digest(BASE),datetime.datetime.now(datetime.timezone.utc).isoformat(),'USER_EXPLICITLY_AUTHORIZED_PUBLIC_GITHUB_ARCHIVE_FOR_THIS_SNAPSHOT'))
 validate_integrity(dst)
 print('normalization issues',problems)
 counts={t:dst.execute('SELECT count(*) FROM '+t).fetchone()[0] for t in ['sections','cases','historical_chart_cells','historical_case_additional_casts','historical_case_additional_cast_cells','historical_case_reasoning','semantic_assertions','historical_case_reasoning_trace','historical_palace_standardization','historical_case_book_verdicts','historical_case_disclosures','historical_case_review_audit']}
 print('counts',counts)
 assert counts['sections']==14 and counts['cases']==71 and counts['historical_chart_cells']==639 and counts['historical_case_additional_casts']==5 and counts['historical_case_additional_cast_cells']==45 and counts['historical_palace_standardization']==684
 assert counts['historical_case_reasoning']==254+36+29

# The historical 12 chapters must be preserved byte-for-byte in source, original cases, raw charts and step text.
with sqlite3.connect(BASE) as old,sqlite3.connect(OUT) as new:
 for table in ['sections','cases','historical_chart_cells','historical_case_additional_casts','historical_case_additional_cast_cells','historical_case_reasoning','historical_case_disclosures','historical_case_protocol','historical_case_book_verdicts','historical_case_source_segments','chapter_knowledge','semantic_assertions']:
  cols=[q[1] for q in old.execute('PRAGMA table_info('+table+')')]
  pk=next((x for x in cols if x in ('section_id','case_id','chapter_key','concept_id')),None)
  rows=old.execute('SELECT '+','.join(cols)+' FROM '+table).fetchall()
  exist=new.execute('SELECT '+','.join(cols)+' FROM '+table+' LIMIT '+str(len(rows))).fetchall()
  # For multikey tables skip ordering and compare using frequency counters
  assert collections.Counter(rows)-collections.Counter(new.execute('SELECT '+','.join(cols)+' FROM '+table).fetchall())=={},(table,'old modified')
 print('All original 12 chapters and existing case rows preserved. SQLite backup OK.')

m={'created_source_file_names':[LOST.name,CRIME.name],'original_12chapter_sha256':digest(BASE),'private_snapshot':OUT.name,'private_snapshot_sha256':digest(OUT),'private_db_size':OUT.stat().st_size,'counts':counts,'chapter13':SOURCE_CHAPTERS['13'],'chapter14':SOURCE_CHAPTERS['14'],'center_rule':'Centre palace original stem kept; derivation 五宫寄坤二宫 from shijia_qiju stored separately; never fabricated door/star/deity; 76 actual charts normalized.','public_archive_user_consent':'User explicitly authorized public repository upload of the full original-content SQLite'}
(WORK/(OUT.stem+'_manifest.json')).write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(m,ensure_ascii=False,indent=2)[:5000])
