"""V4 health symbolic score audit; no clinical prediction or calibrated odds."""
from __future__ import annotations
import hashlib,unittest
from scripts.run_health_v40_score_three_cases import evaluate,PARENT,PARENT_SHA
from src.wengua.health_symbolic_score_v40 import _tomb_and_horse
class V40HealthScoreCandidate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.batch=evaluate()
    def test_exact_parent_preserved_and_fixed_original_cases(self):
        self.assertEqual(hashlib.sha256(PARENT.read_bytes()).hexdigest(),PARENT_SHA)
        self.assertEqual(len(self.batch["records"]),3)
        self.assertEqual([x["family_id"] for x in self.batch["records"]],
          ["user_20261022_1200_EDT","kaiwu.health.19950219.brother_paralysis",
           "shenqi.health.19961102.on_site_health"])
    def test_score_is_not_probability_and_all_adjustments_auditable(self):
        for r in self.batch["records"]:
            s=r["score"]
            self.assertEqual(s["baseline"],100)
            self.assertFalse(s["score_is_probability"])
            self.assertFalse(s["medical_health_index"])
            self.assertFalse(s["clinical_accuracy_validated"])
            self.assertEqual(s["raw_score"],100+sum(x["points"] for x in s["ledger"]))
            self.assertEqual(s["display_score_0_100"],max(0,min(100,s["raw_score"])))
            self.assertEqual(len(s["ledger"]),len({x["id"] for x in s["ledger"]}))
            self.assertFalse(r["original_post_event_result_used"])
            self.assertTrue(len(s["unscored_unknowns"])>=1)
            self.assertEqual(sum(x["family"]=="interaction" for x in s["ledger"])<=1,True)
    def test_user_true_sky_illness_qian6_horse_kun2_not_opened(self):
        s=self.batch["records"][0]["score"]
        self.assertEqual(s["patient_palace"],4)
        self.assertEqual(s["illness_palace"],6)
        self.assertEqual(s["tomb_and_horse"]["horse_branch"],"申")
        self.assertEqual(s["tomb_and_horse"]["horse_palace"],2)
        ids={x["id"] for x in s["ledger"]}
        self.assertIn("illness_controls_patient",ids)
        self.assertNotIn("patient_exact_clash_opens_tomb_refund_fraction",ids)
        self.assertNotIn("patient_opposite_horse_opens_tomb_refund_fraction",ids)
    def test_user_horse_opposite_tomb_is_explicit_method_not_literal_branch_clash(self):
        # User-specified spatial horse opposite Qian6 -> Xun4, horse at 巳
        base={"hour_ganzhi":"乙亥"}
        cal={"year_ganzhi":"丙午","month_ganzhi":"戊戌",
             "day_ganzhi":"己巳"}
        d=_tomb_and_horse(base,{"palace":6},"丙",cal,"休")
        self.assertTrue(d["in_tomb_palace"])
        self.assertTrue(d["horse_spatial_opposite"])
        self.assertEqual(d["horse_branch"],"巳")
        self.assertEqual(d["opposite_palace"],4)
        self.assertFalse(d["direct_clash_in_pillars"])
        self.assertEqual(d["opening_mode"],"opposite_horse_palace_user_method")
        # Explicit 辰 branch clashes 戌, a DIFFERENT test from spatial horse.
        cal2={**cal,"month_ganzhi":"戊辰"}
        e=_tomb_and_horse(base,{"palace":6},"丙",cal2,"休")
        self.assertTrue(e["direct_clash_in_pillars"])
        self.assertEqual(e["opening_mode"],"exact_branch_clash_candidate")
    def test_tomb_never_awarded_when_not_present(self):
        d=_tomb_and_horse({"hour_ganzhi":"乙亥"},{"palace":3},"丙",
                          {"month_ganzhi":"戊辰"},"休")
        self.assertFalse(d["in_tomb_palace"])
        self.assertEqual(d["opening_mode"],"not_in_tomb")
    def test_known_male_aux_not_faked_for_self_without_sex(self):
        self.assertIsNone(self.batch["records"][0]["score"]["male_female_aux_reference"])
        self.assertEqual(self.batch["records"][1]["score"]["male_female_aux_reference"],"male")
    def test_missing_new_chronic_not_silently_used(self):
        for r in self.batch["records"]:
            ids={x["id"] for x in r["score"]["ledger"]}
            self.assertNotIn("patient_void_new",ids)
            self.assertNotIn("patient_void_chronic",ids)
            self.assertNotIn("star_door_fanyin_new",ids)
            self.assertNotIn("star_door_fanyin_chronic",ids)
            self.assertNotIn("star_door_fuyin_chronic",ids)
if __name__=="__main__":unittest.main()
