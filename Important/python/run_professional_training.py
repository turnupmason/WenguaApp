"""PyCharm: choose the existing project Python 3.11/3.12 interpreter and Run.

Default: logistic CPU + CatBoost GPU, each with five baseline/ablation runs.
Pass --device CPU for a CPU machine; no terminal environment variables.
"""
from pathlib import Path
import os
import sys

if __name__ == '__main__':
    if sys.version_info < (3, 11):
        raise SystemExit('Python 3.11/3.12 required. Select local/probability_env/Scripts/python.exe in PyCharm. Current: ' + sys.executable)
    os.chdir(Path(__file__).resolve().parent)
    from scripts.probability_professional import main
    main()
