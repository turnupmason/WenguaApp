"""Independent RAG entry; never edits the active training configuration."""
import os,sys
from pathlib import Path
if __name__=='__main__':
    os.chdir(Path(__file__).resolve().parent)
    for stream in (sys.stdout,sys.stderr):
        if hasattr(stream,'reconfigure'):stream.reconfigure(encoding='utf8')
    from scripts.wengua_rag import main
    raise SystemExit(main())
