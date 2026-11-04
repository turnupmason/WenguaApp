"""Bounded fresh-base book-only SFT loop; heavy imports are lazy.

Reuses generic CUDA/token/padding utilities, never legacy datasets, scores or
teacher verdicts. Validation NLL chooses a checkpoint, not expert correctness.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from contextlib import contextmanager, nullcontext
import csv
import gc
import gzip
import hashlib
import html
import importlib.metadata
import json
import math
import os
from pathlib import Path
import time

from .qwen_book_dataset_v3 import build, VERSION as DATA_VERSION, SOURCE_SHA256, dumps, digest, variant_question, FORBIDDEN

ROOT=Path(__file__).resolve().parents[2]
SCHEMA='wengua_book_loop_v3'
CONFIG=ROOT/'configs/qwen14b_book_loop_v3.json'
SOURCE=ROOT/'archives/sqlite/WenguaApp_双书194案例_V391纯断词十二长生_完整研究库.sqlite3'
COORDINATES=ROOT/'data/knowledge/qwen_book_only_v3/case_source_coordinates_20261104.json'
MODEL_REVISION='40c069824f4251a91eefaf281ebe4c544efd3e18'
KERNELS=('src/wengua/qwen_book_loop_v3.py','src/wengua/qwen_book_dataset_v3.py','src/wengua/qwen_finetune.py')
CKPT_REQUIRED=('adapter_model.safetensors','adapter_config.json','trainer_state.json','optimizer.pt','scheduler.pt','rng_state.pth')


def atomic_json(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_name(path.name+'.tmp');temp.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf8');temp.replace(path)


def read_json(path):return json.loads(Path(path).read_text(encoding='utf8'))


def progress(event,**details):
    print('['+time.strftime('%H:%M:%S')+'] '+event+' '+dumps(details),flush=True)


def file_sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for part in iter(lambda:f.read(1024*1024),b''):h.update(part)
    return h.hexdigest()


def private_output(path):
    path=Path(path).resolve()
    if not path.is_relative_to((ROOT/'local').resolve()):raise ValueError('Book text/weights must stay inside repository local/.')
    return path


def load_config(path=CONFIG,cycles=None):
    c=read_json(path)
    if cycles is not None:c['cycles']=cycles
    if c.get('schema')!=SCHEMA or c.get('model_id')!='Qwen/Qwen3-14B' or c.get('revision')!=MODEL_REVISION:
        raise ValueError('Pinned fresh Qwen3-14B book-only configuration required')
    if any(c.get(k) is not False for k in ('production_enabled','old_adapters_allowed','non_book_teachers_allowed')):
        raise ValueError('Legacy adapters, teachers and production route prohibited')
    if any(k in c for k in ('initial_adapter','adapter_run','teacher_model')):raise ValueError('No external adapter/teacher input')
    for key,lo,hi in [('cycles',1,6),('max_seq_length',256,4096),('inference_max_context',512,4096),
        ('eval_max_new_tokens',1,1024),('save_steps',1,100),('smoke_steps',2,5),('patience',1,6),
        ('gradient_accumulation_steps',1,64),('max_steps_per_cycle',1,2000),('validation_rows',1,256),
        ('validation_generation_rows',1,64),('test_generation_rows',1,128)]:
        if not lo<=c[key]<=hi:raise ValueError('Invalid bounded '+key)
    if c['eval_max_new_tokens']>=c['inference_max_context']:raise ValueError('Generation context budget')
    if not 0<c['learning_rate']<=0.001 or not 0<=c['minimum_loss_improvement']<1:raise ValueError('Invalid optimization settings')
    if c.get('final_test_policy','selected_after_loop') not in ('selected_after_loop','defer_to_sweep'):
        raise ValueError('Invalid final test policy')
    return c


@contextmanager
def job_lock(path):
    """OS lock is released after a crash, including on Windows."""
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('a+b') as stream:
        stream.seek(0);stream.write(b'0');stream.flush();stream.seek(0)
        try:
            if os.name=='nt':
                import msvcrt
                msvcrt.locking(stream.fileno(),msvcrt.LK_NBLCK,1)
            else:
                import fcntl
                fcntl.flock(stream.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
        except OSError as error:raise RuntimeError('This book job is already running in another process.') from error
        try:yield
        finally:
            stream.seek(0)
            if os.name=='nt':
                import msvcrt
                msvcrt.locking(stream.fileno(),msvcrt.LK_UNLCK,1)
            else:
                import fcntl
                fcntl.flock(stream.fileno(),fcntl.LOCK_UN)


@contextmanager
def keep_awake():
    prior=None
    if os.name=='nt':
        import ctypes
        prior=ctypes.windll.kernel32.SetThreadExecutionState(0x80000001)
    try:yield
    finally:
        if os.name=='nt' and prior:
            import ctypes
            ctypes.windll.kernel32.SetThreadExecutionState(prior)


def grouped_select(rows,limit):
    buckets=defaultdict(list)
    for row in sorted(rows,key=lambda r:digest('book-dev:'+r['id'])):buckets[row['format']].append(row)
    chosen=[];seen=set()
    while buckets and len(chosen)<limit:
        for fmt in list(sorted(buckets)):
            while buckets[fmt] and buckets[fmt][0]['group'] in seen:buckets[fmt].pop(0)
            if buckets[fmt]:
                r=buckets[fmt].pop(0);chosen.append(r);seen.add(r['group'])
            if not buckets[fmt]:del buckets[fmt]
            if len(chosen)>=limit:break
    return chosen


def write_rows(path,rows):
    with gzip.open(path,'wt',encoding='utf8',compresslevel=3) as f:
        for r in rows:f.write(dumps(r)+'\n')


def read_rows(path):
    with gzip.open(path,'rt',encoding='utf8') as f:return [json.loads(line) for line in f]


def encode(row,tokenizer,limit):
    opts={'tokenize':True,'enable_thinking':False}
    prefix=tokenizer.apply_chat_template(row['messages'][:-1],add_generation_prompt=True,**opts)
    full=tokenizer.apply_chat_template(row['messages'],add_generation_prompt=False,**opts)
    if full[:len(prefix)]!=prefix or len(full)<=len(prefix):raise ValueError('Assistant mask/chat template mismatch')
    if len(full)>limit:return None,len(full)
    return {'input_ids':full,'attention_mask':[1]*len(full),'labels':[-100]*len(prefix)+full[len(prefix):]},len(full)


def target_views(core,cycle):
    messages=[dict(m) for m in core['messages']]
    if cycle:
        original=messages[-2]['content']
        if not original.startswith(core['question']):raise ValueError('Core question boundary')
        number=1+int(digest(core['id']+':cycle:'+str(cycle))[:8],16)%512
        messages[-2]['content']=variant_question(core,number)+original[len(core['question']):]
    for i,msg in enumerate(messages):
        if msg['role']=='assistant':
            yield {k:core[k] for k in ('id','group','split','format','source_ids','case_id','source_mode','task')}|{
                'id':core['id']+':turn'+str(i),'core_id':core['id'],'messages':messages[:i+1]}


def generation_rows(rows,tokenizer,c):
    fit=[];skips=[]
    for row in rows:
        prompt=tokenizer.apply_chat_template(row['messages'][:-1],tokenize=True,add_generation_prompt=True,enable_thinking=False)
        if len(prompt)+c['eval_max_new_tokens']>c['inference_max_context']:
            skips.append({'id':row['id'],'reason':'whole_prompt_plus_response_exceeds_context','input_tokens':len(prompt)});continue
        target_tokens=len(tokenizer.encode(row['answer'],add_special_tokens=False))+1
        if target_tokens>c['eval_max_new_tokens']:
            skips.append({'id':row['id'],'reason':'whole_reference_answer_exceeds_response_budget','target_tokens':target_tokens});continue
        fit.append(row)
    return fit,skips


def prepare(job,c,tokenizer=None,pack=None):
    prepared=job/'prepared';receipt=prepared/'receipt.json'
    if receipt.exists():
        meta=read_json(receipt)
        if meta['config']!=c:raise ValueError('Prepared configuration changed; use a new job')
        for name,sha in meta['file_sha256'].items():
            if file_sha(prepared/name)!=sha:raise ValueError('Prepared data changed: '+name)
        return meta
    if prepared.exists():
        if (job/'smoke').exists() or any(job.glob('cycle_*')):
            raise ValueError('Prepared receipt missing after training began; preserve the job and restore its original data')
        backup=job/('prepared.incomplete-'+str(time.time_ns()))
        prepared.rename(backup)
        progress('rebuilding_interrupted_preparation',original_preserved=str(backup))
    if tokenizer is None:tokenizer=load_book_tokenizer(c)
    progress('prepare_pure_book_sources',context=c['max_seq_length'],cycles=c['cycles'])
    pack=pack if pack is not None else build(SOURCE,read_json(COORDINATES))
    if pack.get('source_sha256')!=SOURCE_SHA256:raise ValueError('Pure-book archive required')
    units=pack['units'];owners={};cores=pack['records']
    for row in cores:
        if any(word in dumps(row) for word in FORBIDDEN):raise ValueError('Legacy teacher marker')
        for uid in row['source_ids']:
            if uid not in units or units[uid]['book_id'] not in ('shenqi','kaiwu'):raise ValueError('Non-book evidence')
            if owners.setdefault(uid,row['split'])!=row['split']:raise ValueError('Cross-split source')
        if row['split'] not in ('train','validation','test'):raise ValueError('Invalid data split')
    prepared.mkdir(parents=True)
    tokenizer.pad_token=tokenizer.pad_token or tokenizer.eos_token
    tokenizer.padding_side='right';tokenizer.save_pretrained(prepared/'tokenizer')
    write_rows(prepared/'source_units.jsonl.gz',units.values())
    write_rows(prepared/'core_records.jsonl.gz',cores)
    excluded=[];cycle_info=[]
    for cycle in range(c['cycles']):
        progress('tokenize_cycle',cycle=cycle+1,cycles=c['cycles'],context=c['max_seq_length'])
        accepted=[]
        for core in cores:
            if core['split']!='train':continue
            for row in target_views(core,cycle):
                encoded,size=encode(row,tokenizer,c['max_seq_length'])
                if encoded:accepted.append(row|{'encoded':encoded,'tokens':size})
                else:excluded.append({'cycle':cycle+1,'id':row['id'],'core_id':row['core_id'],'tokens':size,'original_retained':True})
        if not accepted:raise ValueError('No whole training targets fit')
        # Every accepted core/turn occurs once per cycle; never replay all its million-pool synonyms.
        accepted.sort(key=lambda r:digest('cycle:'+str(cycle)+':'+r['id']))
        name=f'cycle_{cycle+1:02d}.jsonl.gz';write_rows(prepared/name,accepted)
        progress('cycle_tokens_ready',cycle=cycle+1,rows=len(accepted))
        cycle_info.append({'cycle':cycle+1,'rows':len(accepted),'formats':dict(Counter(r['format'] for r in accepted)),
            'groups':len({r['group'] for r in accepted}),'planned_steps':min(math.ceil(len(accepted)/c['gradient_accumulation_steps']),c['max_steps_per_cycle'])})
        if cycle==0:
            longest=sorted(accepted,key=lambda r:r['tokens'],reverse=True)[:c['gradient_accumulation_steps']*c['smoke_steps']]
            write_rows(prepared/'smoke.jsonl.gz',longest)
        del accepted
    validation=[]
    for core in cores:
        if core['split']=='validation':
            for row in target_views(core,0):
                encoded,size=encode(row,tokenizer,c['max_seq_length'])
                if encoded:validation.append(row|{'encoded':encoded,'tokens':size})
    validation=grouped_select(validation,c['validation_rows'])
    if not validation:raise ValueError('No independent validation groups fit')
    write_rows(prepared/'validation_loss.jsonl.gz',validation)
    eval_skips={}
    for split,limit in [('validation',c['validation_generation_rows']),('test',c['test_generation_rows'])]:
        candidates=[r for r in cores if r['split']==split]
        candidates,skips=generation_rows(candidates,tokenizer,c)
        selected=grouped_select(candidates,limit)
        if not selected:raise ValueError('No whole '+split+' answers fit the response budget; use a new job with a larger budget')
        write_rows(prepared/(split+'_prompts.jsonl.gz'),selected);eval_skips[split]=skips
    atomic_json(prepared/'length_exclusions.json',excluded)
    atomic_json(prepared/'generation_budget_exclusions.json',eval_skips)
    meta={'schema':SCHEMA,'dataset_schema':DATA_VERSION,'source_database_sha256':SOURCE_SHA256,'config':c,
        'core_tasks':len(cores),'cycles':cycle_info,'validation_loss_rows':len(validation),
        'selected_test_prompts':len(read_rows(prepared/'test_prompts.jsonl.gz')),
        'excluded_training_views':len(excluded),'no_truncation':True,'old_adapter_loaded':False,
        'all_assistant_turns_have_prefix_targets':True,'all_million_rows_trained':False,
        'selection_uses_test':False,'semantic_quality_verified':False}
    meta['file_sha256']={p.relative_to(prepared).as_posix():file_sha(p) for p in prepared.rglob('*') if p.is_file()}
    atomic_json(receipt,meta);return meta


def normalized_kernel_hashes():
    return {name:digest((ROOT/name).read_text(encoding='utf8')) for name in KERNELS}


def open_job(output,c,resume=False):
    job=private_output(output);contract={'schema':SCHEMA,'config':c,'source_database_sha256':SOURCE_SHA256,
        'coordinates_sha256':digest(COORDINATES.read_text(encoding='utf8')),'code_sha256':normalized_kernel_hashes(),
        'initial_adapter':None,'initialization':'official_pinned_base_only'}
    path=job/'job_contract.json'
    if job.exists():
        if not resume:raise FileExistsError('Existing job preserved; use --resume for this exact book job.')
        if not path.exists() or read_json(path)!=contract:raise ValueError('Job contract mismatch: do not resume legacy/changed data or code.')
    else:job.mkdir(parents=True);atomic_json(path,contract)
    return job


def checkpoint_latest(stage):
    contract=stage/'stage_contract.json';found=[]
    if not contract.exists():return None
    for path in (stage/'trainer').glob('checkpoint-*'):
        if not path.name[11:].isdigit():continue
        try:
            proof=read_json(path/'resume_receipt.json')
            if proof['contract_sha256']!=file_sha(contract):continue
            if any(not (path/name).is_file() or not (path/name).stat().st_size for name in CKPT_REQUIRED):continue
            if any(file_sha(path/name)!=sha for name,sha in proof['files'].items()):continue
            found.append((int(path.name[11:]),path))
        except (OSError,KeyError,ValueError):continue
    return max(found)[1] if found else None


def seal_checkpoint(stage,path):
    if any(not (path/name).is_file() or not (path/name).stat().st_size for name in CKPT_REQUIRED):
        raise ValueError('Incomplete optimizer/RNG checkpoint')
    files={p.name:file_sha(p) for p in path.iterdir() if p.is_file() and p.name!='resume_receipt.json'}
    atomic_json(path/'resume_receipt.json',{'contract_sha256':file_sha(stage/'stage_contract.json'),'files':files})


def checked_adapter(path):
    path=Path(path);proof=read_json(path/'book_adapter_receipt.json')
    stage=path.parent.parent;contract=stage/'stage_contract.json'
    if proof.get('schema')!=SCHEMA or proof.get('stage_contract_sha256')!=file_sha(contract):raise ValueError('Not an adapter from this book stage')
    stage_contract=read_json(contract)
    if stage_contract.get('job_contract_sha256')!=file_sha(stage.parent/'job_contract.json'):raise ValueError('Adapter job provenance mismatch')
    for name,sha in proof['files'].items():
        if file_sha(path/name)!=sha:raise ValueError('Adapter file changed: '+name)
    return proof


def save_adapter(model,tokenizer,stage,step):
    path=stage/'adapters'/f'step-{step}';temp=stage/'adapters'/f'step-{step}.pending-{time.time_ns()}'
    temp.mkdir(parents=True);model.save_pretrained(temp,safe_serialization=True);tokenizer.save_pretrained(temp)
    files={f.name:file_sha(f) for f in temp.iterdir() if f.is_file()}
    atomic_json(temp/'book_adapter_receipt.json',{'schema':SCHEMA,'stage_contract_sha256':file_sha(stage/'stage_contract.json'),'files':files})
    if path.exists():path.rename(path.with_name(path.name+'.previous-'+str(time.time_ns())))
    temp.rename(path);return path


def stack_versions():
    result={}
    for package in ('torch','transformers','peft','accelerate','bitsandbytes'):
        try:result[package]=importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:result[package]=None
    return result


def answer_diagnostic(answer,expected):
    a,b=Counter(answer),Counter(expected);overlap=sum((a&b).values())
    return {'empty':not answer.strip(),'exact_text_match':answer.strip()==expected.strip(),
        'literal_character_f1':2*overlap/(len(answer)+len(expected) or 1),'semantic_correctness_verified':False}


def generate_rows(model,tokenizer,rows,path,c,deadline,variant,disable_adapter=False):
    import torch
    from transformers import set_seed
    existing=[];partial=False
    if path.exists():
        for line in path.read_text(encoding='utf8').splitlines():
            try:existing.append(json.loads(line))
            except ValueError:partial=True;break
    if partial:path.rename(path.with_name(path.name+'.partial-'+str(time.time_ns())))
    owner={r['id']:r for r in existing}
    if len(owner)!=len(existing):raise ValueError('Duplicate saved evaluation IDs')
    model.eval();model.config.use_cache=True
    with path.open('w',encoding='utf8') as f:
        for record in existing:f.write(dumps(record)+'\n')
        for row in rows:
            prompt_messages=row['messages'][:-1];prompt_sha=digest(dumps(prompt_messages))
            if row['id'] in owner:
                if owner[row['id']]['prompt_sha256']!=prompt_sha:raise ValueError('Evaluation prompt changed')
                continue
            if time.time()>deadline-120:break
            tokens=tokenizer.apply_chat_template(prompt_messages,tokenize=True,add_generation_prompt=True,enable_thinking=False)
            if len(tokens)+c['eval_max_new_tokens']>c['inference_max_context']:raise ValueError('Unchecked generation length')
            prompt=torch.tensor([tokens],device=model.device);set_seed(c['seed'])
            with (model.disable_adapter() if disable_adapter else nullcontext()),torch.inference_mode():
                ids=model.generate(input_ids=prompt,attention_mask=torch.ones_like(prompt),do_sample=False,
                    max_new_tokens=c['eval_max_new_tokens'],pad_token_id=tokenizer.pad_token_id,
                    eos_token_id=tokenizer.eos_token_id,use_cache=True)
            generated=ids[0,len(tokens):];answer=tokenizer.decode(generated,skip_special_tokens=True)
            record={'id':row['id'],'variant':variant,'format':row['format'],'task':row['task'],'group':row['group'],
                'source_mode':row['source_mode'],'source_ids':row['source_ids'],'question':prompt_messages,
                'expected':row['answer'],'answer':answer,'prompt_sha256':prompt_sha,
                'input_tokens':len(tokens),'generated_tokens':len(generated),
                'reached_token_limit':len(generated)>=c['eval_max_new_tokens'],
                **answer_diagnostic(answer,row['answer'])}
            f.write(dumps(record)+'\n');f.flush();existing.append(record)
    return {'completed':len(existing),'requested':len(rows),'state':'complete' if len(existing)==len(rows) else 'paused'}


def render_report(job,status):
    cycles=status.get('cycles',[]);predictions=[];source_index={}
    if (job/'prepared/source_units.jsonl.gz').exists():source_index={r['id']:r for r in read_rows(job/'prepared/source_units.jsonl.gz')}
    for path in sorted((job/'generations').glob('*.jsonl')) if (job/'generations').exists() else []:
        for line in path.read_text(encoding='utf8').splitlines():
            try:predictions.append(json.loads(line))
            except ValueError:continue
    with (job/'results.csv').open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.writer(f);writer.writerow(['cycle','state','steps','train_loss','validation_loss','seconds','peak_gpu_gib'])
        for row in cycles:writer.writerow([row.get(k,'') for k in ('cycle','state','steps','train_loss','validation_loss','runtime_seconds','peak_reserved_gib')])
    e=html.escape;body=['<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>问卦纯古籍训练报告</title>',
        '<style>body{font:16px system-ui;max-width:1300px;margin:35px auto;padding:15px;background:#f5f7fa;color:#172b35}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:white;padding:16px}details{background:white;padding:12px;margin:12px 0}table{border-collapse:collapse}td,th{padding:9px;border:1px solid #ccc}</style>',
        '<h1>纯古籍训练循环报告</h1><p>状态：'+e(status.get('state','preparing'))+'</p>',
        '<p>标准答案仅来自两书。验证损失用于选择检查点；字面相似度不是专业正确率。整案教学含作者资料，不冒充新盘盲测。</p>',
        '<pre>'+e(json.dumps({k:v for k,v in status.items() if k!='cycles'},ensure_ascii=False,indent=2))+'</pre>',
        '<h2>每轮结果</h2><table><tr><th>轮次</th><th>状态</th><th>步数</th><th>训练loss</th><th>验证loss</th><th>秒</th></tr>']
    for row in cycles:body.append('<tr>'+''.join('<td>'+e(str(row.get(k,'')))+'</td>' for k in ('cycle','state','steps','train_loss','validation_loss','runtime_seconds'))+'</tr>')
    body+=['</table><h2>逐题原始回答、参考答案与出处</h2>']
    for row in predictions:
        references='\n\n'.join(f'{source_index[u]["book_id"]}／{source_index[u]["chapter"]}／行{source_index[u]["lines"]}\n'+source_index[u]['original_quote'] for u in row['source_ids'] if u in source_index)
        body+=['<details><summary>'+e(row['variant']+' | '+row['task']+' | '+row['id'])+'</summary>',
            '<p>资料方式：'+e(row['source_mode'])+'；输出到达上限：'+str(row['reached_token_limit'])+'</p>',
            '<h3>完整提问</h3><pre>'+e(dumps(row['question']))+'</pre>',
            '<h3>模型原答</h3><pre>'+e(row['answer'])+'</pre>',
            '<h3>原书参考答案</h3><pre>'+e(row['expected'])+'</pre>',
            '<p>出处ID：'+e(', '.join(row['source_ids']))+'</p><details><summary>古籍原文与定位</summary><pre>'+e(references)+'</pre></details></details>']
    history=[]
    for unit in cycles:
        checkpoint=unit.get('last_optimizer_checkpoint')
        if checkpoint and (Path(checkpoint)/'trainer_state.json').exists():
            for item in read_json(Path(checkpoint)/'trainer_state.json').get('log_history',[]):history.append({'cycle':unit['cycle'],**item})
    with (job/'training_steps.csv').open('w',encoding='utf-8-sig',newline='') as f:
        fields=['cycle','step','loss','grad_norm','learning_rate','epoch'];writer=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');writer.writeheader();writer.writerows(history)
    body.append('<details><summary>全部保存的训练步日志</summary><pre>'+e(json.dumps(history,ensure_ascii=False,indent=2))+'</pre></details>')
    body.append('</html>');(job/'results.html').write_text(''.join(body),encoding='utf8')
    atomic_json(job/'summary.json',status)


def load_book_tokenizer(c):
    from transformers import AutoTokenizer
    from huggingface_hub import try_to_load_from_cache
    paths=[try_to_load_from_cache(c['model_id'],name,revision=c['revision']) for name in ('tokenizer.json','tokenizer_config.json')]
    complete=all(isinstance(p,str) and Path(p).is_file() and Path(p).stat().st_size for p in paths)
    return AutoTokenizer.from_pretrained(c['model_id'],revision=c['revision'],trust_remote_code=False,local_files_only=bool(complete))


def official_model_cached(c):
    """Check pinned config/index/shards locally, without reading full weight bytes."""
    from huggingface_hub import try_to_load_from_cache
    def cached(name):
        value=try_to_load_from_cache(c['model_id'],name,revision=c['revision'])
        return Path(value) if isinstance(value,str) and Path(value).is_file() and Path(value).stat().st_size else None
    if cached('config.json') is None:return False
    index=cached('model.safetensors.index.json')
    if index is None:return cached('model.safetensors') is not None
    data=read_json(index)
    names=set(data.get('weight_map',{}).values())
    if not names:raise ValueError('Pinned model cache index is corrupt')
    return all(cached(name) is not None for name in names)


def load_book_cuda(c,training):
    """Use complete pinned cache offline; only missing files authorize fetching."""
    from .qwen_finetune import load_cuda_base
    complete=official_model_cached(c)
    if not complete:progress('download_missing_official_model_cache',model=c['model_id'],revision=c['revision'])
    model,compute=load_cuda_base(c,training=False,allow_download=not complete)
    model.config.use_cache=not training
    return model,compute


def requested_checkpoint(job,path):
    """Explicit restore may only select this job's latest intact unfinished cycle."""
    path=Path(path).resolve();job=Path(job).resolve();stage=path.parent.parent
    if stage.parent!=job or not stage.name.startswith('cycle_') or path.parent.name!='trainer':
        raise ValueError('resume_from_checkpoint must belong to a cycle of this exact job')
    try:cycle=int(stage.name[6:])
    except ValueError:raise ValueError('Invalid checkpoint cycle') from None
    if stage.name!=f'cycle_{cycle:02d}' or cycle<1:raise ValueError('Invalid checkpoint cycle')
    status=read_json(stage/'stage_status.json') if (stage/'stage_status.json').exists() else {}
    if status.get('state') in ('complete','trained_pending_evaluation'):
        raise ValueError('Cycle already trained; use ordinary --resume to continue evaluation, not checkpoint rollback')
    if checkpoint_latest(stage)!=path:raise ValueError('Explicit checkpoint is not the latest intact sealed optimizer checkpoint')
    return stage.name,path


def train_unit(job,stage_name,c,deadline,*,initial_adapter=None,cpu_factory=None,extra_callbacks=(),resume_from_checkpoint=None):
    import torch
    from transformers import AutoTokenizer,Trainer,TrainingArguments,TrainerCallback,set_seed
    from peft import LoraConfig,PeftModel,get_peft_model
    from .qwen_finetune import collator,load_cuda_base,prepare_frozen_base
    stage=job/stage_name;is_smoke=stage_name=='smoke';cycle=0 if is_smoke else int(stage_name.split('_')[1])
    datafile=job/'prepared'/('smoke.jsonl.gz' if is_smoke else stage_name+'.jsonl.gz')
    rows=read_rows(datafile);validation=[] if is_smoke else read_rows(job/'prepared/validation_loss.jsonl.gz')
    steps=c['smoke_steps'] if is_smoke else min(math.ceil(len(rows)/c['gradient_accumulation_steps']),c['max_steps_per_cycle'])
    initial_proof=None
    if initial_adapter:
        initial_adapter=Path(initial_adapter).resolve()
        previous=job/f'cycle_{cycle-1:02d}'
        if cycle<=1 or not initial_adapter.is_relative_to(previous.resolve()):raise ValueError('Only previous cycle of this job can initialize the next cycle')
        parent=read_json(previous/'stage_status.json')
        if parent.get('state')!='complete' or Path(parent['adapter']).resolve()!=initial_adapter:raise ValueError('Previous cycle incomplete')
        initial_proof=checked_adapter(initial_adapter)
        if initial_proof['stage_contract_sha256']!=file_sha(previous/'stage_contract.json'):raise ValueError('Previous adapter contract mismatch')
    contract={'schema':SCHEMA,'job_contract_sha256':file_sha(job/'job_contract.json'),'unit':stage_name,
        'config':c,'data_sha256':file_sha(datafile),'validation_sha256':file_sha(job/'prepared/validation_loss.jsonl.gz'),
        'steps':steps,'initial_adapter_proof':initial_proof,'stack':stack_versions(),
        'fresh_official_base':initial_adapter is None,'fresh_optimizer_for_new_cycle':True}
    if stage.exists():
        if not (stage/'stage_contract.json').exists() or read_json(stage/'stage_contract.json')!=contract:raise ValueError('Stage resume contract mismatch')
    else:stage.mkdir();atomic_json(stage/'stage_contract.json',contract)
    statusfile=stage/'stage_status.json';prior=read_json(statusfile) if statusfile.exists() else {}
    explicit=None
    if resume_from_checkpoint is not None:
        owner,explicit=requested_checkpoint(job,resume_from_checkpoint)
        if owner!=stage_name:raise ValueError('Checkpoint belongs to a different cycle')
    if prior.get('state')=='complete':checked_adapter(prior['adapter']);return prior
    if time.time()>=deadline-240:return prior|{'state':'paused_before_model_load','cycle':cycle}
    progress('book_unit_start',unit=stage_name,rows=len(rows),planned_steps=steps,fresh_base=initial_adapter is None)
    set_seed(c['seed']);model=trainer=None
    try:
        if cpu_factory:tokenizer,base,compute=cpu_factory()
        else:
            tokenizer=AutoTokenizer.from_pretrained(c['model_id'],revision=c['revision'],trust_remote_code=False,local_files_only=True)
            base,compute=load_book_cuda(c,training=True)
        tokenizer.pad_token=tokenizer.pad_token or tokenizer.eos_token;tokenizer.padding_side='right'
        evaluation_only=prior.get('state')=='trained_pending_evaluation'
        if evaluation_only:
            checked_adapter(prior['adapter']);model=PeftModel.from_pretrained(base,prior['adapter'],is_trainable=False)
        else:
            base=prepare_frozen_base(base,gradient_checkpointing=c['gradient_checkpointing'])
            model=PeftModel.from_pretrained(base,str(initial_adapter),is_trainable=True) if initial_adapter else get_peft_model(base,LoraConfig(
                r=c['lora_r'],lora_alpha=c['lora_alpha'],lora_dropout=c['lora_dropout'],target_modules=c['target_modules'],bias='none',task_type='CAUSAL_LM'))
        class SaveChecked(TrainerCallback):
            def on_save(self,args,state,control,**kwargs):
                seal_checkpoint(stage,Path(args.output_dir)/f'checkpoint-{state.global_step}');return control
            def on_step_end(self,args,state,control,**kwargs):
                if time.time()>=deadline-180:control.should_save=True;control.should_training_stop=True
                return control
        cpu=cpu_factory is not None
        args=TrainingArguments(output_dir=str(stage/'trainer'),max_steps=steps,
            per_device_train_batch_size=1,per_device_eval_batch_size=1,
            gradient_accumulation_steps=c['gradient_accumulation_steps'],learning_rate=c['learning_rate'],
            warmup_ratio=0.03,lr_scheduler_type='cosine',logging_steps=1,
            save_strategy='steps',save_steps=min(c['save_steps'],steps),save_total_limit=3,
            eval_strategy='no',gradient_checkpointing=c['gradient_checkpointing'] and not evaluation_only,
            gradient_checkpointing_kwargs={'use_reentrant':False},optim='adamw_torch',report_to='none',
            seed=c['seed'],data_seed=c['seed'],dataloader_num_workers=0,remove_unused_columns=False,
            use_cpu=cpu,dataloader_pin_memory=not cpu,bf16=str(compute).endswith('bfloat16'),
            fp16=str(compute).endswith('float16') and not str(compute).endswith('bfloat16'))
        trainer=Trainer(model=model,args=args,train_dataset=[r['encoded'] for r in rows],
            eval_dataset=[r['encoded'] for r in validation] or None,processing_class=tokenizer,
            data_collator=collator(tokenizer.pad_token_id),callbacks=[SaveChecked(),*extra_callbacks])
        started=time.time()
        if not cpu:torch.cuda.reset_peak_memory_stats()
        if not evaluation_only:
            checkpoint=explicit or checkpoint_latest(stage)
            if prior.get('steps',0)>0 and checkpoint is None:raise ValueError('No intact optimizer checkpoint; prior outputs preserved')
            atomic_json(statusfile,{'state':'training','cycle':cycle,'steps':int(checkpoint.name[11:]) if checkpoint else 0,
                'planned_steps':steps,'resume_checkpoint':str(checkpoint) if checkpoint else None})
            if checkpoint and int(checkpoint.name[11:])>=steps:
                from peft.utils.save_and_load import load_peft_weights,set_peft_model_state_dict
                from transformers import TrainerState
                state=load_peft_weights(str(checkpoint),device='cpu')
                set_peft_model_state_dict(model,state,adapter_name='default')
                trainer.state=TrainerState.load_from_json(str(checkpoint/'trainer_state.json'))
                training_metrics={'train_loss':prior.get('train_loss'),'finalized_from_complete_optimizer_checkpoint':True}
            else:
                result=trainer.train(resume_from_checkpoint=str(checkpoint) if checkpoint else None)
                training_metrics=result.metrics
            count=trainer.state.global_step
            cp=stage/'trainer'/f'checkpoint-{count}'
            if count and not cp.exists():trainer._save_checkpoint(trainer.model,trial=None)
            if count:seal_checkpoint(stage,cp)
            adapter=save_adapter(model,tokenizer,stage,count)
            status={'state':'trained_pending_evaluation' if count>=steps else 'paused_training','cycle':cycle,
                'steps':count,'planned_steps':steps,'rows':len(rows),'train_loss':training_metrics.get('train_loss'),
                'training_metrics':training_metrics,'runtime_seconds':time.time()-started+prior.get('runtime_seconds',0),
                'adapter':str(adapter),'resume_checkpoint':str(checkpoint) if checkpoint else None,
                'last_optimizer_checkpoint':str(checkpoint_latest(stage)),'fresh_official_base':initial_adapter is None,
                'initial_adapter':str(initial_adapter) if initial_adapter else None,'test_used_for_selection':False,
                'professional_correctness_verified':False}
            if not cpu:status['peak_reserved_gib']=torch.cuda.max_memory_reserved()/2**30
            atomic_json(statusfile,status)
        else:status=dict(prior)
        if status['state']=='paused_training':return status
        if is_smoke:
            status['state']='complete';status['smoke_adapter_not_used_for_formal_training']=True
            atomic_json(statusfile,status);return status
        if time.time()>deadline-240:return status
        model.config.use_cache=False
        base_loss_path=job/'base_validation_loss.json'
        loss_contract={'model_id':c['model_id'],'revision':c['revision'],'validation_sha256':file_sha(job/'prepared/validation_loss.jsonl.gz')}
        if base_loss_path.exists():
            baseline=read_json(base_loss_path)
            if baseline['contract']!=loss_contract:raise ValueError('Base validation contract changed')
        else:
            with model.disable_adapter():base_metrics=trainer.evaluate()
            baseline={'contract':loss_contract,'validation_loss':base_metrics.get('eval_loss'),'is_expert_score':False}
            if baseline['validation_loss'] is None or not math.isfinite(baseline['validation_loss']):raise ValueError('Base validation loss is non-finite')
            atomic_json(base_loss_path,baseline)
        status['base_validation_loss']=baseline['validation_loss']
        metrics=trainer.evaluate()
        loss=metrics.get('eval_loss')
        if loss is None or not math.isfinite(loss):raise ValueError('Validation language loss is non-finite; stop loop')
        status['validation_loss']=loss;status['validation_metrics']=metrics
        dev=read_rows(job/'prepared/validation_prompts.jsonl.gz');gen=job/'generations';gen.mkdir(exist_ok=True)
        base_result=generate_rows(model,tokenizer,dev,gen/'validation_base.jsonl',c,deadline,'base',disable_adapter=True)
        cycle_result=generate_rows(model,tokenizer,dev,gen/(stage_name+'_validation.jsonl'),c,deadline,stage_name)
        status['base_validation_generation']=base_result;status['validation_generation']=cycle_result
        status['state']='complete' if base_result['state']==cycle_result['state']=='complete' else 'trained_pending_evaluation'
        atomic_json(statusfile,status);return status
    except BaseException as error:
        atomic_json(stage/'failure.json',{'type':type(error).__name__,'message':str(error)[:2000],
            'last_complete_checkpoint':str(checkpoint_latest(stage)),'all_outputs_preserved':True})
        raise
    finally:
        if trainer is not None:del trainer
        if model is not None:del model
        if 'base' in locals():del base
        gc.collect()
        if cpu_factory is None:torch.cuda.empty_cache()


def select_best(cycles,c):
    complete=[r for r in cycles if r.get('state')=='complete' and math.isfinite(r.get('validation_loss',math.inf))]
    if not complete:return None,False
    best=min(complete,key=lambda r:r['validation_loss'])
    anchor=complete[0]['validation_loss'];stale=0
    for row in complete[1:]:
        if row['validation_loss']<anchor-c['minimum_loss_improvement']:anchor=row['validation_loss'];stale=0
        else:stale+=1
    return best,stale>=c['patience']


def final_test(job,c,best,deadline,cpu_factory=None):
    """Only the selected adapter and the base touch final test generations."""
    if time.time()>deadline-240:return {'state':'paused_before_final_test'}
    import torch
    from transformers import AutoTokenizer
    from peft import PeftModel
    from .qwen_finetune import load_cuda_base
    checked_adapter(best['adapter'])
    if cpu_factory:tokenizer,base,_=cpu_factory()
    else:
        tokenizer=AutoTokenizer.from_pretrained(c['model_id'],revision=c['revision'],trust_remote_code=False,local_files_only=True)
        base,_=load_book_cuda(c,training=False)
    model=PeftModel.from_pretrained(base,best['adapter']).eval()
    try:
        rows=read_rows(job/'prepared/test_prompts.jsonl.gz');gen=job/'generations';gen.mkdir(exist_ok=True)
        a=generate_rows(model,tokenizer,rows,gen/'final_test_base.jsonl',c,deadline,'final_test_base',disable_adapter=True)
        b=generate_rows(model,tokenizer,rows,gen/'final_test_selected.jsonl',c,deadline,'final_test_selected')
        result={'state':'complete' if a['state']==b['state']=='complete' else 'paused_final_test',
            'selected_cycle':best['cycle'],'base':a,'selected':b,'used_for_selection':False}
        atomic_json(job/'final_test.json',result);return result
    finally:
        del model,base;gc.collect()
        if cpu_factory is None:torch.cuda.empty_cache()


def run_loop(job,c,deadline,*,resume=False,cpu_factory=None,tokenizer=None,pack=None,extra_callbacks=(),resume_from_checkpoint=None):
    if resume_from_checkpoint is not None and not resume:raise ValueError('Explicit checkpoint requires --resume')
    job=open_job(job,c,resume=resume)
    with job_lock(job/'run.lock'),keep_awake():
        explicit=requested_checkpoint(job,resume_from_checkpoint) if resume_from_checkpoint is not None else None
        if explicit and int(explicit[0][6:])>c['cycles']:raise ValueError('Explicit checkpoint cycle is outside this job schedule')
        status_path=job/'job_status.json'
        prior=read_json(status_path) if status_path.exists() else {}
        if prior.get('state')=='complete':
            checked_adapter(prior['selected_adapter']);render_report(job,prior);return prior
        status={'schema':SCHEMA,'state':'preparing','cycles':[], 'maximum_cycles':c['cycles'],
            'source':'two_books_only','initialization':'official_base_new_adapter','test_used_for_selection':False,
            'professional_correctness_verified':False,'production_enabled':False}
        try:
            if cpu_factory is None:
                from .qwen_finetune import environment_report
                report=environment_report(c);atomic_json(job/'doctor.json',report)
                if report['training_preflight']['status']!='ready_for_smoke_test':raise RuntimeError(report['training_preflight']['reason'])
                if any(value is None for value in report['dependencies'].values()):raise RuntimeError('Install requirements-qwen.txt in local/qwen_env first')
            data=prepare(job,c,tokenizer=tokenizer,pack=pack)
            status['preparation']=data;atomic_json(status_path,status)
            smoke=train_unit(job,'smoke',c,deadline,cpu_factory=cpu_factory)
            status['smoke']=smoke
            if smoke['state']!='complete':status['state']='paused_smoke';return status
            for cycle in range(1,c['cycles']+1):
                if time.time()>deadline-240:status['state']='paused_deadline';break
                previous=status['cycles'][-1]['adapter'] if status['cycles'] else None
                unit=train_unit(job,f'cycle_{cycle:02d}',c,deadline,initial_adapter=previous,
                    cpu_factory=cpu_factory,extra_callbacks=extra_callbacks,
                    resume_from_checkpoint=explicit[1] if explicit and explicit[0]==f'cycle_{cycle:02d}' else None)
                status['cycles'].append(unit);status['state']='training_loop';atomic_json(status_path,status);render_report(job,status)
                if unit['state']!='complete':status['state']='paused_cycle';break
                best,stop=select_best(status['cycles'],c)
                if best:
                    atomic_json(job/'selected_checkpoint.json',{'cycle':best['cycle'],'adapter':best['adapter'],
                        'validation_loss':best['validation_loss'],'selection_basis':'validation_language_loss_only',
                        'professional_correctness_verified':False})
                if stop:status['early_stopped']=True;break
            else:status['all_requested_cycles_completed']=True
            best,_=select_best(status['cycles'],c)
            finished=status.get('early_stopped') or status.get('all_requested_cycles_completed')
            if best and finished:
                status['selected_adapter']=best['adapter'];status['selected_cycle']=best['cycle']
                status['validation_loss_better_than_base']=best['validation_loss']<best.get('base_validation_loss',math.inf)
                status['selection_scope']='best_adapter_by_validation_language_loss; professional answers still require review'
                if c.get('final_test_policy')=='defer_to_sweep':
                    status['final_test']={'state':'deferred_to_sweep','used_for_selection':False}
                    status['state']='complete'
                else:
                    status['final_test']=final_test(job,c,best,deadline,cpu_factory=cpu_factory)
                    status['state']='complete' if status['final_test']['state']=='complete' else 'paused_final_test'
            return status
        except BaseException as error:
            status['state']='interrupted' if isinstance(error,KeyboardInterrupt) else 'failed'
            status['failure']={'type':type(error).__name__,'message':str(error)[:2000]}
            raise
        finally:
            atomic_json(status_path,status);render_report(job,status)


def is_cuda_oom(error):
    return type(error).__name__ in ('OutOfMemoryError','CudaOutOfMemoryError') or 'CUDA out of memory' in str(error)


def run_auto(output,c,deadline,*,resume=False,probe_contexts=(4096,2048),cpu_factory=None,tokenizer=None,pack=None):
    """Probe longest supported context, discard probe adapters, then fresh train.

    Only CUDA OOM permits the shorter fallback. Source/config/IO failures abort.
    The selected context is persisted so resume never changes the data contract.
    """
    root=private_output(output);control=root/'control_contract.json'
    control_contract={'schema':SCHEMA,'requested_config':c,'probe_contexts':list(probe_contexts),
        'code_sha256':normalized_kernel_hashes(),'source_database_sha256':SOURCE_SHA256}
    if root.exists():
        if not resume or not control.exists() or read_json(control)!=control_contract:raise ValueError('Existing auto-loop control contract mismatch; use exact --resume or a new job')
    else:root.mkdir(parents=True);atomic_json(control,control_contract)
    with job_lock(root/'auto.lock'),keep_awake():
        selected=root/'selected_config.json';probes=[]
        if selected.exists():
            chosen=read_json(selected)
            if chosen.get('max_seq_length') not in probe_contexts or chosen!=dict(c,max_seq_length=chosen['max_seq_length'],inference_max_context=chosen['max_seq_length']):raise ValueError('Selected context/config changed')
        else:
            for context in probe_contexts:
                progress('context_memory_probe',context=context,smoke_steps=c['smoke_steps'])
                trial=dict(c,max_seq_length=context,inference_max_context=context,cycles=1)
                probe_job=open_job(root/f'probe_{context}',trial,resume=True)
                try:
                    if cpu_factory is None:
                        from .qwen_finetune import environment_report
                        doctor=environment_report(trial);atomic_json(probe_job/'doctor.json',doctor)
                        if doctor['training_preflight']['status']!='ready_for_smoke_test':raise RuntimeError(doctor['training_preflight']['reason'])
                    prepare(probe_job,trial,tokenizer=tokenizer,pack=pack)
                    result=train_unit(probe_job,'smoke',trial,deadline,cpu_factory=cpu_factory)
                    probes.append({'context':context,'state':result['state'],'metrics':result})
                    render_report(root,{'state':'context_probe','probes':probes,'training_started':False})
                    if result['state']!='complete':
                        atomic_json(root/'context_probe.json',probes);return {'state':'paused_context_probe','probes':probes}
                    chosen=dict(c,max_seq_length=context,inference_max_context=context)
                    atomic_json(selected,chosen);break
                except Exception as error:
                    probes.append({'context':context,'state':'oom' if is_cuda_oom(error) else 'failed','message':str(error)[:1000]})
                    atomic_json(root/'context_probe.json',probes)
                    render_report(root,{'state':'context_probe_failed','probes':probes,'training_started':False})
                    if not is_cuda_oom(error):raise
                    error.__traceback__=None
                    gc.collect()
                    try:
                        import torch
                        torch.cuda.empty_cache()
                    except ImportError:pass
            else:raise RuntimeError('Both whole-context probes failed. Preserve logs; free GPU memory before resuming.')
            atomic_json(root/'context_probe.json',probes)
        try:
            result=run_loop(root/'training',chosen,deadline,resume=resume,cpu_factory=cpu_factory,tokenizer=tokenizer,pack=pack)
            return result
        finally:
            report=root/'training/results.html'
            if report.exists():(root/'results.html').write_bytes(report.read_bytes())
            summary=root/'training/summary.json'
            if summary.exists():(root/'summary.json').write_bytes(summary.read_bytes())
