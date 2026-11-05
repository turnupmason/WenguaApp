"""Independent v5 course. Reuses the frozen training math without editing v4."""
from pathlib import Path
from . import qwen_course_training_v4 as v4
from . import qwen8b_book_v1 as old
from .course_complete_v5 import SCHEMA,sha,load

storage=v4.storage
ROOT=storage.ROOT
DATA=ROOT/'local/course_v5_data'
RELEASE=ROOT/'data/knowledge/course_v5/release.json'
CONFIG=ROOT/'configs/course_v5.json'
SPEC=ROOT/'configs/course_v5_sweep.json'
FILES=('src/wengua/course_complete_v5.py','src/wengua/course_training_v5.py',
 'src/wengua/course_process_v5.py','scripts/course_v5.py','run_course_v5.py',
 'run_course_v5_worker.py','train_wengua_v5.cmd','configs/course_v5.json',
 'configs/course_v5_sweep.json','data/knowledge/course_v5/release.json')
SWEEP_SCHEMA=SCHEMA
parameter_signature=v4.parameter_signature
training_integrity=v4.training_integrity


def hashes():return v4.hashes()|{name:sha((ROOT/name).read_bytes()) for name in FILES}


def validate_rows(rows,units,case_splits=None):
    if not rows:raise ValueError('Empty course')
    prompts={};ids=set()
    for r in rows:
        if r['id'] in ids:raise ValueError('Duplicate task ID')
        ids.add(r['id'])
        if r['split'] not in ('train','validation','test'):raise ValueError('Invalid split')
        if not r['source_ids'] or any(x not in units or units[x]['book_id'] not in ('shenqi','kaiwu') for x in r['source_ids']):
            raise ValueError('Missing or non-book evidence')
        if not r['answer'].strip() or r['messages'][-1]!={'role':'assistant','content':r['answer']}:
            raise ValueError('Answer/target mismatch')
        prompt=storage.dumps(r['messages'][:-1])
        if prompt in prompts and prompts[prompt]!=r['answer']:raise ValueError('Conflicting prompt targets')
        prompts[prompt]=r['answer']
        if any(marker in r['answer'] for marker in ('HEALTH_V9_V11','STRENGTH_200','candidate_five_grade_quantization','以下是来源资料，尚非现实预测验证')):
            raise ValueError('Legacy scoring or non-answer boilerplate')
        if case_splits is not None:
            for cid in r['case_ids']:
                if cid not in case_splits:raise ValueError('Unknown historical event')
                if case_splits[cid]!='train' and r['split']=='train':raise ValueError('Case holdout leakage')
    return {'rows':len(rows),'conflicting_prompts':0,'production_enabled':False}


def verify_data(root=DATA,release=None):
    root=Path(root);release=release or load(RELEASE)
    for name,digest in release['files'].items():
        path=root/name
        if not path.is_relative_to(root) or not path.is_file() or sha(path.read_bytes())!=digest:
            raise ValueError('Reviewed dataset file missing/changed: '+name)
    pack=load(root/'pack.json')
    if pack['schema']!=SCHEMA or pack['summary']['schema']!=SCHEMA or pack['source_sha256']!=storage.SOURCE_SHA256:
        raise ValueError('Not the pinned v5 two-book course')
    validate_rows(pack['records'],pack['units'],pack['case_splits'])
    audit=load(root/'token_audit.json')
    if audit['exclusions'] or audit['generation_skips']:raise ValueError('Unresolved token exclusions')
    return pack


def prepare(job,c,*,tokenizer=None,pack=None,testing=False):
    prepared=Path(job)/'prepared'
    if (prepared/'receipt.json').exists():
        meta=load(prepared/'receipt.json')
        if meta['config']!=c:raise ValueError('Prepared v5 configuration changed')
        for name,digest in meta['file_sha256'].items():
            if storage.file_sha(prepared/name)!=digest:raise ValueError('Prepared v5 data changed')
        return meta
    if prepared.exists():raise ValueError('Incomplete preparation preserved')
    pack=pack if testing and pack is not None else verify_data()
    validate_rows(pack['records'],pack['units'],pack.get('case_splits'))
    tokenizer=tokenizer or storage.load_book_tokenizer(c)
    tokenizer.pad_token=tokenizer.pad_token or tokenizer.eos_token;tokenizer.padding_side='right'
    pending=prepared.with_name('prepared.pending')
    if pending.exists():raise ValueError('Incomplete pending v5 data preserved')
    pending.mkdir(parents=True);tokenizer.save_pretrained(pending/'tokenizer')
    storage.write_rows(pending/'core_records.jsonl.gz',pack['records'])
    storage.write_rows(pending/'source_units.jsonl.gz',pack['units'].values())
    bysplit={s:[] for s in ('train','validation','test')}
    for core in pack['records']:
        for row in storage.target_views(core,0):
            encoded,size=storage.encode(row,tokenizer,c['max_seq_length'])
            if encoded is None:raise ValueError('Whole target exceeds context; course must be revised: '+row['id'])
            bysplit[row['split']].append(row|{'encoded':encoded,'tokens':size})
    if not all(bysplit.values()):raise ValueError('Missing course split')
    train=sorted(bysplit['train'],key=lambda r:sha('v5-train:'+r['id']))
    storage.write_rows(pending/'cycle_01.jsonl.gz',train)
    stress=old.stress_rows(train,c['smoke_steps'],c['gradient_accumulation_steps'])
    storage.write_rows(pending/'smoke.jsonl.gz',stress)
    storage.write_rows(pending/'validation_loss.jsonl.gz',storage.grouped_select(bysplit['validation'],c['validation_rows']))
    for split,count in [('validation',c['validation_generation_rows']),('test',c['test_generation_rows'])]:
        fit,skips=storage.generation_rows([r for r in pack['records'] if r['split']==split],tokenizer,c)
        if skips:raise ValueError('Generation budget excludes reviewed targets: '+split)
        storage.write_rows(pending/(split+'_prompts.jsonl.gz'),storage.grouped_select(fit,count))
    storage.atomic_json(pending/'length_exclusions.json',[])
    storage.atomic_json(pending/'stress_plan.json',{'updates':c['smoke_steps'],'rows':len(stress),
        'max_actual_tokens':max(r['tokens'] for r in stress),'max_context_setting':c['max_seq_length'],
        'full_context_capacity_proven':False})
    meta={'schema':SCHEMA,'config':c,'reviewed_course':True,'semantic_infallibility_claimed':False,
        'file_sha256':{p.relative_to(pending).as_posix():storage.file_sha(p) for p in pending.rglob('*') if p.is_file()},
        'excluded_training_views':0,'training_rows':len(train),'stress_protocol':'reviewed_actual_length_mix'}
    storage.atomic_json(pending/'receipt.json',meta);pending.rename(prepared);return meta


# Function globals are isolated. Contextmanager checks are generic graph checks;
# the original v4 profile and its function defaults are never mutated.
_bound=old.bind(v4,__name__+'._isolated',SCHEMA=SCHEMA,SWEEP_SCHEMA=SCHEMA,DATA=DATA,
                RELEASE=RELEASE,CONFIG=CONFIG,SPEC=SPEC)
_bound.hashes=hashes;_bound.verify_data=verify_data;_bound.prepare=prepare
_bound.validate_rows=validate_rows
_bound.install_archive.__defaults__=(DATA,None)
install_archive=_bound.install_archive
profile=_bound.profile
