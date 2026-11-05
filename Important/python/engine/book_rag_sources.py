"""Build a private source library from WenguaApp's already reviewed two books.

Full chapter text remains immutable. Reviewed literal fragments keep shared
conditions in one retrieval bundle. Case coordinates and feedback never become
universal rules. No supervised answer is used as source text.
"""
from collections import Counter,defaultdict
from pathlib import Path
import json,re,sqlite3
from . import book_rag as rag

BOOKS={'shenqi':{'title':'神奇之门','author':'张志春'},'kaiwu':{'title':'开悟之门','author':'张志春'}}
SECTION_DOMAINS={5:'health',6:'marriage',7:'pregnancy',8:'education',9:'employment',10:'business_profit',
11:'travel_abroad',12:'missing_person',13:'lost_property',14:'criminal_case',15:'litigation',16:'sports_competition',
17:'military_history_source',18:'weather',19:'geography_environment_historical_source',20:'life_opportunity_book_study',
21:'miscellaneous_historical_source',26:'life_opportunity_book_study',27:'health',29:'marriage',30:'employment',31:'education',
32:'missing_person',33:'business_profit',34:'lost_property',35:'travel_abroad',36:'criminal_case',37:'weather',
38:'life_opportunity_book_study',39:'life_opportunity_book_study',40:'geography_environment_historical_source',41:'litigation',42:'competition_evaluation'}


def compact(x):return ''.join(x.split())

def literal_selector(chapter,lo,hi,quote=None):
    lines=chapter['original_text'].splitlines();raw='\n'.join(lines[lo-1:hi])
    if not raw:raise ValueError('Empty source selector')
    if quote is None:a,b=0,len(raw)
    else:
        normalized=[];positions=[]
        for i,char in enumerate(raw):
            if not char.isspace():normalized.append(char);positions.append(i)
        key=compact(quote);text=''.join(normalized);offset=text.find(key)
        if not key or offset<0:raise ValueError('Reviewed excerpt not literal at its source coordinates')
        a,b=positions[offset],positions[offset+len(key)-1]+1
    return {'chapter':rag.chapter_key(chapter),'source_sha256':chapter['source_sha256'],'lines':[lo,hi],
            'chars':[a,b],'quote_sha256':rag.digest(raw[a:b])}


def build_two_book_library(db_path,pack,coordinates,fragments,inventory,step_reviews=(),case_links=()):
    from .qwen_book_dataset_v3 import SOURCE_SHA256
    if rag.digest(Path(db_path).read_bytes())!=SOURCE_SHA256 or pack['source_sha256']!=SOURCE_SHA256:
        raise ValueError('Not the pinned immutable WenguaApp two-book database')
    db=sqlite3.connect(Path(db_path).resolve().as_uri()+'?mode=ro',uri=True);db.row_factory=sqlite3.Row
    try:sections={r['section_id']:dict(r) for r in db.execute('SELECT * FROM sections')}
    finally:db.close()
    chapters={sid:{'book_id':s['book_id'],'book_title':BOOKS[s['book_id']]['title'],
        'chapter_id':str(sid),'title':s['title'],'source_revision':s['content_version'],
        'source_sha256':s['sha256'],'original_text':s['original_text'],'method_id':rag.METHOD} for sid,s in sections.items()}
    docs={};dispositions=[];raw_ranges=defaultdict(list)
    for sid,ranges in coordinates.items():
        for span in ranges:
            if span['case_id'] not in {d['case_id'] for d in pack['dossiers']}:raise ValueError('Unknown event in source coordinates')
            raw_ranges[int(sid)].append(span)
    def historical(unit):
        if unit.get('case_ids'):return True
        # Inline retellings of an earlier printed case can occur outside the
        # registered case range. Preserve them as historical reference, not a
        # prospective rule or a newly independent event.
        if re.search(r'《神奇之门》第.{0,12}页|《开悟之门》第.{0,12}页',unit.get('original_quote','')):return True
        if unit.get('match_status')=='sqlite_original_transcription':return True
        sid=unit.get('section_id');lo,hi=unit.get('lines',[0,0])
        return any(max(lo,x['lines'][0])<=min(hi,x['lines'][1]) for x in raw_ranges.get(sid,[]))
    def add(kind,parts,*,cues=(),domains=(),case_ids=(),phase='',topic='source',parent_ids=(),title='',related_phases=()):
        unique={rag.dumps(p):p for p in parts}
        parts=sorted(unique.values(),key=lambda p:(p['chapter'],p['lines'],p['chars']))
        identity=rag.dumps({'kind':kind,'parts':parts,'case_ids':sorted(case_ids)})
        key='rag:'+rag.digest(identity)[:24]
        if key not in docs:docs[key]={'id':key,'kind':kind,'parts':parts,'title':title,'cues':[],
            'domains':list(domains),'case_ids':list(case_ids),'phase':phase,'topic':topic,
            'parent_source_ids':[],'review_status':'reviewed_source_selector','related_case_phases':list(related_phases),
            'case_context_complete':False if kind=='case' else None}
        docs[key].setdefault('topics',[])
        if topic not in docs[key]['topics']:docs[key]['topics'].append(topic)
        docs[key]['cues']=list(dict.fromkeys([*docs[key]['cues'],*cues]))
        docs[key]['parent_source_ids']=list(dict.fromkeys([*docs[key]['parent_source_ids'],*parent_ids]))
        return key
    source_units=pack['units'];by_source=defaultdict(set)
    for row in pack['records']:
        if row['case_ids'] or row['source_mode'].startswith(('attributed_','retrospective_')):continue
        units=[source_units[u] for u in row['source_ids']]
        if any(historical(u) or u.get('section_id') not in chapters for u in units):continue
        pieces=fragments.get(row.get('parent_task_id',row['id']))
        parts=[]
        if pieces:
            if any(f['source_id'] not in row['source_ids'] for f in pieces):raise ValueError('Fragment does not belong to reviewed lesson')
            for fragment in pieces:
                u=source_units[fragment['source_id']]
                if u['original_quote'][fragment['start']:fragment['end']]!=fragment['text']:raise ValueError('Reviewed fragment changed')
                parts.append(literal_selector(chapters[u['section_id']],*u['lines'],fragment['text']))
        else:
            for u in units:parts.append(literal_selector(chapters[u['section_id']],*u['lines'],u['original_quote']))
        scoped={SECTION_DOMAINS[u['section_id']] for u in units if u['section_id'] in SECTION_DOMAINS}
        topic='casting' if any(u['section_id'] in (1,24) for u in units) else 'timing' if any('timing' in u.get('kind','') or '应期' in u['original_quote'] for u in units) else 'rule'
        # Cues are editorial search aids only; assistant targets never enter
        # a retrieved evidence body or FTS source-text column.
        cues=[m['content'] for m in row['messages'] if m['role']=='user']
        docid=add('rule',parts,cues=cues,domains=sorted(scoped),phase='general_rule',topic=topic,
                  parent_ids=row['source_ids'],title='；'.join(sorted({u['chapter'] for u in units})))
        docs[docid]['source_rule_kinds']=sorted(set(docs[docid].get('source_rule_kinds',[]))|{u.get('kind','unclassified') for u in units})
        docs[docid]['source_concepts']=sorted(set(docs[docid].get('source_concepts',[]))|{u.get('concept','') for u in units})
        for uid in row['source_ids']:by_source[uid].add(docid)
    # Account for all 1451 reviewed source materials, including explicit
    # reference-only examples and structural material. Nothing is silently lost.
    for unit in inventory:
        uid=unit['id'];c=chapters[unit['section_id']]
        if not by_source[uid] and not historical(unit):
            key=compact(unit['original_quote'])
            for doc in docs.values():
                if doc['kind']!='rule':continue
                if any(part['chapter']==rag.chapter_key(c) and key in compact(rag.quote_part({rag.chapter_key(c):c},part)) for part in doc['parts']):
                    by_source[uid].add(doc['id'])
        if by_source[uid]:state='reviewed_rule_bundle'
        else:
            state='reference_only_historical_overlap' if historical(unit) else 'reference_only_no_teaching_target'
            part=literal_selector(c,*unit['lines'],unit['original_quote'])
            docid=add('reference',[part],cues=[unit.get('concept',''),c['title']],
                phase='source_context_not_universal_rule',parent_ids=[uid],title=c['title'])
            by_source[uid].add(docid)
        dispositions.append({'review_key':unit['review_key'],'source_id':uid,'state':state,'document_ids':sorted(by_source[uid])})
    cases={d['case_id']:{'case_id':d['case_id'],'event_family_id':d['original_event_family'],'domain':d['domain'],
        'source_scope':'historical_book_report_not_independent_prediction',
        'has_phase_records':bool(d['source_disclosures'] or d['source_phase_events']),
        'index_contains_no_supervised_target_answers':True} for d in pack['dossiers']}
    dossiers={d['case_id']:d for d in pack['dossiers']}
    course_groups={r['case_id']:r['group'] for r in pack['records'] if r['task']=='author_analysis_review'}
    for cid in cases:cases[cid]['course_split_group']=course_groups[cid]
    for sid,ranges in raw_ranges.items():
        for span in ranges:
            cases[span['case_id']].setdefault('spans',[]).append({'chapter':rag.chapter_key(chapters[sid]),'lines':span['lines']})
    for case in cases.values():
        full='\n'.join('\n'.join(chapters[int(span['chapter'].split('/')[-1])]['original_text'].splitlines()[span['lines'][0]-1:span['lines'][1]]) for span in case['spans'])
        case['literal_years']=sorted(set(re.findall(r'(?<!\d)(?:18|19|20)\d{2}(?!\d)',full)))
    # Paragraphs keep source layout and exact text. Missing phase labels remain
    # historical_mixed; never infer pre-outcome status from a generic title.
    for sid,ranges in raw_ranges.items():
        chapter=chapters[sid];lines=chapter['original_text'].splitlines()
        for span in ranges:
            cid=span['case_id'];d=dossiers[cid];lo,hi=span['lines'];i=lo
            known={e['source_line']:e.get('phase','historical_mixed') for e in d['source_disclosures'] if e.get('source_line') and 1<=e['source_line']<=len(lines) and compact(e.get('original_statement','')) in compact(lines[e['source_line']-1])}
            phases=sorted(set(known.values()))
            while i<=hi:
                while i<=hi and not lines[i-1].strip():i+=1
                if i>hi:break
                end=i
                while end<hi and lines[end].strip():end+=1
                part=literal_selector(chapter,i,end)
                present={known[n] for n in range(i,end+1) if n in known}
                phase=next(iter(present)) if len(present)==1 else 'historical_mixed'
                add('case',[part],cues=[cid,chapter['title']],domains=[rag.DOMAIN_EQUIVALENTS.get(d['domain'],d['domain'])],
                    case_ids=[cid],phase=phase,title=chapter['title'],related_phases=phases)
                i=end+1
    review_by_step={(x['case_id'],x['step']):x for x in step_reviews}
    analysis_count=0
    for cid,d in dossiers.items():
        cases[cid]['author_step_source_records']=[]
        cases[cid]['primary_printed_chart_transcription']=d['primary_printed_chart']
        cases[cid]['additional_printed_charts_transcription']=d['additional_printed_charts']
        cases[cid]['chart_status']='original_source_transcription_not_recast_not_a_new_question_chart'
        for step in d['author_steps']:
            u=source_units[step['source_id']];chapter=chapters[u['section_id']]
            part=literal_selector(chapter,*u['lines'],u['original_quote'])
            linked=[x for x in case_links if cid in x['case_ids'] and x['chapter']==rag.chapter_key(chapter) and x['analysis_lines'][0]<=u['lines'][0]<=u['lines'][1]<=x['analysis_lines'][1]]
            linked_ids=linked[0]['case_ids'] if linked else [cid]
            parts=[literal_selector(chapter,*span) for span in linked[0]['context_lines']] if linked else [part]
            if linked and (not linked[0].get('source_reviewed') or any(c not in cases for c in linked_ids)):raise ValueError('Unreviewed cross-case comparison')
            reviewed=review_by_step.get((cid,step['step']),{})
            annotation={'case_id':cid,'step':step['step'],'source_id':step['source_id'],
                'speaker_status':reviewed.get('speaker_status','original_source_speaker_not_assumed'),
                'correction_required':reviewed.get('correction_required',False)}
            docid=add('case',parts,cues=[cid,chapter['title'],'原分析第'+str(step['step'])+'步'],
                domains=[rag.DOMAIN_EQUIVALENTS.get(d['domain'],d['domain'])],case_ids=linked_ids,
                phase='author_cross_case_comparison' if linked else 'attributed_case_analysis_not_prospective_rule',topic='case_analysis',
                parent_ids=[step['source_id']],title=chapter['title'])
            docs[docid].setdefault('analysis_annotations',[]).append(annotation)
            if linked:docs[docid]['comparison_context_review']=linked[0]
            cases[cid]['author_step_source_records'].append(annotation|{'document_id':docid})
            analysis_count+=1
        # Keep original registry fields visible only in explicit case export;
        # retrieved evidence remains located literal text, never these summaries.
        cases[cid]['registry_original_judgment_not_a_literal_quote']=d['author_original_judgment']
        cases[cid]['registry_feedback_not_a_literal_quote']=d['later_feedback_separate']
        cases[cid]['unlocated_registry_judgment_fragments']=d['unlocated_registry_judgment_fragments_omitted']
        cases[cid]['unlocated_registry_feedback_fragments']=d['unlocated_registry_feedback_fragments_omitted']
    # Full chapters remain the primary record. Residual nonblank source lines
    # are indexed as explicit reference context, including diagrams and labels.
    covered=defaultdict(set)
    for doc in docs.values():
        for p in doc['parts']:covered[p['chapter']].update(range(p['lines'][0],p['lines'][1]+1))
    for chapter in chapters.values():
        key=rag.chapter_key(chapter);lines=chapter['original_text'].splitlines();i=1
        while i<=len(lines):
            if not lines[i-1].strip() or i in covered[key]:i+=1;continue
            end=i
            while end<len(lines) and lines[end].strip() and end+1 not in covered[key]:end+=1
            add('reference',[literal_selector(chapter,i,end)],cues=[chapter['title']],
                phase='full_source_context',title=chapter['title'])
            i=end+1
    library={'schema':rag.SCHEMA,'books':BOOKS,'chapters':list(chapters.values()),'documents':list(docs.values()),'cases':cases,
        'source_database_sha256':SOURCE_SHA256,'reviewed_inventory':dispositions,
        'qa_answers_indexed':False,'production_prediction_verified':False,'reviewed_cross_case_links':case_links}
    report=rag.validate_library(library)
    report['located_case_analysis_records']=analysis_count;report['original_index_review_records']=len(step_reviews);report['inventory_materials']=len(dispositions);report['inventory_dispositions']=dict(Counter(x['state'] for x in dispositions))
    return library,report


def stage_chapter(raw_path,*,book_id,book_title,chapter_id,title,method_id,revision):
    """Archive incoming text as draft. It is deliberately not an index library."""
    data=Path(raw_path).read_bytes();text=data.decode('utf-8-sig')
    if not text.strip() or not all((book_id,book_title,chapter_id,title,method_id,revision)):raise ValueError('Complete source identity and method required')
    return {'schema':'wengua_incoming_chapter_draft_v1','review_status':'draft_not_searchable',
        'raw_uploaded_bytes_sha256':rag.digest(data),'book':{'id':book_id,'title':book_title},
        'chapter':{'book_id':book_id,'book_title':book_title,'chapter_id':chapter_id,'title':title,
            'method_id':method_id,'source_revision':revision,'original_text':text,'source_sha256':rag.digest(text)},
        'review_required':'Locate rules/conditions/cases and original feedback separately before producing reviewed selectors'}


def reviewed_chapter_library(draft,review):
    """Convert explicit source-audited selectors; no LLM-generated text or auto approval."""
    if draft.get('schema')!='wengua_incoming_chapter_draft_v1' or review.get('review_status')!='source_review_completed':raise ValueError('A source review must precede indexing')
    c=draft['chapter'];key=rag.chapter_key(c)
    if review.get('source_sha256')!=c['source_sha256']:raise ValueError('Review is for a different chapter revision')
    cases={}
    for event in review.get('cases',[]):
        cid=event['case_id']
        if cid in cases:raise ValueError('Duplicate new event ID')
        if not event.get('event_family_id') or not event.get('domain'):raise ValueError('Event family and domain are required')
        cases[cid]={**event,'spans':[{'chapter':key,'lines':span} for span in event['source_lines']],
                    'source_scope':'historical_book_report_not_independent_prediction'}
    docs=[];coverage=set()
    for selector in review['selectors']:
        if selector['kind'] not in ('rule','case','reference'):raise ValueError('Unknown reviewed selector kind')
        parts=[literal_selector(c,*span) for span in selector['source_lines']]
        for part in parts:coverage.update(range(part['lines'][0],part['lines'][1]+1))
        # Several source ranges are one condition bundle; do not split them
        # because common premises may be in a preceding paragraph.
        doc={'id':'rag:'+rag.digest(rag.dumps({'chapter':key,'hash':c['source_sha256'],'selector':selector}))[:24],
             'kind':selector['kind'],'parts':parts,'title':selector.get('title',c['title']),
             'cues':selector.get('search_cues',[]),'domains':selector.get('domains',[]),
             'case_ids':selector.get('case_ids',[]),'phase':selector['phase'],
             'topic':selector.get('topic','source'),'parent_source_ids':[],
             'review_status':'reviewed_source_selector','related_case_phases':selector.get('related_case_phases',[])}
        docs.append(doc)
    lines=c['original_text'].splitlines()
    for n,line in enumerate(lines,1):
        if line.strip() and n not in coverage:
            docs.append({'id':'rag:'+rag.digest(key+c['source_sha256']+':reference:'+str(n))[:24],
                'kind':'reference','parts':[literal_selector(c,n,n)],'title':c['title'],'cues':[c['title']],
                'domains':[],'case_ids':[],'phase':'unclassified_source_context','topic':'source','parent_source_ids':[],
                'review_status':'reviewed_source_selector','related_case_phases':[]})
    library={'schema':rag.SCHEMA,'books':{c['book_id']:{k:v for k,v in draft['book'].items() if k!='id'}},
        'chapters':[c],'documents':docs,'cases':cases,'qa_answers_indexed':False}
    rag.validate_library(library);return library
