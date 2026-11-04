"""Book-only curriculum, rebuilt from immutable original texts and printed cases.

No legacy scoring engine, role profile, generated verdict, or old QA is read.
Coordinates may be supplied as a separately verified source index. Source
fidelity is distinct from semantic review and real-world predictive validity.
"""
from __future__ import annotations

from collections import Counter, defaultdict
import csv
import gzip
import hashlib
import json
from pathlib import Path
import re
import sqlite3

SOURCE_SHA256 = '21362e6f0266c03dcdc4a7ef35f45954ba274ae6458de0ba341132abca7d0405'
VERSION = 'wengua_book_only_curriculum_v3'
FORMATS = ('foundation_qa', 'conditional_dialogue', 'chart_application', 'complete_case')
QUOTAS = dict(zip(FORMATS, (200000, 300000, 300000, 200000)))
SYSTEM = ('依据《神奇之门》《开悟之门》的知识和本题资料，直接用自然中文回答。'
          '保留适用条件、例外、人物关系和证据顺序。原书复盘只说作者确实写出的分析，'
          '区分初断、后续披露和后来反馈；未提供的信息不补造。')
BOOKS = {'shenqi': '《神奇之门》', 'kaiwu': '《开悟之门》'}
TABLES = ('sections', 'cases', 'historical_case_protocol', 'semantic_assertions',
          'historical_case_reasoning', 'historical_chart_cells',
          'historical_case_additional_casts', 'historical_case_additional_cast_cells',
          'historical_case_disclosures', 'historical_case_phase_events')
FORBIDDEN = ('HEALTH_V9_V11', 'STRENGTH_200', 'candidate_five_grade_quantization',
             'pre_relationship_bonus_score', 'unique_selected_palaces', '宫位基础分')
CONDITIONS = re.compile(r'如果|假如|虽然|但是|但|若|只有|除非|必须|不宜|否则|如遇|如逢|如临|逢|不能|兼看|还要|综合')
CAUSAL = re.compile(r'所以断|故断|因此断|由此断|综合这些信息|说明|表明|可见|由此可知|所以说|因此')
BASIC_KINDS = {'symbol', 'symbol_aspect', 'stem_pair', 'door_pair', 'door_stem',
               'trigram_palace_mapping', 'stem_polarity_element', 'stem_direction_symbolism',
               'branch_fixed_palace', 'branch_polarity_element', 'nine_star_original_palace',
               'eight_deity_contextual_symbol', 'original_earth_stem_layout', 'six_jia_hidden_instrument'}


def dumps(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':'))


def digest(value):
    return hashlib.sha256(value if isinstance(value, bytes) else value.encode('utf8')).hexdigest()


def clean(text):
    return re.sub(r'\s+', '', text)


def readable(text):
    """Sentence layout only; conditions separated by commas stay together."""
    return re.sub(r'([。！？])(?=[^\n”’」』])', r'\1\n', text.strip())


def locate(section, text, reported_line=None):
    original = section['original_text']
    matches = [m.start() for m in re.finditer(re.escape(text), original)] if text else []
    if matches:
        p = min(matches, key=lambda x: abs(original.count('\n', 0, x)+1-(reported_line or 1)))
        return [original.count('\n', 0, p)+1, original.count('\n', 0, p+len(text))+1], 'literal'
    cached = section.get('_normalized')
    if cached is None:
        offsets = [i for i, ch in enumerate(original) if not ch.isspace()]
        cached = (''.join(original[i] for i in offsets), offsets)
        section['_normalized'] = cached
    normalized, offsets = cached
    needle = clean(text)
    p = normalized.find(needle) if needle else -1
    if p >= 0:
        return [original.count('\n', 0, offsets[p])+1,
                original.count('\n', 0, offsets[p+len(needle)-1])+1], 'whitespace_only'
    return None, 'unlocated'


def located_pieces(section, text):
    """Keep only actual original text, not a registry's editorial paraphrase."""
    text=(text or '').strip()
    if not text:return [],[]
    if locate(section,text)[0]:return [text],[]
    chunks=[part.strip() for part in re.split(r'\n+|(?<=[。！？])',text) if part.strip()]
    found=[];pending=[]
    for part in chunks:
        (found if locate(section,part)[0] else pending).append(part)
    return found,pending


class Groups:
    def __init__(self):
        self.parent = {}

    def root(self, key):
        self.parent.setdefault(key, key)
        while self.parent[key] != key:
            self.parent[key] = self.parent[self.parent[key]]
            key = self.parent[key]
        return key

    def join(self, keys):
        roots = sorted({self.root(k) for k in keys})
        for key in roots[1:]:
            self.parent[key] = roots[0]
        return roots[0]


def split_for(group):
    value = int(digest('book-only-v3:'+group)[:8], 16) % 10
    return 'test' if value == 0 else 'validation' if value == 1 else 'train'


def subject(concept, text):
    parts = concept.split(':')
    if parts[0] in ('trigram', 'stem', 'star', 'door', 'deity', 'branch') and len(parts)>1:
        return parts[1] + ('卦' if parts[0]=='trigram' else '干' if parts[0]=='stem' else '')
    if concept.startswith('heaven_over_earth:') and len(parts)>=3:
        return '天盘'+parts[-2]+'加地盘'+parts[-1]
    if concept.startswith('door_over_door:') and len(parts)>=3:
        return parts[-2]+'门加'+parts[-1]+'门'
    if concept.startswith('door_over_stem:') and len(parts)>=3:
        return parts[-2]+'门加'+parts[-1]+'干'
    if concept=='health:role:illness_star':return '天芮星在疾病预测中的取用'
    if concept in ('health:role:doctor_star', 'health:role:medicine_yi'):return '天心星与乙奇在疾病预测中的取用'
    first = re.split(r'[。！？\n]', re.sub(r'^\s*[（(]?\d+[)）.、]?\s*', '', text), 1)[0]
    return '“'+first[:24]+('…' if len(first)>24 else '')+'”这段'


def premise_target(text):
    """Only an author's explicit written inference; no invented causal graph."""
    for match in CAUSAL.finditer(text):
        if match.start()>=18 and len(text)-match.start()>=8:
            return text[:match.start()], text[match.start():]
    return None


def load_tables(db_path):
    if digest(Path(db_path).read_bytes()) != SOURCE_SHA256:
        raise ValueError('Unexpected immutable book archive')
    db = sqlite3.connect(Path(db_path).resolve().as_uri()+'?mode=ro', uri=True)
    db.row_factory = sqlite3.Row
    try:
        if db.execute('pragma integrity_check').fetchone()[0]!='ok':raise ValueError('Archive integrity')
        return {table:[dict(r) for r in db.execute('select * from '+table)] for table in TABLES}
    finally:
        db.close()


def build(db_path, span_index):
    tables = load_tables(db_path)
    sections = {s['section_id']:dict(s) for s in tables['sections']}
    for section in sections.values():
        if digest(section['original_text']) != section['sha256']:raise ValueError('Chapter bytes changed')
    by_key = {(s['book_id'],s['section_key']):s for s in sections.values()}
    cases = {c['case_id']:c for c in tables['cases']}
    spans = {int(k):v for k,v in span_index.items()}
    covered_cases = set()
    for sid, entries in spans.items():
        if sid not in sections:raise ValueError('Unknown source chapter')
        for entry in entries:
            if entry['case_id'] not in cases:raise ValueError('Unknown original case')
            lo, hi = entry['lines']
            if not (1<=lo<=hi<=len(sections[sid]['original_text'].splitlines())):
                raise ValueError('Invalid source coordinates')
            covered_cases.add(entry['case_id'])
    if covered_cases != set(cases):raise ValueError('Every original case must retain source coordinates')
    groups = Groups();units={};records=[];seen=set();issues=[]
    for cid in cases:groups.root('case:'+cid)
    for field in ('author_judgment','later_feedback'):
        duplicate = defaultdict(list)
        for cid,case in cases.items():
            if len(case.get(field) or '')>=80:duplicate[clean(case[field])].append('case:'+cid)
        for owners in duplicate.values():groups.join(owners)

    def linked(sid, lines):
        return sorted({e['case_id'] for e in spans.get(sid,[]) if max(lines[0],e['lines'][0])<=min(lines[1],e['lines'][1])})

    def add_unit(section, text, kind, concept='', reported=None, case_id=None):
        lines,status=locate(section,text,reported)
        if lines is None:
            issues.append({'kind':kind,'case_id':case_id,'section':section['section_id'],'issue':'unlocated_original_retained_in_archive'})
            return None
        uid='book:'+str(section['section_id'])+':L'+str(lines[0])+'-'+str(lines[1])+':'+digest(text)[:12]
        cids=sorted(set(linked(section['section_id'],lines)+([case_id] if case_id else [])))
        if uid not in units:
            units[uid]={'id':uid,'book_id':section['book_id'],'chapter':section['title'],
                'section_id':section['section_id'],'source_sha256':section['sha256'],
                'lines':lines,'match_status':status,'original_quote':text,'kind':kind,
                'concept':concept,'case_ids':cids}
        else:
            units[uid]['case_ids']=sorted(set(units[uid]['case_ids']+cids))
        owner='passage:'+digest(clean(text))
        groups.join([owner]+['case:'+cid for cid in cids])
        return units[uid]

    def add(fmt, task, question, answer, source_ids, context=None, dialogue=None, case_id=None, mode='book_knowledge'):
        if not source_ids or not answer.strip():return
        if any(uid not in units for uid in source_ids):raise ValueError('Missing book evidence')
        key=digest(dumps([fmt,task,question,answer,source_ids,context]))
        if key in seen:return
        seen.add(key)
        owners=['passage:'+digest(clean(units[u]['original_quote'])) for u in source_ids]
        if case_id:owners.append('case:'+case_id)
        group=groups.join(owners)
        messages=[{'role':'system','content':SYSTEM}]+(dialogue or [])+[
            {'role':'user','content':question+ ('\n资料：'+dumps(context) if context else '')},
            {'role':'assistant','content':readable(answer)}]
        row={'id':'bookv3:'+key[:24],'format':fmt,'task':task,'question':question,'answer':readable(answer),
             'source_ids':list(dict.fromkeys(source_ids)),'case_id':case_id,'source_mode':mode,
             'context':context,'messages':messages,'group':group,'is_independent_new_case':False,
             'is_source_fidelity_mechanically_checked':True,'semantic_review_complete':False}
        if any(term in dumps(row) for term in FORBIDDEN):raise ValueError('Legacy teacher marker')
        records.append(row)

    # Fresh extraction from the literal semantic source table, never old answers.
    for assertion in tables['semantic_assertions']:
        section=by_key.get(tuple(assertion['chapter_key'].split('/')[:2]))
        if section:
            add_unit(section,assertion['original_excerpt'].strip(),assertion['kind'],assertion['concept_id'],assertion['source_start_line'])
    # Intact paragraphs fill unindexed general material; case prose stays case-scoped.
    indexed=list(units.values())
    for sid,section in sections.items():
        lines=section['original_text'].splitlines();start=None
        for i,line in enumerate(lines+[''],1):
            if line.strip() and start is None:start=i
            if not line.strip() and start is not None:
                lo,hi=start,i-1;text='\n'.join(lines[lo-1:hi]);start=None
                if len(text)<28 or linked(sid,[lo,hi]):continue
                if any(x.lstrip().startswith(('|','+--','┌','├','└')) for x in text.splitlines()):continue
                if any(u['section_id']==sid and u['lines'][0]<=lo and u['lines'][1]>=hi for u in indexed):continue
                if len(text)>12000:continue
                add_unit(section,text,'unindexed_book_paragraph')
    general=[u for u in units.values() if not u['case_ids']]
    condition_ids=set()
    for u in general:
        text=u['original_quote'];topic=subject(u['concept'],text);book=BOOKS[u['book_id']]
        if u['kind'] in BASIC_KINDS or not CONDITIONS.search(text):
            add('foundation_qa','book_concept',f'按{book}，{topic}怎样理解？',text,[u['id']])
        if CONDITIONS.search(text):
            condition_ids.add(u['id'])
            add('conditional_dialogue','book_conditions',f'{book}中{topic}有哪些适用条件、例外或限制？',text,[u['id']])
            first=re.split(r'(?<=[。！？])',text,1)[0]
            history=[{'role':'user','content':f'请先说{book}中{topic}的基本意思。'},
                     {'role':'assistant','content':readable(first)}]
            add('conditional_dialogue','book_condition_followup','把本段的条件和例外也完整补齐，不能只记前一句。',
                text,[u['id']],dialogue=history)
            if re.search(r'兼看|还要|综合|不能|不宜|但是|但|除非',text):
                add('conditional_dialogue','source_grounded_correction',
                    f'如果只记住{book}这条关于{topic}的部分说法，省掉其条件和例外，原文哪些内容能纠正这种理解？',text,[u['id']])
    # Domain workflows use general original passages in their actual book order.
    for sid,section in sections.items():
        methods=[u for u in general if u['section_id']==sid and
                 (u['id'] in condition_ids or re.search('取|用神|代表|预测|判断|应期',u['original_quote']))]
        if not methods or not re.search('预测|判断|应用|要素',section['title']):continue
        methods=sorted(methods,key=lambda x:(x['lines'][0],x['lines'][1]))
        # Full workflow documents stay intact. Overlong ones are not silently truncated.
        answer='\n\n'.join(u['original_quote'] for u in methods)
        add('conditional_dialogue','domain_original_workflow',
            f'{BOOKS[section["book_id"]]}《{section["title"]}》在案例之外明确给出了哪些取用、判断条件和方法？按原文顺序说明。',
            answer,[u['id'] for u in methods])

    cell_rows=[dict(r,cast_key='primary') for r in tables['historical_chart_cells']]+tables['historical_case_additional_cast_cells']
    boards=defaultdict(list)
    for row in cell_rows:boards[(row['case_id'],row['cast_key'])].append(row)
    chart_units={}
    for (cid,cast),cells in boards.items():
        section=sections[cases[cid]['section_id']]
        for cell in sorted(cells,key=lambda x:x['palace']):
            uid='chart:'+cid+':'+cast+':p'+str(cell['palace'])
            units[uid]={'id':uid,'book_id':section['book_id'],'section_id':section['section_id'],
                'chapter':section['title'],'source_sha256':section['sha256'],
                'lines':[cell['source_line'],cell['source_line']],
                'kind':'original_printed_chart_cell','match_status':'sqlite_original_transcription',
                'original_quote':dumps(cell),'case_ids':[cid]}
            groups.join(['passage:'+digest(clean(units[uid]['original_quote'])),'case:'+cid])
            chart_units[(cid,cast,cell['palace'])]=uid
        if len(cells)!=9:continue
        for character in '蓬任冲辅英芮柱心禽':
            selected=[cell for cell in cells if character in (cell['star_position_raw'] or '')]
            if not selected:continue
            response='\n'.join(f'{cell["palace_label_raw"]}（{cell["palace"]}宫）的原星行是“{cell["star_position_raw"]}”。' for cell in selected)
            add('chart_application','printed_star_location',
                f'原案〔{cid}〕这张原抄盘中，哪些宫的原星行出现“{character}”字？按原抄读取。',
                response,[chart_units[(cid,cast,c['palace'])] for c in selected],
                context={'原抄九宫':cells,'原抄状态':'书中原字转录，不能任意猜定天地层'},case_id=cid,mode='literal_chart_reading')

    steps=defaultdict(list);phase_rows=defaultdict(list);disclosures=defaultdict(list)
    for r in tables['historical_case_reasoning']:steps[r['case_id']].append(r)
    for r in tables['historical_case_phase_events']:phase_rows[r['case_id']].append(r)
    for r in tables['historical_case_disclosures']:disclosures[r['case_id']].append(r)
    dossiers=[]
    for cid,case in cases.items():
        section=sections[case['section_id']];authored=[]
        for step in sorted(steps[cid],key=lambda x:x['step_number']):
            text=step['author_analysis_original'];u=add_unit(section,text,'author_original_step',reported=step['source_line'],case_id=cid)
            if u is None:
                matches=[(s,locate(s,text)[0]) for s in sections.values() if locate(s,text)[0]]
                if len(matches)==1:u=add_unit(matches[0][0],text,'author_original_step',case_id=cid)
            if u is None:continue
            authored.append({'step':step['step_number'],'source_id':u['id'],'original':text})
            board=boards.get((cid,'primary'),[])
            part=premise_target(text)
            if part:
                premise,target=part
                add('chart_application','author_inference_completion',
                    f'复盘原案〔{cid}〕第{step["step_number"]}段：作者已经写下这些依据，接着得出了什么判断？',
                    target,[u['id']],context={'原抄九宫':board,'作者已写明依据':premise,
                    '任务范围':'复盘作者此段因果，不是新事件预测'},case_id=cid,mode='author_written_premise_application')
            else:
                add('chart_application','author_evidence_organization',
                    f'复盘原案〔{cid}〕第{step["step_number"]}段：结合原盘说明作者实际使用的依据和判断，不增加原文没有的步骤。',
                    text,[u['id']],context={'原抄九宫':board,'本段原文':text},case_id=cid,mode='source_assisted_case_application')
            if CONDITIONS.search(text):
                add('chart_application','author_case_conditions',
                    f'原案〔{cid}〕第{step["step_number"]}段中，作者怎样把盘面条件、转折或限制带入判断？',
                    text,[u['id']],context={'原抄九宫':board,'原文供核对':text},case_id=cid,mode='source_assisted_case_application')
        initial=[r for r in phase_rows[cid] if r['phase']=='initial_question' and r['visible_to_initial_blind_test']==1]
        judgments=[r for r in phase_rows[cid] if r['phase']=='initial_judgment']
        judgment_parts,judgment_pending=located_pieces(section,case['author_judgment'])
        feedback_parts,feedback_pending=located_pieces(section,case['later_feedback'])
        located_phases=[r for r in phase_rows[cid] if locate(section,r['original_excerpt'])[0]]
        located_disclosures=[r for r in disclosures[cid] if locate(section,r['original_statement'])[0]]
        dossier={'case_id':cid,'original_event_family':case['event_family_id'],'domain':case['domain_id'],
            'primary_printed_chart':boards.get((cid,'primary'),[]),
            'additional_printed_charts':{cast:cells for (key,cast),cells in boards.items() if key==cid and cast!='primary'},
            'author_steps':authored,'author_original_judgment':'\n'.join(judgment_parts),
            'later_feedback_separate':'\n'.join(feedback_parts),'source_phase_events':located_phases,
            'source_disclosures':located_disclosures,'raw_known_before_not_used_as_initial_input':True,
            'unlocated_registry_judgment_fragments_omitted':len(judgment_pending),
            'unlocated_registry_feedback_fragments_omitted':len(feedback_pending)}
        dossiers.append(dossier)
        if authored:
            refs=[s['source_id'] for s in authored]
            final='\n'.join(judgment_parts)
            for part in judgment_parts:
                ju=add_unit(section,part,'author_original_final_judgment',case_id=cid)
                if ju:refs.append(ju['id'])
            answer='\n\n'.join(f'作者第{s["step"]}段分析：\n{s["original"]}' for s in authored)
            if final:answer+='\n\n原书所载断语：\n'+final
            add('complete_case','complete_author_case_lesson',
                f'原案〔{cid}〕：结合完整原盘和原书资料，按作者顺序整理取用、专业分析及已载断语。',
                answer,refs,context={'原抄九宫':boards.get((cid,'primary'),[]),
                '本例实际补盘':dossier['additional_printed_charts'],
                '原书分析资料':authored,'原书断语供核对':final,
                '学习范围':'完整原书教学复盘；不宣称这是隐藏作者分析的新盘盲测'},case_id=cid,mode='complete_source_assisted_author_lesson')
        if initial and judgments and len(boards.get((cid,'primary'),[]))==9:
            refs=[];texts=[]
            for phase in judgments:
                u=add_unit(section,phase['original_excerpt'],'explicit_initial_judgment',reported=phase['source_start_line'],case_id=cid)
                if u:refs.append(u['id']);texts.append(phase['original_excerpt'])
            if refs:
                add('complete_case','explicit_initial_author_response',
                    f'原案〔{cid}〕：根据书中明确标为初问的背景和原盘，复盘作者当时的初断。',
                    '\n\n'.join(texts),refs,context={'原抄九宫':boards[(cid,'primary')],
                    '明确初问背景':[r['original_excerpt'] for r in initial]},case_id=cid,mode='explicit_initial_phase_reconstruction')
    # Finalize connected groups AFTER all shared-source links have been seen.
    for row in records:
        row['group']=groups.root(row['group']);row['split']=split_for(row['group'])
    for dossier in dossiers:
        dossier['group']=groups.root('case:'+dossier['case_id']);dossier['split']=split_for(dossier['group'])
    # Machine checks are limited to exact source/chronology/family consistency.
    owners={}
    for row in records:
        for uid in row['source_ids']:
            if owners.setdefault(uid,row['split'])!=row['split']:raise ValueError('Cross-split source leakage')
        if row['task']=='explicit_initial_author_response':
            payload=row['context']
            if set(payload)!={'原抄九宫','明确初问背景'}:raise ValueError('Later information in initial view')
    return {'records':records,'units':units,'dossiers':dossiers,'tables':tables,'issues':issues,
            'span_index':span_index,'source_sha256':SOURCE_SHA256}


OPENINGS = ('请回答这道题：','请依据原书作答：','请就本题说明：','请按本题资料回答：',
            '围绕这个问题，请作答：','请保留原书含义回答：','请回到本题回答：','请依据所给范围解释：',
            '这道题请这样处理：','请根据本题内容说明：','请按照原文来回答：','就这份资料，请回答：',
            '针对以下问题，请作答：','本题需要你回答：','请依据本题证据说明：','请回应下面的问题：')
FRAMES = ('{q}','关于本题：{q}','本题的问题是：{q}','请考虑以下提问：{q}',
          '我要问的是：{q}','就当前材料提问：{q}','围绕原书这一内容：{q}','具体问题如下：{q}',
          '在本题给定范围内：{q}','本题请说明：{q}','需要回答的问题为：{q}','请回应这一问法：{q}',
          '按所给资料理解：{q}','讨论本题时：{q}','结合当前题目：{q}','请解答：{q}')
CLOSINGS = ('请保留已有条件。','请依据本题给定范围作答。','请不要省略原文例外。','请保持原书含义。',
            '回答请与本题证据一致。','请保留原文的限定。','请按本题信息回答。','请保持人物和领域条件。',
            '请只用有出处的内容回答。','请保留判断的适用范围。','请保持原题的资料边界。','请依照原文条件说明。',
            '请把已知条件保留在回答中。','请不要补造缺失资料。','请按照本题已有依据说明。','请保留原文的转折。')


def wording(question, number):
    capacity=len(OPENINGS)*len(FRAMES)*len(CLOSINGS)
    if not 0<=number<capacity:raise ValueError('Unique wording capacity exceeded; do not silently duplicate')
    a,rem=divmod(number,len(FRAMES)*len(CLOSINGS));b,c=divmod(rem,len(CLOSINGS))
    return OPENINGS[a]+FRAMES[b].format(q=question)+' '+CLOSINGS[c]


def variant_question(row, number):
    """Task-specific rephrasing changes expression, never the chart or premises."""
    task=row['task'];q=row['question'];cid=row.get('case_id') or ''
    templates=[]
    if task=='book_concept':
        m=re.fullmatch(r'按(《.+?》)，(.+)怎样理解？',q)
        if m:
            book,topic=m.groups()
            templates=[f'{book}如何解释{topic}？',f'请说明{book}中{topic}的含义。',
                f'学习{book}时，{topic}应当怎样理解？',f'{book}关于{topic}具体写了什么？',
                f'如果依据{book}作答，怎样说明{topic}？',f'请把{book}对{topic}的解释说清楚。']
    elif task=='book_conditions':
        m=re.fullmatch(r'(《.+?》)中(.+)有哪些适用条件、例外或限制？',q)
        if m:
            book,topic=m.groups()
            templates=[f'使用{book}关于{topic}的说法时，要保留哪些原文限定？',
                f'{book}对{topic}有哪些条件要求？有例外也请保留。',
                f'关于{topic}，{book}原文的前提和限制分别是什么？',
                f'请完整说明{book}关于{topic}的适用范围和已有例外。']
    elif task=='book_condition_followup':
        templates=['刚才讲了基本意思，还需要补上哪些原文条件和例外？',
            '前一句说法之外，本段还有哪些限定不能漏掉？',
            '请把这条规则尚未说明的条件和原文转折完整补充。',
            '如果只记前面的解释，会遗漏原文哪些限制？']
    elif task=='printed_star_location':
        m=re.search(r'原星行出现“(.)”字',q)
        if m:
            ch=m.group(1);templates=[f'原案〔{cid}〕的原星行中，“{ch}”写在哪些宫？',
                f'请在原案〔{cid}〕九宫原抄中找出原星行含“{ch}”的宫位。',
                f'核对原案〔{cid}〕：哪些宫的原星行能看到“{ch}”字？',
                f'根据原案〔{cid}〕的原字记录，请定位原星行中的“{ch}”。']
    elif task=='author_inference_completion':
        m=re.search(r'第(\d+)段',q);step=m.group(1) if m else ''
        templates=[f'原案〔{cid}〕第{step}段已给出这些依据，作者下一步作了什么判断？',
            f'请接续原案〔{cid}〕第{step}段的作者推断，只补书中随后写出的结论。',
            f'在原案〔{cid}〕第{step}段中，这些已写依据之后接的判断是什么？',
            f'依据题面所列的作者原话，复盘原案〔{cid}〕第{step}段随后的判断。']
    elif task=='author_evidence_organization':
        templates=[f'结合原案〔{cid}〕所给九宫与本段原文，作者实际用了哪些依据并怎样判断？',
            f'请按原案〔{cid}〕这一段原话，说明盘面证据与作者判断的联系。',
            f'对照原案〔{cid}〕原盘，整理本段确实写出的分析，不增加额外步骤。']
    elif task=='author_case_conditions':
        templates=[f'原案〔{cid}〕这一段有哪些盘面条件、转折或限制实际参与了作者判断？',
            f'请对照原盘复盘原案〔{cid}〕本段作者如何使用已写条件和限制。',
            f'在原案〔{cid}〕这段分析中，哪些原文限定需要和判断一起保留？']
    elif task=='complete_author_case_lesson':
        templates=[f'请把原案〔{cid}〕的取用、作者分析和已载断语，按原书顺序连起来说明。',
            f'结合原案〔{cid}〕原盘与所给原书资料，完整整理作者的分析及所载结论。',
            f'请依据提供的原书资料，完成原案〔{cid}〕的整案教学复盘。',
            f'复盘原案〔{cid}〕时，作者怎样取用、组织证据，并作出书中所载断语？']
    elif task=='explicit_initial_author_response':
        templates=[f'原案〔{cid}〕明确初问与原盘已给出，作者当时的初断是什么？',
            f'仅以题面初问背景与原盘，复盘原案〔{cid}〕书中记载的最初判断。',
            f'请按原案〔{cid}〕明确的初问阶段，回答作者当时作了什么初断。']
    # Original instruction stays a semantic alternative; no new conditions are inserted.
    templates=[q]+templates
    style,choice=divmod(number,len(templates))
    return wording(templates[choice],style)


def write_gz(path, rows):
    with gzip.open(path,'wt',encoding='utf8',compresslevel=3) as f:
        for row in rows:f.write(dumps(row)+'\n')


def export(pack, destination, pool_size=1000000, materialize=False):
    out=Path(destination);out.mkdir(parents=True,exist_ok=False)
    rows=pack['records'];by_format={fmt:[r for r in rows if r['format']==fmt] for fmt in FORMATS}
    if any(not values for values in by_format.values()):raise ValueError('Every format needs real supported tasks')
    write_gz(out/'core_tasks.jsonl.gz',rows)
    write_gz(out/'source_units.jsonl.gz',pack['units'].values())
    write_gz(out/'all_194_cases.jsonl.gz',pack['dossiers'])
    write_gz(out/'original_43_chapters.jsonl.gz',pack['tables']['sections'])
    (out/'case_source_coordinates.json').write_text(dumps(pack['span_index'])+'\n',encoding='utf8')
    # Multi-turn prefix targets prevent early assistant turns being silently masked.
    turn_count=0
    with gzip.open(out/'assistant_turn_views.jsonl.gz','wt',encoding='utf8',compresslevel=3) as f:
        for row in rows:
            for i,msg in enumerate(row['messages']):
                if msg['role']=='assistant':
                    view={k:row[k] for k in ('group','split','format','source_ids','case_id','source_mode')}
                    view.update(id=row['id']+':turn'+str(i),core_id=row['id'],messages=row['messages'][:i+1])
                    f.write(dumps(view)+'\n');turn_count+=1
    counts=Counter();family_counts=Counter();sha=hashlib.sha256();n=0
    full=gzip.open(out/'million_dialogues.jsonl.gz','wt',encoding='utf8',compresslevel=3) if materialize else None
    split_files={split:gzip.open(out/(split+'_dialogues.jsonl.gz'),'wt',encoding='utf8',compresslevel=3) for split in ('train','validation','test')} if materialize else {}
    try:
        with gzip.open(out/'million_question_pool.csv.gz','wt',encoding='utf-8-sig',newline='',compresslevel=3) as f:
            writer=csv.writer(f);writer.writerow(['candidate_id','format','core_id','question','answer','source_ids','group','split','variant_index','core_weight'])
            for fmt in FORMATS:
                target=QUOTAS[fmt]*pool_size//1000000
                if fmt==FORMATS[-1]:target=pool_size-n
                cores=by_format[fmt];base,extra=divmod(target,len(cores))
                for index,row in enumerate(cores):
                    amount=base+(index<extra)
                    for variant in range(amount):
                        q=variant_question(row,variant);uid=row['id']+':wording'+str(variant)
                        writer.writerow([uid,fmt,row['id'],q,row['answer'],dumps(row['source_ids']),row['group'],row['split'],variant,1/amount])
                        if full:
                            messages=[dict(msg) for msg in row['messages']]
                            original=messages[-2]['content'];suffix=original[len(row['question']):]
                            if not original.startswith(row['question']):raise ValueError('Unexpected user prompt')
                            messages[-2]['content']=q+suffix
                            encoded_row=dumps({'id':uid,'core_id':row['id'],'format':fmt,'group':row['group'],
                                'split':row['split'],'case_id':row['case_id'],'source_ids':row['source_ids'],
                                'source_mode':row['source_mode'],'core_weight':1/amount,'messages':messages,
                                'variant_token_audit_complete':False})+'\n'
                            full.write(encoded_row);split_files[row['split']].write(encoded_row)
                        sha.update((uid+'\n').encode());n+=1;counts[fmt]+=1;family_counts[row['split']]+=1
    finally:
        if full:full.close()
        for stream in split_files.values():stream.close()
    if n!=pool_size:raise ValueError('Pool row mismatch')
    manifest={'schema':VERSION,'source_database_sha256':pack['source_sha256'],
        'source_books':['shenqi','kaiwu'],'source_chapters':len(pack['tables']['sections']),
        'original_cases':len(pack['dossiers']),'original_author_paragraphs':len(pack['tables']['historical_case_reasoning']),
        'author_paragraphs_located':sum(len(d['author_steps']) for d in pack['dossiers']),
        'unlocated_registry_fields_excluded_from_training':True,
        'cases_with_located_judgment_parts':sum(bool(d['author_original_judgment']) for d in pack['dossiers']),
        'source_units':len(pack['units']),'core_tasks':len(rows),'core_formats':{f:len(r) for f,r in by_format.items()},
        'core_tasks_by_type':dict(Counter(r['task'] for r in rows)),
        'core_split_counts':dict(Counter(r['split'] for r in rows)),'candidate_dialogues':n,
        'candidate_formats':dict(counts),'candidate_split_counts':dict(family_counts),
        'candidate_id_sequence_sha256':sha.hexdigest(),'supervised_turn_views':turn_count,
        'materialized_full_dialogues':materialize,'materialized_separate_split_files':materialize,
        'wording_generation':'task_specific_semantic_rephrasing_plus_finite_expression_templates',
        'million_rows_are_not_a_million_distinct_reasoning_tasks':True,
        'old_qa_or_engine_outputs_read':False,
        'source_coordinate_index_contains_only_source_boundaries':True,'non_book_supplements_used':False,
        'legacy_score_teachers_used':False,'old_adapters_allowed':False,'initialization':'official Qwen base only',
        'paraphrases_are_not_independent_cases':True,'variant_weights_sum_to_one_per_core':True,
        'all_variants_same_group_and_split_as_core':True,'natural_chinese_assistant_output':True,
        'semantic_review_complete':False,'all_variants_token_audited':False,'training_started':False,
        'auto_training_enabled':False,'real_world_prediction_validated':False,'issues':pack['issues']}
    manifest['file_sha256']={p.name:digest(p.read_bytes()) for p in out.iterdir() if p.is_file()}
    (out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    return manifest
