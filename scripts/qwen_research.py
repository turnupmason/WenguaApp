"""Qwen14B/32B private data / retrieval / optional CUDA adapter commands."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import urllib.request

from src.wengua.qwen_research import (ROOT, DEFAULT_CONFIG, check_answer, export_pack,
                                     make_prompt, read_rows, retrieve, private_path, write_json,
                                     response_type_issues, review_inference_trace)
from src.wengua.qwen_finetune import (checked_splits, environment_report, load_config,
                                     tokenize_split, train)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command')
    review = commands.add_parser('review', help='Read an existing UTF-8 inference trace; no GPU, network or regeneration')
    review.add_argument('--trace', type=Path, required=True)
    prepare = commands.add_parser('prepare', help='Read-only source export, private outputs; no GPU or model download')
    prepare.add_argument('--output', type=Path)
    doctor = commands.add_parser('doctor', help='Local environment and GPU report; no checkpoint download')
    doctor.add_argument('--config', type=Path, default=DEFAULT_CONFIG)
    audit = commands.add_parser('audit-tokens', help='Download tokenizer only; inspect context coverage before downloading weights')
    audit.add_argument('--data', type=Path, required=True)
    audit.add_argument('--max-seq-length', type=int)
    audit.add_argument('--config', type=Path, default=DEFAULT_CONFIG)
    audit.add_argument('--output', type=Path)
    fit = commands.add_parser('train', help='Actual CUDA NF4 QLoRA; first downloads the configured pinned base')
    fit.add_argument('--data', type=Path, required=True)
    fit.add_argument('--output', type=Path, required=True)
    fit.add_argument('--config', type=Path, default=DEFAULT_CONFIG)
    fit.add_argument('--max-steps', type=int, default=-1)
    fit.add_argument('--max-seq-length', type=int)
    for name in ('retrieve', 'prompt', 'ask', 'chat'):
        command = commands.add_parser(name)
        command.add_argument('--data', type=Path, required=True)
        command.add_argument('--question', required=True)
        command.add_argument('--mode', choices=['traditional_reading', 'source_study'], default='traditional_reading')
        if name != 'retrieve':
            command.add_argument('--chart', type=Path, help='Explicit JSON dun/ju/hour_ganzhi; no model calendar inference')
        if name == 'ask':
            command.add_argument('--base-url', default='http://127.0.0.1:11434/v1')
            command.add_argument('--model', default='qwen3:14b', help='Running endpoint model ID; RAG alone is NOT a trained adapter')
        if name == 'chat':
            command.add_argument('--adapter-run', type=Path, required=True)
            command.add_argument('--max-new-tokens', type=int, default=512)
            command.add_argument('--base-only', action='store_true', help='Use the same base/tokenizer/prompt without the trained LoRA')
            command.add_argument('--allow-model-download', action='store_true',
                                 help='Opt into Hub access if the pinned base is absent from the local cache')
    reference = commands.add_parser('reference', help='Explicit private source browser; excluded from evaluation retrieval')
    reference.add_argument('--data', type=Path, required=True)
    reference.add_argument('--id', required=True)
    args = parser.parse_args(argv)
    if args.command == 'review':
        result = review_inference_trace(args.trace)
    elif args.command in (None, 'prepare'):
        stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
        output = getattr(args, 'output', None) or ROOT / 'local/qwen14b_v1' / stamp / 'data'
        result = {'output': str(output), **export_pack(output)}
    elif args.command == 'doctor':
        result = environment_report(load_config(args.config))
    elif args.command == 'audit-tokens':
        from transformers import AutoTokenizer
        config = load_config(args.config)
        splits, _ = checked_splits(args.data)
        tokenizer = AutoTokenizer.from_pretrained(config['model_id'], revision=config['revision'], trust_remote_code=False)
        length = args.max_seq_length if args.max_seq_length is not None else config['max_seq_length']
        if length < 128:
            raise ValueError('max_seq_length must be >= 128')
        result = {s: tokenize_split(rows, tokenizer, length)[1] for s, rows in splits.items()}
        result['max_seq_length'] = length
        result['model_weights_downloaded'] = False
        if args.output:
            path = private_path(args.output)
            if path.exists():
                raise ValueError('Preserve previous token audit; choose a new output path')
            path.parent.mkdir(parents=True, exist_ok=True)
            write_json(path, result)
    elif args.command == 'train':
        result = train(args.data, args.output, config_path=args.config,
                       max_steps=args.max_steps, max_length=args.max_seq_length)
    else:
        documents = read_rows(args.data / 'corpus.jsonl')
        if args.command == 'reference':
            result = next((d for d in documents if d['id'] == args.id), None)
            if result is None:
                raise SystemExit('Unknown reference ID')
        elif args.command == 'retrieve':
            result = retrieve(documents, args.question, mode=args.mode)
        else:
            chart = json.loads(args.chart.read_text(encoding='utf8')) if args.chart else None
            messages, docs = make_prompt(args.question, documents, mode=args.mode, explicit_chart=chart)
            if args.command == 'prompt':
                result = {'messages': messages, 'model_called': False}
            else:
                if args.command == 'chat':
                    from src.wengua.qwen_finetune import local_answer
                    content, docs, generation = local_answer(messages, args.adapter_run, args.max_new_tokens,
                                documents=docs, base_only=args.base_only, return_details=True,
                                allow_model_download=args.allow_model_download)
                else:
                    payload = {'model': args.model, 'messages': messages, 'stream': False,
                               'temperature': 0.7, 'top_p': 0.8, 'max_tokens': 2048,
                               'chat_template_kwargs': {'enable_thinking': False}}
                    request = urllib.request.Request(args.base_url.rstrip('/') + '/chat/completions',
                              data=json.dumps(payload, ensure_ascii=False).encode('utf8'),
                              headers={'Content-Type': 'application/json'})
                    with urllib.request.urlopen(request, timeout=120) as response:
                        raw = response.read(4 * 1024 * 1024 + 1)
                        if len(raw) > 4 * 1024 * 1024:
                            raise ValueError('Oversized model response')
                        content = json.loads(raw)['choices'][0]['message']['content']
                # A non-JSON / invented citation result is rejected, not shown as
                # supported divination just because a server returned HTTP 200.
                if args.command == 'chat':
                    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
                    trace_dir = private_path(args.adapter_run) / 'inference'
                    trace_dir.mkdir(exist_ok=True)
                    trace_path = trace_dir / (stamp + '_' + generation['variant'] + '.json')
                    sent_messages = generation.pop('_sent_messages', None)
                    trace = {'question': args.question, 'mode': args.mode, 'generation': generation,
                             'raw_output': content, 'sent_reference_ids': [d['id'] for d in docs],
                             'sent_messages': sent_messages,
                             'prediction_validated': False, 'production_enabled': False}
                    try:
                        result = check_answer(json.loads(content), docs, args.mode)
                    except (ValueError, TypeError, KeyError) as error:
                        trace.update(status='rejected', error=str(error))
                        try:
                            trace['schema_issues'] = response_type_issues(json.loads(content))
                        except (ValueError, TypeError):
                            trace['schema_issues'] = []
                        write_json(trace_path, trace)
                        print(json.dumps({'status': 'rejected', 'error': str(error),
                                          'schema_issues': trace['schema_issues'], 'raw_output': content,
                                          'trace_path': str(trace_path), 'prediction_validated': False},
                                         ensure_ascii=False, indent=2))
                        raise SystemExit(2) from None
                    trace.update(status='parsed', checked_answer=result)
                    write_json(trace_path, trace)
                    result['generation'] = generation
                    result['trace_path'] = str(trace_path)
                else:
                    result = check_answer(json.loads(content), docs, args.mode)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
