"""Fresh real Trainer checks: cold lazy imports and already-bound aliases.

CPU software fixture only, vocab97, no official weights or tokenizer download.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile


def child(case):
    # Reproduce the real worker's cold import order: Callback, then loss hook,
    # then the fit kernel's from-transformers import. Do not preload Trainer.
    from transformers import TrainerCallback
    alias=None;original=None
    if case=='warm_alias':
        from transformers import Trainer as alias
        original=alias.compute_loss
    from src.wengua.qwen8b_loss_v1 import memory_trainer
    with memory_trainer(128) as audit:
        from transformers import AutoTokenizer,Trainer,TrainingArguments,Qwen3Config,Qwen3ForCausalLM,set_seed
        assert Trainer.compute_loss.__module__=='src.wengua.qwen8b_loss_v1', 'Actual imported Trainer bypasses bounded loss'
        if alias is not None:assert alias.compute_loss is Trainer.compute_loss, 'Previously bound Trainer alias bypasses bounded loss'
        import torch
        from peft import LoraConfig,get_peft_model
        from unittest.mock import patch
        torch.set_num_threads(2);set_seed(3407)
        model=get_peft_model(Qwen3ForCausalLM(Qwen3Config(vocab_size=97,hidden_size=32,intermediate_size=64,
            num_hidden_layers=1,num_attention_heads=2,num_key_value_heads=1,head_dim=16,max_position_embeddings=256)),
            LoraConfig(r=4,lora_alpha=8,lora_dropout=0.,target_modules=['q_proj','v_proj'],task_type='CAUSAL_LM'))
        rows=[]
        for n in (145,193,169,185):
            ids=(torch.arange(n)%95+1).unsqueeze(0);labels=ids.clone();labels[:,:7]=-100
            rows.append({'input_ids':ids[0],'attention_mask':torch.ones_like(ids[0]),'labels':labels[0]})
        projections=[]
        hook=model.get_base_model().lm_head.register_forward_pre_hook(lambda m,args:projections.append(args[0].shape[1]))
        forward=model.forward
        def guard(*args,**kwargs):
            assert 'labels' not in kwargs, 'Full causal model forward with labels must not run in bounded Trainer'
            return forward(*args,**kwargs)
        with tempfile.TemporaryDirectory() as tmp,patch.object(model,'forward',guard):
            args=TrainingArguments(output_dir=tmp,use_cpu=True,per_device_train_batch_size=1,per_device_eval_batch_size=1,
                gradient_accumulation_steps=2,max_steps=2,save_strategy='no',report_to='none',logging_strategy='no',
                remove_unused_columns=False,dataloader_pin_memory=False,gradient_checkpointing=True,
                gradient_checkpointing_kwargs={'use_reentrant':False},seed=3407)
            trainer=(alias or Trainer)(model=model,args=args,train_dataset=rows,eval_dataset=rows)
            trainer.train();trainer.evaluate()
        hook.remove()
        assert audit['train_loss_calls']>=4 and audit['eval_loss_calls']>=4, audit
        assert projections and max(projections)<=128 and audit['max_projected_positions']==128, audit
        assert audit['compute_loss_calls']==audit['train_loss_calls']+audit['eval_loss_calls']
        result={'case':case,'state':'passed','actual_train_and_eval_use_bounded_loss':True,
            'full_causal_forward_with_labels_bypassed':True,'loss_audit':dict(audit),'actual_8b_weights_loaded':False}
    assert Trainer.compute_loss.__module__=='transformers.trainer', 'Original Trainer not restored'
    if original is not None:assert alias.compute_loss is original
    print(json.dumps(result))


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--case',choices=('cold_root','warm_alias'))
    args=parser.parse_args()
    if args.case:child(args.case);return
    root=Path(__file__).resolve().parents[1];results=[]
    for case in ('cold_root','warm_alias'):
        result=subprocess.run([sys.executable,'-X','utf8','-m','scripts.check_qwen8b_loss_path','--case',case],
            cwd=root,env=os.environ.copy(),text=True,encoding='utf8',capture_output=True)
        print(result.stdout,end='');print(result.stderr,end='',file=sys.stderr)
        if result.returncode:raise SystemExit(result.returncode)
        results.append(json.loads(result.stdout.strip().splitlines()[-1]))
    path=root/'local/qwen8b_book_v1/loss_route_integration.json';path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps({'state':'passed','cases':results,'cuda_memory_fit_verified':False},indent=2)+'\n')


if __name__=='__main__':main()
