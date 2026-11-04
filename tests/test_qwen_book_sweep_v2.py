from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
import time
import unittest
from unittest.mock import patch

from src.wengua import qwen_book_continuous_v1 as engine
from src.wengua import qwen_book_sweep_v2 as sweep
from src.wengua.qwen_book_continuous_v1 import book


class ContinuousStagedContracts(unittest.TestCase):
    def setUp(self):
        (book.ROOT/'local').mkdir(exist_ok=True);self.spec=book.read_json(sweep.SPEC)

    def small(self):
        spec=deepcopy(self.spec);spec.update(contexts=[1024,2048],structures=[spec['structures'][0]],learning_rates=[2e-5,3e-5])
        return spec

    def test_default_plan_has_user_high_capacity_candidate_and_13_trials(self):
        p=sweep.plan(self.spec)
        self.assertEqual(len(p['structures']),8);self.assertEqual(p['maximum_distinct_trials'],13)
        high=[c for c in p['structures'] if c['lora_r']==32 and c['max_seq_length']==4096][0]
        self.assertEqual(len(high['target_modules']),7);self.assertEqual(high['lora_alpha'],64)
        self.assertEqual(high['num_train_epochs'],5);self.assertEqual(high['gradient_accumulation_steps'],16)
        self.assertFalse(high['optimizer_reset_between_epochs']);self.assertFalse(p['training_started'])

    def test_nonbook_teachers_legacy_adapters_and_changed_training_mode_are_rejected(self):
        for key in ('initial_adapter','teacher_model','old_scores'):
            spec=deepcopy(self.spec);spec['shared_overrides'][key]='legacy'
            with self.assertRaisesRegex(ValueError,'override'):sweep.plan(spec)
        c=engine.base_config();c['optimizer_reset_between_epochs']=True
        with self.assertRaisesRegex(ValueError,'Continuous'):engine.validate(c)

    def test_invalid_optimization_ranges_are_rejected_before_model_loading(self):
        for key,value in [('learning_rates',[0]),('dropouts',[0.9]),('warmup_ratios',[0.8])]:
            s=deepcopy(self.spec);s[key]=value
            with self.assertRaises(ValueError):sweep.plan(s)

    def test_macro_loss_keeps_each_format_equal_weight(self):
        result=engine.macro_losses({'eval_foundation_qa_loss':1.0,'eval_complete_case_loss':3.0},['foundation_qa','complete_case'])
        self.assertEqual(result['validation_loss'],2.0);self.assertFalse(result['professional_correctness_verified'])
        with self.assertRaises(ValueError):engine.macro_losses({'eval_a_loss':float('nan')},['a'])
        with self.assertRaises(ValueError):engine.macro_losses({},['a'])

    def test_epoch_patience_and_duplicate_history_guard(self):
        c=engine.base_config();history=[]
        for step,loss in [(10,1.0),(20,1.1),(30,1.2)]:history,stop=engine.update_history(history,{'steps':step,'validation_loss':loss},c)
        self.assertTrue(stop)
        with self.assertRaisesRegex(ValueError,'repeated'):engine.update_history(history,{'steps':30,'validation_loss':0.1},c)

    def test_optimizer_settings_do_not_change_data_signature_but_context_does(self):
        c=engine.base_config();other=dict(c,lora_r=32,lora_alpha=64,learning_rate=2e-5,warmup_ratio=0.03,lora_dropout=0.01)
        self.assertEqual(engine.data_signature(c),engine.data_signature(other))
        self.assertNotEqual(engine.data_signature(c),engine.data_signature(dict(c,max_seq_length=4096,inference_max_context=4096)))

    def test_continuous_job_cannot_reuse_old_loop_or_changed_schedule(self):
        with TemporaryDirectory(dir=book.ROOT/'local') as tmp:
            job=Path(tmp)/'job';c=engine.base_config();engine.open_job(job,c,resume=False)
            self.assertEqual(engine.open_job(job,c,resume=True),job)
            with self.assertRaises(ValueError):book.open_job(job,c,resume=True)
            with self.assertRaises(ValueError):engine.open_job(job,dict(c,num_train_epochs=6),resume=True)

    def checkpoint(self,job):
        stage=job/'cycle_01';book.atomic_json(stage/'stage_contract.json',{'fixture':True})
        cp=stage/'trainer/checkpoint-2';cp.mkdir(parents=True)
        for name in book.CKPT_REQUIRED:(cp/name).write_bytes(b'fixture')
        engine.seal(stage,cp,[{'steps':2,'validation_loss':1.0}],False);return cp

    def test_optimizer_checkpoint_seals_early_stop_history_and_rejects_changes(self):
        with TemporaryDirectory() as tmp:
            job=Path(tmp)/'job';cp=self.checkpoint(job)
            self.assertEqual(engine.explicit_checkpoint(job,cp),cp.resolve())
            (cp/'continuous_state.json').write_text('{}')
            self.assertIsNone(engine.latest(job/'cycle_01'))
            with self.assertRaises(ValueError):engine.explicit_checkpoint(job,cp)

    def test_finished_training_uses_plain_resume_for_pending_generation(self):
        with TemporaryDirectory() as tmp:
            job=Path(tmp)/'job';cp=self.checkpoint(job)
            book.atomic_json(job/'cycle_01/stage_status.json',{'state':'trained_pending_generation'})
            with self.assertRaisesRegex(ValueError,'ordinary --resume'):engine.explicit_checkpoint(job,cp)

    def fake_prepare(self,root,job,c,**kw):
        return {'context':c['max_seq_length'],'training_views':4815,'updates_per_epoch':301,
            'common_evaluation_sha256':{'validation_loss.jsonl.gz':'fixed','validation_prompts.jsonl.gz':'fixed','test_prompts.jsonl.gz':'fixed'}}

    def fake_probe(self,job,c,*args,**kw):
        self.events.append(('probe',sweep.trial_id(c)))
        result={'state':'complete','adapter':str(job/'smoke/adapter'),'trainable_parameters':20}
        book.atomic_json(job/'smoke/stage_status.json',result);return result

    def fake_trial(self,job,c,*args,**kw):
        self.events.append(('fit',sweep.trial_id(c)))
        value=3-c['max_seq_length']/10000-(0.1 if c['learning_rate']==2e-5 else 0)-(0.1 if c['lora_dropout']==0.01 else 0)-(0.1 if c['warmup_ratio']==0.03 else 0)
        result={'state':'complete','selected_epoch':2,'validation_loss':value,'per_format_loss':{'fixture':value},
            'steps':602,'adapter':str(job/'cycle_01/adapters/step-602'),'planned_steps':1505,'epochs':[]}
        book.atomic_json(job/'job_status.json',result);return result

    def test_all_probes_precede_training_adaptive_stages_reuse_configs_and_one_test(self):
        self.events=[]
        def final(job,c,best,deadline,**kw):
            self.events.append(('test',job.name))
            self.assertEqual(c['max_seq_length'],2048);self.assertEqual(c['learning_rate'],2e-5)
            self.assertEqual(c['lora_dropout'],0.01);self.assertEqual(c['warmup_ratio'],0.03)
            return {'state':'complete','used_for_selection':False}
        with TemporaryDirectory(dir=book.ROOT/'local') as tmp,patch.object(engine,'prepare_shared',side_effect=self.fake_prepare),patch.object(engine,'fit',side_effect=self.fake_probe),patch.object(engine,'run_trial',side_effect=self.fake_trial),patch.object(book,'final_test',side_effect=final) as test,patch.object(book,'checked_adapter'),patch.object(engine,'render'):
            root=Path(tmp)/'run';result=sweep.run(root,self.small(),time.time()+3600,cpu_factory=object())
            self.assertEqual(result['state'],'complete');self.assertEqual(len(result['trials']),6)
            self.assertEqual([x[0] for x in self.events[:2]],['probe','probe']);self.assertEqual(self.events[-1][0],'test')
            self.assertEqual(len([x for x in self.events if x[0]=='fit']),6)
            before=list(self.events);sweep.run(root,self.small(),time.time()+3600,resume=True,cpu_factory=object())
            self.assertEqual(self.events,before);self.assertEqual(test.call_count,1)

    def test_pause_never_freezes_selection_or_touches_final_test(self):
        self.events=[]
        with TemporaryDirectory(dir=book.ROOT/'local') as tmp,patch.object(engine,'prepare_shared',side_effect=self.fake_prepare),patch.object(engine,'fit',side_effect=self.fake_probe),patch.object(engine,'run_trial',return_value={'state':'paused_training'}),patch.object(book,'final_test') as test:
            root=Path(tmp)/'run';r=sweep.run(root,self.small(),time.time()+3600,cpu_factory=object())
            self.assertEqual(r['state'],'paused_trial');test.assert_not_called();self.assertFalse((root/'selected_trial.json').exists())

    def test_formal_resume_does_not_misread_completed_probe_as_paused_probe(self):
        self.events=[];paused=True
        def formal(job,c,*args,**kw):
            nonlocal paused
            if paused:paused=False;return {'state':'paused_training'}
            return self.fake_trial(job,c,*args,**kw)
        with TemporaryDirectory(dir=book.ROOT/'local') as tmp,patch.object(engine,'prepare_shared',side_effect=self.fake_prepare),patch.object(engine,'fit',side_effect=self.fake_probe),patch.object(engine,'run_trial',side_effect=formal),patch.object(book,'final_test',return_value={'state':'complete'}),patch.object(book,'checked_adapter'),patch.object(engine,'render'):
            root=Path(tmp)/'run';spec=self.small()
            self.assertEqual(sweep.run(root,spec,time.time()+3600,cpu_factory=object())['state'],'paused_trial')
            result=sweep.run(root,spec,time.time()+3600,resume=True,cpu_factory=object())
            self.assertEqual(result['state'],'complete')

    def test_oom_is_recorded_without_silent_context_changes_other_errors_stop(self):
        self.events=[]
        with TemporaryDirectory(dir=book.ROOT/'local') as tmp,patch.object(engine,'prepare_shared',side_effect=self.fake_prepare),patch.object(engine,'fit',side_effect=RuntimeError('CUDA out of memory fixture')),patch.object(book,'final_test') as test:
            r=sweep.run(Path(tmp)/'run',self.small(),time.time()+3600,cpu_factory=object())
            self.assertEqual(r['state'],'no_feasible_trial');self.assertEqual({x['context'] for x in r['trials'].values()},{1024,2048});test.assert_not_called()
        with TemporaryDirectory(dir=book.ROOT/'local') as tmp,patch.object(engine,'prepare_shared',side_effect=OSError('disk corrupt')):
            with self.assertRaisesRegex(OSError,'disk corrupt'):sweep.run(Path(tmp)/'run',self.small(),time.time()+3600,cpu_factory=object())

    def test_changed_plan_or_foreign_checkpoint_cannot_resume(self):
        with TemporaryDirectory(dir=book.ROOT/'local') as tmp:
            root=Path(tmp)/'run';sweep.run(root,self.small(),time.time())
            changed=self.small();changed['learning_rates']=[4e-5]
            with self.assertRaisesRegex(ValueError,'contract changed'):sweep.run(root,changed,time.time(),resume=True)
            with self.assertRaisesRegex(ValueError,'another sweep'):
                sweep.run(root,self.small(),time.time(),resume=True,resume_from_checkpoint=Path(tmp)/'foreign/checkpoint-2')


if __name__=='__main__':unittest.main()
