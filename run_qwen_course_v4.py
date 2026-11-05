"""Reviewed course entry point; independent of the paused legacy launcher."""
from pathlib import Path
import os
import sys

if __name__=='__main__':
    os.chdir(Path(__file__).resolve().parent)
    for stream in (sys.stdout,sys.stderr):
        if hasattr(stream,'reconfigure'):stream.reconfigure(encoding='utf8')
    from scripts.qwen_course_v4 import main
    raise SystemExit(main())
