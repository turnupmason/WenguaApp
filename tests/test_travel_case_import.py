"""Tenth-to-eleventh-chapter provenance gate; fake charts only, NEVER check in source text."""
import hashlib,json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch
from src.wengua import compile_shenqi_travel as t
from src.wengua.database import initialize,connect,import_section

ROOT=Path(__file__).resolve().parents[1]
P=ROOT/"data/knowledge/shenqi/travel_abroad_prediction_ch07"
SHA="c273c803eb78a02cfb3c6c00065da81312c1851a679a1e3bca4911acdbc3bc55"
NAMES=(("巽四宫","离九宫","坤二宫"),("震三宫","中五宫","兑七宫"),("艮八宫","坎一宫","乾六宫"))

def synthetic():
    objects={n:json.loads((P/(n+".json")).read_text(encoding="utf-8"))
             for n in ("chapter_manifest","case_index","method_index","source_audit")}
    lines=["原创合成资料"]*350;lines[0]="出行出国预测";lines[20]="第二节 实例解析（6例）"
    for i,c in enumerate(objects["case_index"]["cases"]):
        lines[c["source_span"][0]-1]=f"实例{i+1}：测试"
        for start in c["original_chart_starts"]:
            lines[start-1]="┌────────────┬────────────┬────────────┐"
            for r in range(3):
                a=start+4*r
                lines[a]="│"+"│".join(f"{name}  八神：神" for name in NAMES[r])+"│"
                lines[a+1]="│"+"│".join(["门位：开甲","中宫原字：癸" if r==1 else "门位：死乙","门位：惊丙"])+"│"
                lines[a+2]="│"+"│".join(["星位：辅甲","" if r==1 else "星位：任乙","星位：心丙"])+"│"
                lines[a+3]="├─┼─┼─┤" if r<2 else "└─┴─┴─┘"
        for j,p in enumerate(c["numbered_reasoning_lines"],1):
            lines[p-1]=f"（{j if i not in (3,5) else (j if j<=3 else j-3)}）合成步骤"
    raw=("\n".join(lines)+"\n").encode()
    digest=hashlib.sha256(raw).hexdigest()
    for obj in objects.values():obj["source_sha256"]=digest
    objects["chapter_manifest"]["source_utf8_bytes"]=len(raw)
    return raw,objects,digest

class TravelStudyTests(TestCase):
    def test_six_whole_events_seven_actual_charts_and_handoff(self):
        meta=json.loads((P/"chapter_manifest.json").read_text())
        cases=json.loads((P/"case_index.json").read_text())["cases"]
        methods=json.loads((P/"method_index.json").read_text())["methods"]
        self.assertEqual((meta["source_lines"],meta["source_utf8_bytes"]),(350,31026))
        self.assertEqual(meta["source_sha256"],SHA)
        self.assertEqual((len(cases),sum(len(c["original_chart_starts"]) for c in cases),
                          sum(len(c["numbered_reasoning_lines"]) for c in cases),len(methods)),(6,7,29,38))
        self.assertEqual(cases[3]["original_chart_starts"],[157])
        self.assertEqual(cases[5]["original_chart_starts"],[293,324])
        for p in ("AGENTS.md","docs/PROJECT_STATUS.md","docs/CHAPTER_LEDGER.md"):
            s=(ROOT/p).read_text(encoding="utf-8")
            for x in ("11章","48","690",SHA):self.assertIn(x,s)

    def test_synthetic_import_is_complete_non_destructive_idempotent(self):
        raw,objects,sha=synthetic()
        with TemporaryDirectory() as tmp:
            root=Path(tmp);private=root/"local.sqlite3";source=root/"source.txt";source.write_bytes(raw)
            meta=root/"fake";meta.mkdir()
            for k,v in objects.items():(meta/(k+".json")).write_text(json.dumps(v,ensure_ascii=False))
            initialize(private)
            import_section(private,"shenqi","old","old","PRESERVE")
            with patch.object(t,"SHA",sha),patch.object(t,"INDEX",meta):
                a=t.import_travel_chapter(private,source)
                b=t.import_travel_chapter(private,source)
            self.assertEqual((a["source_cases"],a["historical_chart_cells"],a["historical_case_reasoning"],a["historical_case_additional_casts"],a["source_rules"]),(6,54,29,1,38))
            self.assertEqual(a,b)
            with connect(private) as db:
                self.assertEqual(db.execute("select count(*) from historical_case_additional_cast_cells").fetchone()[0],9)
                self.assertEqual(db.execute("select count(*) from historical_case_book_verdicts").fetchone()[0],6)
                self.assertEqual(db.execute("select original_text from sections where section_key='old'").fetchone()[0],"PRESERVE")
                self.assertEqual(db.execute("pragma integrity_check").fetchone()[0],"ok")
                self.assertFalse(db.execute("pragma foreign_key_check").fetchall())
                fourth=objects["case_index"]["cases"][3]["case_id"]
                self.assertNotIn("十月",db.execute("select known_before from cases where case_id=?",(fourth,)).fetchone()[0])

    def test_sha_mismatch_aborts_before_mutation(self):
        with TemporaryDirectory() as tmp:
            src=Path(tmp)/"bad.txt";src.write_text("invalid");db=Path(tmp)/"no.sqlite3"
            with self.assertRaisesRegex(ValueError,"SHA256 mismatch"):t.import_travel_chapter(db,src)
            self.assertFalse(db.exists())
