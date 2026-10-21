"""Runnable CLI handles unknown birth years, not an unresolved missing-year failure."""
from __future__ import annotations
import json,tempfile,unittest
from pathlib import Path
from scripts.run_marriage_judgment_v18 import main
from scripts.evaluate_marriage_other_families_v17 import CASES
from src.wengua.casting_shenqi import layout_from_explicit_bureau
ROOT=Path(__file__).resolve().parents[1]
DB=ROOT/"archives/sqlite/WenguaApp_双书194案例_婚姻无年命作者取用方法V1_8_完整研究库.sqlite3"
class OptionalBirthYearCli(unittest.TestCase):
 def test_research_answer_for_book_cast_with_no_birth_year(self):
  case=CASES[1]
  chart=layout_from_explicit_bureau(dun=case["dun"],ju=case["ju"],hour_ganzhi=case["hour"])
  question={"chart":chart,"calendar_inputs":{
      "day_ganzhi":case["day"],"hour_ganzhi":case["hour"],
      "year_ganzhi":case["year"],"month_ganzhi":case["month"],
      "solar_term":case["solar_term"],"local_time_iso":case["date"],
      "iana_timezone":"Asia/Shanghai"},
      "inquiry":{"domain":"marriage","scene_id":"marriage.scene.19",
       "question_text":"双方没有出生年，问是否有复合机会。","relationship":"self"}}
  with tempfile.TemporaryDirectory() as d:
   inp=Path(d)/"original.json";out=Path(d)/"audit.json"
   inp.write_text(json.dumps(question,ensure_ascii=False),encoding="utf8")
   original_size=DB.stat().st_size
   result=main(["--input",str(inp),"--database",str(DB),"--output",str(out),
                "--exclude-event-family","kaiwu.marriage.case05"])
   saved=json.loads(out.read_text(encoding="utf8"))
   self.assertEqual(result["traditional_initial_outcome"],saved["traditional_initial_outcome"])
   self.assertEqual(result["year_role_binding"]["strategy"],"no_year_optional")
   self.assertNotEqual(result["traditional_initial_outcome"],"unresolved")
   self.assertEqual(result["year_role_binding"]["subject_year_palace"],None)
   self.assertEqual(result["year_role_binding"]["partner_year_palace"],None)
   self.assertTrue(result["missing_year_no_year_value_invented"])
   self.assertFalse(result["publication_ready"])
   self.assertEqual(DB.stat().st_size,original_size)
   self.assertNotIn("kaiwu.marriage.case05",
     [x["event_family_id"] for x in result["prior_method_witness_holdout"]["pre_event_method_witnesses"]])
if __name__=="__main__":unittest.main()
