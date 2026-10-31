"""Real-clock default BigFish launch window regression (not abstract 518400).

Tests dates/DST/source gates/immutable export without launching fake BigFish.
An additional CI integration actually runs original BigFish TypeScript.
"""
from __future__ import annotations
import importlib.util
import json
import sqlite3
import sys
import tempfile
import types
import unittest
import zipfile
from datetime import date
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
TARGET=ROOT/"scripts/wengua_bigfish_518400_offline_editorial_20261029.py"

def load():
    stub=types.ModuleType("local_batch")
    stub.BIGFISH_SHA="6112b3937d7fcaa2ab0a34aec2a52f74e2effe6c"
    stub.WENGUA_SHA="a288d127883157cb2bea96b676d2c86a45c2ab12"
    stub.GRADE={x:str(x) for x in range(-5,6)}
    stub.COMPILED=ROOT/"build"/"bigfish_fixture"
    old=sys.modules.get("local_batch")
    try:
        sys.modules["local_batch"]=stub
        spec=importlib.util.spec_from_file_location("bigfish_true_date_test",TARGET)
        m=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        return m
    finally:
        if old is None:sys.modules.pop("local_batch",None)
        else:sys.modules["local_batch"]=old

M=load()

class RealClockWindow(unittest.TestCase):
    def test_default_mode_is_real_calendar_not_518400(self):
        self.assertEqual(M.BATCH_MODE,"real_clock")
        self.assertEqual((M.REAL_DATE_START,M.REAL_DATE_END),
                         ("2026-11-15","2027-03-15"))
        self.assertEqual(M.MAX_NEW_ROWS,0) # Direct full window, not a trial
        self.assertEqual(M.N_CASES,518400) # old study preserved
        self.assertEqual(M.ROWS_PER_EXCEL,5000)
        self.assertIsNone(M.PATIENT_BIRTH_GANZHI)
    def test_all_local_dates_have_actual_twelve_distinct_branch_samples(self):
        rows=list(M.real_calendar_slots())
        self.assertEqual(len(rows),1452) # 121 inclusive dates *12
        self.assertEqual((rows[0]["date"],rows[-1]["date"]),
                         ("2026-11-15","2027-03-15"))
        self.assertEqual((rows[0]["branch"],rows[11]["branch"]),("子","亥"))
        self.assertEqual((rows[0]["instant"],rows[-1]["instant"]),
                         ("2026-11-15T00:30:00-05:00",
                          "2027-03-15T21:30:00-04:00"))
        self.assertEqual(len(set(x["instant"] for x in rows)),len(rows))
        self.assertFalse(any("T23:" in x["instant"] for x in rows))
        for start in range(0,len(rows),12):
            self.assertEqual(len({r["branch"] for r in rows[start:start+12]}),12)
    def test_real_spring_dST_has_real_offsets_both_sides(self):
        day={x["instant"][11:16]:x for x in M.real_calendar_slots()
             if x["date"]=="2027-03-14"}
        self.assertEqual(day["01:30"]["instant"][-6:],"-05:00")
        self.assertEqual(day["03:30"]["instant"][-6:],"-04:00")
        self.assertEqual(len(day),12)
    def test_bad_dates_and_timezone_fail_closed(self):
        with self.assertRaises(ValueError):
            list(M.real_calendar_slots("2027-03-16","2027-03-15"))
        with self.assertRaises(ValueError):
            list(M.real_calendar_slots(timezone_name="Not/AZone"))
        # 2026 fall-back civil clock is ambiguous, must not guess an UTC
        with self.assertRaisesRegex(ValueError,"DST"):
            list(M.real_calendar_slots("2026-11-01","2026-11-01"))
    def test_actual_calendar_entry_and_one_term_only(self):
        from src.wengua.astro_calendar import solar_chart_clock
        from src.wengua.casting_shenqi import bureau_for_term
        slot=next(M.real_calendar_slots())
        clock=solar_chart_clock(slot["instant"],slot["timezone"])
        expected=bureau_for_term(clock["four_pillars"]["day"],
                                 clock["active_solar_term"])
        class Worker:
            def bureau(self,term,day):
                self.term,self.day=term,day
                return {"isYangDun":expected["dun"]=="yang",
                        "juNumber":expected["ju"]}
        worker=Worker()
        fake={"status":"原始断词_待润色和人工审核",
              "score":1,"grade":"极小吉","text":"原始真实断词",
              "sections":[{"id":"x","text":"原始真实断词"}],
              "source_fact_lock":{"person_binding":{"stem":"丙"}},
              "original_text_sha256":"old"}
        with patch.object(M,"compute_variant",return_value=fake) as compute:
            result=M.real_case_from_slot(worker,slot,{"relationship":"father"})
        self.assertEqual(result["status"],fake["status"])
        self.assertEqual(worker.term,clock["active_solar_term"])
        self.assertEqual(worker.day,clock["four_pillars"]["day"])
        self.assertEqual(compute.call_count,1) # only actual active JieQi
        self.assertEqual(compute.call_args.args[1],clock["four_pillars"])
        self.assertEqual(result["source_fact_lock"]["exact_real_instant"],slot["instant"])
        self.assertEqual(result["source_fact_lock"]["iana_timezone"],slot["timezone"])
        self.assertTrue(result["not_a_two_hour_interval_certification"])
    def test_mismatched_actual_bigfish_bureau_cannot_fake_a_reading(self):
        slot=next(M.real_calendar_slots())
        class Wrong:
            def bureau(self,term,day):
                return {"isYangDun":False,"juNumber":99}
        with patch.object(M,"compute_variant") as calc:
            result=M.real_case_from_slot(Wrong(),slot,{"relationship":"father"})
        self.assertTrue(result["status"].startswith("失败"))
        self.assertIn("冲突",result["error"])
        calc.assert_not_called()
    def test_one_full_1452_row_excel_per_actor_then_no_rerun_overwrite(self):
        slots=list(M.real_calendar_slots())
        self.assertEqual(len(slots),1452)
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            config={"range":[M.REAL_DATE_START,M.REAL_DATE_END],
                    "actor":"father","source":"current"}
            db=M.initialize_real_db(root/"real.sqlite3",config)
            for slot in slots:
                i=slot["idx"]
                record={"idx":i,"instant":slot["instant"],"utc":slot["utc"],
                        "timezone":slot["timezone"],"branch":slot["branch"],
                        "case_id":"case-"+str(i),
                        "four_pillars":{"year":"丙午","month":"己亥",
                                        "day":"乙丑","hour":"丙子"},
                        "result":{"status":"原始断词_待润色和人工审核",
                                  "score":1,"grade":"极小吉",
                                  "text":"独立来源断词",
                                  "source_fact_lock":{"person_binding":{"stem":"丙"}},
                                  "original_text_sha256":"sourcehash"}}
                db.execute("INSERT INTO real_cases VALUES (?,?,?,?,?)",
                           (i,record["case_id"],slot["instant"],
                            M.canonical(record),"now"))
                if i==19:
                    db.commit()
                    self.assertIsNone(M.export_real_complete(
                        db,root,{"father":"父亲"},slots))
                    self.assertFalse(
                        (root/"Excel_CSV_可直接打开").exists())
            db.commit()
            out=M.export_real_complete(db,root,{"father":"父亲"},slots)
            self.assertTrue(out.is_file())
            directory=root/"Excel_CSV_可直接打开"
            self.assertEqual(len(list(directory.glob("*.xlsx"))),1)
            self.assertEqual(len(list(directory.glob("*.csv"))),1)
            self.assertEqual(len(list(directory.glob("*.jsonl"))),1)
            with zipfile.ZipFile(out) as book:
                sheet=book.read("xl/worksheets/sheet1.xml").decode("utf8")
                self.assertEqual(sheet.count("<row r="),1453) # heading+all
                self.assertIn(slots[0]["instant"],sheet)
                self.assertIn(slots[-1]["instant"],sheet)
            # User makes edits to the formal Excel: rerun must not overwrite.
            before=out.read_bytes()
            self.assertEqual(M.export_real_complete(
                db,root,{"father":"父亲"},slots),out)
            self.assertEqual(out.read_bytes(),before)
            # Human old 200-row snapshot is not our canonical workbook:
            # It remains in this folder but must never be removed.
            historic=directory/"father_真实时辰_0001-0200_旧稿.xlsx"
            historic.write_bytes(b"human-edited-history")
            self.assertEqual(M.export_real_complete(
                db,root,{"father":"父亲"},slots),out)
            self.assertEqual(historic.read_bytes(),b"human-edited-history")
            db.close()

    def test_immutable_database_and_real_xlsx_with_unique_real_clock(self):
        slots=list(M.real_calendar_slots())
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            cfg={"range":["2026-11-15","2027-03-15"],
                 "sha":"source-v1","relation":"father"}
            db=M.initialize_real_db(root/"case.sqlite3",cfg)
            for i in (0,1):
                slot=slots[i]
                result={"status":"原始断词_待润色和人工审核",
                        "score":1,"grade":"极小吉","text":"文章甲",
                        "term":"立冬","bureau":"阴3局",
                        "source_fact_lock":{"person_binding":{"stem":"甲",
                                                              "source_ganzhi":"甲子",
                                                              "carrier_stem":"戊",
                                                              "palace":1}},
                        "original_text_sha256":"text-sha"}
                row={"idx":i,"instant":slot["instant"],"utc":slot["utc"],
                     "timezone":slot["timezone"],"branch":slot["branch"],
                     "four_pillars":{"year":"丙午","month":"己亥",
                                      "day":"乙丑","hour":"丙子"},
                     "case_id":str(i),"result":result}
                db.execute("INSERT INTO real_cases VALUES (?,?,?,?,?)",
                           (i,str(i),slot["instant"],M.canonical(row),"now"))
            db.commit()
            file=M.export_real_new(db,root,{"father":"父亲"},[0,1])
            self.assertTrue(file.is_file())
            with zipfile.ZipFile(file) as archive:
                text=archive.read("xl/worksheets/sheet1.xml").decode("utf8")
            self.assertIn("2026-11-15T00:30:00-05:00",text)
            self.assertIn("完整V10.2原断词",text)
            self.assertNotIn("节气乙",text)
            self.assertEqual(len(list((root/"Excel_CSV_可直接打开").glob("*.jsonl"))),1)
            with self.assertRaises(FileExistsError):
                M.export_real_new(db,root,{"father":"父亲"},[0,1])
            db.close()
            with self.assertRaisesRegex(RuntimeError,"变更"):
                M.initialize_real_db(root/"case.sqlite3",{**cfg,"sha":"changed-source"})

if __name__=="__main__":
    unittest.main()
