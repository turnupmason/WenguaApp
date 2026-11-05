"""Pinned 8B QLoRA: cache bootstrap, 100-update memory probes and staged SFT."""
import argparse
import os
from pathlib import Path
import time

from src.wengua.qwen8b_book_v1 import profile,CONFIG,SPEC,MODEL,REVISION,ALLOCATOR
from src.wengua.qwen8b_process_v1 import isolated


def cache_ready(book,c):
    from huggingface_hub import try_to_load_from_cache
    if not book.official_model_cached(c):return False
    return all(isinstance(try_to_load_from_cache(MODEL,name,revision=REVISION),str)
        for name in ('tokenizer.json','tokenizer_config.json','generation_config.json'))


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=('plan','doctor','download','run'))
    parser.add_argument('--spec',type=Path,default=SPEC);parser.add_argument('--output',type=Path,default=Path('local/qwen8b_book_v1/run1'))
    parser.add_argument('--hours',type=float,default=168);parser.add_argument('--resume',action='store_true')
    parser.add_argument('--resume-from-checkpoint',type=Path);parser.add_argument('--offline',action='store_true')
    args=parser.parse_args(argv)
    # Must precede any torch import/CUDA context in this interpreter.
    os.environ['PYTORCH_CUDA_ALLOC_CONF']=ALLOCATOR;os.environ['PYTORCH_ALLOC_CONF']=ALLOCATOR
    if args.offline:os.environ['HF_HUB_OFFLINE']='1';os.environ['TRANSFORMERS_OFFLINE']='1'
    p=profile();c=p.engine.base_config();spec=p.book.read_json(args.spec)
    if args.command=='plan':print(p.book.dumps(p.sweep.plan(spec)));return 0
    if args.command=='doctor':print(p.book.dumps(p.doctor(c)));return 0
    if args.command=='run':
        if not 0<args.hours<=168:parser.error('hours must be >0 and <=168; repeat the same command to resume')
        assessment=p.doctor(c)
        if assessment['training_preflight']['status']!='ready_for_smoke_test':raise RuntimeError(assessment['training_preflight']['reason'])
        if any(value is None for value in assessment['dependencies'].values()):raise RuntimeError('Use the existing environment with requirements-qwen.txt installed')
    if not cache_ready(p.book,c):
        if args.offline:raise RuntimeError('Pinned 8B cache is incomplete; run the download command online first')
        from huggingface_hub import snapshot_download
        p.book.progress('download_pinned_qwen8b',model=MODEL,revision=REVISION)
        snapshot_download(repo_id=MODEL,revision=REVISION,allow_patterns=['*.safetensors','*.json','*.txt','*.jinja','*.model'])
        if not cache_ready(p.book,c):raise RuntimeError('Pinned 8B model/tokenizer cache incomplete after download')
    if args.command=='download':print('Pinned Qwen3-8B cache ready.');return 0
    # All training/generation workers start fresh and inherit offline flags,
    # preventing PEFT save-time HEAD requests. Parent tokenizer uses local cache.
    os.environ['HF_HUB_OFFLINE']='1';os.environ['TRANSFORMERS_OFFLINE']='1'
    with isolated(p,args.output):
        result=p.sweep.run(args.output,spec,time.time()+args.hours*3600,resume=args.resume,resume_from_checkpoint=args.resume_from_checkpoint)
    print(p.book.dumps(result))
    return 2 if result['state'] in ('no_feasible_trial','failed') else 0


if __name__=='__main__':raise SystemExit(main())
