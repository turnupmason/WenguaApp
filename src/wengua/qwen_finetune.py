"""Optional CUDA QLoRA training. Heavy dependencies are imported only on demand.

No full-model tuning, no 32B download during data preparation. Oversized cases
are counted and excluded, not silently truncated into false supervision. This
is a source-study adapter, not an independently verified forecast model.
"""
from __future__ import annotations

import importlib.metadata
import json
import platform
from pathlib import Path
import sys

from .qwen_research import DEFAULT_CONFIG, VERSION, digest, private_path, read_rows, write_json


def load_config(path=DEFAULT_CONFIG):
    config = json.loads(Path(path).read_text(encoding='utf8'))
    if config['schema'] != VERSION or config['production_enabled'] or config['event_probabilities_enabled']:
        raise ValueError('Research-only configuration required')
    if config['max_seq_length'] < 128 or config['lora_r'] < 1:
        raise ValueError('Invalid sequence length or rank')
    return config


def environment_report():
    report = {'python': sys.version.split()[0], 'platform': platform.system(),
              'cuda_available': False, 'cuda_devices': [],
              'actual_32b_training_verified': False, 'dependencies': {}}
    for package in ('torch', 'transformers', 'peft', 'accelerate', 'bitsandbytes'):
        try:
            report['dependencies'][package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            report['dependencies'][package] = None
    try:
        import torch
        report['cuda_available'] = torch.cuda.is_available()
        if report['cuda_available']:
            for index in range(torch.cuda.device_count()):
                free, total = torch.cuda.mem_get_info(index)
                report['cuda_devices'].append({'index': index, 'name': torch.cuda.get_device_name(index),
                                               'total_gib': round(total / 2**30, 2), 'free_gib': round(free / 2**30, 2)})
    except ImportError:
        pass
    report['training_route'] = 'CUDA NF4 QLoRA; RTX 4090 memory fit requires a real smoke run'
    return report


def checked_splits(data):
    data = Path(data)
    manifest = json.loads((data / 'manifest.json').read_text(encoding='utf8'))
    if manifest['schema'] != VERSION:
        raise ValueError('Wrong dataset version')
    for name, sha in manifest['file_sha256'].items():
        if Path(name).name != name or digest((data / name).read_bytes()) != sha:
            raise ValueError('Dataset hash mismatch: ' + name)
    result = {s: read_rows(data / (s + '.jsonl')) for s in ('train', 'validation', 'test')}
    owners = {}
    for split, rows in result.items():
        for row in rows:
            if row['group'] in owners and owners[row['group']] != split:
                raise ValueError('Event/passage leakage across splits')
            owners[row['group']] = split
            if row['split'] != split or row['mode'] != 'source_study' or row['eligible_forecast_supervision']:
                raise ValueError('Unsupported forecast supervision or split')
            messages = row['messages']
            if [m['role'] for m in messages] != ['system', 'user', 'assistant']:
                raise ValueError('Expected a single supervised assistant turn')
            if json.loads(messages[-1]['content'])['event_probability'] is not None:
                raise ValueError('Generated percentage supervision is not allowed')
    return result, manifest


def encode_sample(row, tokenizer, max_length):
    options = {'tokenize': True, 'enable_thinking': False}
    prefix = tokenizer.apply_chat_template(row['messages'][:-1], add_generation_prompt=True, **options)
    full = tokenizer.apply_chat_template(row['messages'], add_generation_prompt=False, **options)
    if full[:len(prefix)] != prefix:
        raise ValueError('Chat template prefix mismatch; do not mask the wrong tokens')
    if len(full) > max_length:
        return None, len(full)
    if len(full) <= len(prefix):
        raise ValueError('No assistant target tokens')
    return {'input_ids': full, 'attention_mask': [1] * len(full),
            'labels': [-100] * len(prefix) + full[len(prefix):]}, len(full)


def tokenize_split(rows, tokenizer, max_length):
    encoded, skipped, tasks = [], [], {}
    for row in rows:
        item, size = encode_sample(row, tokenizer, max_length)
        if item is None:
            skipped.append({'id': row['id'], 'group': row['group'], 'tokens': size, 'reason': 'over_context_limit_not_truncated'})
        else:
            encoded.append(item)
            tasks[row['task']] = tasks.get(row['task'], 0) + 1
    return encoded, {'accepted': len(encoded), 'accepted_tasks': tasks, 'excluded_long_rows': skipped}


def collator(pad_id):
    def collate(rows):
        import torch
        size = max(len(r['input_ids']) for r in rows)
        return {key: torch.tensor([r[key] + [pad] * (size - len(r[key])) for r in rows], dtype=torch.long)
                for key, pad in [('input_ids', pad_id), ('attention_mask', 0), ('labels', -100)]}
    return collate


def prepare_frozen_base(model, *, gradient_checkpointing=True):
    """Freeze NF4 base without PEFT's blanket FP32 expansion of 2 large matrices.

    Qwen3-32B has untied vocab embeddings/head. Promoting both to FP32 can
    consume several extra GiB, even before activations. Norm vectors remain
    FP32; frozen large matrices retain the loader's BF16/FP16 dtype. The
    non-reentrant checkpoint path does not require embedding-output hooks.
    This does not establish that a particular 24GB GPU fits the whole run.
    """
    import torch
    for parameter in model.parameters():
        parameter.requires_grad_(False)
        if parameter.ndim == 1 and parameter.is_floating_point():
            parameter.data = parameter.data.to(torch.float32)
    model.config.use_cache = False
    if gradient_checkpointing:
        model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={'use_reentrant': False})
    return model


def load_cuda_base(config, *, training):
    import torch
    from transformers import AutoModelForCausalLM, BitsAndBytesConfig
    if not torch.cuda.is_available():
        raise RuntimeError('CUDA GPU required for this 32B QLoRA route. Mac is a client/data-preparation machine.')
    compute = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
    quant = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type='nf4',
                               bnb_4bit_use_double_quant=True, bnb_4bit_compute_dtype=compute)
    model = AutoModelForCausalLM.from_pretrained(config['model_id'], revision=config['revision'],
                quantization_config=quant, device_map={'': torch.cuda.current_device()},
                torch_dtype=compute, attn_implementation='sdpa', trust_remote_code=False)
    model.config.use_cache = not training
    return model, compute


def train(data, output, *, config_path=DEFAULT_CONFIG, max_steps=-1, max_length=None):
    # Validate inputs/hardware before fetching the large checkpoint.
    config = load_config(config_path)
    if max_length is not None:
        if max_length < 128:
            raise ValueError('max_length must be >= 128')
        config['max_seq_length'] = max_length
    rows, manifest = checked_splits(data)
    report = environment_report()
    if not report['cuda_available']:
        raise RuntimeError('No CUDA GPU: use the RTX 4090 machine / WSL2, then run doctor.')
    if any(v is None for v in report['dependencies'].values()):
        raise RuntimeError('Install requirements-qwen.txt in a separate environment first.')
    output = private_path(output)
    output.mkdir(parents=True, exist_ok=False)
    write_json(output / 'run_status.json', {'state': 'preparing', 'config': config, 'environment': report})
    from transformers import AutoTokenizer, Trainer, TrainingArguments, set_seed
    from peft import LoraConfig, get_peft_model
    set_seed(config['seed'])
    tokenizer = AutoTokenizer.from_pretrained(config['model_id'], revision=config['revision'], trust_remote_code=False)
    tokenizer.pad_token = tokenizer.pad_token or tokenizer.eos_token
    tokenizer.padding_side = 'right'
    prepared, token_audit = {}, {}
    for split in ('train', 'validation'):
        prepared[split], token_audit[split] = tokenize_split(rows[split], tokenizer, config['max_seq_length'])
    write_json(output / 'token_audit.json', token_audit)
    if not prepared['train']:
        raise ValueError('No train rows fit; inspect token_audit.json. No target is silently truncated.')
    try:
        import torch
        torch.cuda.reset_peak_memory_stats()
        model, compute = load_cuda_base(config, training=True)
        model = prepare_frozen_base(model, gradient_checkpointing=config['gradient_checkpointing'])
        model = get_peft_model(model, LoraConfig(r=config['lora_r'], lora_alpha=config['lora_alpha'],
                    lora_dropout=config['lora_dropout'], target_modules=config['target_modules'],
                    bias='none', task_type='CAUSAL_LM'))
        model.print_trainable_parameters()
        args = TrainingArguments(output_dir=str(output / 'trainer'),
                per_device_train_batch_size=config['batch_size'], per_device_eval_batch_size=1,
                gradient_accumulation_steps=config['gradient_accumulation_steps'],
                learning_rate=config['learning_rate'], num_train_epochs=config['epochs'], max_steps=max_steps,
                warmup_ratio=0.1, logging_steps=1, save_strategy='no', eval_strategy='no',
                gradient_checkpointing=config['gradient_checkpointing'],
                gradient_checkpointing_kwargs={'use_reentrant': False},
                bf16=str(compute).endswith('bfloat16'), fp16=str(compute).endswith('float16') and not str(compute).endswith('bfloat16'),
                optim='adamw_torch', report_to='none', seed=config['seed'], data_seed=config['seed'],
                dataloader_num_workers=0, remove_unused_columns=False)
        trainer = Trainer(model=model, args=args, train_dataset=prepared['train'],
                          eval_dataset=prepared['validation'] or None, processing_class=tokenizer,
                          data_collator=collator(tokenizer.pad_token_id))
        result = trainer.train()
        validation = trainer.evaluate() if prepared['validation'] else {'not_run': 'no_validation_rows_fit'}
        model.save_pretrained(output / 'adapter', safe_serialization=True)
        tokenizer.save_pretrained(output / 'adapter')
        write_json(output / 'run_status.json', {'state': 'complete', 'config': config, 'environment': report,
                   'dataset_manifest_sha256': digest((Path(data) / 'manifest.json').read_bytes()),
                   'source_database_sha256': manifest['source_database_sha256'], 'token_audit': token_audit,
                   'training_metrics': result.metrics, 'validation_language_loss': validation,
                   'peak_gpu_allocated_gib': torch.cuda.max_memory_allocated() / 2**30,
                   'peak_gpu_reserved_gib': torch.cuda.max_memory_reserved() / 2**30,
                   'test_generation_evaluated': False, 'prediction_accuracy_verified': False,
                   'production_enabled': False, 'artifact': 'adapter', 'max_steps': max_steps})
        return {'output': str(output), 'state': 'complete', 'production_enabled': False}
    except Exception as error:
        write_json(output / 'failure.json', {'type': type(error).__name__, 'message': str(error)[:1000],
                                          'state': 'failed_not_a_trained_model'})
        raise


def local_answer(messages, adapter_run, max_new_tokens=512):
    """Direct 4090 inference using the saved original NF4 base + LoRA adapter."""
    from transformers import AutoTokenizer
    from peft import PeftModel
    run = private_path(adapter_run)
    status = json.loads((run / 'run_status.json').read_text(encoding='utf8'))
    if status.get('state') != 'complete':
        raise ValueError('A completed adapter run is required')
    config = status['config']
    context_limit = config.get('inference_max_context', config['max_seq_length'])
    if not 1 <= max_new_tokens < context_limit:
        raise ValueError('Reserve a positive input token budget')
    tokenizer = AutoTokenizer.from_pretrained(run / 'adapter', trust_remote_code=False)
    inputs = tokenizer.apply_chat_template(messages, tokenize=True, add_generation_prompt=True,
                                           enable_thinking=False, return_tensors='pt')
    if inputs.shape[1] + max_new_tokens > context_limit:
        raise ValueError('Prompt + response exceed this adapter context budget; reduce references or response length.')
    model, _ = load_cuda_base(config, training=False)
    model = PeftModel.from_pretrained(model, run / 'adapter').eval()
    inputs = inputs.to(model.device)
    import torch
    with torch.inference_mode():
        output = model.generate(inputs, attention_mask=torch.ones_like(inputs), max_new_tokens=max_new_tokens,
                                do_sample=True, temperature=0.7, top_p=0.8, top_k=20,
                                pad_token_id=tokenizer.pad_token_id)
    return tokenizer.decode(output[0, inputs.shape[1]:], skip_special_tokens=True)
