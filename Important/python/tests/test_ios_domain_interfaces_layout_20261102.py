"""Domain intent separation, real inputs and frozen-rule boundaries."""
import hashlib
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
UI=ROOT/'ios/WenguaAppUI'

class DomainInterfaceLayout(unittest.TestCase):
    def test_patch_does_not_change_health_math_templates_or_resources(self):
        old=json.loads((ROOT/'archives/engineering_patch_20261102/health_frozen_20261102_before_domain_ui.json').read_text())
        new=json.loads((ROOT/'archives/engineering_patch_20261102/health_frozen_20261102_before_setup_ui.json').read_text())
        a={x['path']:x['sha256'] for x in old['files']}
        b={x['path']:x['sha256'] for x in new['files']}
        self.assertEqual(old['topics'],new['topics'])
        self.assertEqual(set(b)-set(a),{'ios/WenguaAppUI/WenguaReadingLayout.swift'})
        self.assertEqual({p for p in a if a[p]!=b[p]}, {
            'ios/WenguaAppUI/'+name for name in [
                'WenguaDesignPreviewApp.swift','WenguaDomainJourneyScreen.swift',
                'WenguaLocalHistoryView.swift','WenguaNativeCustomerView.swift',
                'WenguaNativeReadingRouter.swift','WenguaPremiumReadingView.swift',
                'WenguaCastTimePlan.swift','WenguaCastTimeView.swift','project.yml']})
        for item in new['files']:
            if item['kind']=='resource':
                self.assertEqual(hashlib.sha256((ROOT/item['path']).read_bytes()).hexdigest(),a[item['path']])

    def test_domain_local_day_selection_is_reserved_not_another_reading(self):
        app=(UI/'WenguaDesignPreviewApp.swift').read_text()
        journey=(UI/'WenguaDomainJourneyScreen.swift').read_text()
        router=(UI/'WenguaNativeReadingRouter.swift').read_text()
        self.assertNotIn('plannedTimingTopic',app+journey)
        self.assertNotIn('挑日子 · 按事项时间排盘',journey)
        self.assertIn('electiveTopics("health","疾病健康")',app)
        self.assertIn('electiveTopics(id,title)',app)
        self.assertIn('electiveReserved',router)
        self.assertIn('if selected.canCast { select(selected) }',journey)
        self.assertIn('selectedRoleIDs',router)
        self.assertIn('forFinalNetScore',router)

    def test_no_inert_description_or_unconfirmed_default_time(self):
        app=(UI/'WenguaDesignPreviewApp.swift').read_text()
        picker=(UI/'WenguaCastTimeView.swift').read_text()
        customer=(UI/'WenguaNativeCustomerView.swift').read_text()
        self.assertNotIn('描述一件具体的事',app)
        self.assertNotIn('normalized.count >= 4',app)
        self.assertIn('structuredSignature',app)
        self.assertIn('nextPermittedIssue',app)
        self.assertIn('isConfirmed',app)
        self.assertIn('Label("选择时辰"',picker)
        self.assertNotIn('WenguaCastTimePlan.display(',picker.split('struct WenguaTimeSourceBanner')[0])
        self.assertNotIn('再加一个候选时间',picker)
        self.assertIn('clock:$draftClock',picker)
        self.assertIn('WenguaReadingLayout.blocks(text,sectionID:sectionID)',customer)
        self.assertIn('WenguaReadingLayout.paragraphs(block)',customer)
