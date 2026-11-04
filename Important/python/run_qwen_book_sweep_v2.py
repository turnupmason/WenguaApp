"""Windows CMD / PyCharm continuous QLoRA staged research entry."""
from pathlib import Path
import os,sys

if __name__=='__main__':
    if sys.version_info<(3,11):raise SystemExit('Use local/qwen_env Python 3.12.')
    os.chdir(Path(__file__).resolve().parent)
    for stream in (sys.stdout,sys.stderr):
        if hasattr(stream,'reconfigure'):stream.reconfigure(encoding='utf8')
    from scripts.qwen_book_sweep_v2 import main
    main()
