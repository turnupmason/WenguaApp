"""No copyrighted original in CI: synthetic compact five-chart source regression."""
import hashlib,json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from src.wengua import compile_shenqi_employment as m
from src.wengua.database import connect,initialize,import_section
from src.wengua.book_case_retrieval import get_whole_event

NAMES=(("巽4","离9","坤2"),("震3","中5","兑7"),("艮8","坎1","乾6"))
CN="一二三四五"

def sample():
    index=json.loads((m.INDEX/"case_index.json").read_text(encoding="utf-8"))
    methods=json.loads((m.INDEX/"method_index.json").read_text(encoding="utf-8"))
    manifest=json.loads((m.INDEX/"chapter_manifest.json").read_text(encoding="utf-8"))
    audit=json.loads((m.INDEX/"source_audit.json").read_text(encoding="utf-8"))
    lines=["测试原文（合成，无版权）"]*228
    lines[0]="第五章 工作就业预测"
    lines[18]="第二节 实例解析（5例）"
    for j,c in enumerate(index["cases"]):
        lines[c["span"][0]-1]="实例"+CN[j]+"：模拟事件"
        for section,(a,b) in enumerate(c["chart_source_groups"]):
            assert b==a+3
            palaces=NAMES[section]
            data=[
                palaces,
                ("神","中神","神"),
                ("开癸","壬","杜丙"),
                ("辅乙","","英丁")]
            for k,n in enumerate(range(a,b+1)):
                lines[n-1]="│"+"│".join(data[k])+"│"
        for k,(a,b) in enumerate(c["step"],1):
            lines[a-1]=f"（{k}）合成原书完整分析"
            for n in range(a+1,b+1):lines[n-1]=f"此处接第{k}步综合证据第{n}行"
        for n in c["validation"]:
            lines[n-1]=f"该事件后续印证第{n}行"
        if j==3:lines[143]="当事人正在开会时突然想测测工作怎么样？于是，我便用信笺纸起了个局。随后预言了日期"
        if j==1:lines[92]="我把11月4日的奇门格局找出来一看："
        if j==3:lines[149]="这次调动我共预测了五次，每次的结论都是调动必成，现把第一次我预测的格局进行一下分析："
    # Validate real compact original has an empty central deity/star; synthetic preserves it too.
    raw=("\n".join(lines)+"\n").encode("utf-8")
    digest=hashlib.sha256(raw).hexdigest()
    for v in (index,methods,manifest,audit):v["source_sha256"]=digest
    manifest["source_utf8_bytes"]=len(raw)
    return raw,index,methods,manifest,audit,digest

class EmploymentChapterTests(TestCase):
    def test_public_index_completeness_and_one_event_multicandidate(self):
        raw,i,methods,meta,audit,sha=sample()
        self.assertEqual((len(i["cases"]),sum(len(c["step"]) for c in i["cases"])),(5,20))
        self.assertEqual(len(methods["methods"]),53)
        self.assertEqual(i["candidate_ranking"]["predicted_top_k"],2)
        self.assertEqual(i["candidate_ranking"]["reported_full_ranks"],5)
        self.assertEqual(len(i["candidate_ranking"]["candidates"]),5)
        self.assertEqual(i["cases"][1]["step"][-1],[95,95])
        self.assertEqual(i["cases"][3]["step"],[[173,177],[179,181]])
        self.assertTrue(all(c["book_outcome_label"]=="author_book_success_default" for c in i["cases"]))

    def test_original_preserving_import_idempotent_and_existing_chapters_unmodified(self):
        raw,index,methods,manifest,audit,digest=sample()
        with TemporaryDirectory() as t:
            root=Path(t)
            source=root/"book.txt";source.write_bytes(raw)
            public=root/"public";public.mkdir()
            for name,val in [("case_index",index),("method_index",methods),
                             ("chapter_manifest",manifest),("source_audit",audit)]:
                (public/(name+".json")).write_text(json.dumps(val,ensure_ascii=False),encoding="utf-8")
            db=root/"private.sqlite3"
            initialize(db)
            import_section(db,"shenqi","old_chapter","existing","OLD SOURCE UNTOUCHED")
            with patch.object(m,"SHA",digest),patch.object(m,"INDEX",public):
                first=m.import_employment_chapter(db,source)
                again=m.import_employment_chapter(db,source)
            self.assertEqual(first["source_cases"],5)
            self.assertEqual(first["nine_palace_raw_cells"],45)
            self.assertEqual(first["numbered_author_reasoning_steps"],20)
            self.assertEqual(first["candidate_rank_records"],5)
            self.assertEqual(first["method_candidates"],53)
            self.assertEqual(first["source_segments"],5)
            self.assertEqual(again["source_cases"],5)
            with connect(db) as con:
                self.assertEqual(con.execute("SELECT count(*) FROM sections").fetchone()[0],2)
                self.assertEqual(con.execute("SELECT count(*) FROM historical_case_book_verdicts").fetchone()[0],5)
                self.assertEqual(con.execute("SELECT count(*) FROM historical_event_candidates WHERE predicted_rank IS NOT NULL").fetchone()[0],2)
                self.assertEqual(con.execute("SELECT count(*) FROM historical_event_candidates WHERE book_reported_rank IS NOT NULL").fetchone()[0],5)
                self.assertEqual(con.execute("SELECT original_text FROM sections WHERE section_key='old_chapter'").fetchone()[0],"OLD SOURCE UNTOUCHED")
                self.assertEqual(con.execute("SELECT count(*) FROM historical_chart_cells WHERE palace=5").fetchone()[0],5)
            case4=get_whole_event(db,index["cases"][3]["case_id"])
            self.assertNotIn("阴历六月份",case4["known_before"])
            case5=get_whole_event(db,index["cases"][4]["case_id"])
            study=get_whole_event(db,index["cases"][4]["case_id"],view="source_study")
            self.assertEqual(len(case5["one_source_chart"]),9)
            self.assertEqual(len(study["author_analysis_steps"]),5)
            self.assertNotIn("original_later_feedback",case5)
            self.assertEqual(case5["book_outcome_label"],"author_book_success_default")

    def test_wrong_chapter_source_hash_blocks_new_database(self):
        with TemporaryDirectory() as d:
            p=Path(d)/"wrong.txt";p.write_text("wrong")
            db=Path(d)/"untouched.sqlite3"
            with self.assertRaisesRegex(ValueError,"SHA256 mismatch"):
                m.import_employment_chapter(db,p)
            self.assertFalse(db.exists())

    def test_missing_one_candidate_is_rejected(self):
        raw,index,methods,manifest,audit,digest=sample()
        with TemporaryDirectory() as d:
            path=Path(d)
            public=path/"public";public.mkdir()
            index["candidate_ranking"]["candidates"].pop()
            for name,val in [("case_index",index),("method_index",methods),
                             ("chapter_manifest",manifest),("source_audit",audit)]:
                (public/(name+".json")).write_text(json.dumps(val,ensure_ascii=False))
            with patch.object(m,"SHA",digest),patch.object(m,"INDEX",public):
                with self.assertRaisesRegex(ValueError,"five-candidate ranking incomplete"):
                    m.prepare(raw)

if __name__=="__main__":
    import unittest
    unittest.main()
