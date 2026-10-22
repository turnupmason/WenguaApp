"""V3.0 user-supplement domain rules: no invented outcomes or per-chart GPT."""
import json,unittest
from pathlib import Path
from unittest.mock import patch
from scripts.run_two_historical_health_v30 import evaluate,LATEST_DB
from src.wengua.health_severity_v30 import (
 analyze_health_severity_v30,_pair_matches,_composites,PAIRS,CURRICULUM,TEMPLATE)
from src.wengua.casting_shenqi import layout_from_explicit_bureau
from src.wengua.astro_calendar import solar_chart_clock

class V30DiseaseDomainCurriculum(unittest.TestCase):
 def test_full_supplement_catalog_and_immutable_prior(self):
    bank=json.loads(PAIRS.read_text("utf8"))
    text=json.loads(CURRICULUM.read_text("utf8"))
    self.assertGreaterEqual(len(bank["pairs"]),40)
    self.assertGreaterEqual(len(bank["composites"]),15)
    self.assertGreaterEqual(len(text["role_order"]),8)
    self.assertIn("further rule verification",text["statuses"]["indexed_not_executable"])
    self.assertEqual(len(json.loads(TEMPLATE.read_text("utf8"))["sections"]),11)
    self.assertEqual(LATEST_DB.name,"WenguaApp_双书194案例_精简医药旺衰应期V2_9_完整研究库.sqlite3")
 def test_old_historical_probes_no_answer_and_preserve_older_seals(self):
    r=evaluate()
    self.assertTrue(r["prior_v27_v28_v29_seals_untouched"])
    self.assertFalse(r["source_author_endings_used"])
    self.assertEqual(len(r["samples"]),2)
    for p in r["samples"]:
     self.assertEqual(p["provisional_traditional_verdict"],"病凶")
     self.assertFalse(p["source_book_answer_used"])
     self.assertIn("患者宫是病情传统吉凶的重要依据",p["readout"])
     self.assertIn("时干主病情现状与发展",p["readout"])
     self.assertNotIn("必死",p["readout"])
     self.assertNotIn("必定是癌症",p["readout"])
     self.assertNotIn("。。",p["readout"])
     self.assertNotIn("门门迫",p["readout"])
     self.assertEqual(len(p["sha256"]),64)
     self.assertGreaterEqual(len(p["sections"]),10)
     med=next(x["text"] for x in p["sections"] if x["id"]=="07_medicine")
     self.assertLessEqual(med.count("天心月废"),1)
     self.assertIn("及时得到医治的机会",p["readout"])
 def test_illness_role_specific_pair_vs_patient_role_distinction(self):
    bank=json.loads(PAIRS.read_text("utf8"))
    cell={"earth_stem":"庚","palace":1,
          "heaven_stars":[{"star":"天芮星","carried_stem":"丙"}],
          "door":"死门","deity":"六合"}
    a=_pair_matches({},cell,"illness",bank)
    b=_pair_matches({},cell,"patient",bank)
    self.assertEqual(a[0]["name"],"荧入太白")
    self.assertNotEqual(a[0]["meaning"],b[0]["meaning"])
    self.assertNotIn("病人必死",a[0]["meaning"])
 def test_composite_only_actual_palace_cells(self):
    ill={"palace":9,"earth_stem":"己","door":"休门","deity":"太阴",
         "heaven_stars":[{"star":"天芮星","carried_stem":"乙"}]}
    person={"palace":6,"earth_stem":"丙","door":"开门","deity":"九地",
         "heaven_stars":[{"star":"天心星","carried_stem":"戊"}]}
    got=_composites(ill,person)
    self.assertEqual([x["name"] for x in got],["地遁"])
    self.assertEqual(_composites({**ill,"earth_stem":"乙"},person),[])
 def test_local_only_byte_repeat(self):
    with patch("socket.socket",side_effect=AssertionError("Offline required")):
     a=evaluate();b=evaluate()
    self.assertEqual([x["readout"].encode() for x in a["samples"]],
                     [x["readout"].encode() for x in b["samples"]])
 def test_new_unknown_context_does_not_invent_age_marriage_or_prognosis(self):
    t=solar_chart_clock("2026-10-21T15:30:00-04:00","America/New_York")
    chart=layout_from_explicit_bureau(dun="yin",ju=6,hour_ganzhi="庚申")
    cal={"year_ganzhi":"丙午","month_ganzhi":"戊戌","day_ganzhi":"戊辰",
         "hour_ganzhi":"庚申","month_branch":"戌"}
    r=analyze_health_severity_v30(chart=chart,inquiry={
      "intent":"severity","relationship":"self","consultation_context":"direct_self"},
      calendar=cal,db_path=LATEST_DB)
    self.assertFalse(r["user_accepted"])
    self.assertFalse(r["audit"]["v30_rules"]["ground_kun_referenced"] is False)
    self.assertNotIn("年命未提供",r["reading_text"])
    self.assertNotIn("癌症",r["reading_text"])
    self.assertIn("传统主判",r["reading_text"])
    with self.assertRaises(ValueError):
     analyze_health_severity_v30(chart=chart,inquiry={
       "intent":"surgery","relationship":"self","consultation_context":"direct_self"},
       calendar=cal,db_path=LATEST_DB)
 def test_print_full_fixed_two_case_output(self):
    for n,row in enumerate(evaluate()["samples"],1):
     print("\nV30_CASE_"+str(n)+"_BEGIN")
     print(row["readout"])
     print("SHA256="+row["sha256"])
     print("V30_CASE_"+str(n)+"_END")

if __name__=="__main__":unittest.main()
