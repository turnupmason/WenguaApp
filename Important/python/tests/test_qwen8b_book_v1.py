from copy import deepcopy
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import time
import unittest
from unittest.mock import patch

from src.wengua import qwen_book_loop_v3 as old_book
from src.wengua import qwen_book_continuous_v1 as old_engine
from src.wengua import qwen_book_sweep_v2 as old_sweep
from src.wengua.qwen8b_book_v1 import profile,validate,stress_rows,MODEL,REVISION,SWEEP_SCHEMA
from src.wengua.qwen8b_process_v1 import launch,execution,pressure_signature
from scripts import qwen8b_research as cli
from types import SimpleNamespace
from unittest.mock import Mock
import sys
from types import ModuleType
from src.wengua.qwen8b_loss_v1 import memory_trainer


class Qwen8BProfile(unittest.TestCase):
    def setUp(self):
        (old_book.ROOT/'local').mkdir(exist_ok=True);self.p=profile();self.c=self.p.engine.base_config()

    def test_pinned_8b_plan_has_100_update_pressure_and_nine_max_configs(self):
        plan=self.p.sweep.plan(self.p.book.read_json(self.p.sweep.SPEC))
        self.assertEqual(len(plan['structures']),4);self.assertEqual(plan['maximum_distinct_trials'],9)
        for c in plan['structures']:
            self.assertEqual(c['model_id'],MODEL);self.assertEqual(c['revision'],REVISION)
            self.assertEqual(c['smoke_steps'],100);self.assertEqual(c['num_train_epochs'],5)
            self.assertFalse(c['optimizer_reset_between_epochs']);self.assertEqual(c['loss_chunk_tokens'],128)

    def test_model_bound_namespaces_do_not_mutate_14b_and_decorated_locks_work(self):
        second=profile()
        self.assertIs(old_engine.book,old_book);self.assertIs(old_sweep.engine,old_engine)
        self.assertIs(self.p.engine.book,self.p.book);self.assertIs(self.p.sweep.engine,self.p.engine)
        self.assertIsNot(self.p.book,second.book)
        self.assertEqual(old_book.load_config()['model_id'],'Qwen/Qwen3-14B')
        self.assertEqual(self.p.book.load_config()['model_id'],MODEL)
        with TemporaryDirectory(dir=old_book.ROOT/'local') as tmp:
            with self.p.book.job_lock(Path(tmp)/'lock'):pass

    def test_14b_revision_legacy_teachers_and_short_real_probe_rejected(self):
        for key,value in [('model_id','Qwen/Qwen3-14B'),('revision','main'),('smoke_steps',2),('old_adapters_allowed',True),('non_book_teachers_allowed',True),('initial_adapter','old'),('attention_mode','math')]:
            with self.subTest(key=key),self.assertRaises(ValueError):validate(self.c|{key:value})
        validate(self.c|{'smoke_steps':2},testing=True)

    def test_pressure_mixes_lengths_dense_targets_formats_without_duplication(self):
        rows=[]
        for i in range(2000):
            length=128+i;count=min(length,i%257+1)
            rows.append({'id':str(i),'tokens':length,'format':str(i%4),'encoded':{'labels':[-100]*(length-count)+[1]*count}})
        rows.append({'id':'dense','tokens':1000,'format':'3','encoded':{'labels':[1]*1000}})
        selected=stress_rows(rows,100,16)
        self.assertEqual(len(selected),1600);self.assertEqual(len({r['id'] for r in selected}),1600)
        self.assertIn('dense',{r['id'] for r in selected});self.assertIn('1999',{r['id'] for r in selected})
        self.assertLess(min(r['tokens'] for r in selected),500)
        self.assertEqual(len({r['format'] for r in selected}),4)
        self.assertEqual([r['id'] for r in selected],[r['id'] for r in stress_rows(rows,100,16)])

    def test_pressure_reuse_signature_changes_on_structure_not_learning_rate(self):
        p=profile(testing=True)
        with TemporaryDirectory(dir=old_book.ROOT/'local') as tmp:
            job=Path(tmp);(job/'prepared').mkdir()
            for name in ('smoke.jsonl.gz','validation_loss.jsonl.gz'):(job/'prepared'/name).write_bytes(b'fixture')
            a=pressure_signature(job,self.c,p)
            self.assertEqual(a,pressure_signature(job,self.c|{'learning_rate':2e-5,'lora_dropout':0.01,'warmup_ratio':0.03},p))
            self.assertNotEqual(a,pressure_signature(job,self.c|{'lora_r':16,'lora_alpha':32},p))

    def test_8b_cannot_adopt_14b_root_or_job(self):
        with TemporaryDirectory(dir=old_book.ROOT/'local') as tmp:
            root=Path(tmp);old_book.atomic_json(root/'sweep_contract.json',{'schema':old_sweep.SCHEMA})
            with self.assertRaisesRegex(ValueError,'14B'):execution(root,self.p)
            self.assertFalse((root/'process_execution.json').exists())
            job=self.p.engine.open_job(root/'trial',self.c,resume=False)
            with self.assertRaises(ValueError):old_engine.open_job(job,old_engine.base_config(),resume=True)

    def test_actual_fresh_8b_worker_transport_without_torch_in_base_or_venv(self):
        p=profile(testing=True);c=p.engine.base_config()|{'smoke_steps':2}
        with TemporaryDirectory(dir=old_book.ROOT/'local') as tmp,patch.dict(os.environ,{'HF_HUB_OFFLINE':'1'}):
            root=Path(tmp);old_book.atomic_json(root/'sweep_contract.json',{'schema':SWEEP_SCHEMA})
            job=p.engine.open_job(root/'trials'/'fixture',c,resume=False)
            first=launch(p,job,c,time.time()+3600,'ping');second=launch(p,job,c,time.time()+3600,'ping')
            self.assertNotEqual(first['pid'],os.getpid());self.assertNotEqual(first['pid'],second['pid'])
            self.assertFalse(first['torch_imported']);self.assertEqual(first['offline'],'1')

    def test_download_retries_network_reset_using_same_pinned_cache(self):
        download=Mock(side_effect=[ConnectionResetError(10054,'reset'),None]);wait=Mock();book=SimpleNamespace(progress=Mock())
        with patch.object(cli,'cache_ready',side_effect=[False,False,True]):
            cli.download_cached_model(book,{},download=download,retryable=lambda e:isinstance(e,ConnectionResetError),wait=wait)
        self.assertEqual(download.call_count,2);wait.assert_called_once_with(5)
        self.assertEqual(download.call_args_list[0],download.call_args_list[1])
        kwargs=download.call_args.kwargs
        self.assertEqual(kwargs['revision'],REVISION);self.assertEqual(kwargs['repo_id'],MODEL)
        self.assertEqual(kwargs['max_workers'],1);self.assertNotIn('force_download',kwargs)

    def test_download_complete_cache_skips_network_and_permanent_failure_is_not_retried(self):
        download=Mock();book=SimpleNamespace(progress=Mock());wait=Mock()
        with patch.object(cli,'cache_ready',return_value=True):
            cli.download_cached_model(book,{},download=download,retryable=lambda e:True,wait=wait)
        download.assert_not_called();wait.assert_not_called()
        download.side_effect=PermissionError('denied')
        with patch.object(cli,'cache_ready',return_value=False),self.assertRaises(PermissionError):
            cli.download_cached_model(book,{},download=download,retryable=lambda e:False,wait=wait)
        self.assertEqual(download.call_count,1);wait.assert_not_called()

    def test_persistent_download_failure_is_bounded_and_never_signals_training_started(self):
        book=SimpleNamespace(progress=Mock());wait=Mock();download=Mock(side_effect=ConnectionResetError(10054,'reset'))
        with patch.object(cli,'cache_ready',return_value=False),self.assertRaisesRegex(RuntimeError,'training has NOT started'):
            cli.download_cached_model(book,{},download=download,retryable=lambda e:True,wait=wait)
        self.assertEqual(download.call_count,5);self.assertEqual([x.args[0] for x in wait.call_args_list],[5,10,20,40])
        incomplete=Mock()
        with patch.object(cli,'cache_ready',return_value=False),self.assertRaisesRegex(RuntimeError,'cache incomplete'):
            cli.download_cached_model(book,{},download=incomplete,retryable=lambda e:True,wait=wait)
        self.assertEqual(incomplete.call_count,1)

    def test_download_http_auth_revision_errors_are_not_retried(self):
        class NetworkError(Exception):pass
        class BadRevision(NetworkError):pass
        self.assertTrue(cli.transient_download_failure(NetworkError(),(NetworkError,),(BadRevision,)))
        self.assertFalse(cli.transient_download_failure(BadRevision(),(NetworkError,),(BadRevision,)))
        for status in (401,403,404,408,429,500,503):
            error=NetworkError();error.response=SimpleNamespace(status_code=status)
            self.assertEqual(cli.transient_download_failure(error,(NetworkError,),()),status in (408,429,500,503))

    def test_loss_binding_reaches_old_and_new_root_aliases_and_restores_on_error(self):
        class Trainer:
            def compute_loss(self,*args,**kwargs):return 'native'
        original=Trainer.compute_loss
        old_root=ModuleType('transformers');old_root.Trainer=Trainer
        new_root=ModuleType('transformers');new_root.__path__=[];new_root.Trainer=Trainer
        canonical=ModuleType('transformers.trainer');canonical.Trainer=Trainer
        with patch.dict(sys.modules,{'transformers':new_root,'transformers.trainer':canonical}):
            with self.assertRaisesRegex(RuntimeError,'fixture interruption'):
                with memory_trainer(128) as audit:
                    self.assertIs(old_root.Trainer.compute_loss,new_root.Trainer.compute_loss)
                    self.assertIsNot(Trainer.compute_loss,original)
                    self.assertEqual(Trainer.compute_loss.__module__,'src.wengua.qwen8b_loss_v1')
                    self.assertEqual(audit['route'],'canonical_trainer_compute_loss_v2')
                    raise RuntimeError('fixture interruption')
            self.assertIs(old_root.Trainer.compute_loss,original)
            self.assertIs(new_root.Trainer.compute_loss,original)


if __name__=='__main__':unittest.main()
