"""Non-book software prose: reversible editing, raw provenance and safe scope."""
from copy import deepcopy
from contextlib import closing
from pathlib import Path
import json,sqlite3,tempfile,unittest,zipfile
from src.wengua import book_rag as r,book_rag_editorial as e
from src.wengua.book_rag_query import make_prompt
from tests.test_book_rag import Tokenizer


def setUpModule():(r.ROOT/'local').mkdir(exist_ok=True)


def fixture():
    raw='软件规 测甲须乙。\nimage软件水印\n若乙缺失，不可使用。\n软件疑词丙。'
    edition=e.make_edition(raw,[{'before':'规测','after':'规则','reason':'软件错字夹具','basis':'software_fixture'}],prose_only=True)
    units=[{'id':'software.edit.rule','title':'软件编辑规则','cleaned_lines':[[1,2]],'search_cues':['软件完整条件'],
            'interpretation_limits':['软件条件必须合取']},
           {'id':'software.edit.uncertain','title':'软件疑点','cleaned_lines':[[3,3]],'uncertainties':['软件疑词未定']}]
    return e.build_library(raw,edition,{'id':'editorial_software','title':'软件校订夹具','method_id':'software_not_runtime'},'1','软件章',units),units


class EditorialIntegrity(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(dir=r.ROOT/'local');self.root=Path(self.tmp.name);self.library,self.units=fixture()
    def tearDown(self):self.tmp.cleanup()
    def test_cleanup_keeps_original_and_replays_all_steps(self):
        c=self.library['chapters'][0];text,mapping=e.replay(c['original_text'],c['editorial_edition'])
        self.assertIn('规 测',c['original_text']);self.assertIn('软件规则甲须乙。',text)
        self.assertNotIn('水印',text);self.assertEqual(len(text),len(mapping))
        self.assertEqual(r.validate_library(self.library)['unaccounted_nonblank_lines'],0)
    def test_layout_sensitive_chart_cannot_be_cleaned_as_prose_by_default(self):
        with self.assertRaisesRegex(ValueError,'charts or tables'):e.make_edition('软件表格',[])
    def test_changed_cleaned_text_or_intermediate_hash_is_rejected(self):
        for field in ('text','step'):
            p=deepcopy(self.library);edition=p['chapters'][0]['editorial_edition']
            if field=='text':edition['cleaned_reading_text']+='虚构'
            else:edition['steps'][0]['output_sha256']='bad'
            with self.subTest(field=field),self.assertRaises(ValueError):r.validate_library(p)
    def test_silent_replacement_or_wrong_source_mapping_is_rejected(self):
        p=deepcopy(self.library);p['documents'][0]['parts']=p['documents'][1]['parts']
        with self.assertRaisesRegex(ValueError,'raw provenance'):r.validate_library(p)
    def test_unresolved_word_cannot_be_promoted_to_positive_rule(self):
        p=deepcopy(self.library);p['documents'][1].update(kind='rule',phase='general_rule')
        with self.assertRaisesRegex(ValueError,'Unresolved'):r.validate_library(p)
    def test_correction_must_match_exact_occurrence_count(self):
        with self.assertRaisesRegex(ValueError,'occurrence count'):
            e.make_edition('软件甲甲。',[{'before':'甲','after':'乙','reason':'test','basis':'fixture'}],prose_only=True)
    def test_multiple_identical_corrections_preserve_span_projection(self):
        raw='软 件甲甲。';edition=e.make_edition(raw,[{'before':'甲','after':'乙乙','expected_occurrences':2,'reason':'test','basis':'fixture'}],prose_only=True)
        c={'book_id':'s','chapter_id':'1','original_text':raw,'source_sha256':r.digest(raw),'editorial_edition':edition}
        parts=e.parts_for_reading(c,[[1,1]]);self.assertEqual(r.quote_part({'s/1':c},parts[0]),raw)
    def test_search_corrected_term_and_prompt_label_without_raw_overwrite(self):
        path=self.root/'index.sqlite3';r.build_index([self.library],path)
        with r.Index(path) as index:
            found=index.search('软件规则甲需要乙');self.assertTrue(found['documents']);d=found['documents'][0]
            self.assertIn('规 测',d['content']);self.assertIn('软件规则',d['reading_content'])
            prompt=make_prompt(found,'软件规则甲需要什么？',Tokenizer(),max_new_tokens=100)
            sent=prompt['messages'][-1]['content'];self.assertIn('校订阅读稿',sent);self.assertIn('若乙缺失',sent)
            self.assertIn('软件条件必须合取',sent)
            self.assertTrue(all(d['kind']=='rule' for d in index.search('软件疑词丙')['documents']))
            study=index.search('软件疑词丙',mode='study');self.assertTrue(any(d.get('source_uncertainties') for d in study['documents']))
    def test_method_stays_separate_from_existing_app_chart_rules(self):
        path=self.root/'index.sqlite3';r.build_index([self.library],path)
        with r.Index(path) as index:self.assertEqual(index.search('软件规则',method_id=r.METHOD)['documents'],[])
    def test_append_database_preserves_source_cases_and_all_original_rows(self):
        source=self.root/'old.sqlite3';output=self.root/'new.sqlite3'
        with closing(sqlite3.connect(source)) as db:
            db.executescript((r.ROOT/'schema/schema.sql').read_text());db.execute('INSERT INTO books(book_id,title) VALUES(?,?)',('old','软件旧书'))
            db.execute('INSERT INTO sections(book_id,section_key,title,original_text,sha256,content_version) VALUES(?,?,?,?,?,?)',('old','1','旧章','旧原字',r.digest('旧原字'),1))
            db.execute('INSERT INTO cases(case_id,section_id,event_family_id,domain_id,known_before,author_yongshen_steps) VALUES(?,?,?,?,?,?)',('software-case',1,'software-event','software','初始','原步骤'))
            db.commit()
        before=r.digest(source.read_bytes());proof=e.append_database(source,output,self.library,self.units)
        self.assertEqual(before,r.digest(source.read_bytes()));self.assertEqual(proof['new_cases'],0)
        # Windows denies renaming an SQLite file while a leaked connection
        # owns it. Check the real files before any GC or process exit.
        for path in (source,output):
            moved=path.with_suffix('.closed.sqlite3');path.rename(moved);moved.rename(path)
        with closing(sqlite3.connect(output)) as db:
            self.assertEqual(db.execute('SELECT COUNT(*) FROM cases').fetchone()[0],1)
            self.assertEqual(db.execute('SELECT original_text FROM sections WHERE section_id=1').fetchone()[0],'旧原字')
            self.assertEqual(db.execute('SELECT COUNT(*) FROM source_editorial_editions').fetchone()[0],1)
            self.assertEqual(db.execute('SELECT COUNT(*) FROM rules').fetchone()[0],0)
        with self.assertRaisesRegex(ValueError,'Preserve prior'):e.append_database(source,output,self.library,self.units)

    def archive(self,members):
        path=self.root/'software.zip'
        with zipfile.ZipFile(path,'w') as z:
            for name,text in members.items():z.writestr(name,text)
        return path,{'archive_sha256':r.digest(path.read_bytes()),'files':{n:r.digest(v) for n,v in members.items()}}
    def test_installer_verifies_unicode_archive_and_preserves_existing_file(self):
        from update_wengua_books import extract_checked
        archive,release=self.archive({'软件原文.txt':'原字','软件/清理版.txt':'清理字'});target=self.root/'installed'
        extract_checked(archive,target,release);self.assertEqual((target/'软件原文.txt').read_text(),'原字')
        extract_checked(archive,target,release)
        (target/'软件原文.txt').write_text('变化')
        with self.assertRaisesRegex(ValueError,'preserved'):extract_checked(archive,target,release)
    def test_installer_rejects_archive_path_escape_and_member_tamper(self):
        from update_wengua_books import extract_checked
        archive,release=self.archive({'../escape':'软件'})
        with self.assertRaisesRegex(ValueError,'Unsafe'):extract_checked(archive,self.root/'installed',release)
        archive,release=self.archive({'software.txt':'软件'});release['files']['software.txt']='bad'
        with self.assertRaisesRegex(ValueError,'member checksum'):extract_checked(archive,self.root/'installed',release)
        self.assertFalse((self.root/'installed').exists())


if __name__=='__main__':unittest.main()
