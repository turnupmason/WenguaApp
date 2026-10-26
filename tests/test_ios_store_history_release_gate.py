"""Local-first review capability contract, score privacy and no fake records."""
import unittest
from pathlib import Path
root=Path(__file__).resolve().parents[1]
class LocalHistoryAndPrivacy(unittest.TestCase):
    def test_history_and_user_initiated_full_delete(self):
        ui=(root/"ios/WenguaAppUI/WenguaDesignPreviewApp.swift").read_text()
        history=(root/"ios/WenguaAppUI/WenguaLocalHistoryView.swift").read_text()
        project=(root/"ios/WenguaAppUI/project.yml").read_text()
        self.assertIn("NavigationLink {\n                            WenguaLocalHistoryView()",ui)
        self.assertIn("WenguaNativeReadingRouter.compose",ui)
        self.assertIn("reading:reading",ui)
        self.assertIn('recordPrefix="wengua:nativecase:"',history)
        self.assertIn('issuePrefix="wengua:completed:"',history)
        self.assertIn("eraseAllLocalIssueData",history)
        self.assertIn("UserDefaults.standard.removeObject",history)
        self.assertIn("清空全部问事记录与本机限制",history)
        self.assertIn("WenguaLocalHistoryView.swift",project)
    def test_nonclinical_release_gates_remain_explicit(self):
        doc=(root/"docs/APP_STORE_RELEASE_GATE_2026-10-26.md").read_text()
        self.assertIn("4.3",doc)
        self.assertIn("TestFlight",doc)
        self.assertIn("200格",doc)
        self.assertIn("未提交App Store",doc)
if __name__=="__main__":unittest.main()
