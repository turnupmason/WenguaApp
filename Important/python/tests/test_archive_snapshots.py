"""Lossless restoration and preservation of existing, possibly changed sources."""
import hashlib
import lzma
from pathlib import Path
import tempfile
import unittest
from src.wengua.archive_snapshots import restore,source_database


class SnapshotRestoration(unittest.TestCase):
    def entry(self,root):
        raw=b'SQLite format 3\0'+bytes(range(256))*32
        payload=lzma.compress(raw);(root/'fixture.sqlite3.xz').write_bytes(payload)
        return raw,{'name':'fixture.sqlite3','bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),
            'compressed':'fixture.sqlite3.xz','compressed_sha256':hashlib.sha256(payload).hexdigest()}

    def test_byte_exact_restore_reuse_and_no_pending_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);raw,entry=self.entry(root)
            path=restore(entry,root);self.assertEqual(path.read_bytes(),raw)
            self.assertEqual(restore(entry,root),path)
            self.assertFalse(list(root.glob('*.pending')))

    def test_changed_existing_source_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);raw,entry=self.entry(root);path=root/entry['name'];path.write_bytes(b'changed user source')
            with self.assertRaisesRegex(ValueError,'preserved'):restore(entry,root)
            self.assertEqual(path.read_bytes(),b'changed user source')

    def test_compressed_tampering_and_wrong_raw_hash_never_install(self):
        for change in ('compressed','raw_hash'):
            with self.subTest(change=change),tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp);_,entry=self.entry(root)
                if change=='compressed':(root/entry['compressed']).write_bytes(b'corrupted')
                else:entry['sha256']='0'*64
                with self.assertRaisesRegex(ValueError,'checksum'):restore(entry,root)
                self.assertFalse((root/entry['name']).exists())

    def test_uncatalogued_or_outside_path_not_created(self):
        with self.assertRaises(ValueError):source_database('not_catalogued.sqlite3')
        with self.assertRaises(ValueError):source_database('/tmp/fixture.sqlite3')

if __name__=='__main__':unittest.main()
