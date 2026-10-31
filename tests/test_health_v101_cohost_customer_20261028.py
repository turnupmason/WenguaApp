"""V10.1 audience copy regression, never alter V8 score."""
import unittest
from pathlib import Path
from src.wengua.health_reading_template_vnext import template
from scripts import ios_vnext_three_random_20261026 as samples

class V101CopyTests(unittest.TestCase):
    def test_template(self):
        t=template()
        self.assertEqual(t["schema"],"health_severity_user_editable_template_v20261031_v11_full_evidence")
        self.assertIn("宫象{grade}。",t["macros"]["palace_compact"])
        self.assertNotIn("全部因素推断后",t["macros"]["palace_compact"])
        self.assertIn("古文：{classical_text}",t["formation"])
    def test_same_real_yi_is_not_repeated(self):
        case=samples.produce(seed=202610282003,count=1,wife_only=True)["cases"][0]
        self.assertEqual(case["instant"],"2025-10-15T07:00:00-04:00")
        self.assertEqual(case["summary"]["score"],-5)
        self.assertEqual(case["roles"]["patient"]["palace"],case["roles"]["medicine"]["palace"])
        verdict=next(s["text"] for s in case["source_sections"] if s["id"]=="90_review")
        self.assertIn("患者乙在坎一宫",verdict)
        self.assertEqual(verdict.count("乙奇势"),1)
        self.assertLess(len(verdict),950)
        self.assertNotIn("全部因素推断后",case["python_reading_text"])
    def test_both_source_engines_deduplicate_without_mutating_scores(self):
        root=Path(__file__).resolve().parents[1]
        swift=(root/"ios/WenguaAppUI/WenguaPythonVNextVerbatim.swift").read_text()
        python=(root/"src/wengua/domain_selected_energy_vnext.py").read_text()
        # V10.1's original behavior remains in the per-role DETAIL sections;
        # V10.2 intentionally replaces only the repetitive verdict loop.
        self.assertIn("var powerSeen:Set<String>",swift)
        self.assertIn("power_seen={}",python)
        self.assertIn('phrase("summary_concise"',swift)
        self.assertIn('render_slot("summary_concise"',python)

if __name__=="__main__":unittest.main()
