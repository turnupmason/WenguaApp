#!/usr/bin/env python3
"""Regression: existing frozen install may NOT bypass Node path bootstrap."""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "scripts" / "wengua_bigfish_518400_offline_editorial_20261029.py"


def load_batch():
    # The actual Mac local_batch.py is supplied by the user's installed bundle.
    # Only the bootstrap/worker unit contracts are tested here; no fake charts.
    stub = types.ModuleType("local_batch")
    stub.check_install = lambda: {"files": {}}
    # Import-time pinned-source audit key is part of the actual Mac local_batch.
    # This fixture models only its constants; it never casts a fake chart.
    stub.BIGFISH_SHA = "6112b3937d7fcaa2ab0a34aec2a52f74e2effe6c"
    stub.WENGUA_SHA = "0eae7d2b94742939e885938f8603e85c9452d1c3"
    stub.GRADE = {i: str(i) for i in range(-5, 6)}
    stub.COMPILED = ROOT / "build" / "bigfish_compiled_test_fixture"
    with patch.dict(sys.modules, {"local_batch": stub}):
        spec = importlib.util.spec_from_file_location("wengua_518400_node_test", SOURCE)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    return module


class TestMacNodeRuntime(unittest.TestCase):
    def test_already_installed_sources_still_prepare_node_before_fast_path(self):
        module = load_batch()
        events = []
        module.base.check_install = lambda: (events.append("source_check") or {"files": {}})
        with patch.object(module, "_extend_macos_tool_path", side_effect=lambda: events.append("path")), \
             patch.object(module, "ensure_node_available", side_effect=lambda: events.append("node")):
            self.assertEqual(module.ensure_install(), {"files": {}})
        self.assertEqual(events, ["path", "node", "source_check"])

    def test_worker_starts_with_resolved_absolute_executable(self):
        module = load_batch()
        with tempfile.TemporaryDirectory() as d:
            with patch.object(module.shutil, "which", return_value="/opt/homebrew/bin/node"), \
                 patch.object(module.subprocess, "Popen") as popen:
                worker = module.BigFishWorker(Path(d))
                self.assertEqual(popen.call_args.args[0][0], "/opt/homebrew/bin/node")
                worker.error_file.close()

    def test_missing_node_fails_actionably_before_popen(self):
        module = load_batch()
        with tempfile.TemporaryDirectory() as d:
            with patch.object(module.shutil, "which", return_value=None), \
                 patch.object(module.subprocess, "Popen") as popen:
                with self.assertRaisesRegex(RuntimeError, "Node.js"):
                    module.BigFishWorker(Path(d))
                popen.assert_not_called()

    def test_birth_year_not_enabled_by_default(self):
        module = load_batch()
        self.assertIsNone(module.PATIENT_BIRTH_GANZHI)


if __name__ == "__main__":
    unittest.main()
