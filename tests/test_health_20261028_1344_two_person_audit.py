"""One-clock, two-person source audit for the user-shown Oct 28 chart.

The test is deliberately read-only. Matching zeroes alone are not proof of
a bug, but an unverified patient binding must not be represented as a firm
traditional verdict. Any recurrence retains its exact score ledger.
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
            }
        print("TWO_PERSON_SAME_CLOCK_AUDIT="+json.dumps(
            results,ensure_ascii=False,sort_keys=True),flush=True)
        self.assertEqual(results["self"]["four_pillars"],
                         results["colleague"]["four_pillars"])
        # Day and month are distinct real carriers on this exact local time.
        self.assertEqual(
            results["self"]["patient_symbol"],
            results["self"]["four_pillars"]["day"][0])
        self.assertEqual(
            results["colleague"]["patient_symbol"],
            results["colleague"]["four_pillars"]["month"][0])
        self.assertEqual(results["self"]["four_pillars"]["hour"],"癸未")
        self.assertEqual(results["self"]["bureau"]["ju"],2)

if __name__=="__main__":
    unittest.main()
