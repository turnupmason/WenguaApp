"""Run the unchanged 8B CLI with native-error sidecars and live stderr."""
import faulthandler

from src.wengua.qwen8b_diagnostics_v1 import diagnostic_processes


def main(argv=None):
    from scripts.qwen8b_research import main as training_main
    faulthandler.enable(all_threads=True)
    with diagnostic_processes():return training_main(argv)


if __name__=='__main__':raise SystemExit(main())
