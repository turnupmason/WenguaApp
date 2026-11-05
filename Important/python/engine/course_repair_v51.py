"""Evidence-visible course revision. Original V4/V5 packs are never overwritten.

Historical review is explicitly distinguished from chart reasoning. Source
summaries and reading exercises are not scored as prospective predictions.
"""
from copy import deepcopy
from collections import Counter
import re
from pathlib import Path
from .course_complete_v5 import sha,load,dump,SYSTEM,semantic_chunks
from . import course_training_v5 as previous

SCHEMA='wengua_evidence_visible_course_v51'
BOOK_NAMES={'shenqi':'神奇之门','kaiwu':'开悟之门'}
PALACES={1:'坎一宫',2:'坤二宫',3:'震三宫',4:'巽四宫',5:'中五宫',6:'乾六宫',7:'兑七宫',8:'艮八宫',9:'离九宫'}
GROUND_TASKS={'author_step_attributed_review','supplementary_attributed_case_source'}
AGGREGATE_TASKS={'author_analysis_review','chronology_review','case_error_correction'}


def prose_only(text):
    """Remove only table layout lines. Keep all prose, including short feedback."""
    def layout(line):
        clean=line.strip()
        if not clean:return True
        if clean.startswith(('|','│','┌','└','├','+---')):return True
        if clean.startswith('─') and not any(c in clean for c in '。；'):return True
        if clean.count('│')>=2 and not any(c in clean for c in '。；'):return True
        return False
    return '\n'.join(line for line in text.splitlines() if not layout(line))



def heading_only(text):
    text=text.strip()
    # A numbered analysis paragraph is substantive, even when it starts '(1)'.
    if len(text)>40 or any(c in text for c in '。；，'):return False
    return bool(re.fullmatch(r'(实例[一二三四五六七八九十0-9]+[：:].*|[（(]例[一二三四五六七八九十0-9]+[）)].*|分析[：:]?|预测[：:]?|反馈[：:]?)',text))


def source_block(units):
    return '\n\n'.join(u['id']+'\n'+u['original_quote'] for u in units)


def fits(row,tokenizer):
    from .qwen_book_loop_v3 import target_views,encode,generation_rows
    if any(encode(v,tokenizer,4096)[0] is None for v in target_views(row,0)):return False
    return not generation_rows([row],tokenizer,{'eval_max_new_tokens':1024,'inference_max_context':4096})[1]


def set_turns(row,messages):
    row['messages']=messages;row['answer']=messages[-1]['content']
    row['question']=next(m['content'] for m in messages if m['role']=='user')


def repair(pack,decisions,tokenizer):
    """Every old row receives a disposition; additions require located sources."""
    previous.validate_rows(pack['records'],pack['units'],pack['case_splits'])
    out=deepcopy(pack);out['schema']=SCHEMA;records=[];audit=[]
    notes={d['case_id']:n for d,n in zip(pack['dossiers'],pack['review_notes'])}
    fixes=decisions['target_fixes'];seen=set()
    for original in pack['records']:
        r=deepcopy(original);oldid=r['id'];changes=[];units=[out['units'][u] for u in r['source_ids']]
        r['id']='v51:'+sha(oldid)[:20];r['parent_task_id']=oldid
        if oldid in fixes:
            fix=fixes[oldid]
            if fix['old_answer']!=r['answer']:raise ValueError('Target correction precondition changed')
            r['answer']=fix['answer'];r['messages'][-1]['content']=r['answer'];changes.append(fix['reason']);seen.add(oldid)
        # Scope is part of the actual prompt, not merely external metadata.
        scopes=sorted({f'《{BOOK_NAMES[u["book_id"]]}》{u.get("chapter","")}' for u in units})
        r['messages'][0]={'role':'system','content':SYSTEM}
        r['messages'][1]['content']='来源范围：'+'；'.join(scopes)+'。\n'+r['messages'][1]['content']
        if r['task']=='printed_star_location':
            # Preserve the existing printed chart selection (some questions
            # concern a supplementary chart). Normalize only its palace label.
            label=re.match(r'([坎坤震巽中乾兑艮离][一二三四五六七八九1-9])宫?',r['answer'])
            if not label:raise ValueError('Non-palace printed star target')
            r['answer']=label[1]+'宫。';r['messages'][-1]['content']=r['answer']
            changes.append('palace_only_target_normalized_without_extra_raw_columns')
        if r['task'] in GROUND_TASKS:
            if r['task']=='supplementary_attributed_case_source' and heading_only(r['answer']):
                audit.append({'parent_task_id':oldid,'state':'provenance_only_heading','source_ids':r['source_ids']});continue
            r['messages'][1]['content']+='\n本题给出的原书证据（历史复盘，非事前已知）：\n'+source_block(units)
            r['source_mode']='evidence_visible_historical_reading_not_independent_prediction'
            changes.append('literal_evidence_added_to_model_input')
        elif r['task'] in AGGREGATE_TASKS:
            full=[u for u in units if u['id'].startswith('review:')]
            if not full:raise ValueError('Case aggregate lacks full source')
            text='\n\n'.join(u['id']+'\n'+prose_only(u['original_quote']) for u in full)
            r['messages'][1]['content']=('来源范围：'+'；'.join(scopes)+'。\n'+r['question']+'\n案例编号：'+r['case_id']+
                '\n以下为原书完整叙述的正文（表格另存原盘；包含后续回访，仅作复盘）：\n'+text)
            r['source_mode']='evidence_visible_full_case_retrospective_review'
            changes.append('missing_original_narrative_and_feedback_supplied')
            if not fits(r,tokenizer):
                # Long raw cases remain intact in the source archive and their
                # paragraph/step tasks. Do not cut the end or hide exclusions.
                n=notes[r['case_id']]
                r['messages'][1]['content']=('来源范围：'+'；'.join(scopes)+'。\n'+r['question']+'\n案例编号：'+r['case_id']+
                    '\n原案核对摘要（整理文字，非原书逐字引文；含事后反馈，仅练来源复盘）：\n'+
                    '\n'.join(k+'：'+n[k] for k in ('context','result','reason','timing_and_feedback','review_note')))
                r['source_mode']='reviewed_case_summary_reading_not_full_chart_prediction'
                changes.append('long_full_prose_preserved_in_archive_and_paragraph_tasks_summary_reading_only')
        set_turns(r,r['messages'])
        if not fits(r,tokenizer):
            # Explicitly replace an overlong reading target by complete source
            # paragraphs. No factual target is truncated or silently excluded.
            if r['task'] not in GROUND_TASKS:raise ValueError('Needs semantic revision: '+oldid)
            audit.append({'parent_task_id':oldid,'state':'long_reading_replaced_by_complete_source_chunks','source_ids':r['source_ids']})
            for u in units:
                for i,chunk in enumerate(semantic_chunks(u['original_quote'],500)):
                    x=deepcopy(r);x['id']+=':'+str(i)+':'+sha(u['id'])[:8]
                    question='按给出的原书片段，准确转述这段记载；保留人物、条件及前后时序。'
                    set_turns(x,[{'role':'system','content':SYSTEM},{'role':'user','content':question+'\n原书片段：\n'+chunk},{'role':'assistant','content':chunk}])
                    x['source_ids']=[u['id']];x['task']='complete_source_chunk_reading';x['source_mode']='literal_source_reading_not_reasoning'
                    if not fits(x,tokenizer):raise ValueError('Indivisible source requires manual review: '+oldid)
                    records.append(x)
            continue
        records.append(r);audit.append({'parent_task_id':oldid,'state':'revised' if changes else 'scope_added','changes':changes,'replacement_id':r['id']})
    if seen!=set(fixes):raise ValueError('Unapplied target corrections')
    # Curated additions are private source-derived decisions, never a second
    # model's invented rules or arbitrary numerical teachers.
    for n,item in enumerate(decisions['additions']):
        r=deepcopy(item);r['id']='v51:add:'+sha(str(n)+str(r))[:20]
        r.setdefault('case_id',None);r.setdefault('case_ids',[]);r.setdefault('split','train')
        r.setdefault('group','repair-rule:'+sha(str(r['source_ids']))[:16]);r.setdefault('format','conditional_dialogue')
        r.setdefault('source_mode','source_based_condition_contrast');r.setdefault('task','reviewed_condition_contrast')
        set_turns(r,[{'role':'system','content':SYSTEM},*r['turns']]);r.pop('turns')
        if not fits(r,tokenizer):raise ValueError('Addition too long: '+r['id'])
        records.append(r)
    if decisions.get('editorial_note_fix'):
        fix=decisions['editorial_note_fix'];index=next(i for i,d in enumerate(out['dossiers']) if d['case_id']==fix['case_id'])
        note=out['review_notes'][index]
        if fix['old'] not in note[fix['field']]:raise ValueError('Editorial note correction precondition changed')
        note[fix['field']]=note[fix['field']].replace(fix['old'],fix['new'])
    canonical={r['case_id']:r['group'] for r in pack['records'] if r['task']=='author_analysis_review'}
    for row in records:
        if row['case_id'] in canonical:row['group']=canonical[row['case_id']]
    seen_ids=[];seen_groups=set();seen_cases=set()
    for row in records:
        if any(row['case_id']==q['case_id'] and q['question'] in row['messages'][1]['content'] for q in decisions.get('seen_v4_questions',[])):
            seen_ids.append(row['id']);seen_groups.add(row['group'])
            seen_cases.update(row['case_ids'])
    out['selection_exclusions']={'seen_v4_diagnostic_ids':seen_ids,'groups':sorted(seen_groups),
        'case_ids':sorted(seen_cases),'policy':'Seen V4 responses and their case families are not future selection evidence'}
    out['records']=records
    out['summary']=pack['summary']|{'schema':SCHEMA,'core_tasks':len(records),'parent_v5_tasks':len(pack['records']),
        'revision_task_dispositions':dict(Counter(a['state'] for a in audit)),
        'task_counts':dict(Counter(r['task'] for r in records)),
        'formats':dict(Counter(r['format'] for r in records)),
        'splits':dict(Counter(r['split'] for r in records)),
        'coverage_definition':'All supplied V5 sources preserved; prior tasks mapped to revised teaching or explicit provenance-only headings. Historical reading is not unseen prediction.',
        'split_counts':dict(Counter(r['split'] for r in records)),
        'new_source_based_additions':len(decisions['additions']),
        'old_24_generation_questions_are_seen_diagnostics':True,'semantic_infallibility_claimed':False,
        'independent_prediction_ability_verified':False}
    previous.validate_rows(records,out['units'],out['case_splits'])
    return out,audit
