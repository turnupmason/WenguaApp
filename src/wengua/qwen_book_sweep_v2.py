"""Predeclared adaptive stages: structure/context, LR, dropout/warmup.

All decisions use the same source-group-held-out format NLL. Final test is
frozen until every stage ends. Each distinct configuration starts fresh.
"""
from __future__ import annotations

import csv
import gc
import html
import itertools
import math
from pathlib import Path
import re
import time

from . import qwen_book_continuous_v1 as engine
from .qwen_book_continuous_v1 import book

SCHEMA='wengua_book_sweep_v2'
SPEC=book.ROOT/'configs/qwen14b_book_sweep_v2.json'
SHARED=frozenset(('num_train_epochs','gradient_accumulation_steps','save_steps','save_total_limit','validation_rows',
    'validation_generation_rows','test_generation_rows','eval_max_new_tokens','smoke_steps','patience','minimum_loss_improvement','seed'))


def plan(spec,base=None):
    if set(spec)!={'schema','contexts','structures','shared_overrides','learning_rates','dropouts','warmup_ratios'} or spec['schema']!=SCHEMA:
        raise ValueError('Unknown staged experiment schema/key')
    if set(spec['shared_overrides'])-SHARED:raise ValueError('Unsupported shared training override')
    contexts=spec['contexts']
    if not contexts or len(contexts)>2 or len(set(contexts))!=len(contexts) or any(x not in (512,1024,2048,4096) for x in contexts):
        raise ValueError('One or two explicit supported contexts required')
    if not 1<=len(spec['structures'])<=4:raise ValueError('One to four structures required')
    c=dict(base or engine.base_config());c.update(spec['shared_overrides'])
    configs=[]
    for context,structure in itertools.product(contexts,spec['structures']):
        if set(structure)!={'lora_r','target_modules'}:raise ValueError('Only rank and explicit modules define a structure')
        cfg=dict(c,**structure,max_seq_length=context,inference_max_context=context,lora_alpha=2*structure['lora_r'])
        engine.validate(cfg)
        if cfg in configs:raise ValueError('Duplicate structure/context')
        configs.append(cfg)
    for key,lo,hi in [('learning_rates',0,0.001),('dropouts',0,0.2),('warmup_ratios',0,0.2)]:
        values=spec[key]
        if not values or len(values)>4 or len(set(values))!=len(values) or any(not isinstance(x,(int,float)) or not lo<=x<=hi for x in values):
            raise ValueError('Invalid bounded '+key)
    if 0 in spec['learning_rates']:raise ValueError('Learning rate must be positive')
    upper=len(configs)+len(spec['learning_rates'])-int(c['learning_rate'] in spec['learning_rates'])+len(spec['dropouts'])*len(spec['warmup_ratios'])-int(c['lora_dropout'] in spec['dropouts'] and c['warmup_ratio'] in spec['warmup_ratios'])
    if upper>28:raise ValueError('At most 28 planned stage candidates')
    return {'structures':configs,'maximum_distinct_trials':upper,
        'stages':['structure_context','learning_rate','dropout_warmup'],'reference_context':min(contexts),
        'selection_basis':'common_validation_macro_format_language_loss','test_used_for_selection':False,'training_started':False}


def trial_id(c):return 'r'+str(c['lora_r'])+'_'+str(c['max_seq_length'])+'_'+book.digest(book.dumps(c))[:12]


def best(rows):
    candidates=[r for r in rows if r['state']=='complete' and math.isfinite(r.get('validation_loss',math.inf))]
    return min(candidates,key=lambda r:(r['validation_loss'],r['id'])) if candidates else None


def review_generations(job):
    """Observable diagnostics, never an LLM judge or a fabricated expert score."""
    records=[]
    for path in sorted((job/'generations').glob('*.jsonl')):
        if 'validation' not in path.name:continue
        for line in path.read_text(encoding='utf8').splitlines():
            try:records.append(book.json.loads(line))
            except ValueError:continue
    summary={}
    names={'坎':1,'坤':2,'震':3,'巽':4,'中':5,'乾':6,'兑':7,'艮':8,'离':9}
    def palaces(text):
        out={int(x) for x in re.findall(r'([1-9])宫',text)}
        for name,num in names.items():
            if re.search(name+r'[一二三四五六七八九1-9]?宫',text):out.add(num)
        return sorted(out)
    for r in records:
        key=r['variant']+' / '+r['task'];row=summary.setdefault(key,{'rows':0,'empty':0,'token_limit':0,'palace_checks':0,'palace_set_matches':0})
        row['rows']+=1;row['empty']+=not bool(r['answer'].strip());row['token_limit']+=r['reached_token_limit']
        if r['task']=='printed_star_location':
            expected=palaces(r['expected'])
            if expected:row['palace_checks']+=1;row['palace_set_matches']+=palaces(r['answer'])==expected
    proof={'by_variant_and_task':summary,'professional_correctness_verified':False,
        'warning':'Palace set extraction cannot interpret negation; inspect raw answers and sources. Not used for selection.'}
    book.atomic_json(job/'answer_review.json',proof);return proof


def render(root,status):
    rows=list(status.get('trials',{}).values());e=lambda x:html.escape(str(x))
    fields=['id','stage','state','context','lora_r','modules','learning_rate','lora_dropout','warmup_ratio',
        'selected_epoch','validation_loss','per_format_loss','steps','maximum_steps','trainable_parameters','peak_reserved_gib','adapter','last_optimizer_checkpoint','error']
    with (root/'results.csv').open('w',encoding='utf-8-sig',newline='') as f:
        out=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');out.writeheader();out.writerows(rows)
    body=['<!doctype html><html lang="zh"><meta charset="utf-8"><title>问卦连续训练与分阶段调参</title>',
        '<style>body{font:16px sans-serif;margin:30px;line-height:1.6}td,th{border:1px solid #ccc;padding:8px}table{border-collapse:collapse}pre{white-space:pre-wrap;overflow-wrap:anywhere}</style>',
        '<h1>纯古籍连续训练 · 分阶段参数实验</h1><p>状态：'+e(status.get('state'))+'</p>',
        '<p>顺序：覆盖与显存→结构/上下文→学习率→dropout/warmup→冻结候选→最后测试。每组官方基模独立开始；组内跨epoch保持同一Adam和余弦计划。共用验证题、四类格式等权语言loss，不是专业正确率。</p>',
        '<p>点实验进入全部epoch回答、原模对照、作者参照与出处。条件题、纠错、完整案例应人工核对；作者资料辅助复盘不冒充未见盘预测。低dropout、更多轮次和更多参数均不保证专业能力。</p>',
        '<h2>上下文覆盖与token占比</h2><pre>'+e(book.json.dumps(status.get('coverage',{}),ensure_ascii=False,indent=2))+'</pre>',
        '<h2>各组实验</h2><table><tr>'+''.join('<th>'+e(x)+'</th>' for x in ('实验','阶段','状态','参数','最佳epoch','格式等权loss','各格式loss','步数','峰值GiB'))+'</tr>']
    for r in rows:
        body.append('<tr><td><a href="trials/'+e(r['id'])+'/results.html">'+e(r['id'])+'</a></td>'+''.join('<td>'+e(x)+'</td>' for x in
            (r.get('stage'),r['state'],{k:r.get(k) for k in ('context','lora_r','modules','learning_rate','lora_dropout','warmup_ratio')},
             r.get('selected_epoch'),r.get('validation_loss'),r.get('per_format_loss'),r.get('steps'),r.get('peak_reserved_gib')))+'</tr>')
        if r.get('error'):body.append('<tr><td colspan="9">'+e(r['error'])+'</td></tr>')
    body+=['</table><h2>逐阶段决策与最后测试</h2><pre>'+e(book.json.dumps(status,ensure_ascii=False,indent=2))+'</pre></html>']
    (root/'results.html').write_text(''.join(body),encoding='utf8');book.atomic_json(root/'summary.json',status)


def run(output,spec,deadline,*,resume=False,resume_from_checkpoint=None,cpu_factory=None,tokenizer=None,pack=None,base=None,extra_callbacks=()):
    setup=plan(spec,base);root=book.private_output(output)
    contract={'schema':SCHEMA,'spec':spec,'plan':setup,'code_sha256':engine.code_hashes(),'source_database_sha256':book.SOURCE_SHA256,
        'coordinates_sha256':book.digest(book.COORDINATES.read_text(encoding='utf8')),'initialization':'official_base_per_configuration',
        'test_used_for_selection':False,'quantization':'NF4_double_quantization'}
    if root.exists():
        if not resume or not (root/'sweep_contract.json').exists() or book.read_json(root/'sweep_contract.json')!=contract:
            raise ValueError('Staged sweep contract changed or legacy output; exact --resume or new output required')
    else:root.mkdir(parents=True);book.atomic_json(root/'sweep_contract.json',contract)
    with book.job_lock(root/'sweep.lock'),book.keep_awake():
        statusfile=root/'sweep_status.json';status=book.read_json(statusfile) if statusfile.exists() else {'state':'preparing','trials':{},'coverage':{},'decisions':{}}
        owner=None
        if resume_from_checkpoint is not None:
            if not resume:raise ValueError('Explicit checkpoint requires --resume')
            cp=Path(resume_from_checkpoint).resolve()
            if not cp.is_relative_to((root/'trials').resolve()):raise ValueError('Checkpoint belongs to another sweep')
            owner=cp.relative_to(root/'trials').parts[0]
            if owner not in status['trials']:raise ValueError('Unknown trial checkpoint')
            engine.explicit_checkpoint(root/'trials'/owner,cp)
            if (root/'selected_trial.json').exists():raise ValueError('Selection frozen; no checkpoint replay')
            if status['trials'][owner]['state']=='oom':raise ValueError('OOM trial preserved; retry in a new experiment after freeing memory')
        if status['state']=='complete':book.checked_adapter(status['selection']['adapter']);render(root,status);return status
        def save():book.atomic_json(statusfile,status);render(root,status)
        def evaluate(c,phase,probe=False):
            tid=trial_id(c);prior=status['trials'].get(tid,{})
            if prior.get('state')=='oom':return prior
            if probe and prior.get('probe_state')=='complete':return prior|{'state':'feasible'}
            if not probe and prior.get('state')=='complete':book.checked_adapter(prior['adapter']);return prior
            if time.time()>=deadline-240:return {'state':'paused_deadline'}
            job=engine.open_job(root/'trials'/tid,c,resume=True)
            status['active_trial']=tid;status['state']='memory_probes' if probe else phase
            row=prior|{'id':tid,'stage':phase,'config':c,'state':'probing' if probe else 'training',
                'context':c['max_seq_length'],'lora_r':c['lora_r'],'modules':c['target_modules'],
                'learning_rate':c['learning_rate'],'lora_dropout':c['lora_dropout'],'warmup_ratio':c['warmup_ratio']}
            status['trials'][tid]=row;save()
            try:
                if cpu_factory is None:
                    from .qwen_finetune import environment_report
                    doctor=environment_report(c);book.atomic_json(job/'doctor.json',doctor)
                    if doctor['training_preflight']['status']!='ready_for_smoke_test':raise RuntimeError(doctor['training_preflight']['reason'])
                proof=engine.prepare_shared(root,job,c,reference_context=setup['reference_context'],tokenizer=tokenizer,pack=pack)
                status['coverage'][str(c['max_seq_length'])]=proof
                if probe:
                    with book.job_lock(job/'run.lock'):result=engine.fit(job,c,deadline,probe=True,cpu_factory=cpu_factory)
                    row.update(state='feasible' if result['state']=='complete' else 'paused_probe',probe_state=result['state'],
                        trainable_parameters=result.get('trainable_parameters'),probe_peak_reserved_gib=result.get('peak_reserved_gib'))
                else:
                    # Tuned variants also get a new longest-sample short test.
                    smoke=job/'smoke/stage_status.json'
                    if not smoke.exists() or book.read_json(smoke)['state']!='complete':
                        with book.job_lock(job/'run.lock'):result=engine.fit(job,c,deadline,probe=True,cpu_factory=cpu_factory)
                        if result['state']!='complete':row['state']='paused_probe';save();return row
                    result=engine.run_trial(job,c,deadline,cpu_factory=cpu_factory,extra_callbacks=extra_callbacks,
                        resume_from_checkpoint=resume_from_checkpoint if tid==owner else None)
                    row.update({k:result[k] for k in ('state','selected_epoch','validation_loss','per_format_loss','steps','adapter',
                        'last_optimizer_checkpoint','trainable_parameters','peak_reserved_gib','runtime_seconds') if k in result})
                    row['maximum_steps']=result.get('planned_steps');row['answer_review']=review_generations(job)
                return row
            except Exception as error:
                if not book.is_cuda_oom(error):raise
                row.update(state='oom',error=str(error)[:2000],all_outputs_preserved=True)
                error.__traceback__=None;error.__context__=None;gc.collect()
                if cpu_factory is None:
                    import torch
                    torch.cuda.empty_cache()
                return row
            finally:save()
        try:
            status.pop('error',None)
            for c in setup['structures']:
                result=evaluate(c,'structure_context',probe=True)
                if result['state'] not in ('feasible','complete','oom'):status['state']='paused_probes';return status
            for phase in ('structure_context','learning_rate','dropout_warmup'):
                if phase=='learning_rate':
                    chosen=status['decisions']['structure_context']['config']
                    configs=[dict(chosen,learning_rate=rate) for rate in spec['learning_rates']]+[chosen]
                elif phase=='dropout_warmup':
                    chosen=status['decisions']['learning_rate']['config']
                    configs=[dict(chosen,lora_dropout=drop,warmup_ratio=warm) for drop,warm in itertools.product(spec['dropouts'],spec['warmup_ratios'])]+[chosen]
                else:configs=setup['structures']
                ids=list(dict.fromkeys(trial_id(c) for c in configs))
                for c in configs:
                    result=evaluate(c,phase)
                    if result['state'] not in ('complete','oom'):status['state']='paused_trial';return status
                winner=best([status['trials'][tid] for tid in ids])
                if winner is None:status['state']='no_feasible_trial';return status
                decision={'id':winner['id'],'config':winner['config'],'validation_loss':winner['validation_loss'],
                    'considered_trials':ids,'test_used_for_selection':False,'selection_basis':'macro_format_language_loss'}
                if phase in status['decisions'] and status['decisions'][phase]!=decision:raise ValueError('Frozen stage decision changed')
                status['decisions'][phase]=decision;save()
            choice=status['trials'][status['decisions']['dropout_warmup']['id']]
            selection={k:choice[k] for k in ('id','adapter','selected_epoch','validation_loss','per_format_loss')}
            selection['test_used_for_selection']=False;frozen=root/'selected_trial.json'
            if frozen.exists() and book.read_json(frozen)!=selection:raise ValueError('Frozen final selection mismatch')
            book.atomic_json(frozen,selection);status['selection']=selection;status['state']='final_test';save()
            finalpath=root/'final_test.json';job=root/'trials'/choice['id']
            if finalpath.exists() and book.read_json(finalpath)['state']=='complete':final=book.read_json(finalpath)
            else:
                with book.job_lock(job/'run.lock'):
                    final=book.final_test(job,choice['config'],{'adapter':choice['adapter'],'cycle':choice['selected_epoch']},deadline,cpu_factory=cpu_factory)
                final['trial_id']=choice['id'];book.atomic_json(finalpath,final)
            status['final_test']=final;status['state']='complete' if final['state']=='complete' else 'paused_final_test'
            child=book.read_json(job/'job_status.json');child['final_test']=final;engine.render(job,child)
            return status
        except BaseException as error:
            status['state']='interrupted' if isinstance(error,KeyboardInterrupt) else 'failed'
            status['error']={'type':type(error).__name__,'message':str(error)[:2000]};raise
        finally:save()
