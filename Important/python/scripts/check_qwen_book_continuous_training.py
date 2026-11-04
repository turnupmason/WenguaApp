"""Actual tiny random Qwen3 CPU continuous-epoch and staged-controller test."""
from copy import deepcopy
from pathlib import Path
import tempfile
import time
from unittest.mock import patch

from src.wengua import qwen_book_continuous_v1 as engine
from src.wengua import qwen_book_sweep_v2 as sweep
from src.wengua.qwen_book_continuous_v1 import book


def main():
    import torch
    from transformers import AutoTokenizer,Qwen3Config,Qwen3ForCausalLM,TrainerCallback,set_seed
    from safetensors.torch import load_file
    torch.set_num_threads(2);set_seed(3407)
    c=engine.base_config();c.update(num_train_epochs=2,max_seq_length=512,inference_max_context=512,
        eval_max_new_tokens=32,gradient_accumulation_steps=2,save_steps=2,validation_rows=4,
        validation_generation_rows=1,test_generation_rows=1)
    tok=AutoTokenizer.from_pretrained(c['model_id'],revision=c['revision'],trust_remote_code=False)
    tok.pad_token=tok.pad_token or tok.eos_token
    base=Qwen3ForCausalLM(Qwen3Config(vocab_size=len(tok),hidden_size=32,intermediate_size=64,
        num_hidden_layers=1,num_attention_heads=2,num_key_value_heads=1,head_dim=16,max_position_embeddings=1024))
    # Reproduce the reported output-head dtype mismatch with real Qwen3 ops.
    # CPU bf16 exercises the arithmetic; mocked CUDA dispatch is not a GPU test.
    from contextlib import nullcontext
    from types import SimpleNamespace
    mixed=deepcopy(base).to(torch.bfloat16).eval();mixed.lm_head.float()
    inputs=torch.tensor([[1,2,3]])
    try:
        with torch.inference_mode():mixed.generate(inputs,max_new_tokens=1,do_sample=False)
    except RuntimeError as error:
        assert 'dtype' in str(error) or 'scalar type' in str(error),str(error)
    else:raise AssertionError('Mixed output head fixture must fail without autocast')
    real_autocast=torch.autocast
    def cpu_dispatch(*args,**kwargs):
        if kwargs.get('device_type')=='cuda':
            assert kwargs['dtype']==torch.bfloat16
            return real_autocast(device_type='cpu',dtype=kwargs['dtype'])
        return real_autocast(*args,**kwargs)
    with patch.object(torch.cuda,'device',return_value=nullcontext()),patch.object(torch.cuda,'is_bf16_supported',return_value=True),patch.object(torch,'autocast',side_effect=cpu_dispatch):
        with book.generation_autocast(SimpleNamespace(device=torch.device('cuda:0'))),torch.inference_mode():
            generated=mixed.generate(inputs,max_new_tokens=1,do_sample=False)
    assert generated.shape[-1]==4
    del mixed
    loads=[]
    def factory():loads.append(1);return tok,deepcopy(base),torch.float32
    records=[];units={};formats=['foundation_qa','conditional_dialogue','chart_application','complete_case']
    for split,count in [('train',3),('validation',4),('test',1)]:
        for i in range(count):
            uid=split+str(i);quote='这是程序夹具，不是古籍知识。'
            if split=='validation' and i==3:quote+='软件测试说明。'*12
            units[uid]={'id':uid,'book_id':'shenqi','chapter':'软件夹具','lines':[1,1],'original_quote':quote}
            messages=[{'role':'system','content':'软件测试。'},{'role':'user','content':'说明夹具。'},{'role':'assistant','content':quote}]
            records.append({'id':uid,'group':uid,'split':split,'format':formats[i],'source_ids':[uid],'case_id':None,
                'source_mode':'synthetic_software_fixture','task':'fixture','question':'说明夹具。','answer':quote,'messages':messages})
    pack={'records':records,'units':units,'source_sha256':book.SOURCE_SHA256}
    spec=book.read_json(sweep.SPEC);spec.update(contexts=[512,1024],structures=[{'lora_r':4,'target_modules':spec['structures'][-1]['target_modules']}],
        learning_rates=[3e-5],warmup_ratios=[0.08])
    class Observe(TrainerCallback):
        fired=False
        def __init__(self):self.starts=[];self.epochs=[]
        def on_train_begin(self,args,state,control,**kw):
            steps=[int(v['step']) for v in kw['optimizer'].state.values() if 'step' in v]
            self.starts.append((state.global_step,steps));return control
        def on_epoch_begin(self,args,state,control,**kw):
            steps=[int(v['step']) for v in kw['optimizer'].state.values() if 'step' in v]
            self.epochs.append((len(self.starts)-1,state.global_step,steps,id(kw['optimizer']),kw['lr_scheduler'].last_epoch));return control
        def on_step_end(self,args,state,control,**kw):
            if not self.fired:self.fired=True;control.should_save=True;control.should_training_stop=True
            return control
    (book.ROOT/'local').mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(dir=book.ROOT/'local') as tmp:
        root=Path(tmp)/'run';callback=Observe();deadline=time.time()+7200
        first=sweep.run(root,spec,deadline,base=c,cpu_factory=factory,tokenizer=tok,pack=pack,extra_callbacks=(callback,))
        assert first['state']=='paused_trial' and not (root/'selected_trial.json').exists()
        cfg=sweep.plan(spec,c)['structures'][0];tid=sweep.trial_id(cfg);job=root/'trials'/tid
        cp=job/'cycle_01/trainer/checkpoint-1';assert cp.is_dir()
        with patch.object(book,'final_test',wraps=book.final_test) as final:
            done=sweep.run(root,spec,deadline,resume=True,resume_from_checkpoint=cp,base=c,cpu_factory=factory,
                tokenizer=tok,pack=pack,extra_callbacks=(callback,))
            assert done['state']=='complete' and len(done['trials'])==3 and final.call_count==1
            assert [x[0] for x in callback.starts]==[0,1,0,0]
            assert callback.starts[1][1] and set(callback.starts[1][1])=={1}
            resumed=[x for x in callback.epochs if x[0]==1]
            assert len(resumed)==2 and resumed[0][3]==resumed[1][3]
            assert resumed[1][1]==2 and set(resumed[1][2])=={2} and resumed[1][4]==2
            for row in done['trials'].values():
                assert row['state']=='complete' and len(row['per_format_loss'])==4 and row['steps']==4
            hashes=[x['common_evaluation_sha256'] for x in done['coverage'].values()]
            assert hashes[0]==hashes[1]
            assert any((root/'trials'/row['id']/'generations/extended_validation_selected.jsonl').exists() for row in done['trials'].values())
            before=len(loads)
            sweep.run(root,spec,deadline,resume=True,base=c,cpu_factory=factory,tokenizer=tok,pack=pack)
            assert before==len(loads) and final.call_count==1
        # Exact same config without interruption should reach the same final LoRA tensors.
        reference=engine.open_job(Path(tmp)/'uninterrupted',cfg,resume=False)
        engine.prepare_shared(root,reference,cfg,reference_context=512,tokenizer=tok,pack=pack)
        uninterrupted=engine.run_trial(reference,cfg,deadline,cpu_factory=factory)
        paused_status=book.read_json(job/'cycle_01/stage_status.json')
        a=load_file(Path(paused_status['last_adapter'])/'adapter_model.safetensors')
        b=load_file(Path(uninterrupted['last_adapter'])/'adapter_model.safetensors')
        diagnostic=book.ROOT/'local/qwen_book_sweep_v2/resume_equivalence';diagnostic.mkdir(parents=True,exist_ok=True)
        import shutil
        for name,source in [('resumed',job/'cycle_01/trainer/checkpoint-4'),('uninterrupted',reference/'cycle_01/trainer/checkpoint-4')]:
            target=diagnostic/name;target.mkdir(exist_ok=True)
            for file in source.iterdir():
                if file.name in (*book.CKPT_REQUIRED,'continuous_state.json'):shutil.copy2(file,target/file.name)
        book.atomic_json(diagnostic/'differences.json',{'deltas':{k:float((a[k]-b[k]).abs().max()) for k in a},
            'callback_starts':callback.starts,'callback_epochs':callback.epochs})
        assert all(torch.allclose(a[k],b[k],rtol=1e-5,atol=1e-7) for k in a)
        # Power-cut window between the last update of an epoch and its evaluation.
        boundary=engine.open_job(Path(tmp)/'boundary_cut',cfg,resume=False)
        engine.prepare_shared(root,boundary,cfg,reference_context=512,tokenizer=tok,pack=pack)
        class CutBeforeEpochValidation(TrainerCallback):
            def on_save(self,args,state,control,**kw):
                if state.global_step==2:raise KeyboardInterrupt('Fixture cut after sealed step-2 checkpoint, before epoch evaluation')
        try:engine.run_trial(boundary,cfg,deadline,cpu_factory=factory,extra_callbacks=(CutBeforeEpochValidation(),))
        except KeyboardInterrupt:pass
        else:raise AssertionError('Boundary cut fixture did not execute')
        boundary_cp=boundary/'cycle_01/trainer/checkpoint-2'
        assert book.read_json(boundary_cp/'continuous_state.json')['history']==[]
        boundary_done=engine.run_trial(boundary,cfg,deadline,cpu_factory=factory,resume_from_checkpoint=boundary_cp)
        assert [r['cycle'] for r in boundary_done['epochs']]==[1,2]
        boundary_weights=load_file(Path(boundary_done['last_adapter'])/'adapter_model.safetensors')
        assert all(torch.allclose(boundary_weights[k],b[k],rtol=1e-5,atol=1e-7) for k in b)
        # A power cut after the final optimizer save must never add another update.
        stale=dict(paused_status,state='training');book.atomic_json(job/'cycle_01/stage_status.json',stale)
        with patch('transformers.Trainer.train',side_effect=AssertionError('Final checkpoint must not train again')):
            repaired=engine.fit(job,cfg,deadline,cpu_factory=factory)
        assert repaired['steps']==4 and repaired['training_metrics']['finalized_without_extra_update']
        preview=book.ROOT/'local/qwen_book_sweep_v2/tiny_cpu_report_not_14b.html'
        preview.parent.mkdir(parents=True,exist_ok=True);preview.write_bytes((root/'results.html').read_bytes())
    receipt={'state':'passed','test':'tiny_random_qwen3_cpu_continuous_optimizer_staged_sweep',
        'two_epochs_same_adam_object_and_monotonic_adam_scheduler_steps':True,'partial_epoch_no_false_validation_or_early_stop':True,
        'mixed_bfloat16_hidden_float32_head_reproduced_and_autocast_fixed_on_cpu':True,
        'interrupted_and_uninterrupted_final_adapter_tensors_match':True,'explicit_checkpoint_restored_optimizer_step_1':True,
        'power_cut_before_epoch_validation_recovers_evaluation_and_matches_uninterrupted_weights':True,
        'new_trials_start_step_zero_empty_optimizer':True,'all_seven_projection_modules_exercised':True,
        'four_format_macro_validation_losses_recorded':True,'two_contexts_byte_identical_common_validation_and_test':True,
        'long_validation_base_and_selected_generation_path_exercised':True,
        'adaptive_stages_reuse_identical_configuration_without_retraining':True,'one_final_selected_test_after_all_stages':True,
        'completed_resume_does_not_reload_or_retest':True,'power_cut_after_final_checkpoint_no_extra_update':True,
        'official_tokenizer':c['model_id'],'revision':c['revision'],'real_14b_weights_loaded':False,'cuda_nf4_tested':False}
    book.atomic_json(book.ROOT/'local/qwen_book_sweep_v2/tiny_integration.json',receipt);print(book.dumps(receipt))


if __name__=='__main__':main()
