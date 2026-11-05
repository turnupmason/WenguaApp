"""Real tiny Qwen3 CPU math/process tests; no real 8B weights or CUDA proof."""
from copy import deepcopy
import os
from pathlib import Path
import tempfile
import time

from src.wengua.qwen8b_book_v1 import profile,MODEL,REVISION
from src.wengua.qwen8b_process_v1 import isolated,launch
from src.wengua.qwen8b_loss_v1 import supervised_loss


def fixture_factory():
    import torch
    from transformers import AutoTokenizer,Qwen3Config,Qwen3ForCausalLM,set_seed
    torch.set_num_threads(2);set_seed(3407)
    tok=AutoTokenizer.from_pretrained(MODEL,revision=REVISION,trust_remote_code=False,local_files_only=True)
    tok.pad_token=tok.pad_token or tok.eos_token
    model=Qwen3ForCausalLM(Qwen3Config(vocab_size=len(tok),hidden_size=32,intermediate_size=64,
        num_hidden_layers=1,num_attention_heads=2,num_key_value_heads=1,head_dim=16,max_position_embeddings=2048))
    return tok,model,torch.float32


def loss_equivalence():
    import torch
    from transformers import Qwen3Config,Qwen3ForCausalLM,set_seed
    from peft import LoraConfig,get_peft_model
    torch.set_num_threads(2);set_seed(3407)
    config=Qwen3Config(vocab_size=97,hidden_size=32,intermediate_size=64,num_hidden_layers=1,num_attention_heads=2,num_key_value_heads=1,head_dim=16)
    model=get_peft_model(Qwen3ForCausalLM(config),LoraConfig(r=4,lora_alpha=8,lora_dropout=0.,target_modules=['q_proj','k_proj','v_proj','o_proj','gate_proj','up_proj','down_proj'],task_type='CAUSAL_LM'))
    for name,param in model.named_parameters():
        if 'lora_B' in name:torch.nn.init.normal_(param,std=0.03)
    reference=deepcopy(model);inputs=torch.tensor([[1,2,3,4,5,6,7,8],[1,3,2,5,4,7,6,8]])
    labels=inputs.clone();labels[:,:3]=-100;labels[1,4]=-100
    original_labels=labels.clone();data={'input_ids':inputs,'attention_mask':torch.ones_like(inputs),'labels':labels}
    count=labels[:,1:].ne(-100).sum()+3
    native=reference(**data,num_items_in_batch=count).loss
    projections=[]
    hook=model.get_base_model().lm_head.register_forward_pre_hook(lambda m,args:projections.append(args[0].shape[1]))
    bounded=supervised_loss(model,data,chunk_tokens=2,num_items_in_batch=count)
    native.backward();bounded.backward();hook.remove()
    assert torch.allclose(native,bounded,atol=1e-6,rtol=1e-6),(native,bounded)
    for (name,a),(_,b) in zip(reference.named_parameters(),model.named_parameters()):
        if a.requires_grad:assert torch.allclose(a.grad,b.grad,atol=1e-5,rtol=1e-4),name
    assert projections and max(projections)<=2 and len(projections)>2
    assert torch.equal(labels,original_labels)
    return {'native_and_chunked_loss_match':True,'all_trainable_gradients_match':True,
        'input_labels_unchanged':True,'vocabulary_projection_chunk_bound_verified':True,'explicit_batch_token_normalization_matches':True}


def main():
    import torch
    from transformers import AutoTokenizer
    from safetensors.torch import load_file
    math=loss_equivalence();p=profile(testing=True);b=p.book
    # Download tokenizer metadata only, never model.safetensors.
    tok=AutoTokenizer.from_pretrained(MODEL,revision=REVISION,trust_remote_code=False)
    tok.pad_token=tok.pad_token or tok.eos_token
    os.environ['HF_HUB_OFFLINE']='1';os.environ['TRANSFORMERS_OFFLINE']='1'
    c=p.engine.base_config();c.update(num_train_epochs=2,max_seq_length=512,inference_max_context=512,smoke_steps=2,
        gradient_accumulation_steps=2,save_steps=2,eval_max_new_tokens=32,validation_rows=4,validation_generation_rows=1,test_generation_rows=1)
    rows=[];units={};formats=['foundation_qa','conditional_dialogue','chart_application','complete_case']
    for split,count in [('train',3),('validation',4),('test',1)]:
        for i in range(count):
            uid=split+str(i);quote='软件测试夹具。'
            if split=='train' and i:quote+='仅验证程序。'*(i*12)
            units[uid]={'id':uid,'book_id':'shenqi','chapter':'软件夹具','lines':[1,1],'original_quote':quote}
            messages=[{'role':'system','content':'程序测试。'},{'role':'user','content':'说明夹具。'},{'role':'assistant','content':quote}]
            rows.append({'id':uid,'group':uid,'split':split,'format':formats[i],'source_ids':[uid],'case_id':None,
                'source_mode':'synthetic_software_fixture','task':'fixture','answer':quote,'question':'说明夹具。','messages':messages})
    pack={'records':rows,'units':units,'source_sha256':b.SOURCE_SHA256}
    spec=deepcopy(b.read_json(p.sweep.SPEC));spec.update(contexts=[512,1024],
        structures=[{'lora_r':4,'target_modules':spec['structures'][0]['target_modules']}],
        learning_rates=[2e-5,3e-5],warmup_ratios=[0.08])
    (b.ROOT/'local').mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(dir=b.ROOT/'local') as tmp:
        root=Path(tmp)/'run';deadline=time.time()+7200
        with isolated(p,root,fixture_stop_once=1):
            paused=p.sweep.run(root,spec,deadline,base=c,cpu_factory=object(),tokenizer=tok,pack=pack)
        assert paused['state']=='paused_trial'
        cfg=p.sweep.plan(spec,c)['structures'][0];job=root/'trials'/p.sweep.trial_id(cfg)
        cp=job/'cycle_01/trainer/checkpoint-1';assert p.engine.latest(job/'cycle_01')==cp
        with isolated(p,root):
            done=p.sweep.run(root,spec,deadline,resume=True,resume_from_checkpoint=cp,base=c,cpu_factory=object(),tokenizer=tok,pack=pack)
        assert done['state']=='complete' and len(done['trials'])>=4
        assert len(list((root/'pressure_proofs').glob('*.json')))==2
        assert list(root.glob('trials/*/pressure_reuse.json'))
        starts=[b.read_json(path) for path in (job/'worker_calls').glob('*.training_start.json')]
        restored=[row for row in starts if row['step']==1]
        assert len(restored)==1 and set(restored[0]['optimizer_steps'])=={1}
        events=[b.read_json(path) for path in (job/'worker_calls').glob('*.epochs.json')]
        assert any(len(e)>=2 and len({x['optimizer_id'] for x in e})==1 and e[-1]['scheduler_step']==e[-1]['step'] for e in events)
        source=b.read_json(job/'cycle_01/stage_status.json')
        refroot=Path(tmp)/'reference'
        p.sweep.run(refroot,spec,time.time(),base=c,cpu_factory=object())
        ref=p.engine.open_job(refroot/'trials'/'uninterrupted',cfg,resume=False)
        p.engine.prepare_shared(root,ref,cfg,reference_context=512,tokenizer=tok,pack=pack)
        plain=launch(p,ref,cfg,deadline,'trial')
        a=load_file(Path(source['last_adapter'])/'adapter_model.safetensors');z=load_file(Path(plain['last_adapter'])/'adapter_model.safetensors')
        assert a.keys()==z.keys()
        for key in a:assert torch.allclose(a[key],z[key],atol=1e-7,rtol=1e-5),key
        before=list(root.glob('trials/*/worker_calls/*.json'))
        with isolated(p,root):again=p.sweep.run(root,spec,deadline,resume=True,base=c,cpu_factory=object(),tokenizer=tok,pack=pack)
        assert again['state']=='complete' and before==list(root.glob('trials/*/worker_calls/*.json'))
    receipt={'state':'passed','test':'8b_profile_tiny_cpu_not_real_8b',**math,
        'actual_child_process_training_and_generation':True,'same_adam_across_epochs':True,
        'step_1_optimizer_restored_in_new_process':True,'interrupted_and_uninterrupted_lora_tensors_match':True,
        'structural_pressure_proof_reused_without_loading_its_adapter_for_training':True,
        'training_workers_offline':True,
        'completed_resume_spawns_nothing':True,'actual_8b_weights_loaded':False,'cuda_memory_fit_verified':False}
    b.atomic_json(b.ROOT/'local/qwen8b_book_v1/tiny_integration.json',receipt);print(b.dumps(receipt))


if __name__=='__main__':main()
