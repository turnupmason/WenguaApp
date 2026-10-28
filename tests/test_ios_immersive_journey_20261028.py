"""UI integration gates for the Oct 28 immersive native entry.

These do not claim that iOS Simulator builds pass; that is a separate macOS
xcodebuild + resource check. This test never alters V8 rules or numeric outcomes.
"""
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
UI=ROOT/"ios/WenguaAppUI"

class ImmersiveJourney(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.main=(UI/"WenguaDesignPreviewApp.swift").read_text()
        cls.cloud=(UI/"WenguaCloudWelcome.swift").read_text()
        cls.journey=(UI/"WenguaDomainJourneyScreen.swift").read_text()
        cls.premium=(UI/"WenguaPremiumReadingView.swift").read_text()
        cls.router=(UI/"WenguaNativeReadingRouter.swift").read_text()
        cls.explain=(UI/"WenguaNativeCustomerView.swift").read_text()
        cls.project=(UI/"project.yml").read_text()
        cls.template=json.loads(
            (ROOT/"data/templates/health_severity_vnext/reading_template.json").read_text())
    def test_cloud_first_then_reveal_domains_then_select_topic(self):
        self.assertIn("WenguaCloudWelcomeScreen {",self.main)
        self.assertIn("WenguaDomainJourneyScreen(select:",self.main)
        self.assertIn("欢迎来到",self.cloud)
        self.assertIn("开始问卦",self.cloud)
        self.assertIn("请问你有什么",self.journey)
        self.assertIn("chosenDomain=item.id",self.journey)
        self.assertIn("chosenTopic=item.id",self.journey)
        self.assertIn(".delay(Double(index)*0.045)",self.journey)
        self.assertIn("if selected.enabled { select(selected) }",self.journey)
    def test_real_confirm_time_only_and_30sec_invariant(self):
        self.assertIn("let finalInstant=Date()",self.main)
        self.assertIn("guard let calmEnds, Date() >= calmEnds",self.main)
        self.assertIn("Date().addingTimeInterval(30)",self.main)
        self.assertIn("QIssuePolicy.commitRealCompletedCast(key,validated:true,stored:true)",self.main)
        self.assertIn("try WenguaNativeReadingRouter.compose(",self.main)
        self.assertNotIn("DatePicker(\"手动选择年月日时分\"",self.main)
        self.assertNotIn("useCurrentInstant",self.main)
        self.assertNotIn("chosenTime",self.main)
    def test_role_watermarks_are_exact_native_role_palaces_and_overlap(self):
        self.assertIn("rolePalaces:review.roles",self.router)
        self.assertIn("var rolePalaces: [String:Int]? = nil",self.router)
        self.assertIn("guard let roles=reading?.rolePalaces else { return [] }",self.premium)
        for role,label in [("illness","病"),("doctor","西医"),("medicine","中医"),
                           ("chief","大吉神"),("hour","病事"),("patient","被测人")]:
            self.assertIn(f'("{role}","{label}")',self.premium)
        self.assertIn('identityLabels.joined(separator:"／")',self.main)
        self.assertIn("WenguaPalaceIdentity.labels(nativeReading,palaceID:palace.id)",self.main)
        self.assertIn("identityLabels.isEmpty",self.main)
        self.assertIn("if palace.id == 5",self.main)
        self.assertIn("WenguaVNextEngine.compute(",self.router)
    def test_no_line_under_door_and_return_to_top_both_views(self):
        self.assertIn("// No divider between the door and heaven stem.",self.main)
        self.assertNotIn("Rectangle().fill(QStyle.line.opacity(0.7)).frame(height:1)",self.main)
        self.assertEqual(self.main.count("WenguaReturnToTop {"),2)
        self.assertIn('reader.scrollTo("readingTop",anchor:.top)',self.main)
    def test_dark_light_and_readability(self):
        self.assertIn('@AppStorage("wengua:appearance")',self.main)
        self.assertIn('appearance=="dark" ? .dark',self.main)
        self.assertIn('appearance=="light" ? .light',self.main)
        self.assertIn('mode=option.0',self.cloud)
        self.assertIn('static let surface = Color(uiColor: .secondarySystemGroupedBackground)',self.main)
        self.assertIn("QStyle.surface",self.explain)
        self.assertIn("WenguaNativeCustomerView(reading:reading)",self.main)
        self.assertIn('id == "90_review"',self.premium)
        self.assertIn('id == "91_timing"',self.premium)
    def test_xcodegen_and_frozen_templates(self):
        for name in ["WenguaCloudWelcome.swift","WenguaDomainJourneyScreen.swift",
                     "WenguaPremiumReadingView.swift"]:
            self.assertIn(name,self.project)
        self.assertEqual(self.template["schema"],
                         "health_severity_user_editable_template_v20261027_v8_selected_signifier_all_relations")
        self.assertIn("综上所述，此病为{grade}。",self.template["macros"]["overall_resolved"])

if __name__=="__main__":
    unittest.main()
