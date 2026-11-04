"""Fresh book-only data preparation and bounded local CUDA training loop."""
import argparse,json,time
from pathlib import Path
from src.wengua.qwen_book_loop_v3 import (CONFIG,load_config,open_job,prepare,run_auto,run_loop)


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='command',required=True)
    for name in ('prepare','run','doctor'):
        p=sub.add_parser(name);p.add_argument('--config',type=Path,default=CONFIG)
        if name!='doctor':
            p.add_argument('--output',type=Path,required=True);p.add_argument('--resume',action='store_true')
            p.add_argument('--cycles',type=int)
        if name=='run':
            p.add_argument('--hours',type=float,default=48);p.add_argument('--fixed-context',action='store_true')
    a=parser.parse_args(argv);c=load_config(a.config,getattr(a,'cycles',None))
    if a.command=='doctor':
        from src.wengua.qwen_finetune import environment_report
        result=environment_report(c)
    elif a.command=='prepare':result=prepare(open_job(a.output,c,resume=a.resume),c)
    else:
        if not 0<a.hours<=168:parser.error('--hours must be positive and <=168; finite cycles still bound the job')
        deadline=time.time()+a.hours*3600
        result=(run_loop if a.fixed_context else run_auto)(a.output,c,deadline,resume=a.resume)
    print(json.dumps(result,ensure_ascii=False,indent=2),flush=True)


if __name__=='__main__':main()
