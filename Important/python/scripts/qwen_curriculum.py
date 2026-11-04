"""Private curriculum preparation and bounded local 14B training. No remote GPU."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import time

from src.wengua.qwen_curriculum_v2 import VERSION, SOURCE_SHA, SYSTEM, export_curriculum, prepare_training_data
from src.wengua.qwen_curriculum_train import atomic_json
from src.wengua.qwen_finetune import load_config
from src.wengua.qwen_research import ROOT, digest, private_path, read_rows, write_json, json_text

CONFIG=ROOT/'configs/qwen14b_curriculum_v2.json'
CONTRACT_FILES=['src/wengua/qwen_curriculum_v2.py','src/wengua/qwen_curriculum_train.py',
                'src/wengua/qwen_finetune.py','src/wengua/qwen_research.py',
                'scripts/qwen_curriculum.py','configs/qwen14b_curriculum_v2.json','run_qwen_overnight.py']


def verify_release_sources():
    """The raw-LF bootstrap also protects workers loaded before this checker."""
    import run_qwen_overnight as worker
    release=json.loads(worker.RELEASE.read_text(encoding='utf8'))
    if release.get('state')=='ready':
        if 'scripts/qwen_curriculum.py' not in release.get('canonical_text_sha256',{}):
            raise ValueError('Checked canonical source fingerprints missing')
        worker.check_release(release)


def config_checked(path=CONFIG):
    config=load_config(path)
    if config.get('curriculum_schema')!=VERSION:raise ValueError('Curriculum V2 config required')
    if not 1<=config['save_steps']<=100 or not 1<=config['validation_rows']<=256:
        raise ValueError('Invalid bounded checkpoint/evaluation schedule')
    if any(not 1<=config['stage_max_steps'][s]<=2000 for s in ('knowledge','workflow')):
        raise ValueError('Training stages must be bounded')
    return config


def job_contract(config):
    inputs=set((ROOT/'data/knowledge').glob('*/**/case_index.json'))
    inputs.update(ROOT/name for name in (
        'data/knowledge/qwen_curriculum_v2/domain_dialogue_seeds.json',
        'data/knowledge/timing_methods/user_notes_20261102/rules.json',
        'data/knowledge/timing_methods/user_notes_20261102/exceptions_and_duplicates.json',
        'data/knowledge/phrase_library/health_v30/user_20261022_disease_curriculum.json',
        'data/knowledge/phrase_library/health_v20/actor_profiles.json'))
    return {'schema':VERSION,'config':config,'source_database_sha256':SOURCE_SHA,
            'code_sha256':{name:digest((ROOT/name).read_bytes()) for name in CONTRACT_FILES},
            'source_index_sha256':{str(p.relative_to(ROOT)):digest(p.read_bytes()) for p in sorted(inputs)},
            'initial_model':'fresh_official_base_not_old_v1_adapter','production_enabled':False}


def prepare_job(output,config,*,resume=False):
    output=private_path(output);contract=job_contract(config)
    if output.exists():
        if not resume:raise FileExistsError('Existing job preserved. Choose a new output or explicitly --resume.')
        old=json.loads((output/'job_contract.json').read_text(encoding='utf8'))
        if old!=contract:raise ValueError('Job resume contract mismatch; preserve this run and start a new job.')
    else:
        output.mkdir(parents=True);atomic_json(output/'job_contract.json',contract)
    data=output/'data';prepared=output/'prepared'
    if not data.exists():
        print('Preparing source-located dialogue curriculum; no model weights loaded.',flush=True)
        export_curriculum(data)
    if not (data/'manifest.json').exists():raise ValueError('Interrupted data export preserved; use a new output to rebuild.')
    manifest=json.loads((data/'manifest.json').read_text(encoding='utf8'))
    for name,sha in manifest['file_sha256'].items():
        if Path(name).name!=name or digest((data/name).read_bytes())!=sha:raise ValueError('Data fingerprint mismatch '+name)
    if not prepared.exists():
        from transformers import AutoTokenizer
        tokenizer=AutoTokenizer.from_pretrained(config['model_id'],revision=config['revision'],trust_remote_code=False)
        prepare_training_data(data,prepared,tokenizer,config['max_seq_length'])
    audit_file=prepared/'token_audit.json'
    if not audit_file.exists():raise ValueError('Interrupted token preparation preserved; use a new output to rebuild.')
    # Encoded arrays must be fingerprinted too; changing a token file cannot
    # silently resume an optimizer trained with a different curriculum.
    token_files={p.name:digest(p.read_bytes()) for p in sorted(prepared.glob('*.jsonl'))}
    fingerprint=prepared/'encoded_sha256.json'
    if fingerprint.exists():
        if json.loads(fingerprint.read_text(encoding='utf8'))!=token_files:raise ValueError('Encoded data fingerprint mismatch')
    else:write_json(fingerprint,token_files)
    write_json(output/'prepare_status.json',{'state':'prepared','schema':VERSION,
               'data_manifest_sha256':digest((data/'manifest.json').read_bytes()),
               'encoded_files_sha256':token_files,'production_enabled':False})
    return output,manifest,json.loads(audit_file.read_text(encoding='utf8'))


def run_job(output,config,deadline,*,resume=False):
    from src.wengua.qwen_finetune import environment_report
    from src.wengua.qwen_curriculum_train import train_stage, evaluate_pair
    output,manifest,token_audit=prepare_job(output,config,resume=resume)
    status={'state':'prepared','output':str(output),'manifest':manifest,'token_audit':token_audit,
            'stages':[],'production_enabled':False,'semantic_expert_review_complete':False}
    atomic_json(output/'job_status.json',status)
    try:
        doctor=environment_report(config);write_json(output/'doctor.json',doctor)
        if doctor['training_preflight']['status']=='blocked':raise RuntimeError(doctor['training_preflight']['reason'])
        adapter=None
        for stage in ('knowledge','workflow'):
            status['state']='training_'+stage;atomic_json(output/'job_status.json',status)
            print('Starting bounded stage '+stage+'; complete local checkpoints every 25 optimizer steps.',flush=True)
            result=train_stage(output/'prepared',output/stage,config,stage,deadline,
                               initial_adapter=adapter,resume=resume)
            status['stages'].append(result);atomic_json(output/'job_status.json',status)
            if result['state']!='complete':
                status['state']=result['state'];break
            adapter=Path(result['adapter']);status['latest_completed_stage']=stage
        else:status['state']='training_complete'
        if adapter and time.time()<deadline-600:
            status['paired_development_evaluation']=evaluate_pair(output/'data',output/'development_evaluation',
                                        config,adapter,deadline)
        if adapter:status['chat_adapter_run']=str(adapter.parent)
        status['test_generation_evaluated']=False
        status['next_review']='Compare paired_answers.jsonl by task and source conditions; low language loss is not proof of better analysis.'
        atomic_json(output/'job_status.json',status)
        return status
    except BaseException as error:
        status.update(state='failed_preserving_checkpoints',error_type=type(error).__name__,error=str(error)[:2000])
        atomic_json(output/'job_status.json',status)
        raise


def ask_job(job,question,*,base_only=False):
    from src.wengua.qwen_finetune import local_answer
    from src.wengua.qwen_research import make_prompt, check_answer
    job=private_path(job)
    status=json.loads((job/'job_status.json').read_text(encoding='utf8'))
    run=status.get('chat_adapter_run')
    if not run:raise ValueError('No completed stage available; inspect job_status.json first.')
    docs=read_rows(job/'data/corpus.jsonl')
    messages,references=make_prompt(question,docs,mode='source_study')
    messages[0]['content']=SYSTEM
    raw,kept,generation=local_answer(messages,run,768,documents=references,base_only=base_only,return_details=True)
    sent=generation.pop('_sent_messages')
    trace={'question':question,'raw_output':raw,'generation':generation,'sent_messages':sent,'prediction_validated':False}
    try:trace.update(check_answer(json.loads(raw),kept,'source_study'),status='accepted_schema_only')
    except (ValueError,TypeError) as error:trace.update(status='rejected',error=str(error))
    out=job/'inference';out.mkdir(exist_ok=True)
    path=out/(datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')+'.json')
    write_json(path,trace)
    return {'answer':trace.get('answer'),'status':trace['status'],'trace_path':str(path),
            'semantic_support_verified':False,'prediction_validated':False}


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__);commands=parser.add_subparsers(dest='command',required=True)
    for name in ('prepare','run'):
        p=commands.add_parser(name);p.add_argument('--output',required=True)
        p.add_argument('--config',default=str(CONFIG));p.add_argument('--resume',action='store_true')
        if name=='run':
            p.add_argument('--hours',type=float,default=15)
            p.add_argument('--deadline-utc-epoch',type=float)
    p=commands.add_parser('ask');p.add_argument('--job',required=True);p.add_argument('--question',required=True)
    p.add_argument('--base-only',action='store_true')
    args=parser.parse_args(argv)
    if args.command=='ask':result=ask_job(args.job,args.question,base_only=args.base_only)
    else:
        config=config_checked(args.config)
        if args.command=='prepare':
            path,manifest,audit=prepare_job(args.output,config,resume=args.resume)
            result={'state':'prepared','output':str(path),'manifest':manifest,'token_audit':audit}
        else:
            if not 0<args.hours<=24:raise ValueError('hours must be (0,24]')
            deadline=args.deadline_utc_epoch if args.deadline_utc_epoch else time.time()+args.hours*3600
            if not time.time()<deadline<=time.time()+24*3600+1:raise ValueError('Deadline must be within the next 24 hours')
            from run_qwen_overnight import prevent_sleep
            prevent_sleep(True)
            try:result=run_job(args.output,config,deadline,resume=args.resume)
            finally:prevent_sleep(False)
    print(json.dumps(result,ensure_ascii=False,indent=2),flush=True)


if __name__=='__main__':main()
