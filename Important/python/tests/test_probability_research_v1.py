import copy
import json
import tempfile
import unittest
from pathlib import Path

from src.wengua.probability_research import (
    CONTRACTS, SOURCE_DB, SOURCE_SHA256, cumulative_incidence, digest,
    extract, features, validate_direction,
)
from scripts.probability_research import partition, predict, validate_rows, weights


class ProbabilityResearchTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pack = extract()

    def test_source_inventory_and_scoped_labels(self):
        inv = self.pack['inventory']
        self.assertEqual((inv['case_count'], inv['chapter_count']), (194, 43))
        self.assertEqual(inv['domains']['health'], 12)
        self.assertEqual(inv['domains']['lost_property'], 13)
        self.assertEqual((inv['exported_rows'], inv['exported_event_families']), (12, 11))
        self.assertEqual(inv['label_counts'], {'recovered': 10, 'not_recovered': 2})
        self.assertFalse(inv['production_enabled'])
        validate_rows(self.pack['rows'])
        self.assertEqual(digest(SOURCE_DB.read_bytes()), SOURCE_SHA256)

    def test_source_timing_and_partial_adapter_exclusions(self):
        excluded = {r['case_id']: r['reason'] for r in self.pack['inventory']['excluded']}
        self.assertIn('initial_sixyao', excluded['kaiwu.lost_property.case04'])
        self.assertIn('selected_adapter', excluded['kaiwu.final.license'])

    def test_bag_and_cash_are_different_targets_in_same_family(self):
        rows = [r for r in self.pack['rows'] if r['case_id'] == 'kaiwu.lost_property.case01']
        self.assertEqual({r['label'] for r in rows}, {'recovered', 'not_recovered'})
        self.assertEqual(len({r['event_family_id'] for r in rows}), 1)
        self.assertEqual(weights(rows), [0.5, 0.5])

    def test_feedback_author_and_identity_cannot_enter_features(self):
        row = copy.deepcopy(self.pack['rows'][0])
        before = features(row)
        row.update({'label': 'opposite', 'case_id': 'secret', 'later_feedback': 'future',
                    'author_judgment': 'future', 'event_family_id': 'different'})
        self.assertEqual(features(row), before)
        self.assertFalse(any('p1.' in k for k in features(row, False)))

    def test_unknown_context_and_incomplete_charts_rejected(self):
        row = copy.deepcopy(self.pack['rows'][0])
        row['context']['death_date'] = 'tomorrow'
        with self.assertRaises(ValueError):
            features(row)
        row['context'].pop('death_date')
        row['chart'].pop()
        with self.assertRaises(ValueError):
            features(row)

    def test_unknown_label_and_duplicate_views_rejected(self):
        row = copy.deepcopy(self.pack['rows'][0])
        with self.assertRaises(ValueError):
            validate_rows([row, row])
        row['label'] = None
        with self.assertRaises(ValueError):
            validate_rows([row])

    def test_group_partition_stable_and_disjoint(self):
        groups = [r['event_family_id'] for r in self.pack['rows']]
        a = partition(groups)
        b = partition(reversed(groups))
        self.assertEqual(a, b)
        self.assertEqual(set.union(*a.values()), set(groups))
        self.assertFalse(a['train'] & a['test'] or a['train'] & a['calibration'] or a['test'] & a['calibration'])

    def test_competing_risk_is_unconditional_not_conditional_recovery_time(self):
        result = cumulative_incidence([{'recovery': 0.2, 'death': 0.3, 'survive': 0.5},
                                       {'recovery': 0.4, 'death': 0.2, 'survive': 0.4}])
        self.assertAlmostEqual(result[1]['recovery'], 0.4)
        self.assertAlmostEqual(result[1]['death'], 0.4)
        self.assertAlmostEqual(result[1]['unresolved'], 0.2)
        for row in result:
            self.assertAlmostEqual(sum(row.values()), 1.0)
        with self.assertRaises(ValueError):
            cumulative_incidence([{'recovery': 0.8, 'death': 0.3, 'survive': 0.0}])

    def test_unknown_direction_is_not_a_negative_and_reference_required(self):
        self.assertFalse(validate_direction(None, None))
        self.assertTrue(validate_direction('NE', 'declared home coordinates'))
        with self.assertRaises(ValueError):
            validate_direction('NE', None)

    def test_direction_pipeline_requires_target_time_and_coordinate_reference(self):
        row = copy.deepcopy(self.pack['rows'][0])
        row.update({'task': 'lost.direction', 'label': 'NE'})
        with self.assertRaises(ValueError):
            validate_rows([row])
        row['context'].update({'reference_frame': 'home', 'location_time': 'at_query'})
        validate_rows([row])

    def test_survival_labels_cannot_be_sent_to_plain_classifier(self):
        row = copy.deepcopy(self.pack['rows'][0])
        row.update({'task': 'health.recovery_hazard', 'label': 'recovery'})
        with self.assertRaises(ValueError):
            validate_rows([row])

    def test_contract_does_not_claim_unimplemented_survival_training(self):
        doc = json.loads(CONTRACTS.read_text())
        task = next(t for t in doc['targets'] if t['id'] == 'health.recovery_hazard')
        self.assertIn('not implemented', task['training_support_v1'])
        task = next(t for t in doc['targets'] if t['id'] == 'health.body_site')
        self.assertEqual(task['kind'], 'multi_label')

    def test_portable_binary_inference_and_research_gate(self):
        row = copy.deepcopy(self.pack['rows'][0])
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            model = {'task': row['task'], 'backend': 'logistic',
                     'classes': ['not_recovered', 'recovered'],
                     'feature_vocabulary': {'context.item_kind=document': 0},
                     'coefficients': [[0.5]], 'intercept': [0.0],
                     'temperature': 1, 'reserved_calibration_used': False}
            (path / 'model.json').write_text(json.dumps(model))
            result = predict(path, row)
            self.assertAlmostEqual(result['class_scores']['recovered'], 0.6224593312018546)
            self.assertIsNone(result['research_percentages'])
            self.assertIsNone(result['user_facing_percentages'])
            self.assertFalse(result['production_enabled'])
            row['task'] = 'health.severity'
            with self.assertRaises(ValueError):
                predict(path, row)


if __name__ == '__main__':
    unittest.main()
