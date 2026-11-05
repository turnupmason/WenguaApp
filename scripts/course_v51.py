"""Continue an approved V4/V5 LoRA with the repaired, evidence-visible course."""
import argparse
import faulthandler
import os
from pathlib import Path
import shutil
import time
from unittest.mock import patch


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=('check','plan','prepare','run'))
    parser.add_argument('--parent',type=Path,help='Formal V4/V5 sealed checkpoint or epoch adapter; default auto-detect')
    parser.add_argument('--archive',type=Path)
    parser.add_argument('--output',type=Path,default=Path('local/course_v51/run1'))
    parser.add_argument('--hours',type=float,default=48)
    parser.add_argument('--resume',action='store_true')
    parser.add_argument('--resume-from-checkpoint',type=Path)
    args=parser.parse_args(argv)
    from src.wengua import course_training_v51 as course
    from src.wengua.course_parent_v51 import snapshot
    from src.wengua.qwen8b_book_v1 import ALLOCATOR
    os.environ['PYTORCH_CUDA_ALLOC_CONF']=ALLOCATOR;os.environ['PYTORCH_ALLOC_CONF']=ALLOCATOR
    if args.command=='plan':
        print('V5.1: one inherited LoRA structure; LR 1e-5; two continuous epochs; fresh phase optimizer; exact resume within phase. Parent/each epoch generations retained. Final test deferred pending semantic review.')
        return 0
    if args.archive:course.install_archive(args.archive)
    elif not course.DATA.exists():
        name=course.load(course.RELEASE)['archive_name'];path=Path.home()/'Downloads'/name
        if not path.is_file():raise FileNotFoundError('Restore the private V5.1 archive with unlock_course_v51.py first')
        course.install_archive(path)
    pack=course.verify_data()
    print(course.storage.dumps(pack['summary']))
    if args.command=='check':return 0
    if not 0<args.hours<=168:parser.error('hours must be >0 and <=168')
    root=course.storage.private_output(args.output)
    proof=snapshot(root,args.parent)
    c=course.load(course.CONFIG)
    for key in ('lora_r','lora_alpha','lora_dropout','target_modules'):
        c[key]=proof['parent_config'][key]
    c.update(book_parent_snapshot=str(root/'parent_adapter'),
        book_parent_provenance_sha256=course.storage.file_sha(root/'parent_provenance.json'))
    p=course.profile();b=p.book;e=p.engine
    contract={'schema':course.SCHEMA,'code_sha256':course.hashes(),'config':c,
        'data_release_sha256':b.file_sha(course.RELEASE),'parent_provenance_sha256':c['book_parent_provenance_sha256']}
    file=root/'sweep_contract.json'
    if file.exists() and b.read_json(file)!=contract:raise ValueError('Phase contract changed; old output preserved')
    if not file.exists():b.atomic_json(file,contract)
    job=e.open_job(root/'trials'/'inherited_repair',c,resume=args.resume)
    if args.command=='run':
        assessment=p.doctor(c)
        if assessment['training_preflight']['status']!='ready_for_smoke_test':raise RuntimeError(assessment['training_preflight']['reason'])
    from scripts.qwen8b_research import download_cached_model
    download_cached_model(b,c)
    os.environ['HF_HUB_OFFLINE']='1';os.environ['TRANSFORMERS_OFFLINE']='1'
    course.prepare(job,c)
    if args.command=='prepare':return 0
    from src.wengua.course_process_v51 import isolated
    from src.wengua import qwen8b_diagnostics_v1 as diag
    def request(command):
        if not isinstance(command,(list,tuple)) or not any(Path(str(x)).name=='run_course_v51_worker.py' for x in command):return None
        path=Path(command[-1]).resolve()
        return path if path.suffix=='.json' and path.parent.name=='worker_calls' and path.is_file() else None
    faulthandler.enable(all_threads=True);deadline=time.time()+args.hours*3600
    try:
        with patch.object(diag,'worker_request',request),diag.diagnostic_processes(),isolated(p,root):
            with b.job_lock(job/'run.lock'):probe=e.fit(job,c,deadline,probe=True)
            if probe['state']!='complete':return 2
            result=e.run_trial(job,c,deadline,resume_from_checkpoint=args.resume_from_checkpoint)
        b.atomic_json(root/'phase_status.json',result)
        return 0 if result['state']=='complete' else 2
    finally:
        # Rendering is additive. A crash must remain visible with its original receipt.
        if (job/'results.html').exists():shutil.copy2(job/'results.html',root/'results.html')
        print('Report: '+str(root/'results.html'))

if __name__=='__main__':raise SystemExit(main())
