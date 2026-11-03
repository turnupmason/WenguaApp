"""PyCharm/terminal entry. Defaults to preparing private data, never downloads 32B."""
import os
from pathlib import Path
import sys

if __name__ == '__main__':
    if sys.version_info < (3, 11):
        raise SystemExit('Select Python 3.11 or 3.12.')
    os.chdir(Path(__file__).resolve().parent)
    from scripts.qwen_research import main
    main()
