"""V1.7 executable source-lines, 81 nonreversible 克应, 六仪/星门 guards."""
from __future__ import annotations
import json,unittest
from src.wengua.casting_shenqi import layout_from_explicit_bureau
from src.wengua.astro_calendar import solar_chart_clock
from src.wengua.marriage_book_combinator_v17 import (
 load_author_source_rules,compute_author_combinations,SIX_YI,TRI_TOMB,HORSE,
 conditional_hierarchy)
from src.wengua.marriage_judgment_v16 import _traditional_decision
from src.wengua.marriage_runtime import ELEMENTS
class MarriageBookCombo(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.rules,cls.pairs=load_author_source_rules()
 def test_canonical_rule_line_full_document_sha_and_81_directional_pairs(self):
  self.assertEqual(len(self.rules),27)
  self.assertEqual(len(self.pairs),81)
  self.assertTrue(all(len(r["source_sha256"])==64 and len(r["excerpt_sha256"])==64 for r in self.rules.values()))
  self.assertEqual(self.rules["six_yi_3"]["source_line"],514)
  self.assertIn("庚加8宫",self.rules["six_yi_3"]["original_line"])
  self.assertEqual(self.rules["sanqi_tomb"]["source_line"],532)
  self.assertEqual(self.rules["fanyin_marriage"]["source_line"],574)
  self.assertEqual(len({(a,b) for a,b in self.pairs}),81)
  self.assertNotEqual(self.pairs[("庚","乙")]["source_line"],self.pairs[("乙","庚")]["source_line"])
 def test_exact_six_instruments_tomb_and_horse_never_nonsourced_palace(self):
  self.assertEqual(SIX_YI,{"戊":3,"己":2,"庚":8,"辛":9,"壬":4,"癸":4})
  self.assertEqual(TRI_TOMB,{"乙":6,"丙":6,"丁":8})
  self.assertEqual(HORSE["辰"],"寅")
  self.assertEqual(HORSE["申"],"寅")
  self.assertEqual(HORSE["卯"],"巳")
  self.assertNotEqual(SIX_YI["庚"],3)
 def test_true_civil_astrology_source_facts_and_fuyin_not_synthetic_rows(self):
  chart=layout_from_explicit_bureau(dun="yin",ju=3,hour_ganzhi="丁亥")
  clock=solar_chart_clock("1998-11-09T21:22:00+08:00","Asia/Shanghai")
  result=compute_author_combinations(chart,clock)
  self.assertEqual(result["source_rule_catalog_count"],27)
  self.assertEqual(result["directional_stem_pair_count"],81)
  self.assertEqual(len(result["month_palace_strength"]),9)
  self.assertEqual(len(result["day_hour_specialized_relationship"]["day_palaces"])>=1,True)
  self.assertEqual(set(result["fu_yin_fan_yin"]).issuperset(
      {"star_fuyin","door_fuyin","star_fanyin","door_fanyin"}),True)
  self.assertEqual(result["source_rule_matches"]["time_horse"][0]["qualifier"]["hour_branch"],"亥")
  for hit in result["source_rule_matches"]["six_yi_striking_punishment"]:
   instrument=hit["computed_symbol_condition"].split("天盘六仪")[1][0]
   self.assertEqual(hit["palace"],SIX_YI[instrument])
  for hit in result["source_rule_matches"]["sanqi_tomb"]:
   symbol=hit["computed_symbol_condition"].split("天盘")[1][0]
   self.assertEqual(hit["palace"],TRI_TOMB[symbol])
  self.assertEqual(len(result["source_rule_matches"]["heaven_earth_stem_paired"])>=7,True)
  self.assertTrue(all("book_source_sha256" in hit for hit in result["source_rule_matches"]["heaven_earth_stem_paired"]))
 def test_weekday_chart_does_not_turn_element_relation_to_medical_fact(self):
  chart=layout_from_explicit_bureau(dun="yang",ju=5,hour_ganzhi="辛亥")
  clock=solar_chart_clock("1998-06-04T21:30:00+08:00","Asia/Shanghai")
  result=compute_author_combinations(chart,clock)
  self.assertTrue(result["traditional_symbolic_conditions_only"])
  self.assertTrue(all(x["cannot_determine_real_world_personality_or_health"] for x in
    result["source_rule_matches"]["six_yi_striking_punishment"]))
  self.assertTrue(all(x["rule_claim_not_automatically_fatal"] for x in
    result["source_rule_matches"]["heaven_earth_stem_paired"]))
if __name__=="__main__":unittest.main()
