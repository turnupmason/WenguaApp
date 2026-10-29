"""Real 1100-row father failure regression: refuse false Jia carrier, recover valid rows.

No frozen score or Swift production source is modified by this scheduler.
"""
from __future__ import annotations
import importlib.util,sys,types,unittest,tempfile,sqlite3,json
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
TARGET=ROOT/"scripts/wengua_bigfish_518400_offline_editorial_20261029.py"
def load():
    fake=types.ModuleType("local_batch")
    fake.BIGFISH_SHA="6112b3937d7fcaa2ab0a34aec2a52f74e2effe6c"
    fake.WENGUA_SHA="0eae7d2b94742939e885938f8603e85c9452d1c3"
    fake.GRADE={i:str(i) for i in range(-5,6)}
    prev=sys.modules.get("local_batch")
    sys.modules["local_batch"]=fake
    try:
        spec=importlib.util.spec_from_file_location("wengua_1100_regression",TARGET)
        m=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
    finally:
        if prev is None:sys.modules.pop("local_batch",None)
        else:sys.modules["local_batch"]=prev
    return m
M=load()
class Failure1100Regression(unittest.TestCase):
    def test_first_1100_all_unsupported_year_jia(self):
        f={"reference":{"kind":"casting_year_stem"},"context":"direct_proxy"}
        for i in range(1100):
            self.assertEqual(M.scenario(i)["year"],"甲子")
            self.assertIn("casting_year_stem",M.deferred_source_jia(M.scenario(i),f))
        self.assertEqual(M.scenario(8640)["year"],"乙丑")
        self.assertIsNone(M.deferred_source_jia(M.scenario(8640),f))
    def test_hour_jia_still_allowed_and_other_independent_jia_deferred(self):
        for kind,column in (("day_stem","day"),("casting_month_stem","month"),
                            ("casting_year_stem","year")):
            f={"reference":{"kind":kind},"context":"direct_proxy"}
            case={"day":"甲子","month":"甲寅","year":"甲子","hour":"甲子"}
            self.assertIsNotNone(M.deferred_source_jia(case,f))
        hour={"reference":{"kind":"casting_hour_stem"},"context":"direct_proxy"}
        self.assertIsNone(M.deferred_source_jia(M.scenario(0),hour))
        evt={"reference":{"kind":"casting_year_stem"},"context":"event_news"}
        self.assertIn("day_stem",M.deferred_source_jia(M.scenario(0),evt))
    def test_new_noncontiguous_export_retains_old_xlsx_and_jsonl(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            db=M.initialize_db(root/"existing.sqlite",{"locked":"same-original-input"})
            def record(idx,why):
                item={"term":"立春","bureau":"阳8局上元","grade":"","score":"",
                      "status":"失败_保留原样","text":"",
                      "base_id":"yang-08-甲子","evidence_sha":"","error":why,
                      "sections":[],"source_fact_lock":{}}
                db.execute("INSERT INTO cases VALUES (?,?,?,?,?,?)",
                    (idx,str(idx),M.canonical(M.scenario(idx)),M.canonical(item),
                     M.canonical({**item,"term":"雨水"}),"now"))
            record(0,"原始年甲历史失败不能删除")
            record(8640,"新来源另一个真实失败；同样必须保留")
            db.commit()
            folder=root/"Excel_CSV_可直接打开"
            folder.mkdir(parents=True)
            oldfile=folder/"father_000001-001100.xlsx"
            oldfile.write_bytes(b"human-edited-old-file")
            M.RELATIONSHIP="father"
            name=M.export_new_batch(db,root,{"father":"父亲"},[8640])
            self.assertTrue(Path(name).exists())
            self.assertEqual(oldfile.read_bytes(),b"human-edited-old-file")
            self.assertEqual(db.execute("SELECT COUNT(*) FROM cases").fetchone()[0],2)
            self.assertEqual(json.loads(db.execute("SELECT result_jie_json FROM cases WHERE idx=0").fetchone()[0])["error"],
                             "原始年甲历史失败不能删除")
            files=list(folder.glob("*_待审事实包.jsonl"))
            self.assertEqual(len(files),1)
            self.assertEqual(len(files[0].read_text(encoding="utf8").splitlines()),2)
            db.close()
    def test_no_rule_or_natal_change(self):
        self.assertIsNone(M.PATIENT_BIRTH_GANZHI)
        self.assertTrue(M.DEFER_UNRESOLVED_JIA)
        self.assertEqual(M.N_CASES,518400)
        self.assertEqual(len([x for x in M.CYCLE60 if x[0]=="甲"]),6)

if __name__=="__main__":unittest.main()
