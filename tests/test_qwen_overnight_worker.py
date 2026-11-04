import hashlib
import json
import tempfile
import subprocess
import unittest
from pathlib import Path
from unittest.mock import patch

import run_qwen_overnight as worker


class OvernightReleaseGate(unittest.TestCase):
    def test_pending_release_never_becomes_training_ready(self):
        self.assertFalse(worker.check_release({'release_id':worker.RELEASE_ID,'worker_protocol':1,'state':'preparing'}))

    def test_checked_release_requires_actual_source_bytes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            entry = root / 'run_qwen_curriculum.py'; entry.write_text('pass\n')
            release = {'release_id': worker.RELEASE_ID, 'worker_protocol': 1, 'state': 'ready',
                       'checks_passed': True, 'dataset_basis':'full_readonly_source_archive_reconstruction',
                       'candidate_11952_used':False,'checks':{k:True for k in (
                           'literal_source_audit','group_holdout_audit','official_token_budget_audit','tiny_checkpoint_resume_test')},
                       'source_sha256': {entry.name: hashlib.sha256(entry.read_bytes()).hexdigest()}}
            with patch.object(worker, 'ROOT', root):
                self.assertTrue(worker.check_release(release))
                entry.write_text('changed\n')
                with self.assertRaisesRegex(ValueError, 'hash mismatch'):
                    worker.check_release(release)

    def test_windows_crlf_is_equivalent_only_for_declared_utf8_text(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);(root/'run_qwen_curriculum.py').write_bytes(b'pass\n')
            text=root/'module.py';text.write_bytes(b'pass\r\n')
            release={'release_id':worker.RELEASE_ID,'worker_protocol':1,'state':'ready','checks_passed':True,
                'dataset_basis':'full_readonly_source_archive_reconstruction','candidate_11952_used':False,
                'checks':{k:True for k in ('literal_source_audit','group_holdout_audit','official_token_budget_audit','tiny_checkpoint_resume_test')},
                'source_sha256':{'run_qwen_curriculum.py':hashlib.sha256(b'pass\n').hexdigest()},
                'canonical_text_sha256':{'module.py':hashlib.sha256(b'pass\n').hexdigest()}}
            with patch.object(worker,'ROOT',root):
                self.assertTrue(worker.check_release(release))
                text.write_bytes(b'changed\r\n')
                with self.assertRaisesRegex(ValueError,'canonical text hash mismatch'):worker.check_release(release)

    def test_existing_crlf_checkout_pulls_bootstrap_as_lf(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);up=root/'up';up.mkdir();checkout=root/'checkout'
            def git(cwd,*args):
                return subprocess.run(['git',*args],cwd=cwd,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            git(up,'init');git(up,'config','core.autocrlf','false')
            git(up,'config','user.name','Local fixture');git(up,'config','user.email','fixture@example.invalid')
            (up/'run_qwen_curriculum.py').write_bytes(b'pass\n')
            git(up,'add','.');git(up,'commit','-m','Initial fixture')
            git(root,'-c','core.autocrlf=true','clone',str(up),str(checkout))
            self.assertEqual((checkout/'run_qwen_curriculum.py').read_bytes(),b'pass\r\n')
            (up/'.gitattributes').write_bytes(b'/run_qwen_curriculum.py text eol=lf\n')
            (up/'run_qwen_curriculum.py').write_bytes(b'pass # checked bootstrap\n')
            git(up,'add','.');git(up,'commit','-m','Stable LF bootstrap fixture')
            git(checkout,'-c','core.autocrlf=true','pull','--ff-only')
            self.assertEqual((checkout/'run_qwen_curriculum.py').read_bytes(),b'pass # checked bootstrap\n')

    def test_unchecked_release_and_escaped_source_cannot_run(self):
        with self.assertRaises(ValueError):
            worker.check_release({'release_id': worker.RELEASE_ID, 'worker_protocol': 1,
                                  'state': 'ready', 'checks_passed': False})
        with self.assertRaises(ValueError):
            worker.safe_relative('../outside.py')


if __name__ == '__main__':
    unittest.main()
