"""Continuous-optimizer, source-only QLoRA SFT with epoch-level format NLL.

Generic tokenization, sealed checkpoints and source rendering are reused from
the old loop. No old adapter, teacher verdict or numerical Qimen score is read.
"""
from __future__ import annotations

from collections import defaultdict
import gc
import math
from pathlib import Path
import shutil
import time

from . import qwen_book_loop_v3 as book
from .qwen_book_sweep_v1 import validate_config as validate_structure

SCHEMA='wengua_book_continuous_v1'
OPT_KEYS=frozenset(('lora_r','lora_alpha','lora_dropout','target_modules','learning_rate','warmup_ratio'))
COMMON_FILES=('validation_loss.jsonl.gz','validation_prompts.jsonl.gz','test_prompts.jsonl.gz')


def base_config():
    c=book.load_config();c.update(cycles=1,gradient_accumulation_steps=16,max_steps_per_cycle=2000,
        num_train_epochs=5,save_total_limit=5,warmup_ratio=0.08,training_mode='continuous_epochs',
        optimizer_reset_between_epochs=False,final_test_policy='defer_to_sweep')
    return c


def validate(c):
    validate_structure(c)
    if c.get('training_mode')!='continuous_epochs' or c.get('optimizer_reset_between_epochs') is not False:
        raise ValueError('Continuous optimizer required')
    if c['cycles']!=1 or c['final_test_policy']!='defer_to_sweep':raise ValueError('Single fixed dataset and deferred test required')
    for key,lo,hi in [('num_train_epochs',1,8),('save_total_limit',3,8)]:
        if type(c[key]) is not int or not lo<=c[key]<=hi:raise ValueError('Invalid '+key)
    if not 0<=c['warmup_ratio']<=0.2:raise ValueError('Invalid warmup ratio')
    return c


def code_hashes():
    return book.normalized_kernel_hashes()|{name:book.digest((book.ROOT/name).read_text(encoding='utf8')) for name in
        ('src/wengua/qwen_book_sweep_v1.py','src/wengua/qwen_book_continuous_v1.py','src/wengua/qwen_book_sweep_v2.py')}


def open_job(path,c,*,resume):
    path=book.private_output(path)
    contract={'schema':SCHEMA,'config':validate(c),'code_sha256':code_hashes(),
        'source_database_sha256':book.SOURCE_SHA256,'coordinates_sha256':book.digest(book.COORDINATES.read_text(encoding='utf8')),
        'initialization':'official_pinned_base_new_adapter','initial_adapter':None,'test_used_for_selection':False}
    if path.exists():
        if not resume or not (path/'job_contract.json').exists() or book.read_json(path/'job_contract.json')!=contract:
            raise ValueError('Continuous job contract changed or belongs to an old loop; use a new output')
    else:path.mkdir(parents=True);book.atomic_json(path/'job_contract.json',contract)
    return path


def data_signature(c):return {k:v for k,v in c.items() if k not in OPT_KEYS}


def cached_prepare(path,c,*,tokenizer=None,pack=None):
    path.mkdir(parents=True,exist_ok=True);receipt=path/'prepared/receipt.json'
    original=book.read_json(receipt)['config'] if receipt.exists() else c
    if data_signature(original)!=data_signature(c):raise ValueError('Shared data contract changed')
    return book.prepare(path,original,tokenizer=tokenizer,pack=pack)


def coverage(prepared,c):
    rows=book.read_rows(prepared/'cycle_01.jsonl.gz');groups=defaultdict(lambda:{'rows':0,'input_and_target_tokens':0,'supervised_tokens':0})
    for row in rows:
        item=groups[row['format']];item['rows']+=1;item['input_and_target_tokens']+=row['tokens']
        item['supervised_tokens']+=sum(x!=-100 for x in row['encoded']['labels'])
    total=sum(x['supervised_tokens'] for x in groups.values())
    for item in groups.values():item['share_of_supervised_tokens']=item['supervised_tokens']/total
    return {'context':c['max_seq_length'],'training_views':len(rows),'core_tasks_covered':len({r['core_id'] for r in rows}),
        'case_ids_covered':len({r['case_id'] for r in rows if r['case_id']}),'source_groups':len({r['group'] for r in rows}),
        'formats':dict(groups),'updates_per_epoch':math.ceil(len(rows)/c['gradient_accumulation_steps']),
        'maximum_updates':math.ceil(len(rows)/c['gradient_accumulation_steps'])*c['num_train_epochs'],
        'no_truncation':True,'one_assistant_prefix_view_per_epoch':True,'million_synonyms_replayed':False}


def prepare_shared(root,job,c,*,reference_context,tokenizer=None,pack=None):
    """Context-specific training; byte-identical common evaluation for all contexts."""
    ref=dict(c,max_seq_length=reference_context,inference_max_context=reference_context)
    common=root/'data'/f'context_{reference_context}';refmeta=cached_prepare(common,ref,tokenizer=tokenizer,pack=pack)
    cache=root/'data'/f'context_{c["max_seq_length"]}'
    meta=cached_prepare(cache,c,tokenizer=tokenizer,pack=pack)
    hashes={name:refmeta['file_sha256'][name] for name in COMMON_FILES}
    if cache!=common:
        raw=cache;cache=raw/'compared';cache.mkdir(exist_ok=True)
        if not (cache/'prepared/receipt.json').exists():
            pending=cache/'prepared.pending'
            for partial in (cache/'prepared',pending):
                if partial.exists():partial.rename(cache/(partial.name+'.incomplete-'+str(time.time_ns())))
            shutil.copytree(raw/'prepared',pending)
            for name in COMMON_FILES:
                shutil.copy2(pending/name,pending/('context_original_'+name))
                shutil.copy2(common/'prepared'/name,pending/name)
            # Longer validation lessons are a separate diagnostic. They never
            # select a model against the common, shorter validation cohort.
            extended=dict(c,eval_max_new_tokens=min(1536,c['max_seq_length']//2))
            cores=book.read_rows(pending/'core_records.jsonl.gz')
            candidates=[r for r in cores if r['split']=='validation' and r['format'] in ('complete_case','conditional_dialogue')]
            if tokenizer is None:tokenizer=book.load_book_tokenizer(c)
            fit,_=book.generation_rows(candidates,tokenizer,extended)
            long_rows=[]
            for r in fit:
                prompt=tokenizer.apply_chat_template(r['messages'][:-1],tokenize=True,add_generation_prompt=True,enable_thinking=False)
                if len(prompt)+c['eval_max_new_tokens']>reference_context or len(tokenizer.encode(r['answer'],add_special_tokens=False))+1>c['eval_max_new_tokens']:
                    long_rows.append(r)
            selected=book.grouped_select(long_rows,4)
            book.write_rows(pending/'extended_validation_prompts.jsonl.gz',selected)
            book.atomic_json(pending/'extended_validation_plan.json',{'rows':len(selected),'max_new_tokens':extended['eval_max_new_tokens'],
                'used_for_selection':False,'split':'validation','source_groups':len({r['group'] for r in selected})})
            meta=dict(meta,common_evaluation={'context':reference_context,'file_sha256':hashes})
            meta['file_sha256']={p.relative_to(pending).as_posix():book.file_sha(p) for p in pending.rglob('*') if p.is_file() and p.name!='receipt.json'}
            book.atomic_json(pending/'receipt.json',meta);pending.rename(cache/'prepared')
        meta=cached_prepare(cache,c)
    if any(meta['file_sha256'][name]!=sha for name,sha in hashes.items()):raise ValueError('Common evaluation changed across contexts')
    target=job/'prepared'
    if not (target/'receipt.json').exists():
        if (job/'smoke').exists() or (job/'cycle_01').exists():raise ValueError('Missing prepared data after training started')
        for partial in (target,job/'prepared.pending'):
            if partial.exists():partial.rename(job/(partial.name+'.incomplete-'+str(time.time_ns())))
        pending=job/'prepared.pending';shutil.copytree(cache/'prepared',pending)
        book.atomic_json(pending/'receipt.json',dict(meta,config=c));pending.rename(target)
    actual=book.prepare(job,c)
    if actual['file_sha256']!=meta['file_sha256']:raise ValueError('Trial data differs from its shared context cache')
    proof=coverage(target,c);proof['common_evaluation_context']=reference_context;proof['common_evaluation_sha256']=hashes
    book.atomic_json(job/'coverage.json',proof);return proof


def macro_losses(metrics,formats):
    values={fmt:metrics.get('eval_'+fmt+'_loss') for fmt in formats}
    if any(v is None or not math.isfinite(v) for v in values.values()):raise ValueError('Incomplete/non-finite format validation losses')
    return {'validation_loss':sum(values.values())/len(values),'per_format_loss':values,
        'selection_basis':'equal_weight_mean_of_format_language_losses','professional_correctness_verified':False}


def update_history(history,row,c):
    if history and row['steps']<=history[-1]['steps']:raise ValueError('Epoch evaluation repeated or out of order')
    history=[*history,row];anchor=history[0]['validation_loss'];stale=0
    for item in history[1:]:
        if item['validation_loss']<anchor-c['minimum_loss_improvement']:anchor=item['validation_loss'];stale=0
        else:stale+=1
    return history,stale>=c['patience']


def seal(stage,path,history,early_stopped):
    book.atomic_json(path/'continuous_state.json',{'history':history,'early_stopped':early_stopped,
        'optimizer_reset_between_epochs':False,'selection_uses_test':False})
    book.seal_checkpoint(stage,path)


def latest(stage):
    cp=book.checkpoint_latest(stage)
    if cp and not (cp/'continuous_state.json').exists():raise ValueError('Not a continuous-optimizer checkpoint')
    return cp


def explicit_checkpoint(job,path):
    job=Path(job).resolve()
    status=job/'cycle_01/stage_status.json'
    if status.exists() and book.read_json(status).get('state','').startswith('trained_pending_'):
        raise ValueError('Training finished; use ordinary --resume to continue evaluation')
    name,cp=book.requested_checkpoint(job,path)
    if name!='cycle_01' or latest(job/'cycle_01')!=cp:raise ValueError('Checkpoint must belong to this exact continuous fit')
    return cp


def render(job,status):
    display=dict(status,cycles=status.get('epochs',[]))
    book.render_report(job,display)
    # One continuous Trainer log, rather than duplicating its history for each epoch.
    import csv
    cp=status.get('last_optimizer_checkpoint');history=[]
    if cp and (Path(cp)/'trainer_state.json').exists():history=book.read_json(Path(cp)/'trainer_state.json')['log_history']
    with (job/'training_steps.csv').open('w',encoding='utf-8-sig',newline='') as f:
        out=csv.DictWriter(f,fieldnames=['step','epoch','loss','learning_rate','grad_norm'],extrasaction='ignore');out.writeheader();out.writerows(history)
    import html
    curves=[('train','#2768b0',[(r['step'],r['loss']) for r in history if 'loss' in r]),
            ('validation macro NLL','#bb5633',[(r['steps'],r['validation_loss']) for r in status.get('epochs',[])])]
    points=[p for _,_,series in curves for p in series if math.isfinite(p[1])]
    if points:
        xmax=max(1,max(x for x,_ in points));ymin=min(y for _,y in points);ymax=max(y for _,y in points)
        span=max(0.01,ymax-ymin);ymax=ymin+span;svg=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 250"><rect width="720" height="250" fill="white"/>']
        for index,(name,color,series) in enumerate(curves):
            coordinates=' '.join(f'{50+640*x/xmax:.2f},{210-170*(y-ymin)/span:.2f}' for x,y in series if math.isfinite(y))
            svg+=['<polyline fill="none" stroke="'+color+'" stroke-width="2" points="'+coordinates+'"/>',
                  f'<text x="{50+index*230}" y="20" fill="{color}" font-size="14">{name}</text>']
        svg.append(f'<text x="5" y="45" font-size="12">{ymax:.4f}</text><text x="5" y="212" font-size="12">{ymin:.4f}</text><text x="50" y="240" font-size="12">0</text><text x="620" y="240" font-size="12">step {xmax}</text></svg>')
        (job/'loss.svg').write_text(''.join(svg),encoding='utf8')
    appendix=('<h2>连续训练曲线</h2><img src="loss.svg" alt="训练loss与格式等权验证NLL曲线" style="width:100%;max-width:900px">' if points else '')
    appendix+='<details><summary>连续Trainer全部训练步日志</summary><pre>'+html.escape(book.json.dumps(history,ensure_ascii=False,indent=2))+'</pre></details>'
    path=job/'results.html';path.write_text(path.read_text(encoding='utf8').replace('</html>',appendix+'</html>'),encoding='utf8')


def fit(job,c,deadline,*,probe=False,cpu_factory=None,extra_callbacks=(),resume_from_checkpoint=None):
    """One Trainer and scheduler for all epochs; every optimizer restore is sealed."""
    import torch
    from transformers import AutoTokenizer,Trainer,TrainingArguments,TrainerCallback,TrainerState,set_seed
    from peft import LoraConfig,PeftModel,get_peft_model
    from peft.utils.save_and_load import load_peft_weights,set_peft_model_state_dict
    from .qwen_finetune import collator,prepare_frozen_base
    job=Path(job);stage=job/('smoke' if probe else 'cycle_01');data=job/'prepared'
    rows=book.read_rows(data/('smoke.jsonl.gz' if probe else 'cycle_01.jsonl.gz'))
    validation=book.read_rows(data/'validation_loss.jsonl.gz');formats=sorted({r['format'] for r in validation})
    datasets={fmt:[r['encoded'] for r in validation if r['format']==fmt] for fmt in formats}
    steps_per_epoch=math.ceil(len(rows)/c['gradient_accumulation_steps']);planned=c['smoke_steps'] if probe else steps_per_epoch*c['num_train_epochs']
    contract={'schema':SCHEMA,'job_contract_sha256':book.file_sha(job/'job_contract.json'),'unit':stage.name,'config':c,
        'data_sha256':book.file_sha(data/('smoke.jsonl.gz' if probe else 'cycle_01.jsonl.gz')),
        'validation_sha256':book.file_sha(data/'validation_loss.jsonl.gz'),'planned_updates':planned,
        'stack':book.stack_versions(),'fresh_official_base':True,'optimizer_reset_between_epochs':False}
    if stage.exists():
        if not (stage/'stage_contract.json').exists() or book.read_json(stage/'stage_contract.json')!=contract:raise ValueError('Continuous stage contract changed')
    else:stage.mkdir();book.atomic_json(stage/'stage_contract.json',contract)
    statusfile=stage/'stage_status.json';prior=book.read_json(statusfile) if statusfile.exists() else {}
    cp=explicit_checkpoint(job,resume_from_checkpoint) if resume_from_checkpoint is not None else latest(stage)
    if prior.get('state')=='complete':book.checked_adapter(prior['adapter']);return prior
    if time.time()>deadline-240:return prior|{'state':'paused_before_model_load'}
    state=book.read_json(cp/'continuous_state.json') if cp else {'history':[],'early_stopped':False}
    if prior.get('steps',0)>0 and cp is None:raise ValueError('No intact continuous optimizer checkpoint; refusing fresh restart')
    pending=prior.get('state') in ('trained_pending_validation','trained_pending_generation')
    if (stage/'epoch_history.json').exists() and not pending:
        old=book.read_json(stage/'epoch_history.json')
        if old!=state['history']:book.atomic_json(stage/('epoch_history.before_restore-'+str(time.time_ns())+'.json'),old)
    book.atomic_json(stage/'epoch_history.json',prior.get('epochs',[]) if pending else state['history'])
    model=trainer=base=None;started=time.time();set_seed(c['seed'])
    try:
        if cpu_factory:tokenizer,base,compute=cpu_factory()
        else:
            tokenizer=AutoTokenizer.from_pretrained(c['model_id'],revision=c['revision'],local_files_only=True,trust_remote_code=False)
            base,compute=book.load_book_cuda(c,training=True)
        tokenizer.pad_token=tokenizer.pad_token or tokenizer.eos_token
        if pending:model=PeftModel.from_pretrained(base,prior['last_adapter'],is_trainable=False)
        else:
            base=prepare_frozen_base(base,gradient_checkpointing=c['gradient_checkpointing'])
            model=get_peft_model(base,LoraConfig(r=c['lora_r'],lora_alpha=c['lora_alpha'],lora_dropout=c['lora_dropout'],
                target_modules=c['target_modules'],bias='none',task_type='CAUSAL_LM'))
        class EpochAudit(TrainerCallback):
            active=False;early=state['early_stopped'];history=prior.get('epochs',[]) if pending else state['history'];partial={}
            def on_train_begin(self,args,state,control,**kw):self.active=True;return control
            def on_train_end(self,args,state,control,**kw):self.active=False;return control
            def on_step_end(self,args,state,control,**kw):
                if time.time()>=deadline-180:control.should_save=True;control.should_training_stop=True
                return control
            def on_epoch_end(self,args,state,control,**kw):
                if state.epoch is None or abs(state.epoch-round(state.epoch))>1e-6:control.should_evaluate=False
                return control
            def on_evaluate(self,args,state,control,metrics=None,**kw):
                if not self.active or probe:return control
                self.partial.update({k:v for k,v in (metrics or {}).items() if k.startswith('eval_') and k.endswith('_loss')})
                if not all('eval_'+fmt+'_loss' in self.partial for fmt in formats):return control
                values=macro_losses(self.partial,formats);self.partial={}
                adapter=book.save_adapter(kw['model'],tokenizer,stage,state.global_step)
                row=dict(values,cycle=round(state.epoch),epoch=state.epoch,steps=state.global_step,
                    state='complete',adapter=str(adapter),optimizer_reset_between_epochs=False)
                self.history,self.early=update_history(self.history,row,c)
                book.atomic_json(stage/'epoch_history.json',self.history)
                control.should_save=True
                if self.early:control.should_training_stop=True
                return control
            def on_save(self,args,state,control,**kw):seal(stage,Path(args.output_dir)/f'checkpoint-{state.global_step}',self.history,self.early);return control
        audit=EpochAudit();cpu=cpu_factory is not None
        args=TrainingArguments(output_dir=str(stage/'trainer'),num_train_epochs=c['num_train_epochs'],max_steps=c['smoke_steps'] if probe else -1,
            per_device_train_batch_size=1,per_device_eval_batch_size=1,gradient_accumulation_steps=c['gradient_accumulation_steps'],
            learning_rate=c['learning_rate'],warmup_ratio=c['warmup_ratio'],lr_scheduler_type='cosine',logging_steps=1,
            save_strategy='steps',save_steps=c['save_steps'],save_total_limit=c['save_total_limit'],eval_strategy='no' if probe else 'epoch',
            gradient_checkpointing=c['gradient_checkpointing'] and not pending,gradient_checkpointing_kwargs={'use_reentrant':False},
            optim='adamw_torch',report_to='none',seed=c['seed'],data_seed=c['seed'],dataloader_num_workers=0,
            remove_unused_columns=False,use_cpu=cpu,dataloader_pin_memory=not cpu,
            bf16=str(compute).endswith('bfloat16'),fp16=str(compute).endswith('float16') and not str(compute).endswith('bfloat16'))
        trainer=Trainer(model=model,args=args,train_dataset=[r['encoded'] for r in rows],eval_dataset=datasets,
            processing_class=tokenizer,data_collator=collator(tokenizer.pad_token_id),callbacks=[audit,*extra_callbacks])
        if not cpu:torch.cuda.reset_peak_memory_stats()
        baseline_path=job/'base_validation_loss.json'
        if not baseline_path.exists():
            with model.disable_adapter():values=trainer.evaluate()
            book.atomic_json(baseline_path,macro_losses(values,formats))
        baseline=book.read_json(baseline_path)
        if not pending:
            book.atomic_json(statusfile,{'state':'training','steps':int(cp.name[11:]) if cp else 0,'planned_steps':planned,'resume_checkpoint':str(cp) if cp else None})
            if cp and not probe and int(cp.name[11:])%steps_per_epoch==0 and (not audit.history or audit.history[-1]['steps']!=int(cp.name[11:])):
                # The step checkpoint can precede epoch validation. Recover that
                # evaluation before Trainer skips to the next epoch on resume.
                set_peft_model_state_dict(model,load_peft_weights(str(cp),device='cpu'),adapter_name='default')
                trainer.state=TrainerState.load_from_json(str(cp/'trainer_state.json'));trainer._load_rng_state(str(cp))
                audit.active=True;trainer.evaluate();audit.active=False
                for name in ('continuous_state.json','trainer_state.json','rng_state.pth'):
                    shutil.copy2(cp/name,cp/(name+'.before_boundary_validation'))
                trainer.state.save_to_json(str(cp/'trainer_state.json'));trainer._save_rng_state(str(cp))
                seal(stage,cp,audit.history,audit.early)
            completed=cp and (int(cp.name[11:])>=planned or audit.early)
            if completed:
                set_peft_model_state_dict(model,load_peft_weights(str(cp),device='cpu'),adapter_name='default')
                trainer.state=TrainerState.load_from_json(str(cp/'trainer_state.json'));metrics={'finalized_without_extra_update':True}
            else:
                # A cached baseline skips evaluation dataloader RNG draws. Fresh
                # training must start identically whether that cache existed;
                # Trainer subsequently restores checkpoint RNG on real resume.
                set_seed(c['seed'])
                metrics=trainer.train(resume_from_checkpoint=str(cp) if cp else None).metrics
            count=trainer.state.global_step;finished=count>=planned or audit.early
            if finished and not probe and (not audit.history or audit.history[-1]['steps']!=count):
                audit.active=True;trainer.evaluate();audit.active=False
            checkpoint=stage/'trainer'/f'checkpoint-{count}'
            if count and not checkpoint.exists():trainer._save_checkpoint(trainer.model,trial=None);seal(stage,checkpoint,audit.history,audit.early)
            last=next((r['adapter'] for r in audit.history if r['steps']==count),None)
            last=last or str(book.save_adapter(model,tokenizer,stage,count))
            status={'state':'trained_pending_generation' if finished else 'paused_training','steps':count,'planned_steps':planned,
                'epochs':audit.history,'early_stopped':audit.early,'last_adapter':last,'last_optimizer_checkpoint':str(latest(stage)),
                'resume_checkpoint':str(cp) if cp else None,'optimizer_reset_between_epochs':False,'fresh_official_base':True,
                'runtime_seconds':time.time()-started+prior.get('runtime_seconds',0),'training_metrics':metrics,
                'base_validation_loss':baseline['validation_loss'],'base_per_format_loss':baseline['per_format_loss'],
                'trainable_parameters':sum(p.numel() for p in model.parameters() if p.requires_grad),
                'peak_reserved_gib':torch.cuda.max_memory_reserved()/2**30 if not cpu else None,
                'professional_correctness_verified':False,'test_used_for_selection':False}
            book.atomic_json(statusfile,status)
        else:status=dict(prior)
        if status['state']=='paused_training':return status
        if probe:
            # Also exercise longest held-out forward and an actual bounded generation.
            longest=max(validation,key=lambda r:r['tokens']);trainer.evaluate(eval_dataset=[longest['encoded']])
            sample=book.read_rows(data/'validation_prompts.jsonl.gz')[:1]
            inference=c
            if (data/'extended_validation_plan.json').exists():
                extension=book.read_json(data/'extended_validation_plan.json')
                if extension['rows']:
                    sample=book.read_rows(data/'extended_validation_prompts.jsonl.gz')[:1]
                    inference=dict(c,eval_max_new_tokens=extension['max_new_tokens'])
            trainer=None;gc.collect()
            if not cpu:torch.cuda.empty_cache()
            sample_result=book.generate_rows(model,tokenizer,sample,job/'smoke_generation.jsonl',inference,deadline,'smoke')
            if not cpu:status['peak_reserved_gib']=torch.cuda.max_memory_reserved()/2**30
            status['state']='complete' if sample_result['state']=='complete' else 'trained_pending_generation'
            status['adapter']=status['last_adapter'];status['smoke_adapter_not_used_for_formal_training']=True
            book.atomic_json(statusfile,status);return status
        if not status['epochs']:raise ValueError('No complete format validation to select an adapter')
        best=min(status['epochs'],key=lambda r:(r['validation_loss'],r['steps']));book.checked_adapter(best['adapter'])
        status.update(adapter=best['adapter'],selected_epoch=best['cycle'],validation_loss=best['validation_loss'],per_format_loss=best['per_format_loss'])
        # Release Adam before inference; parameter shape stays constant within this trial.
        trainer=None;gc.collect()
        if not cpu:torch.cuda.empty_cache()
        gen=job/'generations';gen.mkdir(exist_ok=True);dev=book.read_rows(data/'validation_prompts.jsonl.gz')
        complete=book.generate_rows(model,tokenizer,dev,gen/'validation_base.jsonl',c,deadline,'base',disable_adapter=True)['state']=='complete'
        for epoch in status['epochs']:
            set_peft_model_state_dict(model,load_peft_weights(epoch['adapter'],device='cpu'),adapter_name='default')
            result=book.generate_rows(model,tokenizer,dev,gen/f'epoch_{epoch["cycle"]:02d}_validation.jsonl',c,deadline,f'epoch_{epoch["cycle"]:02d}')
            complete=complete and result['state']=='complete'
            if result['state']!='complete':break
        if complete and (data/'extended_validation_plan.json').exists():
            extension=book.read_json(data/'extended_validation_plan.json');status['extended_validation']=extension
            if extension['rows']:
                longdev=book.read_rows(data/'extended_validation_prompts.jsonl.gz');extended=dict(c,eval_max_new_tokens=extension['max_new_tokens'])
                set_peft_model_state_dict(model,load_peft_weights(best['adapter'],device='cpu'),adapter_name='default')
                a=book.generate_rows(model,tokenizer,longdev,gen/'extended_validation_base.jsonl',extended,deadline,'extended_validation_base',disable_adapter=True)
                b=book.generate_rows(model,tokenizer,longdev,gen/'extended_validation_selected.jsonl',extended,deadline,'extended_validation_selected')
                complete=a['state']==b['state']=='complete'
        status['state']='complete' if complete else 'trained_pending_generation'
        book.atomic_json(statusfile,status);return status
    except BaseException as error:
        book.atomic_json(stage/'failure.json',{'type':type(error).__name__,'message':str(error)[:2000],
            'last_complete_checkpoint':str(latest(stage)),'all_outputs_preserved':True});raise
    finally:
        trainer=model=base=None;gc.collect()
        if cpu_factory is None:torch.cuda.empty_cache()


def run_trial(job,c,deadline,*,cpu_factory=None,extra_callbacks=(),resume_from_checkpoint=None):
    with book.job_lock(job/'run.lock'):
        status=fit(job,c,deadline,cpu_factory=cpu_factory,extra_callbacks=extra_callbacks,resume_from_checkpoint=resume_from_checkpoint)
        book.atomic_json(job/'job_status.json',status);render(job,status);return status
