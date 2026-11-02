"""Real-clock regression: priority, source strength, disabled injury and UI DTO."""
import copy
import unittest
from src.wengua.health_discomfort_v19_parity import compose, load_sources, STRIKING
from tests.test_health_discomfort_injury_gate_20261102 import live_board

class OrderedSummary(unittest.TestCase):
    def test_real_clocks_all_contexts_share_summary_and_keep_full_evidence(self):
        for iso in ('2026-11-12T19:00:00-05:00','2026-11-09T11:00:00-05:00',
                    '2026-12-29T09:00:00-05:00','2027-02-07T11:00:00-05:00'):
            chart,actor=live_board(iso)
            before=copy.deepcopy(chart)
            for context in ('none','accident','bone','bleeding','severe_pain','surgery'):
                with self.subTest(iso=iso,context=context):
                    out=compose(chart,actor,'丈夫',context)
                    summary=out['bodySiteSummary']
                    self.assertTrue(out['sections'][0]['text'].startswith(summary+'\n'))
                    conclusion=out['sections'][-1]['text']
                    self.assertTrue(conclusion.startswith('综上，'+summary))
                    self.assertIn('先',summary)
                    self.assertIn('天盘',conclusion);self.assertIn('地盘',conclusion)
                    self.assertIn('时干',conclusion);self.assertIn('丈夫用神',conclusion)
                    self.assertEqual('injury' in out['rolePalaces'],context!='none')
                    self.assertEqual(out['sections'][0]['id'],'01_location' if context=='none' else '02_injury')
                    self.assertNotIn('肯定受伤',conclusion)
                    if context=='none':self.assertNotIn('先从伤门落宫看',summary)
                    if context in ('accident','bone','bleeding','severe_pain'):
                        self.assertIn('先从伤门落宫看',summary.split('。')[0])
                    if context=='surgery':self.assertIn('伤门所示手术部位另看',conclusion)
                    details=next(x['text'] for x in out['sections'] if x['id']=='01_location')
                    for p in chart['palaces']:
                        if p['id']==5:continue
                        for stem in {x['carriedStem'] for x in p['heavenStars']}|{p['earthStem']}:
                            tomb=any(t['stem']==stem for t in p['tombs'])
                            striking=any(x['carriedStem']==stem for x in p['heavenStars']) and STRIKING.get(stem)==p['id']
                            if tomb or striking:
                                self.assertIn(stem+'主',details)
                    self.assertEqual(chart,before)

    def test_weak_real_tomb_gets_priority_without_inflating_source_tier(self):
        chart,actor=live_board('2026-11-12T19:00:00-05:00')
        out=compose(chart,actor,'丈夫','none')
        summary=out['bodySiteSummary']
        self.assertIn('乾六宫戊入墓',summary)
        self.assertIn('须优先核对',summary)
        detail=next(s['text'] for s in out['sections'] if s['id']=='01_location')
        self.assertIn('乾六宫戊主脾，力量极小，入墓',detail)
        # A broad source image cannot be replaced with the palace's unrelated ear.
        self.assertNotIn('癸六仪击刑所指左耳',summary)

    def test_source_catalogs_unchanged_by_composition(self):
        sources=load_sources();before=copy.deepcopy(sources)
        chart,actor=live_board('2026-11-12T19:00:00-05:00')
        compose(chart,actor,'丈夫','none',sources)
        self.assertEqual(sources,before)

if __name__=='__main__':unittest.main()
