import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import run_qwen_overnight as worker


class OvernightReleaseGate(unittest.TestCase):
    def test_pending_release_never_becomes_training_ready(self):
        release = json.loads(worker.RELEASE.read_text())
        if release['state'] == 'preparing':
            self.assertFalse(worker.check_release(release))

    def test_checked_release_requires_actual_source_bytes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            entry = root / 'run_qwen_curriculum.py'; entry.write_text('pass\n')
            release = {'release_id': worker.RELEASE_ID, 'worker_protocol': 1, 'state': 'ready',
                       'checks_passed': True, 'source_sha256': {entry.name: hashlib.sha256(entry.read_bytes()).hexdigest()}}
            with patch.object(worker, 'ROOT', root):
                self.assertTrue(worker.check_release(release))
                entry.write_text('changed\n')
                with self.assertRaisesRegex(ValueError, 'hash mismatch'):
                    worker.check_release(release)

    def test_unchecked_release_and_escaped_source_cannot_run(self):
        with self.assertRaises(ValueError):
            worker.check_release({'release_id': worker.RELEASE_ID, 'worker_protocol': 1,
                                  'state': 'ready', 'checks_passed': False})
        with self.assertRaises(ValueError):
            worker.safe_relative('../outside.py')


if __name__ == '__main__':
    unittest.main()
