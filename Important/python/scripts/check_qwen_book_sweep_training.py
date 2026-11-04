"""Actual tiny random Qwen3 CPU sweep; explicitly not 14B or CUDA training."""
from copy import deepcopy
from pathlib import Path
import tempfile
import time
from unittest.mock import patch

from src.wengua import qwen_book_loop_v3 as loop
from src.wengua import qwen_book_sweep_v1 as sweep


def main():
    import torch
    from transformers import AutoTokenizer,Qwen3Config,Qwen3ForCausalLM,TrainerCallback,set_seed
    torch.set_num_threads(2);set_seed(3407)
    c=loop.load_config();c.update(cycles=1,max_seq_length=512,inference_max_context=512,eval_max_new_tokens=64,
        gradient_accumulation_steps=1,max_steps_per_cycle=2,save_steps=1,validation_rows=1,
        validation_generation_rows=1,test_generation_rows=1,smoke_steps=2)
    tok=AutoTokenizer.from_pretrained(c['model_id'],revision=c['revision'],trust_remote_code=False)
    tok.pad_token=tok.pad_token or tok.eos_token
    base=Qwen3ForCausalLM(Qwen3Config(vocab_size=len(tok),hidden_size=32,intermediate_size=64,
        num_hidden_layers=1,num_attention_heads=2,num_key_value_heads=1,head_dim=16,max_position_embeddings=512))
    loads=[]
    def factory():loads.append(True);return tok,deepcopy(base),torch.float32
    cores=[];units={}
    for split,number in [('train',0),('train',1),('validation',0),('test',0)]:
        uid=split+str(number);quote='这是程序夹具，不是原书知识。'
        units[uid]={'id':uid,'book_id':'shenqi','chapter':'软件夹具','lines':[1,1],'original_quote':quote}
        messages=[{'role':'system','content':'软件测试。'},{'role':'user','content':'说明夹具。'},{'role':'assistant','content':quote}]
        cores.append({'id':uid,'group':uid,'split':split,'format':'foundation_qa','source_ids':[uid],
            'case_id':None,'source_mode':'synthetic_software_fixture','task':'fixture','question':'说明夹具。','answer':quote,'messages':messages})
    pack={'records':cores,'units':units,'source_sha256':loop.SOURCE_SHA256}
    spec=loop.read_json(sweep.SPEC);spec.update(shared_overrides={},include_reference_config=False)
    spec['grid'].update(learning_rate=[0.00002],target_modules=[['q_proj','v_proj']])
    class StopOnce(TrainerCallback):
        fired=False
        starts=[]
        def on_train_begin(self,args,state,control,**kwargs):
            optimizer_steps=[int(value['step']) for value in kwargs['optimizer'].state.values() if 'step' in value]
            self.starts.append((state.global_step,optimizer_steps))
            return control
        def on_step_end(self,args,state,control,**kwargs):
            if not self.fired:self.fired=True;control.should_save=True;control.should_training_stop=True
            return control
    (loop.ROOT/'local').mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(dir=loop.ROOT/'local') as tmp:
        root=Path(tmp)/'run';cb=StopOnce();deadline=time.time()+3600
        a=sweep.run_sweep(root,spec,deadline,base=c,cpu_factory=factory,tokenizer=tok,pack=pack,extra_callbacks=(cb,))
        assert a['state']=='paused_trial' and not (root/'selected_trial.json').exists()
        first=sweep.expand_spec(spec,c)[0]['id'];cp=root/'trials'/first/'cycle_01/trainer/checkpoint-1'
        with patch.object(loop,'final_test',wraps=loop.final_test) as final:
            b=sweep.run_sweep(root,spec,deadline,resume=True,base=c,cpu_factory=factory,tokenizer=tok,pack=pack,
                extra_callbacks=(cb,),resume_from_checkpoint=cp)
            assert b['state']=='complete' and len(b['trials'])==2 and final.call_count==1
            assert [step for step,_ in cb.starts]==[0,1,0]
            assert cb.starts[1][1] and set(cb.starts[1][1])=={1}
            assert not cb.starts[0][1] and not cb.starts[2][1]
            for trial in sweep.expand_spec(spec,c):
                job=root/'trials'/trial['id'];status=loop.read_json(job/'job_status.json')
                assert status['cycles'][0]['fresh_official_base'] and status['cycles'][0]['initial_adapter'] is None
                assert status['final_test']['state']=='deferred_to_sweep'
                assert loop.read_json(job/'prepared/receipt.json')['file_sha256']==loop.read_json(root/'shared_data/prepared/receipt.json')['file_sha256']
                if trial['id']==first:assert status['cycles'][0]['resume_checkpoint']==str(cp)
            chosen=b['selection']['id']
            assert len(list((root/'trials').glob('*/generations/final_test_selected.jsonl')))==1
            before=len(loads)
            sweep.run_sweep(root,spec,deadline,resume=True,base=c,cpu_factory=factory,tokenizer=tok,pack=pack)
            assert len(loads)==before and final.call_count==1
        preview=loop.ROOT/'local/qwen_book_sweep_v1/tiny_cpu_report_not_14b.html'
        preview.parent.mkdir(parents=True,exist_ok=True);preview.write_bytes((root/'results.html').read_bytes())
        receipt={'state':'passed','test':'tiny_random_qwen3_cpu_two_config_sweep','two_trials_fresh_base_and_new_adapter':True,
            'explicit_checkpoint_restored_optimizer_step_1_to_2':True,'identical_shared_train_and_evaluation_files':True,
            'trainer_and_adam_optimizer_step_states_observed_0_1_0':True,
            'trial_final_tests_deferred':True,'exactly_one_selected_trial_test_after_all_trials':True,
            'complete_resume_no_model_reload_or_retest':True,'html_and_csv_written':True,
            'official_tokenizer':c['model_id'],'revision':c['revision'],'real_14b_weights_loaded':False,'cuda_nf4_tested':False}
    loop.atomic_json(loop.ROOT/'local/qwen_book_sweep_v1/tiny_integration.json',receipt)
    print(loop.dumps(receipt))


if __name__=='__main__':main()
