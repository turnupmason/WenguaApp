"""Software contract fixtures; no private book passages or invented gold rules."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
import zipfile
from src.wengua import course_complete_v5 as compiler
from src.wengua import course_training_v5 as course
from src.wengua import qwen_course_training_v4 as v4


def setUpModule():
    (course.ROOT/'local').mkdir(exist_ok=True)


def fixture():
    rows=[];units={};owners={'fixture:heldout':'test','fixture:train':'train'}
    for split in ('train','validation','test'):
        for n,fmt in enumerate(('foundation_qa','conditional_dialogue','chart_application','complete_case')):
            uid=split+str(n);q='软件夹具问题'+uid;a='软件夹具答案。'
            units[uid]={'id':uid,'book_id':'shenqi','chapter':'软件测试','original_quote':'软件夹具，不是古籍。','lines':[1,1]}
            messages=[{'role':'system','content':'软件测试。'},{'role':'user','content':q},{'role':'assistant','content':a}]
            if fmt=='conditional_dialogue':
                messages += [{'role':'user','content':'软件条件变动呢？'},{'role':'assistant','content':'软件条件变动的答案。'}];a=messages[-1]['content']
            rows.append({'id':uid,'question':q,'answer':a,'messages':messages,'source_ids':[uid],
                'case_id':None,'case_ids':[],'split':split,'group':uid,'format':fmt,'task':'software_fixture','source_mode':'synthetic_software_fixture'})
    return {'schema':compiler.SCHEMA,'source_sha256':course.storage.SOURCE_SHA256,'summary':{'schema':compiler.SCHEMA},
            'records':rows,'units':units,'case_splits':owners}


class CompleteCourse(unittest.TestCase):
    def test_unknown_strategy_fails_instead_of_silently_skipping(self):
        with self.assertRaisesRegex(ValueError,'Unimplemented'):
            compiler.declared_strategies([{'typed_groups':[{'strategy':'unimplemented_strategy'}]}])
        declared=compiler.declared_strategies([{'typed_groups':[{'strategy':s} for s in compiler.STRATEGIES]}])
        self.assertEqual(len(declared),30)

    def test_title_with_substantive_body_is_not_a_structure_only_exclusion(self):
        source={'original_quote':'第五节 软件测试接口 '+('软件完整条件不能随标题丢弃。'*20)}
        self.assertIsNone(compiler.classify_nonlesson(source,''))
        self.assertEqual(compiler.classify_nonlesson({'original_quote':'第五节 软件测试接口'},''),'structure_heading')

    def test_reviewed_numbered_proposition_has_real_target_before_heading_filter(self):
        from collections import defaultdict
        from types import SimpleNamespace
        c=SimpleNamespace(sections={1:{'book_id':'shenqi','original_text':'(1)软件夹具的条件说明。','title':'软件夹具'}},
            inventory=[],ranges=defaultdict(list),reviewed_line_lessons={(1,1):{'question':'软件条件是什么？','answer':'软件夹具的条件说明。'}})
        c.raw=lambda *args:'software-source';c.add=lambda *args,**kwargs:'software-task'
        report,_=compiler.add_line_accounting(c)
        self.assertEqual(report[0]['state'],'reviewed_short_rule_teaching')
        self.assertEqual(report[0]['task_ids'],['software-task'])

    def test_condition_connector_and_and_or_lists_do_not_lose_antecedents(self):
        text='软件前提甲和乙同时成立。若丙缺失，则改用丁或戊。否则保持甲。另一个独立的软件事项。'
        parts=compiler.semantic_chunks(text,9)
        self.assertEqual(parts[0],'软件前提甲和乙同时成立。若丙缺失，则改用丁或戊。否则保持甲。')
        self.assertEqual(''.join(parts),text)

    def test_chart_touching_prose_and_short_factual_lines_are_preserved(self):
        lines=['案例标题','| 软件表甲 | 软件表乙 |','+-----+','正文有应保留的前提。','短事实。','','后来的更正。']
        chunks=compiler.source_paragraphs(lines,1,len(lines))
        self.assertEqual([(x[0],x[1],x[3]) for x in chunks],[(1,1,'prose'),(2,3,'layout'),(4,5,'prose'),(7,7,'prose')])
        self.assertIn('短事实。',chunks[2][2])

    def test_five_jia_reverse_definition_syntax_keeps_alternative_and_common_limit(self):
        # Pure software parser fixture; these placeholders are not book rules.
        quote=('软件前段。五假，是软件标题。软件共限。景门合软件甲，叫天假。'
               '杜门合软件乙，叫地假。惊门合软件丙，叫人假。'
               '伤门合软件丁，叫神假。又一说软件戊。死门合软件己，叫鬼假。')
        intro,common,parts=compiler.five_jia_sections(quote)
        self.assertEqual(intro,'软件前段。');self.assertIn('软件共限',common)
        self.assertEqual([n for n,_ in parts],['天假','地假','人假','神假','鬼假'])
        self.assertIn('又一说软件戊',dict(parts)['神假'])
        with self.assertRaisesRegex(ValueError,'boundaries'):compiler.five_jia_sections('只有标题。')

    def test_literal_quote_roundtrip_checks_source_hash_and_coordinates(self):
        class Sources:pass
        c=Sources();c.sections={1:{'sha256':'fixture','original_text':'软件原文甲。\n软件原文乙。'}}
        c.units={'u':{'section_id':1,'source_sha256':'fixture','lines':[2,2],'original_quote':'软件原文乙。','match_status':'literal'}}
        self.assertEqual(compiler.audit_source_roundtrip(c)['located_literal_or_whitespace_only'],1)
        c.units['u']['original_quote']='无依据的不同文字。'
        with self.assertRaisesRegex(ValueError,'mismatch'):compiler.audit_source_roundtrip(c)
        c.units['u']['match_status']='sqlite_original_transcription'
        self.assertEqual(compiler.audit_source_roundtrip(c),{'separately_labelled_sqlite_transcription':1})

    def test_heldout_case_cannot_train_but_a_universal_rule_can_be_shared(self):
        p=fixture();p['records'][4]['source_ids']=p['records'][0]['source_ids']
        course.validate_rows(p['records'],p['units'],p['case_splits'])
        p['records'][0]['case_ids']=['fixture:heldout']
        with self.assertRaisesRegex(ValueError,'holdout leakage'):course.validate_rows(p['records'],p['units'],p['case_splits'])

    def test_conflicts_wrong_targets_nonbook_and_old_scores_rejected(self):
        for kind in ('conflict','target','evidence','legacy'):
            p=fixture();r=p['records'][0]
            if kind=='conflict':
                x=deepcopy(r);x['id']='collision';x['answer']='另一个软件答案。';x['messages'][-1]['content']=x['answer'];p['records'].append(x)
            elif kind=='target':r['answer']='不一致。'
            elif kind=='evidence':p['units'][r['source_ids'][0]]['book_id']='non_book'
            else:r['answer']='HEALTH_V9_V11';r['messages'][-1]['content']=r['answer']
            with self.subTest(kind=kind),self.assertRaises(ValueError):course.validate_rows(p['records'],p['units'],p['case_splits'])

    def test_independent_schema_plan_and_v4_profile_remain_unchanged(self):
        before=v4.profile().engine.base_config();p=course.profile();c=p.engine.base_config()
        self.assertEqual(c['schema'],compiler.SCHEMA);self.assertEqual(c['model_id'],'Qwen/Qwen3-8B')
        self.assertEqual(p.sweep.plan(course.load(course.SPEC))['maximum_distinct_trials'],6)
        self.assertEqual(v4.profile().engine.base_config(),before)
        with tempfile.TemporaryDirectory(dir=course.ROOT/'local') as t:
            job=p.engine.open_job(Path(t)/'job',c,resume=True)
            p.engine.open_job(job,c,resume=True)
            with self.assertRaisesRegex(ValueError,'resume contract'):
                v4.profile().engine.open_job(job,before,resume=True)

    def test_exact_pinned_zip_install_and_tamper_preservation(self):
        with tempfile.TemporaryDirectory(dir=course.ROOT/'local') as t:
            root=Path(t);p=fixture();raw=json.dumps(p).encode();audit=b'{"exclusions":[],"generation_skips":[]}'
            archive=root/'test.zip'
            with zipfile.ZipFile(archive,'w') as z:z.writestr('pack.json',raw);z.writestr('token_audit.json',audit)
            release={'archive_sha256':compiler.sha(archive.read_bytes()),'files':{'pack.json':compiler.sha(raw),'token_audit.json':compiler.sha(audit)}}
            dest=course.install_archive(archive,root/'data',release)
            self.assertEqual(course.verify_data(dest,release)['schema'],compiler.SCHEMA)
            (dest/'pack.json').write_bytes(b'changed')
            with self.assertRaises(ValueError):course.install_archive(archive,dest,release)
            self.assertEqual((dest/'pack.json').read_bytes(),b'changed')

    def test_real_isolated_worker_requests_cannot_adopt_v4_receipts(self):
        from src.wengua.course_process_v5 import launch
        p=course.profile(testing=True);c=p.engine.base_config()|{'smoke_steps':2}
        with tempfile.TemporaryDirectory(dir=course.ROOT/'local') as t:
            root=Path(t);course.storage.atomic_json(root/'sweep_contract.json',{'schema':compiler.SCHEMA})
            job=p.engine.open_job(root/'trials'/'fixture',c,resume=True)
            a=launch(p,job,c,9999999999,'ping');b=launch(p,job,c,9999999999,'ping')
            self.assertNotEqual(a['pid'],b['pid']);self.assertFalse(a['torch_imported'])

if __name__=='__main__':unittest.main()
