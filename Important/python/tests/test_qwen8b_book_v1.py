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
        for key,value in [('model_id','Qwen/Qwen3-14B'),('revision','main'),('smoke_steps',2),('old_adapters_allowed',True),('non_book_teachers_allowed',True),('initial_adapter','old')]:
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


if __name__=='__main__':unittest.main()
