import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from src.wengua import compile_shenqi_health_cases as c
from src.wengua.database import initialize, import_section, connect
from src.wengua.health_research import health_method_plan, retrieve_historical_case

LABELS = ["巽四宫","离九宫","坤二宫","震三宫","中五宫","兑七宫","艮八宫","坎一宫","乾六宫"]
CN = "一二三四五六"

def fixture():
    idx=json.loads((c.DATA/"case_index.json").read_text(encoding="utf-8"))
    method=json.loads((c.DATA/"method_index.json").read_text(encoding="utf-8"))
    lines=["合成文字"]*298
    lines[0]="第一章 人体疾病预测"
    lines[12]="第二节 实例解析（6例）"
    lines[292]="—— 精校及盘面转写说明"
    for case in idx["cases"]:
        lines[case["line_range"][0]-1]="实例"+CN[case["index"]-1]+"：模拟"
        a,b=case["chart_rows"]
        for n in range(a,b+1):
            label=LABELS[n-a]
            lines[n-1]=label+" — 辛 —" if label=="中五宫" else label+" 符 休戊 蓬乙"
        for j,n in enumerate(case["steps"],1):
            lines[n-1]="（"+str(j)+"）模拟推理"
        for n in case["feedback_lines"]:
            lines[n-1]="后续反馈"+str(n)
        for disclosure in case.get("progressive_disclosures",[])+case.get("disclosure",{}).get("line_events",[]):
            lines[disclosure["lines"][0]-1]="中途披露"
    return "\n".join(lines)+"\n",idx,method

class Tests(unittest.TestCase):
    def test_indices(self):
        s,idx,m=fixture()
        self.assertEqual(len(idx["cases"]),6)
        self.assertEqual(sum(len(x["steps"]) for x in idx["cases"]),29)
        self.assertEqual(len(m["body_palace_mappings"]),8)
        self.assertEqual(len(m["yongshen_rules"]),14)
        self.assertEqual(len(m["author_workflow_nodes"]),8)
        self.assertEqual(health_method_plan("father")["personal_reference"]["symbol_concept_id"],"stem:年干")
        self.assertEqual(health_method_plan("nephew")["personal_reference"]["symbol_concept_id"],"stem:时干")
        self.assertTrue(health_method_plan("spouse")["no_personal_stem_fabricated"])

    def test_synthetic_import_and_no_leak(self):
        source,idx,m=fixture()
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            original=root/"source.txt"
            original.write_text(source,encoding="utf-8")
            digest=hashlib.sha256(original.read_bytes()).hexdigest()
            idx["file_source_sha256"]=digest
            for case in idx["cases"]:case["source_sha256"]=digest
            m["source_sha256"]=digest
            folder=root/"data";folder.mkdir()
            (folder/"case_index.json").write_text(json.dumps(idx,ensure_ascii=False),encoding="utf-8")
            (folder/"method_index.json").write_text(json.dumps(m,ensure_ascii=False),encoding="utf-8")
            db=root/"private.sqlite3"
            initialize(db)
            import_section(db,"shenqi","shijia_qiju","old chapter","保留旧数据")
            with patch.object(c,"EXPECTED_SHA",digest),patch.object(c,"DATA",folder):
                x=c.import_health_chapter(db,original)
                y=c.import_health_chapter(db,original)
            self.assertEqual((x["method_assertions"],x["case_charts"],x["nine_palace_literal_cells"],x["author_reasoning_steps"]),(30,6,54,29))
            self.assertEqual(y["case_charts"],6)
            with connect(db) as con:
                self.assertEqual(con.execute("SELECT COUNT(*) FROM sections").fetchone()[0],2)
                self.assertEqual(con.execute("SELECT COUNT(*) FROM historical_case_disclosures").fetchone()[0],4)
                self.assertEqual(con.execute("SELECT COUNT(*) FROM rules WHERE status='approved'").fetchone()[0],0)
            import src.wengua.health_research as r
            caseid=idx["cases"][0]["event_family_id"]
            with patch.object(r,"INDEX",folder/"case_index.json"):
                blind=retrieve_historical_case(db,caseid)
                study=retrieve_historical_case(db,caseid,view="source_study")
            self.assertNotIn("later_feedback",blind)
            self.assertNotIn("author_judgment",blind)
            self.assertEqual(len(blind["verbatim_chart_cells"]),9)
            self.assertIn("later_feedback",study)
            self.assertEqual(len(study["author_reasoning"]),5)

    def test_wrong_hash_blocks_mutation(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"bad.txt";path.write_text("not the right chapter")
            db=Path(tmp)/"new.sqlite3"
            with self.assertRaisesRegex(ValueError,"SHA256 mismatch"):
                c.import_health_chapter(db,path)
            self.assertFalse(db.exists())

if __name__=="__main__":
    unittest.main()
