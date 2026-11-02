"""Explicit UI patch scope: current V27 conclusion, unchanged frozen rule resources."""
import hashlib
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]

class QimenLunjiRelease(unittest.TestCase):
    def test_display_patch_keeps_templates_and_rules_byte_identical(self):
        old=json.loads((ROOT/'archives/engineering_patch_20261102/health_frozen_20261102_before_frontpage.json').read_text())
        new=json.loads((ROOT/'archives/engineering_patch_20261102/health_frozen_20261102_before_meditation.json').read_text())
        previous={x['path']:x['sha256'] for x in old['files']}
        current={x['path']:x['sha256'] for x in new['files']}
        self.assertEqual(previous.keys(),current.keys())
        self.assertEqual({p for p in previous if previous[p]!=current[p]}, {
            'ios/WenguaAppUI/WenguaDesignPreviewApp.swift',
            'ios/WenguaAppUI/WenguaPremiumReadingView.swift',
            'ios/WenguaAppUI/WenguaLocalHistoryView.swift'})
        self.assertEqual(old['topics'],new['topics'])
        for item in new['files']:
            if item['kind']=='resource':
                self.assertEqual(hashlib.sha256((ROOT/item['path']).read_bytes()).hexdigest(),previous[item['path']])

    def test_topic_labels_and_correct_v27_summary_are_wired(self):
        app=(ROOT/'ios/WenguaAppUI/WenguaDesignPreviewApp.swift').read_text()
        card=(ROOT/'ios/WenguaAppUI/WenguaPremiumReadingView.swift').read_text()
        history=(ROOT/'ios/WenguaAppUI/WenguaLocalHistoryView.swift').read_text()
        self.assertIn('QuestionTopic(id:"health.discomfort",title:"奇门论疾"',app)
        self.assertIn('"健康 · 奇门论疾"',history)
        self.assertIn('"奇门论疾 · 古籍类象"',card)
        self.assertIn('$0.id == "09_conclusion"',card)
        self.assertNotIn('$0.id=="06_conclusion"',card)
        for text in (app,card,history):
            self.assertNotIn('伤病在哪里',text)
            self.assertNotIn('病情在哪里',text)

    def test_concise_meditation_patch_keeps_frozen_templates_and_explicit_scope(self):
        old=json.loads((ROOT/'archives/engineering_patch_20261102/health_frozen_20261102_before_meditation.json').read_text())
        new=json.loads((ROOT/'archives/engineering_patch_20261102/health_frozen_20261102_before_manual_time.json').read_text())
        previous={x['path']:x['sha256'] for x in old['files']}
        current={x['path']:x['sha256'] for x in new['files']}
        self.assertEqual(set(current)-set(previous), {'ios/WenguaAppUI/WenguaMeditationView.swift'})
        self.assertEqual(set(previous)-set(current),set())
        self.assertEqual({p for p in previous if previous[p]!=current[p]}, {
            'ios/WenguaAppUI/WenguaDesignPreviewApp.swift',
            'ios/WenguaAppUI/WenguaPremiumReadingView.swift',
            'ios/WenguaAppUI/WenguaNativeDiscomfortV15.swift',
            'ios/WenguaAppUI/WenguaNativeReadingRouter.swift',
            'ios/WenguaAppUI/project.yml'})
        self.assertEqual(old['topics'],new['topics'])
        for item in new['files']:
            if item['kind']=='resource':
                self.assertEqual(hashlib.sha256((ROOT/item['path']).read_bytes()).hexdigest(),previous[item['path']])

    def test_first_card_is_concise_and_animation_preserves_real_time_gate(self):
        app=(ROOT/'ios/WenguaAppUI/WenguaDesignPreviewApp.swift').read_text()
        card=(ROOT/'ios/WenguaAppUI/WenguaPremiumReadingView.swift').read_text()
        scene=(ROOT/'ios/WenguaAppUI/WenguaMeditationView.swift').read_text()
        self.assertNotIn('Text(verdict.details)',card)
        self.assertIn('with: "先看"',card)
        self.assertIn('WenguaMeditationScene(',app)
        self.assertIn('Date().addingTimeInterval(30)',app)
        self.assertIn('guard let calmEnds, Date() >= calmEnds',app)
        self.assertIn('accessibilityReduceMotion',scene)
        self.assertIn('paused: !animates',scene)
        project=(ROOT/'ios/WenguaAppUI/project.yml').read_text()
        self.assertIn('SWIFT_TREAT_WARNINGS_AS_ERRORS: YES',project)
        self.assertIn('path: WenguaMeditationView.swift',project)
