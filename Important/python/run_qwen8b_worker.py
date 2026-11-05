"""Internal 8B worker; launch run_qwen8b_research.py instead."""
from pathlib import Path
import os,sys

if __name__=='__main__':
    os.chdir(Path(__file__).resolve().parent)
    for stream in (sys.stdout,sys.stderr):
        if hasattr(stream,'reconfigure'):stream.reconfigure(encoding='utf8')
    from src.wengua.qwen8b_process_v1 import worker
    if len(sys.argv)!=2:raise SystemExit('Internal 8B request file required')
    raise SystemExit(worker(Path(sys.argv[1])))
