"""Important/ snapshots must stay byte-identical to active canonical files.

Historical failures and V3.9.1 files remain untouched. Mirrors are not build
inputs; this regression gate prevents them from quietly drifting after edits.
"""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "Important" / "MANIFEST.json"


class ImportantMirrorParity(unittest.TestCase):
    def test_all_selected_important_snapshots_match_canonical_bytes(self):
        catalog = json.loads(MANIFEST.read_text(encoding="utf8"))
        self.assertEqual(catalog["version"], "wengua_important_mirrors_20261026_v1")
        entries = catalog["entries"]
        self.assertGreaterEqual(len(entries), 65)
        self.assertEqual(len(entries), len({e["snapshot"] for e in entries}))
        self.assertIn("python", {e["platform"] for e in entries})
        self.assertIn("swift", {e["platform"] for e in entries})
        for e in entries:
            with self.subTest(snapshot=e["snapshot"]):
                source = ROOT / e["canonical"]
                copied = ROOT / e["snapshot"]
                self.assertTrue(source.is_file(), e["canonical"])
                self.assertTrue(copied.is_file(), e["snapshot"])
                self.assertEqual(copied.read_bytes(), source.read_bytes(),
                                 e["canonical"] + " does not match Important mirror")


if __name__ == "__main__":
    unittest.main()
