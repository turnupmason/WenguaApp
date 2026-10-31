"""V11 BigFish actual source-pin + two-tab summary contract (no fake score)."""
from __future__ import annotations

import importlib.util
import json
import sys
import types
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'scripts/wengua_bigfish_518400_offline_editorial_20261029.py'

def load():
    fake=types.ModuleType('local_batch')
    fake.BIGFISH_SHA='6112b3937d7fcaa2ab0a34aec2a52f74e2effe6c'
    fake.WENGUA_SHA='original_legacy_pin_for_test'
    fake.GRADE={-5:'极大凶',-4:'大凶',-3:'中凶',-2:'小凶',
                -1:'极小凶',0:'微恙',1:'极小吉',2:'小吉',3:'中吉',
                4:'大吉',5:'极大吉'}
    old=sys.modules.get('local_batch')
    try:
        sys.modules['local_batch']=fake
        spec=importlib.util.spec_from_file_location('current_bigfish_v11_test',SOURCE)
        module=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        if old is not None:sys.modules['local_batch']=old
        else:sys.modules.pop('local_batch',None)
B=load()

class BigFishV11TwoTab(unittest.TestCase):
    def test_pin_is_v11_and_v6_wont_replace_historic_databases(self):
        self.assertEqual(B.SIX_JIA_APPROVED_WENGUA_SHA,
                         '46382694a418300ac4660a1c22bcf227857c9a52')
        self.assertIn('v6_V11_full_two_tab',B.REAL_PIPELINE_VERSION)
        self.assertIn('V11_complete',B.PIPELINE_VERSION)
        self.assertIn('V11_20261031',B.SIX_JIA_BATCH_SUBDIR)
        script=SOURCE.read_text(encoding='utf8')
        self.assertIn("WenguaApp_V11_source_20261031",script)
        self.assertIn("frozen_V11_source_20261031",script)
        self.assertIn("source_v6_v11_full_two_tab_friend_month_only",script)
        self.assertEqual(len(B.V11_FRONT_CAPTIONS),11)
        self.assertEqual(json.loads((ROOT/'data/templates/health_severity_vnext/reading_template.json').read_text(encoding='utf8'))['schema'],
                         'health_severity_user_editable_template_v20261031_v11_full_evidence')

    def test_true_source_summary_and_source_verdict_must_match(self):
        evidence=('病星天芮在震三宫，势小，宫象小凶；患者己在坎一宫，势大，生扶病宫。\n\n'
                  '医药两端分别看：天心势大，克病宫，乙奇势中等，受病宫生。\n\n'
                  '另参时干事体、实际值符和合宫限制，不借后验事实修改断语。')
        macro='本时不犯五不遇。 伏吟主慢。'
        for grade in ('极大吉','大吉','中吉','小吉','极小吉','极小凶','小凶','中凶','大凶','极大凶','不凶不吉'):
            with self.subTest(grade=grade):
                source=[
                    {'id':'01_macro','title':'时局总纲','text':macro},
                    {'id':'02_illness','title':'天芮病宫','text':'原始宫位详述不能丢'},
                    {'id':'90_review','title':'综合断语','text':evidence+'\n\n综上所述，此病为'+grade+'；以上仅作参考。'},
                    {'id':'91_timing','title':'时空及应期','text':'未能核实具体日期，不虚构。'}
                ]
                page=B.v11_front_page_from_real_sections(source,'微恙' if grade=='不凶不吉' else grade)
                self.assertEqual(page['grade'],grade)
                self.assertIn(evidence,page['body'])
                self.assertIn('伏吟主慢',page['body'])
                self.assertEqual(page['display_text'].splitlines()[0],B.V11_FRONT_CAPTIONS[grade][0])
                self.assertEqual(page['source_review_sha256'],B.sha_text(source[-2]['text']))
                self.assertEqual(source[1]['text'],'原始宫位详述不能丢')
                self.assertNotIn('以上仅作参考',page['body'])
                with self.assertRaisesRegex(ValueError,'矛盾'):
                    B.v11_front_page_from_real_sections(source,'大凶' if grade!='大凶' else '大吉')

    def test_no_grade_from_missing_source_and_iOS_title_verbatim(self):
        ios=(ROOT/'ios/WenguaAppUI/WenguaPremiumReadingView.swift').read_text(encoding='utf8')
        for category,epithet,description in B.V11_FRONT_CAPTIONS.values():
            self.assertIn('epithet:"'+epithet+'"',ios)
            self.assertIn('interpretation:"'+description+'"',ios)
        with self.assertRaisesRegex(ValueError,'缺综合'):
            B.v11_front_page_from_real_sections([], '大吉')
        with self.assertRaisesRegex(ValueError,'综合证据不完整'):
            B.v11_front_page_from_real_sections([
                {'id':'90_review','text':'综上所述，此病为大吉。'}],'大吉')

if __name__=='__main__':unittest.main()
