"""Independent V-next disease evidence logic acceptance; DO NOT tune to outcomes.

Pins old 4 V3.9.1 SHA facts, plus separately tests new conditional review
logic, no forced binary decision, source polarity gated, no evidence doubles.
"""
from __future__ import annotations
import hashlib
import json
import unittest
from pathlib import Path

from src.wengua.health_text_pipeline import auto_cast_health_v39_text
from src.wengua.health_text_pipeline_vnext_review import auto_cast_health_review_text
from src.wengua.health_severity_vnext_review import (
    review_ordered_pairs,decide_review,dedup_lifecycle_facts,
)

ROOT=Path(__file__).resolve().parents[1]
SAMPLE=ROOT/"data/evaluation/health_v391/four_fixed_random_real_hour_charts_SOURCE_AUDIT.json"
SELF={"intent":"severity","relationship":"self","consultation_context":"direct_self"}


class PureDecisionTests(unittest.TestCase):
    def base(self,**kwargs):
        options={
            "role_confidence":"source_case_specific",
            "patient_void":False,"patient_hazards":[],
            "patient_to_illness":"克","illness_to_star":"克",
            "medicine_controls":False,
            "eligible_bad_patient_pair":False,
            "unverified_bad_patient_pair":False,
        }
        options.update(kwargs)
        return decide_review(**options)

    def test_double_control_only_if_patient_is_unblocked(self):
        self.assertEqual(self.base()["state"],"favorable")
        self.assertEqual(self.base(patient_void=True)["state"],"conflicted")
        self.assertEqual(self.base(patient_hazards=["六仪击刑"])["state"],"conflicted")

    def test_true_double_adverse_and_medicine_conflict(self):
        a=self.base(patient_to_illness="受克",illness_to_star="比和")
        self.assertEqual(a["state"],"adverse")
        self.assertEqual(self.base(patient_to_illness="受克",
                     illness_to_star="比和",medicine_controls=True)["state"],"conflicted")

    def test_unproved_book_bad_cannot_force_original_binary(self):
        state=self.base(patient_to_illness="受克",illness_to_star="受生",
                        unverified_bad_patient_pair=True)
        self.assertEqual(state["state"],"unresolved")
        self.assertIsNone(state["decisive_chain"])

    def test_conditional_person_role_and_no_chain_must_abstain(self):
        self.assertEqual(self.base(role_confidence="research_candidate_only")["state"],"unresolved")
        self.assertEqual(self.base(patient_to_illness="比和",
                                   illness_to_star="比和")["state"],"unresolved")

    def test_source_phrase_not_a_verified_book_predicate(self):
        raw=[{"palace":6,"star":"天芮星","top":"丙","bottom":"戊",
              "roles":["病宫","值符宫"],"title":"飞鸟跌穴",
              "applicability":"book_health_adverse",
              "source_conditions":{"如果":False,"门迫":False,"但":False},
              "source_line":258,"source_sha256":"a"*64,
              "user_health_supplement":"health_supplement_pair_02"}]
        out=review_ordered_pairs(raw,{"illness_duration":"new"})
        self.assertEqual(len(out),1)
        self.assertEqual(out[0]["source_state"],"health_phrase_needs_full_gate")
        self.assertEqual(out[0]["roles"],["病宫","值符宫"])
        self.assertEqual(out[0]["supplement_id_internal"],"health_supplement_pair_02")

    def test_overlapping_roles_share_one_real_lifecycle_fact(self):
        common={"stem":"丙","palace":6,"actual_stage_facts":[
                {"branch":"戌","stage":"墓"},{"branch":"亥","stage":"绝"}]}
        evidence={k:common for k in ("patient","illness_tianrui_heaven",
                   "doctor_tianxin_heaven","medicine_yi","hour_event")}
        facts=dedup_lifecycle_facts(evidence)
        self.assertEqual(len(facts),2)
        self.assertEqual({z["stage"] for z in facts},{"墓","绝"})
        self.assertEqual(len(facts[0]["roles"]),5)


class FullRealChartPreview(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.frozen=json.loads(SAMPLE.read_text("utf8"))["samples"]
        cls.results=[]
        for row in cls.frozen:
            arguments={"iso":row["local_datetime"],"timezone_name":row["timezone"],
                       "inquiry":dict(SELF)}
            old=auto_cast_health_v39_text(**arguments)
            review=auto_cast_health_review_text(**arguments)
            cls.results.append((row,old,review))

    def test_old_frozen_v391_text_byte_identical_after_new_branch_added(self):
        self.assertEqual(len(self.results),4)
        for row,old,review in self.results:
            self.assertEqual(old["reading_text"],row["v391_customer_reading_text"])
            self.assertEqual(hashlib.sha256(old["reading_text"].encode()).hexdigest(),
                             row["v391_customer_reading_sha256"])
            self.assertEqual(old["score"],None)
            self.assertEqual(review["audit"]["legacy_v391_reading_text"],old["reading_text"])

    def test_new_readings_complete_and_no_scores_or_unverified_claims(self):
        for row,old,review in self.results:
            self.assertEqual(review["four_pillars"],row["four_pillars"])
            self.assertEqual(len(review["sections"]),6)
            self.assertEqual(review["sections"][0]["title"],"主判断")
            self.assertEqual(review["sections"][1]["title"],"患者与疾病主证")
            self.assertTrue(review["verdict"]["state"] in
                            {"favorable","adverse","conflicted","unresolved"})
            self.assertEqual(review["audit"]["matched_real_star_pairs"],9)
            self.assertEqual(review["audit"]["book_81_catalog_size"],81)
            self.assertEqual(review["audit"]["supplement_rules_preserved"],42)
            self.assertEqual(review["audit"]["composites_preserved"],17)
            self.assertTrue(review["no_scoring"])
            self.assertFalse(review["medical_validity_claimed"])
            self.assertNotIn("健康指数",review["reading_text"])
            self.assertNotIn("吉凶概率",review["reading_text"])
            self.assertNotIn("原书第",review["reading_text"])
            self.assertNotIn("数据库",review["reading_text"])
            keys=[t["fact_id"] for t in review["audit"]["actual_stage_facts_unique"]]
            self.assertEqual(len(keys),len(set(keys)))

    def test_different_logic_is_preview_only_not_clinically_validated(self):
        for row,old,review in self.results:
            self.assertEqual(review["status"],"review_not_public")
            self.assertEqual(review["audit"]["actual_original_author_outcomes_not_used"],True)
        print("\n=== Four independent source-calculated review examples (not blind outcomes) ===")
        for n,(row,old,review) in enumerate(self.results,1):
            print("CASE",n,row["local_datetime"])
            print("BASELINE",old["reading_text"].split("最后断词：")[-1][:250].strip())
            print("REVIEW",review["sections"][0]["text"])
            print("GATES",review["audit"]["missing_source_predicates"],
                  "LIFECYCLE_UNIQUE",len(review["audit"]["actual_stage_facts_unique"]))


if __name__=="__main__":
    unittest.main()
