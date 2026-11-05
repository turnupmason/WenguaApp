"""Complete source-accounted two-book curriculum, separate from running v4.

Coverage means each supplied source unit has an explicit disposition and each
teaching fragment has a task or an exact duplicate target. It is not a claim
that a model has learned every rule or that historical predictions are true.
"""
from __future__ import annotations
from collections import Counter,defaultdict
import copy
import hashlib
import json
from pathlib import Path
import re
import sqlite3

from .qwen_course_v4 import compact,sha,load,dump,printed_board_key
from .qwen_book_dataset_v3 import SOURCE_SHA256,BOOKS

SCHEMA='wengua_source_accounted_course_v5'
SYSTEM=('直接回答所问。概念题说定义和必要条件；应用题说结果、原因和具体证据，结论不重复。'
        '按题目指定的书、章节和方法解释，不混用异说。原书案例区分初断、后来披露、反馈与纠正。'
        '缺失的宫位、身份、日期不补造；不输出无依据的概率或人工吉凶分数。')

# Every declared strategy must be dispatched. Unknown values fail preparation.
STRATEGIES=frozenset(('trigram_explicit_facets','stem_sentence_facets','branch_sentence_facets',
 'door_source_paragraph_facets','star_source_paragraph_facets','deity_source_facets',
 'ordered_heaven_earth_pairs','ordered_door_pairs','ordered_door_stem_pairs',
 'reviewed_formation_subrules','nine_dun_source_subparagraphs','three_zha_five_jia_source_subparagraphs',
 'body_map_explicit_palace_facets','month_pair_terms_with_boundary','branch_double_hour',
 'sexagenary_members_and_void','reference_solar_dates_only','six_jia_explicit_instruments',
 'star_context_roles_and_duality','literal_twelve_growth_tables','door_role_domain_specific',
 'deity_conditional_duality','hour_branch_horse','timing_success_condition_carried',
 'timing_failure_condition_carried','kaiwu_ordered_pair_briefs','kaiwu_nine_dun_exact_branches',
 'three_nobles_rise','six_instrument_punishment_pairs','guest_host_explicit_dimension'))


def declared_strategies(reviews):
    found=[g['strategy'] for m in reviews for g in m.get('typed_groups',[])]
    unknown=set(found)-STRATEGIES
    if unknown:raise ValueError('Unimplemented curriculum strategy: '+','.join(sorted(unknown)))
    return found


def sentences(text):
    """Keep full sentences; never split an AND/OR list on its commas."""
    return [m.group(0).strip() for m in re.finditer(r'[^。！？]+[。！？]?|[。！？]',text) if m.group(0).strip()]


def semantic_chunks(text,limit=320):
    """Whole dependency-preserving bundles; connectors retain their antecedent."""
    pieces=[];current=''
    for sentence in sentences(text):
        dependent=bool(re.match(r'^(但|若|如果|否则|反之|因此|故|所以|又|此|其|它|他|她|这|前者|后者|得令|失令|遇|逢|受克|生旺)',sentence))
        if current and len(current)+len(sentence)>limit and not dependent:
            pieces.append(current);current=''
        current+=sentence
    if current:pieces.append(current)
    return pieces


def facet_of(text):
    patterns=[('方位',r'^在方位|^在方向|方位为|先天位|后天位'),('时间',r'^在时间|时间为'),
      ('数字',r'^在数|^数字|先天数|后天数'),('动物',r'^在动物|^动物|^动植物'),
      ('静物',r'^在静物|^静物|^物品'),('人体',r'^在人体|^人体|^五脏|^体表'),
      ('颜色',r'^在颜色|^颜色'),('五味',r'^五味|^在五味'),
      ('人物',r'^在国家|^在家庭|^在社会|^在人物|^人物|^在人'),('场所',r'^在场所|^主.*场所'),
      ('阴阳五行及方位',r'^.{0,5}五行|^五行|^[甲乙丙丁戊己庚辛壬癸子丑寅卯辰巳午未申酉戌亥]：五行'),
      ('时令与强弱',r'^得令|^失令|^受克|^生旺'),('专题取用',r'^在奇门|^在测|^测|^奇门中'),
      ('条件转义',r'但是|但若|如果|若逢|双重性|反之')]
    for label,pattern in patterns:
        if re.search(pattern,text):return label
    if re.match(r'^[乾坤震巽坎离艮兑]为',text):return '自然象与性质'
    return '性质与适用条件'


def trim_heading(text):
    return re.sub(r'^\s*[（(][一二三四五六七八九十0-9]+[)）]\s*','',text).strip()


def five_jia_sections(quote):
    """The first book defines these as '...叫天假', not '天假：...'."""
    names=['天假','地假','人假','神假','鬼假']
    starts=[quote.find(x) for x in ('景门合','杜门合','惊门合','伤门合','死门合')]
    common_start=quote.find('五假，是')
    if common_start<0 or any(n<0 for n in starts) or starts!=sorted(starts):
        raise ValueError('Five-jia source needs explicit reviewed boundaries')
    return quote[:common_start].strip(),quote[common_start:starts[0]].strip(),[
        (name,quote[start:starts[i+1] if i+1<len(starts) else len(quote)].strip()) for i,(name,start) in enumerate(zip(names,starts))]


class Curriculum:
    def __init__(self,pack,inventory,reviews,sections,coordinates):
        self.pack=pack;self.inventory=inventory;self.lookup={u['review_key']:u for u in inventory}
        self.reviews=reviews;self.sections=sections;self.coordinates=coordinates
        self.units=copy.deepcopy(pack['units']);self.units.update({u['id']:copy.deepcopy(u) for u in inventory})
        self.rows=[];self.prompts={};self.traces=defaultdict(list);self.dispositions={};self.dispatches=[]
        self.excluded={k:v for m in reviews for k,v in m.get('excluded',{}).items()}
        self.case_splits={r['case_id']:r['split'] for r in pack['records'] if r.get('case_id')}
        self.case_groups={r['case_id']:r['group'] for r in pack['records'] if r.get('case_id')}
        self.case_notes={d['case_id']:(n,pack['review_notes'][n-1]) for n,d in enumerate(pack['dossiers'],1)}
        self.case_refs={r['case_id']:r['source_ids'] for r in pack['records'] if r.get('case_id')}
        self.embedded_case_links={}
        numbers={733:7,734:92,773:3,1065:3,774:98,867:98,786:2,1074:2,1066:23,842:23,1075:85,1085:53,1086:59,1087:63,1249:122,1250:162,1253:6,1254:74,1269:176,1270:77}
        numbers.update({n:30 for n in [*range(1020,1026),*range(1033,1040),1045,1049]})
        numbers.update({n:70 for n in [1046,1050,1083,1084]})
        numbers.update({n:143 for n in range(1442,1451)})
        for n,case in numbers.items():self.embedded_case_links[self.lookup[f'G{n:04d}']['id']]=pack['dossiers'][case-1]['case_id']
        self.ranges=defaultdict(list)
        for sid,items in coordinates.items():
            for x in items:self.ranges[int(sid)].append((x['lines'][0],x['lines'][1],x['case_id']))
    def resolve(self,refs):
        return list(dict.fromkeys(self.lookup[x]['id'] if x in self.lookup else x for x in refs))
    def guarded_cases(self,refs):
        result=set()
        for uid in refs:
            u=self.units[uid];sid=u.get('section_id');lines=u.get('lines')
            if sid is not None and lines:
                for a,b,cid in self.ranges[int(sid)]:
                    if max(a,lines[0])<=min(b,lines[1]):result.add(cid)
        for uid in refs:
            if uid in self.embedded_case_links:result.add(self.embedded_case_links[uid])
            u=self.units[uid]
            if u.get('section_id')==25 and u.get('lines') and (max(49,u['lines'][0])<=min(61,u['lines'][1]) or u['lines']==[101,101]):result.add(self.pack['dossiers'][29]['case_id'])
        return sorted(result)
    def add(self,q,a,refs,*,task,fmt='foundation_qa',context='',mode='book_knowledge',case_id=None,fragments=(),review=None):
        refs=self.resolve(refs);q=q.strip();a=a.strip()
        if not a or not refs:raise ValueError('Empty target/evidence')
        if len(a)>1400:raise ValueError('Unsplit target: '+q)
        for uid in refs:
            if uid not in self.units:raise ValueError('Unknown source: '+uid)
        cases=set(self.guarded_cases(refs))
        if case_id:cases.add(case_id)
        # General chapters also retell cases. The source's initial mistake must
        # not become a positive gold rule merely because it lacks a case ID.
        if cases and case_id is None:
            context+='\n涉及的原案只作来源复盘；不能把后来反馈当成事前已知。'
            if review!='v4_manually_rewritten_target_preserved':
                for cid in sorted(cases):
                    number,note=self.case_notes[cid]
                    if number in getattr(self,'case_correction_required',set()) and compact(note['review_note']) not in compact(a):
                        a+='\n本例核对：'+note['review_note']
                        refs=list(dict.fromkeys([*refs,*self.case_refs[cid]]))
        if len(a)>1400:raise ValueError('Correction needs reviewed split: '+q)
        # Universal knowledge is taught. Historical events remain in their
        # fixed v4 holdout families, including all cross-book rewordings.
        splits={self.case_splits[c] for c in cases if c in self.case_splits}
        split='test' if 'test' in splits else 'validation' if 'validation' in splits else 'train'
        messages=[{'role':'system','content':SYSTEM},{'role':'user','content':q+('\n'+context if context else '')},{'role':'assistant','content':a}]
        identity=json.dumps(messages[:-1],ensure_ascii=False,sort_keys=True)
        if identity in self.prompts:
            row=self.prompts[identity]
            if row['answer']!=a:raise ValueError('Conflicting targets: '+q)
            rid=row['id']
        else:
            rid='v5:'+sha(identity+a)[:20]
            groups=sorted({self.case_groups[c] for c in cases if c in self.case_groups})
            row={'id':rid,'question':q,'answer':a,'messages':messages,'source_ids':refs,
                 'case_id':case_id,'case_ids':sorted(cases),'split':split,
                 'group':groups[0] if len(groups)==1 else 'source:'+sha('|'.join(refs))[:16],
                 'format':fmt,'task':task,'source_mode':mode,'review':review or 'source_supported_target'}
            self.rows.append(row);self.prompts[identity]=row
        for ref in refs:self.traces[ref].append(rid)
        for f in fragments:
            u=self.units[f['source_id']];text=u['original_quote']
            if text[f['start']:f['end']]!=f['text']:raise ValueError('Bad teaching span')
        if fragments:
            self.units.setdefault('_teaching_fragments',{})[rid]=list(fragments)
        return rid
    def source_fragment(self,ref,text):
        uid=self.resolve([ref])[0];quote=self.units[uid]['original_quote'];start=quote.find(text)
        if start<0:
            offsets=[i for i,ch in enumerate(quote) if not ch.isspace()]
            normalized=''.join(quote[i] for i in offsets);needle=compact(text);pos=normalized.find(needle)
            if pos<0:raise ValueError('Teaching fragment not literal: '+ref)
            start=offsets[pos];end=offsets[pos+len(needle)-1]+1;text=quote[start:end]
        return {'source_id':uid,'start':start,'end':start+len(text),'text':text}
    def raw(self,sid,lo,hi):
        section=self.sections[int(sid)];quote='\n'.join(section['original_text'].splitlines()[lo-1:hi])
        uid=f'v5source:{sid}:L{lo}-{hi}:'+sha(quote)[:12]
        self.units[uid]={'id':uid,'book_id':section['book_id'],'section_id':int(sid),'chapter':section['title'],
            'source_sha256':section['sha256'],'lines':[lo,hi],'original_quote':quote,'match_status':'literal_line_slice'}
        return uid
    def source_lesson(self,key,q,text=None,*,carry=(),task='source_condition_rule',fmt='foundation_qa',context=''):
        number=int(key[1:])
        if 1056<=number<=1064:
            context='前提：已综合判断事情可成；先定远近快慢和时间单位。'+context
        elif 1068<=number<=1073:
            context='前提：已综合判断事情不成；取应败之期，不是自动转好的日期。'+context
        if 1328<=number<=1379:
            context='本章职业类象须带合局、得时得地及奇门吉格等共同前提；不能只凭星名定职业。'+context
            carry=tuple(dict.fromkeys((*carry,'G1378')))

        u=self.lookup[key];text=u['original_quote'].strip() if text is None else text
        # The answer retains every condition in this fragment. Its full source
        # context stays available separately, not injected as a later outcome.
        fragment=self.source_fragment(key,text);text=fragment['text']
        carried=[]
        for ref in carry:
            quote=self.lookup[ref]['original_quote'].strip()
            if ref=='G1378':
                quote=next(s for s in sentences(quote) if '前提必须是合局' in s)
            carried.append(self.source_fragment(ref,quote))
        extra='\n'.join(f['text'] for f in carried)
        if extra:text+='\n共同限制：'+extra
        return self.add(q,text,[key,*carry],task=task,fmt=fmt,context=context,fragments=[fragment,*carried],mode='source_rule_explanation')
    def subject(self,u):
        c=u.get('concept','');p=c.split(':')
        if len(p)>1 and p[0] in ('trigram','stem','branch','door','star','deity'):
            return p[1]+('卦' if p[0]=='trigram' else '门' if p[0]=='door' else '')
        s=trim_heading(u['original_quote']);return re.split(r'[：:。；\n]',s)[0][:26]
    def faceted(self,key,*,kind,carry=()):
        u=self.lookup[key];book=BOOKS[u['book_id']];subject=self.subject(u);quote=u['original_quote'].strip()
        if kind=='trigram':chunks=[quote]
        elif kind in ('stem','branch'):
            chunks=[s for s in sentences(quote) if s]
            if kind=='branch':chunks=[x.strip() for s in chunks for x in re.split(r'(?<=；)',s) if x.strip()]
        elif kind=='door':
            chunks=semantic_chunks(quote,180)
        else:chunks=semantic_chunks(quote,250)
        for i,text in enumerate(chunks,1):
            scope=facet_of(trim_heading(text));anchor=re.sub(r'^[①②③④⑤⑥⑦⑧⑨⑩]|^.{1,5}[：:]','',text).strip()[:22]
            q=f'{book}的{subject}条目中，关于{scope}的“{anchor}”应怎样理解？'
            if kind=='trigram':q=f'{book}的{subject}在{scope}方面列有哪些类象与条件？'
            if kind=='stem' and any(x in text for x in ('妻','丈夫','女人','医生','情夫','情妇')):
                q=f'{book}的{subject}有哪些专题角色？请保留原文语境，不当成任意问题的固定身份。'
            self.source_lesson(key,q,text,carry=carry,task=kind+'_facet')
    def dispatch(self,g):
        strategy=g['strategy']
        if strategy not in STRATEGIES:raise ValueError('Unimplemented curriculum strategy: '+strategy)
        before=len(self.rows);keys=[f'G{n:04d}' for n in range(g['keys'][0],g['keys'][1]+1) if n not in g.get('exclude_keys',[])]
        for key in keys:
            u=self.lookup[key];quote=u['original_quote'].strip();book=BOOKS[u['book_id']];concept=u.get('concept','')
            if key in getattr(self,'semantic_overrides',{}):continue
            # Container duplicates are linked after their literal children are rendered.
            if key in self.excluded and any(x in self.excluded[key] for x in ('容器','小节标题','只有图题')):continue
            if strategy=='trigram_explicit_facets':self.faceted(key,kind='trigram')
            elif strategy=='stem_sentence_facets':self.faceted(key,kind='stem')
            elif strategy=='branch_sentence_facets':self.faceted(key,kind='branch')
            elif strategy=='door_source_paragraph_facets':self.faceted(key,kind='door')
            elif strategy in ('star_source_paragraph_facets','star_context_roles_and_duality'):self.faceted(key,kind='star')
            elif strategy in ('deity_source_facets','deity_conditional_duality'):self.faceted(key,kind='deity')
            elif strategy in ('ordered_heaven_earth_pairs','kaiwu_ordered_pair_briefs'):
                parts=concept.split(':')
                if parts[0] not in ('heaven_over_earth','stem_pair'):continue
                h,e=parts[-2:]
                self.source_lesson(key,f'{book}中，天盘{h}加地盘{e}的名称、主客含义和适用限制是什么？',task='ordered_stem_conditions')
            elif strategy in ('ordered_door_pairs','ordered_door_stem_pairs'):
                prefix='door_over_door:' if strategy=='ordered_door_pairs' else 'door_over_stem:'
                if not concept.startswith(prefix):continue
                a,b=concept[len(prefix):].split(':')
                self.source_lesson(key,f'{book}门的克应中，{a}门加{b}{"门" if "door_pairs" in strategy else "干"}有哪些明确断语？',task='ordered_door_rule')
                if key=='G0336':self.source_lesson(key,f'{book}中，休门加癸的克应是什么？壬、癸是否合写？',task='ordered_door_rule')
            elif strategy=='three_zha_five_jia_source_subparagraphs':
                intro,common,parts=five_jia_sections(quote)
                self.source_lesson(key,f'{book}三诈怎样构成，真诈、休诈、重诈怎样区分？',intro,task='three_zha_conditions')
                self.source_lesson(key,f'{book}五假的共同适用条件和忌讳是什么？',common,task='five_jia_common_conditions')
                for name,part in parts:
                    self.add(f'{book}的{name}怎样构成、适宜何事？请保留原文异说与共同限制。',part+'\n共同限制：'+common,[key],
                        task='five_jia_complete_conditions',mode='source_rule_explanation',
                        fragments=[self.source_fragment(key,part),self.source_fragment(key,common)])
            elif strategy=='nine_dun_source_subparagraphs':
                labels='天遁 地遁 人遁 风遁 云遁 龙遁 虎遁 神遁 鬼遁'.split()
                matches=list(re.finditer('('+'|'.join(labels)+r')[：:]',quote))
                if len(matches)!=9:raise ValueError('Nine-dun definitions missing named source branches')
                for i,m in enumerate(matches):
                    text=quote[m.start():matches[i+1].start() if i+1<len(matches) else len(quote)].strip()
                    self.source_lesson(key,f'{book}的{m[1]}怎样构成？哪些选择分支和限制不能省略？',text,task='formation_complete_conditions')
            elif strategy=='body_map_explicit_palace_facets':
                # Full clauses begin with a named palace. Initial rough geometry
                # and detailed outer/inner analogies are different teaching scopes.
                for m in re.finditer(r'(离九宫|坤二宫|巽四宫|震3宫|兑7宫|艮8宫|乾6宫|坎1宫)在体表[^。]+。',quote):
                    text=m[0];self.source_lesson(key,f'{book}疾病象意段中，{m[1]}的体表与体内分别比附什么？',text,task='body_surface_internal_analogy')
                first=quote.split('\n\n')[0]
                self.source_lesson(key,f'{book}怎样以九宫大致比附人体位置？',first,task='body_rough_analogy')
            elif strategy=='sexagenary_members_and_void':
                if not concept.startswith('calendar:xun:'):continue
                xun=concept.split(':')[-1]
                self.source_lesson(key,f'{book}六十甲子表中，{xun}旬包括哪十个干支，哪两支旬空？',task='xun_members_void')
            elif strategy=='reference_solar_dates_only':
                self.source_lesson(key,f'{book}参考日期表中，“{quote}”的两个节气约在何日？',task='reference_dates',context='这里只问原书参考日期；具体年份按精确交节时刻处理。')
            elif strategy=='six_jia_explicit_instruments':
                xun=concept.split(':')[-1]
                self.source_lesson(key,f'{book}为什么把{xun}配给该六仪？请说明本段仪仗与颜色的文化解释。',task='six_jia_source_explanation')
            elif strategy=='literal_twelve_growth_tables':
                if u.get('kind')!='heavenly_stem_twelve_state':continue
                self.source_lesson(key,f'{book}“{self.subject(u)}”的十二长生与原文取法怎样对应？',task='twelve_growth_source_table')
            elif strategy=='door_role_domain_specific':self.faceted(key,kind='door_domain')
            elif strategy=='hour_branch_horse':
                if not concept.startswith('branch:horsemanship:'):continue
                self.source_lesson(key,f'{book}按时支取马星，“{quote}”这一组的马支是什么？',task='hour_branch_horse')
            elif strategy in ('timing_success_condition_carried','timing_failure_condition_carried'):
                if '\n' in quote:continue
                state='事可成' if 'success' in strategy else '事不成'
                self.source_lesson(key,f'{book}已综合判断{state}，关于“{quote}”应怎样取期？',task='outcome_conditioned_timing',fmt='conditional_dialogue',context='解释本条方法，不补造具体年月日。')
            elif strategy in ('month_pair_terms_with_boundary','branch_double_hour'):
                branch=concept.split(':')[-1]
                self.source_lesson(key,f'{book}原表中，{branch}{"月" if "month" in strategy else "时"}对应什么？',task=strategy)
            elif strategy in ('reviewed_formation_subrules','kaiwu_nine_dun_exact_branches','three_nobles_rise','six_instrument_punishment_pairs'):
                name=re.split(r'[：:。\n]',trim_heading(quote))[0][:32]
                self.source_lesson(key,f'{book}“{name}”的完整构成、适用情形及例外是什么？',carry=g.get('carry_refs',()),task='formation_complete_conditions')
            elif strategy=='guest_host_explicit_dimension':
                if '\n' in quote:continue
                scope=re.split('[，,]',quote)[0].lstrip('①②③④⑤⑥⑦⑧⑨⑩')
                self.source_lesson(key,f'{book}按{scope}怎样分主客？',task='guest_host_dimension')
            else:raise AssertionError('Missing strategy branch: '+strategy)
        self.dispatches.append({'strategy':strategy,'keys':g['keys'],'new_tasks':len(self.rows)-before,'dispatched':True})


def classify_nonlesson(u,reason):
    """Only explicit editorial/scaffolding decisions; not a generic skip filter."""
    q=u['original_quote'].strip();k=u.get('review_key','')
    if any(s in q for s in ('原输入','所提供原文只有图题','本文件仅清理','OCR错位','提供的OCR','原输入只有','原图未提供')):
        return 'editorial_source_note'
    if re.fullmatch(r'(?:[（(]?[一二三四五六七八九十0-9]+[)）]?[、.．]?)?(?:第[一二三四五六七八九十]+[章节篇].*|图\d+.*)',q):
        return 'structure_heading'
    if reason and any(s in reason for s in ('教学开场','没有独立知识判断','导言','结束过渡','过渡句','学习要求','练习鼓励','器具介绍','方法推广与宣传','开场','纯宣传')):
        return 'reading_scaffolding'
    return None


def paragraph_scope(text):
    text=trim_heading(text).lstrip('①②③④⑤⑥⑦⑧⑨⑩')
    text=re.sub(r'\s+',' ',text)
    first=re.split(r'[，,。；;：:\n]',text)[0]
    if len(first)<5 or first in ('又曰','歌中曰','比如','例如','首先','其次','再次','总之'):
        return text[:32]
    return first[:32] or text[:24]


def import_v4_targets(c):
    """Re-use reviewed short answers, while fixing the universal-rule split policy."""
    for r in c.pack['records']:
        q=r['question'];message=r['messages'][-2]['content']
        context=message[len(q):].lstrip() if message.startswith(q) else message
        rid=c.add(q,r['answer'],r['source_ids'],task=r['task'],fmt=r['format'],context=context,
                  mode=r['source_mode'],case_id=r.get('case_id'),review='v4_manually_rewritten_target_preserved')
        # Preserve multi-turn conditions exactly, not merely their final question.
        if len(r['messages'])>3:
            row=next(x for x in c.rows if x['id']==rid)
            old_identity=json.dumps(row['messages'][:-1],ensure_ascii=False,sort_keys=True)
            c.prompts.pop(old_identity)
            row['messages']=[dict(m) for m in r['messages']];row['messages'][0]['content']=SYSTEM
            row['id']='v5:'+sha(json.dumps(row['messages'],ensure_ascii=False,sort_keys=True))[:20]
            c.prompts[json.dumps(row['messages'][:-1],ensure_ascii=False,sort_keys=True)]=row
            for uid in row['source_ids']:
                c.traces[uid]=[row['id'] if x==rid else x for x in c.traces[uid]]


def exact_target_coverage(c,quote):
    """A literal target match is stronger than mere presence in its references."""
    needle=compact(quote)
    if not needle:return []
    cache=getattr(c,'_target_text_cache',None)
    if cache is None or cache[0]!=len(c.rows):
        cache=(len(c.rows),[(r['id'],compact(r['answer'])) for r in c.rows]);c._target_text_cache=cache
    return [rid for rid,text in cache[1] if needle in text]


def complete_general_units(c):
    for u in sorted(c.inventory,key=lambda x:(len(compact(x['original_quote'])),x['review_key'])):
        key=u['review_key'];uid=u['id'];quote=u['original_quote'].strip();reason=c.excluded.get(key,'')
        if key in getattr(c,'semantic_overrides',{}):
            decision=c.semantic_overrides[key]
            rid=c.add(decision['q'],decision['a'],decision['refs'],task='source_scope_and_evidence_boundary',mode='reviewed_source_boundary')
            c.dispositions[key]={'state':'scope_or_comparison_explained','reason':'保留本段观点、方法边界与来源性质，不把比较、引述或自述变成无条件事实。','task_ids':[rid]}
            continue
        nonlesson=classify_nonlesson(u,reason)
        if nonlesson:
            c.dispositions[key]={'state':nonlesson,'reason':reason or '原始整理说明或结构文字；保留来源，不编成专业推断规则。','task_ids':[]}
            continue
        match=exact_target_coverage(c,quote)
        if match:
            c.dispositions[key]={'state':'literal_target_or_exact_duplicate','reason':'完整源字串可在列出的教学答案找到；非仅引用ID。','task_ids':match}
            continue
        # Registered short fragments extracted inside a larger source paragraph
        # must be taught with that paragraph's actual conditions, not alone.
        parents=[p for p in c.inventory if p['id']!=uid and p['section_id']==u['section_id'] and
                 len(p['original_quote'])>len(quote) and compact(quote) in compact(p['original_quote'])]
        if parents and len(quote)<70:
            parent=min(parents,key=lambda p:len(p['original_quote']))
            # The full parent is decomposed later; make an explicit source reading
            # exercise whose question retains the entire governing source paragraph.
            q=f'{BOOKS[u["book_id"]]}“{quote}”这句话在本段中有什么上下文条件？'
            a=parent['original_quote'].strip()
            if len(a)<=500:
                rid=c.add(q,a,[uid,parent['id']],task='context_required_fragment',context='请按完整原文理解，勿把孤立短语当通则。',mode='contextual_source_reading',fragments=[c.source_fragment(parent['review_key'],a)])
                c.dispositions[key]={'state':'context_restored_fragment','reason':'恢复父段条件，不能把截断关键词直接当规则。','task_ids':[rid]}
                continue
        if c.traces.get(uid):
            # Prior paraphrases or faceted tasks exist. Still retain a literal,
            # complete dependency-preserving decomposition for the unrendered text.
            existing=list(dict.fromkeys(c.traces[uid]))
        else:existing=[]
        if re.search(r'[|│]',quote):
            ids=[];prose=[]
            for line_index,line in enumerate(quote.splitlines(),1):
                if re.fullmatch(r'[+\-─┌┬┐├┼┤└┴┘\s]+',line):continue
                if line.strip().startswith(('|','│')):
                    for column,cell in enumerate((x.strip() for x in re.split('[|│]',line) if x.strip()),1):
                        question=f'{BOOKS[u["book_id"]]}《{u["chapter"]}》第{u["lines"][0]}—{u["lines"][1]}行文字表，第{line_index}行第{column}格怎样记载？'
                        ids.append(c.add(question,cell,[uid],task='complete_table_cell_reading',fmt='chart_application',
                                   context='按原书本行文字逐格读取，不冒称已核对原图。\n'+line,mode='literal_table_reading'))
                elif line.strip():prose.append(line.strip())
            for index,text in enumerate(prose,1):
                if text.startswith(('图','（','(')) and len(text)<65:continue
                ids.append(c.source_lesson(key,f'{BOOKS[u["book_id"]]}《{u["chapter"]}》第{u["lines"][0]}—{u["lines"][1]}行，文字表旁“{paragraph_scope(text)}”说明什么？',text,task='table_explanatory_rule'))
            if ids:
                c.dispositions[key]={'state':'table_cells_and_explanations','reason':'文字表逐单元格处理；含多宫的一行不归给某一个宫。','task_ids':ids}
                continue
        parts=semantic_chunks(quote,260)
        if any(len(p)>1000 for p in parts):
            # A long container is represented by its literal child units. Its
            # uncovered segments cannot be claimed complete by a citation alone.
            children=[p for p in c.inventory if p['id']!=uid and p['section_id']==u['section_id'] and
                      len(p['original_quote'])<len(quote) and compact(p['original_quote']) in compact(quote)]
            if not children:raise ValueError('Long source needs reviewed decomposition: '+key)
            c.dispositions[key]={'state':'container_pending_child_check','reason':reason,'children':[p['review_key'] for p in children],'task_ids':existing}
            continue
        ids=[]
        for n,text in enumerate(parts,1):
            subject=c.subject(u);scope=paragraph_scope(text)
            q=f'{BOOKS[u["book_id"]]}《{u["chapter"]}》第{u["lines"][0]}—{u["lines"][1]}行，关于“{scope}”的具体条件和原意是什么？'
            if len(parts)>1:q+=f'（本条第{n}个完整语义段）'
            ids.append(c.source_lesson(key,q,text,task='complete_source_rule_reading',context='按指定原书表述；历史类象、作者假设和案例叙述不当作现实事实证明。'))
        c.dispositions[key]={'state':'source_supported_lessons','reason':'已按完整语义段补齐；有分组任务或原短答时保留关联。','task_ids':list(dict.fromkeys([*existing,*ids]))}
    # Resolve only real parent/child coverage, never a blanket "already covered" label.
    pending={k for k,v in c.dispositions.items() if v['state']=='container_pending_child_check'}
    while pending:
        changed=False
        for key in list(pending):
            entry=c.dispositions[key]
            if any(ch in pending for ch in entry['children']):continue
            ids=list(dict.fromkeys(rid for ch in entry['children'] for rid in c.dispositions[ch]['task_ids']))
            parent=compact(c.lookup[key]['original_quote'])
            masked=list(parent)
            for child in entry['children']:
                text=compact(c.lookup[child]['original_quote']);pos=parent.find(text)
                if pos>=0:masked[pos:pos+len(text)]=[' ']*len(text)
            # Never turn partial child coverage into a complete-parent claim.
            if not ids or re.search(r'[\u3400-\u9fffA-Za-z0-9]', ''.join(masked)):
                raise ValueError('Incomplete literal child container coverage: '+key)
            entry.update(state='explicit_child_container',task_ids=ids)
            pending.remove(key);changed=True
        if not changed:raise ValueError('Unresolved source container cycle: '+','.join(sorted(pending)))


def add_author_steps(c):
    notes={n['n']:n for n in c.pack['review_notes']};coverage=[]
    for number,d in enumerate(c.pack['dossiers'],1):
        note=notes[number];cid=d['case_id']
        for s in d['author_steps']:
            uid=s['source_id'];original=s['original'].strip()
            parts=semantic_chunks(original,260)
            ids=[]
            for i,text in enumerate(parts,1):
                scope=paragraph_scope(text)
                q=f'复盘原书案例{cid}：第{s["step"]}步关于“{scope}”，原分析采用了哪些条件和推断？'
                if len(parts)>1:q+=f'（第{i}段）'
                # This is an attributed quotation task. A case-level correction is
                # kept next to it; no raw mistaken step becomes an unqualified rule.
                board='\n'.join(f"{cell['palace_label_raw']}：神{cell['deity_raw']}，门行{cell['door_position_raw']}，星行{cell['star_position_raw']}" for cell in d['primary_printed_chart'])
                context='背景及信息披露：'+note['context']+'\n原书主盘抄录：\n'+(board or '主盘不完整，不补造。')+'\n案例核对：'+note['review_note']
                answer=re.sub(r'^\s*[（(]?\d+[)）.、]\s*','',text)
                if number in getattr(c,'case_correction_required',set()):
                    q+='同时说明本例的更正、反馈差异或适用限制。'
                    answer='原段：'+answer+'\n核对：'+note['review_note']
                ids.append(c.add(q,answer,[uid],task='author_step_attributed_review',fmt='complete_case',context=context,
                      case_id=cid,mode='attributed_historical_step_not_independent_prediction',review='original_statement_with_case_correction_context'))
            speaker='source_narrator_not_assumed_to_be_teacher'
            u=c.units[uid];sid=u.get('section_id');lo=u.get('lines',[0])[0]
            for a,b,case in c.ranges.get(sid,[]):
                if case!=cid:continue
                preceding='\n'.join(c.sections[sid]['original_text'].splitlines()[a-1:lo])
                if re.search(r'张志春[按评批]|张老师[按评批]',preceding):speaker='explicit_teacher_commentary'
            if number in (185,186,187,188,189,190,191) and speaker!='explicit_teacher_commentary':speaker='student_or_letter_analysis_in_explicit_error_case'
            coverage.append({'case_id':cid,'step':s['step'],'source_id':uid,'task_ids':ids,'speaker_status':speaker,'correction_required':number in getattr(c,'case_correction_required',set()),'status':'attributed_review_with_correction_context'})
    return coverage


def add_line_accounting(c):
    """Account every supplied nonblank line; never call borders knowledge."""
    report=[];residual=[]
    for sid,section in sorted(c.sections.items()):
        for n,line in enumerate(section['original_text'].splitlines(),1):
            if not line.strip():continue
            entry={'section_id':sid,'book_id':section['book_id'],'line':n,'sha256':sha(line),'source_ids':[],'task_ids':[]}
            general=[u for u in c.inventory if u['section_id']==sid and u['lines'][0]<=n<=u['lines'][1]]
            cases=[cid for a,b,cid in c.ranges[sid] if a<=n<=b]
            if general:
                entry.update(state='general_source_disposition',source_ids=[u['id'] for u in general],review_keys=[u['review_key'] for u in general])
            elif cases:entry.update(state='historical_case_source',case_ids=sorted(set(cases)))
            elif (sid,n) in {(1,1),(1,20),(1,76),(1,108),(1,120),(1,147),(1,149),(2,1),(2,219),(2,285),(2,349),
              (3,7),(3,27),(3,47),(3,67),(3,485),(4,2),(4,14),(4,22),(4,82),(4,86),(4,98),(4,106),(4,120),(4,136),(4,140),(4,158),(4,222),
              (22,1),(22,179),(23,31),(23,73),(23,184),(24,160),(25,45),(25,80),(25,89),(25,121),(25,145),(25,177),(25,194),(25,208),(25,216),(25,244),(25,434),(25,508),(25,606),(25,634),
              (27,47),(28,3),(43,51),(43,115),(43,211),(43,253),(43,312),(43,380),(43,415),(43,450),(43,525),(43,527)}:
                entry['state']='verified_heading_or_transition'
            elif re.fullmatch(r'[+\-─┌┬┐├┼┤└┴┘\s]+',line):entry['state']='table_border'
            elif re.match(r'^\s*(?:[《（(]?[一二三四五六七八九十0-9]+[)）]?[、.．]|第[一二三四五六七八九十]+[章节篇]|[（(]图?\d+|图\d+|《神奇之门》|《开悟之门》)',line) and len(line)<105:
                entry['state']='chapter_heading_or_diagram_label'
            elif len(line.strip())<12 and not re.search(r'为|从|主|在|门|星|甲|乙|丙|丁',line):entry['state']='structure_caption'
            else:
                uid=c.raw(sid,n,n);quote=line.strip()
                if line.strip().startswith(('|','│')):
                    # One source row may contain three different palaces. Each
                    # literal cell is a separate reading target, never one palace
                    # falsely assigned the whole row.
                    cells=[x.strip() for x in re.split('[|│]',quote) if x.strip()]
                    ids=[]
                    for cell in cells:
                        q=f'{BOOKS[section["book_id"]]}《{section["title"]}》第{n}行表格中，“{paragraph_scope(cell)}”单元格怎样记载？'
                        ids.append(c.add(q,cell,[uid],task='literal_source_table_cell',fmt='chart_application',context='只读原表该单元格；不把本位、示例落宫和现代重排混用。',mode='literal_table_reading'))
                else:
                    q=f'{BOOKS[section["book_id"]]}《{section["title"]}》中，“{paragraph_scope(quote)}”这一条具体怎样说？'
                    ids=[c.add(q,quote,[uid],task='recovered_short_source_rule',mode='source_rule_explanation')]
                entry.update(state='recovered_source_teaching',source_ids=[uid],task_ids=ids)
                residual.append({'section_id':sid,'line':n,'original':line,'task_ids':ids})
            report.append(entry)
    return report,residual


def validate_complete(c,steps,line_report):
    if set(c.dispositions)!={u['review_key'] for u in c.inventory}:raise ValueError('Unaccounted general source')
    if len(steps)!=1008 or len({d['case_id'] for d in c.pack['dossiers']})!=194:raise ValueError('Incomplete original cases')
    if any(not s['task_ids'] for s in steps):raise ValueError('Author analysis lost')
    if len(c.dispatches)!=sum(len(r.get('typed_groups',[])) for r in c.reviews):raise ValueError('Undispatched group')
    ids={r['id'] for r in c.rows};prompts={}
    for key,v in c.dispositions.items():
        if 'pending' in v['state']:raise ValueError('Pending coverage: '+key)
        if any(r not in ids for r in v['task_ids']):raise ValueError('Dead coverage task')
        if v['state'] not in ('editorial_source_note','structure_heading','reading_scaffolding') and not v['task_ids']:raise ValueError('Empty knowledge mapping')
    for r in c.rows:
        for uid in r['source_ids']:
            if uid not in c.units or c.units[uid]['book_id'] not in BOOKS:raise ValueError('Invalid source')
        if any(c.case_splits[cid]!='train' for cid in r['case_ids']) and r['split']=='train':raise ValueError('Case holdout leakage')
        if r['messages'][-1]['content']!=r['answer']:raise ValueError('Wrong target')
        prompt=json.dumps(r['messages'][:-1],ensure_ascii=False,sort_keys=True)
        if prompt in prompts and prompts[prompt]!=r['answer']:raise ValueError('Conflicting identical prompt')
        prompts[prompt]=r['answer']
        if any(x in r['answer'] for x in ('HEALTH_V9_V11','STRENGTH_200','candidate_five_grade_quantization')):raise ValueError('Legacy scoring')
    return {'general_units_accounted':len(c.dispositions),'general_units_total':len(c.inventory),'unaccounted_general_units':0,
      'dispositions':dict(Counter(x['state'] for x in c.dispositions.values())),
      'declared_groups':len(c.dispatches),'dispatched_groups':len(c.dispatches),'unknown_strategy_skipped':False,
      'original_cases':194,'original_author_steps':len(steps),'source_nonblank_lines_accounted':len(line_report),
      'line_dispositions':dict(Counter(x['state'] for x in line_report)),
      'core_tasks':len(c.rows),'formats':dict(Counter(r['format'] for r in c.rows)),
      'splits':dict(Counter(r['split'] for r in c.rows)),'case_holdout_leakage':0,
      'all_knowledge_learned_by_model':False,'semantic_infallibility_claimed':False,
      'coverage_definition':'Each supplied source unit is dispositioned; teacher tasks retain source conditions. This is not an independent prediction or completeness-of-human-interpretation score.'}


def build(review_inputs,v4_pack,database,coordinates,output):
    if sha(Path(database).read_bytes())!=SOURCE_SHA256:raise ValueError('Immutable source database changed')
    inputs=load(review_inputs);reviews=inputs['reviews'];declared_strategies(reviews)
    with sqlite3.connect('file:'+str(Path(database).resolve())+'?mode=ro',uri=True) as db:
        db.row_factory=sqlite3.Row;sections={r['section_id']:dict(r) for r in db.execute('SELECT * FROM sections')}
    c=Curriculum(load(v4_pack),inputs['inventory'],reviews,sections,load(coordinates))
    c.semantic_overrides=inputs.get('semantic_overrides',{})
    c.case_correction_required=set(inputs.get('case_correction_required',[]))
    import_v4_targets(c)
    for review in reviews:
        for group in review.get('typed_groups',[]):c.dispatch(group)
    complete_general_units(c)
    for item in inputs.get('conflict_lessons',[]):c.add(item['q'],item['a'],item['refs'],task='source_difference_correction',fmt='conditional_dialogue',mode='source_version_contrast')
    steps=add_author_steps(c)
    chart_cells=add_full_chart_cell_tasks(c)
    case_paragraphs=add_case_source_paragraphs(c,chart_cells)
    lines,residual=add_line_accounting(c)
    summary=validate_complete(c,steps,lines)
    summary['schema']=SCHEMA
    summary['production_enabled']=False
    summary['literal_chart_cells_taught']=len(chart_cells)
    summary['case_source_paragraphs_accounted']=len(case_paragraphs)
    summary['supplementary_case_lessons']=sum(x['state']=='supplementary_source_lesson' for x in case_paragraphs)
    summary['source_checks']=audit_source_roundtrip(c)
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    fragments=c.units.pop('_teaching_fragments',{})
    pack={'schema':SCHEMA,'source_sha256':SOURCE_SHA256,'records':c.rows,'units':c.units,
          'dossiers':c.pack['dossiers'],'review_notes':c.pack['review_notes'],'summary':summary,
          'case_splits':c.case_splits}
    dump(output/'pack.json',pack);dump(output/'summary.json',summary)
    dump(output/'general_coverage.json',[{'key':k,**v} for k,v in sorted(c.dispositions.items())])
    dump(output/'author_step_coverage.json',steps);dump(output/'source_line_coverage.json',lines);dump(output/'chart_cell_coverage.json',chart_cells);dump(output/'case_paragraph_coverage.json',case_paragraphs)
    dump(output/'teaching_fragments.json',fragments);dump(output/'strategy_dispatch.json',c.dispatches)
    dump(output/'recovered_lines_review.json',residual)
    dump(output/'source_uncertainties.json',inputs.get('source_uncertainties',[]))
    return summary


def add_full_chart_cell_tasks(c):
    coverage=[]
    for d in c.pack['dossiers']:
        cid=d['case_id']
        for cast,cells in [('primary',d['primary_printed_chart']),*d['additional_printed_charts'].items()]:
            board='\n'.join(f"{cell['palace_label_raw']}：神{cell['deity_raw']}，门行{cell['door_position_raw']}，星行{cell['star_position_raw']}" for cell in cells)
            for cell in cells:
                matches=[u['id'] for u in c.units.values() if isinstance(u,dict) and u.get('kind')=='original_printed_chart_cell'
                         and cid in u.get('case_ids',[]) and u.get('lines')==[cell['source_line'],cell['source_line']]]
                if not matches:
                    # Existing transcription source IDs explicitly include cast and palace.
                    possible=f'chart:{cid}:{cast}:p{cell["palace"]}'
                    if possible in c.units:matches=[possible]
                if not matches:
                    source=[u['id'] for u in c.units.values() if isinstance(u,dict) and u.get('book_id') in BOOKS and
                            cid in u.get('case_ids',[]) and u.get('lines') and u['lines'][0]<=cell['source_line']<=u['lines'][1]]
                    matches=source[:1]
                if not matches:raise ValueError('Chart cell without original source: '+cid+':'+cast)
                q=f'读取案例{cid}的{cast}原书抄盘：{cell["palace_label_raw"]}的神、门行、星行分别记什么？'
                a=f'神：{cell["deity_raw"]}；门行：{cell["door_position_raw"]}；星行：{cell["star_position_raw"]}。'
                rid=c.add(q,a,matches,task='all_fields_literal_chart_cell',fmt='chart_application',case_id=cid,
                          mode='literal_source_transcription_not_recast',context='仅按所给原书字面读取，缺损和原书错局不自行修补。\n'+board)
                coverage.append({'case_id':cid,'cast':cast,'palace':cell['palace'],'source_ids':matches,'task_id':rid})
    return coverage


def source_paragraphs(lines,lo,hi):
    """Separate layout from prose even when OCR omitted the blank line."""
    chunks=[];current=[];start=lo;kind=None
    for line_no in range(lo,min(hi,len(lines))+1):
        text=lines[line_no-1]
        this_kind=('layout' if re.match(r'^\s*(?:[|│+┌├└┬]|[-─]{3})',text) else 'prose') if text.strip() else None
        if current and this_kind!=kind:
            chunks.append((start,line_no-1,'\n'.join(current),kind));current=[]
        if this_kind:
            if not current:start=line_no
            current.append(text)
        kind=this_kind
    if current:chunks.append((start,min(hi,len(lines)),'\n'.join(current),kind))
    return chunks


def add_case_source_paragraphs(c,chart_cells=()):
    """Catch teacher comments and narrative facts absent from the 1008-step registry.

    These are explicitly attributed source-study tasks. Mixed narrative is not
    labelled initial information or a correct teacher rule by keyword guessing.
    """
    report=[];notes={d['case_id']:c.pack['review_notes'][i] for i,d in enumerate(c.pack['dossiers'])}
    number={d['case_id']:i+1 for i,d in enumerate(c.pack['dossiers'])}
    seen=set()
    target_index=defaultdict(list)
    for r in c.rows:
        for cid in r.get('case_ids',[]):target_index[cid].append((r['id'],compact(r['answer'])))
    for sid,spans in sorted(c.ranges.items()):
        lines=c.sections[sid]['original_text'].splitlines()
        for lo,hi,cid in spans:
            for start,end,text,kind in source_paragraphs(lines,lo,hi):
                identity=(sid,start,end,cid)
                if identity in seen:continue
                seen.add(identity)
                row={'section_id':sid,'lines':[start,end],'case_id':cid,'task_ids':[]}
                if kind=='layout':
                    linked=[]
                    for cell in chart_cells:
                        if cell['case_id']!=cid:continue
                        for source in cell['source_ids']:
                            u=c.units[source]
                            if u.get('section_id')==sid and u.get('lines') and max(start,u['lines'][0])<=min(end,u['lines'][1]):
                                linked.append(cell['task_id'])
                    if linked:
                        row.update(state='printed_chart_cell_tasks',task_ids=sorted(set(linked)))
                    else:
                        # A diagram absent from the parsed chart adapter is still
                        # taught literally. Never invent its missing layer names.
                        uid=c.raw(sid,start,end);ids=[]
                        for offset,line in enumerate(text.splitlines()):
                            if not line.lstrip().startswith(('|','│')):continue
                            for col,cell in enumerate((x.strip() for x in re.split('[|│]',line) if x.strip()),1):
                                q=f'案例{cid}的原书第{start+offset}行文字表，第{col}格原样记什么？'
                                ids.append(c.add(q,cell,[uid],task='unparsed_case_table_literal_cell',fmt='chart_application',
                                    case_id=cid,context='仅按此原表行读取，不擅自指定层次或补造符号。\n'+line,mode='literal_source_transcription_not_recast'))
                        row.update(state='unparsed_layout_literal_reading' if ids else 'layout_border_only',task_ids=ids)
                    report.append(row);continue
                if re.fullmatch(r'(?:例[一二三四五六七八九十0-9]+[、.．：:]?|分析[：:]?|解说[：:]?|[（(]?[一二三四五六七八九十0-9]+[)）])',text.strip()):
                    row['state']='case_structure_caption';report.append(row);continue
                needle=compact(text)
                existing=[rid for rid,target in target_index[cid] if needle in target]
                if existing:
                    row.update(state='literal_existing_case_target',task_ids=existing);report.append(row);continue
                uid=c.raw(sid,start,end);u=c.units[uid]
                preceding='\n'.join(lines[lo-1:end])
                teacher=bool(re.search(r'张志春[按评批]|张老师[按评批]',preceding))
                actor='明确老师按语' if teacher else '原书叙述或引述，未擅自认作老师观点'
                ids=[]
                for n,part in enumerate(semantic_chunks(text,260),1):
                    scope=paragraph_scope(part)
                    q=f'复盘原书案例{cid}：第{start}—{end}行关于“{scope}”记述了什么？'
                    if n>1:q+=f'（第{n}段）'
                    context='背景与信息披露：'+notes[cid]['context']+'\n资料身份：'+actor+'。本题是来源复盘，不是事前预测输入。'
                    answer=part.strip()
                    if number[cid] in getattr(c,'case_correction_required',set()):
                        q+='结合本例核对信息，哪些地方不能直接作为正确结论沿用？'
                        answer='原段：'+answer+'\n核对：'+notes[cid]['review_note']
                    rid=c.add(q,answer,[uid],task='supplementary_attributed_case_source',fmt='complete_case',context=context,
                              case_id=cid,mode='source_narrative_or_commentary_not_initial_prediction',review='teacher_identity_explicit' if teacher else 'source_actor_not_assumed')
                    ids.append(rid);target_index[cid].append((rid,compact(answer)))
                row.update(state='supplementary_source_lesson',task_ids=ids,speaker='explicit_teacher_commentary' if teacher else 'source_actor_unspecified')
                report.append(row)
    return report


def audit_source_roundtrip(c):
    counts=Counter()
    for uid,u in c.units.items():
        if uid=='_teaching_fragments':continue
        status=u.get('match_status')
        if status=='sqlite_original_transcription':
            counts['separately_labelled_sqlite_transcription']+=1;continue
        sid=u.get('section_id');span=u.get('lines')
        if sid not in c.sections or not span:raise ValueError('Source coordinates missing: '+uid)
        s=c.sections[sid];text='\n'.join(s['original_text'].splitlines()[span[0]-1:span[1]])
        if u.get('source_sha256')!=s['sha256'] or compact(u['original_quote']) not in compact(text):
            raise ValueError('Source quote/coordinate mismatch: '+uid)
        counts['located_literal_or_whitespace_only']+=1
    return dict(counts)
