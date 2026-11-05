"""Verified pure-book LoRA warm starts; never migrate an optimizer across data."""
from pathlib import Path
import shutil
from .qwen_book_loop_v3 import ROOT,read_json,atomic_json,file_sha,CKPT_REQUIRED,private_output

# Only the actual known pure-book schemas, never a caller-supplied label.
from .qwen_course_v4 import SCHEMA as V4_SCHEMA
APPROVED={V4_SCHEMA,'wengua_source_accounted_course_v5'}
ESSENTIAL=('adapter_config.json','adapter_model.safetensors')


def inspect_parent(path,*,testing=False):
    path=private_output(Path(path).resolve())
    if path.name.startswith('checkpoint-') and path.parent.name=='trainer':
        stage=path.parent.parent;receipt=read_json(path/'resume_receipt.json')
        if receipt['contract_sha256']!=file_sha(stage/'stage_contract.json'):raise ValueError('Parent checkpoint contract mismatch')
        required=CKPT_REQUIRED;kind='sealed_optimizer_checkpoint_weights_only'
    elif path.name.startswith('step-') and path.parent.name=='adapters':
        stage=path.parent.parent;receipt=read_json(path/'book_adapter_receipt.json')
        if receipt['stage_contract_sha256']!=file_sha(stage/'stage_contract.json'):raise ValueError('Parent adapter contract mismatch')
        required=ESSENTIAL;kind='sealed_epoch_adapter'
    else:raise ValueError('Select a sealed formal cycle_01 checkpoint or epoch adapter')
    if stage.name!='cycle_01':raise ValueError('Pressure/probe weights cannot initialize a formal phase')
    contract=read_json(stage/'stage_contract.json');job=stage.parent;jobc=read_json(job/'job_contract.json')
    if contract['schema'] not in APPROVED or contract['schema']!=jobc['schema']:raise ValueError('Parent must be approved V4/V5 pure-book course')
    if contract['job_contract_sha256']!=file_sha(job/'job_contract.json'):raise ValueError('Parent job provenance mismatch')
    manifest=ROOT/('data/knowledge/qwen_course_v4/release.json' if contract['schema']==V4_SCHEMA else 'data/knowledge/course_v5/release.json')
    if jobc.get('dataset_release_sha256')!=file_sha(manifest):raise ValueError('Parent is not a pinned reviewed book release')
    c=contract['config'];cfg=read_json(path/'adapter_config.json')
    if any(not (path/x).is_file() or not (path/x).stat().st_size for x in required):raise ValueError('Incomplete parent checkpoint')
    if any(file_sha(path/n)!=digest for n,digest in receipt['files'].items()):raise ValueError('Parent receipt file changed')
    from .qwen8b_book_v1 import MODEL,REVISION
    if c['model_id']!=MODEL or c['revision']!=REVISION:raise ValueError('Parent base/revision incompatible')
    if cfg.get('base_model_name_or_path')!=MODEL and not testing:raise ValueError('Adapter base is not pinned Qwen3-8B')
    for k,a in [('lora_r','r'),('lora_alpha','lora_alpha'),('lora_dropout','lora_dropout')]:
        if c[k]!=cfg[a]:raise ValueError('Parent LoRA structure mismatch: '+k)
    if set(c['target_modules'])!=set(cfg['target_modules']) or cfg.get('bias')!='none' or cfg.get('peft_type')!='LORA':raise ValueError('Parent target/bias/type mismatch')
    if any(cfg.get(k,False) for k in ('use_dora','use_rslora','fan_in_fan_out','lora_bias')) or any(cfg.get(k) for k in ('rank_pattern','alpha_pattern','modules_to_save')):
        raise ValueError('Unsupported parent LoRA variant or extra saved modules')
    if kind=='sealed_epoch_adapter' and receipt.get('schema')!=contract['schema']:raise ValueError('Parent adapter schema mismatch')
    if c.get('non_book_teachers_allowed') is not False or c.get('production_enabled') is not False:raise ValueError('Unapproved parent policy')
    return {'source_path':str(path),'kind':kind,'schema':contract['schema'],'parent_config':c,
        'job_contract_sha256':file_sha(job/'job_contract.json'),'stage_contract_sha256':file_sha(stage/'stage_contract.json'),
        'receipt_sha256':file_sha(path/('resume_receipt.json' if kind.startswith('sealed_optimizer') else 'book_adapter_receipt.json')),
        'files':{n:file_sha(path/n) for n in ESSENTIAL},'optimizer_inherited':False,'source_database_unchanged':True}


def candidates():
    """Use the user-selected V4 completed formal stage, never V5 by default.

    This is recency-based continuation, not a claim of quality-based selection.
    """
    for root in (ROOT/'local/qwen_course_v4',):
        found=[]
        if root.exists():
            for stage in root.glob('*/trials/*/cycle_01'):
                status=stage/'stage_status.json'
                if not status.is_file():continue
                state=read_json(status)
                if state.get('state')!='complete':continue
                paths=[Path(state['adapter'])]
                for path in paths:
                    try:proof=inspect_parent(path)
                    except (ValueError,KeyError,OSError):continue
                    found.append((path.stat().st_mtime_ns,path,proof))
        if found:
            yield from sorted(found,key=lambda x:x[0],reverse=True)


def snapshot(root,path=None,*,testing=False):
    root=private_output(root);dest=root/'parent_adapter';proofpath=root/'parent_provenance.json'
    if dest.exists():
        proof=read_json(proofpath)
        if path is not None and str(Path(path).resolve())!=proof['source_path']:raise ValueError('New phase parent changed')
        if any(file_sha(dest/n)!=v for n,v in proof['files'].items()):raise ValueError('Pinned parent snapshot changed')
        return proof
    if proofpath.exists():raise ValueError('Partial parent snapshot preserved')
    if path is None:
        candidate=next(candidates(),None)
        if candidate is None:raise FileNotFoundError('No intact completed formal V4 adapter found. Use --parent with its cycle_01/trainer/checkpoint-N or adapters/step-N folder.')
        path=candidate[1]
    proof=inspect_parent(path,testing=testing);root.mkdir(parents=True,exist_ok=True)
    pending=root/'parent_adapter.pending'
    if pending.exists():raise ValueError('Partial parent snapshot preserved')
    pending.mkdir()
    for n in ESSENTIAL:shutil.copy2(Path(path)/n,pending/n)
    if any(file_sha(pending/n)!=v for n,v in proof['files'].items()):raise ValueError('Parent changed while copying')
    pending.rename(dest);atomic_json(proofpath,proof);return proof


def verify_snapshot(c):
    path=private_output(c['book_parent_snapshot']);proof=read_json(path.parent/'parent_provenance.json')
    if file_sha(path.parent/'parent_provenance.json')!=c['book_parent_provenance_sha256']:raise ValueError('Parent provenance changed')
    if any(file_sha(path/n)!=v for n,v in proof['files'].items()):raise ValueError('Parent snapshot changed')
    parent=proof['parent_config']
    for k in ('model_id','revision','lora_r','lora_alpha','lora_dropout','target_modules'):
        if c[k]!=parent[k]:raise ValueError('Cannot change inherited LoRA structure: '+k)
    return path
