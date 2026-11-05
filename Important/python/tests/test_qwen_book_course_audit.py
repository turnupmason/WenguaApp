import contextlib
import io
import unittest
from unittest.mock import patch

from scripts.qwen8b_diagnostic import main
from src.wengua.qwen_book_course_audit_v1 import audit, candidate_repairs


class CourseAudit(unittest.TestCase):
    def fixture(self):
        rows = []
        for n, answer in enumerate(['在方位为某方。', '在人体为某部位。']):
            question = '按《测试书》，某卦怎样理解？'
            rows.append({'id': str(n), 'question': question, 'answer': answer,
                'task':'book_concept','case_id':None,'format':'foundation_qa','source_mode':'book_knowledge',
                'source_ids':['source'],'split':'train','group':'same-source',
                'messages':[{'role':'system','content':'fixture'}, {'role':'user','content':question},
                            {'role':'assistant','content':answer}]})
        return {'records':rows,'units':{'source':{}},'dossiers':[]}

    def test_identical_prompt_different_facets_are_flagged_and_repaired_without_new_facts(self):
        pack = self.fixture(); report = audit(pack, {}, {})
        self.assertEqual(report['summary']['identical_prompt_multi_target_groups'],1)
        self.assertEqual(report['summary']['affected_training_core_rows'],2)
        repairs = candidate_repairs(pack,report)
        self.assertEqual(len(repairs),2)
        self.assertNotEqual(repairs[0]['question'],repairs[1]['question'])
        for original,repair in zip(pack['records'],repairs):
            self.assertEqual(original['answer'],repair['answer'])
            self.assertEqual(original['split'],repair['split'])
            self.assertEqual(original['group'],repair['group'])
            self.assertFalse(repair['training_eligible'])
        self.assertFalse(report['summary']['training_ready'])

    def test_unflagged_is_pending_not_semantically_approved(self):
        pack = self.fixture(); pack['records'] = pack['records'][:1]
        report = audit(pack,{}, {})
        self.assertFalse(report['rows'][0]['flags'])
        self.assertFalse(report['rows'][0]['training_eligible'])
        self.assertFalse(report['rows'][0]['semantic_review_complete'])

    def test_confirmed_speaker_issue_is_quarantined_and_other_commentaries_only_require_review(self):
        pack = self.fixture()
        for row,cid in zip(pack['records'],['kaiwu.final.weather','other-case']):
            row['case_id']=cid
        report = audit(pack,{43:{'original_text':'张志春按：'}},
                       {'43':[{'case_id':'other-case','lines':[1,1]}]})
        self.assertIn('confirmed_speaker_misattribution',report['rows'][0]['flags'])
        self.assertIn('commentary_speaker_review_required',report['rows'][1]['flags'])
        self.assertNotIn('confirmed_speaker_misattribution',report['rows'][1]['flags'])
        self.assertEqual(len(candidate_repairs(pack,report)),1)

    def test_training_pause_happens_before_hub_or_cuda_imports(self):
        with patch('sys.modules',{'scripts.qwen8b_research':None}), contextlib.redirect_stderr(io.StringIO()) as err:
            self.assertEqual(main(['run','--resume']),3)
            self.assertEqual(main(['--output','local/existing','--hours','168','run','--resume']),3)
        self.assertIn('课程已暂停',err.getvalue())

    def test_missing_source_fails_instead_of_approving(self):
        pack=self.fixture();pack['units']={}
        with self.assertRaises(ValueError):audit(pack,{}, {})

    def test_same_question_with_different_supplied_conditions_is_not_a_collision(self):
        pack=self.fixture()
        pack['records'][0]['messages'][-2]['content']+='\n已知条件：甲。'
        pack['records'][1]['messages'][-2]['content']+='\n已知条件：乙。'
        report=audit(pack,{}, {})
        self.assertEqual(report['summary']['identical_prompt_multi_target_groups'],0)

    def test_supplied_author_answers_are_not_classified_as_independent_reasoning(self):
        pack=self.fixture();row=pack['records'][0]
        row.update(format='complete_case',source_mode='complete_source_assisted_author_lesson',context={'原抄九宫':[]})
        report=audit(pack,{}, {})
        self.assertEqual(report['rows'][0]['capability_bucket'],'source_organization_not_unseen_chart_reasoning')
        self.assertIn('complete_case_without_nine_primary_cells',report['rows'][0]['flags'])

    def test_counting_cases_does_not_create_nonexistent_commentaries(self):
        pack=self.fixture()
        pack['dossiers']=[{'case_id':'no-commentary','split':'train','group':'same-source',
            'domain':'fixture','primary_printed_chart':[],'author_steps':[]}]
        report=audit(pack,{}, {})
        self.assertEqual(report['summary']['cases_with_commentary_markers'],0)
        self.assertEqual(report['cases'][0]['commentary_markers'],[])


if __name__=='__main__':unittest.main()
