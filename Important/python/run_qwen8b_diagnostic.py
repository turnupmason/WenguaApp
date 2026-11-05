"""Resume the existing run3 unchanged; record native worker exits."""
from pathlib import Path
import os,sys

if __name__=='__main__':
    os.chdir(Path(__file__).resolve().parent)
    for stream in (sys.stdout,sys.stderr):
        if hasattr(stream,'reconfigure'):stream.reconfigure(encoding='utf8')
    from scripts.qwen8b_diagnostic import main
    raise SystemExit(main())
