"""All source-professional features, five ablations, CPU/GPU and PyCharm runner."""
from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from scripts.probability_research import predict, train, write_json
from src.wengua.probability_dataset_v2 import training_pack
from src.wengua.probability_features_v2 import SOURCES, VERSION, flatten_bundle, source_fingerprint
from src.wengua.probability_research import ROOT, stable_json


def log(message):
    print(f'[{datetime.now().strftime("%H:%M:%S")}] {message}', flush=True)


def feature_group(name):
    if name.startswith('heuristic.'):
        return 'fixed_user_heuristics'
    if name.startswith('cohost.'):
        return 'independent_cohost_identity'
    if name.startswith('role_context.'):
        return 'pre_question_role_context'
    if name.startswith('edge.'):
        return 'directed_palace_relations'
    if name.startswith(('role.', 'role_edge.', 'patient_aux.')):
        return 'conditional_signifiers'
    if name.startswith('pillar_relation.'):
        return 'stem_branch_time_relations'
    if '.literal_candidate.' in name or '.ordered81.' in name:
        return 'source_pattern_primitives'
    if '.lifecycle.' in name or '.has_' in name or '.hidden_' in name:
        return 'stem_lifecycle_and_hidden_jia'
    if name.startswith('calendar.'):
        return 'explicit_calendar'
    if name.startswith('macro.'):
        return 'macro_conditions'
    if name.startswith('unresolved.'):
        return 'explicit_unknown_rules'
    return 'palace_residents_season_void_horse'


def feature_sources(name):
    if name.startswith('heuristic.'):
        groups = ['heuristic', 'anatomy'] if '.anatomy.' in name else ['heuristic']
    elif name.startswith(('role.', 'role_edge.', 'role_context.', 'cohost.', 'patient_aux.')):
        groups = ['roles', 'palace', 'season', 'lifecycle']
    elif name.startswith(('edge.', 'pillar_relation.')):
        groups = ['palace', 'relations']
    elif name.startswith('macro.'):
        groups = ['macro']
    elif '.literal_candidate.' in name:
        groups = ['patterns']
    elif '.ordered81.' in name:
        return ['src/wengua/health_81_excel_catalog_vnext.py', 'data/knowledge/health_81_excel_20261025/81_pairs.tsv']
    else:
        groups = ['palace', 'season', 'lifecycle', 'relations']
    return sorted({p for group in groups for p in SOURCES[group]})


def export(output):
    log('Read-only archive audit: all 194 events; labels remain separate from inputs')
    pack = training_pack()
    facts = pack['atlas']
    write_json(output / 'inventory.json', pack['inventory'])
    (output / 'rows.jsonl').write_text('\n'.join(stable_json(r) for r in pack['rows']) + '\n', encoding='utf8')
    with (output / 'case_features.jsonl').open('w', encoding='utf8') as f:
        for row in facts['cases'] + facts['additional_casts']:
            f.write(stable_json(row) + '\n')
    catalog, flat_rows, coverage, inapplicable = {}, [], Counter(), Counter()
    for record in facts['cases']:
        flat = flatten_bundle(record['bundle'])
        flat_rows.append({'case_id': record['case_id'], **flat})
        for key, value in flat.items():
            coverage[key] += value not in ('__unknown__', 'not_applicable')
            inapplicable[key] += value == 'not_applicable'
            catalog.setdefault(key, {'feature_id': key, 'group': feature_group(key),
                                     'missing': '__unknown__', 'inapplicable': 'not_applicable',
                                     'input_only': True, 'source_paths': feature_sources(key),
                                     'predictive_value_validated': False})
    with (output / 'flat_features.tsv').open('w', encoding='utf8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['case_id'] + sorted(catalog), delimiter='\t')
        writer.writeheader()
        writer.writerows(flat_rows)
    for key in catalog:
        catalog[key]['known_applicable_primary_cases'] = coverage[key]
        catalog[key]['not_applicable_primary_cases'] = inapplicable[key]
        catalog[key]['unknown_primary_cases'] = len(facts['cases']) - coverage[key] - inapplicable[key]
    feature_summary = {'schema': VERSION, 'feature_count_per_primary_record': len(catalog),
                       'groups': dict(Counter(r['group'] for r in catalog.values())),
                       'rules_fingerprint': source_fingerprint(), 'source_files': facts['source_manifest'],
                       'source_groups': SOURCES, 'features': [catalog[k] for k in sorted(catalog)],
                       'training_rows': len(pack['rows']), 'coverage': facts['coverage'],
                       'not_a_v11_excel_schema_migration': True}
    write_json(output / 'feature_catalog.json', feature_summary)
    write_json(output / 'case_quality.json', [{k: v for k, v in r.items() if k in ('case_id', 'event_family_id', 'domain_id', 'source_receipt', 'feature_count', 'known_feature_count', 'not_applicable_feature_count')} for r in facts['cases']])
    log(f'Export complete: {len(facts["cases"])} primary records, {len(facts["additional_casts"])} additional casts, {len(catalog)} professional fields')
    log(f'Trainable pilot: {len(pack["rows"])} item targets / {pack["inventory"]["exported_event_families"]} independent events')
    return pack, feature_summary


def run(output, backend='both', device='GPU', *, export_only=False):
    if output.exists():
        raise ValueError('Output directory exists; choose a new run to preserve previous results')
    output.mkdir(parents=True)
    started = time.perf_counter()
    write_json(output / 'run_status.json', {'status': 'started', 'backend': backend, 'device': device,
                                          'python_executable': sys.executable, 'production_enabled': False})
    try:
        data_dir = output / 'data'
        data_dir.mkdir()
        pack, catalog = export(data_dir)
        if export_only:
            write_json(output / 'run_status.json', {'status': 'export_complete', 'training_executed': False})
            return {'output': str(output), 'coverage': catalog['coverage']}
        if backend in ('catboost', 'both') and device == 'GPU':
            from catboost.utils import get_gpu_device_count
            count = get_gpu_device_count()
            if count < 1:
                raise ValueError('Requested GPU is not available; use --device CPU explicitly')
            log(f'CatBoost GPU devices: {count}; device 0 selected')
        elif backend == 'logistic' and device != 'CPU':
            raise ValueError('Logistic baseline requires --device CPU')
        else:
            log('CPU training selected')
        reports, replays = {}, {}
        for active in (['logistic', 'catboost'] if backend == 'both' else [backend]):
            active_device = 'CPU' if active == 'logistic' else device
            destination = output / 'models' / active / 'lost-recovery'
            reports[active] = train(pack['rows'], destination, active, active_device,
                                   feature_mode='professional', progress=lambda message, active=active, active_device=active_device: log(active + '/' + active_device + ' ' + message))
            replays[active] = predict(destination, pack['rows'][0])
        with (output / 'summary.tsv').open('w', encoding='utf8', newline='') as f:
            writer = csv.writer(f, delimiter='\t')
            writer.writerow(['backend', 'model', 'log_loss', 'brier_multiclass_sum', 'event_weighted_accuracy'])
            for active, report in reports.items():
                for name, m in report['metrics'].items():
                    writer.writerow([active, name, m['log_loss'], m['brier_multiclass_sum'], m['accuracy']])
                    log(f'{active}/{name}: Brier={m["brier_multiclass_sum"]:.6f}; logloss={m["log_loss"]:.6f}; accuracy={m["accuracy"]:.4f}')
        tasks = [{'task': report['task'], 'status': 'trained_experimental_book_report_only', 'events': report['event_families']}]
        tasks.extend({'task': t, 'status': ('not_trained_missing_event_time_labels_and_survival_fitter' if t.endswith('_hazard') else 'not_trained_missing_qualified_task_labels'),
                      'features_connected': True, 'probability_available': False} for t in pack['inventory']['unlabelled_tasks'])
        write_json(output / 'task_status.json', tasks)
        # Actual successful inference on an exported input verifies the complete
        # path. This is explicitly a training-item replay, never a new forecast.
        write_json(output / 'training_item_inference_smoke.json', {
            'purpose': 'software_training_item_replay_not_independent_prediction',
            'results_by_backend': replays})
        write_json(output / 'run_status.json', {'status': 'complete', 'backend': backend, 'device': device,
                                              'elapsed_seconds': time.perf_counter()-started,
                                              'production_enabled': False, 'research_probability_calibrated': False})
        log('Complete. Raw chart, source facts and fixed user heuristics were evaluated separately on the SAME events.')
        log('Small book cohort: scores are not calibrated user probabilities. Other task training status is explicit in task_status.json.')
        return reports
    except Exception as error:
        write_json(output / 'run_status.json', {'status': 'failed', 'error_type': type(error).__name__,
                                              'error': str(error), 'elapsed_seconds': time.perf_counter()-started})
        raise


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['run', 'export'], nargs='?', default='run')
    parser.add_argument('--backend', choices=['catboost', 'logistic', 'both'], default='both')
    parser.add_argument('--device', choices=['GPU', 'CPU'], default='GPU')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args(argv)
    if args.command == 'run' and importlib.util.find_spec('sklearn') is None:
        parser.error('Select your project virtualenv and install requirements-probability.txt')
    output = args.output or ROOT / 'local/probability_v2' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S_%fZ')
    log('Python: ' + sys.executable)
    log('Output: ' + str(output.resolve()))
    run(output, args.backend, args.device, export_only=args.command == 'export')


if __name__ == '__main__':
    main()
