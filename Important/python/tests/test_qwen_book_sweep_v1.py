from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
import time
import unittest
from unittest.mock import patch

from src.wengua import qwen_book_loop_v3 as loop
from src.wengua import qwen_book_sweep_v1 as sweep


class BookSweepContracts(unittest.TestCase):
    def setUp(self):
        (loop.ROOT/'local').mkdir(exist_ok=True)
        self.spec=loop.read_json(sweep.SPEC)

    def small(self):
        spec=deepcopy(self.spec);spec['include_reference_config']=False
        spec['grid'].update(learning_rate=[0.00002],target_modules=[['q_proj','v_proj']])
        return spec

    def test_default_nine_fresh_configs_share_data_context_and_seed(self):
        trials=sweep.expand_spec(self.spec)
        self.assertEqual(len(trials),9);self.assertEqual(sum(t['reference'] for t in trials),1)
        self.assertEqual(len({loop.dumps(sweep.data_signature(t['config'])) for t in trials}),1)
        self.assertTrue(all(t['config']['final_test_policy']=='defer_to_sweep' for t in trials))
        self.assertTrue(all(t['config']['max_seq_length']==2048 for t in trials))

    def test_grid_cannot_import_scores_external_adapters_or_unbounded_trials(self):
        for key in ('initial_adapter','teacher_model','health_score'):
            spec=deepcopy(self.spec);spec['shared_overrides'][key]='old'
            with self.assertRaisesRegex(ValueError,'override'):sweep.expand_spec(spec)
        spec=deepcopy(self.spec);spec['grid']['lora_r']=[1,2,4,8,16,32,48,64,9]
        with self.assertRaisesRegex(ValueError,'32'):sweep.expand_spec(spec)

    def test_invalid_rank_modules_and_context_are_rejected_before_model_load(self):
        for key,value in [('lora_r',[0]),('target_modules',[['invented']]),('lora_dropout',[0.9])]:
            spec=self.small();spec['grid'][key]=value
            with self.assertRaises(ValueError):sweep.expand_spec(spec)
        spec=self.small();spec['shared_overrides']['max_seq_length']=4096
        with self.assertRaisesRegex(ValueError,'fixed'):sweep.expand_spec(spec)

    def test_test_metrics_never_choose_trial_and_ties_are_stable(self):
        rows=[{'id':'b','state':'complete','validation_loss':1.1,'test_score':100},
              {'id':'a','state':'complete','validation_loss':1.1,'test_score':0},
              {'id':'c','state':'paused_trial','validation_loss':0.1}]
        self.assertEqual(sweep.select_trial(rows)['id'],'a')
        self.assertIsNone(sweep.select_trial([{'id':'x','state':'oom'}]))

    def test_shared_cache_copies_identical_bytes_and_rewrites_only_config_receipt(self):
        def fake_prepare(job,c,**kwargs):
            dest=job/'prepared';receipt=dest/'receipt.json'
            if not receipt.exists():
                dest.mkdir(parents=True);(dest/'sample.gz').write_bytes(b'exact immutable bytes')
                loop.atomic_json(receipt,{'config':c,'file_sha256':{'sample.gz':loop.file_sha(dest/'sample.gz')}})
            meta=loop.read_json(receipt)
            self.assertEqual(meta['config'],c)
            for name,sha in meta['file_sha256'].items():
                if loop.file_sha(dest/name)!=sha:raise ValueError('Data corrupt')
            return meta
        with TemporaryDirectory(dir=loop.ROOT/'local') as tmp,patch.object(loop,'prepare',side_effect=fake_prepare):
            root=Path(tmp);configs=[t['config'] for t in sweep.expand_spec(self.small())]
            for i,c in enumerate(configs):
                job=root/str(i);job.mkdir();sweep.shared_prepare(root,job,c)
            self.assertEqual((root/'0/prepared/sample.gz').read_bytes(),(root/'1/prepared/sample.gz').read_bytes())
            (root/'1/prepared/sample.gz').write_bytes(b'corrupt')
            with self.assertRaisesRegex(ValueError,'corrupt'):sweep.shared_prepare(root,root/'1',configs[1])

    def checkpoint(self,job,number):
        stage=job/'cycle_01';loop.atomic_json(stage/'stage_contract.json',{'same_job':True})
        cp=stage/'trainer'/f'checkpoint-{number}';cp.mkdir(parents=True)
        for name in loop.CKPT_REQUIRED:(cp/name).write_text('fixture',encoding='utf8')
        loop.seal_checkpoint(stage,cp);return cp

    def test_explicit_checkpoint_is_latest_intact_same_job_and_unfinished(self):
        with TemporaryDirectory() as tmp:
            job=Path(tmp)/'job';old=self.checkpoint(job,1);new=self.checkpoint(job,2)
            owner,path=loop.requested_checkpoint(job,new)
            self.assertEqual(owner,'cycle_01');self.assertEqual(path,new.resolve())
            self.assertTrue(path.is_relative_to(job.resolve()))
            with self.assertRaisesRegex(ValueError,'latest intact'):loop.requested_checkpoint(job,old)
            with self.assertRaisesRegex(ValueError,'exact job'):loop.requested_checkpoint(job/'other',new)
            loop.atomic_json(job/'cycle_01/stage_status.json',{'state':'complete'})
            with self.assertRaisesRegex(ValueError,'already trained'):loop.requested_checkpoint(job,new)

    def test_explicit_corrupt_checkpoint_is_never_silently_fresh_started(self):
        with TemporaryDirectory() as tmp:
            job=Path(tmp)/'job';cp=self.checkpoint(job,2);(cp/'optimizer.pt').write_bytes(b'corrupt')
            with self.assertRaisesRegex(ValueError,'latest intact'):loop.requested_checkpoint(job,cp)

    def fake_run(self,job,c,deadline,**kwargs):
        self.assertIsNone(kwargs.get('initial_adapter'))
        self.assertEqual(c['final_test_policy'],'defer_to_sweep')
        row={'state':'complete','cycle':1,'validation_loss':1/c['lora_r'],'base_validation_loss':2.0,
             'adapter':str(job/'cycle_01/adapters/step-2'),'runtime_seconds':3,'steps':2,'fresh_official_base':True}
        result={'state':'complete','cycles':[row]}
        loop.atomic_json(job/'job_status.json',result)
        return result

    def test_all_trials_finish_before_one_selected_final_test_and_complete_resume_is_noop(self):
        spec=self.small();observed=[]
        def final(job,c,best,deadline,**kwargs):
            observed.append(job.name)
            statuses=list(job.parent.glob('*/job_status.json'))
            self.assertEqual(len(statuses),2)
            return {'state':'complete','used_for_selection':False}
        with TemporaryDirectory(dir=loop.ROOT/'local') as tmp,patch.object(sweep,'shared_prepare'),patch.object(loop,'run_loop',side_effect=self.fake_run),patch.object(loop,'final_test',side_effect=final) as test,patch.object(loop,'render_report'),patch.object(loop,'checked_adapter'):
            root=Path(tmp)/'run'
            r=sweep.run_sweep(root,spec,time.time()+3600,cpu_factory=object())
            self.assertEqual(r['state'],'complete');self.assertEqual(len(observed),1)
            self.assertEqual(r['selection']['id'],sweep.expand_spec(spec)[1]['id'])
            sweep.run_sweep(root,spec,time.time()+3600,resume=True,cpu_factory=object())
            self.assertEqual(test.call_count,1)
            self.assertTrue((root/'results.html').exists())

    def test_pause_never_runs_test_and_resume_continues_same_config(self):
        with TemporaryDirectory(dir=loop.ROOT/'local') as tmp,patch.object(sweep,'shared_prepare'),patch.object(loop,'final_test') as test:
            with patch.object(loop,'run_loop',return_value={'state':'paused_cycle','cycles':[]}):
                r=sweep.run_sweep(Path(tmp)/'run',self.small(),time.time()+3600,cpu_factory=object())
            self.assertEqual(r['state'],'paused_trial');test.assert_not_called()
            self.assertFalse((Path(tmp)/'run/selected_trial.json').exists())

    def test_only_cuda_oom_skips_trial_without_shorter_context(self):
        spec=self.small();calls=[]
        def fake(job,c,*args,**kwargs):
            calls.append(c['max_seq_length'])
            if c['lora_r']==8:raise RuntimeError('CUDA out of memory fixture')
            return self.fake_run(job,c,*args,**kwargs)
        with TemporaryDirectory(dir=loop.ROOT/'local') as tmp,patch.object(sweep,'shared_prepare'),patch.object(loop,'run_loop',side_effect=fake),patch.object(loop,'final_test',return_value={'state':'complete'}),patch.object(loop,'render_report'):
            r=sweep.run_sweep(Path(tmp)/'run',spec,time.time()+3600,cpu_factory=object())
            self.assertEqual(r['trials'][0]['state'],'oom');self.assertEqual(calls,[2048,2048])

    def test_source_or_disk_error_stops_instead_of_skipping(self):
        with TemporaryDirectory(dir=loop.ROOT/'local') as tmp,patch.object(sweep,'shared_prepare',side_effect=ValueError('source corrupt')),patch.object(loop,'final_test') as test:
            with self.assertRaisesRegex(ValueError,'source corrupt'):
                sweep.run_sweep(Path(tmp)/'run',self.small(),time.time()+3600,cpu_factory=object())
            test.assert_not_called();self.assertEqual(loop.read_json(Path(tmp)/'run/sweep_status.json')['state'],'failed')

    def test_changed_grid_cannot_resume_old_experiment(self):
        with TemporaryDirectory(dir=loop.ROOT/'local') as tmp:
            root=Path(tmp)/'run';spec=self.small()
            r=sweep.run_sweep(root,spec,time.time(),cpu_factory=object());self.assertEqual(r['state'],'paused_deadline')
            changed=deepcopy(spec);changed['grid']['learning_rate']=[0.00003]
            with self.assertRaisesRegex(ValueError,'changed grid'):sweep.run_sweep(root,changed,time.time(),resume=True,cpu_factory=object())

    def test_external_checkpoint_requires_explicit_resume_and_same_sweep(self):
        with TemporaryDirectory(dir=loop.ROOT/'local') as tmp:
            root=Path(tmp)/'run'
            with self.assertRaisesRegex(ValueError,'requires --resume'):
                sweep.run_sweep(root,self.small(),time.time(),resume_from_checkpoint=Path(tmp)/'old')
            sweep.run_sweep(root,self.small(),time.time())
            with self.assertRaisesRegex(ValueError,'different sweep'):
                sweep.run_sweep(root,self.small(),time.time(),resume=True,resume_from_checkpoint=Path(tmp)/'old')

    def test_explicit_checkpoint_in_oom_trial_cannot_be_silently_skipped(self):
        with TemporaryDirectory(dir=loop.ROOT/'local') as tmp:
            root=Path(tmp)/'run';spec=self.small();sweep.run_sweep(root,spec,time.time())
            tid=sweep.expand_spec(spec)[0]['id'];cp=self.checkpoint(root/'trials'/tid,1)
            loop.atomic_json(root/'sweep_status.json',{'state':'paused_trial','trials':[{'id':tid,'state':'oom'}]})
            with self.assertRaisesRegex(ValueError,'--retry-oom'):
                sweep.run_sweep(root,spec,time.time()+3600,resume=True,resume_from_checkpoint=cp)


if __name__=='__main__':unittest.main()
