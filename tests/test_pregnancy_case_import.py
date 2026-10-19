"""No copyrighted author text in CI; synthetic 313-line source exercises exact layout."""
import hashlib,json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from src.wengua import compile_shenqi_pregnancy as mod
from src.wengua.database import initialize,import_section,connect
from src.wengua.book_case_retrieval import get_whole_event

LABELS=("巽四宫","离九宫","坤二宫","震三宫","中五宫",
        "兑七宫","艮八宫","坎一宫","乾六宫")
CN="一二三四五六"

def synthetic():
    cases=json.loads((mod.DATA/"case_index.json").read_text(encoding="utf-8"))
    methods=json.loads((mod.DATA/"method_index.json").read_text(encoding="utf-8"))
    lines=["无版权合成占位"]*313
    lines[0]="《神奇之门》"
    lines[1]="第三章 怀孕分娩预测"
    for i,c in enumerate(cases["cases"],1):
        lines[c["source_case_span"][0]-1]="实例"+CN[i-1]+"：测试"
        a,b=c["raw_nine_palace_rows"]
        for n in range(a,b+1):
            label=LABELS[n-a]
            lines[n-1]=label+" — 庚 —" if label=="中五宫" else label+" 地 休丙 芮丁"
        for j,n in enumerate(c["numbered_author_step_lines"],1):
            lines[n-1]=f"（{j}）合成作者分析"
        for n in c["validation_information_lines"]:
            lines[n-1]="合成书内反馈"
    lines[119]="1996年9月24日妇女到访，卢请她坐下，并在后文回答预测"
    lines[205]="张志春按：合成学员评注"
    lines[252]="张志春按：合成学员复审意见"
    raw=("\n".join(lines)+"\n").encode("utf-8")
    digest=hashlib.sha256(raw).hexdigest()
    cases["source_sha256"]=digest
    for c in cases["cases"]:c["source_sha256"]=digest
    methods["source_sha256"]=digest
    return raw,cases,methods,digest

class PregnancySixCaseTests(TestCase):
    def test_case_numbers_and_source_boundaries(self):
        raw,idx,methods,digest=synthetic()
        self.assertEqual(len(idx["cases"]),6)
        self.assertEqual(sum(len(c["numbered_author_step_lines"]) for c in idx["cases"]),23)
        self.assertEqual(len(methods["methods"]),24)
        self.assertEqual(len({c["event_family_id"] for c in idx["cases"]}),6)
        self.assertEqual(idx["cases"][0]["linked_event_family"],idx["cases"][1]["linked_event_family"])
        self.assertNotEqual(idx["cases"][0]["casting"]["local_date"],idx["cases"][1]["casting"]["local_date"])
        self.assertTrue(all(c["book_outcome_label"]=="author_book_success_default" for c in idx["cases"]))
        self.assertFalse(any(c["author_explicit_error_admission"] for c in idx["cases"]))

    def test_private_additive_complete_import_and_idempotency(self):
        raw,idx,methods,digest=synthetic()
        with TemporaryDirectory() as t:
            d=Path(t);source=d/"ch03.txt";source.write_bytes(raw)
            idx["source_sha256"]=digest
            folder=d/"public";folder.mkdir()
            (folder/"case_index.json").write_text(json.dumps(idx,ensure_ascii=False))
            (folder/"method_index.json").write_text(json.dumps(methods,ensure_ascii=False))
            db=d/"private.sqlite3"
            initialize(db)
            import_section(db,"shenqi","shijia_qiju","Old chapter","旧书原文保留")
            with patch.object(mod,"SHA",digest),patch.object(mod,"DATA",folder):
                first=mod.import_pregnancy_chapter(db,source,retrofit_health=False)
                second=mod.import_pregnancy_chapter(db,source,retrofit_health=False)
            self.assertEqual(first["case_families"],6)
            self.assertEqual(first["literal_chart_rows"],54)
            self.assertEqual(first["author_reasoning_steps"],23)
            self.assertEqual(first["source_method_items"],24)
            self.assertEqual(second["case_families"],6)
            with connect(db) as con:
                self.assertEqual(con.execute("SELECT count(*) FROM sections").fetchone()[0],2)
                self.assertEqual(con.execute("SELECT count(*) FROM historical_case_book_verdicts").fetchone()[0],6)
                self.assertEqual(con.execute("SELECT count(*) FROM historical_case_disclosures WHERE fact_type='source_provenance_not_case_failure'").fetchone()[0],2)
                self.assertEqual(con.execute("SELECT count(*) FROM semantic_assertions").fetchone()[0],24)
            event=idx["cases"][1]["event_family_id"]
            brief=get_whole_event(db,event)
            study=get_whole_event(db,event,view="source_study")
            self.assertEqual(len(brief["one_source_chart"]),9)
            self.assertEqual(brief["book_outcome_label"],"author_book_success_default")
            self.assertNotIn("original_later_feedback",brief)
            self.assertEqual(len(study["author_analysis_steps"]),5)
            self.assertTrue(study["validation_information"])

    def test_wrong_uploaded_source_never_creates_database(self):
        with TemporaryDirectory() as t:
            p=Path(t)/"bad.txt";p.write_text("No chapter")
            db=Path(t)/"not-created.sqlite3"
            with self.assertRaisesRegex(ValueError,"SHA256 mismatch"):
                mod.import_pregnancy_chapter(db,p)
            self.assertFalse(db.exists())

if __name__=="__main__":
    import unittest
    unittest.main()
