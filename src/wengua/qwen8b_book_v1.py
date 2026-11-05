"""Pinned 8B profile over isolated namespaces of the existing book kernels.

Shared source files remain byte-identical for 14B recovery. Each clone's
functions resolve globals in its own module dictionary, never the old modules.
"""
from collections import Counter
from pathlib import Path
from types import ModuleType,FunctionType,SimpleNamespace

from . import qwen_book_loop_v3 as old_book
from . import qwen_book_continuous_v1 as old_engine
from . import qwen_book_sweep_v2 as old_sweep

MODEL='Qwen/Qwen3-8B'
REVISION='b968826d9c46dd6066d109eabc6255188de91218'
CONFIG=old_book.ROOT/'configs/qwen8b_book_v1.json'
SPEC=old_book.ROOT/'configs/qwen8b_book_sweep_v1.json'
BOOK_SCHEMA='wengua_qwen8b_book_v1'
ENGINE_SCHEMA='wengua_qwen8b_continuous_v1'
SWEEP_SCHEMA='wengua_qwen8b_sweep_v1'
ALLOCATOR='backend:native,max_split_size_mb:128'
FILES=(*old_book.KERNELS,'src/wengua/qwen_book_sweep_v1.py','src/wengua/qwen_book_continuous_v1.py',
    'src/wengua/qwen_book_sweep_v2.py','src/wengua/qwen_book_process_v1.py','src/wengua/qwen8b_book_v1.py',
    'src/wengua/qwen8b_loss_v1.py','src/wengua/qwen8b_process_v1.py','scripts/qwen8b_research.py',
    'run_qwen8b_research.py','run_qwen8b_worker.py','configs/qwen8b_book_v1.json','configs/qwen8b_book_sweep_v1.json')


def bind(original,name,**overrides):
    module=ModuleType(name);module.__dict__.update(original.__dict__)
    module.__dict__.update(__name__=name,**overrides)
    for key,value in original.__dict__.items():
        # functools.wraps changes __module__ on contextlib wrappers whose real
        # globals are contextlib's. Keep those generic lock/awake helpers intact.
        if isinstance(value,FunctionType) and value.__globals__ is original.__dict__:
            clone=FunctionType(value.__code__,module.__dict__,value.__name__,value.__defaults__,value.__closure__)
            clone.__kwdefaults__=value.__kwdefaults__;clone.__annotations__=value.__annotations__
            module.__dict__[key]=clone
    return module


def hashes():return {name:old_book.digest((old_book.ROOT/name).read_text(encoding='utf8')) for name in FILES}


def validate(c,*,testing=False):
    if c.get('schema')!=BOOK_SCHEMA or c.get('model_id')!=MODEL or c.get('revision')!=REVISION:
        raise ValueError('Pinned fresh Qwen3-8B book-only configuration required')
    if any(c.get(k) is not False for k in ('production_enabled','old_adapters_allowed','non_book_teachers_allowed')):
        raise ValueError('Legacy teachers/adapters and production prohibited')
    if any(k in c for k in ('initial_adapter','adapter_run','teacher_model')):raise ValueError('No external adapter/teacher input')
    for key,lo,hi in [('cycles',1,1),('max_seq_length',512,4096),('inference_max_context',512,4096),
        ('eval_max_new_tokens',1,1024),('save_steps',1,100),('smoke_steps',2 if testing else 100,200),
        ('patience',1,6),('gradient_accumulation_steps',1,64),('max_steps_per_cycle',1,2000),
        ('validation_rows',1,256),('validation_generation_rows',1,64),('test_generation_rows',1,128)]:
        if type(c[key]) is not int or not lo<=c[key]<=hi:raise ValueError('Invalid bounded '+key)
    if c['max_seq_length']!=c['inference_max_context'] or c['eval_max_new_tokens']>=c['inference_max_context']:raise ValueError('Context budget')
    if not 0<c['learning_rate']<=0.001 or not 0<=c['minimum_loss_improvement']<1:raise ValueError('Optimization range')
    if type(c['lora_r']) is not int or not 1<=c['lora_r']<=32 or c['lora_alpha']!=2*c['lora_r']:raise ValueError('Bounded rank and alpha=2r required')
    if not 0<=c['lora_dropout']<=0.2:raise ValueError('Dropout')
    modules=c['target_modules']
    if not modules or len(set(modules))!=len(modules) or any(m not in ('q_proj','k_proj','v_proj','o_proj','gate_proj','up_proj','down_proj') for m in modules):raise ValueError('Explicit projection targets required')
    if c.get('loss_mode')!='checkpointed_supervised_ce_v1' or c.get('loss_chunk_tokens')!=128 or c.get('allocator_config')!=ALLOCATOR:
        raise ValueError('Pinned bounded-memory loss/allocator required')
    return c


def doctor(c):
    import torch
    report={'cuda_available':torch.cuda.is_available(),'model_id':MODEL,'cuda_devices':[],
        'dependencies':old_book.stack_versions(),'training_fit_verified':False}
    reason='CUDA GPU unavailable';ready=False
    if report['cuda_available']:
        index=torch.cuda.current_device();free,total=torch.cuda.mem_get_info(index)
        device={'index':index,'name':torch.cuda.get_device_name(index),'free_gib':free/2**30,'total_gib':total/2**30}
        report.update(current_device_index=index,cuda_devices=[device])
        ready=free>=12*2**30 and total>=12*2**30
        reason='Conservative 12 GiB launch screen passed; pressure run still required' if ready else 'Need 12 GiB total and free VRAM for this bounded all-GPU 8B launch screen'
    report['training_preflight']={'status':'ready_for_smoke_test' if ready else 'blocked','reason':reason}
    return report


def load_cuda(c,training):
    import torch
    from transformers import AutoModelForCausalLM,BitsAndBytesConfig
    assessment=doctor(c)
    if assessment['training_preflight']['status']!='ready_for_smoke_test':raise RuntimeError(assessment['training_preflight']['reason'])
    compute=torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
    quant=BitsAndBytesConfig(load_in_4bit=True,bnb_4bit_quant_type='nf4',bnb_4bit_use_double_quant=True,bnb_4bit_compute_dtype=compute)
    model=AutoModelForCausalLM.from_pretrained(MODEL,revision=REVISION,quantization_config=quant,
        device_map={'':torch.cuda.current_device()},dtype=compute,attn_implementation='sdpa',trust_remote_code=False,local_files_only=True)
    model.config.use_cache=not training;return model,compute


def stress_rows(rows,updates,accumulation):
    size=min(len(rows),updates*accumulation);selected={}
    def add(row):
        if len(selected)<size:selected.setdefault(row['id'],row)
    ranked=sorted(rows,key=lambda r:(-r['tokens'],r['id']))
    for row in ranked[:min(64,max(1,size//8))]:add(row)
    dense=sorted(rows,key=lambda r:(-sum(x!=-100 for x in r['encoded']['labels']),r['id']))
    for row in dense[:min(64,max(1,size//8))]:add(row)
    buckets=[ranked[i*len(ranked)//4:(i+1)*len(ranked)//4] for i in range(4)]
    buckets=[sorted(bucket,key=lambda r:old_book.digest('8b-pressure:'+r['id'])) for bucket in buckets]
    for n in range(max(map(len,buckets))):
        for bucket in buckets:
            if n<len(bucket):add(bucket[n])
    return sorted(selected.values(),key=lambda r:old_book.digest('pressure-order:'+r['id']))


def profile(*,testing=False):
    book=bind(old_book,'src.wengua._qwen8b_book',SCHEMA=BOOK_SCHEMA,CONFIG=CONFIG,MODEL_REVISION=REVISION)
    def load_config(path=CONFIG,cycles=None):
        c=book.read_json(path)
        if cycles is not None:c['cycles']=cycles
        return validate(c,testing=testing)
    book.load_config=load_config;book.load_book_cuda=load_cuda;book.normalized_kernel_hashes=hashes
    original_prepare=book.prepare
    def prepare(job,c,tokenizer=None,pack=None):
        meta=original_prepare(job,c,tokenizer=tokenizer,pack=pack)
        if meta.get('stress_protocol')=='variable_lengths_dense_targets_v1':return meta
        if (job/'smoke').exists() or (job/'cycle_01').exists():raise ValueError('Cannot rewrite prepared pressure data after training started')
        path=job/'prepared';rows=book.read_rows(path/'cycle_01.jsonl.gz')
        chosen=stress_rows(rows,c['smoke_steps'],c['gradient_accumulation_steps'])
        book.write_rows(path/'smoke.jsonl.gz',chosen)
        plan={'protocol':'variable_lengths_dense_targets_v1','optimizer_updates':c['smoke_steps'],'rows':len(chosen),
            'min_tokens':min(r['tokens'] for r in chosen),'max_tokens':max(r['tokens'] for r in chosen),
            'formats':dict(Counter(r['format'] for r in chosen)),'longest_and_dense_targets_included':True,'no_truncation':True}
        book.atomic_json(path/'stress_plan.json',plan);meta['stress_protocol']=plan['protocol']
        for name in ('smoke.jsonl.gz','stress_plan.json'):meta['file_sha256'][name]=book.file_sha(path/name)
        book.atomic_json(path/'receipt.json',meta);return meta
    book.prepare=prepare
    engine=bind(old_engine,'src.wengua._qwen8b_engine',SCHEMA=ENGINE_SCHEMA,book=book)
    engine.validate_structure=lambda c:validate(c,testing=testing);engine.code_hashes=hashes
    def open_job(path,c,*,resume):
        path=book.private_output(path)
        contract={'schema':ENGINE_SCHEMA,'config':engine.validate(c),'code_sha256':hashes(),
            'source_database_sha256':book.SOURCE_SHA256,'coordinates_sha256':book.digest(book.COORDINATES.read_text(encoding='utf8')),
            'initialization':'tiny_random_fixture' if testing else 'official_pinned_base_new_adapter',
            'software_fixture_only':testing,'initial_adapter':None,'test_used_for_selection':False}
        if path.exists():
            if not resume or not (path/'job_contract.json').exists() or book.read_json(path/'job_contract.json')!=contract:
                raise ValueError('8B job contract changed or belongs to another model; preserve it and choose a new output')
        else:path.mkdir(parents=True);book.atomic_json(path/'job_contract.json',contract)
        return path
    engine.open_job=open_job
    sweep=bind(old_sweep,'src.wengua._qwen8b_sweep',SCHEMA=SWEEP_SCHEMA,SPEC=SPEC,engine=engine,book=book)
    return SimpleNamespace(book=book,engine=engine,sweep=sweep,doctor=doctor,testing=testing)
