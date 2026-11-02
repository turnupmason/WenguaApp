"""Sealed release provenance, runtime wrong-version rejection and bundle allowlist."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from scripts.verify_frozen_health_release_20261102 import verify, ROOT, MANIFEST
from src.wengua.health_discomfort_v19_parity import compose, load_sources
from tests.test_health_discomfort_injury_gate_20261102 import live_board

class FrozenHealthRelease(unittest.TestCase):
    def test_production_source_and_retired_hashes(self):
        verify()

    def test_exact_bundle_and_injected_old_template_rejection(self):
        release = verify()
        with tempfile.TemporaryDirectory() as tmp:
            bundle = Path(tmp)
            for item in release['files']:
                if item['kind'] == 'resource':
                    source = ROOT / item['path']
                    (bundle / source.name).write_bytes(source.read_bytes())
            (bundle / MANIFEST.name).write_bytes(MANIFEST.read_bytes())
            verify(bundle)
            (bundle / 'FrozenReadingV391.json').write_text('{}')
            with self.assertRaises(AssertionError):
                verify(bundle)

    def test_v27_rejects_unsealed_or_old_schema(self):
        chart, actor = live_board('2026-11-19T11:00:00-05:00')
        for key, value in [('schema','old_v26'), ('release_status','draft')]:
            sources = list(copy.deepcopy(load_sources()))
            sources[2][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                compose(chart, actor, '哥哥', 'none', sources)
