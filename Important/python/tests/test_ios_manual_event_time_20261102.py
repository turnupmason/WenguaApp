"""Authorized event-time UI and data contracts, independent of frozen scoring."""
import hashlib
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
UI=ROOT/'ios/WenguaAppUI'

class EventTimeEntry(unittest.TestCase):
    def test_release_has_explicit_scope_and_unchanged_rule_resources(self):
        old=json.loads((ROOT/'archives/engineering_patch_20261102/health_frozen_20261102_before_manual_time.json').read_text())
        current=json.loads((ROOT/'archives/engineering_patch_20261102/health_frozen_20261102_before_domain_ui.json').read_text())
        previous={e['path']:e['sha256'] for e in old['files']}
        now={e['path']:e['sha256'] for e in current['files']}
        self.assertEqual(old['topics'],current['topics'])
        self.assertEqual(set(now)-set(previous),{
            'ios/WenguaAppUI/WenguaCastTimePlan.swift',
            'ios/WenguaAppUI/WenguaCastTimeView.swift'})
        self.assertEqual({p for p in previous if now[p]!=previous[p]}, {
            'ios/WenguaAppUI/WenguaDesignPreviewApp.swift',
            'ios/WenguaAppUI/WenguaDomainJourneyScreen.swift',
            'ios/WenguaAppUI/WenguaLocalHistoryView.swift',
            'ios/WenguaAppUI/WenguaNativeCustomerView.swift',
            'ios/WenguaAppUI/WenguaNativeReadingRouter.swift',
            'ios/WenguaAppUI/WenguaPremiumReadingView.swift',
            'ios/WenguaAppUI/project.yml'})
        for item in current['files']:
            if item['kind']=='resource':
                self.assertEqual(hashlib.sha256((ROOT/item['path']).read_bytes()).hexdigest(),previous[item['path']])

    def test_actual_choice_reaches_engine_and_single_group_commit(self):
        app=(UI/'WenguaDesignPreviewApp.swift').read_text()
        picker=(UI/'WenguaCastTimeView.swift').read_text()
        self.assertIn('WenguaCivilClockWheel(clock:$draftClock',picker)
        wheel=(UI/'WenguaSetupPresentation.swift').read_text()
        self.assertIn('.pickerStyle(.wheel)',wheel)
        self.assertIn('draftClock.instants(timezone:timezone)',picker)
        self.assertIn('WenguaCastTimePlan.resolveForTopic(topic.id,mode:castMode',app)
        self.assertIn('WenguaNativeCore.compute(at:instant,timezone:localZone)',app)
        method=app.split('private func completeNativeCast()',1)[1].split('private func tryStartRitual()',1)[0]
        self.assertEqual(method.count('QIssuePolicy.commitRealCompletedCast('),1)
        self.assertLess(method.index('for (index,instant)'),method.index('WenguaCaseBatchStore.save(records)'))
        self.assertLess(method.index('WenguaCaseBatchStore.save(records)'),method.index('QIssuePolicy.commitRealCompletedCast('))
        self.assertIn('completedAt:confirmedAt',method)
        self.assertNotIn('不提供手选时辰',app)

    def test_labels_and_domain_grade_boundaries_are_explicit(self):
        router=(UI/'WenguaNativeReadingRouter.swift').read_text()
        helper=(UI/'WenguaCastTimePlan.swift').read_text()
        card=(UI/'WenguaPremiumReadingView.swift').read_text()
        history=(UI/'WenguaLocalHistoryView.swift').read_text()
        self.assertIn('reference.iso==primary.iso',router)
        self.assertIn('reference.resolvedHealthGrade',router)
        self.assertIn('actual_chart_only_domain_timing_grade_pending',helper)
        self.assertIn('此时辰：',router)
        self.assertIn('reading.timingHeadline',card)
        self.assertIn('timingGradeScope',card)
        self.assertIn('?.interpretationReady == true',(UI/'WenguaDesignPreviewApp.swift').read_text())
        self.assertIn('record.chart.iso',history)
        self.assertIn('WenguaCaseBatchStore.decode(data)',history)
        self.assertIn('SWIFT_TREAT_WARNINGS_AS_ERRORS: YES',(UI/'project.yml').read_text())
