"""Windows CMD / PyCharm entry for the checked two-book dialogue curriculum."""
import os
from pathlib import Path
import sys

if __name__ == '__main__':
    if sys.version_info < (3, 11):raise SystemExit('Use local/qwen_env Python 3.12.')
    os.chdir(Path(__file__).resolve().parent)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):stream.reconfigure(encoding='utf8')
    from scripts.qwen_curriculum import main
    main()
