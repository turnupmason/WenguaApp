"""Versioned read-only adapter from the 194-case archive to professional facts.

Source line labels are NOT universal heaven/earth layer labels. A whole-column
convention is accepted only after comparison with an explicit source bureau.
No individual contradictory stem is corrected from a computed chart.
"""
from __future__ import annotations

import copy
import json
import re
import sqlite3
from collections import Counter

from .casting_shenqi import earth_plate, STARS, DOORS, SIX_JIA, xun_shou, cycle60
from .probability_research import ROOT, SOURCE_DB, SOURCE_SHA256, digest, extract, stable_json
from .probability_features_v2 import VERSION, build_bundle, flatten_bundle, source_manifest

STEMS = '甲乙丙丁戊己庚辛壬癸'
BRANCHES = '子丑寅卯辰巳午未申酉戌亥'
NUMBERS = {c: i+1 for i, c in enumerate('一二三四五六七八九')}
GODS = {'符': '值符', '值符': '值符', '蛇': '螣蛇', '腾蛇': '螣蛇', '螣蛇': '螣蛇',
        '阴': '太阴', '太阴': '太阴', '合': '六合', '六合': '六合', '虎': '白虎', '白虎': '白虎',
        '武': '玄武', '玄武': '玄武', '地': '九地', '九地': '九地', '天': '九天', '九天': '九天'}
SHORT_STARS = {s[1]: s for s in STARS.values()}
SHORT_DOORS = {s[0]: s for s in DOORS.values()}


def _parts(raw, alphabet):
    raw = re.sub(r'\s+', '', raw or '')
    symbols = [s for s in alphabet if s in raw]
    pos = max([raw.rfind(s) for s in symbols], default=-1)
    before, after = raw[:pos] if pos >= 0 else '', raw[pos+1:] if pos >= 0 else raw
    stems = re.findall('[' + STEMS + ']', after)
    return symbols, stems[0] if len(stems) == 1 else None, re.findall('[' + STEMS + ']', before), stems


def source_header(text, cells, metadata):
    if not cells:
        return {}, {'status': 'no_selected_source_board', 'source_lines': []}
    first = min(r['source_line'] for r in cells)
    lines = text.splitlines()
    bounds = metadata.get('source_span') or metadata.get('source_event_span') or metadata.get('source_lines')
    lower = max(0, first-25)
    if isinstance(bounds, list) and bounds and type(bounds[0]) is int:
        lower = max(lower, bounds[0]-1)
    candidates = []
    for i in range(lower, min(first-1, len(lines))):
        s = re.sub(r'\s+', '', lines[i])
        pillars = {name: m.group(1) for name, suffix in [('year', '年'), ('month', '月'), ('day', '日'), ('hour', '[时時]')]
                   if (m := re.search('([' + STEMS + '][' + BRANCHES + '])' + suffix, s))}
        if 'day' not in pillars or 'hour' not in pillars:
            continue
        calendar = {name + '_ganzhi': value for name, value in pillars.items() if value in cycle60()}
        end = min(first-1, i+6, len(lines))
        preamble = re.sub(r'\s+', '', '\n'.join(lines[i:end]))
        bureau_pattern = '([阴陽阳陰])(?:遁)?(?:[上中下]元)?第?([一二三四五六七八九1-9])局'
        options = set(re.findall(bureau_pattern, s))
        bureau_text = s
        if not options:
            options = set(re.findall(bureau_pattern, preamble))
            bureau_text = preamble
        m = re.search(bureau_pattern, bureau_text) if len(options) == 1 else None
        if m:
            calendar['dun'] = 'yin' if m[1] in '阴陰' else 'yang'
            calendar['ju'] = int(m[2]) if m[2].isdigit() else NUMBERS[m[2]]
        value_star = None
        for pattern in [r'(天[蓬任冲辅英芮柱心禽]星?)(?:为)?值符', r'值符(?:为|是)?(天[蓬任冲辅英芮柱心禽]星?)']:
            if m := re.search(pattern, preamble):
                value_star = m[1] if m[1].endswith('星') else m[1] + '星'
                break
        value_door = None
        for pattern in [r'([休生伤杜景死惊开]门)(?:为)?值使', r'值使(?:为|是)?([休生伤杜景死惊开]门)']:
            if m := re.search(pattern, preamble):
                value_door = m[1]
                break
        candidates.append((calendar, {'status': 'source_explicit_not_independent_astronomy',
                          'source_lines': list(range(i+1, end+1)), 'header_sha256': digest('\n'.join(lines[i:end]).encode()),
                          'value_star': value_star, 'value_door': value_door}))
    return candidates[-1] if candidates else ({}, {'status': 'no_unambiguous_pre_board_header', 'source_lines': []})


def literal_board(cells, calendar, header):
    issues = []
    center_row = next((r for r in cells if r['palace'] == 5), None)
    center = None
    if center_row:
        candidates = set(re.findall('[' + STEMS + ']', (center_row['door_position_raw'] or '') + (center_row['star_position_raw'] or '')))
        center = next(iter(candidates)) if len(candidates) == 1 else None
    parsed = {r['palace']: {'row': r,
              'door': _parts(r['door_position_raw'], SHORT_DOORS),
              'star': _parts(r['star_position_raw'], SHORT_STARS)} for r in cells}
    expected = earth_plate(calendar['dun'], calendar['ju']) if calendar.get('dun') and calendar.get('ju') else None
    checks = {}
    if expected:
        for column in ['door', 'star']:
            values = [(p, x[column][1]) for p, x in parsed.items() if p != 5 and x[column][1]]
            checks[column] = {'readable': len(values), 'matching': sum(expected[p] == value for p, value in values)}
    accepted = [k for k, v in checks.items() if v['readable'] >= 6 and v['readable'] == v['matching']]
    if len(accepted) == 1:
        earth_column = accepted[0]
        convention = 'earth_in_' + earth_column + '_source_line'
    elif len(accepted) == 2:
        earth_column = None
        convention = 'coincident_primary_columns'
    else:
        earth_column = None
        convention = 'unresolved_source_planes'
        if cells:
            issues.append('Layer convention not proven by whole-column source-bureau alignment; no stems filled from recast')
    board = {'palaces': {}, 'hour_ganzhi': calendar.get('hour_ganzhi'),
             'value_star': header.get('value_star'), 'value_door': header.get('value_door'),
             'school_id': 'shijia_zhuanpan', 'status': 'source_literal_feature_study'}
    for p in range(1, 10):
        x = parsed.get(p)
        cell = {'palace': p, 'door': None, 'deity': None, 'earth_stem': None,
                'heaven_stars': [], 'hosted_centre_earth_stem': center if p == 2 else None}
        if p == 5:
            cell['earth_stem'] = center
        elif x:
            door_symbols = x['door'][0]
            star_symbols = x['star'][0]
            cell['door'] = SHORT_DOORS[door_symbols[0]] if len(door_symbols) == 1 else None
            cell['deity'] = GODS.get(re.sub(r'\s+', '', x['row']['deity_raw'] or ''))
            if earth_column:
                sky_column = 'star' if earth_column == 'door' else 'door'
                earth, heaven = x[earth_column][1], x[sky_column][1]
            elif convention == 'coincident_primary_columns' and x['star'][1] == x['door'][1]:
                earth = heaven = x['star'][1]
            else:
                earth = heaven = None
            cell['earth_stem'] = earth
            # Named original star locations remain available even if stem planes
            # are unresolved. No modern recast replaces a disagreeing source star.
            for star in star_symbols:
                cell['heaven_stars'].append({'star': SHORT_STARS[star], 'carried_stem': heaven if star != '禽' else None})
        board['palaces'][str(p)] = cell
    qin = [c for c in board['palaces'].values() if any(s['star'] == '天禽星' for s in c['heaven_stars'])]
    rui = [c for c in board['palaces'].values() if any(s['star'] == '天芮星' for s in c['heaven_stars'])]
    if center and len(rui) == 1 and (not qin or (len(qin) == 1 and qin[0]['palace'] == rui[0]['palace'])):
        if not qin:
            rui[0]['heaven_stars'].append({'star': '天禽星', 'carried_stem': center})
        else:
            next(s for s in qin[0]['heaven_stars'] if s['star'] == '天禽星')['carried_stem'] = center
    elif qin:
        issues.append('Source Tianqin/Tianrui hosting incomplete or contradictory; no inferred carrier')
    if expected and calendar.get('hour_ganzhi'):
        head, _, hidden = xun_shou(calendar['hour_ganzhi'])
        origin = next(p for p, s in expected.items() if s == hidden)
        derived_star, derived_door = STARS[origin], DOORS[2 if origin == 5 else origin]
        for key, value in [('value_star', derived_star), ('value_door', derived_door)]:
            if not board[key]:
                board[key] = value
            elif board[key] != value:
                issues.append('Explicit ' + key + ' differs from bureau derivation; original retained')
    return board, {'plane_convention': convention, 'whole_column_alignment': checks,
                   'center_hosting': 'source_ch01_derived_tianqin_with_tianrui_and_earth_at_kun2' if center else 'unknown',
                   'issues': issues, 'original_cells_modified': False}


def atlas(db_path=SOURCE_DB):
    if digest(db_path.read_bytes()) != SOURCE_SHA256:
        raise ValueError('Original source archive hash mismatch')
    db = sqlite3.connect(db_path.resolve().as_uri() + '?mode=ro', uri=True)
    db.row_factory = sqlite3.Row
    cases, additional, coverage = [], [], Counter()
    try:
        context_rows = json.loads((ROOT / 'data/knowledge/probability_research/v2/case_contexts.json').read_text(encoding='utf8'))['cases']
        contexts = {r['case_id']: r for r in context_rows}
        for r in db.execute('select c.case_id,c.domain_id,c.event_family_id,c.known_before,s.section_key,s.sha256,s.original_text,p.metadata_json from cases c join sections s using(section_id) join historical_case_protocol p using(case_id) order by c.case_id'):
            cells = [dict(c) for c in db.execute('select * from historical_chart_cells where case_id=? order by palace', (r['case_id'],))]
            metadata = json.loads(r['metadata_json'] or '{}')
            calendar, header = source_header(r['original_text'], cells, metadata)
            board, audit = literal_board(cells, calendar, header)
            context = contexts.get(r['case_id'])
            if context and digest(r['known_before'].encode()) != context['known_before_sha256']:
                raise ValueError('Reviewed pre-question context changed: ' + r['case_id'])
            inquiry = dict(context['inquiry']) if context else {}
            payload = {'board': board, 'calendar': calendar, 'inquiry': inquiry, 'domain': r['domain_id']}
            bundle = build_bundle(payload)
            flat = flatten_bundle(bundle)
            coverage['cases'] += 1
            coverage['nine_source_cells'] += len(cells) == 9
            coverage['calendar_day_hour'] += bool(calendar.get('day_ganzhi') and calendar.get('hour_ganzhi'))
            coverage['calendar_month'] += bool(calendar.get('month_ganzhi'))
            coverage['plane_convention_resolved'] += audit['plane_convention'] != 'unresolved_source_planes'
            coverage['palace_nodes'] += len(bundle['nodes'])
            coverage['directed_pair_positions'] += len(bundle['edges'])
            cases.append({'case_id': r['case_id'], 'event_family_id': r['event_family_id'],
                          'domain_id': r['domain_id'], 'professional_input': payload,
                          'source_receipt': {'section_key': r['section_key'], 'section_sha256': r['sha256'],
                                             'raw_cells_sha256': digest(stable_json(cells).encode()),
                                             'source_board_cells': len(cells), 'calendar': header, 'layer_audit': audit},
                          'bundle': bundle, 'feature_count': len(flat),
                          'known_feature_count': sum(v not in ('__unknown__', 'not_applicable') for v in flat.values()),
                          'not_applicable_feature_count': sum(v == 'not_applicable' for v in flat.values())})
        for r in db.execute('select a.*,c.domain_id,c.event_family_id,s.original_text,s.section_key,s.sha256 from historical_case_additional_casts a join cases c using(case_id) join sections s using(section_id) order by a.case_id,a.cast_key'):
            cells = [dict(c) for c in db.execute('select * from historical_case_additional_cast_cells where case_id=? and cast_key=? order by palace', (r['case_id'], r['cast_key']))]
            calendar, header = source_header(r['original_text'], cells, {})
            if not calendar.get('hour_ganzhi') and r['hour_ganzhi'] in cycle60():
                calendar['hour_ganzhi'] = r['hour_ganzhi']
            board, audit = literal_board(cells, calendar, header)
            payload = {'board': board, 'calendar': calendar, 'inquiry': {}, 'domain': r['domain_id']}
            bundle = build_bundle(payload)
            additional.append({'case_id': r['case_id'], 'cast_key': r['cast_key'], 'event_family_id': r['event_family_id'],
                               'professional_input': payload, 'bundle': bundle,
                               'source_receipt': {'section_key': r['section_key'], 'section_sha256': r['sha256'],
                                                  'raw_cells_sha256': digest(stable_json(cells).encode()),
                                                  'source_board_cells': len(cells), 'calendar': header, 'layer_audit': audit},
                               'not_an_independent_training_event': True})
        coverage['additional_source_casts'] = len(additional)
        coverage['additional_nine_source_cells'] = sum(r['source_receipt']['source_board_cells'] == 9 for r in additional)
        coverage['all_palace_nodes'] = coverage['palace_nodes'] + 9*len(additional)
        coverage['all_directed_pair_positions'] = coverage['directed_pair_positions'] + 81*len(additional)
        return {'schema': VERSION, 'source_sha256': SOURCE_SHA256, 'cases': cases, 'additional_casts': additional,
                'coverage': dict(coverage), 'source_manifest': source_manifest(),
                'feature_catalog': sorted(flatten_bundle(cases[0]['bundle'])) if cases else [],
                'training_outcomes_in_atlas': False}
    finally:
        db.close()


def training_pack(db_path=SOURCE_DB, *, prepared_atlas=None):
    base = extract(db_path)
    facts = prepared_atlas or atlas(db_path)
    by_id = {r['case_id']: r for r in facts['cases']}
    rows = copy.deepcopy(base['rows'])
    for row in rows:
        record = by_id[row['case_id']]
        row['schema_version'] = 2
        row['professional_input'] = record['professional_input']
        row['evidence']['professional_source'] = record['source_receipt']
        # The first-cast blind question must not acquire the item's category
        # from a subsequent disclosure, even though it precedes the author's
        # later item-specific judgment. Preserve those stages separately.
        if row['case_id'] in ('shenqi.lost_property.case03', 'shenqi.lost_property.case07'):
            row['context']['item_kind'] = '__unknown_at_first_cast__'
            row['evidence']['context_revision'] = 'later_item_disclosure_masked_for_first_cast_view'
            row['evidence']['target_disclosure_source_line'] = 115 if row['case_id'].endswith('case03') else 293
            row['evidence']['target_not_disclosed_at_original_cast'] = True
    inventory = dict(base['inventory'])
    inventory.update({'feature_schema': VERSION, 'atlas_coverage': facts['coverage'],
                      'context_corrections': ['shenqi.lost_property.case03', 'shenqi.lost_property.case07'],
                      'v1_metrics_not_directly_comparable': True,
                      'professional_features_use_outcomes': False})
    return {'inventory': inventory, 'rows': rows, 'atlas': facts}
