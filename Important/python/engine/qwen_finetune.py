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

from .qwen_research import DEFAULT_CONFIG, VERSION, digest, json_text, private_path, read_rows, write_json


def load_config(path=DEFAULT_CONFIG):
    config = json.loads(Path(path).read_text(encoding='utf8'))
    if config['schema'] != VERSION or config['production_enabled'] or config['event_probabilities_enabled']:
        raise ValueError('Research-only configuration required')
    if config['max_seq_length'] < 128 or config['lora_r'] < 1:
        raise ValueError('Invalid sequence length or rank')
    return config


def assess_gpu_capacity(report, config):
    """Reject a known unsuitable card before downloads, without claiming fit.

    Qwen3-32B's ~32.8B parameters alone need ~15.3 GiB at ideal 4 bits;
    the untied non-quantized vocab matrices increase that, before metadata,
    activations or CUDA buffers. A 16 GiB card cannot fit this all-GPU route.
    The per-model total/free screen is a conservative launch policy, NOT a
    measured minimum or a promise that a card can finish training.
    Only assess this configured loader, not all possible offload frameworks.
    """
    result = {'model_id': config['model_id'], 'status': 'blocked',
              'actual_training_fit_verified': False}
    if not report.get('cuda_available'):
        return dict(result, reason='CUDA GPU unavailable; data preparation remains usable.')
    selected = report.get('current_device_index', 0)
    device = next((d for d in report.get('cuda_devices', []) if d['index'] == selected), None)
    if device is None:
        return dict(result, reason='Current CUDA device memory is unknown; run doctor.')
    result['selected_device'] = device
    minimum = {'Qwen/Qwen3-32B': 20, 'Qwen/Qwen3-14B': 12}.get(config['model_id'])
    if minimum is None:
        return dict(result, status='not_assessed', reason='No memory launch policy for this model.')
    result['minimum_total_gib_screen'] = minimum
    result['minimum_free_gib_screen'] = minimum
    if device['total_gib'] < minimum:
        return dict(result, reason=f"{device['name']} has {device['total_gib']} GiB total VRAM. "
                    f"The configured {config['model_id']} all-GPU NF4 route excludes cards below the {minimum} GiB launch screen. "
                    'No weights downloaded; use a larger-memory GPU or explicitly choose a smaller model.')
    if device['free_gib'] < minimum:
        return dict(result, reason=f"Only {device['free_gib']} GiB free VRAM on the selected GPU; "
                    f'release other GPU workloads before retrying the {minimum} GiB launch screen.')
    return dict(result, status='ready_for_smoke_test',
                reason='Launch screen passed; real model loading and training memory fit remain unverified.')


def environment_report(config=None):
    report = {'python': sys.version.split()[0], 'platform': platform.system(),
              'cuda_available': False, 'cuda_devices': [],
              'actual_32b_training_verified': False, 'actual_full_size_training_verified': False,
              'dependencies': {}}
    for package in ('torch', 'transformers', 'peft', 'accelerate', 'bitsandbytes'):
        try:
            report['dependencies'][package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            report['dependencies'][package] = None
    try:
        import torch
        report['cuda_available'] = torch.cuda.is_available()
        if report['cuda_available']:
            report['current_device_index'] = torch.cuda.current_device()
            for index in range(torch.cuda.device_count()):
                free, total = torch.cuda.mem_get_info(index)
                report['cuda_devices'].append({'index': index, 'name': torch.cuda.get_device_name(index),
                                               'total_gib': round(total / 2**30, 2), 'free_gib': round(free / 2**30, 2)})
    except ImportError:
        pass
    config = config if config is not None else load_config()
    report['training_route'] = config['model_id'] + ' CUDA NF4 QLoRA; inspect training_preflight on the actual selected GPU'
    report['training_preflight'] = assess_gpu_capacity(report, config)
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


def load_cuda_base(config, *, training, allow_download=False):
    import torch
    assessment = assess_gpu_capacity(environment_report(config), config)
    if assessment['status'] == 'blocked':
        raise RuntimeError(assessment['reason'])
    from transformers import AutoModelForCausalLM, BitsAndBytesConfig
    compute = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
    quant = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type='nf4',
                               bnb_4bit_use_double_quant=True, bnb_4bit_compute_dtype=compute)
    model = AutoModelForCausalLM.from_pretrained(config['model_id'], revision=config['revision'],
                quantization_config=quant, device_map={'': torch.cuda.current_device()},
                dtype=compute, attn_implementation='sdpa', trust_remote_code=False,
                local_files_only=not (training or allow_download))
    model.config.use_cache = not training
    return model, compute


def train(data, output, *, config_path=DEFAULT_CONFIG, max_steps=-1, max_length=None):
    # Validate inputs/hardware before fetching the large checkpoint.
    config = load_config(config_path)
    if max_length is not None:
        if max_length < 128:
            raise ValueError('max_length must be >= 128')
        config['max_seq_length'] = max_length
    report = environment_report(config)
    assessment = assess_gpu_capacity(report, config)
    if assessment['status'] == 'blocked':
        raise RuntimeError(assessment['reason'])
    if any(v is None for v in report['dependencies'].values()):
        raise RuntimeError('Install requirements-qwen.txt in a separate environment first.')
    rows, manifest = checked_splits(data)
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


def fit_inference_prompt(messages, documents, tokenizer, *, context_limit, max_new_tokens):
    """Keep whole retrieved references that fit, preserving question/chart/system.

    Count the actual official chat template. Never truncate palace facts or
    silently allow citations to references that were not sent to the model.
    Retrieval order is preserved; an oversized first hit must not exclude all
    smaller useful references. This verifies length, not semantic relevance.
    """
    if not 1 <= max_new_tokens < context_limit:
        raise ValueError('Reserve a positive input token budget')
    if not messages or messages[-1].get('role') != 'user':
        raise ValueError('Expected final structured user message')
    payload = json.loads(messages[-1]['content'])
    candidates = payload['references']
    by_id = {d['id']: d for d in documents}
    if any(r['id'] not in by_id for r in candidates):
        raise ValueError('Prompt contains an unregistered source reference')

    def render(references):
        value = dict(payload, references=list(references), no_references=not references)
        return [dict(m) for m in messages[:-1]] + [dict(messages[-1], content=json_text(value))]

    def count(value):
        return len(tokenizer.apply_chat_template(value, tokenize=True, add_generation_prompt=True,
                                                  enable_thinking=False))

    budget = context_limit - max_new_tokens
    selected, dropped = [], []
    if count(render([])) > budget:
        raise ValueError('Question, system instructions and program chart exceed input budget; none were truncated.')
    for reference in candidates:
        if count(render(selected + [reference])) <= budget:
            selected.append(reference)
        else:
            dropped.append(reference['id'])
    fitted = render(selected)
    return fitted, [by_id[r['id']] for r in selected], {
        'context_limit': context_limit, 'max_new_tokens': max_new_tokens,
        'original_input_tokens': count(messages), 'input_tokens': count(fitted),
        'kept_reference_ids': [r['id'] for r in selected], 'dropped_reference_ids': dropped,
        'question_chart_and_system_truncated': False, 'reference_content_truncated': False}


def local_answer(messages, adapter_run, max_new_tokens=512, *, documents=None,
                 base_only=False, return_details=False, allow_model_download=False):
    """Direct CUDA inference, optionally comparing the identical base without LoRA."""
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
    tokenizer = AutoTokenizer.from_pretrained(run / 'adapter', trust_remote_code=False, local_files_only=True)
    audit = None
    kept = documents
    if documents is not None:
        messages, kept, audit = fit_inference_prompt(messages, documents, tokenizer,
                    context_limit=context_limit, max_new_tokens=max_new_tokens)
    inputs = tokenizer.apply_chat_template(messages, tokenize=True, add_generation_prompt=True,
                                           enable_thinking=False, return_tensors='pt')
    if inputs.shape[1] + max_new_tokens > context_limit:
        raise ValueError('Prompt + response exceed this adapter context budget; reduce references or response length.')
    model, _ = load_cuda_base(config, training=False, allow_download=allow_model_download)
    if not base_only:
        model = PeftModel.from_pretrained(model, run / 'adapter', local_files_only=True)
    model.eval()
    inputs = inputs.to(model.device)
    import torch
    from transformers import set_seed
    set_seed(config['seed'])
    with torch.inference_mode():
        output = model.generate(inputs, attention_mask=torch.ones_like(inputs), max_new_tokens=max_new_tokens,
                                do_sample=True, temperature=0.7, top_p=0.8, top_k=20,
                                pad_token_id=tokenizer.pad_token_id)
    content = tokenizer.decode(output[0, inputs.shape[1]:], skip_special_tokens=True)
    if return_details:
        return content, kept, {'variant': 'base_only' if base_only else 'adapter', 'model_id': config['model_id'],
                               'seed': config['seed'], 'prompt_budget': audit,
                               'prompt_sha256': digest(json_text(messages)), '_sent_messages': messages,
                               'generated_tokens': int(output.shape[1] - inputs.shape[1]),
                               'reached_token_limit': int(output.shape[1] - inputs.shape[1]) >= max_new_tokens}
    return content
