import io
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

from src.wengua.qwen8b_diagnostics_v1 import diagnostic_processes,exit_summary


class WorkerDiagnostics(unittest.TestCase):
    def setup_worker(self,root,code):
        worker=root/'run_qwen8b_worker.py';worker.write_text(code,encoding='utf8')
        calls=root/'worker_calls';calls.mkdir();request=calls/'request.json';request.write_text('{"nonce":"fixture"}',encoding='utf8')
        return [sys.executable,'-X','utf8',str(worker),str(request)],request

    def test_abrupt_exit_without_python_receipt_has_live_stderr_and_exit_code(self):
        with TemporaryDirectory() as tmp:
            command,request=self.setup_worker(Path(tmp),"import os,sys,json,pathlib\nos.write(2,b'native-exit-marker\\n')\nassert os.environ['PYTHONFAULTHANDLER']=='1'\npathlib.Path(sys.argv[1]).with_suffix('.heartbeat.json').write_text(json.dumps({'pid':os.getpid(),'phase':'train','step':3}))\nos._exit(7)\n")
            original=request.read_bytes();mirror=io.StringIO()
            with diagnostic_processes(mirror=mirror) as records:
                child=subprocess.Popen(command);self.assertEqual(child.wait(),7)
            self.assertEqual(request.read_bytes(),original);self.assertEqual(len(records),1)
            self.assertFalse(records[0]['receipt_exists']);self.assertEqual(records[0]['exit_code_hex32'],'0x00000007')
            self.assertTrue(records[0]['request_bytes_unchanged']);self.assertTrue(records[0]['stderr_drained'])
            self.assertEqual(records[0]['last_heartbeat_step'],3)
            self.assertEqual(records[0]['worker_pid'],json.loads(request.with_suffix('.heartbeat.json').read_text())['pid'])
            self.assertIn('native-exit-marker',mirror.getvalue())
            self.assertIn('native-exit-marker',request.with_suffix('.native_stderr.log').read_text())
            self.assertEqual(json.loads(request.with_suffix('.exit_diagnostic.json').read_text())['exit_code'],7)

    def test_normal_worker_receipt_and_repeated_wait_are_preserved(self):
        with TemporaryDirectory() as tmp:
            command,request=self.setup_worker(Path(tmp),"import os,sys,pathlib,json\nos.write(2,b'partial-progress\\r')\npathlib.Path(sys.argv[1]).with_suffix('.result.json').write_text(json.dumps({'pid':os.getpid()}))\n")
            with diagnostic_processes(mirror=io.StringIO()) as records:
                child=subprocess.Popen(command);self.assertEqual(child.wait(),0);self.assertEqual(child.wait(),0)
            self.assertEqual(len(records),1);self.assertTrue(records[0]['receipt_exists'])
            self.assertFalse(records[0]['automatic_retry']);self.assertIsNone(records[0]['stderr_error'])

    def test_unrelated_process_pipe_and_environment_are_not_changed(self):
        with diagnostic_processes(mirror=io.StringIO()) as records:
            result=subprocess.run([sys.executable,'-c',"import sys;sys.stdout.write('ordinary');sys.stderr.write('normal-error')"],capture_output=True,text=True)
        self.assertEqual(result.stdout,'ordinary');self.assertEqual(result.stderr,'normal-error');self.assertEqual(records,[])

    def test_timeout_is_not_misreported_as_a_finished_worker(self):
        with TemporaryDirectory() as tmp:
            command,request=self.setup_worker(Path(tmp),"import time\ntime.sleep(2)\n")
            with diagnostic_processes(mirror=io.StringIO()) as records:
                child=subprocess.Popen(command)
                with self.assertRaises(subprocess.TimeoutExpired):child.wait(timeout=0.01)
                self.assertFalse(request.with_suffix('.exit_diagnostic.json').exists())
                child.terminate();child.wait()
            self.assertEqual(len(records),1);self.assertFalse(records[0]['receipt_exists'])

    def test_windows_status_and_posix_signal_are_distinct_from_cuda_oom(self):
        self.assertEqual(exit_summary(-1073741819,'nt')['windows_status_hint'],'access_violation')
        self.assertEqual(exit_summary(3221225477,'nt')['exit_code_hex32'],'0xC0000005')
        self.assertEqual(exit_summary(-9,'posix')['posix_signal'],9)
        self.assertIsNone(exit_summary(7,'nt')['windows_status_hint'])


if __name__=='__main__':unittest.main()
