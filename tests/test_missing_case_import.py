"""Synthetic only CI regression: ten original cases, eleven real charts, three initial errors."""
import json,hashlib
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch
from src.wengua import compile_shenqi_missing as m
from src.wengua.database import initialize,import_section,connect
P=Path(__file__).resolve().parents[1]
D=P/"data/knowledge/shenqi/missing_person_prediction_ch08"
NAMES=(("巽四宫","离九宫","坤二宫"),("震三宫","中五宫","兑七宫"),("艮八宫","坎一宫","乾六宫"))
def synthetic():
    data={n:json.loads((D/(n+".json")).read_text(encoding="utf8"))
          for n in ("chapter_manifest","case_index","method_index","source_audit")}
    lines=["合成非版权测试材料"]*477
    lines[0]="行人走失预测";lines[14]="第二节 实例解析（10例）"
    for case in data["case_index"]["cases"]:
        i=case["case_number"]
        lines[case["source_span"][0]-1]=f"实例{i}：模拟"
        for start in case["original_chart_starts"]:
            lines[start-1]="┌──┬──┬──┐"
            for k,offset in enumerate((1,6,11)):
                panel=[NAMES[k],("合","原五","符"),("开甲","", "死乙"),("辅甲","", "任乙")]
                for j in range(4):
                    n=start+offset+j
                    lines[n-1]="│"+"│".join(panel[j])+"│"
                if k<2:lines[start+offset+4-1]="├─┼─┼─┤"
            lines[start+15-1]="└─┴─┴─┘"
        for pos in case["numbered_reasoning_lines"]:
            lines[pos-1]="(1) 合成来源分析"
    lines[136]="1997年2月26日出走；4月11日其父母找到我预测，此段后面假设有结局"
    lines[238]="此例断错，应该复盘"
    lines[400]="此例断错，原判断不正确"
    lines[456]="来信问哪里判断不对"
    raw=("\n".join(lines)+"\n").encode("utf8")
    digest=hashlib.sha256(raw).hexdigest()
    for o in data.values():o["source_sha256"]=digest
    data["chapter_manifest"]["source_utf8_bytes"]=len(raw)
    return raw,digest,data
class MissingSourceRegression(TestCase):
    def test_full_source_index_and_handoff(self):
        mta=json.loads((D/"chapter_manifest.json").read_text(encoding="utf8"))
        cs=json.loads((D/"case_index.json").read_text(encoding="utf8"))["cases"]
        rules=json.loads((D/"method_index.json").read_text(encoding="utf8"))["methods"]
        self.assertEqual((mta["source_lines"],mta["source_utf8_bytes"]),(477,49372))
        self.assertEqual((len(cs),sum(len(c["original_chart_starts"]) for c in cs),
             sum(len(c["numbered_reasoning_lines"]) for c in cs),len(rules)),(10,11,54,81))
        self.assertEqual([c["case_number"] for c in cs if c["explicit_source_error"]],[5,9,10])
        self.assertEqual(cs[1]["original_chart_starts"],[68,104])
        self.assertEqual(cs[9]["numbered_reasoning_lines"][-1],475)
        self.assertEqual(sum(not r.get("positive_training_eligible",True) for r in rules),6)
        for p in ("AGENTS.md","docs/PROJECT_STATUS.md","docs/CHAPTER_LEDGER.md"):
            t=(P/p).read_text(encoding="utf8")
            for needle in ("12章","58","771","行人走失","5eca2a1a0914691ec439040a9b538fb8e4385fa5cf8ac5286bc5ae86d25b6574"):
                self.assertIn(needle,t)
    def test_full_additive_source_idempotence_and_explicit_errors(self):
        raw,sha,data=synthetic()
        with TemporaryDirectory() as t:
            p=Path(t);file=p/"synthetic.txt";file.write_bytes(raw)
            directory=p/"meta";directory.mkdir()
            for name,o in data.items():(directory/(name+".json")).write_text(json.dumps(o,ensure_ascii=False))
            db=p/"private.sqlite3"
            initialize(db)
            import_section(db,"shenqi","previous","old","PRIOR PRIVATE BOOK UNTOUCHED")
            with patch.object(m,"SHA",sha),patch.object(m,"INDEX",directory):
                first=m.import_missing_chapter(db,file)
                again=m.import_missing_chapter(db,file)
            self.assertEqual(first,again)
            self.assertEqual((first["event_families"],first["main_chart_cells"],first["source_analysis_steps"],
                first["conditional_methods"],first["real_extra_charts"]),(10,90,54,81,1))
            with connect(db) as c:
                self.assertEqual(c.execute("SELECT count(*) FROM historical_case_additional_cast_cells").fetchone()[0],9)
                self.assertEqual(c.execute("SELECT count(*) FROM historical_case_book_verdicts WHERE verdict='author_book_error_explicit'").fetchone()[0],3)
                self.assertEqual(c.execute("SELECT original_text FROM sections WHERE section_key='previous'").fetchone()[0],"PRIOR PRIVATE BOOK UNTOUCHED")
                self.assertEqual(c.execute("PRAGMA integrity_check").fetchone()[0],"ok")
                self.assertFalse(c.execute("PRAGMA foreign_key_check").fetchall())
                self.assertNotIn("结局",c.execute("SELECT known_before FROM cases WHERE case_id='shenqi.missing.case03'").fetchone()[0])
    def test_reject_hash_change_before_database_created(self):
        with TemporaryDirectory() as t:
            src=Path(t)/"other.txt";src.write_text("wrong")
            db=Path(t)/"new.sqlite3"
            with self.assertRaisesRegex(ValueError,"SHA256 mismatch"):
                m.import_missing_chapter(db,src)
            self.assertFalse(db.exists())
