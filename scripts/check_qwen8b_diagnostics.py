"""Exercise unchanged real tiny training/resume under diagnostic-only I/O."""
import json
from pathlib import Path


def main():
    from src.wengua.qwen8b_book_v1 import hashes
    from src.wengua.qwen8b_diagnostics_v1 import diagnostic_processes
    from scripts.check_qwen8b_training import main as actual_training_check
    before=hashes()
    with diagnostic_processes() as records:actual_training_check()
    assert hashes()==before
    assert len(records)>=6 and all(r['exit_code']==0 and r['receipt_exists'] for r in records)
    assert all(r['request_bytes_unchanged'] and r['stderr_drained'] and r['stderr_error'] is None for r in records)
    report={'state':'passed','test':'diagnostic_io_over_unchanged_tiny_training',
        'actual_worker_count':len(records),'frozen_training_hashes_unchanged':True,'native_stderr_tee_and_sidecars_verified':True,
        'original_checkpoint_restore_and_completed_resume_assertions_passed':True,
        'actual_8b_weights_loaded':False,'user_native_crash_root_cause_verified':False}
    path=Path(__file__).resolve().parents[1]/'local/qwen8b_book_v1/diagnostics_integration.json';path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))


if __name__=='__main__':main()
