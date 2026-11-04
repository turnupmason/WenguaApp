"""Actual subprocess/tiny CPU training test, including an existing probe reuse."""
from copy import deepcopy
import os
from pathlib import Path
import tempfile
import time

from src.wengua import qwen_book_continuous_v1 as engine
from src.wengua import qwen_book_sweep_v2 as sweep
from src.wengua.qwen_book_continuous_v1 import book
from src.wengua.qwen_book_process_v1 import isolated_execution,launch,execution_contract,PRE_PID_FIX_SHA,FILES


def fixture_factory():
    import torch
    from transformers import AutoTokenizer,Qwen3Config,Qwen3ForCausalLM,set_seed
    torch.set_num_threads(2);set_seed(3407)
    c=engine.base_config()
    tok=AutoTokenizer.from_pretrained(c['model_id'],revision=c['revision'],local_files_only=True,trust_remote_code=False)
    tok.pad_token=tok.pad_token or tok.eos_token
    model=Qwen3ForCausalLM(Qwen3Config(vocab_size=len(tok),hidden_size=32,intermediate_size=64,
        num_hidden_layers=1,num_attention_heads=2,num_key_value_heads=1,head_dim=16,max_position_embeddings=1024))
    return tok,model,torch.float32


def main():
    tok,base,_=fixture_factory();del base
    c=engine.base_config();c.update(num_train_epochs=2,max_seq_length=512,inference_max_context=512,
        eval_max_new_tokens=16,gradient_accumulation_steps=2,save_steps=2,validation_rows=4,
        validation_generation_rows=1,test_generation_rows=1)
    units={};records=[];formats=['foundation_qa','conditional_dialogue','chart_application','complete_case']
    for split,count in [('train',3),('validation',4),('test',1)]:
        for i in range(count):
            uid=split+str(i);quote='进程软件夹具。'
            units[uid]={'id':uid,'book_id':'shenqi','chapter':'软件夹具','lines':[1,1],'original_quote':quote}
            messages=[{'role':'system','content':'软件测试。'},{'role':'user','content':'说明夹具。'},{'role':'assistant','content':quote}]
            records.append({'id':uid,'group':uid,'split':split,'format':formats[i],'source_ids':[uid],'case_id':None,
                'source_mode':'synthetic_software_fixture','task':'fixture','question':'说明夹具。','answer':quote,'messages':messages})
    pack={'records':records,'units':units,'source_sha256':book.SOURCE_SHA256}
    spec=deepcopy(book.read_json(sweep.SPEC));spec.update(contexts=[512],
        structures=[{'lora_r':r,'target_modules':['q_proj','v_proj']} for r in (4,8)],
        learning_rates=[3e-5],dropouts=[0.05],warmup_ratios=[0.08])
    (book.ROOT/'local').mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(dir=book.ROOT/'local') as tmp:
        root=Path(tmp)/'run';deadline=time.time()+7200
        # Existing, exact-contract completed probe: the user's run3 shape.
        sweep.run(root,spec,time.time(),base=c,cpu_factory=object())
        config=sweep.plan(spec,c)['structures'][0];tid=sweep.trial_id(config)
        job=engine.open_job(root/'trials'/tid,config,resume=False)
        engine.prepare_shared(root,job,config,reference_context=512,tokenizer=tok,pack=pack)
        with book.job_lock(job/'run.lock'):probe=engine.fit(job,config,deadline,probe=True,cpu_factory=fixture_factory)
        assert probe['state']=='complete'
        original_contract=book.file_sha(job/'job_contract.json');original_probe=book.file_sha(job/'smoke/stage_status.json')
        old=execution_contract(True);old.pop('receipt_protocol');old['code_sha256'][FILES[0]]=PRE_PID_FIX_SHA
        book.atomic_json(root/'process_execution.json',old)
        # Parent previously rejected a successful receipt. The completed stage
        # must return without another optimizer update or rewriting its status.
        recovered=launch(job,config,deadline,'fit',probe=True,cpu_fixture=True)
        assert recovered['state']=='complete' and book.file_sha(job/'smoke/stage_status.json')==original_probe
        assert list(root.glob('process_execution.before_pid_fix-*.json'))
        status=book.read_json(root/'sweep_status.json');status['trials'][tid]={'id':tid,'state':'feasible','probe_state':'complete','config':config}
        book.atomic_json(root/'sweep_status.json',status)
        with isolated_execution(root,cpu_fixture=True,fixture_stop_once=1):
            paused=sweep.run(root,spec,deadline,resume=True,base=c,cpu_factory=object(),tokenizer=tok,pack=pack)
        assert paused['state']=='paused_trial'
        cp=job/'cycle_01/trainer/checkpoint-1';assert engine.latest(job/'cycle_01')==cp
        with isolated_execution(root,cpu_fixture=True):
            done=sweep.run(root,spec,deadline,resume=True,resume_from_checkpoint=cp,base=c,cpu_factory=object(),tokenizer=tok,pack=pack)
        assert done['state']=='complete' and len(done['trials'])==2
        assert book.file_sha(job/'job_contract.json')==original_contract
        assert book.file_sha(job/'smoke/stage_status.json')==original_probe
        assert list((job/'worker_calls').glob('*.json'))
        results=[book.read_json(p) for p in root.glob('trials/*/worker_calls/*.result.json')]
        assert len(results)==6 and all(r['ok'] for r in results)
        pids=[r['pid'] for r in results];assert len(set(pids))==6 and os.getpid() not in pids
        for row in done['trials'].values():assert row['steps']==4 and len(row['per_format_loss'])==4
        history=book.read_json(job/'cycle_01/stage_status.json');assert history['resume_checkpoint']==str(cp)
        before=list(root.glob('trials/*/worker_calls/*.result.json'))
        with isolated_execution(root,cpu_fixture=True):
            again=sweep.run(root,spec,deadline,resume=True,base=c,cpu_factory=object(),tokenizer=tok,pack=pack)
        assert again['state']=='complete' and before==list(root.glob('trials/*/worker_calls/*.result.json'))
    receipt={'state':'passed','test':'actual_spawned_tiny_qwen3_cpu_training','distinct_child_processes':6,
        'successful_stage_recovered_without_retraining_after_parent_receipt_failure':True,'known_transport_upgrade_preserves_backup':True,
        'existing_completed_probe_and_contract_preserved':True,'sealed_step_1_optimizer_resumed_in_new_process':True,
        'two_formal_configurations_finish_with_four_format_validation':True,'final_test_isolated_after_selection':True,
        'completed_resume_spawns_no_workers':True,'real_14b_weights_loaded':False,'cuda_allocator_release_verified':False}
    book.atomic_json(book.ROOT/'local/qwen_book_sweep_v2/isolated_integration.json',receipt);print(book.dumps(receipt))


if __name__=='__main__':main()
