"""Fail-closed provenance gate for recovering book material from rejected V3.

This checks source eligibility only; it does not certify answer quality or
license synthetic full-chart conclusions. Never filter classical text by 吉/凶.
"""
LITERAL_ANCHORS = {'literal_unique', 'literal_repeated', 'whitespace_normalized_only'}
BOOK_KINDS = {'book_or_versioned_user_source_study', 'historical_book_reconstruction'}
LEGACY_TEACHERS = {
    'frozen_project_rule_teacher', 'controlled_query_context_pair',
    'abstract_approved_rule_exercise', 'matched_real_chart_pair',
    'versioned_actor_rule_boundary',
}


def source_eligibility(row, source_units):
    kind = row.get('source_kind')
    if kind in LEGACY_TEACHERS:
        return False, 'legacy_engine_or_dependent_teacher'
    if kind not in BOOK_KINDS:
        return False, 'non_book_task_requires_separate_rebuild'
    evidence = row.get('answer', {}).get('evidence', [])
    if not evidence:
        return False, 'no_book_citation'
    for item in evidence:
        unit = source_units.get(item.get('citation'))
        if unit is None or unit.get('book_id') not in {'shenqi', 'kaiwu'}:
            return False, 'non_book_or_unresolved_citation'
        if unit.get('kind') == 'literal_source_chart_cell':
            if unit.get('original_table_row_verified') is not True or not unit.get('source_sha256'):
                return False, 'unverified_original_chart_record'
        elif unit.get('anchor', {}).get('status') not in LITERAL_ANCHORS:
            return False, 'book_anchor_not_literal_located'
    return True, 'located_book_material_not_training_approval'
