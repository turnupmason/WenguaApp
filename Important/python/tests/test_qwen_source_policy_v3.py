import unittest
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from src.wengua.qwen_source_policy_v3 import source_eligibility


class BookSourcePolicyV3(unittest.TestCase):
    def setUp(self):
        self.units = {'book:1': {'book_id': 'shenqi', 'anchor': {'status': 'literal_unique'}}}
        self.row = {'source_kind': 'book_or_versioned_user_source_study',
                    'answer': {'summary': '开门大吉，但须结合原文适用条件。',
                               'evidence': [{'citation': 'book:1'}]}}

    def test_book_judgment_words_are_preserved(self):
        self.assertTrue(source_eligibility(self.row, self.units)[0])

    def test_engine_teacher_is_rejected_even_after_grade_words_removed(self):
        self.row['source_kind'] = 'frozen_project_rule_teacher'
        self.row['answer']['summary'] = '病情会改善。'
        self.assertFalse(source_eligibility(self.row, self.units)[0])

    def test_mislabeling_teacher_as_book_does_not_resolve_citation(self):
        self.row['answer']['evidence'] = [{'citation': 'HEALTH_V9_V11'}]
        self.assertFalse(source_eligibility(self.row, self.units)[0])

    def test_one_book_citation_does_not_launder_mixed_teacher(self):
        self.row['answer']['evidence'].append({'citation': 'STRENGTH_200'})
        self.assertFalse(source_eligibility(self.row, self.units)[0])

    def test_unlocated_abstract_remains_pending(self):
        self.units['book:1']['anchor']['status'] = 'abstract_or_unlocated'
        self.assertFalse(source_eligibility(self.row, self.units)[0])

    def test_user_summary_is_retained_for_review_not_book_attribution(self):
        self.units['book:1']['book_id'] = 'user'
        self.assertFalse(source_eligibility(self.row, self.units)[0])

    def test_original_chart_requires_verified_table_join(self):
        self.units['book:1'].update(kind='literal_source_chart_cell', source_sha256='fixture-book-hash')
        self.assertFalse(source_eligibility(self.row,self.units)[0])
        self.units['book:1']['original_table_row_verified']=True
        self.assertTrue(source_eligibility(self.row,self.units)[0])

    def test_withdrawn_v2_is_blocked_before_training_or_resume(self):
        import run_qwen_overnight as worker
        from scripts.qwen_curriculum import run_job
        with TemporaryDirectory() as tmp:
            release=Path(tmp)/'release.json'
            release.write_text(json.dumps({'state':'withdrawn'}))
            with patch.object(worker,'RELEASE',release):
                with self.assertRaisesRegex(ValueError,'book-only'):
                    run_job(None,None,None,resume=True)

    def test_missing_evidence_and_new_unknown_kinds_fail_closed(self):
        self.row['answer']['evidence'] = []
        self.assertFalse(source_eligibility(self.row, self.units)[0])
        self.row['source_kind'] = 'new_unreviewed_teacher'
        self.assertFalse(source_eligibility(self.row, self.units)[0])


if __name__ == '__main__':
    unittest.main()
