"""Real Kun-2 dual patterns: ordinary earth audit cannot borrow center stem."""
import copy
import hashlib
import json
from pathlib import Path
import types
import unittest
from src.wengua.health_text_pipeline_vnext_review import auto_cast_health_review_text
from src.wengua.health_quant_overlay_vnext import _quantize_one
from tests.test_health_door_break_exception_vnext import detail

ROOT=Path(__file__).resolve().parents[1]

class EarthStemAuditPatch(unittest.TestCase):
    def test_existing_real_clocks_scores_and_customer_words_unchanged(self):
        cases=json.loads((ROOT/'docs/audits/health_cleanup_20261102/pre_patch_score_and_text.json').read_text())
        hosted=0
        for case in cases:
            result=auto_cast_health_review_text(iso=case['iso'],timezone_name='America/New_York',
                inquiry={'intent':'severity','relationship':'self','consultation_context':'direct_self'})
            q=result['full_health_role_strength_network']['candidate_five_grade_quantization']
            self.assertEqual(q['summary'],case['summary'])
            self.assertEqual(hashlib.sha256(result['reading_text'].encode()).hexdigest(),case['reading_sha256'])
            for row in q['roles'].values():
                self.assertEqual(row['ten_stem_intrinsic']['earth']['stem'],row['real_earth_stem_fact']['symbol'])
                if row['palace']==2:hosted+=1
        self.assertGreaterEqual(hosted,3)

    def test_dual_pair_order_never_changes_earth_identity_or_scores(self):
        r=auto_cast_health_review_text(iso='2025-07-18T03:00:00-04:00',timezone_name='America/New_York',
            inquiry={'intent':'severity','relationship':'self','consultation_context':'direct_self'})
        d=r['full_health_role_strength_network']['complete_selected_palace_audits']['illness']
        self.assertEqual(d['palace'],2)
        self.assertEqual(d['earth_stem']['symbol'],'戊')
        self.assertEqual([p['earth'] for p in d['ordered_book_81_pairs']],['戊','丁'])
        one=_quantize_one('illness',d,five_not_encounter=False)
        shuffled=copy.deepcopy(d);shuffled['ordered_book_81_pairs'].reverse()
        two=_quantize_one('illness',shuffled,five_not_encounter=False)
        self.assertEqual(one['ten_stem_intrinsic']['earth']['stem'],'戊')
        self.assertEqual(two['ten_stem_intrinsic']['earth']['stem'],'戊')
        for key in ('score','raw_sum','known_subtotal'):
            self.assertEqual(one['palace_score'][key],two['palace_score'][key])
        old=types.ModuleType('src.wengua._pre_patch');old.__package__='src.wengua'
        exec(compile((ROOT/'archives/engineering_patch_20261102/health_quant_overlay_vnext_before_earth_audit_fix.py.txt').read_text(),str(ROOT/'src/wengua/health_quant_overlay_vnext.py'),'exec'),old.__dict__)
        before=old._quantize_one('illness',d,five_not_encounter=False)
        self.assertEqual(before['ten_stem_intrinsic']['earth']['stem'],'丁')
        self.assertEqual(before['palace_score'],one['palace_score'])
        before.pop('ten_stem_intrinsic');one.pop('ten_stem_intrinsic')
        self.assertEqual(before,one)

    def test_empty_pair_diagnostic_has_no_invented_earth(self):
        got=_quantize_one('medicine',detail('生门',1),five_not_encounter=False)
        self.assertIsNone(got['ten_stem_intrinsic']['earth'])
        self.assertEqual(got['pattern']['matches'],[])

    def test_release_patch_scope_preserves_all_templates_and_other_pins(self):
        previous=json.loads((ROOT/'archives/engineering_patch_20261102/health_frozen_20261102_before_patch.json').read_text())
        current=json.loads((ROOT/'data/releases/health_frozen_20261102.json').read_text())
        old={r['path']:r['sha256'] for r in previous['files']}
        new={r['path']:r['sha256'] for r in current['files']}
        self.assertEqual(set(old),set(new))
        self.assertEqual({p for p in old if old[p]!=new[p]}, {'src/wengua/health_quant_overlay_vnext.py'})
        self.assertEqual(previous['topics'],current['topics'])
        for item in json.loads((ROOT/'archives/engineering_patch_20261102/original_test_index.json').read_text()):
            self.assertEqual(hashlib.sha256((ROOT/item['preserved']).read_bytes()).hexdigest(),item['sha256'])
