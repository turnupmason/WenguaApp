"""Only latest V8/V10.2 audience copy may ship; preserve historical Git facts."""
import json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; UI=ROOT/"ios/WenguaAppUI"
class LiveCopyCleanup(unittest.TestCase):
    def test_obsolete_customer_copy_never_compiled_or_bundled(self):
        premium=(UI/"WenguaPremiumReadingView.swift").read_text()
        router=(UI/"WenguaNativeReadingRouter.swift").read_text()
        board=(UI/"WenguaDesignPreviewApp.swift").read_text()
        template=json.loads((ROOT/"data/templates/health_severity_vnext/reading_template.json").read_text())
        self.assertNotIn("尚未定局",premium)
        self.assertIn('Text("结论依据待核")',premium)
        self.assertNotIn("专业合断尚未接通",router)
        self.assertNotIn("legacy_stage_one_factual_source_only",router)
        self.assertNotIn("V3.9",board)
        self.assertNotIn("当前原生端已核定时辰、九宫、人物宫",str(template))
        self.assertNotIn("待用户验收",str(template))
        for key in ("comment","conditional_rule_overlays_v72","summary_format_version",
                    "summary_dynamic_slots_v73","final_scoring_v75","final_scoring_v76",
                    "final_scoring_v77","final_scoring_v78","final_scoring_v79"):
            self.assertNotIn(key,template)
        self.assertNotIn("summary_five_customer",template["macros"])
        self.assertNotIn("pending",template["native_customer"])
        self.assertIn("final_scoring_v80",template)
        self.assertIn("summary_concise",template["macros"])
    def test_no_source_less_fake_reading_or_unverified_domain_reuse(self):
        router=(UI/"WenguaNativeReadingRouter.swift").read_text()
        self.assertIn("throw WenguaNativeReadingError.missingEnergy",router)
        self.assertIn("WenguaPythonVNextVerbatim.sections(",router)
        self.assertIn("unsupportedTopic",router)
if __name__=="__main__":unittest.main()
