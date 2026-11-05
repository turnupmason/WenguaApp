"""Exact shifted-label CE with checkpointed, bounded-size vocabulary projections.

Only the Qwen3 decoder is evaluated for the full input. Frozen lm_head is
applied to supervised next-token positions in chunks; its CE is recomputed
during backward. No labels, weights, prompt tokens or normalization are changed.
"""
from contextlib import contextmanager
from unittest.mock import patch


def supervised_loss(model,inputs,*,chunk_tokens=128,num_items_in_batch=None,audit=None):
    import torch
    import torch.nn.functional as F
    from torch.utils.checkpoint import checkpoint
    base=model.get_base_model() if hasattr(model,'get_base_model') else model
    if base.config.model_type!='qwen3':raise ValueError('Qwen3 decoder required')
    if any(p.requires_grad for p in base.lm_head.parameters()):raise ValueError('Frozen vocabulary head required')
    labels=inputs['labels'];targets=labels[:,1:]
    positions=targets.ne(-100).any(dim=0).nonzero(as_tuple=False).flatten()
    if positions.numel()==0:raise ValueError('No supervised next-token targets')
    data={k:v for k,v in inputs.items() if k!='labels'}
    data.update(use_cache=False,return_dict=True)
    hidden=base.model(**data).last_hidden_state
    def projected_ce(h,t):
        if h.shape[1]>chunk_tokens:raise RuntimeError('Vocabulary projection exceeded bounded-loss chunk size')
        if audit is not None:audit['max_projected_positions']=max(audit['max_projected_positions'],int(h.shape[1]))
        logits=base.lm_head(h).float()
        return F.cross_entropy(logits.reshape(-1,logits.shape[-1]),t.reshape(-1),ignore_index=-100,reduction='sum')
    total=None
    for indices in positions.split(chunk_tokens):
        h=hidden.index_select(1,indices);t=targets.index_select(1,indices)
        if torch.is_grad_enabled() and h.requires_grad:
            value=checkpoint(projected_ce,h,t,use_reentrant=False,preserve_rng_state=False)
        else:value=projected_ce(h,t)
        total=value if total is None else total+value
    count=targets.ne(-100).sum() if num_items_in_batch is None else num_items_in_batch
    return total/torch.as_tensor(count,device=total.device,dtype=total.dtype)


@contextmanager
def memory_trainer(chunk_tokens):
    # Loading Trainer can replace transformers' root LazyModule object. Patch
    # the canonical class method, so both later imports and existing aliases
    # see the same implementation. Root-module attribute patches are unsafe.
    from transformers.trainer import Trainer
    audit={'route':'canonical_trainer_compute_loss_v2','chunk_tokens':chunk_tokens,
        'compute_loss_calls':0,'train_loss_calls':0,'eval_loss_calls':0,'max_projected_positions':0}
    def compute_loss(self,model,inputs,return_outputs=False,num_items_in_batch=None):
        if self.accelerator.num_processes!=1:raise ValueError('Single-GPU normalization required')
        audit['compute_loss_calls']+=1
        audit['train_loss_calls' if model.training else 'eval_loss_calls']+=1
        with self.accelerator.autocast():
            loss=supervised_loss(model,inputs,chunk_tokens=chunk_tokens,num_items_in_batch=num_items_in_batch,audit=audit)
        return (loss,{'loss':loss}) if return_outputs else loss
    # Worker lifetime only; restore the canonical method even on OOM/interrupt.
    # Old 14B modules on disk and other interpreter processes stay unchanged.
    with patch.object(Trainer,'compute_loss',compute_loss):yield audit
