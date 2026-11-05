"""Windows/PyCharm 8B entry; leaves all 14B experiments untouched."""
from pathlib import Path
import os,sys

if __name__=='__main__':
    if sys.version_info<(3,11):raise SystemExit('Use the existing local/qwen_env Python 3.12.')
    os.chdir(Path(__file__).resolve().parent)
    for stream in (sys.stdout,sys.stderr):
        if hasattr(stream,'reconfigure'):stream.reconfigure(encoding='utf8')
    from scripts.qwen8b_research import main
    raise SystemExit(main())
