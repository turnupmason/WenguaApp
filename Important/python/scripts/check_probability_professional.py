"""Actual-model serialization checks and an explicitly unlabelled 1080-state sweep."""
import argparse
import copy
import json
import tempfile
from pathlib import Path

from scripts.probability_research import fit, probabilities, save_model, predict
from src.wengua.casting_shenqi import cycle60, hour_ganzhi_from_day, layout_from_explicit_bureau
from src.wengua.probability_dataset_v2 import training_pack
from src.wengua.probability_features_v2 import build_bundle, flatten_bundle


def parameter_sweep():
    count, keys = 0, None
    for dun in ['yin', 'yang']:
        for ju in range(1, 10):
            for hour in cycle60():
                raw = layout_from_explicit_bureau(dun=dun, ju=ju, hour_ganzhi=hour)
                board = {k: raw[k] for k in ['palaces', 'hour_ganzhi', 'value_star', 'value_door', 'school_id']}
                for key, cell in board['palaces'].items():
                    if key == '2':
                        cell['hosted_centre_earth_stem'] = board['palaces']['5']['earth_stem']
                    for k in list(cell):
                        if k not in ['palace', 'door', 'deity', 'earth_stem', 'heaven_stars', 'hosted_centre_earth_stem']:
                            cell.pop(k)
                day = next(d for d in cycle60() if hour_ganzhi_from_day(d[0], hour[1]) == hour)
                payload = {'board': board, 'calendar': {'dun': dun, 'ju': ju, 'year_ganzhi': '甲子',
                           'month_ganzhi': '壬申', 'day_ganzhi': day, 'hour_ganzhi': hour},
                           'inquiry': {'relationship': 'self', 'consultation_context': 'direct_self'}, 'domain': 'health'}
                bundle = build_bundle(payload)
                flat = flatten_bundle(bundle)
                assert len(bundle['nodes']) == 9 and len(bundle['edges']) == 81
                assert bundle['nodes'][4]['star'] is None
                if keys is None:
                    keys = set(flat)
                assert keys == set(flat)
                count += 1
    assert count == 1080
    print(json.dumps({'unlabelled_synthetic_parameter_combinations': count,
                      'independent_historical_training_events_added': 0,
                      'feature_count': len(keys), 'predictive_validation': False}))


def model_check(backend):
    rows = training_pack()['rows']
    group = rows[0]['event_family_id']
    training = [r for r in rows if r['event_family_id'] != group]
    heldout = [r for r in rows if r['event_family_id'] == group]
    classes = sorted({r['label'] for r in rows})
    for mode in ['professional_facts', 'professional']:
        fitted = fit(training, backend, True, 'CPU', 1080, feature_mode=mode)
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp)
            save_model(fitted, output, classes, rows[0]['task'], backend, 1.0, False, feature_mode=mode)
            expected = probabilities(fitted, heldout, True, classes, feature_mode=mode)[0]
            result = predict(output, heldout[0])
            for cls, score in zip(classes, expected):
                assert abs(result['class_scores'][cls] - score) < 1e-10
            modified = copy.deepcopy(heldout[0])
            modified['label'] = 'opposite_future_feedback'
            modified['later_feedback'] = 'opposite_future_feedback'
            assert result == predict(output, modified)
            assert result['user_facing_percentages'] is None
            assert result['production_enabled'] is False
    print(json.dumps({'backend': backend, 'professional_modes': 2, 'serialization_and_leakage_check': 'passed'}))


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--backend', choices=['logistic', 'catboost'], default='logistic')
    p.add_argument('--parameter-sweep', action='store_true')
    args = p.parse_args()
    parameter_sweep() if args.parameter_sweep else model_check(args.backend)


if __name__ == '__main__':
    main()
