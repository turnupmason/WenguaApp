"""Source-linked inner/outer chart candidate regression, no clinical inference."""
import json
import unittest
from pathlib import Path
from src.wengua.casting_shenqi import layout_from_explicit_bureau
from src.wengua.core import cycle60
from src.wengua.health_discomfort_location_draft import inspect_traditional_body_clues
from src.wengua.health_discomfort_inner_outer_v12_draft import policy,classify,inspect_priority
from src.wengua.health_discomfort_template_v11_draft import compose_draft

ROOT=Path(__file__).resolve().parents[1]
CAL={"year_ganzhi":"庚午","month_ganzhi":"己丑","day_ganzhi":"辛卯"}
INQUIRY={"intent":"discomfort","relationship":"friend","consultation_context":"direct_proxy"}


class SourceLinkedBodySite(unittest.TestCase):
    def test_all_sixteen_yin_yang_palace_branches(self):
        source=policy()
        self.assertEqual(source["source"][0]["line"],85)
        self.assertEqual(source["source"][1]["line"],31)
        for dun,internal in (("yang",{1,8,3,4}),("yin",{9,2,7,6})):
            for palace in (1,2,3,4,6,7,8,9):
                branch=classify(dun=dun,palace=palace)
                self.assertEqual(branch["sector"]=="inner",palace in internal)
                inverse=classify(dun="yin" if dun=="yang" else "yang",palace=palace)
                self.assertNotEqual(branch["sector"],inverse["sector"])
        with self.assertRaises(ValueError):classify(dun="yang",palace=5)
        with self.assertRaises(ValueError):classify(dun="unknown",palace=2)

    def test_real_kun_two_is_outer_yang_and_inner_yin(self):
        examples={}
        for dun in ("yang","yin"):
            for ju in range(1,10):
                for hour in cycle60():
                    chart=layout_from_explicit_bureau(dun=dun,ju=ju,hour_ganzhi=hour)
                    source=inspect_traditional_body_clues(chart)
                    if source["tianrui_palace"]==2:
                        examples[dun]=(chart,source)
                        break
                if dun in examples:break
        self.assertEqual(set(examples),{"yang","yin"})
        for dun,expected in (("yang","outer"),("yin","inner")):
            chart,body=examples[dun]
            review=inspect_priority(chart=chart,body=body,patient_palace=6,
                        hour_palace=1,
                        injury_palace=body["injury_door_palace_for_secondary_review"])
            self.assertEqual(review["sector"],expected)
            self.assertEqual(review["focus_candidates"],
                body["surface_symbol_candidates"] if expected=="outer"
                else body["internal_symbol_candidates"])
            self.assertFalse(review["one_organ_confirmed"])
            self.assertIsNone(review["medical_diagnosis"])

    def test_full_1080_actual_charts_no_override(self):
        seen=set()
        conflicting=0
        for dun in ("yang","yin"):
            for ju in range(1,10):
                for hour in cycle60():
                    chart=layout_from_explicit_bureau(dun=dun,ju=ju,hour_ganzhi=hour)
                    report=compose_draft(chart=chart,inquiry=INQUIRY,calendar=CAL)
                    p=report["audit"]["location_priority"]
                    seen.add((dun,p["sector"],p["tianrui_palace"]))
                    self.assertTrue(report["audit"]["inner_outer_selected"])
                    self.assertEqual(report["audit"]["v80_severity_score"],None)
                    self.assertEqual(p["focus_candidates"],
                                     report["audit"]["selected_body_candidates"])
                    self.assertFalse(report["released"])
                    self.assertFalse(report["ios_enabled"])
                    self.assertNotIn("必愈",report["reading_text"])
                    self.assertNotIn("必死",report["reading_text"])
                    if p["counterevidence"]:
                        conflicting+=1
                        self.assertEqual(p["sector"],
                            classify(dun=dun,palace=p["tianrui_palace"])["sector"])
        self.assertEqual(len(seen),16)
        self.assertGreater(conflicting,0)

    def test_no_middle_palace_role_or_unverified_release(self):
        chart=layout_from_explicit_bureau(dun="yin",ju=8,hour_ganzhi="戊戌")
        source=inspect_traditional_body_clues(chart)
        with self.assertRaises(ValueError):
            inspect_priority(chart=chart,body=source,patient_palace=5,hour_palace=1,
                      injury_palace=source["injury_door_palace_for_secondary_review"])
        with self.assertRaises(ValueError):
            inspect_priority(chart={**chart,"dun":"bad"},body=source,
                      patient_palace=2,hour_palace=1,
                      injury_palace=source["injury_door_palace_for_secondary_review"])
        profile=json.loads((ROOT/"data/knowledge/health_discomfort/body_location_profile_20261029.json").read_text())
        self.assertFalse(profile["iOS_enabled"])
        self.assertIsNone(profile["approved_customer_template"])


if __name__=="__main__":
    unittest.main()
