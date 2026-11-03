"""Read-only historical-data export and typed probability contracts.

Independent research only: no changes to the App's frozen symbolic engines.
Book reports are observations of what the book reports, not medical evidence.
This module intentionally has no machine-learning dependencies.
"""
from __future__ import annotations

import hashlib
import json
import math
import sqlite3
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE_DB = ROOT / 'archives/sqlite/WenguaApp_双书194案例_V391纯断词十二长生_完整研究库.sqlite3'
SOURCE_SHA256 = '21362e6f0266c03dcdc4a7ef35f45954ba274ae6458de0ba341132abca7d0405'
REGISTRY = ROOT / 'data/knowledge/probability_research/v1/lost_report_labels.json'
CONTRACTS = ROOT / 'data/knowledge/probability_research/v1/targets.json'
OUTER = (1, 2, 3, 4, 6, 7, 8, 9)
CONTEXT_KEYS = frozenset({'item_kind', 'reference_frame', 'subject_species', 'question_kind',
                          'age_band', 'sex', 'known_diagnosis_code', 'treatment_status',
                          'last_seen_environment', 'search_duration_band', 'item_movable',
                          'location_time'})


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def stable_json(value) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def features(row: dict, include_chart: bool = True, *, mode: str = 'raw') -> dict:
    """Only explicit pre-question context and literal board symbols are inputs.

    No free prose, IDs, labels, author verdicts, feedback or source-book identity.
    Literal door/star stem strings retain their source layer names; they are not
    silently reinterpreted as verified heaven/earth stems or derived host rules.
    """
    if mode not in ('raw', 'professional_facts', 'professional'):
        raise ValueError('Unknown feature mode')
    result = {'task': row['task']}
    context = row.get('context', {})
    if row['task'] == 'lost.direction':
        if not context.get('reference_frame') or context.get('location_time') not in ('at_query', 'at_recovery'):
            raise ValueError('Direction requires a predeclared reference and location target time')
    if set(context) - CONTEXT_KEYS:
        raise ValueError('Non-allowlisted context field')
    for key, value in context.items():
        if not isinstance(value, str) or not value:
            raise ValueError('Context values must be explicit nonempty categories')
        result['context.' + key] = value
    if include_chart:
        cells = row.get('chart', [])
        if len(cells) != 9 or {x['palace'] for x in cells} != set(range(1, 10)):
            raise ValueError('A complete literal nine-palace source chart is required')
        for cell in cells:
            palace = cell['palace']
            for field, alphabet in (
                ('deity', '符蛇阴合虎武地天常勾陈朱雀'),
                ('door', '休生伤杜景死惊开'),
                ('star', '蓬任冲辅英芮柱心禽'),
                ('door_stems', '甲乙丙丁戊己庚辛壬癸'),
                ('star_stems', '甲乙丙丁戊己庚辛壬癸'),
            ):
                value = cell.get(field, '')
                if any(ch not in alphabet for ch in value):
                    raise ValueError('Unexpected free text in a chart feature')
                result[f'p{palace}.{field}'] = value or '__missing__'
        if mode != 'raw':
            from .probability_features_v2 import features_for_row
            result.update({'professional.' + k: v for k, v in features_for_row(
                row, include_heuristics=mode == 'professional').items()})
    return result


def extract(db_path: Path = SOURCE_DB, expected_sha: str = SOURCE_SHA256) -> dict:
    """Inventory all source events; export only manually scoped observed labels."""
    if digest(db_path.read_bytes()) != expected_sha:
        raise ValueError('Source database SHA256 mismatch; do not silently change cohorts')
    db = sqlite3.connect(db_path.resolve().as_uri() + '?mode=ro', uri=True)
    db.row_factory = sqlite3.Row
    try:
        if db.execute('pragma integrity_check').fetchone()[0] != 'ok':
            raise ValueError('Source database integrity failure')
        cases = {r['case_id']: dict(r) for r in db.execute('select * from cases')}
        inventory = {'source_sha256': expected_sha, 'case_count': len(cases),
                     'event_family_count': len({r['event_family_id'] for r in cases.values()}),
                     'chapter_count': db.execute('select count(*) from sections').fetchone()[0],
                     'domains': dict(sorted(Counter(r['domain_id'] for r in cases.values()).items())),
                     'external_validation': False, 'production_enabled': False}
        rows, excluded = [], []
        registry = json.loads(REGISTRY.read_text(encoding='utf8'))
        for label in registry['labels']:
            case = cases[label['case_id']]
            if label.get('exclude_reason'):
                excluded.append({'case_id': case['case_id'], 'target_item': label['target_item'],
                                 'reason': label['exclude_reason']})
                continue
            cells = list(db.execute('select * from historical_chart_cells where case_id=? order by palace',
                                    (case['case_id'],)))
            if len(cells) != 9:
                excluded.append({'case_id': case['case_id'], 'target_item': label['target_item'],
                                 'reason': 'no_complete_primary_literal_chart_in_selected_adapter'})
                continue
            section = db.execute('select section_key,sha256 from sections where section_id=?',
                                 (case['section_id'],)).fetchone()
            feedback = case['later_feedback'] or ''
            # Pin each interpretation to the exact feedback bytes that were read.
            if digest(feedback.encode()) != label['feedback_sha256']:
                raise ValueError('Label evidence changed: ' + case['case_id'])
            chart = []
            for c in cells:
                door, star = c['door_position_raw'] or '', c['star_position_raw'] or ''
                chart.append({'palace': c['palace'],
                              'deity': ''.join(ch for ch in (c['deity_raw'] or '') if ch in '符蛇阴合虎武地天常勾陈朱雀'),
                              'door': ''.join(ch for ch in door if ch in '休生伤杜景死惊开'),
                              'star': ''.join(ch for ch in star if ch in '蓬任冲辅英芮柱心禽'),
                              'door_stems': ''.join(ch for ch in door if ch in '甲乙丙丁戊己庚辛壬癸'),
                              'star_stems': ''.join(ch for ch in star if ch in '甲乙丙丁戊己庚辛壬癸')})
            row = {'schema_version': 1, 'case_id': case['case_id'],
                   'event_family_id': case['event_family_id'],
                   'task': registry['task'], 'target_item': label['target_item'],
                   'label': label['label'], 'context': {'item_kind': label['item_kind']},
                   'chart': chart, 'available_before_prediction': True,
                   'evidence': {'section_key': section['section_key'],
                                'section_sha256': section['sha256'],
                                'feedback_sha256': digest(feedback.encode()),
                                'chart_sha256': digest(stable_json([dict(x) for x in cells]).encode()),
                                'chart_source_lines': [c['source_line'] for c in cells],
                                'feedback_source_lines': label['feedback_source_lines'],
                                'chart_source_status': sorted({c['source_status'] for c in cells}),
                                'timing_verification': 'book_attribution_not_independently_timestamped',
                                'kind': 'book_report_only_not_external_verification'}}
            features(row)
            rows.append(row)
        inventory.update({'exported_rows': len(rows),
                          'exported_event_families': len({r['event_family_id'] for r in rows}),
                          'label_counts': dict(Counter(r['label'] for r in rows)),
                          'excluded': excluded,
                          'unlabelled_tasks': ['health.body_site', 'health.severity', 'health.recovery_hazard',
                                              'lost.direction', 'lost.environment', 'lost.recovery_hazard'],
                          'limitations': registry['limitations']})
        return {'inventory': inventory, 'rows': rows}
    finally:
        db.close()


def cumulative_incidence(hazards: list[dict[str, float]]) -> list[dict[str, float]]:
    """Competing recovery/death conditional hazards -> unconditional cumulative risk.

    Each interval's recovery/death/survive sum to one among subjects still at
    risk. Death is a competing endpoint; it must never be recovery or censoring.
    """
    survival, recovered, died = 1.0, 0.0, 0.0
    result = []
    for h in hazards:
        if set(h) != {'recovery', 'death', 'survive'}:
            raise ValueError('Three competing states required')
        if any(not math.isfinite(v) or v < 0 or v > 1 for v in h.values()):
            raise ValueError('Invalid hazard probability')
        if not math.isclose(sum(h.values()), 1.0, abs_tol=1e-8):
            raise ValueError('Conditional probabilities must sum to one')
        recovered += survival * h['recovery']
        died += survival * h['death']
        survival *= h['survive']
        result.append({'recovery': recovered, 'death': died, 'unresolved': survival})
    return result


def validate_direction(label: str | None, reference_frame: str | None) -> bool:
    if label is None:
        return False  # Unknown is a missing label, never a negative direction.
    if label not in ('N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW', 'at_reference'):
        raise ValueError('Unsupported direction')
    if not reference_frame:
        raise ValueError('Direction requires a declared coordinate reference before prediction')
    return True
