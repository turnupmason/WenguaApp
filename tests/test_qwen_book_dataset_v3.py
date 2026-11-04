"""Synthetic plumbing fixture only: its sentences are not actual book claims."""
import csv
import gzip
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from src.wengua.qwen_book_dataset_v3 import (build, export, digest, locate, readable,
    premise_target, wording, variant_question, located_pieces, FORMATS, TABLES)


def fixture():
    concept='测试定义句。还须结合题设条件，不能删除例外。'
    step='测试用神落二宫，另一测试用神落四宫，所以断这是本题作者写出的测试结论。'
    judgment='测试作者初断。'
    text='\n'.join([concept,'','测试原问。','测试盘原行。',step,judgment,'仅后来才知道的反馈标记。'])
    section={'section_id':1,'book_id':'shenqi','section_key':'fixture','title':'测试预测流程',
             'original_text':text,'sha256':digest(text)}
    case={'case_id':'fixture.case','section_id':1,'event_family_id':'fixture.event',
          'domain_id':'fixture','known_before':'不能整段复制：仅后来才知道的反馈标记。',
          'author_judgment':judgment,'later_feedback':'仅后来才知道的反馈标记。'}
    tables={k:[] for k in TABLES};tables.update(sections=[section],cases=[case])
    tables['semantic_assertions']=[{'chapter_key':'shenqi/fixture','concept_id':'star:测试星',
        'kind':'symbol','original_excerpt':concept,'source_start_line':1}]
    tables['historical_case_reasoning']=[{'case_id':'fixture.case','step_number':1,
        'source_line':5,'author_analysis_original':step}]
    tables['historical_chart_cells']=[{'case_id':'fixture.case','palace':i,'source_line':4,
        'palace_label_raw':'测试'+str(i),'star_position_raw':'芮' if i==2 else '测试星',
        'door_position_raw':'测试门','deity_raw':'测试神'} for i in range(1,10)]
    tables['historical_case_phase_events']=[{'case_id':'fixture.case','phase':'initial_question',
        'visible_to_initial_blind_test':1,'original_excerpt':'测试原问。','source_start_line':3},
        {'case_id':'fixture.case','phase':'initial_judgment','visible_to_initial_blind_test':0,
        'original_excerpt':judgment,'source_start_line':6}]
    return tables,{'1':[{'case_id':'fixture.case','lines':[3,7]}]}


class BookDatasetV3(unittest.TestCase):
    def pack(self):
        tables,spans=fixture()
        with patch('src.wengua.qwen_book_dataset_v3.load_tables',return_value=tables):
            return build('unused-fixture',spans)

    def test_book_locator_preserves_original_and_whitespace_coordinates(self):
        section={'original_text':'第一行。\n原 书 条件。\n末行。'}
        self.assertEqual(locate(section,'原书条件。')[0],[2,2])
        self.assertEqual(section['original_text'],'第一行。\n原 书 条件。\n末行。')
        self.assertIsNone(locate(section,'未写的结论')[0])

    def test_sentence_layout_does_not_cut_conditional_at_comma(self):
        self.assertEqual(readable('若甲成立，则乙；否则丙。还须丁。'),'若甲成立，则乙；否则丙。\n还须丁。')

    def test_premise_completion_is_an_exact_author_substring(self):
        text=fixture()[0]['historical_case_reasoning'][0]['author_analysis_original']
        a,b=premise_target(text);self.assertEqual(a+b,text)
        self.assertTrue(b.startswith('所以断'))
        self.assertIsNone(premise_target('短句所以断。'))

    def test_editorial_registry_summary_is_not_taught_as_original_quote(self):
        section={'original_text':'可定位原话。\n原书的另一句。'}
        good,pending=located_pieces(section,'可定位原话。\nEditorial unlocated summary')
        self.assertEqual(good,['可定位原话。'])
        self.assertEqual(pending,['Editorial unlocated summary'])

    def test_all_four_formats_natural_chinese_and_no_scoring_teacher(self):
        pack=self.pack();self.assertEqual({r['format'] for r in pack['records']},set(FORMATS))
        for row in pack['records']:
            self.assertFalse(row['messages'][-1]['content'].startswith('{'))
            self.assertFalse(row['semantic_review_complete'])
        self.assertEqual(len(pack['dossiers'][0]['author_steps']),1)

    def test_initial_view_never_copies_raw_known_before_or_feedback(self):
        row=next(r for r in self.pack()['records'] if r['task']=='explicit_initial_author_response')
        prompt=json.dumps(row['messages'][:-1],ensure_ascii=False)
        self.assertNotIn('仅后来才知道的反馈标记',prompt)
        self.assertEqual(set(row['context']),{'原抄九宫','明确初问背景'})

    def test_source_and_case_groups_are_shared_across_task_formats(self):
        pack=self.pack();owner={}
        for row in pack['records']:
            for uid in row['source_ids']:
                self.assertEqual(owner.setdefault(uid,row['split']),row['split'])
        case_rows=[r for r in pack['records'] if r['case_id']]
        self.assertEqual(len({r['group'] for r in case_rows}),1)

    def test_unknown_case_coordinates_fail_closed(self):
        tables,spans=fixture();spans['1'][0]['case_id']='missing'
        with patch('src.wengua.qwen_book_dataset_v3.load_tables',return_value=tables):
            with self.assertRaisesRegex(ValueError,'Unknown original case'):build('unused',spans)

    def test_unique_wordings_keep_conditions_without_creating_new_facts(self):
        variants={wording('测试问题？',i) for i in range(4096)}
        self.assertEqual(len(variants),4096)
        self.assertTrue(all('测试问题？' in q for q in variants))
        with self.assertRaises(ValueError):wording('测试问题？',4096)

    def test_task_specific_rephrasing_does_not_add_chart_facts(self):
        row=next(r for r in self.pack()['records'] if r['task']=='author_inference_completion')
        q=variant_question(row,1)
        self.assertIn(row['case_id'],q)
        self.assertNotIn('出生',q)
        self.assertNotIn('极大吉',q)

    def test_materialized_pool_and_each_assistant_turn_are_written(self):
        with TemporaryDirectory() as tmp:
            out=Path(tmp)/'out';pack=self.pack();meta=export(pack,out,100,True)
            with gzip.open(out/'million_dialogues.jsonl.gz','rt',encoding='utf8') as f:
                rows=[json.loads(line) for line in f]
            self.assertEqual(len(rows),100);self.assertEqual(len({r['id'] for r in rows}),100)
            self.assertEqual(sum(meta['candidate_formats'].values()),100)
            with gzip.open(out/'assistant_turn_views.jsonl.gz','rt',encoding='utf8') as f:
                views=[json.loads(line) for line in f]
            self.assertGreater(len(views),len(pack['records']))
            self.assertTrue(all(r['messages'][-1]['role']=='assistant' for r in views))
            self.assertFalse(meta['auto_training_enabled'])
            split_rows=[]
            for name in ('train','validation','test'):
                with gzip.open(out/(name+'_dialogues.jsonl.gz'),'rt',encoding='utf8') as f:
                    part=[json.loads(line) for line in f]
                self.assertTrue(all(r['split']==name for r in part))
                split_rows.extend(part)
            self.assertEqual(len(split_rows),100)
            self.assertEqual({r['id'] for r in split_rows},{r['id'] for r in rows})


if __name__=='__main__':unittest.main()
