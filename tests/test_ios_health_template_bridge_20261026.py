"""Stage-1 bridge contract: app bundles the EXACT checked-in JSON and 81 pairs.
No dynamic GitHub fetch and no invented severity verdict in Swift.
"""
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"ios/WenguaAppUI/WenguaHealthTemplateBridge.swift"
MAIN=ROOT/"ios/WenguaAppUI/WenguaDesignPreviewApp.swift"
PROJECT=ROOT/"ios/WenguaAppUI/project.yml"
TEMPLATE=ROOT/"data/templates/health_severity_vnext/reading_template.json"
PAIRS=ROOT/"data/knowledge/health_81_excel_20261025/81_pairs.tsv"

class NativeTemplateBundleContract(unittest.TestCase):
    def test_exact_live_sources_are_bundled_and_looked_up_in_real_chart(self):
        source=SRC.read_text("utf8")
        project=PROJECT.read_text("utf8")
        view=MAIN.read_text("utf8")
        for part in ["WenguaHealthTemplateBridge.swift",
                     "../../data/templates/health_severity_vnext/reading_template.json",
                     "../../data/knowledge/health_81_excel_20261025/81_pairs.tsv"]:
            self.assertIn(part,project)
        for word in ['fromBundle(chart:','fromText(chart:',
                     'item.carriedStem+"|"+palace.earthStem',
                     'WenguaHealthTemplateError.invalidCatalog']:
            self.assertIn(word,source)
        self.assertIn("WenguaHealthTemplateBridge.fromBundle(chart:chart)",view)
        data=json.loads(TEMPLATE.read_text("utf8"))
        for key in ["heaven","earth","name","polarity",
                    "classical_text","classical_meaning","imagery"]:
            self.assertIn("{"+key+"}",data["formation"])
        lines=PAIRS.read_text("utf8").splitlines()
        self.assertEqual(len(lines),82)
        self.assertEqual(len({(r.split("|")[0],r.split("|")[1]) for r in lines[1:]}),81)
    def test_full_clinical_or_vnext_score_is_not_claimed_on_phone(self):
        swift=SRC.read_text("utf8")
        view=MAIN.read_text("utf8")
        self.assertIn("尚非完整断案",view)
        self.assertNotIn("auto_cast_health_review_text(",swift)
        self.assertIn("完整专业解读尚在接入中",view)
if __name__=="__main__":
    unittest.main()
