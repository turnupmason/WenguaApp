"""No private book passages in fixtures; production release is hash-pinned."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

from src.wengua.qwen_course_v4 import SCHEMA,validate_rows,sha
from src.wengua import qwen_course_training_v4 as course
from src.wengua import qwen8b_book_v1 as old
from src.wengua.qwen_course_process_v4 import launch


def fixture_pack():
    records=[];units={}
    for split in ('train','validation','test'):
        for n,fmt in enumerate(('foundation_qa','conditional_dialogue','chart_application','complete_case')):
            uid=split+str(n);a='软件夹具答案。'
            units[uid]={'id':uid,'book_id':'shenqi','chapter':'软件测试','original_quote':'软件夹具，不是古籍。','lines':[1,1]}
            q='软件测试：'+uid
            messages=[{'role':'system','content':'程序测试。'},{'role':'user','content':q},{'role':'assistant','content':a}]
            if fmt=='conditional_dialogue':
                messages += [{'role':'user','content':'条件变化后呢？'},{'role':'assistant','content':'另一个软件夹具答案。'}];a=messages[-1]['content']
            records.append({'id':uid,'group':uid,'split':split,'format':fmt,'question':q,'answer':a,'messages':messages,
                            'source_ids':[uid],'case_id':None,'task':'software_fixture','source_mode':'synthetic_software_fixture'})
    return {'records':records,'units':units,'source_sha256':course.storage.SOURCE_SHA256,'summary':{'schema':SCHEMA}}


class CourseV4(unittest.TestCase):
    def test_all_four_formats_and_multiturn_prefix_targets_have_distinct_evidence(self):
        p=fixture_pack();proof=validate_rows(p['records'],p['units'])
        self.assertEqual(proof['rows'],12);self.assertEqual(proof['family_and_source_leakage'],0)
        r=p['records'][1];views=list(course.storage.target_views(r,0))
        self.assertEqual(len(views),2);self.assertEqual(views[0]['messages'][-1]['content'],'软件夹具答案。')
        self.assertEqual(views[1]['messages'][-1]['content'],r['answer'])

    def test_conflicting_prompt_targets_and_repeated_sentences_are_rejected(self):
        p=fixture_pack();x=deepcopy(p['records'][0]);x['id']='collision';x['answer']='不同答案。';x['messages'][-1]['content']=x['answer'];p['records'].append(x)
        with self.assertRaisesRegex(ValueError,'conflicting targets'):validate_rows(p['records'],p['units'])
        p=fixture_pack();p['records'][0]['answer']='这是一条很长的完全重复的回答句子。'*2;p['records'][0]['messages'][-1]['content']=p['records'][0]['answer']
        with self.assertRaisesRegex(ValueError,'Repeated answer'):validate_rows(p['records'],p['units'])

    def test_shared_case_family_and_source_cannot_cross_folds(self):
        for change in ('group','source_ids'):
            p=fixture_pack();p['records'][4][change]=p['records'][0][change]
            with self.assertRaisesRegex(ValueError,'split leakage'):validate_rows(p['records'],p['units'])

    def test_empty_missing_nonbook_legacy_boilerplate_and_target_mismatch_rejected(self):
        for change in ('empty','missing','nonbook','legacy','boilerplate','mismatch'):
            with self.subTest(change=change):
                p=fixture_pack();r=p['records'][0]
                if change=='empty':r['answer']=''
                if change=='missing':r['source_ids']=['unknown']
                if change=='nonbook':p['units']['train0']['book_id']='old_scoring'
                if change=='legacy':r['answer']='HEALTH_V9_V11'
                if change=='boilerplate':r['answer']='以下是来源资料，尚非现实预测验证'
                if change!='mismatch':r['messages'][-1]['content']=r['answer']
                else:r['answer']='mismatch'
                with self.assertRaises(ValueError):validate_rows(p['records'],p['units'])

    def test_release_hashes_checked_before_any_model_import(self):
        course.storage.ROOT.joinpath('local').mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=course.storage.ROOT/'local') as tmp:
            root=Path(tmp);raw=json.dumps(fixture_pack()).encode();(root/'pack.json').write_bytes(raw)
            rel={'files':{'pack.json':sha(raw)}}
            self.assertEqual(len(course.verify_data(root,rel)['records']),12)
            (root/'pack.json').write_bytes(raw+b' ')
            with self.assertRaisesRegex(ValueError,'missing/changed'):course.verify_data(root,rel)

    def test_archive_is_sha_pinned_and_cannot_overwrite_existing_changed_data(self):
        with tempfile.TemporaryDirectory(dir=course.storage.ROOT/'local') as tmp:
            root=Path(tmp);z=root/'fixture.zip';raw=json.dumps(fixture_pack()).encode()
            with zipfile.ZipFile(z,'w') as f:f.writestr('pack.json',raw)
            rel={'archive_sha256':sha(z.read_bytes()),'files':{'pack.json':sha(raw)}}
            dest=course.install_archive(z,root/'installed',rel)
            self.assertEqual(course.install_archive(z,dest,rel),dest)
            (dest/'pack.json').write_bytes(b'changed')
            with self.assertRaises(ValueError):course.install_archive(z,dest,rel)
            rel['archive_sha256']='0'*64
            with self.assertRaisesRegex(ValueError,'ZIP SHA'):course.install_archive(z,root/'other',rel)

    def test_unsafe_or_unexpected_zip_members_rejected(self):
        with tempfile.TemporaryDirectory(dir=course.storage.ROOT/'local') as tmp:
            root=Path(tmp);z=root/'fixture.zip'
            with zipfile.ZipFile(z,'w') as f:f.writestr('../escape',b'x')
            rel={'archive_sha256':sha(z.read_bytes()),'files':{'../escape':sha(b'x')}}
            with self.assertRaisesRegex(ValueError,'Unsafe'):course.install_archive(z,root/'installed',rel)
            self.assertFalse((root/'escape').exists())

    def test_new_plan_six_maximum_trials_new_adapter_only_old_profile_untouched(self):
        p=course.profile();c=p.engine.base_config();plan=p.sweep.plan(course.load(course.SPEC))
        self.assertEqual(plan['maximum_distinct_trials'],6)
        self.assertEqual({x['lora_r'] for x in plan['structures']},{8,16})
        self.assertTrue(all(x['max_seq_length']==4096 and x['smoke_steps']==100 for x in plan['structures']))
        self.assertEqual(c['num_train_epochs'],3)
        self.assertEqual(old.profile().engine.base_config()['schema'],old.BOOK_SCHEMA)
        with tempfile.TemporaryDirectory(dir=course.storage.ROOT/'local') as tmp:
            job=p.engine.open_job(Path(tmp)/'job',c,resume=True)
            p.engine.open_job(job,c,resume=True)
            with self.assertRaisesRegex(ValueError,'resume contract'):p.engine.open_job(job,c|{'learning_rate':2e-5},resume=True)
            with self.assertRaises(ValueError):old.profile().engine.open_job(job,old.profile().engine.base_config(),resume=True)

    def test_new_actual_worker_nonce_transport_without_torch_and_distinct_pids(self):
        p=course.profile(testing=True);c=p.engine.base_config()|{'smoke_steps':2}
        with tempfile.TemporaryDirectory(dir=course.storage.ROOT/'local') as tmp:
            root=Path(tmp);course.storage.atomic_json(root/'sweep_contract.json',{'schema':SCHEMA})
            job=p.engine.open_job(root/'trials'/'fixture',c,resume=True)
            first=launch(p,job,c,9999999999,'ping');second=launch(p,job,c,9999999999,'ping')
            self.assertNotEqual(first['pid'],second['pid']);self.assertFalse(first['torch_imported'])

    def test_physical_board_aliases_join_without_inventing_missing_symbols(self):
        from src.wengua.qwen_course_v4 import printed_board_key
        short=[{'palace':6,'deity_raw':'符','door_position_raw':'开乙','star_position_raw':'心丙'}]
        full=[{'palace':6,'deity_raw':'值符','door_position_raw':'开门 乙','star_position_raw':'天心 丙'}]
        self.assertEqual(printed_board_key(short),printed_board_key(full))
        unknown=[{'palace':6,'deity_raw':'—','door_position_raw':'开乙','star_position_raw':'心丙'}]
        self.assertNotEqual(printed_board_key(short),printed_board_key(unknown))

    def test_malformed_parameter_graph_is_reported_instead_of_swallowed(self):
        class Bad:
            def named_parameters(self):yield ('name',object(),'third item')
        with self.assertRaisesRegex(RuntimeError,'Parameter graph integrity check failed'):course.parameter_signature(Bad())
        class Param:shape=(2,3);requires_grad=True
        class Good:
            p=Param()
            def named_parameters(self):yield ('name',self.p)
        model=Good();first=course.parameter_signature(model);self.assertEqual(first,course.parameter_signature(model))
        model.p=Param();self.assertNotEqual(first,course.parameter_signature(model))
