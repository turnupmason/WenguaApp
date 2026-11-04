"""Candidate-only instruction workbook manifest; no source-book content or GPU training."""
import hashlib
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANON = ROOT / "data/knowledge/qwen_curriculum_v2/candidate_11952_manifest.json"
MIRROR = ROOT / "Important/python/data/knowledge/qwen_curriculum_v2/candidate_11952_manifest.json"
RELEASE = ROOT / "data/knowledge/qwen_curriculum_v2/overnight_release.json"


class QwenDialogueCandidateV1Tests(unittest.TestCase):
    def test_important_mirror_identical_and_registered(self):
        self.assertEqual(CANON.read_bytes(), MIRROR.read_bytes())
        data = json.loads((ROOT / "Important/MANIFEST.json").read_text(encoding="utf8"))
        entries = [x for x in data["entries"] if x["canonical"] == str(CANON.relative_to(ROOT))]
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["snapshot"], str(MIRROR.relative_to(ROOT)))

    def test_counts_and_source_groups(self):
        d = json.loads(CANON.read_text(encoding="utf8"))
        n = d["data_counts"]
        self.assertEqual(n["rows"], 11952)
        self.assertEqual(sum((n["questions_basic"], n["questions_conditional"],
                              n["palace_relations"], n["case_index_replays"])), n["rows"])
        self.assertEqual(sum(n["review_status_counts"].values()), n["rows"])
        self.assertEqual(sum(n["group_split_source_units"].values()), n["source_units"])
        self.assertEqual(n["case_index_replays"], 792)
        self.assertEqual(n["case_event_families_unique"], 65)
        self.assertGreater(n["multi_turn"], 0)
        for artifact in d["outputs"].values():
            self.assertRegex(artifact["sha256"], r"^[0-9a-f]{64}$")
            self.assertTrue(artifact["shared_in_conversation_only"])

    def test_not_gold_and_release_gate_still_closed(self):
        d = json.loads(CANON.read_text(encoding="utf8"))
        p = d["training_policy"]
        self.assertTrue(p["all_rows_candidate_not_gold"])
        self.assertEqual(p["trainable_gold_rows_approved_in_this_delivery"], 0)
        self.assertTrue(p["case_index_replays_are_not_actual_author_analysis"])
        self.assertFalse(p["auto_train_enabled"])
        release = json.loads(RELEASE.read_text(encoding="utf8"))
        self.assertEqual(release["state"], "preparing")
        self.assertFalse(release["checks_passed"])


if __name__ == "__main__":
    unittest.main()
