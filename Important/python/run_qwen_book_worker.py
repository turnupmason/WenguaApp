"""Internal fresh-interpreter worker; use the normal research launcher."""
from pathlib import Path
import os,sys

if __name__=='__main__':
    os.chdir(Path(__file__).resolve().parent)
    for stream in (sys.stdout,sys.stderr):
        if hasattr(stream,'reconfigure'):stream.reconfigure(encoding='utf8')
    from src.wengua.qwen_book_process_v1 import worker
    if len(sys.argv)!=2:raise SystemExit('Internal worker requires a request file')
    raise SystemExit(worker(Path(sys.argv[1])))
