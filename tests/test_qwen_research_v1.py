"""Source isolation, retrospective labels, deterministic chart tool, assistant mask."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

from src.wengua.qwen_research import (ROOT, build_pack, check_answer, export_pack, make_prompt,
                                     retrieve, split_for, terms, trusted_chart)
from src.wengua.qwen_finetune import checked_splits, encode_sample, load_config


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
        self.assertEqual(config['model_id'], 'Qwen/Qwen3-32B')
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


if __name__ == '__main__':
    unittest.main()
