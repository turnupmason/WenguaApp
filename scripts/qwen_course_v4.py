"""Launch the reviewed private course in a fresh, resumable 8B experiment."""
import argparse
import faulthandler
import os
from pathlib import Path
import time
from unittest.mock import patch


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=('install','check','plan','doctor','prepare','run'))
    parser.add_argument('--archive',type=Path)
    parser.add_argument('--output',type=Path,default=Path('local/qwen_course_v4/run1'))
    parser.add_argument('--hours',type=float,default=168)
    parser.add_argument('--resume',action='store_true')
    parser.add_argument('--resume-from-checkpoint',type=Path)
    args=parser.parse_args(argv)
    from src.wengua import qwen_course_training_v4 as course
    from src.wengua.qwen8b_book_v1 import ALLOCATOR
    os.environ['PYTORCH_CUDA_ALLOC_CONF']=ALLOCATOR;os.environ['PYTORCH_ALLOC_CONF']=ALLOCATOR
    os.environ.setdefault('HF_HUB_ETAG_TIMEOUT','60');os.environ.setdefault('HF_HUB_DOWNLOAD_TIMEOUT','120')
    p=course.profile();c=p.engine.base_config();spec=course.load(course.SPEC)
    if args.command=='plan':print(p.book.dumps(p.sweep.plan(spec)));return 0
    if args.command=='doctor':print(p.book.dumps(p.doctor(c)));return 0
    if args.archive:course.install_archive(args.archive)
    elif not course.DATA.exists():
        name=course.load(course.RELEASE)['archive_name']
        candidates=[Path.home()/'Downloads'/name,course.storage.ROOT/name]
        found=next((x for x in candidates if x.is_file()),None)
        if found:course.install_archive(found)
        else:raise FileNotFoundError('Download '+name+' into your Downloads folder; then repeat this command.')
    pack=course.verify_data()
    print(p.book.dumps(pack['summary']))
    if args.command in ('install','check'):return 0
    if args.command=='prepare':
        meta=course.prepare(args.output,c)
        print(p.book.dumps(meta));return 0
    if not 0<args.hours<=168:parser.error('hours must be >0 and <=168')
    assessment=p.doctor(c)
    if assessment['training_preflight']['status']!='ready_for_smoke_test':raise RuntimeError(assessment['training_preflight']['reason'])
    if any(v is None for v in assessment['dependencies'].values()):raise RuntimeError('Use local/qwen_env with requirements-qwen.txt')
    from scripts.qwen8b_research import download_cached_model
    download_cached_model(p.book,c)
    os.environ['HF_HUB_OFFLINE']='1';os.environ['TRANSFORMERS_OFFLINE']='1'
    from src.wengua.qwen_course_process_v4 import isolated
    from src.wengua import qwen8b_diagnostics_v1 as diag
    def course_request(command):
        if not isinstance(command,(list,tuple)) or not any(Path(str(x)).name=='run_qwen_course_v4_worker.py' for x in command):return None
        path=Path(command[-1]).resolve()
        return path if path.suffix=='.json' and path.parent.name=='worker_calls' and path.is_file() else None
    faulthandler.enable(all_threads=True)
    with patch.object(diag,'worker_request',course_request),diag.diagnostic_processes(),isolated(p,args.output):
        result=p.sweep.run(args.output,spec,time.time()+args.hours*3600,resume=args.resume,resume_from_checkpoint=args.resume_from_checkpoint)
    print(p.book.dumps(result))
    return 0 if result['state']=='complete' else 2


if __name__=='__main__':raise SystemExit(main())
