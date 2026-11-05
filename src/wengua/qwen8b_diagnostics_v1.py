"""Sidecar-only worker stderr/exit diagnostics; frozen training files unchanged."""
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import time
import uuid
from unittest.mock import patch


def exit_summary(code,platform=None):
    platform=platform or os.name;unsigned=int(code)&0xffffffff
    names={0xc0000005:'access_violation',0xc0000017:'no_memory_status',0xc000009a:'insufficient_resources',
        0xc00000fd:'stack_overflow',0xc000013a:'control_c_exit',0xc0000374:'heap_corruption',0xc0000409:'fast_fail'}
    return {'exit_code':int(code),'exit_code_hex32':f'0x{unsigned:08X}','platform':platform,
        'windows_status_hint':names.get(unsigned) if platform=='nt' else None,
        'posix_signal':-int(code) if platform!='nt' and code<0 else None}


def worker_request(command):
    if not isinstance(command,(list,tuple)) or len(command)<3:return None
    if not any(Path(str(arg)).name=='run_qwen8b_worker.py' for arg in command):return None
    path=Path(command[-1]).resolve()
    return path if path.suffix=='.json' and path.parent.name=='worker_calls' and path.is_file() else None


def atomic(path,data):
    tmp=path.with_name(path.name+'.tmp-'+uuid.uuid4().hex)
    tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');os.replace(tmp,path)


@contextmanager
def diagnostic_processes(*,mirror=None):
    """Tee only actual 8B worker pipes; preserve args, polling and return codes.

    No retry, backend switch, checkpoint edits, CUDA calls or tensor operations.
    The child receives only fault-handler/unbuffered I/O environment additions.
    """
    original=subprocess.Popen;mirror=sys.stderr if mirror is None else mirror;records=[]
    wrapper_sha=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    class DiagnosticPopen(original):
        def __init__(self,args,*positional,**kwargs):
            self.diag_request=worker_request(args);self.diag_thread=None;self.diag_saved=False;self.diag_failure=None
            if self.diag_request is None:
                super().__init__(args,*positional,**kwargs);return
            if positional or kwargs.get('stderr') is not None or kwargs.get('text') or kwargs.get('encoding'):
                raise ValueError('8B diagnostic tee requires the existing binary worker pipe contract')
            self.diag_started=time.time();self.diag_digest=hashlib.sha256(self.diag_request.read_bytes()).hexdigest()
            self.diag_log=self.diag_request.with_suffix('.native_stderr.log')
            env=dict(os.environ if kwargs.get('env') is None else kwargs['env']);env.update(PYTHONFAULTHANDLER='1',PYTHONUNBUFFERED='1')
            kwargs.update(env=env,stderr=subprocess.PIPE)
            super().__init__(args,*positional,**kwargs)
            self.diag_thread=threading.Thread(target=self.drain_stderr,daemon=True);self.diag_thread.start()

        def drain_stderr(self):
            try:
                with self.diag_log.open('wb') as log:
                    while True:
                        chunk=self.stderr.read1(4096)
                        if not chunk:break
                        log.write(chunk);log.flush()
                        try:
                            if hasattr(mirror,'buffer'):mirror.buffer.write(chunk);mirror.buffer.flush()
                            else:mirror.write(chunk.decode('utf8',errors='replace'));mirror.flush()
                        except (OSError,ValueError):pass
            except Exception as error:self.diag_failure=type(error).__name__+': '+str(error)
            finally:self.stderr.close()

        def wait(self,*args,**kwargs):
            code=super().wait(*args,**kwargs)
            if self.diag_request is not None and not self.diag_saved:
                if self.diag_thread is not None:self.diag_thread.join(timeout=5)
                reply=self.diag_request.with_suffix('.result.json')
                heartbeat={};heart=self.diag_request.with_suffix('.heartbeat.json')
                if heart.exists():
                    try:heartbeat=json.loads(heart.read_text(encoding='utf8'))
                    except (ValueError,OSError):pass
                row={'schema':'wengua_qwen8b_exit_diagnostic_v1',**exit_summary(code),
                    'launcher_pid':self.pid,'request_sha256':self.diag_digest,
                    'worker_pid':heartbeat.get('pid'),'last_heartbeat_phase':heartbeat.get('phase'),
                    'last_heartbeat_step':heartbeat.get('step'),
                    'request_bytes_unchanged':hashlib.sha256(self.diag_request.read_bytes()).hexdigest()==self.diag_digest,
                    'receipt_exists':reply.exists(),'stderr_path':str(self.diag_log),
                    'stderr_drained':self.diag_thread is not None and not self.diag_thread.is_alive(),
                    'stderr_error':self.diag_failure,'fault_handler_enabled':True,
                    'elapsed_seconds':time.time()-self.diag_started,'diagnostic_wrapper_sha256':wrapper_sha,
                    'training_behavior_changed':False,'automatic_retry':False}
                atomic(self.diag_request.with_suffix('.exit_diagnostic.json'),row)
                records.append(row);self.diag_saved=True
                print('[qwen8b_exit_diagnostic] '+json.dumps(row,ensure_ascii=False),flush=True)
            return code
    with patch.object(subprocess,'Popen',DiagnosticPopen):yield records
