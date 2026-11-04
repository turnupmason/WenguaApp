"""Windows CMD/PyCharm entry for the new, book-only, fresh-base loop."""
from pathlib import Path
import os,sys

if __name__=='__main__':
    if sys.version_info<(3,11):raise SystemExit('Use the established local/qwen_env Python 3.12 environment.')
    os.chdir(Path(__file__).resolve().parent)
    for stream in (sys.stdout,sys.stderr):
        if hasattr(stream,'reconfigure'):stream.reconfigure(encoding='utf8')
    from scripts.qwen_book_loop import main
    main()
