"""Local CPU/GPU training. Usage: python -m scripts.probability_research --help."""
from __future__ import annotations

import argparse
import importlib.metadata
import json
from collections import Counter
from pathlib import Path

from src.wengua.probability_research import (
    CONTRACTS, SOURCE_DB, SOURCE_SHA256, digest, extract, features, stable_json, validate_direction,
)


def weights(rows):
    counts = Counter(r['event_family_id'] for r in rows)
    return [1.0 / counts[r['event_family_id']] for r in rows]


def fit(train, backend, include_chart, device, seed, feature_mode='raw', *, filter_constants=None):
    # Imports are local so inventory/core/inference need no training libraries.
    from sklearn.feature_extraction import DictVectorizer
    from sklearn.linear_model import LogisticRegression
    import numpy as np

    vectorizer = DictVectorizer(sparse=False)
    x = vectorizer.fit_transform([features(r, include_chart, mode=feature_mode) for r in train])
    y = [r['label'] for r in train]
    if len(set(y)) < 2:
        raise ValueError('Training partition must contain at least two observed classes')
    if filter_constants is None:
        filter_constants = feature_mode != 'raw'
    if filter_constants:
        # The audit retains every professional field. A constant in THIS
        # training partition has no learnable contrast; do not fit thousands
        # of duplicate intercepts or inspect the heldout partition to select it.
        keep = np.ptp(x, axis=0) > 0
        if not keep.any():
            if include_chart:
                raise ValueError('No varying chart predictors in the training partition')
            from sklearn.dummy import DummyClassifier
            prior = DummyClassifier(strategy='prior').fit(x, y, sample_weight=np.asarray(weights(train)))
            return vectorizer, prior
        vectorizer.restrict(keep)
        x = x[:, keep]
    if backend == 'logistic':
        if device != 'CPU':
            raise ValueError('Logistic baseline uses CPU; choose catboost for GPU')
        model = LogisticRegression(C=0.1, max_iter=1000, random_state=seed)
    else:
        from catboost import CatBoostClassifier
        model = CatBoostClassifier(iterations=150, depth=3, learning_rate=0.05,
                                   l2_leaf_reg=10, random_seed=seed, task_type=device,
                                   loss_function='Logloss' if len(set(y)) == 2 else 'MultiClass',
                                   verbose=False, allow_writing_files=False, thread_count=4,
                                   **({'devices': '0'} if device == 'GPU' else {}))
    model.fit(x, y, sample_weight=np.asarray(weights(train)))
    return vectorizer, model


def probabilities(fitted, rows, include_chart, classes, feature_mode='raw'):
    import numpy as np
    vectorizer, model = fitted
    raw = model.predict_proba(vectorizer.transform([features(r, include_chart, mode=feature_mode) for r in rows]))
    aligned = np.zeros((len(rows), len(classes)))
    for i, cls in enumerate(model.classes_):
        aligned[:, classes.index(str(cls))] = raw[:, i]
    return aligned


def temperature_scale(probs, temperature):
    import numpy as np
    z = np.log(np.clip(probs, 1e-12, 1)) / temperature
    z -= z.max(axis=1, keepdims=True)
    exp = np.exp(z)
    return exp / exp.sum(axis=1, keepdims=True)


def metrics(rows, probs, classes):
    import numpy as np
    from sklearn.metrics import log_loss
    y = np.array([classes.index(r['label']) for r in rows])
    onehot = np.eye(len(classes))[y]
    w = np.asarray(weights(rows))
    bins = []
    for cls_index, cls in enumerate(classes):
        for lo, hi in [(0, .2), (.2, .4), (.4, .6), (.6, .8), (.8, 1.0000001)]:
            mask = (probs[:, cls_index] >= lo) & (probs[:, cls_index] < hi)
            if mask.any():
                bins.append({'class': cls, 'range': [lo, min(1, hi)], 'rows': int(mask.sum()),
                             'mean_score': float(np.average(probs[mask, cls_index], weights=w[mask])),
                             'observed_fraction': float(np.average(y[mask] == cls_index, weights=w[mask]))})
    return {'rows': len(rows), 'event_families': len({r['event_family_id'] for r in rows}),
            'log_loss': float(log_loss(y, probs, labels=list(range(len(classes))), sample_weight=w)),
            'brier_multiclass_sum': float(np.average(((probs - onehot) ** 2).sum(axis=1), weights=w)),
            'accuracy': float(np.average(probs.argmax(axis=1) == y, weights=w)),
            'reliability_bins': bins}


def validate_rows(rows):
    if not rows or len({r['task'] for r in rows}) != 1:
        raise ValueError('Train one explicitly defined target per run')
    if rows[0]['task'] in ('health.recovery_hazard', 'lost.recovery_hazard'):
        raise ValueError('Censoring-aware time-to-event fitting is not implemented; do not treat it as ordinary classification')
    if rows[0]['task'] == 'health.body_site':
        raise ValueError('Define a separate task ID for one anatomical region, with observed positive/negative labels')
    contract = next((t for t in json.loads(CONTRACTS.read_text(encoding='utf8'))['targets']
                     if t['id'] == rows[0]['task']), None)
    if contract and 'classes' in contract:
        observed = {r.get('label') for r in rows}
        if observed != set(contract['classes']):
            raise ValueError('Declared outcome classes must all be observed; absent categories cannot be assigned zero probability')
    seen = set()
    for row in rows:
        if not row.get('available_before_prediction'):
            raise ValueError('Missing explicit pre-prediction chart/context declaration')
        if row.get('label') is None or not isinstance(row['label'], str):
            raise ValueError('Unknown outcomes must be excluded, never mapped to failure')
        if row['task'] == 'lost.direction':
            validate_direction(row['label'], row.get('context', {}).get('reference_frame'))
        if row['task'] == 'health.severity' and row['label'] not in ('mild', 'moderate', 'severe', 'critical'):
            raise ValueError('Severity requires a specified ordered grade, not a symbolic score')
        if not row.get('evidence') or not row['evidence'].get('feedback_sha256'):
            raise ValueError('An outcome must have an evidence receipt')
        key = row['event_family_id'], row['task'], row['target_item']
        if key in seen:
            raise ValueError('Repeated views of the same event/item must not become extra samples')
        seen.add(key)
        features(row)


def partition(groups):
    """Fixed group-only hash assignment, independent of labels and chart features."""
    result = {'train': set(), 'calibration': set(), 'test': set()}
    for group in groups:
        bucket = int(digest(('qimennet-probability-v1:' + group).encode())[:8], 16) % 10
        result['train' if bucket < 6 else 'calibration' if bucket < 8 else 'test'].add(group)
    return result


def train(rows, output, backend='logistic', device='CPU', seed=1080, *, feature_mode='raw', progress=None):
    import numpy as np
    validate_rows(rows)
    if feature_mode not in ('raw', 'professional'):
        raise ValueError('Choose raw or complete professional ablations')
    if feature_mode == 'professional':
        from src.wengua.probability_features_v2 import source_fingerprint
        initial_rule_fingerprint = source_fingerprint()
        for row in rows:
            features(row, mode='professional')
    output.mkdir(parents=True, exist_ok=True)
    classes = sorted({r['label'] for r in rows})
    if len(classes) < 2:
        raise ValueError('At least two observed classes are required')
    groups = sorted({r['event_family_id'] for r in rows})
    class_groups = [len({r['event_family_id'] for r in rows if r['label'] == c}) for c in classes]
    if min(class_groups) < 2:
        raise ValueError('A class occurs in fewer than two event families; cannot assess unseen events')
    # Small book cohorts get grouped leave-one-event-out research scores only.
    # Larger cohorts reserve an untouched test and a separate calibration set.
    holdout = len(groups) >= 60 and min(class_groups) >= 10
    predictions, report = [], {'task': rows[0]['task'], 'backend': backend, 'device': device,
                               'seed': seed, 'classes': classes, 'rows': len(rows),
                               'event_families': len(groups), 'production_enabled': False,
                               'calibration_status': 'not_fitted_small_cohort',
                               'protocol': 'group_leave_one_event_out',
                               'cohort_sha256': digest(stable_json(rows).encode()),
                               'external_validation': False, 'metrics': {},
                               'limitations': ['Book selection bias; not a prospective cohort.',
                                               'Last-report recovery has unequal/unknown follow-up.',
                                               'Context baseline is item kind, not full real-world background.',
                                               'Historical group holdout is not a chronological or prospective validation.',
                                               'Software tests do not validate divination or clinical prediction.']}
    splits = partition(groups) if holdout else None
    if holdout:
        subsets = {k: [r for r in rows if r['event_family_id'] in v] for k, v in splits.items()}
        for name, subset in subsets.items():
            if {r['label'] for r in subset} != set(classes):
                raise ValueError(f'Fixed {name} split misses classes; collect more data, do not reshuffle by test result')
        report.update({'protocol': 'fixed_group_train_calibration_test',
                       'partitions': {k: sorted(v) for k, v in splits.items()},
                       'calibration_status': 'temperature_on_reserved_calibration_only'})
    else:
        report['partitions'] = {'leave_one_event_out': groups}
    names = ['prior', 'context', 'chart'] + (['professional_facts', 'professional'] if feature_mode == 'professional' else [])
    deployment = names[-1]
    report['feature_mode'] = feature_mode
    report['professional_preprocessing'] = 'training_partition_only_zero_variance_filter' if feature_mode == 'professional' else 'original_v1_vectorizer'
    report['deployed_research_model'] = deployment
    ablation_predictions = {}
    for name in names:
        active_mode = name if name in ('professional_facts', 'professional') else 'raw'
        if progress:
            progress(f'{name}: start, {len(groups)} independent events')
        scores = np.zeros((len(rows), len(classes)))
        temperature = 1.0
        folds = [(subsets['train'], subsets['test'])] if holdout else [
            ([r for r in rows if r['event_family_id'] != g],
             [r for r in rows if r['event_family_id'] == g]) for g in groups]
        index = {id(r): i for i, r in enumerate(rows)}
        for fold_index, (train_rows, test_rows) in enumerate(folds, 1):
            if progress:
                progress(f'{name}: fold {fold_index}/{len(folds)}; train={len(train_rows)}, test={len(test_rows)}')
            if name == 'prior':
                counts = {c: sum(w for r, w in zip(train_rows, weights(train_rows)) if r['label'] == c)
                          for c in classes}
                prior = np.array([counts[c] + 1 for c in classes])
                raw = np.tile(prior / prior.sum(), (len(test_rows), 1))
            else:
                include_chart = name != 'context'
                fitted = fit(train_rows, backend, include_chart, device, seed, active_mode,
                             filter_constants=feature_mode == 'professional')
                raw = probabilities(fitted, test_rows, include_chart, classes, active_mode)
                if holdout:
                    from scipy.optimize import minimize_scalar
                    cal = probabilities(fitted, subsets['calibration'], include_chart, classes, active_mode)
                    objective = lambda t: metrics(subsets['calibration'], temperature_scale(cal, t), classes)['log_loss']
                    solution = minimize_scalar(objective, bounds=(0.25, 10), method='bounded')
                    temperature = float(solution.x)
                    raw = temperature_scale(raw, temperature)
            for row, p in zip(test_rows, raw):
                scores[index[id(row)]] = p
        evaluated = subsets['test'] if holdout else rows
        report['metrics'][name] = metrics(evaluated, np.array([scores[index[id(r)]] for r in evaluated]), classes)
        ablation_predictions[name] = [{'case_id': row['case_id'], 'event_family_id': row['event_family_id'],
                                      'target_item': row['target_item'], 'label': row['label'],
                                      'class_scores': dict(zip(classes, scores[index[id(row)]].tolist()))} for row in evaluated]
        if name == deployment:
            for row in evaluated:
                p = scores[index[id(row)]].tolist()
                predictions.append({'case_id': row['case_id'], 'event_family_id': row['event_family_id'],
                                    'target_item': row['target_item'], 'observed_label': row['label'],
                                    'class_scores': dict(zip(classes, p)),
                                    'research_percentages': dict(zip(classes, [100 * x for x in p])) if holdout else None,
                                    'user_facing_percentages': None})
            deployment_training = subsets['train'] if holdout else rows
            final = fitted if holdout else fit(deployment_training, backend, True, device, seed, active_mode,
                                              filter_constants=feature_mode == 'professional')
            if feature_mode == 'professional' and source_fingerprint() != initial_rule_fingerprint:
                raise ValueError('Professional source files changed during training; preserve this run and restart from a fixed revision')
            save_model(final, output, classes, rows[0]['task'], backend, temperature, holdout, feature_mode=active_mode)
            vectorizer, estimator = final
            importance = (abs(estimator.coef_).mean(axis=0).tolist() if backend == 'logistic'
                          else estimator.get_feature_importance().tolist())
            names_in_order = vectorizer.get_feature_names_out().tolist()
            write_json(output / 'feature_importance.json', {
                'meaning': 'training_model_diagnostic_not_causality_or_independent_predictive_evidence',
                'feature_mode': active_mode,
                'features': sorted([{'feature': k, 'importance': float(v)} for k, v in zip(names_in_order, importance)],
                                   key=lambda r: (-r['importance'], r['feature']))})
    report['descriptive_chart_brier_lower_than_context'] = report['metrics']['chart']['brier_multiclass_sum'] < report['metrics']['context']['brier_multiclass_sum']
    report['versions'] = {p: importlib.metadata.version(p) for p in
                          ['numpy', 'scikit-learn', 'scipy'] + (['catboost'] if backend == 'catboost' else [])}
    write_json(output / 'evaluation.json', report)
    write_json(output / 'heldout_predictions.json', predictions)
    if feature_mode == 'professional':
        from src.wengua.probability_features_v2 import source_fingerprint
        report['professional_source_fingerprint'] = source_fingerprint()
        report['professional_inputs_from_outcomes'] = False
        report['fixed_user_heuristics_separately_ablated'] = True
        write_json(output / 'ablation_predictions.json', ablation_predictions)
        write_json(output / 'evaluation.json', report)
    return report


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf8')


def save_model(fitted, output, classes, task, backend, temperature, calibrated, *, feature_mode='raw'):
    vectorizer, model = fitted
    doc = {'version': 1, 'task': task, 'backend': backend, 'classes': classes,
           'feature_vocabulary': vectorizer.vocabulary_, 'temperature': temperature,
           'reserved_calibration_used': calibrated, 'production_enabled': False,
           'feature_mode': feature_mode}
    if feature_mode != 'raw':
        from src.wengua.probability_features_v2 import source_fingerprint
        doc['professional_source_fingerprint'] = source_fingerprint()
    if backend == 'logistic':
        doc.update({'coefficients': model.coef_.tolist(), 'intercept': model.intercept_.tolist()})
    else:
        model.save_model(str(output / 'model.cbm'))
        doc['model_sha256'] = digest((output / 'model.cbm').read_bytes())
    write_json(output / 'model.json', doc)


def predict(path, row):
    """Portable logistic inference; CatBoost inference uses its local runtime."""
    import math
    model = json.loads((path / 'model.json').read_text(encoding='utf8'))
    if row['task'] != model['task']:
        raise ValueError('Model target mismatch')
    mode = model.get('feature_mode', 'raw')
    if mode != 'raw':
        from src.wengua.probability_features_v2 import source_fingerprint
        if model['professional_source_fingerprint'] != source_fingerprint():
            raise ValueError('Professional feature rules differ from the training version; use its recorded source revision')
    x = [0.0] * len(model['feature_vocabulary'])
    for key, value in features(row, mode=mode).items():
        encoded = key + '=' + value if isinstance(value, str) else key
        index = model['feature_vocabulary'].get(encoded)
        if index is not None:
            x[index] = 1.0 if isinstance(value, str) else float(value)
    if model['backend'] == 'logistic':
        z = [(sum(a * b for a, b in zip(coef, x)) + b) / model['temperature']
             for coef, b in zip(model['coefficients'], model['intercept'])]
        if len(z) == 1:
            p = 1 / (1 + math.exp(-max(-700, min(700, z[0]))))
            probs = [1 - p, p]
        else:
            exps = [math.exp(v - max(z)) for v in z]
            probs = [v / sum(exps) for v in exps]
    else:
        from catboost import CatBoostClassifier
        if digest((path / 'model.cbm').read_bytes()) != model['model_sha256']:
            raise ValueError('Model SHA256 mismatch')
        cb = CatBoostClassifier().load_model(str(path / 'model.cbm'))
        raw = cb.predict_proba([x])[0]
        exps = [math.exp(math.log(max(1e-12, p)) / model['temperature']) for p in raw]
        probs = [p / sum(exps) for p in exps]
    return {'task': row['task'], 'class_scores': dict(zip(model['classes'], probs)),
            'research_percentages': dict(zip(model['classes'], [100 * p for p in probs])) if model['reserved_calibration_used'] else None,
            'user_facing_percentages': None, 'production_enabled': False,
            'note': 'Exploratory historical-book model; no prospective or clinical validation.'}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='command', required=True)
    export = sub.add_parser('export')
    export.add_argument('--db', type=Path, default=SOURCE_DB)
    export.add_argument('--output', type=Path, default=Path('local/probability_v1/data'))
    training = sub.add_parser('train')
    training.add_argument('--input', type=Path, default=Path('local/probability_v1/data/rows.jsonl'))
    training.add_argument('--output', type=Path, default=Path('local/probability_v1/logistic'))
    training.add_argument('--backend', choices=['logistic', 'catboost'], default='logistic')
    training.add_argument('--device', choices=['CPU', 'GPU'], default='CPU')
    training.add_argument('--features', choices=['raw', 'professional'], default='raw')
    training.add_argument('--progress', action='store_true')
    inference = sub.add_parser('predict')
    inference.add_argument('--model', type=Path, required=True)
    inference.add_argument('--input', type=Path, required=True, help='One input row as JSON')
    args = p.parse_args()
    if args.command == 'export':
        if args.output.exists():
            raise SystemExit('Output already exists; use a new version directory to preserve earlier runs')
        pack = extract(args.db, SOURCE_SHA256)
        write_json(args.output / 'inventory.json', pack['inventory'])
        (args.output / 'rows.jsonl').write_text('\n'.join(stable_json(r) for r in pack['rows']) + '\n', encoding='utf8')
        print(json.dumps(pack['inventory'], ensure_ascii=False, indent=2))
    elif args.command == 'train':
        if args.output.exists():
            raise SystemExit('Output already exists; use a new version directory to preserve earlier runs')
        rows = [json.loads(line) for line in args.input.read_text(encoding='utf8').splitlines() if line.strip()]
        args.output.mkdir(parents=True)
        report = train(rows, args.output, args.backend, args.device, feature_mode=args.features,
                       progress=(lambda message: print(message, flush=True)) if args.progress else None)
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(predict(args.model, json.loads(args.input.read_text(encoding='utf8'))), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
