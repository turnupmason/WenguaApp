"""V13 region/duration/carrier/door research across actual 1080 clock layouts."""
import json
import unittest
from pathlib import Path

from src.wengua.core import cycle60
from src.wengua.casting_shenqi import layout_from_explicit_bureau
from src.wengua.health_discomfort_detail_v13_draft import detail_policy,inspect_detail
from src.wengua.health_discomfort_location_draft import load_traditional_location_candidates
from src.wengua.health_discomfort_template_v11_draft import compose_draft

ROOT=Path(__file__).resolve().parents[1]
INQUIRY={"intent":"discomfort","relationship":"friend","consultation_context":"direct_proxy"}
CAL={"year_ganzhi":"庚午","month_ganzhi":"己丑","day_ganzhi":"辛卯"}


class HealthSiteDetailsV13(unittest.TestCase):
    def test_all_eight_physical_regions_plus_symbolic_centre(self):
        data=detail_policy()
        mapping={}
        for name,group in data["body_axis"].items():
            for p in group["palaces"]:
                self.assertNotIn(p,mapping)
                mapping[p]=name
        self.assertEqual(mapping,{9:"upper",4:"upper",2:"upper",
                                  3:"middle",7:"middle",
                                  8:"lower",1:"lower",6:"lower"})
        self.assertEqual(data["body_axis"]["middle"]["symbolic_centre"],5)
        self.assertFalse(data["public_gate"]["ios_enabled"])
        self.assertFalse(data["public_gate"]["medical_diagnosis"])
        self.assertIsNone(data["source"]["book_id"])

    def test_actual_dual_carriers_are_independent_and_earth_is_gated(self):
        notes=load_traditional_location_candidates()
        saw_kun=False
        for dun in ("yang","yin"):
            for ju in range(1,10):
                for hour in cycle60():
                    c=layout_from_explicit_bureau(dun=dun,ju=ju,hour_ganzhi=hour)
                    r=compose_draft(chart=c,inquiry=INQUIRY,calendar=CAL)
                    e=r["audit"]["body_v13_detail"]
                    main=r["audit"]["location_priority"]
                    p=main["tianrui_palace"]
                    self.assertEqual(e["carriers"][0]["symbol"],
                                     main["actual_sky_stem"])
                    self.assertEqual(e["carriers"][1]["symbol"],
                                     main["companion_stem"])
                    self.assertEqual(e["carriers"][2]["symbol"],
                                     c["palaces"][str(p)]["earth_stem"])
                    self.assertFalse(e["carriers"][2]["conditional_eligible"])
                    self.assertEqual(e["symbolic_centre_only"],5)
                    self.assertFalse(e["illness_duration"]["new_or_old_determined"])
                    self.assertFalse(e["illness_duration"]["customer_phrase_allowed"])
                    self.assertEqual(e["illness_door_meaning"],
                                     notes["doors"][e["illness_door"]]["illness"])
                    self.assertEqual(e["patient_door_meaning"],
                                     notes["doors"][e["patient_door"]]["patient"])
                    self.assertIn(e["anatomical_region_zh"],r["sections"][0]["text"])
                    self.assertEqual(e["true_medical_diagnosis"],None)
                    self.assertNotIn("癌症",r["reading_text"])
                    self.assertNotIn("必死",r["reading_text"])
                    if p==2:
                        saw_kun=True
                        self.assertEqual(e["kun_centre_host_earth_stem"],
                                         c["palaces"]["5"]["earth_stem"])
                        self.assertEqual(len(r["audit"]["81_pairs"]),2)
                    else:
                        self.assertIsNone(e["kun_centre_host_earth_stem"])
        self.assertTrue(saw_kun)

    def test_illness_door_and_patient_door_are_not_interchanged(self):
        found=False
        for dun,ju,hour in (("yang",3,"丁巳"),("yin",8,"戊戌"),
                            ("yang",1,"甲子")):
            c=layout_from_explicit_bureau(dun=dun,ju=ju,hour_ganzhi=hour)
            r=compose_draft(chart=c,inquiry=INQUIRY,calendar=CAL)
            d=r["audit"]["body_v13_detail"]
            self.assertIn(d["illness_door"],r["sections"][1]["text"])
            self.assertIn(d["patient_door"],r["sections"][3]["text"])
            if d["illness_door"]!=d["patient_door"]:
                found=True
                self.assertNotEqual(d["illness_door_meaning"],
                                    d["patient_door_meaning"])
        self.assertTrue(found)

    def test_user_note_ocr_revisions_remain_unapproved(self):
        raw=detail_policy()["ocr_aliases"]
        self.assertTrue(any(x["raw"]=="王" and x["candidate"]=="壬"
                            for x in raw))
        self.assertTrue(all("review" in x["status"] or
                            x["status"].startswith("ambiguous") for x in raw))
        self.assertEqual(detail_policy()["disease_duration"]["inner"]["status"],
                         "unverified_user_generalization")

    def test_fabricated_centre_and_invalid_actual_patient_fail(self):
        c=layout_from_explicit_bureau(dun="yang",ju=3,hour_ganzhi="丁巳")
        r=compose_draft(chart=c,inquiry=INQUIRY,calendar=CAL)
        d=r["audit"]["location_priority"]
        with self.assertRaises(ValueError):
            inspect_detail(chart=c,illness_palace=5,
                           patient_cell=c["palaces"]["1"],
                           location=d)
        p=dict(c["palaces"]["7"])
        p["door"]="假的门"
        with self.assertRaises(ValueError):
            inspect_detail(chart=c,illness_palace=d["tianrui_palace"],
                           patient_cell=p,location=d)
        with self.assertRaises(ValueError):
            inspect_detail(chart=c,illness_palace=d["tianrui_palace"],
                           patient_cell=c["palaces"]["1"],
                           location=d,patient_sex="made_up")


if __name__=="__main__":
    unittest.main()
