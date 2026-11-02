"""Source-preserving import and three-valued condition checks for user timing notes.

This module verifies the recorded material. It neither invents chart facts nor
selects a real-world event date. Conditions holding does not approve a rule.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BUNDLE = ROOT / 'data/knowledge/timing_methods/user_notes_20261102'
FORBIDDEN_FACTS = {
    'actual_outcome', 'reported_feedback', 'actual_recovery_date',
    'actual_discharge_date', 'later_diagnosis', 'book_outcome',
    'feedback', 'observed_outcome', 'posterior_diagnosis',
    'reported_result', 'author_outcome', 'validation_label',
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def evaluate_condition(node: dict, facts: dict) -> bool | None:
    """Kleene three-valued eligibility: an unknown prerequisite is not false.

    Only explicit bool/string/int facts are compared; False must not equal 0.
    The caller remains responsible for deriving facts from an actual chart.
    """
    if not isinstance(node, dict) or not isinstance(facts, dict):
        raise ValueError('Need a condition object and a fact dictionary')
    if FORBIDDEN_FACTS.intersection(facts):
        raise ValueError('Posterior feedback cannot be a timing input')
    if set(node) == {'const'} and type(node['const']) is bool:
        return node['const']
    if set(node) in ({'all'}, {'any'}):
        op = next(iter(node))
        children = node[op]
        if not isinstance(children, list) or not children:
            raise ValueError('A compound condition needs nonempty children')
        results = [evaluate_condition(child, facts) for child in children]
        if op == 'all':
            return False if False in results else None if None in results else True
        return True if True in results else None if None in results else False
    if set(node) == {'not'}:
        result = evaluate_condition(node['not'], facts)
        return None if result is None else not result
    if set(node) == {'field', 'eq'}:
        field, expected = node['field'], node['eq']
        if not isinstance(field, str) or type(expected) not in (str, bool, int):
            raise ValueError('Unsupported condition comparison')
        actual = facts.get(field)
        if actual is None:
            return None
        if type(actual) not in (str, bool, int):
            raise ValueError('Chart facts must be explicit scalar values')
        return type(actual) is type(expected) and actual == expected
    raise ValueError('Unknown condition expression')


def load_bundle(folder: Path = BUNDLE) -> dict:
    """Validate hashes, source links, every line, and exception references."""
    folder = Path(folder)
    manifest = json.loads((folder / 'source_manifest.json').read_text('utf8'))
    data = {}
    for name, expected in manifest['assets_sha256'].items():
        if Path(name).name != name:
            raise ValueError('Bundle asset must be a direct child')
        raw = (folder / name).read_bytes()
        if sha256(raw) != expected:
            raise ValueError('Timing asset hash changed: ' + name)
        data[name] = json.loads(raw.decode('utf8'))
    units = data['source_units.json']['units']
    if [x['line'] for x in units] != list(range(1, manifest['source_lines'] + 1)):
        raise ValueError('Missing or duplicated original line')
    cursor = 0
    for unit in units:
        if not cursor == unit['char_start'] <= unit['char_end'] <= unit['line_end']:
            raise ValueError('Original character offsets do not form a full source')
        cursor = unit['line_end']
    if cursor != manifest['unicode_characters']:
        raise ValueError('Original source tail not preserved')
    rules = data['rules.json']['rules']
    by_id = {r['id']: r for r in rules}
    if len(by_id) != len(rules) or len(rules) != manifest['rule_records']:
        raise ValueError('Rule IDs or rule count changed')
    qualifications = data['exceptions_and_duplicates.json']
    conflicts = {x['id'] for x in qualifications['conflicts']}
    illustrations = {x['id'] for x in data['illustrations.json']['illustrations']}
    for actual, key in [(len(conflicts), 'conflict_groups'),
                        (len(illustrations), 'illustrations'),
                        (len(data['domain_contracts.json']['domains']), 'domain_contracts'),
                        (len(qualifications['normalization_candidates']), 'normalization_candidates'),
                        (len(qualifications['duplicate_groups']), 'duplicate_groups')]:
        if actual != manifest[key]:
            raise ValueError('Timing inventory count changed: ' + key)
    for rule in rules:
        if rule['source_id'] != manifest['source_id']:
            raise ValueError('Mixed source provenance')
        if rule['runtime_enabled'] or rule['review_status'] != 'draft':
            raise ValueError('Notes cannot silently become approved live rules')
        if [a['line'] for a in rule['source_anchors']] != rule['source_lines']:
            raise ValueError('Rule source-line and anchor mismatch')
        for anchor in rule['source_anchors']:
            if anchor['sha256'] != units[anchor['line'] - 1]['text_sha256']:
                raise ValueError('Source excerpt receipt mismatch')
        if set(rule['exceptions']) - (conflicts | set(by_id)):
            raise ValueError('Unknown rule exception')
        evaluate_condition(rule['conditions'], {})
    for unit in units:
        if set(unit['rule_ids']) - set(by_id) or set(unit['illustration_ids']) - illustrations:
            raise ValueError('Unknown source coverage reference')
        expected = {r['id'] for r in rules if unit['line'] in r['source_lines']}
        if set(unit['rule_ids']) != expected:
            raise ValueError('A source line lost a normalized rule')
        if unit['kind'] != 'heading' and not (unit['rule_ids'] or unit['illustration_ids']):
            raise ValueError('Unrecorded source line')
    for conflict in qualifications['conflicts']:
        if set(conflict['related_rule_ids']) - set(by_id) or conflict['auto_resolved']:
            raise ValueError('Source conflict silently resolved')
    return {'manifest': manifest, **data}


def validate_original(raw: bytes, bundle: dict) -> str:
    """Verify the exact uploaded bytes as well as each line's receipt."""
    manifest = bundle['manifest']
    if len(raw) != manifest['utf8_bytes'] or sha256(raw) != manifest['source_sha256']:
        raise ValueError('Uploaded original differs; no archive was modified')
    text = raw.decode('utf8')
    if len(text) != manifest['unicode_characters']:
        raise ValueError('Original Unicode length mismatch')
    if len(text.splitlines()) != manifest['source_lines']:
        raise ValueError('Original line count mismatch')
    for unit in bundle['source_units.json']['units']:
        segment = text[unit['char_start']:unit['char_end']]
        if sha256(segment.encode('utf8')) != unit['text_sha256']:
            raise ValueError('Original line hash mismatch')
    source_lines = text.splitlines()
    qualifications = bundle.get('exceptions_and_duplicates.json', {})
    for candidate in qualifications.get('normalization_candidates', []):
        if any(candidate['raw_token'] not in source_lines[n - 1]
               for n in candidate['source_lines']):
            raise ValueError('A candidate correction has an incorrect source line')
    for group in qualifications.get('duplicate_groups', []):
        if group['kind'] == 'exact_duplicate':
            before = ''.join(source_lines[n - 1] for n in group['earlier_lines'])
            after = ''.join(source_lines[n - 1] for n in group['later_lines'])
            if before != after:
                raise ValueError('A claimed exact duplicate is not identical')
    return text


def archive_original(source: Path, destination: Path, folder: Path = BUNDLE) -> dict:
    """Idempotent local-only backup; reject mismatches before writing files.

    User notes are not labelled as a new original-book chapter or full case.
    This deliberately leaves the user's existing historical SQLite untouched.
    """
    bundle = load_bundle(folder)
    raw = Path(source).read_bytes()
    text = validate_original(raw, bundle)
    destination = Path(destination)
    numbered = ''.join(f'{n:03d} {line}\n' for n, line in enumerate(text.splitlines(), 1))
    receipt = {
        'source_id': bundle['manifest']['source_id'], 'sha256': sha256(raw),
        'utf8_bytes': len(raw), 'line_count': len(text.splitlines()),
        'original_preserved_byte_for_byte': True,
        'normalization_applied_to_original': False,
        'note': 'Numbered reading is a copy. Candidate corrections remain separate.',
    }
    contents = {'original.txt': raw, 'numbered_reading.txt': numbered.encode('utf8'),
                'import_receipt.json': (json.dumps(receipt, ensure_ascii=False, indent=2) + '\n').encode('utf8')}
    for name, expected in contents.items():
        path = destination / name
        if path.exists() and path.read_bytes() != expected:
            raise ValueError('Refuse to overwrite previous private source: ' + name)
    destination.mkdir(parents=True, exist_ok=True)
    for name, expected in contents.items():
        path = destination / name
        if not path.exists():
            with path.open('xb') as handle:
                handle.write(expected)
        if path.read_bytes() != expected:
            raise ValueError('Private source reopen verification failed')
    return receipt
