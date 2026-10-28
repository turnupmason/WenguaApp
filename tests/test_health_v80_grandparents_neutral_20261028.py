"""Exact 2026-10-28 13:44 roles, no invented natal stems."""
import json, unittest
from pathlib import Path
from src.wengua.health_text_pipeline_vnext_review import auto_cast_health_review_text
ISO="2026-10-28T13:44:00-04:00"
class GrandparentV80(unittest.TestCase):
    def test_two_distinct_older_roles(self):
        path=Path(__file__).resolve().parents[1]/"data/knowledge/phrase_library/health_v20/actor_profiles.json"
        profiles={p["id"]:p for p in json.loads(path.read_text())["profiles"]}
        for role,palace in (("grandfather",6),("grandmother",2)):
            with self.subTest(role=role):
                self.assertEqual(profiles[role]["palaces"],[palace])
                self.assertIn("analogy_not_exact_case",profiles[role]["references"][0]["status"])
                out=auto_cast_health_review_text(
                    iso=ISO,timezone_name="America/New_York",
                    inquiry={"intent":"severity","relationship":role,
                             "consultation_context":"direct_proxy"})
                q=out["full_health_role_strength_network"]["candidate_five_grade_quantization"]
                self.assertEqual(q["summary"]["actual_role_strengths"]["patient"]["symbol"],
                                 out["four_pillars"]["year"][0])
                self.assertEqual(q["summary"]["actual_role_strengths"]["gender"]["palace"],palace)
                self.assertNotIn("natal",q["roles"])
                self.assertEqual(out["audit"]["role_confidence"],
                                 "conditional_older_generation_analogy_not_exact_case")
    def test_wrong_sex_denied(self):
        for relation,sex in (("grandfather","female"),("grandmother","male")):
            with self.subTest(relation=relation),self.assertRaises(ValueError):
                auto_cast_health_review_text(iso=ISO,timezone_name="America/New_York",
                    inquiry={"intent":"severity","relationship":relation,
                             "consultation_context":"direct_proxy","patient_sex":sex})
if __name__=="__main__": unittest.main()
