import hashlib,json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from src.wengua import compile_shenqi_marriage as importer
from src.wengua.database import initialize,import_section,connect
from src.wengua.book_case_retrieval import get_whole_event

LABELS=("巽四宫","离九宫","坤二宫","震三宫","中五宫",
        "兑七宫","艮八宫","坎一宫","乾六宫")
CN="一二三四五六"

def synthetic():
    cases=json.loads((importer.DATA/"case_index.json").read_text(encoding="utf-8"))
    methods=json.loads((importer.DATA/"method_index.json").read_text(encoding="utf-8"))
    src=["合成测试资料"]*367
    src[0]="第二章 恋爱婚姻预测"
    src[14]="第二节 实例解析（6例）"
    for x in cases["cases"]:
        i=x["case_number"]
        src[x["source_case_span"][0]-1]="实例"+CN[i-1]+"：合成"
        a,b=x["source_nine_palace_table_span"]
        for n in range(a,b+1):
            label=LABELS[n-a]
            src[n-1]=label+" — 辛 —" if label=="中五宫" else label+" 符 休庚 蓬乙"
        for j,n in enumerate(x["author_numbered_step_lines"],1):
            src[n-1]=f"（{j}）合成作者分析"
        for n in x["author_book_feedback_lines"]:
            src[n-1]="同一事的书内验证信息"
    raw=("\n".join(src)+"\n").encode("utf-8")
    digest=hashlib.sha256(raw).hexdigest()
    cases["source_sha256"]=digest
    for x in cases["cases"]:x["source_document_sha256"]=digest
    methods["source_sha256"]=digest
    return raw,cases,methods,digest

class MarriageSourceTests(TestCase):
    def test_six_families_54_palaces_23_steps(self):
        raw,ci,mi,d=synthetic()
        self.assertEqual(len(ci["cases"]),6)
        self.assertEqual(sum(len(x["author_numbered_step_lines"]) for x in ci["cases"]),23)
        self.assertTrue(all(x["book_outcome_label"]=="author_book_success_default" for x in ci["cases"]))
        self.assertEqual(len(mi["author_method_candidates"]),18)
        self.assertTrue(all(x["source_nine_palace_table_span"][1]-x["source_nine_palace_table_span"][0]==8 for x in ci["cases"]))
    def test_append_idempotent_unchanged_old_sections_and_single_reading(self):
        raw,ci,mi,d=synthetic()
        with TemporaryDirectory() as t:
            root=Path(t);src=root/"chapter.txt";src.write_bytes(raw)
            data=root/"metadata";data.mkdir()
            (data/"case_index.json").write_text(json.dumps(ci,ensure_ascii=False))
            (data/"method_index.json").write_text(json.dumps(mi,ensure_ascii=False))
            db=root/"personal.sqlite3"
            initialize(db)
            import_section(db,"shenqi","existing_chapter","existing original","old original unchanged")
            with patch.object(importer,"SHA",d),patch.object(importer,"DATA",data):
                one=importer.import_marriage_chapter(db,src)
                again=importer.import_marriage_chapter(db,src)
            self.assertEqual(one["new_chapter_case_families"],6)
            self.assertEqual(one["literal_chart_cells"],54)
            self.assertEqual(one["original_author_numbered_steps"],23)
            self.assertEqual(again["new_chapter_case_families"],6)
            with connect(db) as conn:
                self.assertEqual(conn.execute("SELECT count(*) FROM sections").fetchone()[0],2)
                self.assertEqual(conn.execute("SELECT count(*) FROM historical_case_book_verdicts").fetchone()[0],6)
                self.assertEqual(conn.execute("SELECT count(*) FROM historical_case_reasoning").fetchone()[0],23)
                self.assertEqual(conn.execute("SELECT count(*) FROM semantic_assertions").fetchone()[0],18)
            caseid=ci["cases"][0]["event_family_id"]
            brief=get_whole_event(db,caseid)
            full=get_whole_event(db,caseid,view="source_study")
            self.assertEqual(len(brief["one_source_chart"]),9)
            self.assertEqual(brief["book_outcome_label"],"author_book_success_default")
            self.assertNotIn("original_later_feedback",brief)
            self.assertNotIn("author_analysis_steps",brief)
            self.assertEqual(len(full["author_analysis_steps"]),3)
            self.assertTrue(full["validation_information"])
    def test_wrong_sha_never_touch_existing_database(self):
        with TemporaryDirectory() as t:
            src=Path(t)/"source.txt";src.write_text("not same",encoding="utf-8")
            db=Path(t)/"new.sqlite3"
            with self.assertRaisesRegex(ValueError,"SHA256 mismatch"):
                importer.import_marriage_chapter(db,src)
            self.assertFalse(db.exists())

if __name__=="__main__":
    import unittest;unittest.main()
