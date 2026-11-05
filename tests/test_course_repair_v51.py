"""Evidence visibility and parent contracts; synthetic software text only."""
from copy import deepcopy
from pathlib import Path
import tempfile,unittest
from unittest.mock import patch
from src.wengua import course_repair_v51 as c
from src.wengua import course_parent_v51 as parent
from src.wengua import course_training_v51 as training
from src.wengua import qwen_course_training_v4 as v4
from tests.test_course_complete_v5 import fixture


class EvidenceRepair(unittest.TestCase):
    def pack(self):
        p=fixture();p.update(dossiers=[],review_notes=[])
        r=p['records'][0];r['task']='supplementary_attributed_case_source'
        p['units'][r['source_ids'][0]]['original_quote']='软件证据甲与乙同时成立；后来才记录软件结果丙。'
        return p

    def test_sources_must_be_visible_in_prompt_not_metadata_only(self):
        p=self.pack();original=deepcopy(p)
        with patch.object(c,'fits',return_value=True):out,audit=c.repair(p,{'target_fixes':{},'additions':[]},object())
        row=out['records'][0];self.assertIn('软件证据甲与乙',row['messages'][1]['content'])
        self.assertIn('来源范围',row['question']);self.assertEqual(p,original)
        self.assertEqual(row['source_mode'],'evidence_visible_historical_reading_not_independent_prediction')
        self.assertEqual(len(audit),len(p['records']))

    def test_numbered_prose_and_heading_with_body_are_never_discarded(self):
        for text in ['（3）软件条件甲；满足后才能断乙。','实例一：软件标题。这里有完整条件。','（2）软件条件甲']:
            self.assertFalse(c.heading_only(text))
        self.assertTrue(c.heading_only('实例一：软件测试'))
        self.assertTrue(c.heading_only('反馈：'))

    def test_layout_filter_preserves_short_prose_and_late_feedback(self):
        text='软件背景。\n| 软件表 |\n后来才补充。\n短句。'
        self.assertEqual(c.prose_only(text),'软件背景。\n后来才补充。\n短句。')

    def test_target_fix_requires_exact_old_answer_and_keeps_raw_source(self):
        p=self.pack();r=p['records'][0];uid=r['source_ids'][0]
        decisions={'target_fixes':{r['id']:{'old_answer':r['answer'],'answer':'软件修订答案。','reason':'人工核对软件来源。'}},'additions':[]}
        with patch.object(c,'fits',return_value=True):out,_=c.repair(p,decisions,object())
        self.assertEqual(out['records'][0]['answer'],'软件修订答案。')
        self.assertEqual(out['units'][uid],p['units'][uid])
        decisions['target_fixes'][r['id']]['old_answer']='wrong'
        with patch.object(c,'fits',return_value=True),self.assertRaisesRegex(ValueError,'precondition'):
            c.repair(p,decisions,object())

    def test_cross_family_training_addition_is_rejected(self):
        p=self.pack();decisions={'target_fixes':{},'additions':[{'turns':[{'role':'user','content':'软件提问。'},
            {'role':'assistant','content':'软件答案。'}],'source_ids':[p['records'][0]['source_ids'][0]],'case_ids':['fixture:heldout']}]}
        with patch.object(c,'fits',return_value=True),self.assertRaisesRegex(ValueError,'holdout leakage'):
            c.repair(p,decisions,object())

    def test_missing_or_probe_parent_cannot_be_used(self):
        with tempfile.TemporaryDirectory(dir=parent.ROOT/'local') as tmp:
            with self.assertRaises((ValueError,FileNotFoundError)):parent.inspect_parent(Path(tmp)/'smoke/adapters/step-2')

    def test_seen_case_ids_are_excluded_even_if_group_alias_differs(self):
        row={'group':'alias','case_ids':['seen-case']}
        pack={'selection_exclusions':{'groups':['canonical'],'case_ids':['seen-case']}}
        self.assertFalse(training.selection_eligible(row,pack))
        self.assertTrue(training.selection_eligible({'group':'new','case_ids':['new-case']},pack))

    def test_development_round_robin_keeps_each_format_in_small_case_pool(self):
        rows=[{'id':str(i),'format':fmt,'group':'same-case'} for i,fmt in enumerate(('foundation_qa','conditional_dialogue','chart_application','complete_case'))]
        selected=training.balanced_rows(rows,4)
        self.assertEqual({r['format'] for r in selected},{r['format'] for r in rows})
        self.assertEqual(len(selected),4)

    def test_parent_rank_and_file_tampering_are_rejected(self):
        b=parent
        from src.wengua.qwen_book_loop_v3 import atomic_json,file_sha
        with tempfile.TemporaryDirectory(dir=parent.ROOT/'local') as tmp:
            job=Path(tmp)/'parent';stage=job/'cycle_01';adapter=stage/'adapters/step-1'
            cfg=v4.load(v4.CONFIG)
            atomic_json(job/'job_contract.json',{'schema':v4.SCHEMA,'config':cfg,'dataset_release_sha256':file_sha(v4.RELEASE)})
            atomic_json(stage/'stage_contract.json',{'schema':v4.SCHEMA,'config':cfg,'job_contract_sha256':file_sha(job/'job_contract.json')})
            atomic_json(adapter/'adapter_config.json',{'base_model_name_or_path':cfg['model_id'],'r':cfg['lora_r'],
                'lora_alpha':cfg['lora_alpha'],'lora_dropout':cfg['lora_dropout'],'target_modules':cfg['target_modules'],'bias':'none','peft_type':'LORA'})
            (adapter/'adapter_model.safetensors').write_bytes(b'software fixture, not model tensors')
            atomic_json(adapter/'book_adapter_receipt.json',{'schema':v4.SCHEMA,'stage_contract_sha256':file_sha(stage/'stage_contract.json'),
                'files':{n:file_sha(adapter/n) for n in parent.ESSENTIAL}})
            proof=parent.inspect_parent(adapter)
            self.assertFalse(proof['optimizer_inherited'])
            phase=Path(tmp)/'phase';parent.snapshot(phase,adapter)
            c=cfg|{'book_parent_snapshot':str(phase/'parent_adapter'),'book_parent_provenance_sha256':file_sha(phase/'parent_provenance.json')}
            parent.verify_snapshot(c)
            with self.assertRaisesRegex(ValueError,'structure'):parent.verify_snapshot(c|{'lora_r':16})
            (phase/'parent_adapter/adapter_model.safetensors').write_bytes(b'changed')
            with self.assertRaisesRegex(ValueError,'changed'):parent.verify_snapshot(c)

    def test_v4_runtime_code_and_release_contract_are_unchanged(self):
        expected=v4.load(v4.storage.ROOT/'docs/audits/qwen_course_v4_20261105/data_and_token_review.json')['new_runtime_code_sha256']
        self.assertEqual(v4.hashes(),expected)
        self.assertNotEqual(training.SCHEMA,v4.SCHEMA)

if __name__=='__main__':unittest.main()
