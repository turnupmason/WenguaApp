"""Real CPU checkpoint/resume/stage-continuation contract; no 14B weights/GPU."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import time
from unittest.mock import patch

from src.wengua.qwen_research import ROOT, json_text, write_json
from src.wengua.qwen_curriculum_v2 import SYSTEM, VERSION
from src.wengua.qwen_curriculum_train import train_stage, evaluate_pair
from src.wengua.qwen_finetune import encode_sample
from scripts.qwen_curriculum import config_checked


def main():
    import torch
    from transformers import AutoTokenizer, Qwen3Config, Qwen3ForCausalLM, TrainerCallback, set_seed
    torch.set_num_threads(2);set_seed(3407)
    config=config_checked();config.update(gradient_accumulation_steps=1,save_steps=1,
          stage_max_steps={'knowledge':2,'workflow':2},validation_rows=2,eval_max_new_tokens=128)
    tokenizer=AutoTokenizer.from_pretrained(config['model_id'],revision=config['revision'],trust_remote_code=False)
    tokenizer.pad_token=tokenizer.pad_token or tokenizer.eos_token
    base=Qwen3ForCausalLM(Qwen3Config(vocab_size=len(tokenizer),hidden_size=32,intermediate_size=64,
                num_hidden_layers=1,num_attention_heads=2,num_key_value_heads=1,head_dim=16,max_position_embeddings=2048))
    class StopAfterFirst(TrainerCallback):
        reached=False
        def on_step_end(self,args,state,control,**kwargs):
            self.reached=True;control.should_save=True;control.should_training_stop=True;return control
    (ROOT/'local').mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(dir=ROOT/'local') as temp:
        root=Path(temp);prepared=root/'prepared';prepared.mkdir();data=root/'data';data.mkdir()
        rows=[]
        for i in range(2):
            answer={'mode':'source_study','summary':'这是程序夹具，不是书内知识。','evidence':[],
                    'missing_information':['没有古籍资料'],'counter_evidence':[],'event_probability':None}
            row={'id':'fixture'+str(i),'group':'fixture'+str(i),'task':'fixture','source_ids':[],
                'messages':[{'role':'system','content':SYSTEM},{'role':'user','content':'说明这个程序夹具。'},
                            {'role':'assistant','content':json_text(answer)}]}
            encoded,size=encode_sample(row,tokenizer,1536)
            assert encoded
            rows.append(dict(row,encoded=encoded))
        for name in ('knowledge_stage','workflow_stage','validation_encoded'):
            (prepared/(name+'.jsonl')).write_text(''.join(json_text(r)+'\n' for r in rows),encoding='utf8')
        (data/'validation.jsonl').write_text(json_text(rows[0])+'\n',encoding='utf8')
        deadline=time.time()+3600
        with patch('src.wengua.qwen_curriculum_train.deadline_callback',return_value=StopAfterFirst()):
            interrupted=train_stage(prepared,root/'knowledge',config,'knowledge',deadline,
                                    cpu_fixture=(tokenizer,deepcopy(base),torch.float32))
        assert interrupted['state']=='deadline_checkpointed' and interrupted['steps']==1
        resumed=train_stage(prepared,root/'knowledge',config,'knowledge',deadline,resume=True,
                            cpu_fixture=(tokenizer,deepcopy(base),torch.float32))
        assert resumed['state']=='complete' and resumed['steps']==2
        assert resumed['resume_checkpoint'].endswith('checkpoint-1')
        # The second stage is a warm start of the learned adapter, not a true
        # optimizer resume across different training data.
        workflow=train_stage(prepared,root/'workflow',config,'workflow',deadline,
                            initial_adapter=root/'knowledge/adapter',
                            cpu_fixture=(tokenizer,deepcopy(base),torch.float32))
        assert workflow['state']=='complete' and workflow['resume_checkpoint'] is None
        pair=evaluate_pair(data,root/'eval',config,root/'workflow/adapter',deadline,limit=1,
                          cpu_fixture=(tokenizer,deepcopy(base),torch.float32))
        raw=[json.loads(line) for line in (root/'eval/paired_answers.jsonl').read_text(encoding='utf8').splitlines()]
        assert len(raw)==2 and raw[0]['prompt_sha256']==raw[1]['prompt_sha256']
        assert pair['completed_generations']==2 and not pair['test_used']
        receipt={'state':'passed','test':'tiny_random_qwen3_cpu_curriculum_checkpoint_resume',
                 'official_tokenizer':config['model_id'],'revision':config['revision'],
                 'stop_after_first_optimizer_step':True,'restored_optimizer_rng_scheduler_step_2':True,
                 'new_stage_loads_adapter_with_new_optimizer':True,'same_prompt_base_adapter_generations':True,
                 'development_pair':pair,'real_14b_weights_loaded':False,'cuda_nf4_tested':False}
    output=ROOT/'local/qwen_curriculum_v2/tiny_integration.json';output.parent.mkdir(parents=True,exist_ok=True)
    write_json(output,receipt);print(json.dumps(receipt,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
