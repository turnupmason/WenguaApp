"""Regression contract for offline BigFish -> frozen V8/V10.2 pre-generation.

No network or mock final verdicts are claimed to be real Wengua forecasts.
Tests cover enumeration, CSV/XLSX/JSONL, retained error, no overwrite, resume.
"""
import csv
import importlib.util
import json
import sqlite3
import sys
import tempfile
import types
import unittest
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
TARGET=ROOT/"scripts/wengua_bigfish_518400_offline_editorial_20261029.py"

def load_module():
    fake=types.ModuleType("local_batch")
    fake.BIGFISH_SHA="6112b3937d7fcaa2ab0a34aec2a52f74e2effe6c"
    fake.WENGUA_SHA="0eae7d2b94742939e885938f8603e85c9452d1c3"
    fake.GRADE={i:("grade"+str(i)) for i in range(-5,6)}
    previous=sys.modules.get("local_batch")
    sys.modules["local_batch"]=fake
    try:
        spec=importlib.util.spec_from_file_location("bigfish_precompute_test",str(TARGET))
        module=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    finally:
        if previous is not None:
            sys.modules["local_batch"]=previous
        else:
            sys.modules.pop("local_batch",None)
    return module

M=load_module()

class FrozenEditorialBatchContract(unittest.TestCase):
    def test_enumeration_518400_and_720_legal_hours(self):
        self.assertEqual(M.N_CASES,518400)
        self.assertEqual(M.scenario(0),{
            "year":"甲子","month":"丙寅","day":"甲子","hour":"甲子"})
        self.assertEqual(M.scenario(11)["hour"],"乙亥")
        self.assertEqual(M.scenario(12)["hour"],"丙子")
        self.assertEqual(M.scenario(518399)["year"],"癸亥")
        for day in M.CYCLE60:
            for branch in M.BRANCHES:
                self.assertIn(M.hour_ganzhi(day,branch),M.CYCLE60)

    def test_both_terms_no_early_stop_on_missing_role(self):
        self.assertFalse(M.STOP_IF_FIRST_ROW_FAILS)
        self.assertEqual(M.TERM_BY_MONTH["寅"],("立春","雨水"))
        self.assertEqual(M.TERM_BY_MONTH["戌"],("寒露","霜降"))
        self.assertIn("analyze_health_severity_review",
                      TARGET.read_text(encoding="utf8"))
        self.assertNotIn("result['grade']='吉'", TARGET.read_text(encoding="utf8"))

    def test_export_csv_xlsx_editorial_jsonl_and_keep_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            original_relation=M.RELATIONSHIP
            original_rows=M.ROWS_PER_EXCEL
            try:
                M.RELATIONSHIP="father"
                M.ROWS_PER_EXCEL=2
                db=M.initialize_db(root/"progress.sqlite3",{"version":"locked"})
                success={
                    "term":"立春","status":"原始断词_待润色和人工审核",
                    "grade":"中吉","score":3,"text":"真实原文不得由GPT改写为规则依据。",
                    "base_id":"yang-08-甲子","evidence_sha":"sha-lock",
                    "bureau":"阳8局上元","error":"",
                    "original_text_sha256":"text-hash",
                    "sections":[{"id":"90_review","title":"综合","text":"原文结论"}],
                    "source_fact_lock":{"score":3,"patient":"father"},
                }
                failure={
                    "term":"雨水","status":"失败_保留原样",
                    "grade":"","score":"","text":"",
                    "base_id":"yang-09-甲子","evidence_sha":"",
                    "bureau":"阳9局上元",
                    "error":"Patient signifier unresolved",
                    "sections":[],"source_fact_lock":{},"original_text_sha256":"",
                }
                for i in range(2):
                    db.execute(
                        "INSERT INTO cases VALUES (?,?,?,?,?,?)",
                        (i,"case"+str(i),M.canonical(M.scenario(i)),
                         M.canonical(success),M.canonical(failure),"now"))
                db.commit()
                self.assertEqual(
                    M.export_completed_chunks(db,root,{"father":"父亲"},completed_only=False),1)
                outputs=root/"Excel_CSV_可直接打开"
                csv_path=next(outputs.glob("*.csv"))
                xlsx_path=next(outputs.glob("*.xlsx"))
                jsonl_path=next(outputs.glob("*.jsonl"))
                with csv_path.open(encoding="utf-8-sig",newline="") as inp:
                    rows=list(csv.reader(inp))
                self.assertEqual(len(rows),3)
                self.assertIn("断词甲",rows[0])
                self.assertIn("GPT修订甲",rows[0])
                self.assertEqual(rows[1][12],success["text"])
                with zipfile.ZipFile(xlsx_path) as z:
                    self.assertIsNone(z.testzip())
                    self.assertIn("xl/worksheets/sheet1.xml",z.namelist())
                data=[json.loads(line) for line in jsonl_path.read_text("utf8").splitlines()]
                self.assertEqual(len(data),4)
                self.assertEqual(data[0]["original_result"]["original_text"],success["text"])
                self.assertFalse(data[0]["editorial"]["approved_for_app"])
                self.assertEqual(data[1]["original_result"]["original_text"],"")
                self.assertIn("unresolved",data[1]["original_result"]["failure_reason"])
                # Simulate real human edits: old original snapshots must not change.
                xlsx_before=xlsx_path.read_bytes()
                jsonl_before=jsonl_path.read_bytes()
                self.assertEqual(
                    M.export_completed_chunks(db,root,{"father":"父亲"},completed_only=False),0)
                self.assertEqual(xlsx_before,xlsx_path.read_bytes())
                self.assertEqual(jsonl_before,jsonl_path.read_bytes())
                db.close()
            finally:
                M.RELATIONSHIP=original_relation
                M.ROWS_PER_EXCEL=original_rows

    def test_db_frozen_settings_cannot_mutate(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/"check.sqlite3"
            m=M.initialize_db(p,{"actor":"father"})
            m.close()
            with self.assertRaisesRegex(RuntimeError,"DIFFERENT frozen config"):
                M.initialize_db(p,{"actor":"mother"})

if __name__=="__main__":
    unittest.main()
