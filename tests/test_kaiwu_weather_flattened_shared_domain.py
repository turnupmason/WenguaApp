"""Kaiwu weather: two true book inquiries with TWO OCR-unresolvable boards.

Keep 33 literal source lines intact and ZERO invented nine-palace cells.
Shared weather_historical_source domain with five older Shenqi weather cases.
"""
from __future__ import annotations
import hashlib,json,sqlite3,tempfile,unittest
from pathlib import Path
from scripts.build_kaiwu_weather_from_criminal import (
 ROOT,BASE_NAME,BASE_SHA,NEW_NAME,SOURCE_SHA,validate,build,CASES
)
PARENT=ROOT/"archives/sqlite"/BASE_NAME
SOURCE=ROOT/"sources/kaiwu/开悟之门_天时气象预测.txt"
class KaiwuWeatherUnresolvedOriginalTest(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.raw=SOURCE.read_bytes()
  cls.L=validate(cls.raw)
 def test_original_bytes_and_two_flattened_charts_no_invented_cells(self):
  self.assertEqual(len(self.raw),6643)
  self.assertEqual(len(self.L),79)
  self.assertEqual(hashlib.sha256(self.raw).hexdigest(),SOURCE_SHA)
  self.assertEqual(len(CASES),2)
  self.assertEqual([e["chart"] for e in CASES],[(16,32),(52,67)])
  self.assertEqual(sum(e["chart"][1]-e["chart"][0]+1 for e in CASES),33)
  self.assertEqual([e["steps"] for e in CASES],[[36,38,40,42],[71,73,75,77]])
  self.assertIn("生  王",self.L[22])
  self.assertIn("冲  士",self.L[23])
  self.assertEqual(self.L[15],"阴")
  self.assertEqual(self.L[51],"武")
 def test_reported_dates_and_source_only_no_hydrological_measurements(self):
  self.assertIn("4月24日",self.L[41])
  self.assertIn("4月25日",self.L[41])
  self.assertIn("4月26日",self.L[41])
  self.assertIn("两天天气晴朗",self.L[44])
  self.assertIn("下起雨来",self.L[44])
  self.assertIn("有一位同志要搬家",self.L[43])
  self.assertIn("长江发生特大洪水",self.L[47])
  self.assertIn("壬戌月",self.L[77])
  self.assertIn("果验",self.L[77])
 def test_exact_complete_sqlite_append_old_source_rows_are_unchanged(self):
  self.assertEqual(hashlib.sha256(PARENT.read_bytes()).hexdigest(),BASE_SHA)
  with tempfile.TemporaryDirectory() as tmp:
   out=Path(tmp)/NEW_NAME;idx=Path(tmp)/"index"
   m=build(PARENT,SOURCE,out,idx)
   self.assertEqual(m["independent_historical_events"],163)
   self.assertEqual(m["new_recoverable_complete_original_nine_palace_grids"],0)
   self.assertEqual(m["all_original_OCR_fragment_lines_stored"],33)
   with sqlite3.connect(out) as db:
    for table,count in m["counts"].items():
     self.assertEqual(db.execute('SELECT count(*) FROM "'+table+'"').fetchone()[0],count)
    self.assertEqual(db.execute("SELECT count(*) FROM historical_chart_cells").fetchone()[0],1440)
    self.assertEqual(db.execute("SELECT count(*) FROM historical_palace_standardization").fetchone()[0],1611)
    self.assertEqual(db.execute("SELECT count(*) FROM kaiwu_weather_raw_cast_fragments").fetchone()[0],2)
    self.assertEqual(db.execute("SELECT count(*) FROM kaiwu_weather_raw_fragment_lines").fetchone()[0],33)
    self.assertEqual(db.execute("SELECT count(*) FROM historical_weather_cast_context").fetchone()[0],7)
    old_new={f"shenqi.weather.case{i:02d}" for i in range(1,6)}|{"kaiwu.weather.case01","kaiwu.weather.case02"}
    self.assertTrue(old_new.issubset({r[0] for r in db.execute("SELECT case_id FROM unified_weather_source_cases_across_books")}))
    self.assertEqual(db.execute("SELECT count(*) FROM historical_case_book_verdicts WHERE verdict='author_book_error_explicit'").fetchone()[0],10)
    self.assertEqual(db.execute("SELECT original_text FROM sections WHERE section_key='weather_prediction_ch02_section13'").fetchone()[0],self.raw.decode("utf8"))
    self.assertEqual(db.execute("PRAGMA integrity_check").fetchone()[0],"ok")
    self.assertEqual(db.execute("PRAGMA foreign_key_check").fetchall(),[])
   audit=json.loads((idx/"temporal_and_book_claim_audit.json").read_text("utf8"))
   self.assertTrue(audit["no_fabricated_nine_palace_chart_cells"])
   self.assertTrue(audit["book_flood_retreat_guoyan_no_gauged_verification"])
if __name__=="__main__":unittest.main()
