"""One-clock, two-person source audit for the user-shown Oct 28 chart.

The test is deliberately read-only. Historical V8.0 before Tianqin
centre-earth hosting was 0 for both. The NEW explicitly authorized 81 source
pairing once changed both to +3; the later fixed Kun host returns both to 0.
Any recurrence retains its exact score ledger.
"""
import json
import unittest
from src.wengua.health_text_pipeline_vnext_review import auto_cast_health_review_text

ISO="2026-10-28T13:44:00-04:00"
ZONE="America/New_York"

class TwoPersonExactClockAudit(unittest.TestCase):
    def test_one_clock_self_vs_colleague_raw_ledger(self):
        results={}
        for person,relation,context in [
            ("self","self","direct_self"),
            ("colleague","colleague","direct_proxy")]:
            result=auto_cast_health_review_text(
                iso=ISO,timezone_name=ZONE,inquiry={
                    "intent":"severity","relationship":relation,
                    "consultation_context":context})
            network=result["full_health_role_strength_network"]
            quant=network["candidate_five_grade_quantization"]
            summary=quant["summary"]
            patient=quant["summary"]["actual_role_strengths"]["patient"]
            results[person]={
                "four_pillars":result["four_pillars"],
                "bureau":result["bureau"],
                "relationship":relation,
                "patient_symbol":patient["symbol"],
                "patient_palace":patient["palace"],
                "patient_role_confidence":result["audit"]["role_confidence"],
                "patient_role_via":result["audit"]["role_via"],
                "unique_palace_scores": {
                    role:{"palace":q["palace"],
                          "score":q["palace_score"]["score"],
                          "raw":q["palace_score"]["raw_sum"]}
                    for role,q in quant["roles"].items()},
                "physical_palaces":list(summary["unique_palace_score_details"]),
                "pre_relationship":summary["post_void_known_sum"],
                "control_bonus":summary["control_bonus_score"],
                "drain":summary["weak_illness_drain_bonus_score"],
                "auspice":summary["auspice_applied_extra_score"],
                "five_not_penalty":summary["five_not_global_penalty"],
                "raw_final":summary["raw_final_before_saturation"],
                "score":summary["score"],
                "grade":summary["grade"],
                "evidence_state":result["verdict"]["state"],
                "cohost_bonus_details":summary["auspice_bonus_details"],
            }
        print("TWO_PERSON_SAME_CLOCK_AUDIT="+json.dumps(
            results,ensure_ascii=False,sort_keys=True),flush=True)
        # Real physical chart invariant: ONLY the Tianrui illness palace
        # carries Tianrui+Tianqin and therefore TWO ordered 81 pairs.
        for relationship,context in [
            ("self","direct_self"),("colleague","direct_proxy")]:
            chart=auto_cast_health_review_text(
                iso=ISO,timezone_name=ZONE,inquiry={
                    "intent":"severity","relationship":relationship,
                    "consultation_context":context})
            ill_pid=chart["full_health_role_strength_network"][
                "candidate_five_grade_quantization"]["summary"][
                "actual_role_strengths"]["illness"]["palace"]
            for key,cell in chart["nine_palaces"].items():
                count=len(cell["heaven_stars"])
                if int(key)==5:
                    self.assertEqual(count,0)
                elif int(key)==ill_pid:
                    self.assertEqual(count,2)
                    self.assertEqual({x["star"] for x in cell["heaven_stars"]},
                                     {"天芮星","天禽星"})
                    self.assertEqual(len({x["carried_stem"] for x in cell["heaven_stars"]}),2)
                    star_carrier={x["star"]:x["carried_stem"] for x in cell["heaven_stars"]}
                    self.assertEqual(star_carrier["天禽星"],"丁")
                    self.assertNotIn("乙",star_carrier.values())
                else:
                    self.assertEqual(count,1,f"Non-illness palace {key} cannot gain a 2nd star")
        self.assertEqual(results["self"]["four_pillars"],
                         results["colleague"]["four_pillars"])
        # Three distinct USER-authorized versions on this seen clock:
        # original 0/0, Tianqin-following-centre 3/3, permanent Kun host 0/0.
        self.assertEqual(results["self"]["raw_final"],0)
        self.assertEqual(results["colleague"]["raw_final"],0)
        self.assertEqual(results["self"]["evidence_state"],"adverse")
        self.assertEqual(results["colleague"]["patient_role_confidence"],
                         "research_candidate_only")
        self.assertNotEqual(results["self"]["patient_palace"],
                            results["colleague"]["patient_palace"])
        self.assertEqual(set(results["self"]["physical_palaces"]),
                         set(results["colleague"]["physical_palaces"]))
        # Day and month are distinct real carriers on this exact local time.
        self.assertEqual(
            results["self"]["patient_symbol"],
            results["self"]["four_pillars"]["day"][0])
        self.assertEqual(
            results["colleague"]["patient_symbol"],
            results["colleague"]["four_pillars"]["month"][0])
        self.assertEqual(results["self"]["four_pillars"]["hour"],"癸未")
        self.assertEqual(results["self"]["bureau"]["ju"],2)

    def test_permanent_kun_host_zero_uses_neutral_copy(self):
        # Original 0, moving-centre-host 3, and permanent-Kun host 0 are
        # three explicit versions, never hidden tuning on a blind case.
        for relation,context in [
            ("self","direct_self"),("colleague","direct_proxy")]:
            output=auto_cast_health_review_text(
                iso=ISO,timezone_name=ZONE,inquiry={
                    "intent":"severity","relationship":relation,
                    "consultation_context":context})
            summary=output["full_health_role_strength_network"][
                "candidate_five_grade_quantization"]["summary"]
            self.assertEqual(summary["score"],0)
            self.assertEqual(summary["tianxian_global_final_bonus"],0)
            verdict=next(s["text"] for s in output["sections"]
                         if s["id"]=="90_review")
            self.assertIn("此病为不凶不吉",verdict)
            self.assertNotIn("暂不强断吉凶",verdict)

if __name__=="__main__":
    unittest.main()
