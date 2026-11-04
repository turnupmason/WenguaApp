"""Process lifetime isolation for the unchanged continuous book training kernel.

The coordinator never loads model weights. Each fit/final test uses a fresh
interpreter; exit releases CUDA allocator segments even when empty_cache cannot.
An additional execution receipt pins this runner without rewriting old training
contracts, checkpoints, completed probes or source data.
"""
from __future__ import annotations

from contextlib import contextmanager
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import traceback
import uuid
from unittest.mock import patch

from . import qwen_book_continuous_v1 as engine
from . import qwen_book_sweep_v2 as sweep
from .qwen_book_continuous_v1 import book

SCHEMA='wengua_book_process_v1'
FILES=('src/wengua/qwen_book_process_v1.py','run_qwen_book_worker.py','scripts/qwen_book_sweep_v2.py')


def execution_contract(cpu_fixture=False):
    return {'schema':SCHEMA,'mode':'fresh_process_per_training_unit','training_kernel_unchanged':True,
        'cpu_fixture':cpu_fixture,'code_sha256':{name:book.digest((book.ROOT/name).read_text(encoding='utf8')) for name in FILES}}


def ensure_execution(root,contract):
    root=book.private_output(root);path=root/'process_execution.json'
    if path.exists():
        if book.read_json(path)!=contract:raise ValueError('Process execution code changed; use a new experiment directory')
    elif (root/'sweep_contract.json').exists():book.atomic_json(path,contract)
    # The existing coordinator creates the root and its original contract first.


def stop_child(process):
    if process.poll() is not None:return
    try:process.send_signal(signal.CTRL_BREAK_EVENT if os.name=='nt' else signal.SIGINT)
    except OSError:pass
    try:process.wait(timeout=60)
    except subprocess.TimeoutExpired:
        process.terminate()
        try:process.wait(timeout=10)
        except subprocess.TimeoutExpired:process.kill();process.wait()


def launch(job,c,deadline,operation,*,probe=False,checkpoint=None,best=None,cpu_fixture=False,stop_step=None):
    job=book.private_output(job);root=job.parent.parent
    ensure_execution(root,execution_contract(cpu_fixture))
    calls=job/'worker_calls';calls.mkdir(exist_ok=True)
    request=calls/(str(time.time_ns())+'-'+uuid.uuid4().hex+'.json')
    book.atomic_json(request,{'schema':SCHEMA,'job':str(job),'config':c,'deadline':deadline,'operation':operation,
        'probe':probe,'checkpoint':str(checkpoint) if checkpoint is not None else None,'best':best,
        'cpu_fixture':cpu_fixture,'fixture_stop_step':stop_step})
    result_path=request.with_suffix('.result.json')
    command=[sys.executable,'-X','utf8',str(book.ROOT/'run_qwen_book_worker.py'),str(request)]
    process=subprocess.Popen(command,cwd=book.ROOT,env=os.environ.copy(),
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name=='nt' else 0)
    book.progress('isolated_worker_started',operation=operation,probe=probe,pid=process.pid,trial=job.name)
    try:code=process.wait()
    except BaseException:
        stop_child(process);raise
    book.progress('isolated_worker_exited',operation=operation,pid=process.pid,exit_code=code)
    if not result_path.exists():raise RuntimeError('Worker exited without a result; outputs preserved: '+str(request))
    result=book.read_json(result_path)
    if result.get('request_sha256')!=book.file_sha(request) or result.get('pid')!=process.pid:
        raise ValueError('Worker result/request provenance mismatch')
    if code or not result.get('ok'):
        error=result.get('error',{})
        if error.get('type')=='KeyboardInterrupt':raise KeyboardInterrupt()
        prefix='CUDA out of memory: ' if error.get('cuda_oom') else 'Isolated worker failed: '
        raise RuntimeError(prefix+error.get('message',str(code)))
    return result['result']


@contextmanager
def isolated_execution(root,*,cpu_fixture=False,fixture_stop_once=None):
    """Install explicit execution delegates; child imports the original functions.

    Only execution changes. Original kernel file hashes and training contracts
    remain identical, so a completed run3 probe can be reused without migration.
    """
    contract=execution_contract(cpu_fixture);ensure_execution(root,contract)
    stopping=[fixture_stop_once]
    def fit(job,c,deadline,*,probe=False,cpu_factory=None,extra_callbacks=(),resume_from_checkpoint=None):
        if extra_callbacks or (cpu_factory is not None and not cpu_fixture):raise ValueError('Callbacks/factories cannot cross worker boundaries')
        return launch(job,c,deadline,'fit',probe=probe,checkpoint=resume_from_checkpoint,cpu_fixture=cpu_fixture)
    def trial(job,c,deadline,*,cpu_factory=None,extra_callbacks=(),resume_from_checkpoint=None):
        if extra_callbacks or (cpu_factory is not None and not cpu_fixture):raise ValueError('Callbacks/factories cannot cross worker boundaries')
        step=stopping[0];stopping[0]=None
        return launch(job,c,deadline,'trial',checkpoint=resume_from_checkpoint,cpu_fixture=cpu_fixture,stop_step=step)
    def final(job,c,best,deadline,*,cpu_factory=None):
        if cpu_factory is not None and not cpu_fixture:raise ValueError('Factory cannot cross worker boundary')
        return launch(job,c,deadline,'final',best=best,cpu_fixture=cpu_fixture)
    with patch.object(engine,'fit',fit),patch.object(engine,'run_trial',trial),patch.object(book,'final_test',final):
        yield


def worker(request):
    request=Path(request).resolve();payload=book.read_json(request)
    if payload.get('schema')!=SCHEMA:raise ValueError('Invalid worker schema')
    job=book.private_output(payload['job'])
    if request.parent!=job/'worker_calls':raise ValueError('Worker request must belong to its private trial')
    config=payload['config'];engine.open_job(job,config,resume=True)
    if payload['operation'] not in ('fit','trial','final','ping'):raise ValueError('Invalid worker operation')
    cpu_fixture=payload.get('cpu_fixture') is True
    if payload.get('fixture_stop_step') is not None and not cpu_fixture:raise ValueError('Test controls forbidden for real training')
    factory=None;callbacks=()
    if cpu_fixture:
        from scripts.check_qwen_book_isolated_training import fixture_factory
        factory=fixture_factory
        if payload.get('fixture_stop_step') is not None:
            from transformers import TrainerCallback
            class Stop(TrainerCallback):
                def on_step_end(self,args,state,control,**kwargs):
                    if state.global_step>=payload['fixture_stop_step']:control.should_save=True;control.should_training_stop=True
                    return control
            callbacks=(Stop(),)
    def interrupt(signum,frame):raise KeyboardInterrupt()
    if os.name=='nt':signal.signal(signal.SIGBREAK,interrupt)
    out={'schema':SCHEMA,'pid':os.getpid(),'request_sha256':book.file_sha(request),'cpu_fixture':cpu_fixture}
    try:
        with book.job_lock(job.parent.parent/'isolated_gpu_worker.lock'):
            args=(job,config,payload['deadline'])
            if payload['operation']=='ping':
                result={'pid':os.getpid(),'torch_imported':'torch' in sys.modules,'offline':os.environ.get('HF_HUB_OFFLINE')}
            elif payload['operation']=='fit':
                result=engine.fit(*args,probe=payload['probe'],cpu_factory=factory,resume_from_checkpoint=payload['checkpoint'])
            elif payload['operation']=='trial':
                result=engine.run_trial(*args,cpu_factory=factory,extra_callbacks=callbacks,resume_from_checkpoint=payload['checkpoint'])
            else:result=book.final_test(job,config,payload['best'],payload['deadline'],cpu_factory=factory)
        out.update(ok=True,result=result);code=0
    except BaseException as error:
        out.update(ok=False,error={'type':type(error).__name__,'message':str(error),'cuda_oom':book.is_cuda_oom(error)})
        traceback.print_exc();code=130 if isinstance(error,KeyboardInterrupt) else 1
    book.atomic_json(request.with_suffix('.result.json'),out)
    return code
