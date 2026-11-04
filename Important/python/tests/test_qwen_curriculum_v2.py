import copy
import json
from pathlib import Path
import tempfile
import unittest

from src.wengua.qwen_curriculum_v2 import (build_curriculum, audit_curriculum, SOURCE_SHA,
    source_position, fact_supported, fit_training_view, substantive, qualified_summary)
from src.wengua.qwen_curriculum_train import (stage_contract, validate_stage_directory,
    latest_checkpoint, select_grouped, measure_answer, seal_checkpoint)
from src.wengua.qwen_research import ROOT, SOURCE_DB, digest, json_text
from scripts.qwen_curriculum import config_checked, job_contract


class DialogueSourceContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pack=build_curriculum()

    def test_source_archive_and_all_original_events_preserved(self):
        self.assertEqual(digest(SOURCE_DB.read_bytes()),SOURCE_SHA)
        self.assertEqual(len(self.pack['cases']),194)
        self.assertEqual(len(self.pack['source_tables']['sections']),43)
        self.assertTrue(audit_curriculum(self.pack)['passed'])
        self.assertGreater(len(self.pack['samples']),10000)
        self.assertGreater(self.pack['manifest']['source_database_table_inventory']['semantic_assertions'],2000)
        coverage={s['section_id']:s for s in self.pack['manifest']['section_index_coverage']}
        for sid in (1,4):self.assertGreater(coverage[sid]['indexed_assertion_or_author_lines'],0)

    def test_author_paragraphs_are_not_rewritten_or_invented(self):
        original=self.pack['source_tables']['historical_case_reasoning']
        units={u['id']:u for u in self.pack['units']}
        self.assertEqual(len(original),1008)
        for step in original:
            unit=units[f"author:{step['case_id']}:step:{step['step_number']}"]
            self.assertEqual(unit['text'],step['author_analysis_original'])
            self.assertNotEqual(unit['anchor']['status'],'abstract_or_unlocated')

    def test_all_case_ranges_located_including_reprints_and_three_without_steps(self):
        located={s['case_id'] for ranges in self.pack['case_spans'].values() for s in ranges}
        self.assertEqual(located,{c['case_id'] for c in self.pack['cases']})
        self.assertEqual(sum(c['reasoning_steps']==0 for c in self.pack['cases']),3)

    def test_identical_source_evidence_never_crosses_event_or_passage_holdouts(self):
        units={u['id']:u for u in self.pack['units']};owner={}
        for row in self.pack['samples']:
            for uid in row['source_ids']:
                text=units[uid]['text']
                if len(text)>=80:
                    key=digest(text)
                    self.assertEqual(owner.setdefault(key,row['split']),row['split'],uid)
        # Shared divorce/remarriage letter is one conservative evidence group.
        cases={r['case_id']:r for r in self.pack['cases']}
        self.assertEqual(cases['kaiwu.final.divorce']['evidence_component'],cases['kaiwu.final.remarriage']['evidence_component'])

    def test_general_retrieval_does_not_include_case_specific_rules(self):
        corpus=self.pack['corpus']
        self.assertTrue(any(d['fresh_question_allowed'] for d in corpus))
        for d in corpus:
            if d['kind']=='historical_case':self.assertFalse(d['fresh_question_allowed'])
        self.assertFalse(any(u['anchor']['status']=='abstract_or_unlocated'
            for u in self.pack['units'] if u['id'] in {d['id'] for d in corpus}))

    def test_ambiguous_metadata_does_not_become_lookup_gold(self):
        self.assertFalse(fact_supported('element','金',{},'图13 十天干与五方对应'))
        self.assertFalse(fact_supported('branch','亥',{'stem':'甲','stage':'长生','branch':'亥'},'甲在亥地，但本句未记长生。'))
        self.assertTrue(fact_supported('branch','亥',{'stem':'甲','stage':'长生','branch':'亥'},'甲木长生在亥。'))
        self.assertFalse(substantive('见(图27)。'))
        self.assertIn('但是必须先分清人物关系',qualified_summary('先看本人的用神。',
                          '先看本人的用神。但是必须先分清人物关系，不能任意替换。'))
        self.assertTrue(any(i['issue']=='normalized_field_not_literally_supported_for_lookup' for i in self.pack['source_issues']))

    def test_repeated_source_location_and_original_line_numbers(self):
        s={'original_text':'原句。\n别句。\n原句。'}
        self.assertEqual(source_position(s,'原句。',[3,3])['lines'],[3,3])
        self.assertEqual(source_position(s,'原 句。')['status'],'whitespace_normalized_only')
        self.assertEqual(source_position(s,'编辑摘要')['status'],'abstract_or_unlocated')

    def test_dialogues_distinguish_contexts_and_use_consistent_json_arrays(self):
        rows={r['id']:r for r in self.pack['samples']}
        self.assertIn('domain:business_borrow',rows)
        self.assertEqual([m['role'] for m in rows['domain:business_borrow']['messages']],
                         ['system','user','assistant','user','assistant'])
        switches=[r for r in rows.values() if r['task']=='role_context_switch']
        self.assertEqual(len(switches),1)
        self.assertIn('不是父病一律日干',json.loads(switches[0]['messages'][-1]['content'])['summary'])
        for row in rows.values():
            for m in row['messages']:
                if m['role']=='assistant':
                    a=json.loads(m['content']);self.assertIsNone(a['event_probability'])
                    for k in ['evidence','missing_information','counter_evidence']:self.assertIsInstance(a[k],list)

    def test_oversize_author_reading_view_keeps_entire_original_paragraph(self):
        class Tokenizer:
            def apply_chat_template(self,messages,add_generation_prompt,**kwargs):
                text=''.join(m['role']+':'+m['content']+'|' for m in messages)
                if add_generation_prompt:text+='assistant:'
                return list(text)
        row=copy.deepcopy(next(r for r in self.pack['samples'] if r['task']=='author_stage'))
        row['messages'][-2]['content']+='原盘冗长上下文'*1000
        before=json_text(row);quote=json.loads(row['messages'][-1]['content'])['evidence'][0]['statement']
        view,encoded,audit=fit_training_view(row,Tokenizer(),1800)
        self.assertIsNotNone(encoded)
        self.assertEqual(audit['action'],'intact_author_paragraph_view')
        self.assertIn(quote,view['messages'][-2]['content'])
        self.assertEqual(json_text(row),before)


class CheckpointContracts(unittest.TestCase):
    def test_only_identical_data_stage_config_can_resume(self):
        (ROOT/'local').mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=ROOT/'local') as temp:
            path=Path(temp)/'stage';rows=[{'encoded':{'input_ids':[1,2]}}]
            contract=stage_contract(rows,{'seed':1},'knowledge',2)
            validate_stage_directory(path,contract)
            self.assertEqual(validate_stage_directory(path,contract,resume=True),path.resolve())
            changed=stage_contract(rows,{'seed':2},'knowledge',2)
            with self.assertRaisesRegex(ValueError,'contract mismatch'):validate_stage_directory(path,changed,resume=True)
            with self.assertRaises(FileExistsError):validate_stage_directory(path,contract)

    def test_partial_checkpoint_is_not_restorable(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp);valid=path/'trainer/checkpoint-25';valid.mkdir(parents=True)
            (path/'stage_contract.json').write_text('{}')
            for name in ('adapter_model.safetensors','adapter_config.json','trainer_state.json','optimizer.pt','scheduler.pt','rng_state.pth'):
                (valid/name).write_text('fixture')
            seal_checkpoint(path,valid)
            partial=path/'trainer/checkpoint-50';partial.mkdir();(partial/'trainer_state.json').write_text('{}')
            self.assertEqual(latest_checkpoint(path),valid)
            (valid/'optimizer.pt').write_text('changed after receipt')
            self.assertIsNone(latest_checkpoint(path))

    def test_development_sampling_and_schema_checks_do_not_claim_semantics(self):
        rows=[{'id':str(i),'group':str(i//2),'task':str(i%3)} for i in range(12)]
        chosen=select_grouped(rows,4)
        self.assertEqual(len({r['group'] for r in chosen}),4)
        self.assertEqual(chosen,select_grouped(rows,4))
        row=build_curriculum()['samples'][0]
        result=measure_answer(row['messages'][-1]['content'],row)
        self.assertTrue(result['schema_and_citation_passed']);self.assertFalse(result['semantic_correctness_verified'])
        answer=json.loads(row['messages'][-1]['content']);answer['missing_information']='错误类型'
        self.assertFalse(measure_answer(json_text(answer),row)['schema_and_citation_passed'])

    def test_job_is_fresh_base_and_bounded_not_continued_old_adapter(self):
        config=config_checked();contract=job_contract(config)
        self.assertEqual(contract['initial_model'],'fresh_official_base_not_old_v1_adapter')
        self.assertEqual(config['epochs'],1)
        self.assertLessEqual(sum(config['stage_max_steps'].values()),1200)


if __name__=='__main__':unittest.main()
