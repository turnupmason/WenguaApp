"""V3.4 user explicit spouse/animal/son-in-law, real chart, 42+17 audited sources."""
from __future__ import annotations
import hashlib, unittest
from src.wengua.casting_shenqi import layout_from_explicit_bureau
from src.wengua.health_dynamic_v21 import bind_patient
from scripts.replay_all_historical_health_v34 import evaluate, CASES, PARENT, PARENT_SHA
from src.wengua.health_severity_v34 import analyze_health_severity_v34, _pair_catalog, _composite_catalog, CATALOG

class HealthV34AllRules(unittest.TestCase):
    def test_exact_parent_and_preserve_twelve_unique_families(self):
        self.assertEqual(hashlib.sha256(PARENT.read_bytes()).hexdigest(),PARENT_SHA)
        self.assertEqual(len(CASES),12)
        self.assertEqual(len({z["id"] for z in CASES}),12)
        r=evaluate()
        self.assertEqual(len(r["samples"]),12)
        self.assertEqual(sum(r["counts"].values()),12)
        self.assertGreater(r["counts"]["rendered"],8,"New role router must unlock previously blocked source patient relationships")
        for x in r["samples"]:
            self.assertFalse(x["author_answer_used"])
            self.assertFalse(x["later_feedback_used"])
    def test_spouse_harmony_plus_yi_not_questioner_day(self):
        chart=layout_from_explicit_bureau(dun="yang",ju=7,hour_ganzhi="癸亥")
        cal={"year_ganzhi":"丁丑","month_ganzhi":"壬子","day_ganzhi":"癸卯","hour_ganzhi":"癸亥"}
        q={"intent":"severity","relationship":"spouse","consultation_context":"direct_proxy","patient_sex":"female"}
        s=bind_patient(chart,q,cal)
        self.assertEqual(s["stem"],"乙")
        self.assertEqual(s["harmony_stem"],"戊")
        self.assertIsNotNone(s["main_cell"])
        self.assertIsNotNone(s["harmony_palace"])
        with self.assertRaisesRegex(ValueError,"性别"):
            bind_patient(chart,{**q,"patient_sex":None},cal)
    def test_husband_geng_and_day_combine_never_wife_yi(self):
        chart=layout_from_explicit_bureau(dun="yang",ju=7,hour_ganzhi="癸亥")
        cal={"day_ganzhi":"癸卯","hour_ganzhi":"癸亥"}
        x=bind_patient(chart,{"relationship":"husband","consultation_context":"direct_proxy"},cal)
        self.assertEqual(x["stem"],"庚")
        self.assertEqual(x["harmony_stem"],"戊")
    def test_animal_and_son_in_law_actual_hour(self):
        for dun,ju,hour,relation in [
          ("yang",6,"己巳","animal_hen"),("yang",3,"戊辰","animal_rooster"),
          ("yang",6,"乙亥","son_in_law")]:
            chart=layout_from_explicit_bureau(dun=dun,ju=ju,hour_ganzhi=hour)
            q={"relationship":relation,"consultation_context":"direct_proxy"}
            r=bind_patient(chart,q,{"hour_ganzhi":hour})
            self.assertEqual(r["stem"],hour[0])
            self.assertIsNotNone(r["main_cell"])
    def test_all_42_ordered_pairs_and_17_composites_each_state_reported(self):
        out=evaluate()
        for s in out["samples"]:
            if s["result"]!="rendered":continue
            self.assertEqual(len(s["ordered_pairs"]),42)
            self.assertEqual(len(s["composites"]),17)
            self.assertEqual(len({r["id"] for r in s["ordered_pairs"]}),42)
            self.assertEqual(len({r["id"] for r in s["composites"]}),17)
            self.assertTrue(all(r["state"]!="triggered" or r["matched"] for r in s["ordered_pairs"]))
            self.assertTrue(all(r["state"]!="triggered" or r["evidence"] or int(r["id"][-2:]) in (1,2,3,4,5) for r in s["composites"]))
            self.assertEqual(hashlib.sha256(s["reading"].encode()).hexdigest(),s["sha256"])
    def test_double_control_relation_requires_distinct_two_controls(self):
        # Metal patient -> wood illness palace -> earth Tianrui star.
        from src.wengua.marriage_runtime import element_relation
        self.assertEqual(element_relation("金","木"),"克")
        self.assertEqual(element_relation("木","土"),"克")
        self.assertNotEqual(element_relation("木","土"),"生")
    def test_medical_copalace_opportunity_survives_weak_doctor_month(self):
        # Source's two independent triggers are reported in the audit and
        # cannot be vetoed simply because Tianxin/Yi are weak or empty.
        out=evaluate()
        found=[x for x in out["samples"] if x["result"]=="rendered" and
               x["medicine_copalace"]["independent_opportunities"] and
               x["medicine_copalace"]["weaknesses_kept"]]
        self.assertTrue(found,"Need real chart showing both co-palace and weak/obstructed doctor")
        for sample in found:
            self.assertTrue(sample["medicine_copalace"]["no_strength_veto_on_co_palace"])
            self.assertIn("及时获得医治",sample["reading"])
    def test_prior_v31_two_unchanged(self):
        import json
        old=json.loads((PARENT.parent.parent.parent/"data/evaluation/health_v33/all_historical_health_V31_READOUTS_SEALED.json").read_text("utf8"))
        self.assertEqual(sum(z["status"]=="rendered_v31" for z in old["records"]),8)

if __name__=="__main__":
    unittest.main()
