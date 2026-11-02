import hashlib
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
UI = ROOT / 'ios/WenguaAppUI'

class ScreenshotPolish(unittest.TestCase):
    def test_only_authorized_presentation_changes_and_resources_unchanged(self):
        old=json.loads((ROOT/'archives/engineering_patch_20261102/before_polish_p7/health_frozen_20261102.json').read_text())
        new=json.loads((ROOT/'data/releases/health_frozen_20261102.json').read_text())
        previous={x['path']:x['sha256'] for x in old['files']}
        changed={x['path'] for x in new['files'] if x['sha256']!=previous[x['path']]}
        self.assertEqual(changed,{'ios/WenguaAppUI/'+s for s in ['WenguaDesignPreviewApp.swift','WenguaSetupPresentation.swift','WenguaCastTimeView.swift','WenguaPremiumReadingView.swift','WenguaReadingLayout.swift','WenguaNativeCustomerView.swift']})
        self.assertEqual(old['topics'],new['topics'])
        for entry in new['files']:
            self.assertEqual(hashlib.sha256((ROOT/entry['path']).read_bytes()).hexdigest(),entry['sha256'])

    def test_visible_controls_complete_text_and_concise_summary(self):
        views=(UI/'WenguaSetupPresentation.swift').read_text()
        app=(UI/'WenguaDesignPreviewApp.swift').read_text()
        time=(UI/'WenguaCastTimeView.swift').read_text()
        summary=(UI/'WenguaPremiumReadingView.swift').read_text().split('func frontNarrative(')[1].split('static func from(')[0]
        self.assertIn('.lineLimit(nil).fixedSize(horizontal:false,vertical:true)',views)
        self.assertIn('struct WenguaChoiceField:',views)
        self.assertIn('stroke(QStyle.blue.opacity(0.40)',views)
        self.assertIn('起局时间：当前时辰问事',time)
        self.assertIn('.frame(maxWidth:.infinity,alignment:.leading)',time)
        self.assertIn('return ending',summary)
        self.assertNotIn('return body',summary)
        self.assertIn('entry.element.map(String.init).joined(separator:"\\n")',app)
        self.assertIn('WenguaCivilDateRow(iso:chart.iso,timezone:chart.timezone)',app)
