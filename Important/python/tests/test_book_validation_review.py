from pathlib import Path
from tempfile import TemporaryDirectory
import csv
import unittest

from scripts.prepare_book_validation_review import prepare
from src.wengua import qwen_book_loop_v3 as book


class ValidationReview(unittest.TestCase):
    def setUp(self):
        (book.ROOT/'local').mkdir(exist_ok=True)

    def inputs(self,root):
        dataset=root/'dataset';prepared=root/'prepared';dataset.mkdir();prepared.mkdir()
        rows=[]
        for split in ('train','validation','test'):
            answer='SECRET_FINAL_TEST_TARGET' if split=='test' else 'fixture answer'
            rows.append({'id':split,'split':split,'format':'foundation_qa','task':'fixture','case_id':None,
                'group':split,'source_mode':'book_knowledge','source_ids':['unit'],'answer':answer,
                'messages':[{'role':'user','content':'fixture question'},{'role':'assistant','content':answer}]})
        unit={'id':'unit','book_id':'shenqi','chapter':'fixture','lines':[1,1],'source_sha256':'source','original_quote':'fixture source'}
        book.write_rows(dataset/'core_tasks.jsonl.gz',rows);book.write_rows(dataset/'source_units.jsonl.gz',[unit])
        book.write_rows(prepared/'validation_prompts.jsonl.gz',[rows[1]]);book.write_rows(prepared/'source_units.jsonl.gz',[unit])
        book.atomic_json(dataset/'manifest.json',{'source_database_sha256':book.SOURCE_SHA256,'file_sha256':{p.name:book.file_sha(p) for p in dataset.iterdir()}})
        book.atomic_json(prepared/'receipt.json',{'source_database_sha256':book.SOURCE_SHA256,'file_sha256':{p.name:book.file_sha(p) for p in prepared.iterdir()}})
        return dataset,prepared

    def test_only_validation_exported_answers_and_reviews_blank_inputs_unchanged(self):
        with TemporaryDirectory(dir=book.ROOT/'local') as tmp:
            root=Path(tmp);dataset,prepared=self.inputs(root);before={p:book.file_sha(p) for d in (dataset,prepared) for p in d.iterdir()}
            result=prepare(dataset,prepared,root/'review')
            self.assertEqual(result['validation_tasks'],1);self.assertFalse(result['test_questions_exported'])
            with (root/'review/模型验收.csv').open(encoding='utf-8-sig',newline='') as stream:rows=list(csv.reader(stream))
            self.assertTrue(all(value=='' for value in rows[1][10:]));self.assertEqual(rows[1][0],'validation')
            self.assertNotIn('SECRET_FINAL_TEST_TARGET',(root/'review/review.html').read_text())
            self.assertEqual(before,{p:book.file_sha(p) for p in before})
            with self.assertRaises(FileExistsError):prepare(dataset,prepared,root/'review')

    def test_changed_question_reference_and_nonvalidation_selection_rejected(self):
        for change in ('answer','split'):
            with self.subTest(change=change),TemporaryDirectory(dir=book.ROOT/'local') as tmp:
                root=Path(tmp);dataset,prepared=self.inputs(root);path=prepared/'validation_prompts.jsonl.gz';rows=book.read_rows(path)
                rows[0][change]='modified' if change=='answer' else 'test';book.write_rows(path,rows)
                receipt=book.read_json(prepared/'receipt.json');receipt['file_sha256'][path.name]=book.file_sha(path);book.atomic_json(prepared/'receipt.json',receipt)
                with self.assertRaises(ValueError):prepare(dataset,prepared,root/'review')
                self.assertFalse((root/'review').exists())

    def test_prepared_source_mismatch_rejected_before_export(self):
        with TemporaryDirectory(dir=book.ROOT/'local') as tmp:
            root=Path(tmp);dataset,prepared=self.inputs(root);path=prepared/'source_units.jsonl.gz';rows=book.read_rows(path)
            rows[0]['original_quote']='different';book.write_rows(path,rows)
            receipt=book.read_json(prepared/'receipt.json');receipt['file_sha256'][path.name]=book.file_sha(path);book.atomic_json(prepared/'receipt.json',receipt)
            with self.assertRaisesRegex(ValueError,'Prepared source differs'):prepare(dataset,prepared,root/'review')
            self.assertFalse((root/'review').exists())


if __name__=='__main__':unittest.main()
