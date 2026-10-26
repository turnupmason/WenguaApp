"""App-level verified Apple required-reason API manifest for local UserDefaults."""
import plistlib
import unittest
from pathlib import Path
root=Path(__file__).resolve().parents[1]
class PrivacyReason(unittest.TestCase):
    def test_manifest_local_defaults_only(self):
        source=root/"ios/WenguaAppUI/PrivacyInfo.xcprivacy"
        manifest=plistlib.loads(source.read_bytes())
        self.assertFalse(manifest["NSPrivacyTracking"])
        self.assertEqual(manifest["NSPrivacyCollectedDataTypes"],[])
        self.assertEqual(manifest["NSPrivacyAccessedAPITypes"],[{
            "NSPrivacyAccessedAPIType":"NSPrivacyAccessedAPICategoryUserDefaults",
            "NSPrivacyAccessedAPITypeReasons":["CA92.1"]}])
        spec=(root/"ios/WenguaAppUI/project.yml").read_text()
        self.assertIn("PrivacyInfo.xcprivacy",spec)
if __name__=="__main__":unittest.main()
