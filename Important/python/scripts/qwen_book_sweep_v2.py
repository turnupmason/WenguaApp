"""Continuous book-only QLoRA with staged structural and optimization trials."""
import argparse
from pathlib import Path
import time
from src.wengua import qwen_book_sweep_v2 as sweep
from src.wengua.qwen_book_continuous_v1 import book


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('command',choices=('plan','run'))
    p.add_argument('--spec',type=Path,default=sweep.SPEC)
    p.add_argument('--output',type=Path,default=Path('local/qwen_book_sweep_v2/run1'))
    p.add_argument('--hours',type=float,default=168);p.add_argument('--resume',action='store_true')
    p.add_argument('--resume-from-checkpoint',type=Path)
    a=p.parse_args(argv);spec=book.read_json(a.spec)
    if a.command=='plan':result=sweep.plan(spec)
    else:
        if not 0<a.hours<=168:p.error('hours must be positive and <=168; same command resumes the remaining work')
        result=sweep.run(a.output,spec,time.time()+3600*a.hours,resume=a.resume,resume_from_checkpoint=a.resume_from_checkpoint)
    print(book.json.dumps(result,ensure_ascii=False,indent=2),flush=True)


if __name__=='__main__':main()
