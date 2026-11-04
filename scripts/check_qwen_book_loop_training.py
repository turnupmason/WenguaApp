"""Actual tiny random Qwen3 CPU loop test; no real 14B weights or CUDA."""
from copy import deepcopy
import json
from pathlib import Path
from unittest.mock import patch
import tempfile
import time

from src.wengua.qwen_book_loop_v3 import (ROOT,load_config,run_loop,atomic_json,file_sha)
from src.wengua.qwen_book_dataset_v3 import SOURCE_SHA256


def main():
    import torch
    from transformers import AutoTokenizer,Qwen3Config,Qwen3ForCausalLM,TrainerCallback,set_seed
    from safetensors.torch import load_file
    torch.set_num_threads(2);set_seed(3407)
    c=load_config();c.update(cycles=2,max_seq_length=256,inference_max_context=512,eval_max_new_tokens=64,
        gradient_accumulation_steps=1,max_steps_per_cycle=2,save_steps=1,validation_rows=1,
        validation_generation_rows=1,test_generation_rows=1,smoke_steps=2)
    tok=AutoTokenizer.from_pretrained(c['model_id'],revision=c['revision'],trust_remote_code=False)
    tok.pad_token=tok.pad_token or tok.eos_token
    base=Qwen3ForCausalLM(Qwen3Config(vocab_size=len(tok),hidden_size=32,intermediate_size=64,
        num_hidden_layers=1,num_attention_heads=2,num_key_value_heads=1,head_dim=16,max_position_embeddings=512))
    def factory():return tok,deepcopy(base),torch.float32
    cores=[];units={}
    for split in ('train','validation','test'):
        for i in range(2 if split=='train' else 1):
            uid=split+str(i);quote='这是程序夹具，不是原书知识或真实预测。'
            units[uid]={'id':uid,'book_id':'shenqi','chapter':'程序夹具','lines':[1,1],'original_quote':quote}
            messages=[{'role':'system','content':'这是软件测试。'},{'role':'user','content':'说明夹具。'},{'role':'assistant','content':quote}]
            if i:messages += [{'role':'user','content':'夹具能否当作古籍知识？'},{'role':'assistant','content':'不能。这只是程序测试。'}]
            cores.append({'id':uid,'group':uid,'split':split,'format':'conditional_dialogue' if i else 'foundation_qa',
                'source_ids':[uid],'case_id':None,'source_mode':'synthetic_software_fixture','task':'fixture',
                'question':messages[-2]['content'],'answer':messages[-1]['content'],'messages':messages})
    pack={'records':cores,'units':units,'source_sha256':SOURCE_SHA256}
    class StopOnce(TrainerCallback):
        fired=False
        def on_step_end(self,args,state,control,**kwargs):
            if not self.fired:self.fired=True;control.should_save=True;control.should_training_stop=True
            return control
    (ROOT/'local').mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(dir=ROOT/'local') as tmp:
        job=Path(tmp)/'job';callback=StopOnce();deadline=time.time()+3600
        paused=run_loop(job,c,deadline,cpu_factory=factory,tokenizer=tok,pack=pack,extra_callbacks=(callback,))
        assert paused['state']=='paused_cycle' and paused['cycles'][0]['steps']==1
        assert not (job/'generations/final_test_selected.jsonl').exists()
        first=load_file(job/'cycle_01/trainer/checkpoint-1/adapter_model.safetensors')
        finished=run_loop(job,c,deadline,resume=True,cpu_factory=factory,tokenizer=tok,pack=pack,extra_callbacks=(callback,))
        assert finished['state']=='complete' and len(finished['cycles'])==2
        a,b=finished['cycles'];assert a['steps']==2 and a['resume_checkpoint'].endswith('checkpoint-1')
        assert a['fresh_official_base'] and not b['fresh_official_base']
        assert b['initial_adapter']==a['adapter'] and b['resume_checkpoint'] is None
        second=load_file(Path(a['adapter'])/'adapter_model.safetensors')
        assert any(not torch.equal(first[k],second[k]) for k in first)
        predictions={}
        for path in (job/'generations').glob('*.jsonl'):
            predictions[path.name]=[json.loads(line) for line in path.read_text().splitlines()]
        for name in ('cycle_01_validation.jsonl','cycle_02_validation.jsonl'):
            assert predictions[name][0]['prompt_sha256']==predictions['validation_base.jsonl'][0]['prompt_sha256']
        assert predictions['final_test_base.jsonl'][0]['prompt_sha256']==predictions['final_test_selected.jsonl'][0]['prompt_sha256']
        before=file_sha(job/'generations/final_test_selected.jsonl')
        def never_load():raise AssertionError('Completed resume must not reload/retrain')
        again=run_loop(job,c,deadline,resume=True,cpu_factory=never_load,tokenizer=tok,pack=pack)
        assert again['state']=='complete' and file_sha(job/'generations/final_test_selected.jsonl')==before
        assert (job/'results.html').exists() and (job/'training_steps.csv').exists()
        # Power-cut window: max-step optimizer checkpoint exists, final status was not committed.
        from src.wengua.qwen_book_loop_v3 import train_unit,read_json
        stale=read_json(job/'cycle_01/stage_status.json');stale['state']='training'
        atomic_json(job/'cycle_01/stage_status.json',stale)
        with patch('transformers.Trainer.train',side_effect=AssertionError('Completed optimizer must not take another step')):
            repaired=train_unit(job,'cycle_01',c,deadline,cpu_factory=factory)
        assert repaired['steps']==2 and repaired['training_metrics']['finalized_from_complete_optimizer_checkpoint']
        preview=ROOT/'local/qwen_book_loop_v3/tiny_cpu_report_not_14b.html'
        preview.parent.mkdir(parents=True,exist_ok=True);preview.write_bytes((job/'results.html').read_bytes())
        receipt={'state':'passed','test':'tiny_random_qwen3_cpu_book_loop',
            'official_tokenizer':c['model_id'],'revision':c['revision'],
            'smoke_not_used_as_initial_formal_adapter':True,'paused_step_1_then_resumed_optimizer_to_step_2':True,
            'adapter_weights_changed_after_resume':True,'next_cycle_same_job_adapter_new_optimizer':True,
            'base_and_each_cycle_identical_validation_prompts':True,'final_test_selected_only_after_loop':True,
            'complete_job_resume_does_not_repeat_training_or_test':True,
            'max_step_checkpoint_after_power_cut_finalized_without_extra_training_step':True,'natural_chinese_answer_report_written':True,
            'real_14b_weights_loaded':False,'cuda_nf4_tested':False}
    output=ROOT/'local/qwen_book_loop_v3/tiny_integration.json';atomic_json(output,receipt)
    print(json.dumps(receipt,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
