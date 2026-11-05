"""CPU proof of exact KV expansion, HF integration and cached generation.

Actual CUDA backend/3866-token capacity remains a local GPU probe, not this test.
"""
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace
import json


def main():
    import torch
    from torch.nn.attention import sdpa_kernel,SDPBackend
    from transformers.integrations.sdpa_attention import sdpa_attention_forward
    from transformers.integrations import sdpa_attention as hf
    import torch.nn.functional as F
    from transformers import Qwen3Config,Qwen3ForCausalLM,set_seed
    from src.wengua.qwen8b_attention_v1 import attention_route,cuda_probe
    torch.set_num_threads(2);set_seed(3407)
    cases=[]
    for qlen,klen,masked in ((7,7,False),(1,7,False),(7,7,True)):
        inputs=[torch.randn(1,h,n,8,requires_grad=True) for h,n in ((4,qlen),(2,klen),(2,klen))]
        copies=[x.detach().clone().requires_grad_() for x in inputs]
        mask=torch.ones(qlen,klen,dtype=torch.bool).tril()[None,None] if masked else None
        owner=SimpleNamespace(num_key_value_groups=2,is_causal=True)
        with sdpa_kernel([SDPBackend.MATH]):
            native=sdpa_attention_forward(owner,*inputs,mask,dropout=0.,scaling=0.5)[0]
            with attention_route(testing=True) as audit:
                expanded=sdpa_attention_forward(owner,*copies,mask,dropout=0.,scaling=0.5)[0]
            weight=torch.randn_like(native);(native*weight).sum().backward();(expanded*weight).sum().backward()
        assert torch.allclose(native,expanded,atol=1e-6,rtol=1e-5)
        assert all(torch.allclose(a.grad,b.grad,atol=1e-6,rtol=1e-5) for a,b in zip(inputs,copies))
        assert audit['calls']==1 and audit['native_gqa_calls']==0 and audit['cuda_calls']==0
        cases.append({'query_tokens':qlen,'key_tokens':klen,'masked':masked,'output_and_qkv_gradients_match':True})
    original=F.scaled_dot_product_attention;old_gqa=hf.use_gqa_in_sdpa
    try:
        with attention_route(testing=True) as bad:
            F.scaled_dot_product_attention(*inputs,enable_gqa=True)
        raise AssertionError('Native GQA bypass accepted')
    except RuntimeError as error:assert 'explicit KV' in str(error)
    assert bad['native_gqa_calls']==1 and F.scaled_dot_product_attention is original and hf.use_gqa_in_sdpa is old_gqa
    try:
        with attention_route(report={'state':'ready','selected_backend':'MATH'}):pass
        raise AssertionError('Unverified math fallback accepted')
    except RuntimeError as error:assert 'Verified fused' in str(error)
    model=Qwen3ForCausalLM(Qwen3Config(vocab_size=97,hidden_size=32,intermediate_size=64,num_hidden_layers=1,
        num_attention_heads=4,num_key_value_heads=2,head_dim=8,max_position_embeddings=256,bos_token_id=1,eos_token_id=96,pad_token_id=0))
    model.set_attn_implementation('sdpa');reference=deepcopy(model);ids=torch.tensor([[1,2,3,4,5,6,7]])
    with sdpa_kernel([SDPBackend.MATH]),attention_route(testing=True) as audit:
        model(input_ids=ids,labels=ids,use_cache=False).loss.backward()
        model.eval();generated=model.generate(ids,max_new_tokens=3,do_sample=False,use_cache=True)
    with sdpa_kernel([SDPBackend.MATH]):
        reference.eval();native=reference.generate(ids,max_new_tokens=3,do_sample=False,use_cache=True)
    assert torch.equal(generated,native)
    assert audit['calls']>=4 and audit['current_query_tokens']==1 and audit['max_key_tokens']>ids.shape[1]
    assert audit['native_gqa_calls']==0 and audit['cuda_calls']==0
    if not torch.cuda.is_available():assert cuda_probe()['state']=='blocked'
    report={'state':'passed','cases':cases,'actual_hf_training_and_cached_generation_use_explicit_kv':True,
        'cached_generation_tokens_match':True,'native_gqa_bypass_rejected':True,'math_backend_rejected_for_real_runs':True,
        'global_bindings_restored_on_error':True,'audit':audit,'cuda_backend_verified':False,'official_8b_weights_loaded':False}
    path=Path(__file__).resolve().parents[1]/'local/qwen8b_book_v1/attention_integration.json'
    path.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))


if __name__=='__main__':main()
