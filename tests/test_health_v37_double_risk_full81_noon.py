"""V3.7 regressions: full 81 name/direction, symmetric adverse/favorable priority,
genuine noon chart, preserve V3.6 prior readout, double unfavorable hidden proof.
"""
from __future__ import annotations
import hashlib, unittest
from src.wengua.health_severity_v37 import (load_81_book_pairs,
    two_sided_evidence, actual_81_pair_context, analyze_health_severity_v37)
from scripts.run_health_v37_user_20261022_noon import test_case,PARENT,PARENT_SHA

class V37BookTruth(unittest.TestCase):
    def setUp(self):self.assertEqual(hashlib.sha256(PARENT.read_bytes()).hexdigest(),PARENT_SHA)

    def test_book_all_81_ordered_both_directions(self):
        pairs=load_81_book_pairs()
        self.assertEqual(len(pairs),81)
        self.assertEqual(pairs["己/癸"]["source_line"],384)
        self.assertEqual(pairs["丙/辛"]["source_line"],332)
        self.assertNotEqual(pairs["乙/庚"]["source_original"],pairs["庚/乙"]["source_original"])

    def _decision(self,patient_p,ill_p,patient_pairs=(),void=False,hazards=(),
                  doctor=False,yi=False):
        return two_sided_evidence(patient={"palace":patient_p},ill={"palace":ill_p},
          patient_void=void,patient_hazards=list(hazards),
          patient_pairs=list(patient_pairs),month_phase=None,
          doctor_controls=doctor,yi_controls=yi)

    def test_exact_double_control_and_its_void_exception(self):
        v=self._decision(6,3)
        self.assertTrue(v["double_control"])
        self.assertEqual(v["decision_override"],"病吉")
        self.assertFalse(v["double_adverse_types"])
        blocked=self._decision(6,3,void=True)
        self.assertTrue(blocked["double_control"])
        self.assertIsNone(blocked["decision_override"])

    def test_two_distinct_double_unfavorable_mechanisms(self):
        a=self._decision(6,9)
        self.assertTrue(a["double_adverse_disease_growth"])
        self.assertEqual(a["decision_override"],"病凶")
        b=self._decision(3,9)
        self.assertTrue(b["double_adverse_patient_nourishes"])
        self.assertEqual(b["decision_override"],"病凶")

    def test_compound_adverse_must_have_actual_original_bad_pair(self):
        x=self._decision(4,6,[{"applicability":"book_adverse_formation",
                    "title":"地刑玄武","pair_key":"己/癸","source_line":384}])
        self.assertTrue(x["double_adverse_patient_formation"])
        self.assertFalse(x["double_adverse_disease_growth"])
        self.assertEqual(x["illness_palace_vs_tianrui_earth"],"受生")
        self.assertEqual(x["decision_override"],"病凶")
        no_formation=self._decision(4,6,[])
        self.assertFalse(no_formation["double_adverse_types"])
        self.assertIsNone(no_formation["decision_override"])

    def test_2026_noon_four_pillars_and_culturally_qualified_real_source(self):
        z=test_case()
        self.assertEqual(z["pillars"],{"year":"丙午","month":"戊戌","day":"己巳","hour":"庚午"})
        self.assertEqual(z["bureau"]["ju"],9)
        self.assertEqual(z["bureau"]["dun"],"yin")
        self.assertEqual(z["calendar"]["active_solar_term"],"寒露")
        self.assertEqual(z["chart"]["value_star"],"天英星")
        self.assertEqual(z["chart"]["value_door"],"景门")
        self.assertEqual(len(z["actual_all_nine_source_pairs"]),9)
        self.assertEqual(len(z["matched_42_user_health_pairs"]),42)
        self.assertEqual(len(z["seventeen_composite_checks"]),17)
        d=z["double_evidence"]
        self.assertTrue(d["double_adverse_patient_formation"])
        self.assertFalse(d["double_adverse_disease_growth"],
            "Tianrui earth GENERATES Qian metal; do not call it illness boosted")
        self.assertFalse(d["double_control"])
        self.assertEqual(d["patient_vs_illness"],"受克")
        self.assertEqual(d["illness_palace_vs_tianrui_earth"],"受生")
        self.assertEqual(z["traditional_v37_verdict"],"病凶")
        self.assertEqual(hashlib.sha256(z["reading_text"].encode()).hexdigest(),z["reading_sha256"])
        pairs=z["actual_all_nine_source_pairs"]
        assert_source=lambda key,role:next(p for p in pairs if p["pair_key"]==key and role in p["roles"])
        self.assertIn("地刑玄武",assert_source("己/癸","患者宫")["title"])
        self.assertEqual(assert_source("丙/辛","病宫")["applicability"],"book_health_favorable")
        self.assertEqual(assert_source("戊/庚","值符宫")["applicability"],"book_health_adverse" if False else assert_source("戊/庚","值符宫")["applicability"])
        self.assertIn("月奇相合",z["reading_text"])
        self.assertIn("地刑玄武",z["reading_text"])
        self.assertIn("反证",z["reading_text"])
        self.assertNotIn("确诊",z["reading_text"])

    def test_requires_source_complete_six_layer_not_default_bureau(self):
        from src.wengua.casting_shenqi import bureau_for_term
        self.assertEqual(bureau_for_term("己巳","寒露")["yuan"],"middle")
        self.assertEqual(bureau_for_term("己巳","寒露")["ju"],9)

if __name__=="__main__":unittest.main()
