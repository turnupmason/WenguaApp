"""Explicit KV expansion permits fused CUDA SDPA without native GQA support.

No approximate/windowed attention. Keep HF mask/causal/dropout/scale handling;
the only GQA change is exact head repetition. CUDA math fallback is forbidden.
"""
from contextlib import contextmanager
from unittest.mock import patch

POLICY='explicit_kv_fused_sdpa_v1'


def cuda_probe():
    import torch
    import torch.nn.functional as F
    from torch.nn.attention import SDPBackend,sdpa_kernel
    from transformers.integrations.sdpa_attention import repeat_kv
    report={'policy':POLICY,'cuda':torch.cuda.is_available(),'selected_backend':None,
        'math_fallback_allowed':False,'attempts':[],'full_model_loaded':False}
    if not report['cuda']:return report|{'state':'blocked','reason':'CUDA unavailable'}
    report['flash_compiled']=torch.backends.cuda.is_flash_attention_available()
    dtype=torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
    report['dtype']=str(dtype);index=torch.cuda.current_device()
    report['device']=torch.cuda.get_device_name(index);torch.cuda.reset_peak_memory_stats(index)
    candidates=['FLASH_ATTENTION','EFFICIENT_ATTENTION','CUDNN_ATTENTION']
    with torch.random.fork_rng(devices=[index]):
        for name in candidates:
            if name=='FLASH_ATTENTION' and not report['flash_compiled']:continue
            cases=[];q=k=v=out=None
            try:
                with sdpa_kernel([getattr(SDPBackend,name)]):
                    for qlen,klen in ((64,64),(3866,3866),(4096,4096),(1,64)):
                        q=torch.randn(1,32,qlen,128,device='cuda',dtype=dtype,requires_grad=True)
                        k=torch.randn(1,8,klen,128,device='cuda',dtype=dtype,requires_grad=True)
                        v=torch.randn_like(k,requires_grad=True)
                        out=F.scaled_dot_product_attention(q,repeat_kv(k,4),repeat_kv(v,4),
                            is_causal=qlen>1,dropout_p=0.,enable_gqa=False)
                        operator=type(out.grad_fn).__name__
                        out[...,0].sum().backward();torch.cuda.synchronize()
                        if not all(t.grad is not None and torch.isfinite(t.grad).all().item() for t in (q,k,v)):
                            raise RuntimeError('Nonfinite or missing fused attention gradients')
                        cases.append({'query_tokens':qlen,'key_tokens':klen,'operator':operator,'forward_backward_passed':True})
                        del out,q,k,v
                report['attempts'].append({'backend':name,'state':'passed','cases':cases})
                report.update(state='ready',selected_backend=name);break
            except RuntimeError as error:
                report['attempts'].append({'backend':name,'state':'failed','cases':cases,'error':str(error)[:1500]})
            finally:
                # Probe-local references/cache must not consume the model budget.
                q=k=v=out=None
                import gc
                gc.collect();torch.cuda.empty_cache()
    if report['selected_backend'] is None:report.update(state='blocked',reason='No fused SDPA backend passed forward/backward; inspect probe report before loading 8B')
    report['probe_peak_allocated_gib']=torch.cuda.max_memory_allocated(index)/2**30
    report['probe_peak_reserved_gib']=torch.cuda.max_memory_reserved(index)/2**30
    return report


@contextmanager
def attention_route(*,testing=False,report=None):
    import torch.nn.functional as F
    from torch.nn.attention import SDPBackend,sdpa_kernel
    from transformers.integrations import sdpa_attention as hf
    if not testing and (report is None or report.get('state')!='ready' or report.get('selected_backend') not in ('FLASH_ATTENTION','EFFICIENT_ATTENTION','CUDNN_ATTENTION')):
        raise RuntimeError('Verified fused CUDA SDPA probe required before model training')
    original=F.scaled_dot_product_attention
    audit={'policy':POLICY,'selected_backend':report['selected_backend'] if report else 'cpu_fixture',
        'calls':0,'cuda_calls':0,'max_query_tokens':0,'max_key_tokens':0,'native_gqa_calls':0,
        'math_fallback_allowed':bool(testing),'software_fixture':bool(testing)}
    def checked(query,key,value,*args,**kwargs):
        if kwargs.get('enable_gqa',False):
            audit['native_gqa_calls']+=1
            raise RuntimeError('SDPA bypassed explicit KV expansion')
        if query.shape[1]!=key.shape[1] or key.shape[1]!=value.shape[1]:
            raise RuntimeError('SDPA bypassed explicit KV expansion')
        audit['current_query_tokens']=int(query.shape[-2]);audit['current_key_tokens']=int(key.shape[-2])
        if query.device.type=='cuda':
            if testing:raise RuntimeError('CPU fixture cannot certify CUDA attention')
            # Exactly one validated fused backend; never silently use math.
            with sdpa_kernel([getattr(SDPBackend,audit['selected_backend'])]):out=original(query,key,value,*args,**kwargs)
            audit['cuda_calls']+=1
        elif testing:out=original(query,key,value,*args,**kwargs)
        else:raise RuntimeError('All-GPU attention required')
        audit['calls']+=1;audit['max_query_tokens']=max(audit['max_query_tokens'],int(query.shape[-2]))
        audit['max_key_tokens']=max(audit['max_key_tokens'],int(key.shape[-2]))
        return out
    # HF's registered sdpa function reads these canonical module globals on
    # every call, including checkpoint recomputation and cached generation.
    with patch.object(hf,'use_gqa_in_sdpa',lambda attention_mask,key:False),patch.object(F,'scaled_dot_product_attention',checked):
        yield audit
