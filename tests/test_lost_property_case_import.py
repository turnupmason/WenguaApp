"""No copyrighted source in CI: eight cases and author steps synthesized."""
import hashlib,json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch
from src.wengua import compile_shenqi_lost_property as m
from src.wengua.database import connect,initialize,import_section
from src.wengua.case_reasoning_trace import get_case_trace
ROOT=Path(__file__).resolve().parents[1]
D=ROOT/"data/knowledge/shenqi/lost_money_property_prediction_ch09"
N=(("巽四宫","离九宫","坤二宫"),("震三宫","中五宫","兑七宫"),("艮八宫","坎一宫","乾六宫"))
def synthetic():
    d={n:json.loads((D/(n+".json")).read_text(encoding="utf8")) for n in
       ("chapter_manifest","case_index","method_index","source_audit")}
    s=["Synthetic only test"]*362
    s[0]="钱物丢失预测";s[13]="第二节 实例解析（8例）"
    for c in d["case_index"]["cases"]:
        i=c["case_number"];start=c["original_chart_start"]
        s[c["source_span"][0]-1]="实例%d：合成"%i
        s[start-1]="┌─┬─┬─┐"
        for row in range(3):
            n=start+1+4*row
            s[n-1]="│"+"│".join(v+("  中宫" if v=="中五宫" else " 八神：合") for v in N[row])+"│"
            s[n]="│"+"│".join("中宫原字：戊" if v=="中五宫" else "门位原字：开甲" for v in N[row])+"│"
            s[n+1]="│"+"│".join("" if v=="中五宫" else "星位原字：辅乙" for v in N[row])+"│"
        for n in c["numbered_or_unnumbered_analysis_lines"]:
            s[n-1]="（1）合成来源一宫证据与景门"
        for n in c["later_book_feedback_lines"]:s[n-1]="合成后来反馈不可泄漏"
    s[112]="源书作者无编号初判";s[116]="源书作者无编号再次分析"
    s[252]="文件在车里，这一点事先没有断出。"
    s[306]="张志春按：合成复盘"
    raw=("\n".join(s)+"\n").encode("utf8")
    digest=hashlib.sha256(raw).hexdigest()
    for value in d.values():value["source_sha256"]=digest
    d["chapter_manifest"]["source_utf8_bytes"]=len(raw)
    return raw,digest,d
class LostPropertyImportTest(TestCase):
    def test_manifest_source_counts_and_historical_retroaudit(self):
        mta=json.loads((D/"chapter_manifest.json").read_text(encoding="utf8"))
        cases=json.loads((D/"case_index.json").read_text(encoding="utf8"))["cases"]
        self.assertEqual((mta["source_lines"],mta["source_utf8_bytes"],len(cases)),(362,34197,8))
        self.assertEqual(sum(len(c["numbered_or_unnumbered_analysis_lines"]) for c in cases),36)
        a=json.loads((ROOT/"data/knowledge/shenqi/case_reasoning_retroaudit.json").read_text(encoding="utf8"))
        self.assertEqual(len(a["old_history"]),58)
        self.assertTrue(all(not c["positive_training_eligible"] for c in a["old_history"]))
    def test_private_non_destructive_import_idempotent(self):
        raw,sha,data=synthetic()
        with TemporaryDirectory() as tmp:
            p=Path(tmp);source=p/"original.txt";source.write_bytes(raw)
            d=p/"meta";d.mkdir()
            for name,x in data.items():(d/(name+".json")).write_text(json.dumps(x,ensure_ascii=False),encoding="utf8")
            db=p/"private.sqlite"
            initialize(db)
            import_section(db,"shenqi","unrelated_prior_chapter","old","PRIOR SOURCE INTACT")
            with patch.object(m,"SHA",sha),patch.object(m,"INDEX",d):
                first=m.import_lost_property(db,source)
                second=m.import_lost_property(db,source)
            self.assertEqual((first["cases"],first["palaces"],first["author_steps"],first["candidates"],first["traces"]),(8,72,36,54,36))
            self.assertEqual(second["mechanical_legacy_traces_newly_created_if_private_db_supplied"],0)
            with connect(db) as c:
                self.assertEqual(c.execute("SELECT original_text FROM sections WHERE section_key='unrelated_prior_chapter'").fetchone()[0],"PRIOR SOURCE INTACT")
                self.assertEqual(c.execute("PRAGMA integrity_check").fetchone()[0],"ok")
                self.assertFalse(c.execute("PRAGMA foreign_key_check").fetchall())
            initial=get_case_trace(db,"shenqi.lost_property.case06")
            self.assertNotIn("author_judgment",initial)
            advanced=get_case_trace(db,"shenqi.lost_property.case06",view="source_study")
            self.assertEqual(len(advanced["author_step_traces"]),5)
    def test_wrong_source_hash_prevents_mutation(self):
        with TemporaryDirectory() as tmp:
            path=Path(tmp);source=path/"wrong.txt";source.write_text("wrong")
            db=path/"notcreated.sqlite"
            with self.assertRaisesRegex(ValueError,"SHA256 mismatch"):m.import_lost_property(db,source)
            self.assertFalse(db.exists())
