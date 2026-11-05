"""Software source fixtures only: no private book text or expert gold answers."""
from copy import deepcopy
from pathlib import Path
import json,tempfile,subprocess,sys,unittest
from src.wengua import book_rag as r
from src.wengua.book_rag_sources import literal_selector,stage_chapter,reviewed_chapter_library
from src.wengua.book_rag_query import cast_time,checked_chart,make_prompt,check_answer


def setUpModule():(r.ROOT/'local').mkdir(exist_ok=True)


def fixture(book='software',method=r.METHOD):
    chapter={'book_id':book,'book_title':'软件夹具','chapter_id':'1','title':'软件测试章','method_id':method,
        'source_revision':'fixture1','original_text':'软件规则甲要求乙，同时受丙限制。\n若乙缺失，不能套用甲。\n软件案例初始情况甲。\n后来才反馈软件结果丁。\n软件图题。'}
    chapter['source_sha256']=r.digest(chapter['original_text']);key=r.chapter_key(chapter);cid=book+':case'
    def doc(name,kind,lo,hi,phase,cases=(),cues=()):
        return {'id':book+':'+name,'kind':kind,'title':'软件测试','parts':[literal_selector(chapter,lo,hi)],
            'cues':list(cues),'domains':[],'case_ids':list(cases),'phase':phase,'topic':'rule',
            'review_status':'reviewed_source_selector','related_case_phases':['book_feedback']}
    docs=[doc('rule','rule',1,2,'general_rule',cues=['软件规则的完整条件']),
          doc('initial','case',3,3,'historical_mixed',[cid],['软件案例']),
          doc('feedback','case',4,4,'book_feedback',[cid],['软件后来结果丁']),
          doc('caption','reference',5,5,'source_context',cues=['软件图题'])]
    return {'schema':r.SCHEMA,'books':{book:{'title':'软件夹具'}},'chapters':[chapter],'documents':docs,
        'cases':{cid:{'event_family_id':'software-family','domain':'health','spans':[{'chapter':key,'lines':[3,4]}]}}}


class Tokenizer:
    def apply_chat_template(self,messages,**kw):return list(range(sum(len(m['content']) for m in messages)+5))


class SourceIntegrity(unittest.TestCase):
    def test_full_chapter_and_every_line_are_accounted(self):
        p=fixture();a=r.validate_library(p);self.assertEqual(a['chapters'],1);self.assertEqual(a['cases'],1)
        self.assertEqual(a['unaccounted_nonblank_lines'],0);self.assertFalse(a['qa_answers_indexed'])
    def test_chapter_hash_tamper_rejected(self):
        p=fixture();p['chapters'][0]['original_text']+='坏'
        with self.assertRaisesRegex(ValueError,'chapter changed'):r.validate_library(p)
    def test_literal_span_tamper_rejected(self):
        p=fixture();p['documents'][0]['parts'][0]['quote_sha256']='bad'
        with self.assertRaisesRegex(ValueError,'quote changed'):r.validate_library(p)
    def test_invalid_source_lines_and_offsets_rejected(self):
        for change in [{'lines':[0,2]},{'lines':[1,999]},{'chars':[3,1]},{'source_sha256':'bad'}]:
            p=fixture();p['documents'][0]['parts'][0].update(change)
            with self.subTest(change=change),self.assertRaises(ValueError):r.validate_library(p)
    def test_unaccounted_nonblank_source_cannot_disappear(self):
        p=fixture();p['documents'].pop()
        with self.assertRaisesRegex(ValueError,'without an explicit'):r.validate_library(p)
    def test_feedback_cannot_be_relabeled_as_universal_rule(self):
        p=fixture();d=p['documents'][2];d.update(kind='rule',case_ids=[],phase='general_rule')
        with self.assertRaisesRegex(ValueError,'Case source range'):r.validate_library(p)
    def test_unknown_case_or_outside_case_source_is_rejected(self):
        p=fixture();p['documents'][1]['parts']=[p['documents'][0]['parts'][0]]
        with self.assertRaisesRegex(ValueError,'outside'):r.validate_library(p)
    def test_case_registry_must_have_evidence(self):
        p=fixture();p['cases']['unrepresented']=deepcopy(next(iter(p['cases'].values())))
        with self.assertRaisesRegex(ValueError,'coverage mismatch'):r.validate_library(p)
    def test_new_book_appends_without_changing_old_source(self):
        a=fixture();copy=deepcopy(a);b=fixture('second',method='another-explicit-method')
        merged=r.merge_libraries([a,b]);self.assertEqual(len(merged['chapters']),2);self.assertEqual(a,copy)
        self.assertEqual(r.validate_library(merged)['cases'],2)
    def test_author_comparison_links_two_events_without_merging_them(self):
        p=fixture();a='software:case';b='software:other'
        p['cases'][a]['spans'][0]['lines']=[3,3]
        p['cases'][b]={'event_family_id':'another-family','domain':'health','spans':[{'chapter':'software/1','lines':[4,4]}]}
        p['documents'][2]['case_ids']=[b]
        shared=deepcopy(p['documents'][1]);shared.update(id='software:comparison',case_ids=[a,b],phase='author_cross_case_comparison')
        shared['parts']=[*p['documents'][1]['parts'],*p['documents'][2]['parts']];p['documents'].append(shared)
        self.assertEqual(r.validate_library(p)['cases'],2)
        with tempfile.TemporaryDirectory(dir=r.ROOT/'local') as t:
            path=Path(t)/'index.sqlite3';r.build_index([p],path)
            with r.Index(path) as i:
                linked=i.get('software:comparison',mode='study');self.assertEqual(set(linked['case_ids']),{a,b})
                result=i.search('软件案例',mode='study',case_id=a,exclude_event_families=['another-family'])
                self.assertTrue(all(b not in d['case_ids'] for d in result['documents']))
                with self.assertRaises(ValueError):i.get('software:comparison',mode='reading')

    def test_duplicate_identical_library_deduplicates(self):
        p=fixture();merged=r.merge_libraries([p,p]);self.assertEqual(len(merged['documents']),4)
    def test_different_active_revision_is_not_silently_overwritten(self):
        a=fixture();b=fixture();b['chapters'][0]['source_revision']='v2'
        with self.assertRaisesRegex(ValueError,'Different active'):r.merge_libraries([a,b])
    def test_unreviewed_library_cannot_enter_index(self):
        p=fixture();p['documents'][0]['review_status']='draft'
        with self.assertRaisesRegex(ValueError,'Unreviewed'):r.validate_library(p)
    def test_draft_source_is_not_searchable_and_raw_bytes_hash_is_kept(self):
        with tempfile.TemporaryDirectory(dir=r.ROOT/'local') as t:
            path=Path(t)/'original.txt';raw='软件原文。\r\n第二行。'.encode();path.write_bytes(raw)
            draft=stage_chapter(path,book_id='software',book_title='软件夹具',chapter_id='2',title='测试章',method_id=r.METHOD,revision='v1')
            self.assertEqual(draft['raw_uploaded_bytes_sha256'],r.digest(raw));self.assertIn('\r\n',draft['chapter']['original_text'])
            with self.assertRaisesRegex(ValueError,'schema'):r.validate_library(draft)
    def test_explicit_review_keeps_joint_conditions_in_one_bundle(self):
        p=fixture();c=p['chapters'][0];draft={'schema':'wengua_incoming_chapter_draft_v1','chapter':c,'book':{'id':'software','title':'软件夹具'}}
        review={'review_status':'source_review_completed','source_sha256':c['source_sha256'],'selectors':[
            {'kind':'rule','source_lines':[[1,1],[2,2]],'phase':'general_rule','search_cues':['软件完整条件']}],
            'cases':[]}
        built=reviewed_chapter_library(draft,review);rule=next(d for d in built['documents'] if d['kind']=='rule')
        self.assertEqual(len(rule['parts']),2);self.assertEqual(r.validate_library(built)['unaccounted_nonblank_lines'],0)
        review['review_status']='draft'
        with self.assertRaisesRegex(ValueError,'review must precede'):reviewed_chapter_library(draft,review)


class Retrieval(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(dir=r.ROOT/'local');self.path=Path(self.temp.name)/'index.sqlite3';self.p=fixture()
        r.build_index([self.p],self.path)
    def tearDown(self):self.temp.cleanup()
    def test_active_snapshot_switch_preserves_old_index_and_no_weights_are_loaded(self):
        pointer=Path(self.temp.name)/'active.json'
        original=r.activate_index(self.path,pointer)
        second=Path(self.temp.name)/'second.sqlite3';r.build_index([self.p,fixture('second')],second)
        r.activate_index(second,pointer)
        self.assertEqual(r.active_index(pointer),second.resolve());self.assertTrue(self.path.exists())
        history=list((pointer.parent/'index_history').glob('*.json'));self.assertEqual(len(history),1)
        self.assertEqual(r.read(history[0]),original)
        with r.Index(self.path) as prior:self.assertEqual(prior.coverage['books'],1)
    def test_review_html_handles_numeric_source_revision_and_escapes_literal_data(self):
        from src.wengua.book_rag_audit import review_html
        library=fixture();library['chapters'][0]['source_revision']=1
        path=Path(self.temp.name)/'numeric.sqlite3';r.build_index([library],path)
        output=Path(self.temp.name)/'review.html'
        with r.Index(path) as index:review_html(index,output)
        self.assertIn('软件规则',output.read_text());self.assertIn(' 1',output.read_text())

    def test_cpu_fts_finds_literal_rule_and_retains_both_conditions(self):
        with r.Index(self.path) as i:
            docs=i.search('软件规则需要什么条件')['documents'];self.assertTrue(docs)
            self.assertIn('同时受丙限制',docs[0]['content']);self.assertIn('若乙缺失',docs[0]['content'])
    def test_case_feedback_cannot_enter_either_fresh_mode(self):
        with r.Index(self.path) as i:
            for mode in ['knowledge','reading']:
                docs=i.search('后来反馈软件结果丁',mode=mode)['documents']
                self.assertTrue(all(d['kind']=='rule' for d in docs))
                self.assertTrue(all('后来才反馈' not in d['content'] for d in docs))
    def test_study_can_retrieve_case_feedback_with_phase_and_source(self):
        with r.Index(self.path) as i:
            docs=i.search('后来软件结果丁',mode='study',case_id='software:case')['documents']
            self.assertTrue(any(d['phase']=='book_feedback' for d in docs));self.assertTrue(all(d['case_ids']==['software:case'] for d in docs))
    def test_direct_get_cannot_bypass_case_gate(self):
        with r.Index(self.path) as i:
            with self.assertRaises(ValueError):i.get('software:feedback',mode='knowledge')
            self.assertEqual(i.get('software:feedback',mode='study')['phase'],'book_feedback')
    def test_case_id_requires_study_mode(self):
        with r.Index(self.path) as i:
            with self.assertRaises(ValueError):i.search('软件',case_id='software:case')
    def test_holdout_event_id_excluded(self):
        with r.Index(self.path) as i:
            self.assertFalse(i.search('软件反馈',mode='study',case_id='software:case',exclude_case_ids=['software:case'])['documents'])
    def test_wrong_book_or_method_is_not_substituted(self):
        with r.Index(self.path) as i:
            with self.assertRaises(ValueError):i.search('软件',book='unknown')
            self.assertEqual(i.search('软件',method_id='other-method')['documents'],[])
    def test_snapshot_tamper_and_overwrite_rejected(self):
        with self.assertRaisesRegex(ValueError,'immutable'):r.build_index([self.p],self.path)
        with self.path.open('ab') as f:f.write(b'changed')
        with self.assertRaisesRegex(ValueError,'changed'):r.Index(self.path)
    def test_sql_and_fts_punctuation_are_not_executed(self):
        with r.Index(self.path) as i:
            i.search('" OR *; DROP TABLE documents; -- 软件规则')
            self.assertTrue(i.search('软件规则')['documents'])
    def test_case_export_preserves_initial_and_feedback(self):
        with r.Index(self.path) as i:
            data=i.case('software:case');self.assertEqual(len(data['documents']),2)
            self.assertEqual({d['phase'] for d in data['documents']},{'historical_mixed','book_feedback'})
    def test_event_family_exclusion_blocks_shared_comparison(self):
        with r.Index(self.path) as i:
            docs=i.search('软件结果',mode='study',exclude_event_families=['software-family'])['documents']
            self.assertTrue(all(not d['case_ids'] for d in docs))
    def test_explicit_case_lookup_has_source_fallback_without_keyword_overlap(self):
        with r.Index(self.path) as i:
            docs=i.search('unmatchedfoobar',mode='study',case_id='software:case')['documents']
            self.assertTrue(docs);self.assertTrue(all(d['case_ids']==['software:case'] for d in docs))
    def test_different_explicit_historical_year_does_not_become_another_case(self):
        with r.Index(self.path) as i:
            self.assertEqual(i.search('2009年软件案例的后来结果',mode='study')['documents'],[])

    def test_query_normalization_does_not_change_literal_source(self):
        self.assertIn('父亲',r.normalize('爸爸'));self.assertEqual(r.ordered_pairs('天丁地壬'),{('丁','壬')})
        self.assertNotEqual(r.ordered_pairs('丁加壬'),r.ordered_pairs('壬加丁'))
        with r.Index(self.path) as i:self.assertEqual(i.get('software:rule',mode='knowledge')['content'],r.document_text({r.chapter_key(c):c for c in self.p['chapters']},self.p['documents'][0]))
    def test_build_and_search_do_not_import_torch(self):
        code="from src.wengua.book_rag import Index; import sys; i=Index("+repr(str(self.path))+"); i.search('软件'); assert 'torch' not in sys.modules; i.close()"
        result=subprocess.run([sys.executable,'-c',code],cwd=r.ROOT,capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)


class PromptAndProgramFacts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet=cast_time('2026-10-28T13:44:00-04:00','America/New_York')
    def prompt(self):
        p=fixture();doc=p['documents'][0]|{'content':'软件规则甲要求乙，同时受丙限制。若乙缺失，不能套用甲。','sources':[{
            'book_title':'软件夹具','chapter':'测试章','lines':[1,2],'method_id':r.METHOD}]}
        return make_prompt({'mode':'knowledge','documents':[doc],'index_sha256':'fixture'},'软件条件是什么？',Tokenizer(),max_new_tokens=128)
    def test_cast_delegates_to_existing_app_functions_with_exact_nine_palaces(self):
        from src.wengua.astro_calendar import solar_chart_clock
        from src.wengua.casting_shenqi import bureau_for_term,layout_from_explicit_bureau
        c=solar_chart_clock(self.packet['time'],self.packet['timezone']);p=c['four_pillars'];b=bureau_for_term(p['day'],c['active_solar_term'])
        expected=layout_from_explicit_bureau(dun=b['dun'],ju=b['ju'],hour_ganzhi=p['hour'])
        self.assertEqual(self.packet['chart'],expected);self.assertEqual(set(expected['palaces']),set(map(str,range(1,10))))
        self.assertEqual(checked_chart(self.packet),self.packet)
    def test_model_modified_chart_or_receipt_rejected(self):
        for changed in ['palace','method','clock']:
            p=deepcopy(self.packet)
            if changed=='palace':p['chart']['palaces']['1']['earth_stem']='伪'
            elif changed=='method':p['method_id']='another-school'
            else:p['calendar']['four_pillars']['day']='甲子'
            with self.subTest(changed=changed),self.assertRaises(ValueError):checked_chart(p)
    def test_existing_clock_ambiguities_remain_rejected(self):
        for iso in ['2026-10-28T13:44:00','2026-10-28T13:44:00+08:00','2026-10-28T23:44:00-04:00']:
            with self.subTest(iso=iso),self.assertRaises(ValueError):cast_time(iso,'America/New_York')
    def test_cast_adapter_does_not_import_old_health_scoring(self):
        code="import sys; from src.wengua.book_rag_query import cast_time; cast_time('2026-10-28T13:44:00-04:00','America/New_York'); assert not any(k.startswith('src.wengua.health_') for k in sys.modules)"
        result=subprocess.run([sys.executable,'-c',code],cwd=r.ROOT,capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)
    def test_question_chart_and_whole_condition_bundle_are_never_truncated(self):
        p=self.prompt();self.assertEqual(p['state'],'ready');self.assertIn('若乙缺失',p['messages'][1]['content']);self.assertFalse(p['prompt_budget']['question_chart_or_source_truncated'])
    def test_budget_skips_whole_bundle_instead_of_cutting_conditions(self):
        p=self.prompt();doc=deepcopy(p['references'][0]);doc['content']='软件完整条件。'*800
        q=make_prompt({'mode':'knowledge','documents':[doc]},'软件条件？',Tokenizer(),max_new_tokens=128)
        self.assertEqual(q['state'],'insufficient_retrieved_evidence');self.assertEqual(q['references'],[])
    def test_question_itself_exceeding_budget_is_rejected(self):
        with self.assertRaisesRegex(ValueError,'never truncate'):make_prompt({'mode':'knowledge','documents':[]},'字'*5000,Tokenizer())
    def test_reading_requires_program_chart_and_matching_method(self):
        with self.assertRaisesRegex(ValueError,'requires a program chart'):make_prompt({'mode':'reading','documents':[]},'软件问题',Tokenizer())
        doc=self.prompt()['references'][0];doc['sources'][0]['method_id']='other-school'
        with self.assertRaisesRegex(ValueError,'methods differ'):make_prompt({'mode':'reading','documents':[doc]},'软件问题',Tokenizer(),packet=self.packet)
    def test_historical_text_cannot_be_injected_into_fresh_prompt(self):
        doc=self.prompt()['references'][0];doc['kind']='case'
        with self.assertRaisesRegex(ValueError,'leaked'):make_prompt({'mode':'knowledge','documents':[doc]},'软件问题',Tokenizer())
    def test_generated_reading_percentages_are_not_accepted_as_probabilities(self):
        p=self.prompt();p['mode']='reading';p['chart_receipt']=self.packet
        result=check_answer('有85%的可能[S1]。',p)
        self.assertEqual(result['status'],'rejected_generated_probability')
        self.assertFalse(result['prediction_validated'])

    def test_study_keeps_speaker_and_correction_annotations_visible(self):
        doc=self.prompt()['references'][0];doc['kind']='case';doc['analysis_annotations']=[{'speaker_status':'student_initial','correction_required':True}]
        p=make_prompt({'mode':'study','documents':[doc]},'原案怎么纠正？',Tokenizer(),max_new_tokens=128)
        self.assertIn('student_initial',p['messages'][1]['content']);self.assertIn('correction_required',p['messages'][1]['content'])
        self.assertIn('不能直接当作最终结论',p['messages'][0]['content'])

    def test_no_citation_and_unknown_citation_are_explicit_not_type_crashes(self):
        p=self.prompt();self.assertEqual(check_answer('软件答案。',p)['status'],'uncited_answer')
        self.assertEqual(check_answer('软件答案[S99]。',p)['status'],'rejected_unknown_citation')
    def test_valid_membership_does_not_claim_semantic_correctness(self):
        c=check_answer('软件答案[S1]。',self.prompt());self.assertTrue(c['citation_membership_checked']);self.assertFalse(c['semantic_support_verified']);self.assertFalse(c['prediction_validated'])
    def test_explicit_wrong_current_star_palace_is_flagged(self):
        p=self.prompt();p['mode']='reading';p['chart_receipt']=self.packet
        actual=next(int(k) for k,c in self.packet['chart']['palaces'].items() if any(s['star']=='天芮星' for s in c['heaven_stars']))
        bad=actual%9+1;c=check_answer('本局天芮星落'+str(bad)+'宫[S1]。',p)
        self.assertEqual(c['status'],'rejected_chart_conflict');self.assertTrue(c['chart_claim_conflicts'])

if __name__=='__main__':unittest.main()
