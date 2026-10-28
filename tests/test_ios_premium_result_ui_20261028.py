"""UI-only guard: no replacement of V8 parity-checked customer reading."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UI = ROOT / "ios/WenguaAppUI"

class PremiumResultSourceContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.chart = (UI / "WenguaDesignPreviewApp.swift").read_text()
        cls.presentation = (UI / "WenguaPremiumReadingView.swift").read_text()
        cls.template = json.loads((ROOT / "data/templates/health_severity_vnext/reading_template.json").read_text())

    def test_native_truth_is_the_only_summary_source(self):
        self.assertIn('id == "90_review"', self.presentation)
        self.assertIn('id == "91_timing"', self.presentation)
        self.assertIn('WenguaVerdictPresentation.from(reading)', self.presentation)
        self.assertIn('{evidence}', self.template["macros"]["verdict"])
        self.assertIn('{conclusion}', self.template["macros"]["verdict"])
        self.assertIn("综上所述，此病为{grade}。", self.template["macros"]["overall_resolved"])
        self.assertNotIn("review.score", self.presentation)
        self.assertNotIn("compute(", self.presentation)

    def test_real_corner_markers(self):
        self.assertIn('if !QFive.void(palace).isEmpty', self.chart)
        self.assertIn('Circle()', self.chart)
        self.assertIn('if let horse=QFive.horse(palace)', self.chart)
        self.assertIn('Text("🐎")', self.chart)
        self.assertIn('if let c=p.computed { return c.voidBranches }', self.chart)
        self.assertIn('if let c=p.computed { return c.horseBranch }', self.chart)
        self.assertIn('if palace.id == 5', self.chart)

    def test_two_tabs_and_history(self):
        self.assertIn('WenguaReadingTabStrip(selection:$selectedReadingTab)', self.chart)
        self.assertIn('WenguaReadingTabStrip(selection:$selectedTab)', self.chart)
        self.assertIn('WenguaPremiumVerdictCard(reading:reading)', self.chart)
        self.assertIn('WenguaNativeCustomerView(reading:reading)', self.chart)
        self.assertIn('NativePalaceEvidenceCard(palace:palace)', self.chart)
        self.assertIn('["接卦", "专业解盘"]', self.presentation)
        self.assertIn('WenguaPremiumReadingView.swift', (UI / "project.yml").read_text())
        self.assertIn('try WenguaNativeReadingRouter.compose(', self.chart)

if __name__ == "__main__":
    unittest.main()
