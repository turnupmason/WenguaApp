"""Actual tiny-Qwen CPU RAG inference; never an 8B/4080 quality claim."""
from pathlib import Path
import tempfile
from unittest.mock import patch


def main():
    import torch
    from peft import LoraConfig,get_peft_model
    from transformers import AutoTokenizer
    from src.wengua import course_training_v51 as course,book_rag as r
    from src.wengua.book_rag_query import make_prompt
    from src.wengua.book_rag_inference import answer,verified_adapter
    from scripts.check_qwen8b_training import fixture_factory
    from tests.test_book_rag_editorial import fixture
    torch.set_num_threads(2)
    # Download/tokenizer metadata only, never full 8B weights.
    AutoTokenizer.from_pretrained(course.old.MODEL,revision=course.old.REVISION)
    (r.ROOT/'local').mkdir(exist_ok=True);before=course.hashes();p=course.profile(testing=True);b=p.book;c=p.engine.base_config()
    with tempfile.TemporaryDirectory(dir=r.ROOT/'local') as tmp:
        root=Path(tmp);job=root/'run/trials/software';stage=job/'cycle_01'
        b.atomic_json(job/'job_contract.json',{'schema':course.SCHEMA,'config':c,'code_sha256':course.hashes(),'dataset_release_sha256':r.digest(course.RELEASE.read_bytes())})
        b.atomic_json(stage/'stage_contract.json',{'schema':course.SCHEMA,'config':c,'job_contract_sha256':b.file_sha(job/'job_contract.json')})
        tok,base,_=fixture_factory()
        model=get_peft_model(base,LoraConfig(r=c['lora_r'],lora_alpha=c['lora_alpha'],lora_dropout=c['lora_dropout'],target_modules=c['target_modules'],task_type='CAUSAL_LM',bias='none'))
        for name,param in model.named_parameters():
            if 'lora_B' in name:param.data.fill_(0.01)
        adapter=b.save_adapter(model,tok,stage,1);b.atomic_json(stage/'stage_status.json',{'state':'complete','adapter':str(adapter)})
        digest=r.digest((adapter/'adapter_model.safetensors').read_bytes())
        path=root/'source.sqlite3';r.build_index([fixture()[0]],path)
        with r.Index(path) as index:retrieved=index.search('软件完整条件')
        prompt=make_prompt(retrieved,'软件完整条件是什么？',tok,max_context=1024,max_new_tokens=16)
        assert prompt['state']=='ready'
        assert '校订阅读稿' in prompt['messages'][-1]['content']
        result=answer(prompt,adapter,root/'answer.json',cpu_factory=fixture_factory)
        trace=r.read(root/'answer.json');assert trace['attention_path']['calls']>0 and not trace['actual_cuda_inference']
        assert trace['adapter_provenance']['adapter_sha256']==digest and trace['prompt']['references']
        assert isinstance(result['answer'],str) and result['checks']['semantic_support_verified'] is False
        parent=answer(prompt,adapter,root/'base.json',cpu_factory=fixture_factory,base_only=True)
        baseline=r.read(root/'base.json');assert baseline['variant']=='base_with_rag' and baseline['prompt']==trace['prompt']
        assert r.digest((adapter/'adapter_model.safetensors').read_bytes())==digest
        # The real completion guard rejects an active phase, without changing
        # its weights, optimizer, source contract or state to force an answer.
        b.atomic_json(stage/'stage_status.json',{'state':'training'})
        try:verified_adapter(adapter,testing=True)
        except ValueError as e:assert 'still active' in str(e)
        else:raise AssertionError('Incomplete training phase was accepted')
    assert course.hashes()==before
    proof={'actual_tiny_qwen_cpu_inference':True,'literal_source_retrieval_to_prompt_to_lora_generate':True,
        'verified_adapter_provenance':True,'same_prompt_base_and_adapter_variants':True,
        'active_training_rejected_before_model_load':True,'adapter_weights_unchanged':True,
        'frozen_training_runtime_unchanged':True,'citation_checks_not_semantic_proof':True,
        'actual_8b_or_cuda_inference_verified':False}
    r.write(r.ROOT/'local/wengua_rag/tiny_bridge.json',proof);print(r.dumps(proof))

if __name__=='__main__':main()
