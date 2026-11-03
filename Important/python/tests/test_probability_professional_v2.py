import copy
import hashlib
import json
import lzma
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from src.wengua.casting_shenqi import layout_from_explicit_bureau
from src.wengua.probability_dataset_v2 import atlas, literal_board, source_header, training_pack
from src.wengua.probability_features_v2 import build_bundle, flatten_bundle, features_for_row, _rel, source_fingerprint
from src.wengua.probability_research import ROOT, SOURCE_DB, SOURCE_SHA256, features
from scripts.probability_research import predict


def sample_payload(*, month='壬申', day='甲子', hour='己巳', dun='yin', ju=8, domain='health'):
    raw = layout_from_explicit_bureau(dun=dun, ju=ju, hour_ganzhi=hour)
    board = {k: raw[k] for k in ['palaces', 'hour_ganzhi', 'value_star', 'value_door', 'school_id']}
    for p, cell in board['palaces'].items():
        if int(p) == 2:
            cell['hosted_centre_earth_stem'] = board['palaces']['5']['earth_stem']
        for key in list(cell):
            if key not in ['palace', 'door', 'deity', 'earth_stem', 'heaven_stars', 'hosted_centre_earth_stem']:
                cell.pop(key)
    return {'board': board, 'calendar': {'year_ganzhi': '己丑', 'month_ganzhi': month,
            'day_ganzhi': day, 'hour_ganzhi': hour, 'dun': dun, 'ju': ju},
            'inquiry': {'relationship': 'self', 'consultation_context': 'direct_self', 'intent': 'severity'}, 'domain': domain}


class ProfessionalFeaturesV2Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.atlas = atlas()
        cls.pack = training_pack(prepared_atlas=cls.atlas)

    def test_all_original_events_and_real_additional_casts_remain_grouped(self):
        self.assertEqual(len(self.atlas['cases']), 194)
        self.assertEqual(len(self.atlas['additional_casts']), 19)
        self.assertEqual(self.atlas['coverage']['nine_source_cells'], 160)
        self.assertEqual(self.atlas['coverage']['all_directed_pair_positions'], 213*81)
        self.assertEqual(len(self.pack['rows']), 12)
        self.assertEqual(len({r['event_family_id'] for r in self.pack['rows']}), 11)
        self.assertEqual(hashlib.sha256(SOURCE_DB.read_bytes()).hexdigest(), SOURCE_SHA256)

    def test_nine_nodes_all_eighty_one_positions_and_source_direction(self):
        bundle = build_bundle(sample_payload())
        self.assertEqual(len(bundle['nodes']), 9)
        self.assertEqual(len(bundle['edges']), 81)
        edges = {(r['source'], r['target']): r for r in bundle['edges']}
        self.assertEqual(edges[3, 2]['palace_relation'], '克')
        self.assertEqual(edges[2, 3]['palace_relation'], '受克')
        self.assertEqual(edges[3, 3]['applicability'], 'self')
        self.assertIsNone(edges[3, 3]['branch_punishment_component'])
        flat = flatten_bundle(bundle)
        self.assertEqual(flat['edge.p3.p3.branch_punishment_component'], 'not_applicable')

    def test_nine_star_month_and_palace_month_are_different(self):
        bundle = build_bundle(sample_payload())
        node = bundle['nodes'][2]
        self.assertEqual(node['star'], '天芮星')
        self.assertEqual(node['star_month_stage'], '旺')
        self.assertEqual(node['palace_month_stage'], '死')
        self.assertEqual(node['star_palace_relation'], '受克')
        self.assertEqual(node['deity_month_stage'], 'not_applicable')

    def test_source_directional_cycles_are_not_symmetrized(self):
        self.assertTrue(_rel('branch_punishment', '寅', '巳'))
        self.assertFalse(_rel('branch_punishment', '巳', '寅'))
        self.assertTrue(_rel('branch_self_punishment', '午', '午'))

    def test_actual_twelve_life_branches_and_no_fabricated_gui_chen_tomb(self):
        bundle = build_bundle(sample_payload())
        for node in bundle['nodes']:
            if node['palace'] == 4:
                for carrier in node['carriers']:
                    if carrier['stem'] == '癸':
                        self.assertFalse(any(r['stage'] == '墓' for r in carrier['lifecycle']))
        from src.wengua.probability_features_v2 import _stage
        self.assertEqual(_stage('癸', 4), [{'branch': '辰', 'stage': '养'}, {'branch': '巳', 'stage': '胎'}])
        self.assertEqual(_stage('庚', 4), [{'branch': '辰', 'stage': '养'}, {'branch': '巳', 'stage': '长生'}])

    def test_center_has_no_fabricated_normal_occupants(self):
        bundle = build_bundle(sample_payload())
        self.assertIsNone(bundle['nodes'][4]['star'])
        flat = flatten_bundle(bundle)
        self.assertEqual(flat['node.p5.star'], 'not_applicable')
        self.assertEqual(flat['node.p5.heaven.lifecycle.辰'], 'not_applicable')
        self.assertNotEqual(flat['node.p5.earth'], '__unknown__')

    def test_missing_month_or_stem_stays_unknown_not_zero(self):
        payload = sample_payload()
        payload['calendar'].pop('month_ganzhi')
        cell = payload['board']['palaces']['3']
        cell['heaven_stars'][0]['carried_stem'] = None
        flat = flatten_bundle(build_bundle(payload))
        self.assertEqual(flat['node.p3.palace_month_stage'], '__unknown__')
        self.assertEqual(flat['node.p3.heaven.has_墓'], '__unknown__')

    def test_same_schema_for_full_partial_and_missing_charts(self):
        keys = None
        for record in self.atlas['cases']:
            current = set(flatten_bundle(record['bundle']))
            if keys is None:
                keys = current
            self.assertEqual(keys, current)
        empty = build_bundle({'board': {}, 'calendar': {}, 'inquiry': {}, 'domain': 'health'})
        self.assertEqual(keys, set(flatten_bundle(empty)))
        self.assertEqual(flatten_bundle(empty)['cohost.p1.stem:乙'], '__unknown__')

    def test_whole_column_layer_audit_and_original_bytes_preserved(self):
        db = sqlite3.connect(SOURCE_DB.as_uri() + '?mode=ro', uri=True)
        db.row_factory = sqlite3.Row
        cells = [dict(r) for r in db.execute("select * from historical_chart_cells where case_id='shenqi.lost_property.case01' order by palace")]
        db.close()
        original = copy.deepcopy(cells)
        calendar = {'dun': 'yang', 'ju': 1, 'hour_ganzhi': '壬申'}
        board, audit = literal_board(cells, calendar, {})
        self.assertEqual(audit['plane_convention'], 'earth_in_star_source_line')
        self.assertEqual(board['palaces']['1']['earth_stem'], '戊')
        self.assertEqual(board['palaces']['1']['heaven_stars'][0]['carried_stem'], '辛')
        self.assertEqual(cells, original)
        cells[0]['star_position_raw'] = '辅乙'
        changed, audit = literal_board(cells, calendar, {})
        self.assertEqual(audit['plane_convention'], 'unresolved_source_planes')
        self.assertIsNone(changed['palaces']['1']['earth_stem'])
        self.assertEqual(cells[0]['star_position_raw'], '辅乙')

    def test_split_line_explicit_bureau_and_conflicting_alternatives(self):
        lines = ['丙子年丁酉月癸亥日辛酉时。', '', '阴4局，甲寅旬，值符天任星、值使生门。', '格局如下', '盘']
        calendar, receipt = source_header('\n'.join(lines), [{'source_line': 5}], {})
        self.assertEqual((calendar['dun'], calendar['ju']), ('yin', 4))
        self.assertEqual(receipt['value_star'], '天任星')
        self.assertEqual(receipt['value_door'], '生门')
        lines[2] = '阴4局或阴7局，来源待核。'
        calendar, _ = source_header('\n'.join(lines), [{'source_line': 5}], {})
        self.assertNotIn('ju', calendar)
        lines[0] += '阴4局或阴7局。'
        calendar, _ = source_header('\n'.join(lines), [{'source_line': 5}], {})
        self.assertNotIn('ju', calendar)

    def test_initial_blind_disclosures_are_masked_without_adding_events(self):
        corrected = [r for r in self.pack['rows'] if r['case_id'] in self.pack['inventory']['context_corrections']]
        self.assertEqual(len(corrected), 2)
        self.assertTrue(all(r['context']['item_kind'] == '__unknown_at_first_cast__' for r in corrected))

    def test_feedback_and_author_prose_cannot_change_any_professional_feature(self):
        row = copy.deepcopy(self.pack['rows'][0])
        before = features(row, mode='professional')
        row.update({'label': 'a different outcome', 'author_reasoning': 'future', 'later_feedback': 'future',
                    'case_id': 'different_id', 'evidence': {'feedback_sha256': 'different'}})
        self.assertEqual(before, features(row, mode='professional'))
        row['professional_input']['inquiry']['later_feedback'] = 'future'
        with self.assertRaises(ValueError):
            features_for_row(row)

    def test_source_heuristics_are_a_separate_ablation(self):
        row = self.pack['rows'][0]
        facts, complete = features(row, mode='professional_facts'), features(row, mode='professional')
        self.assertLess(len(facts), len(complete))
        self.assertFalse(any(k.startswith('professional.heuristic.') for k in facts))
        self.assertTrue(any(k.startswith('professional.heuristic.') for k in complete))
        self.assertEqual(features(row, False, mode='professional'), features(row, False))

    def test_jia_day_uses_its_own_hidden_instrument_not_hour_jia(self):
        bundle = build_bundle(sample_payload(day='甲午', hour='己巳'))
        self.assertEqual(bundle['roles']['day']['symbol'], '辛')
        self.assertEqual(bundle['roles']['hour']['symbol'], '己')
        self.assertEqual(bundle['roles']['patient']['symbol'], '辛')
        self.assertEqual(bundle['roles']['patient']['palace'], bundle['roles']['day']['palace'])

    def test_cohost_same_symbol_under_multiple_roles_is_not_an_extra_helper(self):
        payload = sample_payload(day='乙巳', hour='乙酉', dun='yang', ju=3, domain='lost_property')
        bundle = build_bundle(payload)
        p = bundle['roles']['day']['palace']
        self.assertEqual(p, bundle['roles']['hour']['palace'])
        self.assertFalse(bundle['independent_cohosts'][p-1]['candidates']['stem:乙'])
        self.assertEqual(bundle['independent_cohosts'][p-1]['unique_selected_identities'], 1)

    def test_proxy_and_heard_news_use_different_patient_bindings(self):
        payload = sample_payload()
        payload['inquiry'] = {'relationship': 'colleague', 'consultation_context': 'event_news'}
        news = build_bundle(payload)
        self.assertEqual(news['roles']['patient']['palace'], news['roles']['day']['palace'])
        payload['inquiry']['consultation_context'] = 'direct_proxy'
        proxy = build_bundle(payload)
        self.assertEqual(proxy['roles']['patient']['palace'], proxy['roles']['month']['palace'])

    def test_true_fake_void_and_striking_are_actual_plane_specific(self):
        payload = sample_payload(hour='甲子', day='甲子', month='丙寅', dun='yang', ju=3)
        bundle = build_bundle(payload)
        self.assertEqual(bundle['nodes'][5]['source_heuristics']['void_classification'], 'true_void')
        payload['calendar']['month_ganzhi'] = '壬申'
        bundle = build_bundle(payload)
        self.assertEqual(bundle['nodes'][5]['source_heuristics']['void_classification'], 'fake_void')
        for node in bundle['nodes']:
            for carrier in node['carriers']:
                if 'earth' in carrier['plane'] and carrier['stem']:
                    self.assertEqual(carrier['six_yi_striking_punishment'], 'not_applicable')

    def test_role_view_keeps_actual_neighborhood_and_carrier(self):
        bundle = build_bundle(sample_payload())
        flat = flatten_bundle(bundle)
        p = bundle['roles']['illness_marker']['palace']
        self.assertEqual(flat['role.illness_marker.earth'], flat[f'node.p{p}.earth'])
        self.assertEqual(flat['role.value_door.heaven'], flat[f'node.p{bundle["roles"]["value_door"]["palace"]}.heaven'])
        edges = {(r['source_role'], r['target_role']): r for r in bundle['role_edges']}
        self.assertEqual(edges['medicine_marker', 'illness_marker']['symbol_element_relation'], '克')
        self.assertEqual(edges['doctor_marker', 'illness_marker']['symbol_element_relation'], '受生')

    def test_bad_school_and_extra_prose_in_calendar_rejected(self):
        payload = sample_payload()
        payload['board']['school_id'] = 'different_flying_school'
        with self.assertRaises(ValueError):
            build_bundle(payload)
        payload = sample_payload()
        payload['calendar']['author_judgment'] = 'future'
        with self.assertRaises(ValueError):
            build_bundle(payload)

    def test_professional_inference_refuses_different_rule_version(self):
        with tempfile.TemporaryDirectory() as tmp:
            model = {'task': self.pack['rows'][0]['task'], 'feature_mode': 'professional',
                     'professional_source_fingerprint': 'different_rule_revision'}
            path = Path(tmp)
            (path / 'model.json').write_text(json.dumps(model))
            with self.assertRaisesRegex(ValueError, 'rules differ'):
                predict(path, self.pack['rows'][0])

    def test_published_field_dictionary_matches_actual_rules_and_reopens(self):
        root = ROOT / 'data/knowledge/probability_research/v2'
        manifest = json.loads((root / 'feature_manifest.json').read_text(encoding='utf8'))
        packed = (root / 'feature_catalog.json.xz').read_bytes()
        self.assertEqual(hashlib.sha256(packed).hexdigest(), manifest['catalogue_compressed_sha256'])
        raw = lzma.decompress(packed)
        self.assertEqual(hashlib.sha256(raw).hexdigest(), manifest['catalogue_uncompressed_sha256'])
        catalogue = json.loads(raw)
        self.assertEqual(len(catalogue['features']), 4606)
        self.assertEqual(manifest['source_fingerprint'], source_fingerprint())
        self.assertEqual(set(r['feature_id'] for r in catalogue['features']), set(flatten_bundle(self.atlas['cases'][0]['bundle'])))

    def test_patient_auxiliary_palaces_reuse_conditional_source_binding(self):
        payload = sample_payload()
        payload['inquiry'] = {'relationship': 'father', 'patient_sex': 'male', 'consultation_context': 'direct_proxy'}
        bundle = build_bundle(payload)
        self.assertIn(6, bundle['patient_binding']['auxiliary_palaces'])
        flat = flatten_bundle(bundle)
        self.assertEqual(flat['patient_aux.p6.selected_candidate'], 1)
        self.assertEqual(flat['patient_aux.p6.primary_star'], bundle['nodes'][5]['star'])
        payload['domain'] = 'lost_property'
        flat = flatten_bundle(build_bundle(payload))
        self.assertEqual(flat['patient_aux.p6.selected_candidate'], 'not_applicable')

    def test_pycharm_launcher_export_works_from_another_working_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / 'export'
            command = [sys.executable, str(ROOT / 'run_professional_training.py'), 'export', '--output', str(output)]
            result = subprocess.run(command, cwd=tmp, capture_output=True, text=True, timeout=120)
            self.assertEqual(result.returncode, 0, result.stderr)
            catalog = json.loads((output / 'data/feature_catalog.json').read_text(encoding='utf8'))
            self.assertEqual(catalog['coverage']['cases'], 194)
            self.assertEqual(catalog['coverage']['additional_source_casts'], 19)
            self.assertTrue((output / 'data/flat_features.tsv').is_file())
            self.assertEqual(json.loads((output / 'run_status.json').read_text())['status'], 'export_complete')


if __name__ == '__main__':
    unittest.main()
