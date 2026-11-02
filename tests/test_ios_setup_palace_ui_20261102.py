"""Current-only ordinary setup, future-only elective setup and display boundaries.

Native civil-time and real six-context router execution lives in
verify_ios_manual_event_time_runtime_20261102.py and the full macOS build gate.
"""
import hashlib
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
UI = ROOT / 'ios/WenguaAppUI'


class SetupPalaceUI(unittest.TestCase):
    def test_patch_scope_preserves_sealed_engines_and_all_resources(self):
        old = json.loads((ROOT / 'archives/engineering_patch_20261102/health_frozen_20261102_before_setup_ui.json').read_text())
        new = json.loads((ROOT / 'data/releases/health_frozen_20261102.json').read_text())
        before = {f['path']: f['sha256'] for f in old['files']}
        after = {f['path']: f['sha256'] for f in new['files']}
        self.assertEqual(old['topics'], new['topics'])
        self.assertEqual(set(after) - set(before), {'ios/WenguaAppUI/WenguaSetupPresentation.swift'})
        self.assertEqual(set(before) - set(after), set())
        self.assertEqual({p for p in before if before[p] != after[p]}, {
            'ios/WenguaAppUI/' + p for p in [
                'WenguaDesignPreviewApp.swift', 'WenguaNativeReadingRouter.swift',
                'WenguaDomainJourneyScreen.swift', 'WenguaCastTimePlan.swift',
                'WenguaCastTimeView.swift', 'WenguaReadingLayout.swift',
                'WenguaNativeCustomerView.swift', 'project.yml']})
        for f in new['files']:
            self.assertEqual(hashlib.sha256((ROOT / f['path']).read_bytes()).hexdigest(), f['sha256'])

    def test_preparation_is_explicit_inline_and_form_is_one_group(self):
        app = (UI / 'WenguaDesignPreviewApp.swift').read_text()
        setup = app.split('struct CastSetupScreen: View {')[1].split('struct TraditionalReadingPreview:')[0]
        self.assertNotIn('.sheet(isPresented:$showAsk)', app)
        self.assertNotIn('if nativeChart == nil {showAsk=true}', app)
        self.assertIn('if showAsk { setupFlow } else { chartContent }', app)
        self.assertIn('WenguaPreparationCard(topic:topic) {showAsk=true}', app)
        self.assertNotIn('NavigationStack {', setup)
        self.assertIn('VStack(alignment:.leading,spacing:18)', setup)
        self.assertIn('Text("问事人与自己的关系")', setup)
        for heading, binding in [('伤损情况（必选）', '$injuryContext'), ('病程（记录用，可选）', '$duration')]:
            self.assertLess(setup.index('Text("' + heading + '")'), setup.index('selection: ' + binding) if 'selection: ' + binding in setup else setup.index('selection:' + binding))

    def test_clock_mode_is_derived_from_topic_and_five_columns_are_labeled(self):
        app = (UI / 'WenguaDesignPreviewApp.swift').read_text()
        picker = (UI / 'WenguaCastTimeView.swift').read_text().split('struct WenguaTimeSourceBanner:')[0]
        wheel = (UI / 'WenguaSetupPresentation.swift').read_text()
        self.assertIn('topic.isElective ? .plannedEvent : .currentInquiry', app)
        self.assertNotIn('$castMode', app)
        self.assertNotIn('@Binding var mode', picker)
        self.assertNotIn('selection: $mode', picker)
        self.assertEqual(app.count('WenguaCastTimePlan.resolveForTopic(topic.id,mode:castMode'), 2)
        for title in ['年', '月', '日', '时', '分']:
            self.assertIn('column("' + title + '",value:', wheel)
        self.assertIn('draftClock.instants(timezone:timezone)', picker)
        self.assertIn('confirmedAt:Date(),timezone:timezone)', picker)
        self.assertIn('.navigationDestination(isPresented:$choosingTime)', picker)

    def test_stem_marks_do_not_change_pair_width_and_pillars_label_below(self):
        app = (UI / 'WenguaDesignPreviewApp.swift').read_text()
        marker = app.split('private func markedStem(')[1].split('private func skyStemLine(')[0]
        self.assertIn('.overlay(alignment:.topTrailing)', marker)
        self.assertNotIn('HStack', marker.split('.overlay(')[0])
        self.assertLess(marker.index('.frame(height:'), marker.index('.overlay('))
        pillar = app.split('private func pillarMini(')[1].split('private func clockFactsLine(')[0]
        self.assertLess(pillar.index('Text(String(stem.prefix(1)))'), pillar.index('Text(label)'))
        header = app.split('private func chartHeaderCompact(')[1].split('private func pillarMini(')[0]
        self.assertNotIn('chart.iso', header)
        banner = (UI / 'WenguaCastTimeView.swift').read_text().split('struct WenguaTimeSourceBanner:')[1].split('struct WenguaCandidateComparison:')[0]
        self.assertIn('QuestionCatalog.directionTitle(reading.topicID)', banner)
        self.assertNotIn('castTimeZone', banner)

    def test_palace_details_center_title_and_enlarge_identity(self):
        app = (UI / 'WenguaDesignPreviewApp.swift').read_text()
        detail = app.split('struct ProfessionalPalaceDetail:')[1].split('enum QIssuePolicy')[0]
        self.assertNotIn('本机 Swift', detail)
        self.assertNotIn('本机实算', detail)
        self.assertIn('alignment:.center', detail)
        self.assertIn('.font(.system(size:16,weight:.semibold))', detail)

    def test_previous_contracts_are_archived_with_hashes(self):
        index = json.loads((ROOT / 'archives/engineering_patch_20261102/before_setup_ui_tests/INDEX.json').read_text())
        self.assertGreaterEqual(len(index['entries']), 6)
        for entry in index['entries']:
            self.assertEqual(hashlib.sha256((ROOT / entry['archive']).read_bytes()).hexdigest(), entry['sha256'])
