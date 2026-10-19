"""Synthetic no-copyright end-to-end school/exam importer and provenance regression."""
import hashlib,json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from src.wengua import compile_shenqi_education as e
from src.wengua.database import connect,initialize,import_section
from src.wengua.book_case_retrieval import get_whole_event

NAMES=("巽四宫","离九宫","坤二宫","震三宫","中五宫",
       "兑七宫","艮八宫","坎一宫","乾六宫")
CN="一二三四五"

def synthetic_source():
    cases=json.loads((e.INDEX/"case_index.json").read_text(encoding="utf-8"))
    methods=json.loads((e.INDEX/"method_index.json").read_text(encoding="utf-8"))
    manifest=json.loads((e.INDEX/"chapter_manifest.json").read_text(encoding="utf-8"))
    lines=["无版权的示范资料"]*349
    lines[0]="《神奇之门》"
    lines[1]="第四章 求学考试预测"
    lines[21]="第二节 实例解析（5例）"
    for i,c in enumerate(cases["cases"],1):
        lines[c["source_lines"][0]-1]="实例"+CN[i-1]+"：测试故事"
        a,b=c["original_nine_palace_row_lines"]
        for n in range(a,b+1):
            palace=NAMES[n-a]
            lines[n-1]=palace+" — 辛 —" if palace=="中五宫" else palace+" 符 景丁 辅壬"
        for j,(first,last) in enumerate(c["author_full_analysis_ranges"],1):
            lines[first-1]=f"（{j}）合成作者详细分析"
            for n in range(first+1,last+1):lines[n-1]=f"第{j}条详细证据行{n}"
        for n in c["book_validation_lines"]:
            lines[n-1]="最终收到录取通知书10月9日" if i==5 and n==278 else "同一事件后续验证资料"
    # Prior-known facts must not leak October outcomes to the 8/23 initial query.
    lines[263]="1997年8月23日早上父问女儿考试高分被质疑、希望解决录取难题"
    raw=("\n".join(lines)+"\n").encode("utf-8")
    digest=hashlib.sha256(raw).hexdigest()
    for obj in (cases,methods,manifest):obj["source_sha256"]=digest
    manifest["source_utf8_bytes"]=len(raw)
    return raw,cases,methods,manifest,digest

class EducationCaseTests(TestCase):
    def test_all_five_canonical_book_cases_and_step_ranges(self):
        raw,cases,methods,meta,sha=synthetic_source()
        self.assertEqual(len(cases["cases"]),5)
        self.assertEqual(len(methods["methods"]),35)
        self.assertEqual(sum(len(x["author_full_analysis_ranges"]) for x in cases["cases"]),17)
        self.assertEqual(cases["cases"][-1]["original_question_source_lines"],[264,264])
        self.assertEqual(cases["cases"][-1]["author_full_analysis_ranges"][-1],[345,349])
        self.assertEqual(meta["original_nine_palace_rows"],45)
        self.assertTrue(all(x["book_outcome_label"]=="author_book_success_default" for x in cases["cases"]))

    def test_safe_additive_import_idempotence_and_full_retrospective_analysis(self):
        raw,cases,methods,manifest,digest=synthetic_source()
        with TemporaryDirectory() as tmp:
            root=Path(tmp)
            source=root/"fictional.txt";source.write_bytes(raw)
            metadata=root/"public";metadata.mkdir()
            for name,obj in (("case_index",cases),("method_index",methods),
                             ("chapter_manifest",manifest)):
                (metadata/(name+".json")).write_text(json.dumps(obj,ensure_ascii=False))
            db=root/"private.sqlite3"
            initialize(db)
            import_section(db,"shenqi","existing","old","the prior chapter remains forever")
            with patch.object(e,"SHA",digest),patch.object(e,"INDEX",metadata):
                first=e.import_education_chapter(db,source)
                second=e.import_education_chapter(db,source)
            self.assertEqual((first["one_shot_cases"],first["source_palace_rows"],
                              first["full_author_analysis_steps"],
                              first["domain_method_records"]),(5,45,17,35))
            self.assertEqual(second["one_shot_cases"],5)
            with connect(db) as con:
                self.assertEqual(con.execute("SELECT count(*) FROM sections").fetchone()[0],2)
                self.assertEqual(con.execute("SELECT count(*) FROM historical_case_book_verdicts").fetchone()[0],5)
                self.assertEqual(con.execute("SELECT count(*) FROM semantic_assertions").fetchone()[0],35)
                self.assertEqual(con.execute("SELECT count(*) FROM historical_case_disclosures").fetchone()[0],15)
            fifth=cases["cases"][-1]["event_family_id"]
            blind=get_whole_event(db,fifth)
            study=get_whole_event(db,fifth,view="source_study")
            self.assertIn("8月23日",blind["known_before"])
            self.assertNotIn("10月9日",blind["known_before"])
            self.assertNotIn("original_later_feedback",blind)
            self.assertEqual(len(blind["one_source_chart"]),9)
            self.assertEqual(len(study["author_analysis_steps"]),5)
            self.assertIn("第5条详细证据行349",study["author_analysis_steps"][-1]["original_text"])
            self.assertIn("10月9日",study["original_later_feedback"])
            self.assertEqual(blind["book_outcome_label"],"author_book_success_default")

    def test_sha_guard_blocks_mutation(self):
        with TemporaryDirectory() as t:
            f=Path(t)/"fake.txt";f.write_text("wrong")
            db=Path(t)/"notcreated.sqlite3"
            with self.assertRaisesRegex(ValueError,"SHA256 mismatch"):
                e.import_education_chapter(db,f)
            self.assertFalse(db.exists())

    def test_case_five_rejects_prior_outcome_leak_in_public_index(self):
        raw,cases,methods,manifest,digest=synthetic_source()
        with TemporaryDirectory() as t:
            root=Path(t);meta=root/"meta";meta.mkdir()
            cases["cases"][-1]["original_question_source_lines"]=[264,284]
            for name,obj in (("case_index",cases),("method_index",methods),
                             ("chapter_manifest",manifest)):
                (meta/(name+".json")).write_text(json.dumps(obj,ensure_ascii=False))
            with patch.object(e,"SHA",digest),patch.object(e,"INDEX",meta):
                with self.assertRaisesRegex(ValueError,"initial question must stop"):
                    e.prepare_source(raw)

if __name__=="__main__":
    import unittest;unittest.main()
