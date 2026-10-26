"""Latest user-confirmed score contract, Tianrui-only, value protection.

The score is a traditional-symbolic research classification only. It is
NEVER a clinical illness grade or mortality/medical advice.
"""
import unittest
from src.wengua.health_intrinsic_scoring_vnext import (
    stem_intrinsic_score,resolve_ordered_pair)
from src.wengua.health_five_level_quant_vnext import (
    saturate,palace_tally,multi_palace_tally)
from src.wengua.health_text_pipeline_vnext_review import auto_cast_health_review_text

INQUIRY={"intent":"severity","relationship":"self",
         "consultation_context":"direct_self"}
DATE="2025-10-21T03:00:00-04:00"
ZONE="America/New_York"


class UserSignedFinalScore(unittest.TestCase):
    def test_nine_visible_stems_and_all_six_hidden_jia(self):
        expected={"乙":3,"丙":3,"丁":3,"戊":0,"己":0,
                  "庚":-3,"辛":0,"壬":0,"癸":0}
        for stem,score in expected.items():
            with self.subTest(stem=stem):
                self.assertEqual(stem_intrinsic_score(stem)["baseline"],score)
        for head in ("甲子","甲戌","甲申","甲午","甲辰","甲寅"):
            v=stem_intrinsic_score("甲",xun_shou=head)
            self.assertEqual(v["baseline"],-3 if head=="甲申" else 0)
            self.assertEqual(v["hidden_in"],"庚" if head=="甲申" else None)
        self.assertIsNone(stem_intrinsic_score("甲")["baseline"])

    def test_yy_is_health_minus_three_with_original_context_preserved(self):
        result=resolve_ordered_pair("乙","乙",illness_domain=True)
        self.assertEqual((result["polarity"],result["baseline"]),("凶",-3))
        self.assertEqual(result["status"],"user_health_explicit_jiayi_override")
        self.assertTrue(result["historical_text_remains_conditional"])
        nonhealth=resolve_ordered_pair("乙","乙",illness_domain=False)
        self.assertNotEqual(nonhealth["status"],result["status"])

    def test_saturation_keeps_true_raw_signed_total(self):
        illness=palace_tally(factors={
            "star":-4,"door":-5,"deity":-3,"pattern":-5})
        doctor=palace_tally(factors={
            "star":1,"door":4,"deity":4,"pattern":4})
        self.assertEqual((illness["raw_sum"],illness["score"],illness["grade"]),
                         (-17,-5,"极大凶"))
        self.assertEqual((doctor["raw_sum"],doctor["score"],doctor["grade"]),
                         (13,5,"极大吉"))
        self.assertEqual(saturate(-13),-5)
        self.assertEqual(saturate(8),5)
        # If the medicine has +7 *before* its 乙乙 -3, it is +4 after.
        # The four named raw contributions sum to -5, NOT -13.
        raw=-17+13+(7-3)-5
        self.assertEqual(raw,-5)
        net=multi_palace_tally(palaces={
            "illness":{"palace":2,"raw_sum":-17,"score":-5},
            "doctor":{"palace":6,"raw_sum":13,"score":5},
            "medicine":{"palace":4,"raw_sum":4,"score":4},
            "patient":{"palace":7,"raw_sum":-5,"score":-5},
            "hour":{"palace":7,"raw_sum":-5,"score":-5}})
        self.assertEqual(net["raw_known_sum"],-5)
        # Current authoring now nets each REAL palace's adjusted five-tier
        # score, NOT raw signed component sums across all palaces.
        self.assertEqual(net["post_void_known_sum"],-1)
        self.assertEqual((net["score"],net["grade"]),(-1,"极小凶"))
        self.assertEqual(len(net["duplicate_physical_roles"]),1)

    def test_real_2025_chart_tianqin_fact_not_second_illness_star(self):
        out=auto_cast_health_review_text(
            iso=DATE,timezone_name=ZONE,inquiry=INQUIRY)
        net=out["full_health_role_strength_network"]
        illness=net["candidate_five_grade_quantization"]["roles"]["illness"]
        audit=net["complete_selected_palace_audits"]["illness"]
        self.assertIn("天芮星",[x["name"] for x in audit["stars"]])
        self.assertEqual(len([x for x in illness["star"]["per_star"]
                              if x.get("score") is not None]),1)
        self.assertEqual(illness["star"]["per_star"][0]["symbol"],"天芮星")
        self.assertTrue(illness["star"]["illness_tianrui_only"])
        self.assertTrue(illness["pattern"]["only_tianrui_carried_stem_if_illness"])
        real_top={x["carried_stem"] for x in audit["stars"]
                  if x["name"]=="天芮星"}
        self.assertTrue(real_top)
        self.assertTrue(all(
            x["key"].split("/")[0] in real_top
            for x in illness["pattern"]["matches"]))
        self.assertIn("chief",net["nodes"])
        self.assertIn("hour",net["nodes"])
        self.assertEqual(net["nodes"]["chief"]["palace"],next(
            int(p) for p,c in out["nine_palaces"].items()
            if c["deity"]=="值符"))
        self.assertIn("值符护持宫",out["reading_text"])
        self.assertIn("时干事体",out["reading_text"])
        self.assertIn("全部因素推断后，此宫为",out["reading_text"])

    def test_user_requires_both_real_qian_and_kun_auxiliary_palaces(self):
        for sex in ("male","female"):
            with self.subTest(sex=sex):
                r=auto_cast_health_review_text(
                    iso=DATE,timezone_name=ZONE,
                    inquiry={**INQUIRY,"patient_sex":sex})
                titles=[x["title"] for x in r["sections"]]
                self.assertFalse(any(x.startswith("乾坤辅助：") for x in titles))
                self.assertIn("乾宫辅助（男）" if sex=="male" else "坤宫辅助（女）",titles)
                self.assertNotIn("坤宫辅助（女）" if sex=="male" else "乾宫辅助（男）",titles)
                q=r["full_health_role_strength_network"][
                    "candidate_five_grade_quantization"]
                self.assertIn("qian",q["auxiliary_qian_kun"])
                self.assertIn("kun",q["auxiliary_qian_kun"])
        none=auto_cast_health_review_text(
            iso=DATE,timezone_name=ZONE,inquiry=INQUIRY)
        self.assertFalse(any(x["title"].startswith("乾坤辅助：") for x in none["sections"]))
        # Unprovided sex is not the same as guessing two patient identities.
        self.assertIsNone(none["full_health_role_strength_network"][
            "selected_gender_palace"])


if __name__=="__main__":
    unittest.main()
