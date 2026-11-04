"""Source isolation, retrospective labels, deterministic chart tool, assistant mask."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from src.wengua.qwen_research import (ROOT, build_pack, check_answer, export_pack, make_prompt,
                                     retrieve, split_for, terms, trusted_chart)
from src.wengua.qwen_finetune import assess_gpu_capacity, checked_splits, encode_sample, load_config, train


class QwenResearch(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        (ROOT / 'local').mkdir(exist_ok=True)
        cls.pack = build_pack()

    def test_archive_is_not_relabelled_as_forecast_training(self):
        m = self.pack['manifest']
        self.assertEqual((m['case_count'], m['section_count'], m['author_reasoning_steps']), (194, 43, 1008))
        self.assertEqual(m['forecast_supervision_rows'], 0)
        self.assertFalse(m['production_enabled'])
        self.assertEqual(len(self.pack['case_registry']), 194)
        self.assertEqual(m['sft_tasks']['author_case_reconstruction'], 191)
        for row in self.pack['samples']:
            self.assertFalse(row['eligible_forecast_supervision'])
            self.assertEqual(row['mode'], 'source_study')
            self.assertIsNone(json.loads(row['messages'][-1]['content'])['event_probability'])

    def test_event_and_identical_rule_passages_never_cross_splits(self):
        owners = {}
        passages = {}
        for row in self.pack['samples']:
            self.assertEqual(row['split'], split_for(row['group']))
            self.assertEqual(owners.setdefault(row['group'], row['split']), row['split'])
            if row['task'] == 'source_rule':
                text = json.loads(row['messages'][-1]['content'])['evidence'][0]['statement']
                self.assertEqual(passages.setdefault(text, row['split']), row['split'])
        self.assertEqual(len({r['split'] for r in self.pack['samples']}), 3)

    def test_no_cases_feedback_or_raw_chapters_in_fresh_question_rag(self):
        for question in ('天芮 生门 疾病什么时候好', '失物 找回 现金', '甲子 戊 隐甲'):
            docs = retrieve(self.pack['documents'], question)
            self.assertTrue(docs)
            for doc in docs:
                self.assertTrue(doc['fresh_question_allowed'])
                self.assertEqual(doc['kind'], 'source_assertion')
                self.assertIsNone(doc['event_group'])

    def test_test_case_is_not_reintroduced_via_study_retrieval(self):
        docs = retrieve(self.pack['documents'], '失物 找回 作者 反馈', mode='source_study', limit=12)
        for doc in docs:
            self.assertNotEqual(doc['kind'], 'chapter_reference')
            if doc['event_group']:
                self.assertEqual(doc['split'], 'train')
        training_case = next(d for d in self.pack['documents'] if d['kind'] == 'historical_case' and d['split'] == 'train')
        found = retrieve([training_case], training_case['content'][:100], mode='source_study',
                         exclude_groups=[training_case['event_group']])
        self.assertEqual(found, [])

    def test_question_does_not_gain_an_invented_chart(self):
        messages, docs = make_prompt('天芮星是什么', self.pack['documents'])
        payload = json.loads(messages[-1]['content'])
        self.assertIsNone(payload['program_chart'])
        self.assertIn('missing_chart', payload)
        self.assertEqual({r['id'] for r in payload['references']}, {r['id'] for r in docs})
        chart = trusted_chart({'dun': 'yin', 'ju': 8, 'hour_ganzhi': '己巳'})
        self.assertIsInstance(chart, dict)
        with self.assertRaises(ValueError):
            trusted_chart({'dun': 'yin', 'ju': 8, 'hour_ganzhi': '己巳', 'later_feedback': 'found'})

    def test_bad_citation_and_model_probability_are_rejected(self):
        answer = {'mode': 'traditional_reading', 'summary': '资料不足', 'evidence': [],
                  'counter_evidence': [], 'missing_information': ['无资料'], 'event_probability': None}
        result = check_answer(answer, [], 'traditional_reading')
        self.assertFalse(result['semantic_support_verified'])
        self.assertFalse(result['prediction_validated'])
        bad = deepcopy(answer)
        bad['event_probability'] = 0.8
        with self.assertRaises(ValueError):
            check_answer(bad, [], 'traditional_reading')
        bad = deepcopy(answer)
        bad['evidence'] = [{'citation': 'invented', 'statement': 'fake'}]
        with self.assertRaises(ValueError):
            check_answer(bad, [], 'traditional_reading')

    def test_private_export_hashes_and_no_overwriting(self):
        with tempfile.TemporaryDirectory(dir=ROOT / 'local') as temp:
            target = Path(temp) / 'data'
            manifest = export_pack(target)
            splits, restored = checked_splits(target)
            self.assertEqual(sum(map(len, splits.values())), manifest['sft_rows'])
            self.assertEqual(restored['source_database_sha256'], self.pack['manifest']['source_database_sha256'])
            with self.assertRaises(FileExistsError):
                export_pack(target)
            path = target / 'train.jsonl'
            path.write_text(path.read_text() + '\n', encoding='utf8')
            with self.assertRaisesRegex(ValueError, 'hash mismatch'):
                checked_splits(target)
        with self.assertRaises(ValueError):
            export_pack(ROOT / 'data/illegal_full_book_export')

    def test_chinese_search_and_research_only_config(self):
        self.assertIn('天芮', terms('天芮星不是西文单词'))
        config = load_config()
        self.assertEqual(config['model_id'], 'Qwen/Qwen3-14B')
        self.assertEqual(len(config['revision']), 40)
        self.assertEqual(config['target_modules'], ['q_proj', 'v_proj'])
        self.assertFalse(config['enable_thinking'])


class AssistantMask(unittest.TestCase):
    def test_prompt_mask_and_oversize_exclusion(self):
        class Tokenizer:
            def apply_chat_template(self, messages, *, add_generation_prompt, **kwargs):
                return [1, 2, 3] if add_generation_prompt else [1, 2, 3, 10, 11, 12]
        row = {'messages': [{'role': 'user', 'content': 'q'}, {'role': 'assistant', 'content': 'a'}]}
        encoded, size = encode_sample(row, Tokenizer(), 6)
        self.assertEqual(encoded['labels'], [-100, -100, -100, 10, 11, 12])
        self.assertEqual(size, 6)
        self.assertIsNone(encode_sample(row, Tokenizer(), 5)[0])

    def test_template_mismatch_does_not_train_on_user_prompt(self):
        class BadTokenizer:
            def apply_chat_template(self, messages, *, add_generation_prompt, **kwargs):
                return [1, 2] if add_generation_prompt else [9, 2, 3]
        with self.assertRaisesRegex(ValueError, 'prefix mismatch'):
            encode_sample({'messages': [{}, {}]}, BadTokenizer(), 100)


class ActualGpuCapacity(unittest.TestCase):
    @staticmethod
    def config32():
        return load_config(ROOT / 'configs/qwen32b_v1.json')

    @staticmethod
    def report(total=15.99, free=14.72):
        return {'cuda_available': True, 'current_device_index': 0,
                'cuda_devices': [{'index': 0, 'name': 'NVIDIA GeForce RTX 4080',
                                  'total_gib': total, 'free_gib': free}]}

    def test_reported_4080_cannot_be_mistaken_for_training_ready_4090(self):
        result = assess_gpu_capacity(self.report(), self.config32())
        self.assertEqual(result['status'], 'blocked')
        self.assertIn('RTX 4080', result['reason'])
        self.assertFalse(result['actual_training_fit_verified'])

    def test_16gb_rejection_precedes_dataset_read_and_output_creation(self):
        output = ROOT / 'local/this_blocked_4080_run_must_not_be_created'
        with patch('src.wengua.qwen_finetune.environment_report', return_value=self.report()), \
             patch('src.wengua.qwen_finetune.checked_splits') as read:
            with self.assertRaisesRegex(RuntimeError, 'RTX 4080'):
                train('does_not_exist', output, config_path=ROOT / 'configs/qwen32b_v1.json')
            read.assert_not_called()
            self.assertFalse(output.exists())

    def test_24gb_screen_is_not_training_verification(self):
        result = assess_gpu_capacity(self.report(23.99, 22.0), self.config32())
        self.assertEqual(result['status'], 'ready_for_smoke_test')
        self.assertFalse(result['actual_training_fit_verified'])
        self.assertEqual(assess_gpu_capacity(self.report(23.99, 14.72), self.config32())['status'], 'blocked')

    def test_assessment_uses_selected_gpu_not_a_larger_other_card(self):
        report = self.report()
        report['cuda_devices'].append({'index': 1, 'name': 'Larger GPU', 'total_gib': 80, 'free_gib': 78})
        self.assertEqual(assess_gpu_capacity(report, self.config32())['status'], 'blocked')
        report['current_device_index'] = 1
        self.assertEqual(assess_gpu_capacity(report, self.config32())['status'], 'ready_for_smoke_test')
        self.assertEqual(assess_gpu_capacity({'cuda_available': False}, self.config32())['status'], 'blocked')

    def test_user_authorized_14b_is_default_and_4080_only_passes_startup_screen(self):
        config = load_config()
        self.assertEqual(config['model_id'], 'Qwen/Qwen3-14B')
        self.assertEqual(config['max_seq_length'], 1536)
        result = assess_gpu_capacity(self.report(), config)
        self.assertEqual(result['status'], 'ready_for_smoke_test')
        self.assertFalse(result['actual_training_fit_verified'])
        self.assertEqual(assess_gpu_capacity(self.report(15.99, 9), config)['status'], 'blocked')


if __name__ == '__main__':
    unittest.main()
