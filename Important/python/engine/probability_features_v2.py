"""Source-indexed professional feature extraction, independent of outcome labels.

Nine nodes, all 81 directed palace positions, literal rules and explicit role
bindings. Missing, false and inapplicable are distinct. No verdict or probability
is calculated here. Fixed user heuristics are a separate ablation group.
"""
from __future__ import annotations

import hashlib
import json
import ast
from collections import Counter
from functools import lru_cache
from itertools import product
from pathlib import Path

from .casting_shenqi import DOORS, STARS, GUA, SIX_JIA, cycle60, xun_shou
from .factor_energy_review import DEITY_ELEMENTS, ordinary_month_stage, SEASON_BY_BRANCH
from .health_lifecycle_v391 import source_full12
from .marriage_runtime import ELEMENTS, PALACE_BRANCHES, element_relation, hourly_void_branches
from .semantic_lookup import STAR_ELEMENT, DOORS as DOOR_ELEMENTS, nine_star_month_status
from .selected_signifier_graph_v80 import palace_spatial_relation
from .symbol_relations import _data as relation_data, door_season

ROOT = Path(__file__).resolve().parents[2]
VERSION = 'professional_features_v2_20261103'
BRANCHES = '子丑寅卯辰巳午未申酉戌亥'
STEMS = '甲乙丙丁戊己庚辛壬癸'
STEM_ELEMENTS = dict(zip(STEMS, '木木火火土土金金水水'))
BRANCH_ELEMENTS = dict(zip(BRANCHES, '水土木木土火火土金金土水'))
HORSE = {b: h for group, h in [('申子辰', '寅'), ('寅午戌', '申'), ('巳酉丑', '亥'), ('亥卯未', '巳')] for b in group}
HIDDEN = {v: k[1] for k, v in SIX_JIA.items()}
INNER = {'yang': {1, 8, 3, 4}, 'yin': {9, 2, 7, 6}}
SOURCES = {
    'palace': ['src/wengua/casting_shenqi.py', 'src/wengua/marriage_runtime.py'],
    'season': ['src/wengua/semantic_lookup.py', 'src/wengua/factor_energy_review.py'],
    'lifecycle': ['src/wengua/health_lifecycle_v391.py', 'data/knowledge/score_models/health_severity_v42/twelve_life_stages_source_anchor_full.json'],
    'relations': ['data/knowledge/shenqi/shijia_symbols_ch04/relations_and_lifecycle.json'],
    'patterns': ['data/knowledge/shenqi/shijia_judgments_ch05/formation_variants_draft.json'],
    'roles': ['src/wengua/health_dynamic_v21.py', 'data/knowledge/probability_research/v2/case_contexts.json', 'data/knowledge/shenqi/health_prediction_ch01/method_index.json', 'data/knowledge/shenqi/lost_money_property_prediction_ch09/method_index.json', 'data/knowledge/shenqi/employment_prediction_ch05/method_index.json'],
    'macro': ['src/wengua/health_severity_v25.py', 'src/wengua/health_macro_facts_vnext.py'],
    'heuristic': ['src/wengua/user_domain_matrices_20261023.py', 'src/wengua/health_palace_detailed_vnext.py', 'src/wengua/health_quant_overlay_vnext.py', 'src/wengua/health_severity_v28.py', 'data/knowledge/health_81_excel_20261025/81_pairs.tsv', 'data/mobile/health_vnext/health_energy_200.json', 'data/knowledge/phrase_library/health_v20/actor_profiles.json'],
    'anatomy': ['data/knowledge/health_discomfort/three_source_stem_variants_v14_20261101.json', 'data/templates/health_discomfort_v11/native_discomfort_v15.json'],
}


def _json(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


@lru_cache(maxsize=1)
def _source_paths():
    paths = {ROOT / p for values in SOURCES.values() for p in values}
    paths.update({Path(__file__).resolve(), ROOT / 'src/wengua/probability_dataset_v2.py'})
    pending = [p for p in paths if p.suffix == '.py']
    inspected = set()
    while pending:
        path = pending.pop()
        if path in inspected:
            continue
        inspected.add(path)
        for node in ast.walk(ast.parse(path.read_text(encoding='utf8'))):
            if isinstance(node, ast.ImportFrom) and node.level:
                base = path.parent
                for _ in range(node.level-1):
                    base = base.parent
                names = [node.module] if node.module else [a.name for a in node.names]
                for name in names:
                    dependency = base.joinpath(*name.split('.')).with_suffix('.py')
                    if dependency.is_file() and dependency not in paths:
                        paths.add(dependency)
                        pending.append(dependency)
    return tuple(sorted(paths))


def source_manifest():
    # Exact disk bytes are retained for audit, independently of platform.
    return {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in _source_paths()}


@lru_cache(maxsize=1)
def _anatomy():
    return json.loads((ROOT / SOURCES['anatomy'][0]).read_text(encoding='utf8'))['mapping']


def source_fingerprint():
    # Git for Windows may checkout CRLF. Match the same text rule revision
    # across Windows/Linux while preserving exact-byte receipts above. Neither
    # the SQLite archive nor original book text is normalized or rewritten.
    logical = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes().replace(b'\r\n', b'\n')).hexdigest() for p in _source_paths()}
    return hashlib.sha256(_json(logical).encode()).hexdigest()


@lru_cache(maxsize=4096)
def _rel(kind, a, b):
    """Pair primitives only; a cycle link does not imply a complete formation."""
    found = []
    for row in relation_data()['relations']:
        if row['kind'] != kind:
            continue
        members = row['members']
        if len(members) == 2:
            directed = kind in ('branch_punishment', 'branch_self_punishment') and not row.get('attributes', {}).get('mutual')
            match = [a, b] == members if directed else Counter([a, b]) == Counter(members)
        elif row.get('attributes', {}).get('directed_cycle'):
            match = (a, b) in list(zip(members, members[1:] + members[:1]))
        else:
            match = a != b and a in members and b in members
        if match:
            found.append(row['relation_id'])
    return tuple(found)


def _stem(kind, a, b):
    return None if a is None or b is None else bool(_rel(kind, a, b))


def _stage(stem, palace):
    if stem is None or palace == 5:
        return None
    table = _life()[stem]['branch_to_stage']
    return [{'branch': b, 'stage': table[b]} for b in PALACE_BRANCHES[palace]]


@lru_cache(maxsize=1)
def _life():
    return source_full12()


@lru_cache(maxsize=1)
def _patterns():
    path = ROOT / SOURCES['patterns'][0]
    return json.loads(path.read_text(encoding='utf8'))['variants']


def _condition(ast, row):
    states = []
    for condition in ast:
        value = row.get(condition['field'])
        if value is None:
            states.append(None)
        elif condition['op'] == 'eq':
            states.append(value == condition['value'])
        elif condition['op'] == 'in':
            states.append(value in condition['values'])
        else:
            raise ValueError('Unsupported source formation AST')
    return False if False in states else None if None in states else True


def _or(states):
    return True if True in states else None if not states or None in states else False


def _and(states):
    return False if False in states else None if None in states else True


def _pattern(rule, cell):
    if cell['palace'] == 5:
        return 'not_applicable'
    rows = [{'heaven_stem': s.get('carried_stem'), 'earth_stem': cell.get('earth_stem'),
             'door': (cell.get('door') or '').removesuffix('门') or None,
             'deity': cell.get('deity'), 'palace': cell['palace']}
            for s in cell.get('heaven_stars', [])]
    states = []
    for row in rows:
        all_of = _condition(rule['preconditions'], row)
        any_of = _or([_condition(a, row) for a in rule['alternatives']]) if rule['alternatives'] else True
        states.append(_and([all_of, any_of]))
    return _or(states)


def _safe_input(payload):
    if set(payload) - {'board', 'calendar', 'inquiry', 'domain'}:
        raise ValueError('Unregistered professional input field')
    calendar = payload.get('calendar', {})
    if set(calendar) - {'year_ganzhi', 'month_ganzhi', 'day_ganzhi', 'hour_ganzhi', 'dun', 'ju'}:
        raise ValueError('Only source calendar facts allowed')
    for key in ['year_ganzhi', 'month_ganzhi', 'day_ganzhi', 'hour_ganzhi']:
        if calendar.get(key) is not None and calendar[key] not in cycle60():
            raise ValueError('Invalid sexagenary calendar fact: ' + key)
    if calendar.get('dun') not in (None, 'yin', 'yang') or (calendar.get('ju') is not None and (type(calendar['ju']) is not int or not 1 <= calendar['ju'] <= 9)):
        raise ValueError('Invalid explicit bureau')
    inquiry = payload.get('inquiry', {})
    if set(inquiry) - {'relationship', 'patient_sex', 'patient_birth_ganzhi', 'subject_year_ganzhi', 'birth_order', 'sibling_order', 'intent', 'consultation_context', 'question_kind', 'subject_species'}:
        raise ValueError('Only pre-question structured role context allowed')
    if inquiry.get('patient_sex') not in (None, 'male', 'female') or inquiry.get('consultation_context') not in (None, 'direct_self', 'direct_proxy', 'event_news'):
        raise ValueError('Explicit sex and consultation context categories required')
    for k in ['patient_birth_ganzhi', 'subject_year_ganzhi']:
        if inquiry.get(k) is not None and inquiry[k] not in cycle60():
            raise ValueError('Invalid explicitly supplied birth pillar')
    raw = payload.get('board') or {}
    if set(raw) - {'palaces', 'value_star', 'value_door', 'hour_ganzhi', 'school_id', 'status', 'source_key'}:
        raise ValueError('Unregistered board input')
    if raw.get('school_id') not in (None, 'shijia_zhuanpan'):
        raise ValueError('Do not mix another casting school into rotating-chart features')
    if raw.get('value_star') not in (None, *STARS.values()) or raw.get('value_door') not in (None, *DOORS.values()):
        raise ValueError('Invalid value-star/value-door symbol')
    board = {'palaces': {}, 'hour_ganzhi': calendar.get('hour_ganzhi'),
             'school_id': 'shijia_zhuanpan', 'status': 'source_literal_feature_study',
             'value_star': raw.get('value_star'), 'value_door': raw.get('value_door')}
    if raw.get('hour_ganzhi') not in (None, calendar.get('hour_ganzhi')):
        raise ValueError('Board/calendar hour mismatch')
    if set(raw.get('palaces', {})) - {str(p) for p in range(1, 10)}:
        raise ValueError('Only real nine-palace identifiers permitted')
    for p in range(1, 10):
        c = raw.get('palaces', {}).get(str(p), {})
        if set(c) - {'palace', 'gua', 'door', 'deity', 'earth_stem', 'heaven_stars', 'hosted_centre_earth_stem'}:
            raise ValueError('Unregistered palace input')
        if c.get('palace', p) != p:
            raise ValueError('Palace identity mismatch')
        if c.get('gua') not in (None, GUA[p]):
            raise ValueError('Palace/trigram mismatch')
        if c.get('door') not in (None, *DOORS.values()) or c.get('deity') not in (None, *DEITY_ELEMENTS):
            raise ValueError('Invalid literal door or deity')
        if c.get('earth_stem') is not None and c['earth_stem'] not in tuple(STEMS):
            raise ValueError('Invalid earth stem')
        if c.get('hosted_centre_earth_stem') is not None and (p != 2 or c['hosted_centre_earth_stem'] not in tuple(STEMS)):
            raise ValueError('Invalid fixed centre-earth host')
        stars = []
        for s in c.get('heaven_stars', []):
            if set(s) - {'star', 'carried_stem'} or s.get('star') not in STARS.values() or (s.get('carried_stem') is not None and s['carried_stem'] not in tuple(STEMS)):
                raise ValueError('Invalid actual star carrier')
            stars.append(dict(s))
        if p == 5 and (stars or c.get('door') or c.get('deity')):
            raise ValueError('Do not manufacture ordinary centre occupants')
        board['palaces'][str(p)] = {'palace': p, 'gua': GUA[p], 'door': c.get('door'), 'deity': c.get('deity'),
                                    'earth_stem': c.get('earth_stem'), 'heaven_stars': stars,
                                    'hosted_centre_earth_stem': c.get('hosted_centre_earth_stem')}
    return {'board': board, 'calendar': dict(calendar), 'inquiry': dict(inquiry), 'domain': payload.get('domain')}


def _season(kind, symbol, p, month):
    if kind == 'deity' and symbol is not None and p != 5:
        return 'not_applicable'
    if symbol is None or month is None or p == 5:
        return None
    month_element = BRANCH_ELEMENTS[month]
    if kind == 'star':
        return nine_star_month_status(symbol, month_element)['value']
    if kind == 'deity':
        return 'not_applicable'
    element = STEM_ELEMENTS[symbol] if kind == 'stem' else DOOR_ELEMENTS[symbol.removesuffix('门')]
    return ordinary_month_stage(element, month_element)


@lru_cache(maxsize=16384)
def _power(kind, symbol, p, month, plane='heaven'):
    if symbol is None or month is None or p == 5:
        return None
    from .user_domain_matrices_20261023 import lookup_selected_factor
    return lookup_selected_factor(kind, symbol, month, p, plane=plane)['strength_label']


def _positions(board, kind, symbol):
    if symbol is None:
        return []
    result = []
    for key, cell in board['palaces'].items():
        p = int(key)
        if kind == 'stem':
            if any(s['carried_stem'] == symbol for s in cell['heaven_stars']):
                result.append(p)
        elif kind == 'star':
            if any(s['star'] == symbol for s in cell['heaven_stars']):
                result.append(p)
        elif cell.get(kind) == symbol:
            result.append(p)
    return result


def _pillar_symbol(ganzhi):
    return (SIX_JIA.get(ganzhi) if ganzhi[0] == '甲' else ganzhi[0]) if ganzhi else None


def _symbol_element(role):
    tables = {'stem': STEM_ELEMENTS, 'star': STAR_ELEMENT, 'deity': DEITY_ELEMENTS,
              'door': {k + '门': v for k, v in DOOR_ELEMENTS.items()}}
    return tables[role['kind']].get(role['symbol'])


def _roles(board, calendar, inquiry, domain):
    roles = {}
    for name in ['year', 'month', 'day', 'hour']:
        pillar = calendar.get(name + '_ganzhi')
        roles[name] = ('stem', _pillar_symbol(pillar))
    roles.update({'value_star': ('star', board.get('value_star')), 'value_door': ('door', board.get('value_door')),
                  'chief_deity': ('deity', '值符'), 'illness_marker': ('star', '天芮星'),
                  'doctor_marker': ('star', '天心星'), 'medicine_marker': ('stem', '乙'),
                  'link_marker': ('deity', '六合'), 'xuanwu_marker': ('deity', '玄武'),
                  'tianpeng_marker': ('star', '天蓬星'), 'open_marker': ('door', '开门'),
                  'closed_marker': ('door', '杜门'), 'life_marker': ('door', '生门'),
                  'injury_marker': ('door', '伤门'), 'death_marker': ('door', '死门'),
                  'cash_marker': ('stem', '戊'), 'geng_marker': ('stem', '庚'),
                  'natal_if_supplied': ('stem', _pillar_symbol(inquiry.get('patient_birth_ganzhi') or inquiry.get('subject_year_ganzhi')))})
    bound, binding = None, None
    if domain == 'health' and inquiry.get('relationship'):
        from .health_dynamic_v21 import bind_patient
        try:
            # This reuses the frozen conditional relation profiles; it does not
            # copy a later birth correction or infer sex/birth from an outcome.
            binding = bind_patient(board, inquiry, calendar)
            bound = binding.get('main_cell')
            symbol = binding.get('carrier_stem')
        except ValueError:
            symbol = None
        roles['patient'] = ('stem', symbol)
    else:
        roles['patient'] = ('stem', None)
    result = {}
    for name, (kind, symbol) in roles.items():
        positions = _positions(board, kind, symbol)
        palace = positions[0] if len(positions) == 1 else None
        if name == 'patient' and not bound:
            palace = None
        result[name] = {'kind': kind, 'symbol': symbol, 'palace': palace,
                        'binding_state': 'bound' if palace is not None else 'missing_or_ambiguous',
                        'identity': [kind, symbol, palace] if palace is not None else None}
    binding_meta = {'state': ('known' if binding else 'unknown') if domain == 'health' else 'not_applicable',
                    'auxiliary_palaces': sorted({c['palace'] for c in binding.get('extra_cells', []) if c}) if binding else [],
                    'auxiliaries_are_conditional_candidates_not_outcome_votes': True}
    return result, binding_meta


def build_bundle(payload):
    return json.loads(_cached_bundle(_json(_safe_input(payload))))


@lru_cache(maxsize=512)
def _cached_bundle(serialized):
    safe = json.loads(serialized)
    board, calendar, inquiry = safe['board'], safe['calendar'], safe['inquiry']
    month = calendar.get('month_ganzhi', '')
    month = month[1] if month else None
    hour, day = calendar.get('hour_ganzhi'), calendar.get('day_ganzhi')
    empties = hourly_void_branches(hour)['xun_kong_branches'] if hour else None
    nodes, edges = [], []
    for p in range(1, 10):
        cell = board['palaces'][str(p)]
        stars = cell['heaven_stars']
        primary = [s for s in stars if s['star'] != '天禽星']
        star = primary[0]['star'] if len(primary) == 1 else None
        heaven = primary[0]['carried_stem'] if len(primary) == 1 else None
        branch_set = PALACE_BRANCHES[p]
        node = {'palace': p, 'element': ELEMENTS[p], 'branches': list(branch_set),
                'star': star, 'door': cell['door'], 'deity': cell['deity'],
                'earth': cell['earth_stem'], 'heaven': heaven,
                'hosted_earth': cell['hosted_centre_earth_stem'],
                'centre_star_carried_stem': next((s['carried_stem'] for s in stars if s['star'] == '天禽星'), None),
                'inner': p in INNER[calendar['dun']] if p != 5 and calendar.get('dun') else None,
                'palace_month_stage': ordinary_month_stage(ELEMENTS[p], BRANCH_ELEMENTS[month]) if month else None,
                'hour_void_branches': [b for b in branch_set if b in empties] if empties is not None else None,
                'day_horse': HORSE[day[1]] in branch_set if day and p != 5 else None,
                'hour_horse': HORSE[hour[1]] in branch_set if hour and p != 5 else None,
                'patterns': {}, 'source_heuristics': {}, 'carriers': []}
        node['hour_void'] = bool(node['hour_void_branches']) if empties is not None and p != 5 else None
        if p == 5:
            node['applicability'] = 'centre_earth_only'
        else:
            node['applicability'] = 'outer_palace'
        for kind, symbol in [('star', star), ('door', cell['door']), ('deity', cell['deity'])]:
            node[kind + '_month_stage'] = _season(kind, symbol, p, month)
            el = STAR_ELEMENT.get(symbol) if kind == 'star' else DOOR_ELEMENTS.get((symbol or '').removesuffix('门')) if kind == 'door' else DEITY_ELEMENTS.get(symbol)
            node[kind + '_palace_relation'] = element_relation(el, ELEMENTS[p]) if el and p != 5 else None
            node['source_heuristics'][kind + '_power'] = _power(kind, symbol, p, month)
        node['door_book_season'] = door_season(cell['door'], SEASON_BY_BRANCH[month])['stage'] if cell['door'] and month and p != 5 else None
        node['door_press'] = node['door_palace_relation'] == '克' if cell['door'] and p != 5 else None
        # Do not replace source coexistence or stage ambiguity with a maximum.
        for plane, symbol in [('heaven', heaven), ('earth', cell['earth_stem']),
                              ('centre_heaven', node['centre_star_carried_stem']), ('hosted_earth', node['hosted_earth'])]:
            stages = _stage(symbol, p)
            hidden = HIDDEN.get(symbol)
            life = {'plane': plane, 'stem': symbol, 'lifecycle': stages,
                    'month_stage': _season('stem', symbol, p, month),
                    'hidden_jia_branch': hidden,
                    'hidden_jia_lifecycle': _stage('甲', p) if hidden else None,
                    'hidden_branch_clash': any(_rel('branch_clash', hidden, b) for b in branch_set) if hidden and p != 5 else None,
                    'hidden_branch_join': any(_rel('branch_six_harmony', hidden, b) for b in branch_set) if hidden and p != 5 else None,
                    'hidden_branch_punishment_link': any(_rel('branch_punishment', hidden, b) for b in branch_set) if hidden and p != 5 else None,
                    'six_yi_striking_punishment': None,
                    'tomb_release_branch': None,
                    'power': _power('stem', symbol, p, month, 'earth' if 'earth' in plane else 'heaven')}
            if symbol:
                tomb = _life()[symbol]['stage_to_branch']['墓']
                life['tomb_release_branch'] = next((b for b in BRANCHES if _rel('branch_clash', tomb, b)), None)
                from .health_severity_v28 import STRIKING_PALACE
                life['six_yi_striking_punishment'] = STRIKING_PALACE[symbol] == p if symbol in STRIKING_PALACE and p != 5 and plane in ('heaven', 'centre_heaven') else 'not_applicable'
            node['carriers'].append(life)
        if p != 5 and empties is not None:
            if not node['hour_void']:
                node['source_heuristics']['void_classification'] = 'not_void'
                node['source_heuristics']['horse_cleared_void'] = False
            elif month:
                from .health_palace_detailed_vnext import inspect_role_void
                v = inspect_role_void(palace=p, occupied_void_branches=node['hour_void_branches'], month_branch=month, hour_ganzhi=hour)
                node['source_heuristics']['void_classification'] = v['classification']
                node['source_heuristics']['horse_cleared_void'] = v['horse_cleared_void']
            else:
                node['source_heuristics']['void_classification'] = None
        node['stem_combine_pair'] = _stem('stem_combine', heaven, cell['earth_stem'])
        node['stem_clash_pair'] = _stem('stem_clash', heaven, cell['earth_stem'])
        # Source 39 conditional AST variants; partial/missing facts stay unknown.
        node['patterns'] = {r['variant_id']: _pattern(r, cell) for r in _patterns()}
        if p != 5 and cell['earth_stem'] and stars and (p != 2 or cell['hosted_centre_earth_stem']):
            from .health_81_excel_catalog_vnext import for_real_palace
            if all(s['carried_stem'] in tuple(STEMS) for s in stars):
                try:
                    node['ordered81'] = [{'pair': r['key'], 'star': r['star'], 'polarity': r['polarity']} for r in for_real_palace(cell)]
                except ValueError:
                    node['ordered81'] = None
            else:
                node['ordered81'] = None
        else:
            node['ordered81'] = None
        nodes.append(node)
    for a, b in product(nodes, repeat=2):
        pa, pb = a['palace'], b['palace']
        state = 'self' if pa == pb else 'centre' if 5 in (pa, pb) else 'outer_pair'
        edge = {'source': pa, 'target': pb, 'applicability': state,
                'same_palace': pa == pb, 'geometry': palace_spatial_relation(pa, pb),
                'palace_relation': element_relation(a['element'], b['element']),
                'opposite': pa != 5 and pb != 5 and pa + pb == 10,
                'heaven_stem_combine': _stem('stem_combine', a['heaven'], b['heaven']) if state == 'outer_pair' else None,
                'heaven_stem_clash': _stem('stem_clash', a['heaven'], b['heaven']) if state == 'outer_pair' else None}
        for kind in ['branch_clash', 'branch_harm', 'branch_six_harmony', 'branch_punishment', 'branch_three_meeting', 'branch_three_harmony']:
            edge[kind + '_component'] = bool([r for x, y in product(a['branches'], b['branches']) for r in _rel(kind, x, y)]) if state == 'outer_pair' else None
        edges.append(edge)
    roles, binding_meta = _roles(board, calendar, inquiry, safe.get('domain'))
    role_edges = []
    for an, bn in [('day', 'hour'), ('hour', 'day'), ('doctor_marker', 'illness_marker'),
                   ('medicine_marker', 'illness_marker'), ('patient', 'illness_marker'),
                   ('illness_marker', 'patient'), ('natal_if_supplied', 'illness_marker'),
                   ('open_marker', 'day'), ('closed_marker', 'day'), ('year', 'day'),
                   ('month', 'day'), ('xuanwu_marker', 'hour'), ('tianpeng_marker', 'hour'),
                   ('link_marker', 'hour'), ('geng_marker', 'hour'), ('value_door', 'hour')]:
        a, b = roles[an], roles[bn]
        pa, pb = a['palace'], b['palace']
        edge = {'source_role': an, 'target_role': bn,
                'same_identity': a['identity'] == b['identity'] if pa and pb else None,
                'palace_relation': ('同宫' if pa == pb else element_relation(ELEMENTS[pa], ELEMENTS[pb])) if pa and pb else None,
                'both_inner': nodes[pa-1]['inner'] and nodes[pb-1]['inner'] if pa and pb and nodes[pa-1]['inner'] is not None and nodes[pb-1]['inner'] is not None else None,
                'both_outer': not nodes[pa-1]['inner'] and not nodes[pb-1]['inner'] if pa and pb and nodes[pa-1]['inner'] is not None and nodes[pb-1]['inner'] is not None else None}
        ae, be = _symbol_element(a), _symbol_element(b)
        edge['symbol_element_relation'] = element_relation(ae, be) if ae and be else None
        for name, role, palace in [('source', a, pa), ('target', b, pb)]:
            edge[name + '_power'] = _power(role['kind'], role['symbol'], palace, month) if palace and role['symbol'] else None
        edge['control_matrix_status'], edge['control_matrix_result'] = 'not_applicable', 'not_applicable'
        if edge['palace_relation'] == '克':
            if not edge['source_power'] or not edge['target_power']:
                edge['control_matrix_status'], edge['control_matrix_result'] = 'power_unknown', None
            else:
                from .user_domain_matrices_20261023 import inspect_control
                av = nodes[pa-1]['source_heuristics'].get('void_classification')
                bv = nodes[pb-1]['source_heuristics'].get('void_classification')
                control = inspect_control(actor_power=edge['source_power'], target_power=edge['target_power'], palace_relation='克',
                    attacker_void_unknown=av is None, target_void_unknown=bv is None,
                    attacker_fake_void=av == 'fake_void', target_fake_void=bv == 'fake_void',
                    attacker_true_void=av == 'true_void', target_true_void=bv == 'true_void')
                edge['control_matrix_status'], edge['control_matrix_result'] = control['status'], control['result']
        role_edges.append(edge)
    from .health_quant_overlay_vnext import independent_special_host
    selected_names = (['illness_marker', 'doctor_marker', 'medicine_marker', 'patient', 'hour']
                      if safe.get('domain') == 'health' else ['day', 'hour'])
    if safe.get('domain') == 'health' and roles['natal_if_supplied']['symbol']:
        selected_names.append('natal_if_supplied')
    cohosts = []
    for node in nodes:
        p = node['palace']
        hosts = [roles[name] for name in selected_names if roles[name]['palace'] == p]
        auxiliary_star = node['star'] if p in binding_meta['auxiliary_palaces'] else None
        if auxiliary_star:
            hosts.append({'kind': 'star', 'symbol': auxiliary_star, 'identity': ['star', auxiliary_star, p]})
        record = {'palace': p, 'unique_selected_identities': len({tuple(r['identity']) for r in hosts}), 'candidates': {}}
        for kind, symbol in [('stem', '乙'), ('stem', '丁'), ('star', '天心星'), ('deity', '值符')]:
            cell = board['palaces'][str(p)]
            if kind == 'stem':
                residents = [s['carried_stem'] for s in cell['heaven_stars']]
                present = True if symbol in residents else False if residents and None not in residents else None
            elif kind == 'star':
                residents = [s['star'] for s in cell['heaven_stars']]
                present = symbol in residents if residents else None
            else:
                present = cell['deity'] == symbol if cell['deity'] is not None else None
            independent = independent_special_host(hosts, kind, symbol)
            unresolved_host = any(roles[n]['palace'] is None for n in selected_names) or (p in binding_meta['auxiliary_palaces'] and auxiliary_star is None)
            result = None if present is None else False if not present else True if independent else None if unresolved_host else False
            record['candidates'][kind + ':' + symbol] = result if p != 5 else None
        cohosts.append(record)
    macro = {'star_fuyin': None, 'star_fanyin': None, 'door_fuyin': None, 'door_fanyin': None,
             'five_not_encounter': None, 'tianxian_hour': None, 'day_stem_in_heaven': None,
             'stem_fuyin': None, 'stem_fanyin': None}
    try:
        from .health_severity_v25 import fuyin_fanyin_facts
        fy = fuyin_fanyin_facts(board)
        for layer in ['star', 'door']:
            macro[layer + '_fuyin'] = fy[layer] == '伏吟'
            macro[layer + '_fanyin'] = fy[layer] == '反吟'
    except ValueError:
        pass
    if day and hour:
        from .health_severity_v27 import five_not_encounter
        from .health_macro_facts_vnext import tianxian_hour
        macro['five_not_encounter'] = five_not_encounter(day, hour)['triggered']
        macro['tianxian_hour'] = tianxian_hour(day, hour)
    if day:
        macro['day_stem_in_heaven'] = bool(_positions(board, 'stem', _pillar_symbol(day))) if all(n['heaven'] is not None for n in nodes if n['palace'] != 5) else None
    if all(n['heaven'] and n['earth'] for n in nodes if n['palace'] != 5):
        outer = [n for n in nodes if n['palace'] != 5]
        macro['stem_fuyin'] = all(n['heaven'] == n['earth'] for n in outer)
        macro['stem_fanyin'] = all(n['heaven'] == nodes[9-n['palace']]['earth'] for n in outer)
    pillar_relations = {}
    for a, b in product(['year', 'month', 'day', 'hour'], repeat=2):
        ga, gb = calendar.get(a + '_ganzhi'), calendar.get(b + '_ganzhi')
        for kind in ['branch_clash', 'branch_harm', 'branch_six_harmony', 'branch_punishment', 'branch_self_punishment']:
            pillar_relations[f'{a}.{b}.{kind}'] = bool(_rel(kind, ga[1], gb[1])) if ga and gb and a != b else None
    result = {'schema': VERSION, 'calendar': calendar,
              'role_context': {k: inquiry.get(k) for k in ['relationship', 'patient_sex', 'consultation_context', 'subject_species']},
              'macro': macro,
              'nodes': nodes, 'edges': edges, 'roles': roles, 'role_edges': role_edges,
              'pillar_relations': pillar_relations,
              'independent_cohosts': cohosts,
              'patient_binding': binding_meta,
              'unresolved_rule_families': {'branch_break': 'not_defined_in_current_source_relation_catalog',
                                           'combination_transformation': 'pair_presence_does_not_prove_transformation',
                                           'tomb_timing_selection': 'requires_declared_target_not_known_outcome_duration'},
              'provenance': SOURCES, 'outcome_features_present': False}
    return _json(result)


def flatten_bundle(bundle, *, include_heuristics=True):
    """Stable field keys; null remains unknown, never a false event observation."""
    result = {}
    def add(key, value, *, categorical=False):
        if value is None:
            result[key] = '__unknown__'
        elif isinstance(value, bool):
            result[key] = int(value)
        elif isinstance(value, (int, float)) and not categorical:
            result[key] = value
        elif isinstance(value, str):
            result[key] = value
        elif categorical:
            result[key] = str(value)
        else:
            raise ValueError('Only declared scalar features may be flattened')
    for key in ['year_ganzhi', 'month_ganzhi', 'day_ganzhi', 'hour_ganzhi', 'dun', 'ju']:
        add('calendar.' + key, bundle['calendar'].get(key), categorical=True)
    for key, value in bundle['role_context'].items():
        add('role_context.' + key, value)
    for key, value in bundle['macro'].items():
        add('macro.' + key, value)
    for node in bundle['nodes']:
        prefix = 'node.p' + str(node['palace']) + '.'
        for key in ['element', 'star', 'door', 'deity', 'earth', 'heaven', 'hosted_earth', 'centre_star_carried_stem',
                    'inner', 'palace_month_stage', 'star_month_stage', 'door_month_stage', 'deity_month_stage',
                    'star_palace_relation', 'door_palace_relation', 'deity_palace_relation', 'door_book_season',
                    'door_press', 'hour_void', 'day_horse', 'hour_horse', 'stem_combine_pair', 'stem_clash_pair', 'applicability']:
            value = node[key]
            if node['palace'] == 5 and key not in ('element', 'earth', 'palace_month_stage', 'applicability'):
                value = 'not_applicable'
            add(prefix + key, value)
        for carrier in node['carriers']:
            cp = prefix + carrier['plane'] + '.'
            for key in ['stem', 'month_stage', 'hidden_jia_branch', 'hidden_branch_clash', 'hidden_branch_join', 'hidden_branch_punishment_link', 'six_yi_striking_punishment', 'tomb_release_branch']:
                value = carrier[key]
                if node['palace'] == 5 or (key.startswith('hidden_') and carrier['stem'] is not None and carrier['hidden_jia_branch'] is None):
                    value = 'not_applicable'
                add(cp + key, value)
            for branch in BRANCHES:
                stages = carrier['lifecycle']
                add(cp + 'lifecycle.' + branch, 'not_applicable' if node['palace'] == 5 else next((s['stage'] for s in stages if s['branch'] == branch), 'not_applicable') if stages is not None else None)
            for key in ['墓', '绝', '死', '长生', '帝旺']:
                add(cp + 'has_' + key, any(s['stage'] == key for s in carrier['lifecycle']) if carrier['lifecycle'] is not None else None)
                add(cp + 'hidden_jia_has_' + key, any(s['stage'] == key for s in carrier['hidden_jia_lifecycle']) if carrier['hidden_jia_lifecycle'] is not None else None)
            if include_heuristics:
                add('heuristic.' + cp + 'power', carrier['power'])
                # Original, separate anatomical source families; these are
                # traditional correspondences, never observed medical labels.
                for source_family in ['qimen_secret_vol13', 'sanming_viscera', 'sanming_body_surface']:
                    mappings = _anatomy().get(carrier['stem'])
                    add('heuristic.' + cp + 'anatomy.' + source_family,
                        '/'.join(mappings[source_family]) if mappings else None)
        for rule, value in node['patterns'].items():
            add(prefix + 'literal_candidate.' + rule, value)
        pairs = node['ordered81']
        for a, b in product('戊乙丙丁己庚辛壬癸', repeat=2):
            add(prefix + 'ordered81.' + a + b, sum(r['pair'] == a + '/' + b for r in pairs) if pairs is not None else None)
        if include_heuristics:
            for key in ['star_power', 'door_power', 'deity_power', 'void_classification', 'horse_cleared_void']:
                add('heuristic.' + prefix + key, node['source_heuristics'].get(key))
            if node['deity'] and node['palace'] != 5:
                from .health_palace_detailed_vnext import inspect_god
                god = inspect_god(deity=node['deity'], palace_element=node['element'])
            else:
                god = {}
            for key in ['strength_effect', 'polarity']:
                add('heuristic.' + prefix + 'god_no_month.' + key, god.get(key))
            add('heuristic.' + prefix + 'ordered81_good', sum(r['polarity'] == '吉' for r in pairs) if pairs is not None else None)
            add('heuristic.' + prefix + 'ordered81_bad', sum(r['polarity'] == '凶' for r in pairs) if pairs is not None else None)
    for edge in bundle['edges']:
        prefix = f'edge.p{edge["source"]}.p{edge["target"]}.'
        for key, value in edge.items():
            if key not in ['source', 'target']:
                if value is None and edge['applicability'] != 'outer_pair':
                    value = 'not_applicable'
                add(prefix + key, value)
    for name, role in bundle['roles'].items():
        for key in ['kind', 'symbol', 'palace', 'binding_state']:
            add('role.' + name + '.' + key, role[key], categorical=True)
        palace = role['palace']
        for key in ['inner', 'hour_void', 'hour_horse', 'day_horse', 'door_press', 'palace_month_stage',
                    'star', 'door', 'deity', 'earth', 'heaven', 'hosted_earth', 'centre_star_carried_stem',
                    'star_month_stage', 'door_month_stage', 'star_palace_relation', 'door_palace_relation']:
            add('role.' + name + '.' + key, bundle['nodes'][palace-1][key] if palace else None)
        # Bind the COMPLETE local environment to the selected role, rather than
        # asking a shallow model to rediscover a palace-number join. A marker
        # sharing a palace does not acquire another marker's own strength.
        month_pillar = bundle['calendar'].get('month_ganzhi')
        month = month_pillar[1] if month_pillar else None
        own_symbol = role['symbol']
        if role['kind'] == 'stem':
            carrier = own_symbol
        elif role['kind'] == 'star' and palace:
            node = bundle['nodes'][palace-1]
            carrier = node['centre_star_carried_stem'] if own_symbol == '天禽星' else node['heaven']
        else:
            carrier = None
        add('role.' + name + '.actual_carrier_stem', carrier if role['kind'] in ('stem', 'star') else 'not_applicable')
        stages = _stage(carrier, palace) if palace and carrier else None
        for stage in ['墓', '绝', '死', '长生', '帝旺']:
            value = any(s['stage'] == stage for s in stages) if stages is not None else None
            add('role.' + name + '.carrier_has_' + stage, value if role['kind'] in ('stem', 'star') else 'not_applicable')
        if include_heuristics:
            add('heuristic.role.' + name + '.selected_power', _power(role['kind'], own_symbol, palace, month) if palace and own_symbol else None)
    for edge in bundle['role_edges']:
        prefix = 'role_edge.' + edge['source_role'] + '.' + edge['target_role'] + '.'
        for key, value in edge.items():
            if key in ['source_role', 'target_role'] or key.endswith('_power') or key.startswith('control_matrix'):
                continue
            add(prefix + key, value)
        if include_heuristics:
            for key in ['source_power', 'target_power', 'control_matrix_status', 'control_matrix_result']:
                add('heuristic.' + prefix + key, edge[key])
    for record in bundle['independent_cohosts']:
        for name, value in record['candidates'].items():
            add('cohost.p' + str(record['palace']) + '.' + name, value)
    binding = bundle['patient_binding']
    patient, illness = bundle['roles']['patient']['palace'], bundle['roles']['illness_marker']['palace']
    for node in bundle['nodes']:
        p = node['palace']
        selected = p in binding['auxiliary_palaces']
        prefix = 'patient_aux.p' + str(p) + '.'
        def scoped(value):
            return 'not_applicable' if binding['state'] == 'not_applicable' else None if binding['state'] == 'unknown' else value
        add(prefix + 'selected_candidate', scoped(selected))
        add(prefix + 'same_main_palace', scoped(p == patient if selected and patient else 'not_applicable' if not selected else None))
        add(prefix + 'primary_star', scoped(node['star'] if selected else 'not_applicable'))
        add(prefix + 'relation_to_patient', scoped(('同宫' if p == patient else element_relation(ELEMENTS[p], ELEMENTS[patient])) if selected and patient else 'not_applicable' if not selected else None))
        add(prefix + 'relation_to_illness', scoped(('同宫' if p == illness else element_relation(ELEMENTS[p], ELEMENTS[illness])) if selected and illness else 'not_applicable' if not selected else None))
        if include_heuristics:
            month = bundle['calendar'].get('month_ganzhi')
            add('heuristic.' + prefix + 'actual_star_power', scoped(_power('star', node['star'], p, month[1] if month else None) if selected else 'not_applicable'))
    for key, value in bundle['pillar_relations'].items():
        add('pillar_relation.' + key, value)
    for key in bundle['unresolved_rule_families']:
        add('unresolved.' + key, None)
    return result


def features_for_row(row, *, include_heuristics=True):
    if 'professional_input' not in row:
        raise ValueError('Professional mode requires the V2 source adapter output')
    # Never trust externally precomputed features, explanations or predictions.
    return flatten_bundle(build_bundle(row['professional_input']), include_heuristics=include_heuristics)
