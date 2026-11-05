"""Real tiny-CPU inherited weights, fresh phase optimizer and exact resume.

No Qwen3-8B weights or CUDA training claim is made by this software fixture.
"""
from pathlib import Path
import tempfile,time,os
from unittest.mock import patch


def main():
    import torch
    from transformers import AutoTokenizer,TrainerCallback
    from peft import LoraConfig,get_peft_model
    from safetensors.torch import load_file
    from src.wengua import course_training_v51 as course
    from src.wengua import qwen_course_training_v4 as v4
    from src.wengua.course_parent_v51 import snapshot,verify_snapshot
    from src.wengua.course_process_v51 import isolated
    from tests.test_course_complete_v5 import fixture
    from scripts.check_qwen8b_training import fixture_factory
    from src.wengua.qwen8b_attention_v1 import attention_route
    from src.wengua.qwen8b_loss_v1 import memory_trainer
    torch.set_num_threads(2);b=course.storage
    tokenizer=AutoTokenizer.from_pretrained(course.old.MODEL,revision=course.old.REVISION)
    os.environ['HF_HUB_OFFLINE']='1';os.environ['TRANSFORMERS_OFFLINE']='1'
    p=course.profile(testing=True);c=p.engine.base_config()|dict(max_seq_length=512,inference_max_context=512,
        num_train_epochs=2,smoke_steps=2,gradient_accumulation_steps=1,save_steps=2,
        eval_max_new_tokens=16,validation_rows=8,validation_generation_rows=1,test_generation_rows=1)
    (b.ROOT/'local').mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(dir=b.ROOT/'local') as tmp:
        root=Path(tmp);parent=root/'v4/trials/fixture';stage=parent/'cycle_01';adapter=stage/'adapters/step-9'
        pc=v4.load(v4.CONFIG)
        b.atomic_json(parent/'job_contract.json',{'schema':v4.SCHEMA,'config':pc,'dataset_release_sha256':b.file_sha(v4.RELEASE)})
        b.atomic_json(stage/'stage_contract.json',{'schema':v4.SCHEMA,'config':pc,'job_contract_sha256':b.file_sha(parent/'job_contract.json')})
        _,base,_=fixture_factory();model=get_peft_model(base,LoraConfig(r=pc['lora_r'],lora_alpha=pc['lora_alpha'],
            lora_dropout=pc['lora_dropout'],target_modules=pc['target_modules'],bias='none',task_type='CAUSAL_LM'))
        for name,param in model.named_parameters():
            if 'lora_B' in name:param.data.fill_(0.0125)
        model.save_pretrained(adapter,safe_serialization=True)
        b.atomic_json(adapter/'book_adapter_receipt.json',{'schema':v4.SCHEMA,
            'stage_contract_sha256':b.file_sha(stage/'stage_contract.json'),
            'files':{f.name:b.file_sha(f) for f in adapter.iterdir() if f.is_file()}})
        phase=root/'phase';proof=snapshot(phase,adapter,testing=True)
        c.update(book_parent_snapshot=str(phase/'parent_adapter'),book_parent_provenance_sha256=b.file_sha(phase/'parent_provenance.json'))
        verify_snapshot(c)
        # Verify the actual PEFT path used by the new fit, before any update.
        expected=load_file(str(adapter/'adapter_model.safetensors'))
        class CheckParent(TrainerCallback):
            seen=False
            def on_train_begin(self,args,state,control,**kw):
                from peft.utils.save_and_load import get_peft_model_state_dict
                got=get_peft_model_state_dict(kw['model'])
                assert all(torch.equal(got[k].cpu(),v) for k,v in expected.items())
                assert state.global_step==0 and not kw['optimizer'].state
                assert not kw['model'].config.use_cache
                self.seen=True
        pack=fixture();pack['schema']=course.SCHEMA;pack['summary']['schema']=course.SCHEMA
        import copy
        seen=next(r for r in pack['records'] if r['split']=='validation' and r['format']=='foundation_qa')
        extra=copy.deepcopy(seen);extra.update(id='unseen-software-validation',group='unseen-software-validation')
        extra['messages'][1]['content']+='软件新问法。';extra['question']=extra['messages'][1]['content'];pack['records'].append(extra)
        pack['selection_exclusions']={'groups':[seen['group']],'case_ids':[],'seen_v4_diagnostic_ids':[seen['id']]}
        # First direct phase establishes initial weights and fresh optimizer.
        direct=p.engine.open_job(phase/'trials/direct',c,resume=True)
        course.prepare(direct,c,tokenizer=tokenizer,pack=pack,testing=True)
        checked=CheckParent()
        with attention_route(testing=True),memory_trainer(c['loss_chunk_tokens']):
            done=p.engine.fit(direct,c,time.time()+3600,cpu_factory=fixture_factory,extra_callbacks=(checked,))
        assert checked.seen and done['state']=='complete' and done['parent_weights_reused'] is True
        assert done['fresh_official_base'] is False and done['steps']==10
        # A separate run from the same parent stops at update1 then restores
        # optimizer/scheduler/RNG in a fresh worker interpreter.
        job=p.engine.open_job(phase/'trials/resume',c,resume=True)
        course.prepare(job,c,tokenizer=tokenizer,pack=pack,testing=True)
        with isolated(p,phase,fixture_stop_once=1):paused=p.engine.run_trial(job,c,time.time()+3600)
        assert paused['state']=='paused_training' and paused['steps']==1
        with isolated(p,phase):resumed=p.engine.run_trial(job,c,time.time()+3600,resume_from_checkpoint=paused['last_optimizer_checkpoint'])
        assert resumed['state']=='complete' and resumed['steps']==10
        starts=[b.read_json(x) for x in (job/'worker_calls').glob('*.training_start.json')]
        assert any(x['step']==1 and any(v>=1 for v in x['optimizer_steps']) for x in starts),starts
        a=load_file(str(Path(done['last_adapter'])/'adapter_model.safetensors'))
        z=load_file(str(Path(resumed['last_adapter'])/'adapter_model.safetensors'))
        assert all(torch.equal(a[k],z[k]) for k in a),'resumed parameters differ'
        assert (job/'generations/validation_parent.jsonl').is_file()
        pool=b.read_json(job/'prepared/selection_pool.json')
        assert seen['id'] not in pool['eligible_core_ids']
        for name in ['parent_seen_diagnostics.jsonl','epoch_01_seen_diagnostics.jsonl','epoch_02_seen_diagnostics.jsonl']:
            assert len((job/'generations'/name).read_text().splitlines())==1
        assert resumed['selection_status']=='provisional_language_loss_only_requires_semantic_review'
        assert b.read_json(stage/'stage_contract.json')['schema']==v4.SCHEMA
        verify_snapshot(c)
    proof={'state':'complete','real_tiny_cpu_training':True,'parent_parameters_verified_before_update':True,
        'new_phase_optimizer_initial_state_empty':True,'training_kv_cache_disabled_after_parent_generation':True,'exact_resume_from_step':1,'updates':10,
        'resumed_weights_equal_uninterrupted':True,'parent_source_unchanged':True,
        'actual_8b_or_cuda_verified':False,'final_test_used':False}
    b.atomic_json(b.ROOT/'local/course_v51/tiny_integration.json',proof);print(b.dumps(proof))

if __name__=='__main__':main()
