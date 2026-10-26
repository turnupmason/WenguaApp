"""App Store binary uses only source-indexed rules, not book SQLite."""
import json
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class NativeVNextAppContract(unittest.TestCase):
    def test_source_index_and_roles(self):
        actors=json.loads((ROOT/"data/knowledge/phrase_library/health_v20/actor_profiles.json").read_text("utf8"))
        self.assertEqual(len(actors["profiles"]),20)
        self.assertTrue(all(a["references"] for a in actors["profiles"]))
        binder=(ROOT/"ios/WenguaAppUI/WenguaNativeActorBinding.swift").read_text("utf8")
        self.assertIn("eligibleForFirmTraditionalJudgment",binder)
        self.assertIn("event_news",binder)
    def test_main_is_not_frozen_v391_and_book_sqlite_is_not_bundled(self):
        self.assertTrue((ROOT/"ios/WenguaAppUI/FrozenReadingV391.json").is_file())
        proj=(ROOT/"ios/WenguaAppUI/project.yml").read_text("utf8")
        main=(ROOT/"ios/WenguaAppUI/WenguaDesignPreviewApp.swift").read_text("utf8")
        self.assertNotIn("FrozenReadingV391.json",proj)
        self.assertNotIn("FrozenPreview",main)
        self.assertIn("WenguaVNextInlineReading",main)
        self.assertIn("WenguaNativeReadingRouter.compose(",main)
        self.assertIn("actor_profiles.json",proj)
        self.assertNotIn(".sqlite",proj)
        self.assertNotIn("/archives/",proj)
    def test_customer_excludes_scoring(self):
        comp=(ROOT/"ios/WenguaAppUI/WenguaVNextCustomerComposer.swift").read_text("utf8")
        reasoner=(ROOT/"ios/WenguaAppUI/WenguaVNextReasoner.swift").read_text("utf8")
        engine=(ROOT/"ios/WenguaAppUI/WenguaNativeVNextEngine.swift").read_text("utf8")
        self.assertIn("WenguaVNextReasoner.build(",comp)
        self.assertIn('audit.roleStatus != "eligible"',reasoner)
        self.assertIn("energyEvidence",engine)
        self.assertIn("roleEnergy",engine)
        self.assertIn("factorLine",reasoner)
        self.assertIn("reason_verdict_conflict",reasoner)
        self.assertNotIn("postVoidKnownSum",reasoner)
        self.assertNotIn("postVoidKnownSum",comp)
if __name__=="__main__":unittest.main()
