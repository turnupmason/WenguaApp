"""Fresh Qwen3-14B NF4 QLoRA book-only parameter experiments."""
import argparse
import json
from pathlib import Path
import time
from src.wengua.qwen_book_sweep_v1 import SPEC,expand_spec,run_sweep
from src.wengua.qwen_book_loop_v3 import read_json


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('command',choices=('plan','run'))
    p.add_argument('--spec',type=Path,default=SPEC)
    p.add_argument('--output',type=Path,default=Path('local/qwen_book_sweep_v1/run1'))
    p.add_argument('--hours',type=float,default=168)
    p.add_argument('--resume',action='store_true')
    p.add_argument('--resume-from-checkpoint',type=Path)
    p.add_argument('--retry-oom',action='store_true')
    a=p.parse_args(argv);spec=read_json(a.spec)
    if a.command=='plan':result={'trials':expand_spec(spec),'training_started':False,'quantization':'NF4 QLoRA'}
    else:
        if not 0<a.hours<=168:p.error('--hours must be positive and <=168; rerun with --resume after the budget expires')
        result=run_sweep(a.output,spec,time.time()+a.hours*3600,resume=a.resume,
            resume_from_checkpoint=a.resume_from_checkpoint,retry_oom=a.retry_oom)
    print(json.dumps(result,ensure_ascii=False,indent=2),flush=True)


if __name__=='__main__':main()
