"""Regression gate for the 12-event source-only V3.1 historical health replay."""
import hashlib, json, unittest
from unittest.mock import patch
from scripts.replay_all_historical_health_v31_v33 import evaluate, CASES, PARENT, PARENT_SHA, ROOT

class HealthAllFamiliesV33Test(unittest.TestCase):
    def test_exact_full_parent_and_complete_deduplicated_scope(self):
        self.assertEqual(hashlib.sha256(PARENT.read_bytes()).hexdigest(),PARENT_SHA)
        x=evaluate()
        self.assertEqual(x["source_scope"]["total_unique_events"],12)
        self.assertEqual(len(CASES),12)
        self.assertEqual(len({c["id"] for c in CASES}),12)
        self.assertEqual(len(x["records"]),12)
        self.assertEqual(x["counts"]["rendered_v31"]+x["counts"]["blocked"],12)
        self.assertFalse(x["selected_cases_have_author_feedback_as_input"])
    def test_blocked_roles_never_disguised_as_self(self):
        x={q["family_id"]:q for q in evaluate()["records"]}
        for family in ("kaiwu.health.19980616.hen_illness",
                       "kaiwu.health.19980621.rooster_illness",
                       "kaiwu.final.recovery",
                       "shenqi.health.19971227.spouse_travel_for_treatment"):
            self.assertEqual(x[family]["status"],"blocked_unverified_role_or_chart")
            self.assertNotIn("readout",x[family])
    def test_existing_two_real_histories_preserve_original_v31_wording(self):
        sealed=json.loads((ROOT/"data/evaluation/health_v32/two_new_source_families_V31_READOUTS_SEALED.json").read_text("utf8"))
        x={q["family_id"]:q for q in evaluate()["records"]}
        for old in sealed["samples"]:
            new=x[old["family_id"]]
            self.assertEqual(new["status"],"rendered_v31")
            self.assertEqual(new["readout"],old["text"])
            self.assertEqual(new["readout_sha256"],old["text_sha256"])
    def test_deterministic_offline_no_later_answers_as_input(self):
        with patch("socket.socket",side_effect=AssertionError("Offline only")):
            a=evaluate()
            b=evaluate()
        self.assertEqual(json.dumps(a,ensure_ascii=False,sort_keys=True),
                         json.dumps(b,ensure_ascii=False,sort_keys=True))
        self.assertGreaterEqual(a["counts"]["rendered_v31"],2)
        for row in a["records"]:
            self.assertFalse(row["author_judgment_loaded"])
            self.assertFalse(row["later_feedback_loaded"])
            if row["status"]=="rendered_v31":
                self.assertEqual(row["readout_sha256"],
                                 hashlib.sha256(row["readout"].encode("utf8")).hexdigest())
                self.assertTrue(row["sections"])
                self.assertEqual(row["traditional_verdict"] in ("病吉","病凶"),True)
                self.assertEqual(row["user_approval"],"pending")
    def test_all_non_severity_questions_labeled_as_proxy_not_official_intent(self):
        out=evaluate()
        for x in out["records"]:
            if x["source_question_intent"] in ("discharge","surgery","travel_for_treatment","recovery"):
                self.assertEqual(x["template_intent"],"severity")
                self.assertNotEqual(x["source_question_intent"],x["template_intent"])

if __name__=="__main__":
    unittest.main()
