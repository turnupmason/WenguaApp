"""Restore byte-identical historical SQLite sources from tracked .xz copies.

The current two-book source remains expanded in Git. Historical regression
fixtures opt in explicitly; no import hook or background extraction is used.
"""
import hashlib
import json
import lzma
import os
from pathlib import Path
import tempfile

ROOT=Path(__file__).resolve().parents[2]/'archives/sqlite'
CATALOG=ROOT/'source_archive_catalog.json'
_fixture_batch_ready=False


def digest(raw):return hashlib.sha256(raw).hexdigest()


def restore(entry,root):
    root=Path(root);name=entry['name'];compressed=entry['compressed']
    if Path(name).name!=name or Path(compressed).name!=compressed:raise ValueError('Unsafe archive name')
    path=root/name
    def verify():
        if path.stat().st_size!=entry['bytes'] or digest(path.read_bytes())!=entry['sha256']:
            raise ValueError('Existing source differs; preserved: '+name)
        return path
    if path.exists():return verify()
    payload=(root/compressed).read_bytes()
    if digest(payload)!=entry['compressed_sha256']:raise ValueError('Compressed source checksum mismatch: '+name)
    raw=lzma.decompress(payload)
    if len(raw)!=entry['bytes'] or digest(raw)!=entry['sha256']:raise ValueError('Restored source checksum mismatch: '+name)
    pending=None
    try:
        with tempfile.NamedTemporaryFile(dir=root,prefix=name+'.',suffix='.pending',delete=False) as f:
            pending=Path(f.name);f.write(raw);f.flush();os.fsync(f.fileno())
        try:os.link(pending,path)
        except FileExistsError:pass
        return verify()
    finally:
        if pending is not None:pending.unlink(missing_ok=True)


def source_database(path):
    path=Path(path)
    if path.parent==Path('.'):path=ROOT/path
    if path.resolve().parent!=ROOT.resolve():raise ValueError('Not a catalogued source archive path')
    entries=json.loads(CATALOG.read_text(encoding='utf8'))['entries']
    entry=next((e for e in entries if e['name']==path.name),None)
    if entry is None:raise ValueError('Source not in archive catalogue: '+path.name)
    return restore(entry,ROOT)


def restore_historical_inputs():
    """Explicit once-per-test-process precondition for the full legacy cohort.

    Those regression runners use frozen default paths inside old modules, so
    restoring only the path imported by a test does not restore every parent.
    No production module calls this, and it never runs just by importing us.
    """
    global _fixture_batch_ready
    if _fixture_batch_ready:return
    for entry in json.loads(CATALOG.read_text(encoding='utf8'))['entries']:
        restore(entry,ROOT)
    _fixture_batch_ready=True
