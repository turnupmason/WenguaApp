"""Restore the encrypted reviewed dataset on Windows; no model is loaded."""
from pathlib import Path
import os
import sys

if __name__=='__main__':
    os.chdir(Path(__file__).resolve().parent)
    for stream in (sys.stdout,sys.stderr):
        if hasattr(stream,'reconfigure'):stream.reconfigure(encoding='utf8')
    from src.wengua.course_delivery_v1 import main
    raise SystemExit(main())
