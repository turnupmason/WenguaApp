"""81 source-pair candidate gate regressions; no clinical scores or invented risks."""
from __future__ import annotations
import hashlib,unittest
from src.wengua.health_symbolic_score_v41 import (all81_proposed,
    _author_disease_direction,_safe_proposal,calculate_health_symbolic_score_v41)
from src.wengua.health_severity_v37 import load_81_book_pairs
from scripts.run_health_v41_source_gated_3_cases import evaluate,PARENT,PARENT_SHA

class V41Book81Context(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.book=load_81_book_pairs()
        cls.cfg,cls.proposed=all81_proposed()
        cls.batch=evaluate()
    def test_exact_full_db_and_all81_real_ordered_stems(self):
        self.assertEqual(hashlib.sha256(PARENT.read_bytes()).hexdigest(),PARENT_SHA)
        self.assertEqual(len(self.book),81)
        self.assertEqual(len(self.proposed),81)
        self.assertNotEqual(self.proposed["戊/庚"],self.proposed["庚/戊"])
        self.assertEqual(self.proposed["己/癸"]["proposed_points"],-20)
        self.assertEqual(len(self.batch["records"]),3)
    def test_author_overrides_generic_good_in_disease_context(self):
        for k in ("戊/丙","丙/戊"):
            author=self.book[k]["source_original"]
            self.assertEqual(_author_disease_direction(author),"traditional_illness_adverse")
            p=self.proposed[k]
            self.assertEqual(p["proposed_points"],20)
            val,status=_safe_proposal(k,p,author,None)
            self.assertIsNone(val)
            self.assertEqual(status,"source_vs_user_positive_conflict")
    def test_book_bingxin_illness_exception_cannot_turn_chronic_negative(self):
        key="丙/辛"
        source=self.book[key]["source_original"]
        self.assertEqual(_author_disease_direction(source),"traditional_illness_favorable")
        u=self.proposed[key]
        self.assertEqual(_safe_proposal(key,u,source,None)[1],"requires_original_new_or_chronic")
        self.assertEqual(_safe_proposal(key,u,source,"new")[0],10)
        self.assertEqual(_safe_proposal(key,u,source,"chronic")[1],"source_vs_user_negative_conflict")
    def test_book_original_explicit_bad_not_reversed_in_illness_palace(self):
        for key in ("戊/庚","己/己","己/癸","癸/辛"):
            source=self.book[key]["source_original"]
            self.assertEqual(_author_disease_direction(source),"traditional_illness_adverse")
            val,_=_safe_proposal(key,self.proposed[key],source,None)
            self.assertLess(val,0)
            self.assertNotEqual(val,-self.proposed[key]["proposed_points"])
    def test_origin_42_supplements_are_separate_from_all81(self):
        for r in self.batch["records"]:
            s=r["score"]
            audit=s["book_pair_source_audit"]
            self.assertEqual(audit["source_81_total"],81)
            self.assertEqual(audit["supplement_42_total"],42)
            self.assertEqual(len(audit["matched_real_star_pairs"]),9)
            self.assertTrue(all(len(q["source_sha256_internal_only"])==64 for q in audit["matched_real_star_pairs"]))
            self.assertTrue(all(q["match_status"] for q in audit["matched_real_star_pairs"]))
            self.assertTrue(all(q["source_is_clinically_validated"] is False for q in audit["matched_real_star_pairs"]))
            self.assertIsNone(s["actual_medical_risk_probability"])
            self.assertFalse(s["real_health_or_treatment_outcome_predicted"])
            self.assertEqual(s["revised_raw_score"],s["baseline"]+sum(z["points"] for z in s["evidence_ledger"]))
            self.assertEqual(s["revised_display_score"],max(0,min(100,s["revised_raw_score"])))
    def test_2026_patient_ji_gui_actual_minus20_not_buggy_inversion(self):
        r=self.batch["records"][0]["score"]
        matching=[x for x in r["book_pair_source_audit"]["matched_real_star_pairs"]
                  if x["ordered_pair"]=="己/癸" and x["actual_role"]=="patient"]
        self.assertEqual(len(matching),1)
        self.assertEqual(matching[0]["applied_delta"],-20)
        self.assertEqual(matching[0]["source_book_name"],"地刑玄武")
        self.assertEqual(r["previous_v40_raw"],46)
        self.assertEqual(r["revised_raw_score"],34)
        self.assertEqual(len(r["removed_duplicate_interactions"]),1)
        self.assertEqual(r["removed_duplicate_interactions"][0]["points"],-8)
    def test_source_dependent_illegal_medical_claims_are_not_present(self):
        for r in self.batch["records"]:
            for x in r["score"]["book_pair_source_audit"]["matched_real_star_pairs"]:
                self.assertNotIn("virus",x["match_status"])
                self.assertNotIn("cancer",x["match_status"])
                self.assertFalse(x["source_is_clinically_validated"])
    def test_clinical_veto_prohibited_by_design(self):
        self.assertFalse(self.batch["user_approved"])
        for r in self.batch["records"]:
            self.assertNotIn("death_risk",r["score"])
            self.assertNotIn("health_probability",r["score"])
            self.assertFalse(r["original_post_event_result_used"])
if __name__=="__main__":unittest.main()
