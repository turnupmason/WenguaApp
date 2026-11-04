"""Bounded source-study QLoRA stages, checkpoint fingerprints and paired dev QA.

No full model weights or book text are published. Heavy dependencies are lazy.
Resume restores optimizer state only within the identical stage/data/config;
moving to another stage loads adapter weights and creates a new optimizer.
"""
from __future__ import annotations

from collections import Counter
from contextlib import nullcontext
import json
import math
from pathlib import Path
import time

from .qwen_research import ROOT, digest, json_text, private_path, read_rows, write_json, check_answer
from .qwen_finetune import collator, load_config, load_cuda_base, prepare_frozen_base
from .qwen_curriculum_v2 import VERSION, fit_training_view


def atomic_json(path, value):
    path=Path(path);temp=path.with_suffix(path.suffix+'.tmp')
    write_json(temp,value);temp.replace(path)


def stage_contract(rows, config, stage, max_steps, initial_adapter=None):
    adapter=Path(initial_adapter) if initial_adapter else None
    return {'schema':VERSION,'stage':stage,'config':config,'max_steps':max_steps,
            'encoded_rows_sha256':digest(json_text(rows)),
            'initial_adapter_sha256':digest((adapter/'adapter_model.safetensors').read_bytes()) if adapter else None,
            'initial_adapter_config_sha256':digest((adapter/'adapter_config.json').read_bytes()) if adapter else None,
            'fresh_optimizer_for_new_stage':True,'production_enabled':False}


CHECKPOINT_FILES=('adapter_model.safetensors','adapter_config.json','trainer_state.json','optimizer.pt','scheduler.pt','rng_state.pth')


def seal_checkpoint(output,checkpoint):
    output=Path(output);checkpoint=Path(checkpoint)
    receipt={'stage_contract_sha256':digest((output/'stage_contract.json').read_bytes()),
             'file_sha256':{name:digest((checkpoint/name).read_bytes()) for name in CHECKPOINT_FILES}}
    atomic_json(checkpoint/'resume_receipt.json',receipt)


def latest_checkpoint(output):
    """Skip incomplete writes after a power cut. Never load another stage."""
    result=[]
    for p in (Path(output)/'trainer').glob('checkpoint-*'):
        if not p.name[11:].isdigit():continue
        if not all((p/n).is_file() and (p/n).stat().st_size for n in CHECKPOINT_FILES):continue
        receipt=p/'resume_receipt.json';contract=Path(output)/'stage_contract.json'
        if not receipt.exists() or not contract.exists():continue
        try:
            proof=json.loads(receipt.read_text(encoding='utf8'))
            if proof['stage_contract_sha256']!=digest(contract.read_bytes()):continue
            if any(proof['file_sha256'][name]!=digest((p/name).read_bytes()) for name in CHECKPOINT_FILES):continue
        except (KeyError,ValueError,OSError):continue
        result.append((int(p.name[11:]),p))
    return max(result)[1] if result else None


def validate_stage_directory(output, contract, *, resume=False):
    output=private_path(output);path=output/'stage_contract.json'
    if output.exists():
        if not resume:raise FileExistsError('Existing stage preserved; explicitly use --resume for this job.')
        if not path.exists() or json.loads(path.read_text(encoding='utf8'))!=contract:
            raise ValueError('Resume contract mismatch: stage, data, model or optimizer schedule changed.')
    else:
        output.mkdir(parents=True);atomic_json(path,contract)
    return output


def deadline_callback(deadline, reserve_seconds=240):
    from transformers import TrainerCallback
    class CheckpointBeforeDeadline(TrainerCallback):
        reached=False
        def on_step_end(self,args,state,control,**kwargs):
            if time.time()>=deadline-reserve_seconds:
                self.reached=True;control.should_save=True;control.should_training_stop=True
            return control
    return CheckpointBeforeDeadline()


def checkpoint_callback(output):
    from transformers import TrainerCallback
    class CheckedCheckpoint(TrainerCallback):
        def on_save(self,args,state,control,**kwargs):
            seal_checkpoint(output,Path(args.output_dir)/f'checkpoint-{state.global_step}')
            return control
    return CheckedCheckpoint()


def select_grouped(rows, limit):
    """Deterministic task round-robin, one source/event per development prompt."""
    tasks={};seen=set();selected=[]
    for row in sorted(rows,key=lambda r:digest('dev:'+r['id'])):
        tasks.setdefault(row['task'],[]).append(row)
    while tasks and len(selected)<limit:
        for task in list(sorted(tasks)):
            while tasks[task] and tasks[task][0]['group'] in seen:tasks[task].pop(0)
            if tasks[task]:
                row=tasks[task].pop(0);seen.add(row['group']);selected.append(row)
            if not tasks[task]:del tasks[task]
            if len(selected)>=limit:break
    return selected


def train_stage(prepared, output, config, stage, deadline, *, initial_adapter=None,
                resume=False, cpu_fixture=None):
    """One finite stage. cpu_fixture is only for tiny random integration tests."""
    import torch
    from transformers import AutoTokenizer, Trainer, TrainingArguments, set_seed
    from peft import LoraConfig, PeftModel, get_peft_model
    from .qwen_finetune import encode_sample
    set_seed(config['seed'])
    rows=read_rows(Path(prepared)/(stage+'_stage.jsonl'))
    validation=select_grouped(read_rows(Path(prepared)/'validation_encoded.jsonl'),config['validation_rows'])
    if not rows:raise ValueError('Empty curriculum stage')
    max_steps=min(math.ceil(len(rows)/config['gradient_accumulation_steps']),config['stage_max_steps'][stage])
    contract=stage_contract(rows,config,stage,max_steps,initial_adapter)
    output=validate_stage_directory(output,contract,resume=resume)
    saved=output/'stage_status.json'
    if saved.exists():
        prior=json.loads(saved.read_text(encoding='utf8'))
        if prior['state']=='complete':
            if digest((output/'adapter/adapter_model.safetensors').read_bytes())!=prior['adapter_sha256']:
                raise ValueError('Completed adapter changed; existing outputs preserved.')
            return prior
    if time.time()>=deadline-600:
        status={'state':'insufficient_time_before_stage','stage':stage,'production_enabled':False}
        atomic_json(saved,status);return status
    tokenizer,model,compute=cpu_fixture if cpu_fixture is not None else (None,None,None)
    if tokenizer is None:
        tokenizer=AutoTokenizer.from_pretrained(config['model_id'],revision=config['revision'],
                          trust_remote_code=False,local_files_only=True)
        model,compute=load_cuda_base(config,training=True)
    tokenizer.pad_token=tokenizer.pad_token or tokenizer.eos_token
    tokenizer.padding_side='right'
    model=prepare_frozen_base(model,gradient_checkpointing=config['gradient_checkpointing'])
    if initial_adapter:
        model=PeftModel.from_pretrained(model,str(initial_adapter),is_trainable=True)
    else:
        model=get_peft_model(model,LoraConfig(r=config['lora_r'],lora_alpha=config['lora_alpha'],
            lora_dropout=config['lora_dropout'],target_modules=config['target_modules'],bias='none',task_type='CAUSAL_LM'))
    model.print_trainable_parameters()
    callback=deadline_callback(deadline)
    cpu=cpu_fixture is not None
    kwargs={'bf16':str(compute).endswith('bfloat16'),
            'fp16':str(compute).endswith('float16') and not str(compute).endswith('bfloat16')}
    args=TrainingArguments(output_dir=str(output/'trainer'),max_steps=max_steps,
        per_device_train_batch_size=1,per_device_eval_batch_size=1,
        gradient_accumulation_steps=config['gradient_accumulation_steps'],
        learning_rate=config['stage_learning_rates'][stage],warmup_ratio=0.03,lr_scheduler_type='cosine',
        logging_steps=1,save_strategy='steps',save_steps=config['save_steps'],save_total_limit=3,
        eval_strategy='no',gradient_checkpointing=config['gradient_checkpointing'],
        gradient_checkpointing_kwargs={'use_reentrant':False},optim='adamw_torch',
        report_to='none',seed=config['seed'],data_seed=config['seed'],
        dataloader_num_workers=0,remove_unused_columns=False,use_cpu=cpu,
        dataloader_pin_memory=not cpu,**kwargs)
    checkpoint=latest_checkpoint(output) if resume else None
    atomic_json(saved,{'state':'training','stage':stage,'planned_steps':max_steps,
                      'rows':len(rows),'resume_checkpoint':str(checkpoint) if checkpoint else None})
    try:
        if not cpu:torch.cuda.reset_peak_memory_stats()
        trainer=Trainer(model=model,args=args,train_dataset=[r['encoded'] for r in rows],
                    eval_dataset=[r['encoded'] for r in validation],processing_class=tokenizer,
                    data_collator=collator(tokenizer.pad_token_id),callbacks=[callback,checkpoint_callback(output)])
        result=trainer.train(resume_from_checkpoint=str(checkpoint) if checkpoint else None)
        # Also save optimizer/RNG at the normal stage end if the last step was
        # between periodic checkpoints. Adapter alone is not an optimizer resume.
        if trainer.state.global_step and not (output/'trainer'/f'checkpoint-{trainer.state.global_step}').exists():
            trainer._save_checkpoint(trainer.model,trial=None)
        if trainer.state.global_step:seal_checkpoint(output,output/'trainer'/f'checkpoint-{trainer.state.global_step}')
        model.save_pretrained(output/'adapter',safe_serialization=True)
        tokenizer.save_pretrained(output/'adapter')
        validation_metrics=trainer.evaluate() if validation and time.time()<deadline-300 else {'not_run':'deadline_reserve'}
        status={'state':'deadline_checkpointed' if callback.reached else 'complete','stage':stage,
                'steps':trainer.state.global_step,'planned_steps':max_steps,'rows':len(rows),
                'training_metrics':result.metrics,'validation_language_loss':validation_metrics,
                'validation_rows':len(validation),'validation_groups':len({r['group'] for r in validation}),
                'resume_checkpoint':str(checkpoint) if checkpoint else None,
                'adapter':str(output/'adapter'),'optimizer_checkpoint':str(latest_checkpoint(output)),
                'adapter_sha256':digest((output/'adapter/adapter_model.safetensors').read_bytes()),
                'test_set_used_for_selection':False,'prediction_accuracy_verified':False,'production_enabled':False}
        if not cpu:status.update(peak_allocated_gib=torch.cuda.max_memory_allocated()/2**30,
                                peak_reserved_gib=torch.cuda.max_memory_reserved()/2**30)
        atomic_json(saved,status)
        atomic_json(output/'run_status.json',{'state':'complete' if status['state']=='complete' else status['state'],
                    'config':config,'curriculum_schema':VERSION,'production_enabled':False,
                    'prediction_accuracy_verified':False,'stage_status_file':'stage_status.json'})
        return status
    except BaseException as error:
        atomic_json(output/'failure.json',{'type':type(error).__name__,'message':str(error)[:2000],
                    'last_complete_checkpoint':str(latest_checkpoint(output)),'original_outputs_preserved':True})
        raise
    finally:
        # Do not carry the previous 14B allocation into the next stage.
        if 'trainer' in locals():del trainer
        del model
        import gc
        gc.collect()
        if not cpu:torch.cuda.empty_cache()


def measure_answer(raw, row, budget_hit=False):
    """Format / literal similarity diagnostics are not expert correctness."""
    expected=json.loads(row['messages'][-1]['content'])
    value={'id':row['id'],'task':row['task'],'group':row['group'],'raw_output':raw,
           'reached_token_limit':budget_hit,'semantic_correctness_verified':False,'prediction_validated':False}
    try:
        answer=json.loads(raw)
        check_answer(answer,[{'id':uid} for uid in row['source_ids']],'source_study')
        summary=answer['summary'].strip()
        generic=summary in ('以下是来源资料，尚非现实预测验证。','作者书内复盘；可能包含后验解释，不能视为事前命中。')
        a,b=Counter(summary),Counter(expected['summary'])
        overlap=sum((a&b).values())
        value.update(schema_and_citation_passed=True,generic_summary=generic,
                     summary=summary,empty_summary=not summary,
                     literal_character_f1=2*overlap/(sum(a.values())+sum(b.values()) or 1),
                     exact_summary_match=summary==expected['summary'])
    except (ValueError,TypeError,KeyError) as error:
        value.update(schema_and_citation_passed=False,error=str(error))
    return value


def evaluate_pair(data, output, config, adapter, deadline, *, limit=12, cpu_fixture=None):
    """Same fixed validation prompts/seeds, base then adapter in one allocation.

    Validation is development feedback; untouched event-level test is not used
    to select a checkpoint. Raw answers await professional review.
    """
    import torch
    from transformers import AutoTokenizer, set_seed
    from peft import PeftModel
    output=private_path(output);output.mkdir(parents=True,exist_ok=False)
    rows=select_grouped(read_rows(Path(data)/'validation.jsonl'),limit)
    if cpu_fixture:
        tokenizer,base,compute=cpu_fixture
    else:
        tokenizer=AutoTokenizer.from_pretrained(config['model_id'],revision=config['revision'],local_files_only=True)
        base,compute=load_cuda_base(config,training=False)
    model=PeftModel.from_pretrained(base,str(adapter)).eval()
    model.config.use_cache=True
    results=[];budget_skips=[]
    try:
        with (output/'paired_answers.jsonl').open('w',encoding='utf8') as trace:
            for original in rows:
                if time.time()>=deadline-240:break
                row,_,view=fit_training_view(original,tokenizer,config['max_seq_length'])
                if row is None:budget_skips.append(view);continue
                messages=row['messages'][:-1]
                tokens=tokenizer.apply_chat_template(messages,tokenize=True,add_generation_prompt=True,enable_thinking=False)
                new_tokens=min(config['eval_max_new_tokens'],config['inference_max_context']-len(tokens))
                if new_tokens<128:budget_skips.append({'id':row['id'],'reason':'insufficient_generation_budget'});continue
                prompt=torch.tensor([tokens],device=model.device)
                for variant in ('base','adapter'):
                    if time.time()>=deadline-180:break
                    set_seed(config['seed'])
                    with (model.disable_adapter() if variant=='base' else nullcontext()),torch.inference_mode():
                        ids=model.generate(input_ids=prompt,attention_mask=torch.ones_like(prompt),do_sample=False,
                            max_new_tokens=new_tokens,pad_token_id=tokenizer.pad_token_id,eos_token_id=tokenizer.eos_token_id,
                            use_cache=True)
                    generated=ids[0,len(tokens):]
                    raw=tokenizer.decode(generated,skip_special_tokens=True)
                    result=measure_answer(raw,row,len(generated)>=new_tokens)
                    result.update(variant=variant,input_tokens=len(tokens),generated_tokens=len(generated),
                        prompt_sha256=digest(json_text(messages)),view_audit=view,source_ids=row['source_ids'])
                    trace.write(json_text(result)+'\n');trace.flush();results.append(result)
        summary={'state':'complete' if len(results)==2*len(rows) else 'partial_preserving_raw_outputs',
                 'requested_prompts':len(rows),'completed_generations':len(results),'budget_skips':budget_skips,
                 'variants':{},'split':'validation','test_used':False,
                 'semantic_expert_review_complete':False,'production_enabled':False}
        for variant in ('base','adapter'):
            part=[r for r in results if r['variant']==variant]
            summary['variants'][variant]={'generations':len(part),
                'schema_and_citation_passed':sum(r['schema_and_citation_passed'] for r in part),
                'generic_summaries':sum(r.get('generic_summary',False) for r in part),
                'truncated':sum(r['reached_token_limit'] for r in part)}
        write_json(output/'paired_summary.json',summary)
        return summary
    finally:
        del model,base
        import gc
        gc.collect()
        if cpu_fixture is None:torch.cuda.empty_cache()
