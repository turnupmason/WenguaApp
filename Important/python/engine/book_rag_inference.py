"""Read-only 8B LoRA inference over a complete, sealed WenguaApp course run."""
from pathlib import Path
import gc,time
from contextlib import ExitStack,nullcontext
from . import book_rag as r
from .book_rag_query import check_answer


def verified_adapter(path,*,testing=False):
    path=r.private(path);stage=path.parent.parent;job=stage.parent
    if path.parent.name!='adapters' or stage.name!='cycle_01':raise ValueError('Use a sealed formal epoch adapter; pressure weights are forbidden')
    contract=r.read(job/'job_contract.json');schema=contract['schema']
    from . import qwen_course_training_v4 as v4,course_training_v5 as v5,course_training_v51 as v51
    modules={v4.SCHEMA:v4,v5.SCHEMA:v5,v51.SCHEMA:v51}
    if schema not in modules:raise ValueError('Only pinned WenguaApp pure-book V4/V5/V5.1 adapters are accepted')
    module=modules[schema];profile=module.profile(testing=testing)
    if contract['code_sha256']!=module.hashes():raise ValueError('Training runtime differs from this checked-out version; preserve its original files')
    if contract['dataset_release_sha256']!=r.digest(module.RELEASE.read_bytes()):raise ValueError('Adapter dataset provenance mismatch')
    profile.book.checked_adapter(path)
    status=r.read(stage/'stage_status.json')
    if status.get('state')!='complete':raise ValueError('Training/evaluation is still active or incomplete; keep training running, infer after completion')
    c=contract['config'];cfg=r.read(path/'adapter_config.json')
    if c['model_id']!='Qwen/Qwen3-8B' or c['revision']!='b968826d9c46dd6066d109eabc6255188de91218':raise ValueError('Adapter is not the pinned 8B base')
    if c.get('non_book_teachers_allowed') is not False or c.get('production_enabled') is not False:raise ValueError('Unknown teacher policy')
    if (cfg['r']!=c['lora_r'] or cfg['lora_alpha']!=c['lora_alpha'] or set(cfg['target_modules'])!=set(c['target_modules'])):raise ValueError('LoRA structure mismatch')
    return profile,c,{'schema':schema,'adapter':str(path),'adapter_sha256':r.digest((path/'adapter_model.safetensors').read_bytes()),
        'job_contract_sha256':r.digest((job/'job_contract.json').read_bytes()),'stage_status_sha256':r.digest((stage/'stage_status.json').read_bytes()),
        'weights_modified':False,'model_id':c['model_id'],'revision':c['revision']}


def answer(prompt,adapter,output,*,cpu_factory=None,base_only=False):
    if prompt['state']!='ready':raise ValueError('No complete evidence bundle fits; narrow the question or inspect sources before loading GPU')
    profile,c,proof=verified_adapter(adapter,testing=cpu_factory is not None)
    output=r.private(output)
    if output.exists():raise ValueError('Inference trace is immutable; choose a new output')
    if prompt['prompt_budget']['context_limit']>c['inference_max_context']:raise ValueError('Prompt exceeds trained inference contract')
    import os
    if cpu_factory is None:
        os.environ['PYTORCH_CUDA_ALLOC_CONF']=c['allocator_config'];os.environ['PYTORCH_ALLOC_CONF']=c['allocator_config']
    import torch
    from peft import PeftModel
    from .qwen8b_attention_v1 import cuda_probe,attention_route
    from .qwen_book_loop_v3 import generation_autocast
    model=base=None;started=time.time();trace={'schema':r.SCHEMA,'question':prompt['question'],
        'prompt':prompt,'adapter_provenance':proof,
        'rag_runtime_sha256':{p:r.digest((r.ROOT/p).read_bytes()) for p in ('src/wengua/book_rag.py','src/wengua/book_rag_query.py','src/wengua/book_rag_inference.py','scripts/wengua_rag.py')},'source_citations_are_not_semantic_verification':True}
    stage=Path(adapter).parent.parent;job=stage.parent
    with ExitStack() as stack:
        stack.enter_context(profile.book.job_lock(job/'run.lock'))
        stack.enter_context(profile.book.job_lock(job.parent.parent/'isolated_gpu_worker.lock'))
        try:
            if cpu_factory:tokenizer,base,compute=cpu_factory();report=None
            else:
                assessment=profile.doctor(c)
                if assessment['training_preflight']['status']!='ready_for_smoke_test':raise RuntimeError('GPU is occupied or unavailable; finish training before RAG model inference. '+assessment['training_preflight']['reason'])
                report=cuda_probe()
                if report['state']!='ready':raise RuntimeError('Existing fused attention preflight did not pass')
                from transformers import AutoTokenizer
                tokenizer=AutoTokenizer.from_pretrained(c['model_id'],revision=c['revision'],local_files_only=True,trust_remote_code=False)
                base,compute=profile.book.load_book_cuda(c,training=False)
            model=PeftModel.from_pretrained(base,str(adapter),is_trainable=False).eval();model.config.use_cache=True
            tokens=tokenizer.apply_chat_template(prompt['messages'],tokenize=True,add_generation_prompt=True,enable_thinking=False)
            if len(tokens)!=prompt['prompt_budget']['input_tokens']:raise ValueError('Tokenizer/template differs from the budgeted prompt')
            max_new=prompt['prompt_budget']['max_new_tokens']
            if len(tokens)+max_new>prompt['prompt_budget']['context_limit']:raise ValueError('Unbudgeted prompt; no truncation allowed')
            ids=torch.tensor([tokens],device=model.device)
            with (attention_route(testing=cpu_factory is not None,report=report) as attention,
                  torch.inference_mode(),generation_autocast(model),
                  model.disable_adapter() if base_only else nullcontext()):
                generated=model.generate(input_ids=ids,attention_mask=torch.ones_like(ids),do_sample=False,
                    max_new_tokens=max_new,logits_to_keep=1,pad_token_id=tokenizer.pad_token_id or tokenizer.eos_token_id)
            raw=tokenizer.decode(generated[0,len(tokens):],skip_special_tokens=True)
            result=check_answer(raw,prompt)
            if generated.shape[-1]-len(tokens)>=max_new:result['status']='incomplete_token_limit'
            trace.update(answer=raw,checks=result,variant='base_with_rag' if base_only else 'trained_adapter_with_rag',attention_path=dict(attention),generated_tokens=int(generated.shape[-1]-len(tokens)),
                reached_token_limit=generated.shape[-1]-len(tokens)>=max_new,runtime_seconds=time.time()-started,
                actual_cuda_inference=cpu_factory is None,production_enabled=False)
            r.write(output,trace)
            return {'answer':raw,'checks':result,'references':prompt['references'],'trace_path':str(output)}
        except BaseException as error:
            trace.update(error={'type':type(error).__name__,'message':str(error)},production_enabled=False)
            r.write(output,trace);raise
        finally:
            model=base=None;gc.collect()
            if cpu_factory is None and torch.cuda.is_available():torch.cuda.empty_cache()
