"""Static iOS DESIGN contract tests; not a substitute for Xcode iPhone builds.

Ensures design doesn't regress to false nine-palace casts or output the abandoned
V4 numbers. Old PWA app/ and verified Python engine must remain unchanged.
"""
from __future__ import annotations
import json,re,unittest
from html.parser import HTMLParser
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MOCK=ROOT/"ios/design-v1/preview.html"
NATIVE=ROOT/"ios/WenguaAppUI/WenguaDesignPreviewApp.swift"
DOC=ROOT/"docs/IOS_V1_PRODUCT_UX_DESIGN_2026-10-22.md"
ACTIVE=ROOT/"src/wengua/health_text_pipeline.py"
FULL=ROOT/"archives/sqlite/wengua_health_v391_active_numerics_disabled_manifest.json"

class HtmlReader(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids=set()
        self.buttons=0
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if a.get("id"):self.ids.add(a["id"])
        if tag=="button":self.buttons+=1

class IOSVisualContract(unittest.TestCase):
    def test_uses_only_staged_active_v39_no_numeric_scoring(self):
        for p in (MOCK,NATIVE,DOC,ACTIVE,FULL):
            self.assertTrue(p.is_file(),str(p))
        js=MOCK.read_text("utf8")
        native=NATIVE.read_text("utf8")
        self.assertNotIn("calculate_health_symbolic_score",js)
        self.assertNotIn("health_symbolic_score_v42",native)
        self.assertNotIn("健康指数",js)
        self.assertNotIn("吉凶概率",js)
        self.assertIn("非实时起盘",js)
        self.assertIn("固定历史样例",native)
        self.assertIn("demo",native.lower())
        self.assertIn("无 V4.2 分数", (ROOT/"ios/design-v1/README.md").read_text("utf8"))
        self.assertIn("auto_cast_health_v39_text",ACTIVE.read_text("utf8"))
        self.assertTrue(json.loads(FULL.read_text("utf8"))["new_active_v391_has_no_score_or_probability"])
    def test_standalone_browser_mock_has_true_9_standard_positions(self):
        s=MOCK.read_text("utf8")
        parser=HtmlReader();parser.feed(s)
        for key in ("home","question","result","history","more","board","read","sources",
                    "palaces","reading-sections","cover"):
            self.assertIn(key,parser.ids)
        self.assertGreaterEqual(parser.buttons,8)
        names=re.findall(r'\{id:(\d+),n:"([^"]+)"',s)
        self.assertEqual(names,[
            ("4","巽四"),("9","离九"),("2","坤二"),
            ("3","震三"),("5","中五"),("7","兑七"),
            ("8","艮八"),("1","坎一"),("6","乾六")])
        self.assertIn('id:5,n:"中五",s:"",d:"",g:""',s)
        self.assertIn("traditional",DOC.read_text("utf8").lower())
    def test_not_fake_api_web_requests_or_saved_health_details(self):
        s=MOCK.read_text("utf8")
        self.assertNotIn("fetch(",s)
        self.assertNotIn("localStorage",s)
        self.assertNotIn("serviceWorker",s)
        self.assertNotIn("navigator.geolocation",s)
        self.assertIn("演示结果使用固定历史样例",NATIVE.read_text("utf8"))
        self.assertNotIn("pythonkit",NATIVE.read_text("utf8").lower())
    def test_native_has_one_entry_3_tabs_9_palaces_and_no_finished_engine_claim(self):
        s=NATIVE.read_text("utf8")
        self.assertEqual(s.count("@main"),1)
        self.assertIn("NavigationStack",s)
        self.assertIn("TabView",s)
        for t in ("问事","记录","更多"):
            self.assertIn('Label("'+t+'"',s)
        self.assertEqual(s.count(".init(id: "),9)
        for token in ('Pill(text: "固定历史样例 · 非实时起盘"',".sheet(item: $selectedPalace)",
                      "DemoReadingSection","读", "V3.9.1"):
            self.assertIn(token,s)
        self.assertNotIn('Text("100',s)
    def test_reference_sources_are_not_rewritten_by_design(self):
        for path in ("src/wengua/health_severity_v39.py",
                     "src/wengua/health_severity_v391_active.py",
                     "data/knowledge/phrase_library/health_v391/severity_text_full12_template.json"):
            self.assertTrue((ROOT/path).is_file())
        self.assertTrue((ROOT/"app/index.html").is_file())
if __name__=="__main__":
    unittest.main()
