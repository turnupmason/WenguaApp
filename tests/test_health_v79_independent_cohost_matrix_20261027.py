"""V7.9 future-proof synthetic matrix + two preserved user-clock integrations.

The combinations are new artificial rule tests, NOT source-book cases or
hidden historical blind tests. They audit the actual production helpers.
"""
import itertools
import unittest
from scripts.ios_vnext_manual_colleague_natal_yi_20261027 import produce as colleague
from scripts.ios_vnext_manual_1920_female_20261027 import produce as elder
from src.wengua.health_quant_overlay_vnext import (
    independent_special_host, special_cohost_total,
    special_disease_control_points,
)
from src.wengua.health_five_level_quant_vnext import saturate


def actor(kind, symbol, role="hour"):
    return {"role": role, "kind": kind, "symbol": symbol}


class IndependentCohostMatrix(unittest.TestCase):
    def test_symbol_self_never_adds_once_or_under_different_role_alias(self):
        for kind, name in [
            ("stem", "乙"), ("stem", "丁"), ("star", "天心星"),
            ("deity", "值符")]:
            hosts = [actor(kind, name, role) for role in
                     ("hour", "natal", "patient")]
            self.assertFalse(independent_special_host(hosts, kind, name),
                             (kind, name))

    def test_independent_selected_host_any_role_or_any_order(self):
        for kind, symbol in [
            ("stem", "乙"), ("stem", "丁"),
            ("star", "天心星"), ("deity", "值符")]:
            for role in ("illness", "patient", "hour", "natal", "gender"):
                hosts = [actor(kind, symbol, "first"),
                         actor("stem", "戊", role)]
                for order in (hosts, list(reversed(hosts))):
                    self.assertTrue(
                        independent_special_host(order, kind, symbol),
                        (role, kind, symbol))
            self.assertFalse(independent_special_host([], kind, symbol))

    def test_one_family_per_palace_and_complete_void_half_once(self):
        for chief, stem, tianxin, void in itertools.product(
            (0, 2, 3), (0, 1, 2, 3), (0, 2, 3), (False, True)
        ):
            total=chief+stem+tianxin
            expected=total//2 if void else total
            self.assertEqual(special_cohost_total(
                chief, stem, tianxin_points=tianxin, void=void
            ), expected)
        # 时干戊临天心和值符 -> 两个独立标志同时加。
        self.assertEqual(special_cohost_total(3, 0, tianxin_points=3), 6)
        self.assertEqual(special_cohost_total(
            3, 0, tianxin_points=3, void=True), 3)
        # 时干戊临乙/丁一组、天心和值符：3+3+3, 空亡统一取整。
        self.assertEqual(special_cohost_total(
            3, 3, tianxin_points=3, void=True), 4)
        # 墓刑同时出现只一档，特殊符号家族只记+1。
        self.assertEqual(special_cohost_total(
            2, 1, tianxin_points=2, void=True), 2)

    def test_all_25_power_pairs_never_infer_strength_from_signed_grade(self):
        from src.wengua.user_domain_matrices_20261023 import inspect_control
        tiers=("极小","小","中等","大","极大")
        for a,b in itertools.product(tiers,repeat=2):
            source=inspect_control(actor_power=a,target_power=b,
                                   palace_relation="克")
            ability=("能" if source["result"] in {
                "有效克制","高效克制","强力主克","绝对主克",
                "极限压制","有效主克","完全清除"}
                else "艰难" if source["result"] in {
                    "微弱克制","减力克制","断续克制","效力递减"}
                else "不能")
            points=special_disease_control_points(
                attacker_strength=a,target_strength=b,
                control_status=source["status"],
                control_result=source["result"],control_ability=ability)
            self.assertEqual(points,3 if ability!="不能" else 0,
                             (a,b,source))
            for palace_grade in (-5,-3,0,3,5):
                self.assertEqual(
                    special_disease_control_points(
                        attacker_score=palace_grade,attacker_strength=a,
                        target_strength=b,control_status=source["status"],
                        control_result=source["result"],
                        control_ability=ability),
                    points,("the signed grade cannot affect control",a,b))
        self.assertEqual(special_disease_control_points(
            attacker_score=-5,attacker_strength=None,
            target_strength="中等",control_result="有效克制",
            control_status="matched",control_ability="能"),0)
        self.assertEqual(special_disease_control_points(
            attacker_score=5,attacker_strength="极大",
            target_strength=None,control_result="有效克制",
            control_status="matched",control_ability="能"),0)
        self.assertEqual(special_disease_control_points(
            attacker_strength="极大",target_strength="中等",
            control_result="有效克制",control_status="matched",
            control_ability="能",attacker_void=True),1)
        self.assertEqual(special_disease_control_points(
            attacker_strength="极大",target_strength="中等",
            control_result="有效克制",control_status="matched",
            control_ability="能",illness_void=True),5)

    @classmethod
    def setUpClass(cls):
        cls.clock_colleague=colleague()["cases"][0]
        cls.clock_elder=elder()["cases"][0]

    def test_both_real_clocks_account_for_actual_distinct_palaces(self):
        for case in (self.clock_colleague, self.clock_elder):
            s=case["summary"]
            self.assertEqual(
                s["final_scoring_policy"],
                "V8.0_SELECTED_SIGNIFIER_STRENGTH_ALL_INTERPALACE"
            )
            physical=s["unique_palace_score_details"]
            self.assertEqual(
                s["post_void_known_sum"],
                sum(p["score"] for p in physical.values()))
            self.assertEqual(len(physical),s["unique_palace_count"])
            for p in physical.values():
                self.assertTrue(p["heaven_stem_strength_applied_in_81_only"])
                self.assertTrue(all(x==0 for x in
                                    p["unique_stem_scores"].values()))
            for pid, record in s["auspice_cohost_audit"].items():
                self.assertTrue(record["self_signifier_excluded"])
                self.assertTrue(record["void_after_all_bonuses"])
                self.assertEqual(record["after_void"],
                    special_cohost_total(
                        record["chief"],record["stem_family"],
                        tianxin_points=record["tianxin"],
                        void=record["empty"]))
                self.assertTrue(record["hosts"])
            expected=s["post_void_known_sum"]+s["control_bonus_score"]+(
                s["weak_illness_drain_bonus_score"])+(
                s["auspice_applied_extra_score"])-s["five_not_global_penalty"]
            self.assertEqual(expected,s["raw_final_before_saturation"])
            self.assertEqual(s["score"],saturate(expected))

    def test_yearstem_yi_is_not_yi_own_auspice(self):
        s=self.clock_colleague["summary"]
        # Natal Yi has no other allowed host in the same palace.
        self.assertEqual(s["auspice_cohost_audit"]["3"]["stem_family"],0)
        self.assertEqual(s["auspice_cohost_audit"]["3"]["tianxin"],2)
        self.assertNotIn("7",s["auspice_cohost_audit"])
        self.assertEqual(s["auspice_bonus_score"],2)

    def test_distinct_illness_host_allows_one_yi_ding_family(self):
        s=self.clock_elder["summary"]
        # Illness Tianrui is a distinct selected symbol co-located with Yi.
        self.assertEqual(s["auspice_cohost_audit"]["9"]["stem_family"],3)
        self.assertEqual(s["auspice_cohost_audit"]["9"]["chief"],0)
        self.assertEqual(s["auspice_cohost_audit"]["2"]["chief"],3)
        self.assertEqual(s["auspice_bonus_score"],6)


if __name__=="__main__":
    unittest.main()
