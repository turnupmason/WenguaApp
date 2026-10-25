"""2026-10-24 user literal intrinsic good/bad and 81 pattern coverages."""
import unittest
from src.wengua.health_intrinsic_scoring_vnext import (
    STARS,DOORS,GODS,PAIR_ROWS,catalog_validation,
    star_score,door_score,god_score,resolve_ordered_pair)
from src.wengua.health_five_level_quant_vnext import palace_tally
from src.wengua.health_text_pipeline_vnext_review import auto_cast_health_review_text
from src.wengua.health_quant_overlay_vnext import render_palace_signed_score


class LiteralPolarityTests(unittest.TestCase):
    def test_nine_stars_exact_default(self):
        self.assertEqual(STARS,{
            "天辅星":4,"天禽星":4,"天心星":4,
            "天冲星":3,"天任星":3,"天英星":-1,
            "天蓬星":-4,"天芮星":-4,"天柱星":-2})
        for name,base in STARS.items():
            x=star_score(name,"中等")
            self.assertEqual(x["baseline"],base)
            self.assertEqual(x["score"],3 if base>0 else -3)
        self.assertEqual(star_score("天心星","极大")["label"],"极大吉")
        self.assertEqual(star_score("天芮星","极大")["label"],"极大凶")
        self.assertIsNone(star_score("天芮星",None)["score"])

    def test_eight_doors_exact_baseline_and_neutral(self):
        self.assertEqual(DOORS,{
            "开门":3,"休门":3,"生门":3,
            "死门":-3,"惊门":-3,"伤门":-3,
            "杜门":0,"景门":0})
        for name,base in DOORS.items():
            score=door_score(name,"中等")
            self.assertEqual(score["baseline"],base)
            self.assertEqual(score["score"],(3 if base>0 else
                                             -3 if base<0 else 0))
        for x in ("杜门","景门"):
            self.assertEqual(door_score(x,"极大")["score"],0)
        x=palace_tally(factors={"star":3,"door":0,"deity":-3,"pattern":3})
        self.assertEqual((x["score"],x["grade"]),(3,"中等吉"))
        self.assertTrue(x["known_neutral_door"])

    def test_eight_gods_exact_month_free_five_relation(self):
        self.assertEqual(GODS,{
            "值符":3,"六合":3,"太阴":3,"九天":3,
            "白虎":-3,"玄武":-3,"螣蛇":-3,"九地":-3})
        relation={
            "符号生宫":3,"符号克宫":3,"比和":4,
            "宫克符号":2,"宫生符号":5}
        for name,base in GODS.items():
            for rel,magnitude in relation.items():
                x=god_score(name,rel)
                self.assertEqual(x["score"],magnitude if base>0 else -magnitude)
                self.assertEqual(x["baseline"],base)
                self.assertIsNone(x["month_stage"])
                self.assertEqual(x["status"],"calculated")
        self.assertEqual(god_score("腾蛇","宫生符号")["score"],-5)

    def test_ordered81_are_not_fabricated_missing_or_duplicate(self):
        c=catalog_validation()
        self.assertEqual(c["expected_pair_positions"],81)
        self.assertEqual(c["literal_supplied_rows"],78)
        self.assertEqual(c["distinct_declared_pairs"],77)
        self.assertEqual(set(c["missing_pair_keys"]),
                         {"乙/壬","乙/癸","丙/癸","戊/乙"})
        self.assertEqual(c["duplicate"][0]["key"],"庚/己")
        self.assertEqual(resolve_ordered_pair("庚","己")["status"],
                         "duplicate_user_pair_variants_pending")
        self.assertEqual(resolve_ordered_pair("戊","乙")["status"],
                         "user_pair_not_supplied")
        self.assertEqual(resolve_ordered_pair("乙","丁")["baseline"],3)
        self.assertEqual(resolve_ordered_pair("庚","癸")["baseline"],-3)
        self.assertEqual(resolve_ordered_pair(
            "戊","丙")["status"],"book_illness_conflict_pending")
        self.assertEqual(resolve_ordered_pair(
            "丙","辛")["status"],"book_illness_conflict_pending")
        self.assertEqual(resolve_ordered_pair(
            "癸","戊",door_name="杜门")["status"],
            "conditional_door_gate_pending")
        self.assertEqual(resolve_ordered_pair(
            "癸","戊",door_name="开门")["baseline"],3)
        self.assertEqual(resolve_ordered_pair(
            "丙","己",door_name="伤门")["baseline"],-3)

    def test_real_chart_all_selected_roles_have_auditable_current_scores(self):
        out=auto_cast_health_review_text(
            iso="2026-10-22T12:00:00-04:00",
            timezone_name="America/New_York",
            inquiry={"intent":"severity","relationship":"self",
                     "consultation_context":"direct_self"})
        net=out["full_health_role_strength_network"]
        q=net["candidate_five_grade_quantization"]
        for key in ("illness","doctor","medicine","patient","hour"):
            d=q["roles"][key]
            self.assertTrue(d["intrinsic_user_baselines_applied"])
            self.assertIsNotNone(d["door"]["score"])
            self.assertIsNotNone(d["deity"]["score"])
            self.assertTrue(d["star"]["per_star"])
            self.assertIn("神基准",render_palace_signed_score(d))
            self.assertIn("门基准",render_palace_signed_score(d))
        self.assertIn("宫内吉凶能量",out["reading_text"])
        self.assertIn("五级能量量化合断",out["reading_text"])
        self.assertTrue(q["not_a_medical_diagnosis"])


if __name__=="__main__":unittest.main()
