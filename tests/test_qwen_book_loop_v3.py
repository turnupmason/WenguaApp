import json
from pathlib import Path
from tempfile import TemporaryDirectory
import time
import unittest
from unittest.mock import patch

from src.wengua.qwen_book_loop_v3 import (ROOT,SCHEMA,load_config,open_job,job_lock,
    target_views,select_best,answer_diagnostic,seal_checkpoint,checkpoint_latest,CKPT_REQUIRED,prepare,generation_rows,
    atomic_json,generate_rows,run_auto,is_cuda_oom,load_book_cuda,official_model_cached,load_book_tokenizer)


class BookLoopContracts(unittest.TestCase):
    def setUp(self):
        (ROOT/'local').mkdir(exist_ok=True)

    def test_old_configs_and_external_adapters_are_rejected(self):
        with self.assertRaises(ValueError):load_config(ROOT/'configs/qwen14b_curriculum_v2.json')
        c=load_config();c['initial_adapter']='old-adapter'
        with TemporaryDirectory() as tmp:
            p=Path(tmp)/'config.json';atomic_json(p,c)
            with self.assertRaisesRegex(ValueError,'adapter/teacher'):load_config(p)

    def test_new_job_cannot_resume_legacy_or_changed_optimizer_schedule(self):
        with TemporaryDirectory(dir=ROOT/'local') as tmp:
            path=Path(tmp)/'job';c=load_config();open_job(path,c)
            self.assertEqual(open_job(path,c,resume=True),path)
            with self.assertRaises(FileExistsError):open_job(path,c)
            changed=dict(c,cycles=2)
            with self.assertRaises(ValueError):open_job(path,changed,resume=True)
            data=json.loads((path/'job_contract.json').read_text());self.assertIsNone(data['initial_adapter'])

    def test_os_job_lock_releases_after_exception(self):
        with TemporaryDirectory() as tmp:
            path=Path(tmp)/'lock'
            with self.assertRaises(RuntimeError):
                with job_lock(path):raise RuntimeError('fixture interruption')
            with job_lock(path):pass

    def test_each_assistant_turn_is_supervised_without_changing_sources(self):
        r={'id':'test','group':'g','split':'train','format':'conditional_dialogue',
            'source_ids':['book1'],'case_id':None,'source_mode':'fixture','task':'fixture',
            'question':'后问？','messages':[{'role':'system','content':'s'},{'role':'user','content':'前问？'},
            {'role':'assistant','content':'前答。'},{'role':'user','content':'后问？\n资料：条件'},
            {'role':'assistant','content':'后答。'}]}
        a=list(target_views(r,0));b=list(target_views(r,1))
        self.assertEqual(len(a),2);self.assertEqual(a[0]['messages'][-1]['content'],'前答。')
        self.assertEqual(a[-1]['messages'][-1],b[-1]['messages'][-1])
        self.assertTrue(b[-1]['messages'][-2]['content'].endswith('\n资料：条件'))

    def test_test_answers_never_select_best_checkpoint(self):
        c=load_config();rows=[{'state':'complete','cycle':1,'validation_loss':1.1,'test_score':0},
                             {'state':'complete','cycle':2,'validation_loss':1.3,'test_score':100},
                             {'state':'complete','cycle':3,'validation_loss':1.4,'test_score':1000}]
        best,stop=select_best(rows,c);self.assertEqual(best['cycle'],1);self.assertTrue(stop)
        d=answer_diagnostic('不同写法','原书表达');self.assertFalse(d['semantic_correctness_verified'])

    def test_corrupt_or_partial_checkpoint_is_not_resumed(self):
        with TemporaryDirectory() as tmp:
            stage=Path(tmp);atomic_json(stage/'stage_contract.json',{'source':'book-fixture'})
            cp=stage/'trainer/checkpoint-2';cp.mkdir(parents=True)
            for name in CKPT_REQUIRED:(cp/name).write_text('fixture')
            seal_checkpoint(stage,cp);self.assertEqual(checkpoint_latest(stage),cp)
            (cp/'optimizer.pt').write_text('changed');self.assertIsNone(checkpoint_latest(stage))

    def test_changed_prepared_tokens_fail_before_model_loading(self):
        with TemporaryDirectory() as tmp:
            job=Path(tmp);p=job/'prepared';p.mkdir()
            (p/'cycle_01.jsonl.gz').write_bytes(b'changed')
            c=load_config();atomic_json(p/'receipt.json',{'config':c,'file_sha256':{'cycle_01.jsonl.gz':'wrong'}})
            with self.assertRaisesRegex(ValueError,'Prepared data changed'):prepare(job,c)

    def test_interrupted_preparation_is_archived_only_before_training(self):
        c=load_config()
        with TemporaryDirectory() as tmp:
            job=Path(tmp);prepared=job/'prepared';prepared.mkdir();(prepared/'partial.txt').write_text('preserve')
            with patch('src.wengua.qwen_book_loop_v3.build',side_effect=ValueError('fixture stop after archive')):
                with self.assertRaisesRegex(ValueError,'fixture stop'):prepare(job,c,tokenizer=object())
            backups=list(job.glob('prepared.incomplete-*'));self.assertEqual(len(backups),1)
            self.assertEqual((backups[0]/'partial.txt').read_text(),'preserve')
            prepared.mkdir();(job/'cycle_01').mkdir()
            with self.assertRaisesRegex(ValueError,'receipt missing'):prepare(job,c,tokenizer=object())

    def test_generation_does_not_truncate_reference_answers_to_fit(self):
        class Tokens:
            def apply_chat_template(self,*args,**kwargs):return [1]*8
            def encode(self,text,**kwargs):return list(text)
        rows=[{'id':'long','answer':'x'*100,'messages':[{'role':'user','content':'q'},{'role':'assistant','content':'a'}]},
              {'id':'short','answer':'short','messages':[{'role':'user','content':'q'},{'role':'assistant','content':'a'}]}]
        c=load_config();c.update(eval_max_new_tokens=32,inference_max_context=256)
        accepted,skips=generation_rows(rows,Tokens(),c)
        self.assertEqual([r['id'] for r in accepted],['short'])
        self.assertEqual(skips[0]['reason'],'whole_reference_answer_exceeds_response_budget')
        self.assertEqual(rows[0]['answer'],'x'*100)

    def test_only_cuda_oom_triggers_shorter_context_fallback(self):
        self.assertTrue(is_cuda_oom(RuntimeError('CUDA out of memory')))
        self.assertFalse(is_cuda_oom(ValueError('wrong source database')))
        self.assertFalse(is_cuda_oom(OSError('disk full')))

    def test_context_fallback_does_not_hide_source_or_disk_errors(self):
        c=load_config()
        with TemporaryDirectory(dir=ROOT/'local') as tmp:
            path=Path(tmp)/'auto'
            calls=[]
            def probe(job,name,config,deadline,**kwargs):
                calls.append(config['max_seq_length'])
                if config['max_seq_length']==4096:raise RuntimeError('CUDA out of memory')
                return {'state':'complete','cycle':0}
            with patch('src.wengua.qwen_book_loop_v3.prepare',return_value={}), patch('src.wengua.qwen_book_loop_v3.train_unit',side_effect=probe), patch('src.wengua.qwen_book_loop_v3.run_loop',return_value={'state':'complete'}):
                run_auto(path,c,time.time()+3600,cpu_factory=lambda:None)
            self.assertEqual(calls,[4096,2048])
            self.assertEqual(json.loads((path/'selected_config.json').read_text())['max_seq_length'],2048)
        with TemporaryDirectory(dir=ROOT/'local') as tmp:
            with patch('src.wengua.qwen_book_loop_v3.prepare',side_effect=ValueError('wrong source')), patch('src.wengua.qwen_book_loop_v3.train_unit') as train:
                with self.assertRaisesRegex(ValueError,'wrong source'):
                    run_auto(Path(tmp)/'auto',c,time.time()+3600,cpu_factory=lambda:None)
                train.assert_not_called()

    def test_cached_model_is_offline_and_only_cache_miss_allows_download(self):
        from types import SimpleNamespace
        model=SimpleNamespace(config=SimpleNamespace(use_cache=True));c=load_config()
        with patch('src.wengua.qwen_book_loop_v3.official_model_cached',return_value=True), patch('src.wengua.qwen_finetune.load_cuda_base',return_value=(model,'dtype')) as loader:
            result,_=load_book_cuda(c,True)
            loader.assert_called_once_with(c,training=False,allow_download=False)
            self.assertFalse(result.config.use_cache)
        with patch('src.wengua.qwen_book_loop_v3.official_model_cached',return_value=False), patch('src.wengua.qwen_finetune.load_cuda_base',return_value=(model,'dtype')) as loader:
            load_book_cuda(c,True)
            loader.assert_called_once_with(c,training=False,allow_download=True)
        with patch('src.wengua.qwen_book_loop_v3.official_model_cached',return_value=True), patch('src.wengua.qwen_finetune.load_cuda_base',side_effect=OSError('corrupt disk')) as loader:
            with self.assertRaisesRegex(OSError,'corrupt disk'):load_book_cuda(c,True)
            self.assertEqual(loader.call_count,1)

    def test_tokenizer_cache_avoids_optional_hub_requests(self):
        from types import SimpleNamespace
        from unittest.mock import Mock
        import sys
        with TemporaryDirectory() as tmp:
            root=Path(tmp)
            for name in ('tokenizer.json','tokenizer_config.json'):(root/name).write_text('fixture')
            hub=SimpleNamespace(try_to_load_from_cache=lambda repo,name,revision:str(root/name))
            loader=Mock(return_value='fixture-tokenizer');transformers=SimpleNamespace(AutoTokenizer=SimpleNamespace(from_pretrained=loader))
            with patch.dict(sys.modules,{'huggingface_hub':hub,'transformers':transformers}):
                load_book_tokenizer(load_config());self.assertTrue(loader.call_args.kwargs['local_files_only'])
                (root/'tokenizer.json').unlink()
                load_book_tokenizer(load_config());self.assertFalse(loader.call_args.kwargs['local_files_only'])
                self.assertFalse(loader.call_args.kwargs['trust_remote_code'])

    def test_all_pinned_weight_shards_must_exist_before_offline_loading(self):
        from types import SimpleNamespace
        import sys
        with TemporaryDirectory() as tmp:
            root=Path(tmp)
            for name in ('config.json','part1.safetensors','part2.safetensors'):(root/name).write_text('fixture')
            atomic_json(root/'model.safetensors.index.json',{'weight_map':{'a':'part1.safetensors','b':'part2.safetensors'}})
            hub=SimpleNamespace(try_to_load_from_cache=lambda repo,name,revision:str(root/name))
            with patch.dict(sys.modules,{'huggingface_hub':hub}):
                self.assertTrue(official_model_cached(load_config()))
                (root/'part2.safetensors').unlink()
                self.assertFalse(official_model_cached(load_config()))
                atomic_json(root/'model.safetensors.index.json',{'weight_map':{}})
                with self.assertRaisesRegex(ValueError,'corrupt'):official_model_cached(load_config())

    def test_cli_has_bounded_resumable_windows_entry(self):
        text=(ROOT/'run_book_training_windows.cmd').read_text()
        self.assertIn('--cycles 6 --hours 48 --resume',text)
        self.assertIn('local\\qwen_env\\Scripts\\python.exe',text)
        self.assertIn('cd /d "%~dp0"',text)


if __name__=='__main__':unittest.main()
