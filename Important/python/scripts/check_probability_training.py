"""Optional integration verification, executed by the local-model CI workflow.

Uses real source reports; it checks extraction/split/inference consistency, not
whether divination predicts events. No medical or location labels are invented.
"""
import argparse
import copy
import json
import tempfile
from pathlib import Path

from scripts.probability_research import fit, predict, probabilities, save_model, train
from src.wengua.probability_research import extract


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--backend', choices=['logistic', 'catboost'], default='logistic')
    args = p.parse_args()
    rows = extract()['rows']
    classes = sorted({r['label'] for r in rows})
    heldout_group = rows[0]['event_family_id']
    training = [r for r in rows if r['event_family_id'] != heldout_group]
    heldout = [r for r in rows if r['event_family_id'] == heldout_group]
    fitted = fit(training, args.backend, True, 'CPU', 1080)
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp)
        save_model(fitted, path, classes, rows[0]['task'], args.backend, 1.0, False)
        direct = probabilities(fitted, heldout, True, classes)[0]
        portable = predict(path, heldout[0])
        for cls, expected in zip(classes, direct):
            assert abs(portable['class_scores'][cls] - expected) < 1e-10
        # Changing future feedback/label cannot change a fixed fitted model's inputs.
        changed = copy.deepcopy(heldout[0])
        changed['label'] = 'changed future label'
        changed['later_feedback'] = 'changed future feedback'
        assert predict(path, changed) == portable
        # No category seen only in the heldout chart may enter the fitted vocabulary.
        changed['chart'][0]['door_stems'] = '甲甲甲'
        assert not any('甲甲甲' in k for k in fitted[0].vocabulary_)
    with tempfile.TemporaryDirectory() as tmp:
        report = train(rows, Path(tmp), args.backend)
        assert report['event_families'] == 11
        assert report['calibration_status'] == 'not_fitted_small_cohort'
        predictions = json.loads((Path(tmp) / 'heldout_predictions.json').read_text())
        assert len(predictions) == len(rows)
        assert all(r['research_percentages'] is None and r['user_facing_percentages'] is None for r in predictions)
    if args.backend == 'logistic':
        # Explicit SOFTWARE FIXTURE, never exported into the source cohort. This
        # checks the larger-cohort multiclass/calibration path and test-label
        # independence; its metrics have no historical or predictive meaning.
        fixtures = []
        for i in range(180):
            r = copy.deepcopy(rows[i % len(rows)])
            r.update({'case_id': f'synthetic_software_fixture.{i}',
                      'event_family_id': f'synthetic_software_fixture.{i}',
                      'task': 'synthetic_software_fixture.multiclass',
                      'label': ['A', 'B', 'C'][i % 3], 'target_item': 'synthetic_fixture'})
            r['evidence'] = {'feedback_sha256': 'synthetic_fixture_not_a_book_observation'}
            fixtures.append(r)
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            report = train(fixtures, Path(a))
            assert report['calibration_status'] == 'temperature_on_reserved_calibration_only'
            changed = copy.deepcopy(fixtures)
            test_groups = set(report['partitions']['test'])
            for r in changed:
                if r['event_family_id'] in test_groups:
                    r['label'] = {'A': 'B', 'B': 'C', 'C': 'A'}[r['label']]
            train(changed, Path(b))
            # Both coefficients and calibration temperature must be unchanged.
            assert (Path(a) / 'model.json').read_bytes() == (Path(b) / 'model.json').read_bytes()
            model = json.loads((Path(a) / 'model.json').read_text())
            portable = predict(Path(a), fixtures[0])
            assert abs(sum(portable['class_scores'].values()) - 1) < 1e-12
            assert model['production_enabled'] is False
    print(json.dumps({'backend': args.backend, 'real_source_rows': len(rows), 'event_families': 11,
                      'portable_inference_and_group_oof': 'passed', 'clinical_validation': False}))


if __name__ == '__main__':
    main()
