"""Read-only, source-located dialogue curriculum. No fabricated author reasoning.

Full source/case records remain intact. Short training views are linked to the
same source/event groups. Source-study, literal chart reading and constructed
lookup exercises are different tasks, never independent observed outcomes.
"""
from __future__ import annotations

from collections import Counter, defaultdict
import csv
import hashlib
import json
from pathlib import Path
import re
import sqlite3

from .qwen_research import ROOT, SOURCE_DB, FOUNDATION_KINDS, digest, json_text, private_path, split_for, write_json

VERSION = 'wengua_dialogue_curriculum_v2'
SOURCE_SHA = '21362e6f0266c03dcdc4a7ef35f45954ba274ae6458de0ba341132abca7d0405'
SYSTEM = '''你是依据所给两书及标明来源的用户补充进行资料学习的问卦助手。
正面回答当前问题，summary写该题具体答案，不写固定的“以下是来源资料”。
保留原文的适用条件、例外和先后披露。案例复盘引用作者原话，不能伪造原作者未写的推理；
书内断语、后来反馈、作者纠错和现实独立验证分开。原抄盘只按记录读取，未知不补造。
资料学习不要求另起新盘；新事件须由可靠程序排盘和明确人物关系后再按领域选用神。
不把学习题、原书断语或用户自定表当成已验证的现实预测；不得编百分比、诊断或寿命。
只输出JSON，mode为source_study，summary为字符串，evidence为含citation和statement的数组，
counter_evidence及missing_information均为字符串数组，没有就填[]；event_probability必须为null。'''

KIND_NAMES = {'symbol': '符号属性', 'symbol_aspect': '符号类象', 'stem_pair': '天盘地盘干组合',
              'door_pair': '门门组合', 'door_stem': '门干组合', 'health_yongshen': '疾病取用',
              'employment_domain_method': '工作取用', 'business_domain_method': '经营求财方法',
              'pregnancy_method': '孕产取用', 'heavenly_stem_twelve_state': '天干十二长生',
              'conditional_formation_rule': '有前提的格局', 'marriage_method': '婚恋取用'}
FACETS = {'element': '五行', 'direction': '后天方位', 'palace': '宫数', 'stage': '十二长生状态',
          'branch': '地支', 'stem': '天干', 'heaven_stem': '天盘干', 'earth_stem': '地盘干',
          'traditional_month': '传统月份', 'solar_terms': '节气', 'number': '数', 'door': '门', 'star': '星'}
SPANS = ('source_span', 'source_lines', 'line_range', 'source_range', 'whole_story_lines',
         'source_whole_story_lines', 'source_original_span', 'source_original_OCR_raw_lines',
         'original_span', 'original_chapter_source_span', 'whole_original_story_line_span',
         'original_source_span', 'whole_original_story_lines', 'case_lines', 'source_event_span',
         'source_case_span', 'span', 'source')


def strip_number(text):
    return re.sub(r'^\s*(?:[（(]\d+[)）]|\d+[、.．])\s*', '', text).strip()


def sentences(text):
    """Complete sentence/paragraph units; never split a conditional at a comma."""
    return [s.strip() for s in re.findall(r'.+?(?:[。！？](?:[”’"])?|\n+|$)', text, flags=re.S) if s.strip()]


def specific_summary(text, *, last=False):
    pieces = [s for s in sentences(strip_number(text)) if substantive(s)]
    return (pieces[-1] if last else pieces[0]) if pieces else text.strip()


def substantive(text):
    """Exclude navigation-only captions, not unfamiliar traditional claims."""
    clean=text.strip()
    navigation=(len(clean)<35 and '图' in clean and
                not re.sub(r'[参见图示表页及如上如下\d\s（）()，,。.:：\-—]+','',clean))
    return len(clean)>=9 and not navigation


def explicit_qualifiers(text):
    return [s for s in sentences(text) if any(x in s for x in
            ('若','如果','但是','但','虽然','除非','须','必须','不宜','相反','还要','兼看',
             '如遇','如逢','如临','如无','如有','否则','只有','只要'))]


def qualified_summary(base, text):
    """A concise first/last sentence must not erase a later explicit exception."""
    extra=[s for s in explicit_qualifiers(text) if s not in base]
    return base+('\n本段同时限定：'+'\n'.join(extra) if extra else '')


def source_position(section, text, reported=None):
    """Resolve original coordinates without modifying archive or quoted wording."""
    original = section['original_text']
    found, start = [], 0
    while text and (at := original.find(text, start)) >= 0:
        found.append(at); start = at + max(1, len(text))
    if found:
        candidates = [(original.count('\n', 0, p) + 1,
                       original.count('\n', 0, p + len(text)) + 1) for p in found]
        if reported and any(a <= reported[0] <= b for a, b in candidates):
            chosen = next((a, b) for a, b in candidates if a <= reported[0] <= b)
        else:
            chosen = candidates[0]
        return {'status': 'literal_unique' if len(found) == 1 else 'literal_repeated',
                'lines': list(chosen), 'reported_lines': reported, 'occurrences': len(found),
                'reported_start_matches': not reported or chosen[0] == reported[0]}
    # Match OCR whitespace only, preserving a map to the exact original lines.
    clean, offsets = [], []
    for i, char in enumerate(original):
        if not char.isspace(): clean.append(char); offsets.append(i)
    needle = re.sub(r'\s+', '', text)
    at = ''.join(clean).find(needle) if needle else -1
    if at >= 0:
        lo, hi = offsets[at], offsets[at + len(needle) - 1] + 1
        return {'status': 'whitespace_normalized_only', 'lines': [original.count('\n', 0, lo)+1,
                 original.count('\n', 0, hi)+1], 'reported_lines': reported,
                'normalization': 'matching_copy_only_original_unchanged'}
    return {'status': 'abstract_or_unlocated', 'lines': None, 'reported_lines': reported}


def _span(record):
    for a, b in [('begin', 'end'), ('source_start', 'source_end'), ('source_start_line', 'source_end_line')]:
        if type(record.get(a)) is int and type(record.get(b)) is int:
            return [record[a], record[b]]
    for key in SPANS:
        value = record.get(key)
        if isinstance(value, list) and len(value) == 2 and all(type(x) is int for x in value) and value[0] <= value[1]:
            return value
    return None


def walk(value):
    if isinstance(value, dict):
        yield value
        for child in value.values(): yield from walk(child)
    elif isinstance(value, list):
        for child in value: yield from walk(child)


def case_spans(sections, cases, protocols):
    """Include explicit cross-book reprints under their existing case identity."""
    by_sha = {s['sha256']: s for s in sections.values()}
    result, titles = defaultdict(list), {}
    for case in cases.values():
        metadata = json.loads(protocols[case['case_id']]['metadata_json'])
        span = _span(metadata)
        if span:
            result[case['section_id']].append({'case_id': case['case_id'], 'lines': span, 'source': 'protocol'})
        for span in metadata.get('event_source_ranges', []):
            if isinstance(span,list) and len(span)==2 and all(type(v) is int for v in span):
                result[case['section_id']].append({'case_id':case['case_id'],'lines':span,'source':'protocol_explicit_multiple_ranges'})
    for path in sorted((ROOT / 'data/knowledge').glob('*/**/case_index.json')):
        data = json.loads(path.read_text(encoding='utf8'))
        sha = next((data[k] for k in ('source_sha256','file_source_sha256') if data.get(k) in by_sha), None)
        section = by_sha.get(sha)
        if section is None: continue
        for record in walk(data):
            cid = record.get('case_id', record.get('id', record.get('event_family_id')))
            if cid not in cases and isinstance(cid,str):
                matches=[k for k,c in cases.items() if c['section_id']==section['section_id'] and k.endswith('.'+cid)]
                cid=matches[0] if len(matches)==1 else cid
            if cid not in cases: continue
            span = _span(record)
            if span:
                result[section['section_id']].append({'case_id': cid, 'lines': span,
                    'source': str(path.relative_to(ROOT)), 'source_sha256': sha})
            if record.get('title'): titles.setdefault(cid, record['title'])
    return dict(result), titles


def linked_cases(section_id, lines, spans):
    if not lines: return []
    return sorted({r['case_id'] for r in spans.get(section_id, [])
                   if max(lines[0], r['lines'][0]) <= min(lines[1], r['lines'][1])})


def _book(section):
    return '《神奇之门》' if section['book_id'] == 'shenqi' else '《开悟之门》'


def _label(row, normalized):
    cid = row['concept_id']
    if normalized.get('stem') and normalized.get('stage'):
        return f"{normalized['stem']}干的{normalized['stage']}"
    if cid.startswith('trigram:'): return cid.split(':')[1] + '卦'
    if cid.startswith('stem:'): return cid.split(':')[1] + '干'
    if cid.startswith('door_over_stem:'):
        p=cid.split(':');return p[-2]+'门加'+p[-1]+'干'
    if cid.startswith('door_over_door:'):
        p=cid.split(':');return p[-2]+'门加'+p[-1]+'门'
    if cid.startswith(('star:', 'door:', 'deity:', 'branch:')): return cid.split(':')[1]
    if normalized.get('heaven_stem') and normalized.get('earth_stem'):
        return f"天盘{normalized['heaven_stem']}加地盘{normalized['earth_stem']}"
    if cid.startswith('heaven_over_earth:'):
        p = cid.split(':'); return '天盘' + p[-2] + '加地盘' + p[-1]
    role_labels = {'illness_star':'天芮星的疾病取用', 'doctor_star':'天心星的医药取用',
                   'medicine_yi':'乙奇的医药取用', 'father':'本例父亲的取用', 'self':'本例本人取用'}
    if cid.startswith('health:role:') and cid.split(':')[-1] in role_labels:
        return role_labels[cid.split(':')[-1]]
    for key in ('public_method_index','summary','source_summary','conditional_summary','topic'):
        value=normalized.get(key)
        if isinstance(value,str) and value and len(value)<=80:return value
    return KIND_NAMES.get(row['kind'], '本段规则')


def _answer(text, citation, quote, *, counter=(), missing=()):
    return {'mode': 'source_study', 'summary': text, 'evidence': [{'citation': citation, 'statement': quote}],
            'counter_evidence': list(counter), 'missing_information': list(missing), 'event_probability': None}


def fact_supported(key, value, normalized, text):
    """Fail closed on metadata values absent from their own literal source."""
    if key in ('stage','branch') and normalized.get('stem') and normalized.get('stage') and normalized.get('branch'):
        stage,branch=normalized['stage'],normalized['branch']
        clean=re.sub(r'\s+','',text)
        return any(p in clean for p in (stage+'在'+branch,stage+'于'+branch,stage+'：'+branch,stage+':'+branch))
    values=value if isinstance(value,list) else [value]
    nums={1:'一',2:'二',3:'三',4:'四',5:'五',6:'六',7:'七',8:'八',9:'九',10:'十',11:'十一',12:'十二'}
    return all(str(v) in text or (type(v) is int and nums.get(v,'__none__') in text) for v in values)


def _card(uid, task, question, answer, group, source_ids, *, context=None, dialogue=None, stage='knowledge'):
    user = question + ('\n' + json_text(context) if context else '')
    messages = [{'role':'system','content':SYSTEM}]
    if dialogue:
        for turn in dialogue:
            turn=dict(turn)
            if turn['role']=='assistant':
                try:previous=json.loads(turn['content'])
                except (ValueError,TypeError):previous={'summary':turn['content']}
                if not isinstance(previous,dict):raise ValueError('Prior assistant turn must be a clarification or JSON object')
                previous={k:v for k,v in previous.items() if k!='prior_source'}
                turn['content']=json_text({'mode':'source_study','evidence':[],'counter_evidence':[],
                    'missing_information':[],'event_probability':None,**previous})
            messages.append(turn)
    messages += [{'role':'user','content':user},{'role':'assistant','content':json_text(answer)}]
    return {'id':uid,'task':task,'curriculum_stage':stage,'mode':'source_study','group':group,
            'split':split_for(group),'source_ids':source_ids,'eligible_forecast_supervision':False,
            'messages':messages}


def _read_tables(db):
    tables = ['sections','cases','historical_case_protocol','semantic_assertions','historical_case_reasoning',
              'historical_chart_cells','historical_case_additional_casts','historical_case_additional_cast_cells',
              'historical_case_disclosures','historical_case_phase_events','historical_case_book_verdicts']
    return {name:[dict(r) for r in db.execute('SELECT * FROM ' + name)] for name in tables}


def build_curriculum(db_path=SOURCE_DB):
    path = Path(db_path).resolve()
    if digest(path.read_bytes()) != SOURCE_SHA:
        raise ValueError('Unexpected source archive; do not silently rebuild the historical database')
    db = sqlite3.connect(path.as_uri()+'?mode=ro',uri=True); db.row_factory=sqlite3.Row
    try:
        if db.execute('PRAGMA integrity_check').fetchone()[0] != 'ok': raise ValueError('Archive integrity failure')
        tables = _read_tables(db)
        inventory={r[0]:db.execute('SELECT COUNT(*) FROM "'+r[0]+'"').fetchone()[0]
                   for r in db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'").fetchall()}
    finally: db.close()
    sections = {r['section_id']:r for r in tables['sections']}
    by_key = {(r['book_id'],r['section_key']):r for r in sections.values()}
    for s in sections.values():
        if digest(s['original_text']) != s['sha256']: raise ValueError('Original chapter changed')
    cases = {r['case_id']:r for r in tables['cases']}
    case_sections={r['section_id'] for r in cases.values()}
    protocols = {r['case_id']:r for r in tables['historical_case_protocol']}
    spans, titles = case_spans(sections, cases, protocols)
    units, cards, issues, coverage = [], [], [], Counter()
    reasoning = defaultdict(list)
    for r in tables['historical_case_reasoning']: reasoning[r['case_id']].append(r)
    for steps in reasoning.values(): steps.sort(key=lambda r:r['step_number'])
    main_cells=defaultdict(list)
    for row in tables['historical_chart_cells']:main_cells[row['case_id']].append(row)
    disclosures=defaultdict(list)
    for row in tables['historical_case_disclosures']:disclosures[row['case_id']].append(row)
    # Event records, all original texts and phase records are archived separately.
    # We do not overwrite original event IDs when conservative evidence groups merge.
    parent = {cid:cid for cid in cases}

    def find(cid):
        while parent[cid]!=cid:
            parent[cid]=parent[parent[cid]];cid=parent[cid]
        return cid

    def union(ids):
        if ids:
            root=min(find(cid) for cid in ids)
            for cid in ids:parent[find(cid)]=root

    # Shared exact verdict paragraphs can describe several people in one source
    # exchange. Preserve each case but prevent evidence crossing split boundaries.
    shared=defaultdict(set)
    for cid,c in cases.items():
        for key in ('author_judgment','later_feedback'):
            if len(c[key] or '')>80:shared[digest(c[key])].add(cid)
    for ids in shared.values():union(sorted(ids))

    # Locate every assertion. Context-linked rows inherit event grouping; only
    # safely general passages are taught as general knowledge.
    for row in tables['semantic_assertions']:
        section=by_key.get(tuple(row['chapter_key'].split('/')[:2]))
        text=row['original_excerpt'].strip()
        if section is None or not text:
            issues.append({'id':row['concept_id'],'issue':'missing_source_or_empty_excerpt'});continue
        anchor=source_position(section,text,[row['source_start_line'],row['source_end_line']])
        coverage[anchor['status']]+=1
        if anchor.get('reported_start_matches') is False:
            issues.append({'id':row['concept_id'],'issue':'derived_locator_differs_original_preserved','anchor':anchor})
        linked=linked_cases(section['section_id'],anchor['lines'],spans)
        meta=json.loads(row['metadata_json']); explicit=meta.get('source_case_id')
        if explicit in cases:linked=sorted(set(linked+[explicit]))
        if len(linked)>1:union(linked)
        uid='assert:'+digest(row['chapter_key']+row['concept_id']+str(row['source_start_line']))
        unit={'id':uid,'kind':row['kind'],'concept_id':row['concept_id'],'text':text,
              'book_id':section['book_id'],'section_id':section['section_id'],'section_title':section['title'],
              'source_sha256':section['sha256'],'anchor':anchor,'linked_cases':linked,
              'review_status':row['review_status'],'metadata':meta,
              'v1_passage_split':split_for('passage:'+digest(text))
                    if row['kind'] in FOUNDATION_KINDS and section['section_id'] not in case_sections else None}
        units.append(unit)
        if anchor['status']=='abstract_or_unlocated':
            issues.append({'id':uid,'issue':'retain_abstract_not_verbatim_quote'});continue
        normalized=meta.get('normalized',meta.get('predicate',{}))
        if not isinstance(normalized,dict):normalized={}
        subject=_label(row,normalized)
        if subject=='本段规则':
            for key in ('summary','source_summary','conditional_summary','topic'):
                value=meta.get(key)
                if isinstance(value,str) and re.search('[\u4e00-\u9fff]',value) and len(value)<=80:
                    subject=value;break
        group=linked[0] if linked else 'passage:'+digest(text)
        stage='workflow' if linked else 'knowledge'
        context={'book':_book(section),'chapter':section['title'],'source':uid,
                 'scope':'本案书内复盘，不能直接推广为无条件通则' if linked else '按本书本段的条件解释',
                 'source_excerpt':text}
        first,last=specific_summary(text),specific_summary(text,last=True)
        qualified_first,qualified_last=qualified_summary(first,text),qualified_summary(last,text)
        meaning_question=(f"{_book(section)}本例开篇明确说了什么事实或判断？请只复盘原文。" if linked else
                          f"{_book(section)}这一段怎样解释{subject}？请直接说明。")
        if substantive(first):
            cards.append(_card(uid+':meaning','source_meaning',meaning_question,
                     _answer(qualified_first,uid,text if qualified_first!=first else first),group,[uid],context=context,stage=stage))
        else:issues.append({'id':uid,'issue':'navigation_or_short_fragment_not_answer_gold'})
        if last!=first and substantive(last):
            cards.append(_card(uid+':conclusion','source_conclusion',f"这一段最后明确给了什么判断或限制？请保留其适用范围。",
                    _answer(qualified_last,uid,text if qualified_last!=last else last),group,[uid],context=context,stage=stage))
        # Concrete field lookup questions are grounded in existing normalized
        # source facts, never arbitrary new expert conclusions.
        for key in FACETS:
            value=normalized.get(key)
            if value is None or isinstance(value,(dict,bool)):continue
            if not isinstance(value,(str,int,float,list)):continue
            value_text='、'.join(map(str,value)) if isinstance(value,list) else str(value)
            if not value_text or len(value_text)>120:continue
            if not fact_supported(key,value,normalized,text):
                issues.append({'id':uid,'issue':'normalized_field_not_literally_supported_for_lookup','field':key})
                continue
            label=subject
            if key=='stage' and normalized.get('stem') and normalized.get('branch'):
                label=f"{normalized['stem']}干在{normalized['branch']}支"
            if key=='branch' and normalized.get('stem') and normalized.get('stage'):
                label=f"{normalized['stem']}干的{normalized['stage']}"
            answer=f"按本段记录，{label}的{FACETS[key]}是{value_text}。"
            cards.append(_card(uid+':field:'+key,'source_fact_lookup',
                 f"按{_book(section)}，{label}对应的{FACETS[key]}是什么？",
                 _answer(answer,uid,text),group,[uid],context={'source':uid,'scope':context['scope'],
                            **({'source_excerpt':text} if subject=='本段规则' else {})},stage=stage))
        qualifiers=explicit_qualifiers(text)
        if qualifiers:
            quote='\n'.join(qualifiers)
            cards.append(_card(uid+':conditions','source_conditions',
                '这段解释中明确写了哪些前提、转折或限制？请只列原文已有的条件。',
                _answer(quote,uid,text),group,[uid],context=context,stage=stage))

    # The semantic_assertions table does not index two existing foundation
    # chapters. Read their intact blank-line paragraphs from the pinned archive
    # instead of falsely reporting that a table export covered all chapters.
    # The satellite anecdote and its later callback are retained in the full
    # archive, not promoted into an unregistered independent forecast case.
    for sid in (1,4):
        section=sections[sid];lines=section['original_text'].splitlines();blocks=[];start=None
        for i,line in enumerate(lines+[''],1):
            if line.strip() and start is None:start=i
            if not line.strip() and start is not None:
                blocks.append((start,i-1,'\n'.join(lines[start-1:i-1])));start=None
        heading=section['title']
        for lo,hi,text in blocks:
            if len(text)<35 and not any(c in text for c in '。；，'):
                if len(text)>3:heading=text
                continue
            if sid==4 and (max(lo,32)<=min(hi,38) or lo<=122<=hi):
                issues.append({'section_id':sid,'lines':[lo,hi],'issue':'unregistered_source_anecdote_archived_not_forecast_gold'})
                continue
            if len(text)<25 or text.startswith(('图','（所提供','+--','|')):continue
            uid=f'assert:chapter:{sid}:L{lo}-{hi}'
            units.append({'id':uid,'kind':'source_chapter_paragraph','concept_id':f'chapter:{sid}:paragraph:{lo}',
                 'text':text,'book_id':section['book_id'],'section_id':sid,'section_title':section['title'],
                 'source_sha256':section['sha256'],'anchor':source_position(section,text,[lo,hi]),
                 'linked_cases':[],'review_status':'literal_source_checked_not_prediction_validated',
                 'metadata':{'heading':heading,'source_scope':'book_traditional_method_or_didactic_example'}})
            group='passage:'+digest(text)
            context={'book':_book(section),'chapter':section['title'],'heading':heading,
                     'source':uid,'source_excerpt':text,'scope':'本书方法和教学例解；不是现实独立验证'}
            cards.append(_card(uid+':method','source_chapter_method',
                   f"{_book(section)}『{heading}』这一完整段落，具体说明了什么方法或条件？",
                   _answer(qualified_summary(specific_summary(text),text),uid,text),group,[uid],context=context))

    # Original numbered/method paragraphs are intact teacher units. Long whole
    # stories become linked stage dialogues, not artificially independent cases.
    for cid,steps in reasoning.items():
        case=cases[cid];section=sections[case['section_id']]
        previous=None
        for r in steps:
            text=r['author_analysis_original'];anchor=source_position(section,text,[r['source_line'],r['source_line']])
            if anchor['status']=='abstract_or_unlocated':
                matches=[]
                for s in sections.values():
                    a=source_position(s,text)
                    if a['status']!='abstract_or_unlocated':matches.append((s,a))
                if len(matches)==1:section,anchor=matches[0]
                else:issues.append({'case_id':cid,'step':r['step_number'],'issue':'author_quote_location_unresolved'})
            linked=linked_cases(section['section_id'],anchor['lines'],spans)
            union(sorted(set([cid]+linked)))
            uid=f"author:{cid}:step:{r['step_number']}"
            units.append({'id':uid,'kind':'author_explicit_paragraph','text':text,'case_id':cid,
                          'book_id':section['book_id'],'section_id':section['section_id'],
                          'source_sha256':section['sha256'],'anchor':anchor,'linked_cases':[cid],
                          'topic':r['short_method_topic'],'original_step_number':r['step_number'],
                          'chronology':'source_reconstruction_may_include_retrospective_reasoning'})
            context={'case_id':cid,'domain':case['domain_id'],'case_title':titles.get(cid,cid),
                     'author_topic':r['short_method_topic'],'source':uid,
                     'scope':'复盘作者这段原文；不将后来反馈冒充首问已知',
                     'source_cells':{c['palace']:[c['deity_raw'],c['door_position_raw'],c['star_position_raw']]
                                     for c in main_cells.get(cid,[])},
                     'source_columns':['原神行','原门行','原星行；不默认天地层'],
                     'source_disclosures_in_written_order':[{'line':d['source_line'],'phase':d['phase'],
                           'text':d['original_statement']} for d in disclosures.get(cid,[]) if d['source_line']<r['source_line']]}
            topic=r['short_method_topic'] or '本阶段证据和判断'
            cards.append(_card(uid+':analysis','author_stage',f"在此书内案例中，作者如何分析『{topic}』？",
                       _answer(specific_summary(text,last=True),uid,text),cid,[uid],context=context,stage='workflow'))
            if previous:
                dialogue=[{'role':'user','content':f"我们复盘{titles.get(cid,cid)}。作者前一阶段怎么分析？"},
                          {'role':'assistant','content':json_text({'mode':'source_study',
                                'summary':specific_summary(previous['author_analysis_original'],last=True),
                                'prior_source':f"author:{cid}:step:{previous['step_number']}"})}]
                cards.append(_card(uid+':dialogue','author_stage_dialogue',f"接着作者怎样处理『{topic}』？请保留原文因果与例外。",
                         _answer(specific_summary(text,last=True),uid,text),cid,[uid],context=context,dialogue=dialogue,stage='workflow'))
            for marker in ('综合这些信息','所以断','故断','因此断','由此断'):
                if marker in text:
                    at=text.index(marker)
                    if at>15 and len(text[at:])>5:
                        cards.append(_card(uid+':link','author_explicit_condition_link',
                             '根据作者已经写出的这些依据，他接着作了什么判断？',
                             _answer(text[at:],uid,text),cid,[uid],
                             context=dict(context,author_written_premises=text[:at]),stage='workflow'))
                    break
            previous=r

    # Small manually phrased seed set makes the intended conversational task
    # explicit. Teacher answers are intact matching source paragraphs, not
    # synthetic new rules. Other method cards cover the complete registry.
    seed_file=ROOT/'data/knowledge/qwen_curriculum_v2/domain_dialogue_seeds.json'
    seed_data=json.loads(seed_file.read_text(encoding='utf8'))
    for seed in seed_data['seeds']:
        candidates=[u for u in units if u.get('concept_id')==seed['concept'] and
                    not u.get('linked_cases') and seed['match'] in u['text'] and
                    u.get('anchor',{}).get('status')!='abstract_or_unlocated']
        if not candidates:raise ValueError('Domain seed lacks literal general source: '+seed['id'])
        source=candidates[0];uid=source['id'];text=source['text']
        dialogue=[{'role':'user','content':seed['initial']},
                  {'role':'assistant','content':seed['clarify']}] if seed.get('initial') else None
        cards.append(_card('domain:'+seed['id'],'domain_role_dialogue' if dialogue else 'domain_specific_question',
            seed['question'],_answer(strip_number(text),uid,text),'passage:'+digest(text),[uid],
            dialogue=dialogue,context={'book':source['book_id'],'chapter':source['section_title'],
                    'scope':'本书本方法的明确情境；不能无条件跨领域套用','source':uid},stage='workflow'))
        if dialogue:
            # Last-turn masking does not supervise an earlier assistant turn.
            # Teach the clarification itself too, attributed to this curriculum
            # design rather than fabricated as an original author utterance.
            guidance='teaching-clarification:'+seed['id']
            units.append({'id':guidance,'kind':'curated_teaching_clarification','text':seed['clarify'],
                'file':str(seed_file.relative_to(ROOT)),'file_sha256':digest(seed_file.read_bytes()),
                'source_record':seed,'linked_cases':[],
                'provenance':'curriculum_clarification_design_not_original_author_quote'})
            cards.append(_card('domain:'+seed['id']+':initial','domain_initial_clarification',
                seed['initial'],_answer(seed['clarify'],guidance,seed['clarify'],
                    missing=['尚需明确所问的具体情境和采用的方法']),group='passage:'+digest(text),source_ids=[guidance],
                context={'scope':'课程设计的追问示范，不冒充原作者原话'},stage='workflow'))

    # Read only literal rows, with source row/column labels. No guessed heaven/
    # earth convention, no recasting damaged source diagrams.
    cells=[dict(r,cast_key='primary') for r in tables['historical_chart_cells']]
    cells += [dict(r) for r in tables['historical_case_additional_cast_cells']]
    boards=defaultdict(list)
    for r in cells:boards[(r['case_id'],r['cast_key'])].append(r)
    for (cid,cast),rows in boards.items():
        board={r['palace']:[r['deity_raw'],r['door_position_raw'],r['star_position_raw']] for r in rows}
        for r in rows:
            uid=f"chart:{cid}:{cast}:p{r['palace']}:L{r['source_line']}"
            literal={'原神行':r['deity_raw'],'原门行':r['door_position_raw'],'原星行':r['star_position_raw']}
            quote=json_text({'palace':r['palace'],**literal})
            units.append({'id':uid,'kind':'literal_source_chart_cell','text':quote,'case_id':cid,
                          'linked_cases':[cid],'cast_key':cast,'original_source_line':r['source_line'],
                          'status':'original_transcription_not_independent_chart_validation'})
            context={'case_id':cid,'cast_key':cast,'原抄盘三行顺序':['神行','门行','星行'],
                     'source_cells':board,'scope':'只读取原抄格；门行/星行不能默认成天盘/地盘'}
            for key,value in literal.items():
                answer=f"本原抄格的{key}记录为：{value}。" if value else f"本原抄格未记录{key}，不能补造。"
                cards.append(_card(uid+':'+key,'source_chart_cell',f"这张原抄盘第{r['palace']}宫的{key}写了什么？",
                    _answer(answer,uid,quote,missing=[] if value else ['原抄本此栏未记载']),cid,[uid],context=context,stage='chart'))
            combined='；'.join(f"{k}：{v if v else '原抄未记载'}" for k,v in literal.items())+'。'
            cards.append(_card(uid+':row','source_chart_row',f"请核对本原抄盘第{r['palace']}宫的三行记录，区分原字与未记录。",
                         _answer(combined,uid,quote),cid,[uid],context=context,stage='chart'))

    # User additions are explicitly attributed to their own versioned source.
    # Do not automatically train every obsolete template/revision in the repo.
    supplements=['data/knowledge/timing_methods/user_notes_20261102/rules.json',
                 'data/knowledge/phrase_library/health_v30/user_20261022_disease_curriculum.json',
                 'data/knowledge/phrase_library/health_v20/actor_profiles.json']
    for name in supplements:
        data=json.loads((ROOT/name).read_text(encoding='utf8'))
        records=data.get('rules',data.get('profiles',[]))
        if not records:
            records=[{'id':f'{k}:{i}','summary':text} for k,v in data.items() if isinstance(v,list)
                     for i,text in enumerate(v) if isinstance(text,str)]
        for i,r in enumerate(records):
            text=r.get('summary',r.get('note',''))
            if not text:continue
            uid='user:'+digest(name+str(r.get('id',i)))
            unit={'id':uid,'kind':'user_supplement','text':text,'file':name,
                  'file_sha256':digest((ROOT/name).read_bytes()),'source_record':r,
                  'provenance':'user_supplied_or_project_rule_not_original_book_quote','linked_cases':[]}
            units.append(unit)
            group='user-source:'+digest(name+text)
            context={'source':uid,'source_type':'用户补充/项目规则，非古籍原话','record':r}
            context['version_scope']='仅此具名版本；旧草稿不自动等于当前运行规则'
            label=r.get('title',r.get('label','这条补充'))
            cards.append(_card(uid+':meaning','user_rule',f"按这版用户补充，{label}的具体说明是什么？",
                         _answer(text,uid,text),group,[uid],context=context,stage='workflow'))
            limits=r.get('limits',[])
            if limits:
                cards.append(_card(uid+':limits','user_rule_conditions',f"使用{label}时有哪些明示限制？",
                    _answer('；'.join(limits),uid,json_text(r),counter=limits),group,[uid],context=context,stage='workflow'))

    # Dialogue role clarifications use the frozen, versioned actor profile;
    # event-news and direct-proxy are intentionally separate situations.
    actor_file='data/knowledge/phrase_library/health_v20/actor_profiles.json'
    actors=json.loads((ROOT/actor_file).read_text(encoding='utf8'))
    father=next(p for p in actors['profiles'] if p['id']=='father')
    actor_uid='user:'+digest(actor_file+'father')
    group='user-source:'+digest(actor_file+father['note'])
    cards.append(_card(actor_uid+':clarify','role_clarification_dialogue',
        '是我直接代父亲问病，没有提供他的出生年份。现在按这版关系规则怎样取用？',
        _answer('按这版人物关系规则，长辈参考年干，父亲另参乾六宫；出生年命有则兼看，未提供时不虚构。',actor_uid,father['note']),
        group,[actor_uid],dialogue=[{'role':'user','content':'爸爸看病，用神是什么？'},
          {'role':'assistant','content':'先明确是父亲本人问、你直接代问，还是按闻讯的事件时刻起局；另说明有无出生年命。不同情境不能混用。'}],
        context={'consultation_context':'direct_proxy','source_profile':actor_file},stage='workflow'))
    override=actors['event_news_override']
    override_uid='user:'+digest(actor_file+'event_news_override')
    units.append({'id':override_uid,'kind':'user_context_override','text':json_text(override),
                  'file':actor_file,'file_sha256':digest((ROOT/actor_file).read_bytes()),
                  'source_record':override,'linked_cases':[],'provenance':'versioned_project_rule_not_book_quote'})
    clarification=_answer('先明确是父亲本人自问、你直接代问，还是闻讯后按事件时刻起局；出生年命有真实信息再提供。情境未明确时不直接混套年干、年命或辅助宫。',
                    actor_uid,father['note'],missing=['起局情境','真实出生年命如有'])
    clarification['evidence'].append({'citation':override_uid,'statement':json_text(override)})
    cards.append(_card(actor_uid+':initial','domain_initial_clarification','爸爸看病，用神是什么？',
                clarification,group,[actor_uid,override_uid],stage='workflow',
                context={'scope':'按具名人物规则先问清起局情境；追问为课程示范'}))
    cards.append(_card(actor_uid+':event-news','role_context_switch',
        '如果明确改成闻讯后按事件时刻占父亲病情，还能不加区分地套上一条取用吗？',
        _answer('不能混用情境。此版本明确的闻讯占事覆盖规则以日干代表事件病人；这不是父病一律日干。',override_uid,json_text(override)),
        group,[override_uid],context={'source_profile':actor_file,'profile_rule':override},stage='workflow'))
    # The supplied timing notes themselves contain explicit qualifications;
    # retain their competing contexts instead of silently choosing one.
    qualification_file=ROOT/'data/knowledge/timing_methods/user_notes_20261102/exceptions_and_duplicates.json'
    qualifications=json.loads(qualification_file.read_text(encoding='utf8'))
    for record in qualifications.get('conflicts',[]):
        uid='user-qualification:'+record['id']
        text=record.get('detail','')
        if not text:continue
        units.append({'id':uid,'kind':'user_explicit_qualification','text':text,'source_record':record,
                      'file':str(qualification_file.relative_to(ROOT)),'linked_cases':[]})
        cards.append(_card(uid,'user_qualification',f"用户资料里『{record['title']}』为什么要保留情境分别处理？",
            _answer(text,uid,json_text(record),counter=[text]),'user-qualification:'+digest(json_text(record)),[uid],
            context={'source_type':'用户补充中已有的分歧记录，不能伪称原书统一定论','record':record},stage='workflow'))

    # Conservative evidence components never move an old held-out case into
    # training. Shared source passages inherit the most restrictive old split.
    text_case_ids=defaultdict(set)
    for unit in units:
        if len(unit['text'])>=80:
            text_case_ids[digest(unit['text'])].update(unit.get('linked_cases',[]))
    for ids in text_case_ids.values():union(sorted(ids))
    components=defaultdict(list)
    for cid in cases:components[find(cid)].append(cid)
    rank={'train':0,'validation':1,'test':2}
    component_split={root:max((split_for(cases[cid]['event_family_id']) for cid in ids),key=rank.get)
                     for root,ids in components.items()}
    unit_map={u['id']:u for u in units}
    for unit in units:
        ids=text_case_ids.get(digest(unit['text']),set())
        if ids and unit.get('v1_passage_split'):
            root=find(next(iter(ids)))
            component_split[root]=max([component_split[root],unit['v1_passage_split']],key=rank.get)
    for card in cards:
        group=card['group']
        if group not in cases:
            ids=set()
            for uid in card['source_ids']:
                unit=unit_map.get(uid)
                if unit:ids.update(text_case_ids.get(digest(unit['text']),set()))
            if ids:group=min(ids)
        if group in cases:
            card['original_event_id']=group;card['group']='event-component:'+find(group)
            card['split']=component_split[find(group)]
    seen, unique=[],set()
    for card in cards:
        if card['task'] in ('source_meaning','source_conclusion','source_conditions'):
            # A paragraph indexed under 26 concepts is still one reading
            # exercise. Concrete per-concept lookup questions remain separate.
            unit=unit_map[card['source_ids'][0]]
            key=digest(json_text([card['task'],card['group'],unit['book_id'],unit['text']]))
        else:key=digest(json_text(card['messages']))
        if key in unique:continue
        unique.add(key);seen.append(card)
    cards=seen
    registry=[dict(case_id=cid,event_family_id=c['event_family_id'],domain=c['domain_id'],
                   evidence_component=find(cid),split=component_split[find(cid)],
                   title=titles.get(cid),reasoning_steps=len(reasoning.get(cid,[])),
                   original_fields=c,protocol=protocols[cid]) for cid,c in cases.items()]
    # Retrieval has its own permission boundary. Case-derived rules remain
    # historical context even if their wording sounds like a general maxim.
    corpus=[]
    for u in units:
        linked=set(u.get('linked_cases',[]))|text_case_ids.get(digest(u['text']),set())
        if u.get('anchor',{}).get('status')=='abstract_or_unlocated':continue
        if not u['id'].startswith('assert:'):continue
        section=sections[u['section_id']]
        group='event-component:'+find(min(linked)) if linked else 'passage:'+digest(u['text'])
        split=component_split[find(min(linked))] if linked else split_for(group)
        corpus.append({'id':u['id'],'kind':'historical_case' if linked else 'source_assertion',
            'content':u['text'],'concept_id':u['concept_id'],'book_id':u['book_id'],
            'section_id':u['section_id'],'section_key':section['section_key'],
            'source_sha256':u['source_sha256'],'lines':u['anchor']['lines'],
            'assertion_kind':u['kind'],'review_status':u['review_status'],
            'excerpt_kind':'literal_source_transcription_not_independently_verified',
            'event_group':group,'split':split,'fresh_question_allowed':not linked})
    section_coverage=[]
    for sid,section in sections.items():
        indexed=set()
        for u in units:
            lines=u.get('anchor',{}).get('lines')
            if u.get('section_id')==sid and lines:indexed.update(range(lines[0],lines[1]+1))
        nonempty={i for i,line in enumerate(section['original_text'].splitlines(),1) if line.strip()}
        section_coverage.append({'section_id':sid,'book_id':section['book_id'],'title':section['title'],
             'original_nonblank_lines':len(nonempty),'indexed_assertion_or_author_lines':len(nonempty&indexed),
             'literal_index_line_coverage':round(len(nonempty&indexed)/max(1,len(nonempty)),4),
             'not_a_semantic_completeness_score':True})
    manifest={'schema':VERSION,'source_database_sha256':SOURCE_SHA,'section_count':len(sections),
              'case_registry_count':len(cases),'original_event_family_count':len({c['event_family_id'] for c in cases.values()}),
              'conservative_evidence_components':len(components),'source_assertion_count':len(tables['semantic_assertions']),
              'source_author_paragraphs':len(tables['historical_case_reasoning']),
              'source_additional_casts':len(tables['historical_case_additional_casts']),
              'source_units':len(units),'dialogue_samples':len(cards),
              'source_database_table_inventory':inventory,'verbatim_exported_tables':list(tables),
              'section_index_coverage':section_coverage,
              'tasks':dict(Counter(c['task'] for c in cards)), 'splits':dict(Counter(c['split'] for c in cards)),
              'stages':dict(Counter(c['curriculum_stage'] for c in cards)),
              'source_anchor_status':dict(coverage),'source_audit_issues':len(issues),
              'all_knowledge_proven_error_free':False,'prediction_accuracy_verified':False,'production_enabled':False,
              'notes':['QA count is not independent cases; chart reading is a separate capped task.',
                       'Author paragraphs and verdicts remain unchanged; no invented atomic reasoning.',
                       'Shared-event evidence uses holdout precedence test > validation > train.',
                       'Unlocated abstract records stay in archive, not automatically approved as literal gold.',
                       'User additions are versioned separately from original books.']}
    return {'manifest':manifest,'samples':cards,'units':units,'cases':registry,'source_tables':tables,'corpus':corpus,
            'source_issues':issues,'case_spans':spans}


def export_curriculum(output, db_path=SOURCE_DB):
    output=private_path(output);output.mkdir(parents=True,exist_ok=False)
    pack=build_curriculum(db_path)
    audit=audit_curriculum(pack)
    if not audit['passed']:raise ValueError('Curriculum audit failed: '+json_text(audit['errors'][:10]))
    for name,records in [('source_units',pack['units']),('case_registry',pack['cases']),('corpus',pack['corpus'])]+[
            (s,[r for r in pack['samples'] if r['split']==s]) for s in ('train','validation','test')]:
        (output/(name+'.jsonl')).write_text(''.join(json_text(r)+'\n' for r in records),encoding='utf8')
    write_json(output/'original_source_tables.json',pack['source_tables'])
    write_json(output/'source_audit_issues.json',pack['source_issues'])
    write_json(output/'case_source_spans.json',pack['case_spans'])
    write_json(output/'quality_audit.json',audit)
    with (output/'qa_review.csv').open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.writer(f)
        writer.writerow(['id','task','stage','split','source_or_event_group','question',
                         'prior_conversation','specific_answer','source_evidence','source_ids','status'])
        for row in pack['samples']:
            answer=json.loads(row['messages'][-1]['content'])
            writer.writerow([row['id'],row['task'],row['curriculum_stage'],row['split'],row['group'],
                row['messages'][-2]['content'],json_text(row['messages'][1:-2]),answer['summary'],
                json_text(answer['evidence']),json_text(row['source_ids']),
                'source_study_literal_checked_not_empirical_prediction_gold'])
    pack['manifest']['file_sha256']={p.name:digest(p.read_bytes()) for p in sorted(output.iterdir()) if p.is_file()}
    write_json(output/'manifest.json',pack['manifest'])
    return pack['manifest']


def audit_curriculum(pack):
    """Mechanical source/schema/leakage audit, not a claim of universal truth."""
    unit_map={u['id']:u for u in pack['units']}
    owners={}; errors=[]; summaries=Counter(); tasks=Counter()
    for row in pack['samples']:
        owners.setdefault(row['group'],set()).add(row['split'])
        if row['eligible_forecast_supervision'] or row['mode']!='source_study':errors.append([row['id'],'wrong_supervision_scope'])
        answer=json.loads(row['messages'][-1]['content'])
        summaries[answer['summary']]+=1;tasks[row['task']]+=1
        if answer['event_probability'] is not None or not all(isinstance(answer[k],list) for k in
                   ('evidence','counter_evidence','missing_information')):errors.append([row['id'],'schema'])
        if not answer['summary'].strip() or answer['summary'] in ('以下是来源资料，尚非现实预测验证。','作者书内复盘；可能包含后验解释，不能视为事前命中。'):
            errors.append([row['id'],'generic_or_empty_answer'])
        if any(uid not in unit_map for uid in row['source_ids']):errors.append([row['id'],'missing_source_unit'])
        if not all(e['citation'] in row['source_ids'] for e in answer['evidence']):errors.append([row['id'],'wrong_source_id'])
        for e in answer['evidence']:
            unit=unit_map[e['citation']]
            if unit['id'].startswith(('assert:','author:')):
                if re.sub(r'\s+','',e['statement']) not in re.sub(r'\s+','',unit['text']):
                    errors.append([row['id'],'book_evidence_not_verbatim'])
        for turn in row['messages']:
            if turn['role']=='assistant':
                a=json.loads(turn['content'])
                if set(a)!={'mode','summary','evidence','counter_evidence','missing_information','event_probability'}:
                    errors.append([row['id'],'prior_assistant_schema'])
    for group,splits in owners.items():
        if len(splits)>1:errors.append([group,'group_crosses_splits'])
    rank={'train':0,'validation':1,'test':2}
    for case in pack['cases']:
        if rank[case['split']]<rank[split_for(case['event_family_id'])]:errors.append([case['case_id'],'old_holdout_moved_into_training'])
    return {'passed':not errors,'errors':errors,'unique_answers':len(summaries),
            'largest_exact_answer_repetition':summaries.most_common(5),'task_counts':dict(tasks),
            'sample_count':len(pack['samples']),'original_case_count':len(pack['cases']),
            'independent_prediction_validation':False,'semantic_expert_review_complete':False}


def fit_training_view(row, tokenizer, max_length):
    """Preserve original records; compact only a declared contextual study view."""
    from copy import deepcopy
    from .qwen_finetune import encode_sample
    encoded,size=encode_sample(row,tokenizer,max_length)
    if encoded:return row,encoded,{'action':'original','tokens':size}
    adapted=deepcopy(row)
    # The original author paragraph is never truncated. For an oversized stage
    # dialogue, use its intact source paragraph as a reading/interpretation
    # exercise and retain the full board/disclosures in the archive.
    if row['task'].startswith('author_'):
        answer=json.loads(row['messages'][-1]['content'])
        source='\n'.join(e['statement'] for e in answer['evidence'])
        adapted['messages']=[row['messages'][0],{'role':'user','content':
            '这是书内作者一个完整分析阶段。原盘和全案另存，不把它当新事件首断。请据原文说明本阶段判断。\n'+source},row['messages'][-1]]
        adapted['task']='author_stage_source_reading_short_view'
        encoded,size=encode_sample(adapted,tokenizer,max_length)
        if encoded:return adapted,encoded,{'action':'intact_author_paragraph_view','tokens':size}
    return None,None,{'action':'needs_longer_context_original_retained','tokens':size,'id':row['id']}


def prepare_training_data(data, output, tokenizer, max_length=1536):
    """Tokenize and balance stages without silently deleting long source cases."""
    from .qwen_research import read_rows
    output=private_path(output);output.mkdir(parents=True,exist_ok=False)
    data=Path(data);manifest=json.loads((data/'manifest.json').read_text(encoding='utf8'))
    if manifest['schema']!=VERSION:raise ValueError('Wrong curriculum version')
    for name,sha in manifest['file_sha256'].items():
        if Path(name).name!=name or digest((data/name).read_bytes())!=sha:raise ValueError('Curriculum file hash mismatch '+name)
    result={}; audits={}; owner={}
    for split in ('train','validation','test'):
        rows=read_rows(data/(split+'.jsonl')); fitted=[]; excluded=[]; adaptations=Counter()
        for row in rows:
            if owner.setdefault(row['group'],split)!=split:raise ValueError('Shared event/source leakage')
            view,encoded,audit=fit_training_view(row,tokenizer,max_length)
            adaptations[audit['action']]+=1
            if view:
                fitted.append({'id':row['id'],'group':row['group'],'split':split,'task':view['task'],
                               'stage':row['curriculum_stage'],'encoded':encoded,'view_audit':audit})
            else:excluded.append(audit)
        result[split]=fitted
        audits[split]={'accepted':len(fitted),'accepted_tasks':dict(Counter(r['task'] for r in fitted)),
                       'adaptations':dict(adaptations),'excluded':excluded,
                       'accepted_event_components':len({r['group'] for r in fitted if r['group'].startswith('event-component:')})}
        (output/(split+'_encoded.jsonl')).write_text(''.join(json_text(r)+'\n' for r in fitted),encoding='utf8')
    # Keep chart reading useful but subordinate. This is sampling, not creation
    # of additional observed cases or discarded source knowledge.
    rows=result['train']; knowledge=[r for r in rows if r['stage']=='knowledge']
    workflow=[r for r in rows if r['stage']=='workflow']; chart=[r for r in rows if r['stage']=='chart']
    deterministic=lambda r:digest('v2-stage-selection:'+r['id'])
    chart=sorted(chart,key=deterministic)[:max(1,len(knowledge)//3)]
    stage1=knowledge+chart+sorted(workflow,key=deterministic)[:max(1,len(knowledge)//3)]
    stage2=workflow+sorted(knowledge,key=deterministic)[:max(1,len(workflow)//3)]
    for name,rows in [('knowledge',stage1),('workflow',stage2)]:
        (output/(name+'_stage.jsonl')).write_text(''.join(json_text(r)+'\n' for r in rows),encoding='utf8')
    status={'schema':VERSION,'max_seq_length':max_length,'audits':audits,
            'stage_counts':{'knowledge':len(stage1),'workflow':len(stage2)},
            'training_cases_independent_of_question_count':True,'production_enabled':False}
    write_json(output/'token_audit.json',status)
    return status
