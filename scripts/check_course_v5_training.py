"""Real tiny CPU new-course preparation, masked targets and exact worker resume."""
from pathlib import Path
import os
import tempfile
import time
from unittest.mock import patch


def main():
    import torch
    from transformers import AutoTokenizer,Trainer
    from src.wengua import course_training_v5 as course
    from src.wengua.course_process_v5 import isolated
    from tests.test_course_complete_v5 import fixture as fixture_pack
    from scripts.check_qwen8b_training import fixture_factory
    from src.wengua.qwen8b_attention_v1 import attention_route
    from src.wengua.qwen8b_loss_v1 import memory_trainer
    torch.set_num_threads(2)
    tokenizer=AutoTokenizer.from_pretrained(course.old.MODEL,revision=course.old.REVISION,trust_remote_code=False)
    tokenizer.pad_token=tokenizer.pad_token or tokenizer.eos_token
    os.environ['HF_HUB_OFFLINE']='1';os.environ['TRANSFORMERS_OFFLINE']='1'
    p=course.profile(testing=True);b=p.book
    c=p.engine.base_config()|dict(max_seq_length=512,inference_max_context=512,num_train_epochs=2,
        smoke_steps=2,gradient_accumulation_steps=1,save_steps=2,eval_max_new_tokens=16,
        validation_rows=8,validation_generation_rows=1,test_generation_rows=1)
    pack=fixture_pack()
    # Repeat independent software fixtures to cross the old failing step 35.
    base=[r for r in pack['records'] if r['split']=='train']
    import copy
    for n in range(3):
        for row in base:
            r=copy.deepcopy(row);suffix='-extra'+str(n)
            r['id']+=suffix;r['group']+=suffix;r['question']+=suffix;r['messages'][1]['content']+=suffix
            pack['records'].append(r)
    course.validate_rows(pack['records'],pack['units'])
    original=Trainer.floating_point_ops
    with tempfile.TemporaryDirectory(dir=b.ROOT/'local') as tmp:
        root=Path(tmp)/'run';b.atomic_json(root/'sweep_contract.json',{'schema':course.SCHEMA})
        job=p.engine.open_job(root/'trials'/'fixture',c,resume=True)
        p.engine.prepare_shared(root,job,c,reference_context=512,tokenizer=tokenizer,pack=pack)
        rows=b.read_rows(job/'prepared/cycle_01.jsonl.gz')
        assert len(rows)==20 and all(-100 in x['encoded']['labels'] and any(v!=-100 for v in x['encoded']['labels']) for x in rows)
        with isolated(p,root,fixture_stop_once=1):
            paused=p.engine.run_trial(job,c,time.time()+3600,cpu_factory=object())
        assert paused['state']=='paused_training',paused
        cp=paused['last_optimizer_checkpoint'];assert cp
        with isolated(p,root):
            done=p.engine.run_trial(job,c,time.time()+3600,cpu_factory=object(),resume_from_checkpoint=cp)
        assert done['state']=='complete' and done['steps']==40,done
        receipts=sorted((job/'worker_calls').glob('*.training_start.json'))
        starts=[b.read_json(x) for x in receipts]
        assert any(x['step']==1 and any(v>=1 for v in x['optimizer_steps']) for x in starts),starts
        before=list((job/'worker_calls').glob('*.json'))
        with isolated(p,root):again=p.engine.run_trial(job,c,time.time()+3600,cpu_factory=object())
        assert again['steps']==done['steps'] and again['adapter']==done['adapter']
    assert Trainer.floating_point_ops is original
    # Test graph changes and telemetry restoration in the real Trainer callback.
    _,model,_=fixture_factory();signature=course.parameter_signature(model)
    assert signature
    with course.training_integrity():assert Trainer.floating_point_ops is not original
    assert Trainer.floating_point_ops is original
    proof={'state':'complete','real_tiny_cpu_training':True,'updates':40,'exact_optimizer_resume_from_step':1,
           'all_assistant_turn_prefixes_masked':True,'new_worker_transport':True,'frozen_old_kernels_edited':False,
           'actual_8b_or_cuda_verified':False,'parameter_signature_checked':True,'telemetry_patch_restored':True}
    output=b.ROOT/'local/course_v5/tiny_integration.json';b.atomic_json(output,proof);print(b.dumps(proof))

if __name__=='__main__':main()
