"""New-data namespace and private release verification; old kernels stay frozen."""
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import patch
import json
import math
import os
import zipfile

from . import qwen8b_book_v1 as old
from . import qwen_book_loop_v3 as storage
from .qwen_course_v4 import SCHEMA, validate_rows, sha, load

RELEASE=storage.ROOT/'data/knowledge/qwen_course_v4/release.json'
SWEEP_SCHEMA=SCHEMA
CONFIG=storage.ROOT/'configs/qwen_course_v4.json'
SPEC=storage.ROOT/'configs/qwen_course_v4_sweep.json'
DATA=storage.ROOT/'local/qwen_course_v4_data'
FILES=('src/wengua/qwen8b_diagnostics_v1.py','src/wengua/qwen_course_v4.py','src/wengua/qwen_course_training_v4.py',
       'src/wengua/qwen_course_process_v4.py','scripts/qwen_course_v4.py',
       'run_qwen_course_v4.py','run_qwen_course_v4_worker.py',
       'configs/qwen_course_v4.json','configs/qwen_course_v4_sweep.json',
       'data/knowledge/qwen_course_v4/release.json')


def hashes():
    return old.hashes() | {name:sha((storage.ROOT/name).read_bytes()) for name in FILES}


def verify_data(root=DATA, release=None):
    root=Path(root);release=release or load(RELEASE)
    for name,digest in release['files'].items():
        p=root/name
        if not p.is_relative_to(root) or not p.is_file() or sha(p.read_bytes())!=digest:
            raise ValueError('Reviewed dataset file missing/changed: '+name)
    pack=load(root/'pack.json')
    if pack['summary']['schema']!=SCHEMA or pack['source_sha256']!=storage.SOURCE_SHA256:
        raise ValueError('Not the reviewed v4 book release')
    validate_rows(pack['records'],pack['units'])
    return pack


def install_archive(archive, destination=DATA, release=None):
    release=release or load(RELEASE);archive=Path(archive);destination=storage.private_output(destination)
    if sha(archive.read_bytes())!=release['archive_sha256']:raise ValueError('Wrong dataset ZIP SHA256')
    if destination.exists():verify_data(destination,release);return destination
    staging=destination.with_name(destination.name+'.pending')
    if staging.exists():raise ValueError('Incomplete extraction preserved: '+str(staging))
    with zipfile.ZipFile(archive) as z:
        members=z.namelist()
        if len(members)!=len(set(members)) or set(members)!=set(release['files']):raise ValueError('Unexpected ZIP members')
        if any(Path(n).is_absolute() or '..' in Path(n).parts or '\\' in n for n in members):raise ValueError('Unsafe ZIP path')
        staging.mkdir(parents=True)
        for name in members:
            p=staging/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(z.read(name))
    verify_data(staging,release);staging.rename(destination);return destination


def parameter_signature(model):
    """Check the actual graph, rather than hiding malformed parameter iterators."""
    signature=[];names=set();objects=set()
    try:
        for item in model.named_parameters():
            if not isinstance(item,tuple) or len(item)!=2:raise ValueError('named_parameters must yield (name, parameter)')
            name,param=item
            if not isinstance(name,str) or name in names or id(param) in objects or not hasattr(param,'shape'):
                raise ValueError('Duplicate/invalid parameter graph')
            names.add(name);objects.add(id(param));signature.append((name,id(param),tuple(param.shape),param.requires_grad))
    except Exception as error:
        raise RuntimeError('Parameter graph integrity check failed: '+str(error)) from error
    if not signature:raise RuntimeError('Empty parameter graph')
    return tuple(signature)


@contextmanager
def training_integrity():
    from transformers import Trainer, TrainerCallback
    class Integrity(TrainerCallback):
        signature=None
        def on_train_begin(self,args,state,control,**kw):
            self.signature=parameter_signature(kw['model'])
            storage.progress('v4_parameter_graph_checked',parameters=len(self.signature),flop_telemetry='disabled')
        def on_step_end(self,args,state,control,**kw):
            if state.global_step%25==0 and parameter_signature(kw['model'])!=self.signature:
                raise RuntimeError('Parameter identities/shapes/trainability changed while training')
            return control
        def on_train_end(self,args,state,control,**kw):
            if parameter_signature(kw['model'])!=self.signature:raise RuntimeError('Parameter graph changed')
    # FLOP telemetry does not affect gradients. Avoid the old per-microbatch
    # recursive num_parameters path; still inspect graph at start/every 25 updates/end.
    with patch.object(Trainer,'floating_point_ops',lambda self,inputs:0):yield Integrity()


def prepare(job,c,*,tokenizer=None,pack=None,testing=False):
    prepared=Path(job)/'prepared';receipt=prepared/'receipt.json'
    if receipt.exists():
        meta=storage.read_json(receipt)
        if meta['config']!=c:raise ValueError('Prepared v4 configuration changed')
        for name,digest in meta['file_sha256'].items():
            if storage.file_sha(prepared/name)!=digest:raise ValueError('Prepared v4 data changed: '+name)
        return meta
    if prepared.exists():raise ValueError('Incomplete preparation preserved; restore/remove only this pre-training cache after inspection')
    pack=pack if testing and pack is not None else verify_data()
    validate_rows(pack['records'],pack['units'])
    if tokenizer is None:tokenizer=storage.load_book_tokenizer(c)
    tokenizer.pad_token=tokenizer.pad_token or tokenizer.eos_token;tokenizer.padding_side='right'
    pending=prepared.with_name('prepared.pending')
    if pending.exists():raise ValueError('Incomplete v4 preparation preserved: '+str(pending))
    pending.mkdir(parents=True);tokenizer.save_pretrained(pending/'tokenizer')
    storage.write_rows(pending/'core_records.jsonl.gz',pack['records'])
    storage.write_rows(pending/'source_units.jsonl.gz',pack['units'].values())
    bysplit={x:[] for x in ('train','validation','test')};excluded=[]
    for core in pack['records']:
        for row in storage.target_views(core,0):
            encoded,size=storage.encode(row,tokenizer,c['max_seq_length'])
            if encoded:bysplit[core['split']].append(row|{'encoded':encoded,'tokens':size})
            else:excluded.append({'id':row['id'],'split':core['split'],'tokens':size,'policy':'whole target excluded; never truncated'})
    if not bysplit['train'] or not bysplit['validation']:raise ValueError('No complete train/validation targets fit')
    train=sorted(bysplit['train'],key=lambda r:sha('v4-train:'+r['id']))
    storage.write_rows(pending/'cycle_01.jsonl.gz',train)
    stress=old.stress_rows(train,c['smoke_steps'],c['gradient_accumulation_steps'])
    storage.write_rows(pending/'smoke.jsonl.gz',stress)
    validation=storage.grouped_select(bysplit['validation'],c['validation_rows'])
    storage.write_rows(pending/'validation_loss.jsonl.gz',validation)
    for split,count in [('validation',c['validation_generation_rows']),('test',c['test_generation_rows'])]:
        accepted,_=storage.generation_rows([r for r in pack['records'] if r['split']==split],tokenizer,c)
        chosen=storage.grouped_select(accepted,count)
        if not chosen:raise ValueError('No generation targets fit '+split)
        storage.write_rows(pending/(split+'_prompts.jsonl.gz'),chosen)
    storage.atomic_json(pending/'length_exclusions.json',excluded)
    # Real long examples only. Synthetic filler is never used to inflate a pressure claim.
    stress_plan={'updates':c['smoke_steps'],'rows':len(stress),'max_actual_tokens':max(r['tokens'] for r in stress),
                 'max_context_setting':c['max_seq_length'],'full_context_capacity_proven':False}
    storage.atomic_json(pending/'stress_plan.json',stress_plan)
    meta={'schema':SCHEMA,'config':c,'reviewed_course':True,'semantic_infallibility_claimed':False,
          'file_sha256':{p.relative_to(pending).as_posix():storage.file_sha(p) for p in pending.rglob('*') if p.is_file()},
          'excluded_training_views':sum(x['split']=='train' for x in excluded),'training_rows':len(train),'stress_protocol':'reviewed_actual_length_mix'}
    storage.atomic_json(pending/'receipt.json',meta);pending.rename(prepared);return meta


def profile(*,testing=False):
    p=old.profile(testing=testing);b=p.book;e=p.engine;s=p.sweep
    def validate(c):
        if c.get('schema')!=SCHEMA:raise ValueError('Reviewed v4 schema required')
        return old.validate(c|{'schema':old.BOOK_SCHEMA},testing=testing) and c
    b.CONFIG=CONFIG;b.SCHEMA=SCHEMA;b.DATA_VERSION=SCHEMA;b.normalized_kernel_hashes=hashes
    b.load_config=lambda path=CONFIG,cycles=None:validate(load(path))
    b.prepare=lambda job,c,tokenizer=None,pack=None:prepare(job,c,tokenizer=tokenizer,pack=pack,testing=testing)
    e.SCHEMA=SCHEMA;e.code_hashes=hashes;e.validate_structure=validate
    e.base_config=lambda:load(CONFIG)
    def open_job(path,c,*,resume):
        path=b.private_output(path)
        contract={'schema':SCHEMA,'config':e.validate(c),'code_sha256':hashes(),
                  'dataset_release_sha256':sha(RELEASE.read_bytes()),'initial_adapter':None,
                  'initialization':'tiny_fixture' if testing else 'official_pinned_base_new_adapter'}
        if path.exists():
            if not resume or not (path/'job_contract.json').exists() or b.read_json(path/'job_contract.json')!=contract:
                raise ValueError('v4 resume contract changed; never adopt old data/adapter/checkpoint')
        else:path.mkdir(parents=True);b.atomic_json(path/'job_contract.json',contract)
        return path
    e.open_job=open_job
    original_fit=e.fit
    def fit(job,c,deadline,*,extra_callbacks=(),**kwargs):
        with training_integrity() as check:
            return original_fit(job,c,deadline,extra_callbacks=(*extra_callbacks,check),**kwargs)
    e.fit=fit;s.SCHEMA=SCHEMA;s.SPEC=SPEC
    return p
