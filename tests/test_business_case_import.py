"""Synthetic CI for 14 whole business cases and three real charts in one drawing story."""
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from src.wengua import compile_shenqi_business as book
from src.wengua.database import initialize,import_section,connect
from src.wengua.book_case_retrieval import get_whole_event

PALACE=(("巽4","离9","坤2"),("震3","中5","兑7"),("艮8","坎1","乾6"))

def simulated_chapter():
    indexes={n:json.loads((book.INDEX/(n+".json")).read_text(encoding="utf-8"))
             for n in ("case_index","method_index","chapter_manifest","source_audit")}
    lines=["无版权原文合成测试"]*717
    lines[0]="第六章 经营求财预测"
    lines[62]="第二节 实例解析（14例）"
    for i,case in enumerate(indexes["case_index"]["cases"]):
        lines[case["source_span"][0]-1]=f"实例：模拟第{i+1}个事件"
        for start in case["chart_source_starts"]:
            lines[start-1]="┌─┬─┬─┐"
            for row in range(3):
                a=start+1+row*5
                line=[
                    PALACE[row],
                    ("蛇","", "符"),
                    ("杜乙","戊", "休丙"),
                    ("冲己","", "芮丁")
                ]
                for k in range(4):
                    lines[a+k-1]="│"+"│".join(line[k])+"│"
                if row<2:lines[a+4-1]="├─┼─┼─┤"
            lines[start+15-1]="└─┴─┴─┘"
        for j,(a,b) in enumerate(case["numbered_or_explicit_analysis_ranges"],1):
            lines[a-1]=f"（{j}）合成原书方法"
            if i==9:
                lines[a-1]=("第一种方法：","第二种方法：","第三种方法，")[j-1]+"合成"
            if i==11:lines[a-1]=f"（{j}）抽奖资料"
            for n in range(a+1,b+1):
                lines[n-1]=f"第{j}条方法的补充论证行{n}"
        for n in case["same_case_feedback_lines"]:
            lines[n-1]="书内后来反馈（验证资料）"
    lines[307]="问题是租赁能否成功？杜起出奇门局看了一会儿说：这才是作者断语。"
    lines[419]="最初询问经营前景，杜依奇门格局首先对企业目前运行态势指出有三：之后才给解释"
    lines[549]="开奖前预先得知活动，本着好奇心作一整体预测。事后，预测验证称开奖于各时辰"
    lines[63]="第一节为传统取用"
    raw=("\n".join(lines)+"\n").encode("utf-8")
    digest=hashlib.sha256(raw).hexdigest()
    for name in indexes:indexes[name]["source_sha256"]=digest
    indexes["chapter_manifest"]["source_utf8_bytes"]=len(raw)
    return raw,indexes,digest

class Business14CaseTests(TestCase):
    def test_all_14_families_16_casts_and_81_methods(self):
        raw,indexes,digest=simulated_chapter()
        ix=indexes["case_index"]
        self.assertEqual(len(ix["cases"]),14)
        self.assertEqual(sum(len(c["chart_source_starts"]) for c in ix["cases"]),16)
        self.assertEqual(sum(len(c["numbered_or_explicit_analysis_ranges"]) for c in ix["cases"]),59)
        self.assertEqual(len(indexes["method_index"]["methods"]),81)
        self.assertEqual(len({m["concept_id"] for m in indexes["method_index"]["methods"]}),81)
        self.assertEqual(ix["cases"][11]["chart_source_starts"],[555,585,614])
        self.assertTrue(all(c["book_outcome_label"]=="author_book_success_default" for c in ix["cases"]))

    def test_additive_original_preservation_and_idempotent_case12_extras(self):
        raw,indexes,digest=simulated_chapter()
        with TemporaryDirectory() as tmp:
            t=Path(tmp)
            source=t/"synthetic.txt";source.write_bytes(raw)
            public=t/"public";public.mkdir()
            for name,data in indexes.items():
                (public/(name+".json")).write_text(json.dumps(data,ensure_ascii=False))
            db=t/"private.sqlite3"
            initialize(db)
            import_section(db,"shenqi","older_book","previous preserved","SOURCE ORIGINAL PRESERVED")
            with patch.object(book,"SHA",digest),patch.object(book,"INDEX",public):
                one=book.import_business_chapter(db,source)
                again=book.import_business_chapter(db,source)
            self.assertEqual(one["new_event_families"],14)
            self.assertEqual(one["primary_source_cells"],126)
            self.assertEqual(one["additional_source_cells"],18)
            self.assertEqual(one["fully_sourced_additional_casts"],2)
            self.assertEqual(one["author_analysis_units"],59)
            self.assertEqual(one["source_method_candidates"],81)
            self.assertEqual(again["new_event_families"],14)
            with connect(db) as con:
                self.assertEqual(con.execute("SELECT count(*) FROM sections").fetchone()[0],2)
                self.assertEqual(con.execute("SELECT count(*) FROM historical_case_book_verdicts").fetchone()[0],14)
                self.assertEqual(con.execute("SELECT count(*) FROM historical_chart_cells").fetchone()[0],126)
                self.assertEqual(con.execute("SELECT count(*) FROM historical_case_additional_cast_cells").fetchone()[0],18)
                self.assertEqual(con.execute("SELECT original_text FROM sections WHERE section_key='older_book'").fetchone()[0],"SOURCE ORIGINAL PRESERVED")
            case7=get_whole_event(db,indexes["case_index"]["cases"][6]["case_id"])
            self.assertNotIn("作者断语",case7["known_before"])
            case12=get_whole_event(db,indexes["case_index"]["cases"][11]["case_id"])
            self.assertNotIn("事后",case12["known_before"])
            self.assertNotIn("original_later_feedback",case12)

    def test_invalid_hash_never_creates_sqlite(self):
        with TemporaryDirectory() as tmp:
            p=Path(tmp)/"not-the-original.txt";p.write_text("bad source")
            db=Path(tmp)/"should-not-exist.sqlite3"
            with self.assertRaisesRegex(ValueError,"SHA256 mismatch"):
                book.import_business_chapter(db,p)
            self.assertFalse(db.exists())

    def test_missing_one_complete_lottery_cast_is_rejected(self):
        raw,indexes,digest=simulated_chapter()
        with TemporaryDirectory() as tmp:
            p=Path(tmp)
            public=p/"public";public.mkdir()
            indexes["case_index"]["cases"][11]["chart_source_starts"]=[555,585]
            for name,obj in indexes.items():
                (public/(name+".json")).write_text(json.dumps(obj,ensure_ascii=False))
            with patch.object(book,"SHA",digest),patch.object(book,"INDEX",public):
                with self.assertRaisesRegex(ValueError,"16 supplied casts"):
                    book.prepare(raw)

if __name__=="__main__":
    import unittest
    unittest.main()
