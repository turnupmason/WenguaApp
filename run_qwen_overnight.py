"""User-started local waiting/overnight worker. Stdlib; never trains a pending release."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent
RELEASE = ROOT / 'data/knowledge/qwen_curriculum_v2/overnight_release.json'
RELEASE_ID = 'qwen_curriculum_v2_20261103'


def safe_relative(name):
    path = (ROOT / name).resolve()
    if not path.is_relative_to(ROOT) or not isinstance(name, str):
        raise ValueError('Release path must stay inside the project')
    return path


def check_release(release):
    if release.get('release_id') != RELEASE_ID or release.get('worker_protocol') != 1:
        raise ValueError('Unexpected release identity/protocol')
    if release.get('state') == 'preparing':
        return False
    if release.get('state') != 'ready' or not release.get('checks_passed'):
        raise ValueError('Release is not checked and ready')
    proof=release.get('checks',{})
    if release.get('dataset_basis')!='full_readonly_source_archive_reconstruction' or release.get('candidate_11952_used') is not False:
        raise ValueError('Index-only candidate data cannot authorize this training release')
    required=('literal_source_audit','group_holdout_audit','official_token_budget_audit','tiny_checkpoint_resume_test')
    if any(proof.get(key) is not True for key in required):
        raise ValueError('Missing full-source or executable training checks')
    fingerprints = release.get('source_sha256', {})
    if 'run_qwen_curriculum.py' not in fingerprints:
        raise ValueError('Missing checked curriculum entrypoint')
    for name, sha in fingerprints.items():
        if hashlib.sha256(safe_relative(name).read_bytes()).hexdigest() != sha:
            raise ValueError('Release source hash mismatch: ' + name)
    for name,sha in release.get('canonical_text_sha256',{}).items():
        raw=safe_relative(name).read_bytes();raw.decode('utf8')
        if hashlib.sha256(raw.replace(b'\r\n',b'\n')).hexdigest()!=sha:
            raise ValueError('Release canonical text hash mismatch: '+name)
    for name,sha in release.get('binary_source_sha256',{}).items():
        if hashlib.sha256(safe_relative(name).read_bytes()).hexdigest()!=sha:
            raise ValueError('Release binary source hash mismatch: '+name)
    return True


def update_repo():
    for command in (['git', 'diff', '--quiet'], ['git', 'diff', '--cached', '--quiet']):
        if subprocess.run(command, cwd=ROOT, check=False).returncode:
            raise RuntimeError('Tracked local edits found; preserved. Commit/stash them before updating; no reset was run.')
    subprocess.run(['git', 'pull', '--ff-only', 'origin', 'main'], cwd=ROOT, check=True)


def prevent_sleep(enabled):
    if os.name == 'nt':
        import ctypes
        flags = 0x80000000 | (0x00000001 if enabled else 0)
        ctypes.windll.kernel32.SetThreadExecutionState(flags)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--hours', type=float, default=15)
    parser.add_argument('--poll-seconds', type=float, default=60)
    parser.add_argument('--check-only', action='store_true')
    args = parser.parse_args(argv)
    if not 0 < args.hours <= 24 or not 10 <= args.poll_seconds <= 300:
        raise SystemExit('hours must be (0,24], polling must be 10..300 seconds')
    if sys.version_info < (3, 11):
        raise SystemExit('Use the existing local/qwen_env Python 3.12 interpreter.')
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf8')
    os.chdir(ROOT)
    started = time.time()
    deadline = started + args.hours * 3600
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    output = ROOT / 'local/qwen_curriculum_v2' / ('overnight_' + stamp)
    output.mkdir(parents=True, exist_ok=False)
    status_path = output / 'worker_status.json'

    def status(state, **extra):
        value = {'state': state, 'release_id': RELEASE_ID, 'deadline_utc_epoch': deadline,
                 'output': str(output), **extra}
        status_path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
        print(json.dumps(value, ensure_ascii=False), flush=True)

    process = None
    prevent_sleep(True)
    try:
        status('waiting_for_checked_data_release', training_started=False)
        while time.time() < deadline:
            if not args.check_only:
                try:
                    update_repo()
                except subprocess.CalledProcessError as error:
                    status('waiting_network_or_fast_forward', training_started=False, error=str(error))
                    time.sleep(min(args.poll_seconds, max(0, deadline - time.time())))
                    continue
            release = json.loads(RELEASE.read_text(encoding='utf8')) if RELEASE.exists() else {}
            ready = check_release(release) if release else False
            if args.check_only:
                status('release_ready' if ready else 'waiting_for_checked_data_release', training_started=False)
                return
            if not ready:
                time.sleep(min(args.poll_seconds, max(0, deadline - time.time())))
                continue
            command = [sys.executable, str(ROOT / 'run_qwen_curriculum.py'), 'run',
                       '--output', str(output / 'job'), '--deadline-utc-epoch', str(deadline)]
            status('running_checked_curriculum', training_started=True)
            with (output / 'job_console.log').open('w', encoding='utf8') as log:
                process = subprocess.Popen(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
                while process.poll() is None and time.time() < deadline:
                    time.sleep(min(5, max(0, deadline - time.time())))
                if process.poll() is None:
                    process.terminate()
                    try:
                        process.wait(timeout=30)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait()
                    status('deadline_reached', training_started=True, returncode=process.returncode)
                    return
            status('job_complete' if process.returncode == 0 else 'job_failed',
                   training_started=True, returncode=process.returncode,
                   console_log=str(output / 'job_console.log'))
            return
        status('deadline_reached_before_release', training_started=False)
    except Exception as error:
        status('failed_preserving_outputs', error=str(error), training_started=process is not None)
        raise
    finally:
        if process is not None and process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
        prevent_sleep(False)


if __name__ == '__main__':
    main()
