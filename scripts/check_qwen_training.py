"""Real CPU tiny-Qwen3/LoRA/tokenizer integration; NOT a 32B/CUDA memory test."""
import json
from copy import deepcopy
from pathlib import Path
import tempfile

from src.wengua.qwen_finetune import collator, encode_sample, fit_inference_prompt, load_config, prepare_frozen_base
from src.wengua.qwen_research import ROOT, build_pack, make_prompt, sample, write_json


def main():
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, Qwen3Config, Qwen3ForCausalLM, Trainer, TrainingArguments, set_seed
    from peft import LoraConfig, PeftModel, get_peft_model
    torch.set_num_threads(2)
    (ROOT / 'local').mkdir(exist_ok=True)
    set_seed(3407)
    config = load_config()
    tokenizer = AutoTokenizer.from_pretrained(config['model_id'], revision=config['revision'], trust_remote_code=False)
    tokenizer.pad_token = tokenizer.pad_token or tokenizer.eos_token
    prompt, documents = make_prompt('古籍中天芮星与天心星的作用有什么区别？', build_pack()['documents'], mode='source_study')
    _, kept, budget = fit_inference_prompt(prompt, documents, tokenizer, context_limit=2048, max_new_tokens=768)
    assert budget['input_tokens'] + budget['max_new_tokens'] <= 2048
    assert kept and budget['dropped_reference_ids']
    assert {(9, 9), (11, 11)} <= {tuple(d.get('lines', [])) for d in kept
                                if d.get('section_key') == 'health_prediction_ch01'}
    row = sample('integration', 'synthetic_no_historical_event', '说明来源。',
                 {'mode': 'source_study', 'summary': '这是程序夹具。', 'evidence': [],
                  'counter_evidence': [], 'missing_information': [], 'event_probability': None}, 'synthetic')
    encoded, length = encode_sample(row, tokenizer, 2048)
    assert encoded and any(x != -100 for x in encoded['labels'])
    first = next(i for i, v in enumerate(encoded['labels']) if v != -100)
    assert first > 0 and encoded['labels'][:first] == [-100] * first
    model = Qwen3ForCausalLM(Qwen3Config(vocab_size=len(tokenizer), hidden_size=32,
                intermediate_size=64, num_hidden_layers=1, num_attention_heads=2,
                num_key_value_heads=1, head_dim=16, max_position_embeddings=4096))
    model = prepare_frozen_base(model.to(torch.bfloat16))
    assert model.get_input_embeddings().weight.dtype == torch.bfloat16
    assert model.get_output_embeddings().weight.dtype == torch.bfloat16
    assert all(not p.requires_grad for p in model.parameters())
    assert all(p.dtype == torch.float32 for p in model.parameters() if p.ndim == 1)
    independent_base = deepcopy(model)
    model = get_peft_model(model, LoraConfig(r=8, lora_alpha=16, target_modules=['q_proj', 'v_proj'],
                                           lora_dropout=0.0, task_type='CAUSAL_LM'))
    before = {k: v.detach().clone() for k, v in model.named_parameters() if v.requires_grad}
    with tempfile.TemporaryDirectory(dir=ROOT / 'local') as temp:
        independent_base.save_pretrained(Path(temp) / 'cached_base')
        cached = AutoModelForCausalLM.from_pretrained(Path(temp) / 'cached_base', dtype=torch.bfloat16,
                                                    local_files_only=True, trust_remote_code=False)
        assert cached.get_input_embeddings().weight.dtype == torch.bfloat16
        del cached
        args = TrainingArguments(output_dir=temp, max_steps=2, per_device_train_batch_size=1,
                                 learning_rate=0.001, report_to='none', save_strategy='no', logging_steps=1,
                                 use_cpu=True, bf16=True, dataloader_pin_memory=False, seed=3407)
        trainer = Trainer(model=model, args=args, train_dataset=[encoded], processing_class=tokenizer,
                          data_collator=collator(tokenizer.pad_token_id))
        result = trainer.train()
        assert torch.isfinite(torch.tensor(result.training_loss))
        assert any(not torch.equal(before[k], v) for k, v in model.named_parameters() if v.requires_grad)
        model.save_pretrained(Path(temp) / 'adapter', safe_serialization=True)
        restored = PeftModel.from_pretrained(independent_base, Path(temp) / 'adapter').eval()
        # Test serialization independently from the trained adapter instance.
        batch = collator(tokenizer.pad_token_id)([encoded])
        model.eval()
        with torch.no_grad(), torch.autocast('cpu', dtype=torch.bfloat16):
            original = model(**batch).logits
            actual = restored(**batch).logits
        # Accelerate wraps the trained forward and upcasts its output to FP32;
        # the independently reloaded model returns BF16. Compare same values.
        assert torch.allclose(original.float(), actual.float(), atol=1e-6)
        receipt = {'state': 'passed', 'test': 'tiny_random_qwen3_cpu_lora', 'steps': 2,
                   'tokenizer': config['model_id'], 'tokenizer_revision': config['revision'],
                   'assistant_mask_tokens': first, 'total_tokens': length,
                   'trainable_weights_changed': True, 'adapter_reload_logits_equal': True,
                   'frozen_large_matrices_keep_bf16': True, 'norm_vectors_fp32': True,
                   'official_tokenizer_inference_budget': budget,
                   'offline_cached_dtype_loader': True,
                   'loss': result.training_loss, 'real_32b_trained': False,
                   'real_full_size_model_trained': False, 'cuda_nf4_tested': False}
    profile = 'qwen14b_v1' if config['model_id'] == 'Qwen/Qwen3-14B' else 'qwen32b_v1'
    output = ROOT / 'local' / profile / 'tiny_integration.json'
    output.parent.mkdir(parents=True, exist_ok=True)
    write_json(output, receipt)
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
