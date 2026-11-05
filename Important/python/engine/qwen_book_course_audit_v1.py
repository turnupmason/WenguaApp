"""Read-only course triage; mechanical checks never approve semantic quality.

Full texts and repair suggestions belong in private local/ exports. The frozen
bookv3 builder and existing training/checkpoint contracts are not modified.
"""
from collections import Counter, defaultdict
import hashlib
import json
import re


STYLE = ('先直接回答问题，再给必要依据。概念题通常一至三句；条件题说清成立条件和例外；'
         '案例题按证据给出分析和结论。只答所问，不复述问题，不加固定开场和结束套话，'
         '不重复句子。不得为简短删掉必要条件，不编造人物、宫位或日期。')

# A confirmed attribution defect, not a claim that every pre-commentary passage
# in the books belongs to a student. Other commentary cases require role review.
CONFIRMED_ROLE_DEFECTS = {'kaiwu.final.weather': {'section_id': 43,
    'student_lines': [416, 418], 'teacher_lines': [439, 445]}}
GENERIC_CONDITION_TASKS = {'book_conditions', 'book_condition_followup',
                           'source_grounded_correction'}
SOURCE_ORGANIZATION_MODES = {'source_assisted_case_application',
                              'complete_source_assisted_author_lesson'}


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                    separators=(',', ':')).encode()).hexdigest()


def scope_proposal(row):
    """Suggest a facet only when the original answer explicitly names it.

    Never infer a new rule or synthesize an answer. A suggestion still needs
    semantic review; unresolvable generic questions remain quarantined.
    """
    if row['task'] != 'book_concept':
        return None
    match = re.match(r'按(《[^》]+》)，(.+)怎样理解？$', row['question'])
    if not match or match[2].startswith('“'):
        return None
    answer = row['answer'].lstrip()
    prefixes = [('在国家', '人物身份'), ('在家庭', '人物身份'),
                ('在场所', '场所'), ('在方位', '方位'), ('在方向', '方位'),
                ('在时间', '时间'), ('在数字', '数字'), ('在动物', '动物'),
                ('在静物', '物品'), ('静物', '物品'), ('在人体', '人体'),
                ('在颜色', '颜色'), ('在五味', '五味'), ('五味', '五味')]
    facet = next((facet for prefix, facet in prefixes if answer.startswith(prefix)), None)
    return f'按{match[1]}，{match[2]}在{facet}方面有哪些象意？' if facet else None


def audit(pack, sections, coordinates):
    records, units, dossiers = pack['records'], pack['units'], pack['dossiers']
    prompt_groups = defaultdict(list)
    for row in records:
        prompt_groups[digest(row['messages'][:-1])].append(row)
    collisions = [rows for rows in prompt_groups.values()
                  if len({r['answer'] for r in rows}) > 1]
    collision_ids = {r['id'] for rows in collisions for r in rows}
    rows_by_case = defaultdict(list)
    for row in records:
        if row.get('case_id'):
            rows_by_case[row['case_id']].append(row)

    commentary = defaultdict(set)
    for sid, spans in coordinates.items():
        lines = sections[int(sid)]['original_text'].splitlines()
        for span in spans:
            lo, hi = span['lines']
            for n in range(lo, hi + 1):
                if '张志春按' in lines[n - 1]:
                    commentary[span['case_id']].add((int(sid), n))

    reviewed = []
    for row in records:
        flags = []
        if row['id'] in collision_ids:
            flags.append('identical_prompt_different_target_scope')
        if row['task'] in GENERIC_CONDITION_TASKS:
            flags.append('specific_condition_question_review_required')
        if row.get('case_id') in CONFIRMED_ROLE_DEFECTS:
            flags.append('confirmed_speaker_misattribution')
        elif row.get('case_id') in commentary and row['source_mode'] != 'literal_chart_reading':
            flags.append('commentary_speaker_review_required')
        context = row.get('context') or {}
        if row['format'] == 'complete_case' and len(context.get('原抄九宫', [])) != 9:
            flags.append('complete_case_without_nine_primary_cells')
        if row['source_mode'] in SOURCE_ORGANIZATION_MODES:
            capability = 'source_organization_not_unseen_chart_reasoning'
        elif row['source_mode'] == 'literal_chart_reading':
            capability = 'literal_chart_reading'
        elif row['source_mode'] == 'explicit_initial_phase_reconstruction':
            capability = 'initial_judgment_reconstruction_not_full_evidence_chain'
        else:
            capability = row['source_mode']
        missing = [sid for sid in row['source_ids'] if sid not in units]
        if missing:
            raise ValueError('Missing source references: ' + row['id'])
        proposal = scope_proposal(row) if row['id'] in collision_ids else None
        reviewed.append({'id': row['id'], 'case_id': row.get('case_id'),
            'format': row['format'], 'task': row['task'], 'split': row['split'],
            'group': row['group'], 'source_ids': row['source_ids'],
            'flags': flags, 'capability_bucket': capability,
            'question_repair_proposal': proposal,
            'answer_preserved': True, 'semantic_review_complete': False,
            'training_eligible': False, 'review_status': 'quarantined' if flags else 'pending_semantic_review'})

    case_reviews = []
    for dossier in dossiers:
        cid = dossier['case_id']
        case_reviews.append({'case_id': cid, 'split': dossier['split'],
            'source_group': dossier['group'], 'domain': dossier['domain'],
            'printed_primary_cells': len(dossier['primary_printed_chart']),
            'registry_author_steps': len(dossier['author_steps']),
            'commentary_markers': sorted(commentary.get(cid, ())),
            'confirmed_role_defect': cid in CONFIRMED_ROLE_DEFECTS,
            'semantic_speaker_and_chronology_review_complete': False,
            'course_rows': len(rows_by_case[cid])})
    counts = Counter(flag for row in reviewed for flag in row['flags'])
    summary = {'schema': 'wengua_book_course_triage_v1', 'core_rows': len(records),
        'case_count': len(dossiers), 'identical_prompt_multi_target_groups': len(collisions),
        'identical_prompt_multi_target_rows': len(collision_ids),
        'affected_training_core_rows': sum(r['split'] == 'train' for rows in collisions for r in rows),
        'flag_counts': dict(counts), 'quarantined_rows': sum(bool(r['flags']) for r in reviewed),
        'pending_semantic_review_rows': sum(not r['flags'] for r in reviewed),
        'scoped_question_repair_proposals': sum(bool(r['question_repair_proposal']) for r in reviewed),
        'cases_with_commentary_markers': len(commentary),
        'capability_counts': dict(Counter(r['capability_bucket'] for r in reviewed)),
        'source_records_digest': digest(records), 'original_book_and_registry_modified': False,
        'all_rows_mechanically_checked': True, 'all_rows_semantically_reviewed': False,
        'approved_training_rows': 0, 'training_ready': False,
        'style_instruction_for_next_course': STYLE,
        'scope_warning': 'A flag is a review requirement, not proof the original book is wrong. '
            'Missing flags do not certify a target. Source-assisted tasks are not blind evaluation.'}
    return {'summary': summary, 'rows': reviewed, 'cases': case_reviews}


def paragraphize(text):
    """Add reading breaks only; no sentence deletion or factual rewriting."""
    return re.sub(r'([。！？])(?=[^\n])', r'\1\n', text)


def candidate_repairs(pack, report):
    originals = {r['id']: r for r in pack['records']}
    candidates = []
    for item in report['rows']:
        question = item['question_repair_proposal']
        if not question or item['case_id'] in CONFIRMED_ROLE_DEFECTS:
            continue
        original = originals[item['id']]
        messages = [dict(m) for m in original['messages']]
        messages[0]['content'] += '\n' + STYLE
        messages[-2]['content'] = question
        messages[-1]['content'] = paragraphize(original['answer'])
        candidates.append({'id': 'course-repair:' + digest([item['id'], question])[:24],
            'original_id': item['id'], 'question': question,
            'answer': messages[-1]['content'], 'messages': messages,
            'source_ids': item['source_ids'], 'split': item['split'], 'group': item['group'],
            'status': 'draft_scoped_question_repair', 'semantic_review_complete': False,
            'training_eligible': False, 'new_facts_added': False})
    return candidates
