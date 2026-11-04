"""Independent fresh-base NF4 QLoRA trials on identical book-only data.

No test-set tuning, cross-trial adapter continuation or model-written teachers.
The selected model is a language-loss candidate, not a verified Qimen expert.
"""
from __future__ import annotations

import csv
import gc
import html
import itertools
import math
from pathlib import Path
import shutil
import time

from . import qwen_book_loop_v3 as loop

SCHEMA='wengua_book_sweep_v1'
SPEC=loop.ROOT/'configs/qwen14b_book_sweep_v1.json'
OPT_KEYS=frozenset(('lora_r','lora_alpha','lora_dropout','target_modules','learning_rate'))
SHARED_KEYS=frozenset(('cycles','max_seq_length','inference_max_context','eval_max_new_tokens',
    'gradient_accumulation_steps','max_steps_per_cycle','save_steps','validation_rows',
    'validation_generation_rows','test_generation_rows','smoke_steps','patience','minimum_loss_improvement','seed'))


def validate_config(c):
    # Reuse every standalone-loop bound without changing its public path API.
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        path=Path(tmp)/'config.json';loop.atomic_json(path,c);loop.load_config(path)
    if type(c['lora_r']) is not int or not 1<=c['lora_r']<=64:raise ValueError('LoRA rank must be 1..64')
    if type(c['lora_alpha']) is not int or not 1<=c['lora_alpha']<=256:raise ValueError('LoRA alpha must be 1..256')
    if not isinstance(c['lora_dropout'],(int,float)) or not 0<=c['lora_dropout']<=0.2:raise ValueError('Dropout must be 0..0.2')
    modules=c['target_modules']
    if not isinstance(modules,list) or not modules or len(set(modules))!=len(modules) or any(
        x not in ('q_proj','k_proj','v_proj','o_proj','gate_proj','up_proj','down_proj') for x in modules):
        raise ValueError('Explicit unique Qwen projection modules required')
    if c['max_seq_length']!=c['inference_max_context']:raise ValueError('Sweep requires one fixed train/inference context')
    return c


def expand_spec(spec,base=None):
    if set(spec)!={'schema','shared_overrides','grid','alpha_per_rank','include_reference_config'} or spec['schema']!=SCHEMA:
        raise ValueError('Invalid sweep schema or unknown key')
    if not isinstance(spec['shared_overrides'],dict) or set(spec['shared_overrides'])-SHARED_KEYS:raise ValueError('Unsupported shared override')
    if set(spec['grid'])!={'lora_r','learning_rate','target_modules','lora_dropout'}:raise ValueError('Unsupported grid axes')
    if type(spec['alpha_per_rank']) is not int or not 1<=spec['alpha_per_rank']<=4:raise ValueError('Invalid alpha/rank ratio')
    if type(spec['include_reference_config']) is not bool:raise ValueError('Reference flag must be boolean')
    base=dict(base or loop.load_config());base.update(spec['shared_overrides']);base['final_test_policy']='defer_to_sweep'
    axes=list(spec['grid']);values=[spec['grid'][k] for k in axes]
    if any(not isinstance(v,list) or not v for v in values):raise ValueError('Every grid axis must be a nonempty list')
    if math.prod(map(len,values))>32:raise ValueError('At most 32 grid trials per immutable experiment')
    configs=[]
    if spec['include_reference_config']:configs.append(validate_config(dict(base)))
    for valueset in itertools.product(*values):
        c=dict(base);c.update(zip(axes,valueset));c['lora_alpha']=c['lora_r']*spec['alpha_per_rank']
        validate_config(c)
        if c not in configs:configs.append(c)
    if len(configs)>32:raise ValueError('At most 32 total trials including the reference')
    trials=[]
    for i,c in enumerate(configs,1):
        suffix=loop.digest(loop.dumps(c))[:10]
        tid=f'trial_{i:02d}_r{c["lora_r"]}_{len(c["target_modules"])}proj_{suffix}'
        trials.append({'id':tid,'config':c,'reference':c==base})
    return trials


def data_signature(c):
    """Optimization axes cannot change samples, ordering, masking or evaluation."""
    return {k:v for k,v in c.items() if k not in OPT_KEYS}


def shared_prepare(root,job,c,*,tokenizer=None,pack=None):
    cache=root/'shared_data';cache.mkdir(exist_ok=True)
    receipt=cache/'prepared/receipt.json'
    if receipt.exists():
        original=loop.read_json(receipt)['config']
        if data_signature(original)!=data_signature(c):raise ValueError('Sweep data signature changed')
        meta=loop.prepare(cache,original)
    else:meta=loop.prepare(cache,c,tokenizer=tokenizer,pack=pack)
    target=job/'prepared'
    if (target/'receipt.json').exists():
        actual=loop.prepare(job,c)
        if actual['file_sha256']!=meta['file_sha256']:raise ValueError('Trial data differs from shared immutable data')
        return actual
    if (job/'smoke').exists() or any(job.glob('cycle_*')):raise ValueError('Trial data receipt missing after training began')
    for partial in (target,job/'prepared.pending'):
        if partial.exists():partial.rename(job/(partial.name+'.incomplete-'+str(time.time_ns())))
    pending=job/'prepared.pending'
    shutil.copytree(cache/'prepared',pending)
    copied=dict(meta,config=c);loop.atomic_json(pending/'receipt.json',copied)
    pending.rename(target)
    return loop.prepare(job,c)


def trial_result(tid,c,result):
    best,_=loop.select_best(result.get('cycles',[]),c)
    row={'id':tid,'state':result['state'],'parameters':{k:c[k] for k in sorted(OPT_KEYS)},
        'cycles_completed':sum(r.get('state')=='complete' for r in result.get('cycles',[])),
        'runtime_seconds':sum(r.get('runtime_seconds',0) for r in result.get('cycles',[])),
        'peak_reserved_gib':max((r.get('peak_reserved_gib',0) for r in result.get('cycles',[])),default=0),
        'last_optimizer_checkpoint':next((r.get('last_optimizer_checkpoint') for r in reversed(result.get('cycles',[])) if r.get('last_optimizer_checkpoint')),None),
        'professional_correctness_verified':False}
    if best:row.update(best_cycle=best['cycle'],validation_loss=best['validation_loss'],
        base_validation_loss=best.get('base_validation_loss'),adapter=best['adapter'])
    return row


def select_trial(rows):
    eligible=[r for r in rows if r['state']=='complete' and math.isfinite(r.get('validation_loss',math.inf))]
    return min(eligible,key=lambda r:(r['validation_loss'],r['id'])) if eligible else None


def render(root,status,trials):
    root.mkdir(parents=True,exist_ok=True);rows=status.get('trials',[])
    keys=('id','state','lora_r','lora_alpha','lora_dropout','target_modules','learning_rate',
        'best_cycle','validation_loss','base_validation_loss','cycles_completed','runtime_seconds','peak_reserved_gib','adapter','last_optimizer_checkpoint','error')
    with (root/'results.csv').open('w',encoding='utf-8-sig',newline='') as f:
        out=csv.DictWriter(f,fieldnames=keys,extrasaction='ignore');out.writeheader()
        for r in rows:out.writerow(r|r.get('parameters',{}))
    e=lambda value:html.escape(str(value))
    text=['<!doctype html><html lang="zh"><meta charset="utf-8"><title>问卦参数实验</title>',
        '<style>body{font:16px sans-serif;margin:28px;line-height:1.6}table{border-collapse:collapse}td,th{border:1px solid #ccc;padding:8px}pre{white-space:pre-wrap;overflow-wrap:anywhere}</style>',
        '<h1>纯古籍 QLoRA 参数实验</h1><p>状态：'+e(status.get('state'))+'；计划 '+str(len(trials))+' 个独立组合。</p>',
        '<p>所有组合使用相同数据、验证题、种子和上下文。每个组合从官方基模新建适配器。只用验证语言损失选候选，测试题在全部组合结束后只评一次所选模型。损失、字面相似度不代表专业正确率。</p>',
        '<p>点击实验名称查看各轮完整问题、原模回答、微调回答、原书依据和训练日志。未见盘与纠错题的专业表现仍须审阅，不能仅按损失认定训练到位。</p>',
        '<table><tr><th>组合</th><th>参数</th><th>状态</th><th>最佳轮</th><th>验证 loss</th><th>基模 loss</th><th>耗时秒</th><th>峰值显存 GiB</th></tr>']
    byid={r['id']:r for r in rows}
    for trial in trials:
        r=byid.get(trial['id'],{'state':'pending'});params={k:trial['config'][k] for k in sorted(OPT_KEYS)}
        text.append('<tr><td><a href="trials/'+e(trial['id'])+'/results.html">'+e(trial['id'])+'</a></td><td>'+e(params)+'</td>'+''.join(
            '<td>'+e(r.get(k,''))+'</td>' for k in ('state','best_cycle','validation_loss','base_validation_loss','runtime_seconds','peak_reserved_gib'))+'</tr>')
        if r.get('error'):text.append('<tr><td colspan="8">'+e(r['error'])+'</td></tr>')
    text.append('</table><pre>'+e(loop.dumps(status))+'</pre></html>')
    (root/'results.html').write_text(''.join(text),encoding='utf8');loop.atomic_json(root/'summary.json',status)


def run_sweep(output,spec,deadline,*,resume=False,resume_from_checkpoint=None,retry_oom=False,
              cpu_factory=None,tokenizer=None,pack=None,base=None,extra_callbacks=()):
    root=loop.private_output(output);trials=expand_spec(spec,base)
    contract={'schema':SCHEMA,'spec':spec,'trials':trials,'source_database_sha256':loop.SOURCE_SHA256,
        'coordinates_sha256':loop.digest(loop.COORDINATES.read_text(encoding='utf8')),
        'code_sha256':loop.normalized_kernel_hashes()|{'src/wengua/qwen_book_sweep_v1.py':loop.digest(Path(__file__).read_text(encoding='utf8'))},
        'quantization':'NF4_double_quantization_4bit','cross_trial_adapter_or_optimizer_transfer':False,
        'test_selection':False,'professional_correctness_verified':False}
    if resume_from_checkpoint is not None and not resume:raise ValueError('Explicit checkpoint requires --resume')
    if root.exists():
        if not resume or not (root/'sweep_contract.json').exists() or loop.read_json(root/'sweep_contract.json')!=contract:
            raise ValueError('Existing sweep preserved: exact --resume required; changed grid/config/code needs a new output')
    else:root.mkdir(parents=True);loop.atomic_json(root/'sweep_contract.json',contract)
    with loop.job_lock(root/'sweep.lock'),loop.keep_awake():
        path=root/'sweep_status.json';status=loop.read_json(path) if path.exists() else {'schema':SCHEMA,'state':'pending','trials':[]}
        explicit_owner=None
        if resume_from_checkpoint is not None:
            cp=Path(resume_from_checkpoint).resolve()
            owners=[t for t in trials if cp.is_relative_to((root/'trials'/t['id']).resolve())]
            if len(owners)!=1:raise ValueError('Explicit checkpoint belongs to a different sweep or trial')
            explicit_owner=owners[0]['id'];loop.requested_checkpoint(root/'trials'/explicit_owner,cp)
        if status['state']=='complete':
            if retry_oom or explicit_owner:raise ValueError('Completed sweep is frozen; use a new output for further tuning')
            loop.checked_adapter(status['selection']['adapter']);render(root,status,trials);return status
        if retry_oom and (root/'selected_trial.json').exists():raise ValueError('Selection frozen; new grid/trial requires a new sweep')
        if explicit_owner and (root/'selected_trial.json').exists():raise ValueError('Selection frozen; checkpoint replay cannot change the selected trial')
        if explicit_owner and any(r['id']==explicit_owner and r['state']=='oom' for r in status['trials']) and not retry_oom:
            raise ValueError('Explicit checkpoint belongs to an OOM trial; add --retry-oom to resume it before selection freezes')
        try:
            known={r['id']:r for r in status['trials']};status['state']='running';status.pop('error',None)
            for trial in trials:
                tid=trial['id'];c=trial['config'];previous=known.get(tid,{})
                if previous.get('state')=='oom' and not retry_oom:continue
                if time.time()>=deadline-240:status['state']='paused_deadline';return status
                loop.progress('sweep_trial',trial=tid,total=len(trials),parameters={k:c[k] for k in sorted(OPT_KEYS)})
                status['active_trial']=tid;loop.atomic_json(path,status)
                job=root/'trials'/tid
                try:
                    job=loop.open_job(job,c,resume=resume)
                    if cpu_factory is None:
                        from .qwen_finetune import environment_report
                        doctor=environment_report(c);loop.atomic_json(job/'doctor.json',doctor)
                        if doctor['training_preflight']['status']!='ready_for_smoke_test':raise RuntimeError(doctor['training_preflight']['reason'])
                    shared_prepare(root,job,c,tokenizer=tokenizer,pack=pack)
                    result=loop.run_loop(job,c,deadline,resume=True,cpu_factory=cpu_factory,tokenizer=tokenizer,pack=pack,
                        extra_callbacks=extra_callbacks,resume_from_checkpoint=resume_from_checkpoint if explicit_owner==tid else None)
                    row=trial_result(tid,c,result)
                except Exception as error:
                    if not loop.is_cuda_oom(error):raise
                    row={'id':tid,'state':'oom','error':str(error)[:2000],
                        'parameters':{k:c[k] for k in sorted(OPT_KEYS)},'context_fallback_used':False,'all_outputs_preserved':True}
                    error.__traceback__=None;error.__context__=None;gc.collect()
                    if cpu_factory is None:
                        import torch
                        torch.cuda.empty_cache()
                known[tid]=row;status['trials']=[known[t['id']] for t in trials if t['id'] in known]
                loop.atomic_json(path,status);render(root,status,trials)
                if row['state'] not in ('complete','oom'):status['state']='paused_trial';return status
            winner=select_trial(status['trials'])
            if winner is None:status['state']='no_feasible_trial';return status
            selected={k:winner[k] for k in ('id','adapter','best_cycle','validation_loss')}
            selected.update(selection_basis='fixed_validation_language_loss_only',test_used_for_selection=False)
            frozen=root/'selected_trial.json'
            if frozen.exists() and loop.read_json(frozen)!=selected:raise ValueError('Frozen selection mismatch; test results cannot select another trial')
            loop.atomic_json(frozen,selected);status['selection']=selected;status['state']='final_test'
            loop.atomic_json(path,status);render(root,status,trials)
            chosen=next(t for t in trials if t['id']==selected['id']);job=root/'trials'/chosen['id']
            final_path=root/'final_test.json'
            if final_path.exists() and loop.read_json(final_path)['state']=='complete':final=loop.read_json(final_path)
            else:
                with loop.job_lock(job/'run.lock'):
                    final=loop.final_test(job,chosen['config'],{'adapter':selected['adapter'],'cycle':selected['best_cycle']},deadline,cpu_factory=cpu_factory)
                final=dict(final,trial_id=chosen['id']);loop.atomic_json(final_path,final)
            status['final_test']=final;status['state']='complete' if final['state']=='complete' else 'paused_final_test'
            child=loop.read_json(job/'job_status.json');child['sweep_final_test']=final;loop.render_report(job,child)
            return status
        except BaseException as error:
            status['state']='interrupted' if isinstance(error,KeyboardInterrupt) else 'failed'
            status['error']={'type':type(error).__name__,'message':str(error)[:2000]};raise
        finally:
            loop.atomic_json(path,status);render(root,status,trials)
