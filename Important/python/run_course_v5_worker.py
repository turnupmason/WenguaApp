"""Internal reviewed-course isolated worker."""
from pathlib import Path
import faulthandler
import os
import sys

if __name__=='__main__':
    os.chdir(Path(__file__).resolve().parent)
    for stream in (sys.stdout,sys.stderr):
        if hasattr(stream,'reconfigure'):stream.reconfigure(encoding='utf8')
    faulthandler.enable(all_threads=True)
    from src.wengua.course_process_v5 import worker
    if len(sys.argv)!=2:raise SystemExit('Internal worker request required')
    raise SystemExit(worker(Path(sys.argv[1])))
