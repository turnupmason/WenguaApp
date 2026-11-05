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


def transient_download_failure(error,network_errors=(),permanent_errors=()):
    if isinstance(error,permanent_errors):return False
    status=getattr(getattr(error,'response',None),'status_code',None)
    if isinstance(status,int):return status in (408,429) or 500<=status<600
    return isinstance(error,network_errors)


def download_cached_model(book,c,*,download=None,retryable=None,wait=time.sleep):
    """Retry transient Hub/transport failures without clearing partial files.

    Full snapshots remain in the standard Hub cache: completed blobs are reused
    and Hub resumes its own incomplete files. Never force-redownload on retry.
    """
    if cache_ready(book,c):return
    if download is None:
        from huggingface_hub import snapshot_download
        download=snapshot_download
    if retryable is None:
        from huggingface_hub.errors import GatedRepoError,RepositoryNotFoundError,RevisionNotFoundError,LocalEntryNotFoundError
        from requests.exceptions import ConnectionError,Timeout,ChunkedEncodingError
        retryable=lambda e:transient_download_failure(e,
            (ConnectionError,Timeout,ChunkedEncodingError,LocalEntryNotFoundError),
            (GatedRepoError,RepositoryNotFoundError,RevisionNotFoundError))
    for attempt in range(1,6):
        book.progress('download_pinned_qwen8b',model=MODEL,revision=REVISION,attempt=attempt,attempts=5,max_workers=1)
        try:
            download(repo_id=MODEL,revision=REVISION,allow_patterns=['*.safetensors','*.json','*.txt','*.jinja','*.model'],max_workers=1)
        except Exception as error:
            if not retryable(error):raise
            if cache_ready(book,c):return
            if attempt==5:
                raise RuntimeError('Qwen3-8B download failed after 5 network attempts; training has NOT started. '
                    'Partial files remain in the Hugging Face cache. Check access to huggingface.co or your proxy, '
                    'then repeat the same command; do not delete the cache.') from error
            delay=min(5*2**(attempt-1),40)
            book.progress('qwen8b_download_network_retry',attempt=attempt,retry_in_seconds=delay,
                error_type=type(error).__name__,cached_files_preserved=True,training_started=False)
            wait(delay)
        else:
            if not cache_ready(book,c):raise RuntimeError('Pinned 8B model/tokenizer cache incomplete after download; training has NOT started')
            return


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=('plan','doctor','download','run'))
    parser.add_argument('--spec',type=Path,default=SPEC);parser.add_argument('--output',type=Path,default=Path('local/qwen8b_book_v1/run1'))
    parser.add_argument('--hours',type=float,default=168);parser.add_argument('--resume',action='store_true')
    parser.add_argument('--resume-from-checkpoint',type=Path);parser.add_argument('--offline',action='store_true')
    args=parser.parse_args(argv)
    # Must precede any torch import/CUDA context in this interpreter.
    os.environ['PYTORCH_CUDA_ALLOC_CONF']=ALLOCATOR;os.environ['PYTORCH_ALLOC_CONF']=ALLOCATOR
    # Hub reads timeout constants at import time. Keep user overrides intact.
    os.environ.setdefault('HF_HUB_ETAG_TIMEOUT','60');os.environ.setdefault('HF_HUB_DOWNLOAD_TIMEOUT','120')
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
        download_cached_model(p.book,c)
    if args.command=='download':print('Pinned Qwen3-8B cache ready.');return 0
    # All training/generation workers start fresh and inherit offline flags,
    # preventing PEFT save-time HEAD requests. Parent tokenizer uses local cache.
    os.environ['HF_HUB_OFFLINE']='1';os.environ['TRANSFORMERS_OFFLINE']='1'
    with isolated(p,args.output):
        result=p.sweep.run(args.output,spec,time.time()+args.hours*3600,resume=args.resume,resume_from_checkpoint=args.resume_from_checkpoint)
    print(p.book.dumps(result))
    return 2 if result['state'] in ('no_feasible_trial','failed') else 0


if __name__=='__main__':raise SystemExit(main())
