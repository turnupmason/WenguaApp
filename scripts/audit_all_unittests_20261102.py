"""Run every test without skipping/xfail; keep full logs and structured failures."""
import argparse
import contextlib
import gzip
import hashlib
import inspect
import io
import json
from pathlib import Path
import subprocess
import traceback
import unittest

ROOT = Path(__file__).resolve().parents[1]

class AuditResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.records = []

    def record(self, test, error, outcome):
        underlying = getattr(test, 'test_case', test)
        name = getattr(underlying, '_testMethodName', None)
        method = getattr(underlying, name, None) if name else None
        frames = traceback.extract_tb(error[2])
        self.records.append({
            'test_id': test.id(), 'outcome': outcome,
            'exception_type': error[0].__name__, 'message': str(error[1])[:1600],
            'test_source': str(Path(inspect.getsourcefile(method)).relative_to(ROOT)) if method else None,
            'method_source': inspect.getsource(method) if method else None,
            'frames': [{'path': str(Path(f.filename).relative_to(ROOT)) if Path(f.filename).is_relative_to(ROOT) else f.filename,
                        'line': f.lineno, 'code': f.line} for f in frames],
        })

    def addFailure(self, test, err):
        super().addFailure(test, err); self.record(test, err, 'failure')

    def addError(self, test, err):
        super().addError(test, err); self.record(test, err, 'error')

    def addSubTest(self, test, subtest, err):
        super().addSubTest(test, subtest, err)
        if err is not None:
            self.record(subtest, err, 'failure' if issubclass(err[0], test.failureException) else 'error')


def run(destination):
    destination.mkdir(parents=True, exist_ok=False)
    text = io.StringIO()
    with contextlib.redirect_stdout(text), contextlib.redirect_stderr(text):
        suite = unittest.defaultTestLoader.discover(str(ROOT / 'tests'))
        result = unittest.TextTestRunner(stream=text, verbosity=2, resultclass=AuditResult).run(suite)
    raw = text.getvalue().encode()
    doc = {'source_sha': subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip(),
           'worktree_diff_sha256': hashlib.sha256(subprocess.check_output(['git','diff','HEAD','--binary'], cwd=ROOT)).hexdigest(),
           'sealed_manifest_sha256': hashlib.sha256((ROOT/'data/releases/health_frozen_20261102.json').read_bytes()).hexdigest(),
           'tests_run': result.testsRun, 'failures': len(result.failures), 'errors': len(result.errors),
           'skipped': [{'test_id': t.id(), 'reason': reason} for t,reason in result.skipped],
           'full_log_sha256': hashlib.sha256(raw).hexdigest(), 'records': result.records}
    (destination / 'results.json').write_text(json.dumps(doc, ensure_ascii=False, indent=2) + '\n')
    (destination / 'full_unittest.log.gz').write_bytes(gzip.compress(raw, mtime=0))
    print(json.dumps({k:v for k,v in doc.items() if k not in {'records','skipped'}}, ensure_ascii=False))
    return result.wasSuccessful()

if __name__ == '__main__':
    p=argparse.ArgumentParser(); p.add_argument('destination', type=Path)
    raise SystemExit(0 if run(p.parse_args().destination) else 1)
