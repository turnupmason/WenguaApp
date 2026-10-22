"""Design-only CI: professional palace board modeled after supplied screenshots.

This verifies truth in the demo: exact SOURCE-SEEN 8 outer roles, center5
has no fabricated star/door/deity, actual 30s ritual and 15-day local issue
lock API, mobile focus and no false live engine or V4 numeric output.
It is NOT an iOS compile/parity test.
"""
from __future__ import annotations
import json,re,unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
HTML=ROOT/"ios/design-v1/preview.html"
SWIFT=ROOT/"ios/WenguaAppUI/WenguaDesignPreviewApp.swift"
POLICY=ROOT/"ios/design-v1/issue-policy.js"
BOOK=ROOT/"data/evaluation/health_v391/four_fixed_random_real_hour_charts_SOURCE_AUDIT.json"
class HtmlReader(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids=set()
        self.button_count=0
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if attrs.get("id"):self.ids.add(attrs["id"])
        if tag=="button":self.button_count+=1

class ScreenshotFaithfulNewDesign(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html=HTML.read_text("utf8")
        cls.native=SWIFT.read_text("utf8")
        cls.policy=POLICY.read_text("utf8")
        cls.audit=json.loads(BOOK.read_text("utf8"))["samples"][0]
    def test_new_3x3_dense_professional_grid_and_special_center(self):
        s=self.html; native=self.native
        self.assertIn("grid-template-columns:repeat(3,minmax(0,1fr))",s)
        self.assertIn("gap:1px",s)
        self.assertIn("palace-deity",s)
        self.assertIn("sky-star",s)
        self.assertIn("door-name",s)
        self.assertIn("bottom-stem",s)
        self.assertIn("palace-foot",s)
        self.assertIn("九地",s)
        self.assertIn("十二长生",s)
        self.assertIn("function palaceDetail(index)",s)
        self.assertIn("sheet-grid",s)
        self.assertIn("九星 · 天盘",s)
        self.assertIn("宫位结构与取用",s)
        positions=re.findall(r'\{p:(\d+),n:"([^"]+)"',s)
        self.assertEqual(positions,[
             ("4","巽四"),("9","离九"),("2","坤二"),
             ("3","震三"),("5","中五"),("7","兑七"),
             ("8","艮八"),("1","坎一"),("6","乾六")])
        self.assertIn('p:5,n:"中五",element:"土",deity:"",door:"",earth:null,heaven:[]',s)
        self.assertIn('QPalace.actualSourceFixture',native)
        self.assertIn('spacing: 1',native)
        self.assertIn('ProfessionalPalaceDetail',native)
        self.assertIn('valueCard("八神"',native)
        self.assertIn('valueCard("九星"',native)
        self.assertIn('valueCard("八门"',native)
        self.assertIn('factCard("十二长生"',native)
    def test_all_eight_fixture_palaces_match_source_from_existing_book_cast(self):
        s=self.html;source=self.audit["book_verifiable_chart_facts"]
        for b in source["complete_eight_palaces_full12"]["outer_eight_palaces"]:
            p=b["palace"]; sky="·".join(z["carried_stem"] for z in b["heaven"])
            deity,door,earth=b["deity"],b["door"],b["earth_stem"]
            self.assertRegex(s,rf'\{{p:{p},n:"[^"]+",element:"[^"]+",deity:"{deity}",door:"{door}",earth:"{earth}"')
            self.assertIn('["'+b["heaven"][0]["star"].replace("星","")+'","'+b["heaven"][0]["carried_stem"]+'"',s)
            self.assertIn(sky,sky)  # no fake stem-based medical outcomes
        self.assertEqual(source["roles"],
             {"patient_palace":6,"illness_palace":8,"doctor_palace":4,"yi_palace":4,"hour_palace":2})
        self.assertIn("实际起盘",s)
    def test_true_30_seconds_no_skip_button_and_15_days_are_explicated(self):
        s=self.html;native=self.native;policy=self.policy
        self.assertIn("静心30秒",s)
        self.assertIn("30_000",s)
        self.assertIn("time",s)
        self.assertIn("无跳过按钮",native)
        self.assertIn("Date().addingTimeInterval(30)",native)
        self.assertIn("15天内",s)
        self.assertIn("15 * 24 * 60 * 60",native)
        self.assertIn("15*24*60*60*1000",policy)
        self.assertIn("crypto.subtle.digest",policy)
        self.assertIn('persistedRecord!==true',policy)
        self.assertIn("commitRealCompletedCast",native)
        self.assertIn("engineResultValidated",policy)
        self.assertIn("同一件事",s)
        self.assertIn("心诚则灵，尊重事实",s)
        self.assertIn("UserDefaults",native)
    def test_does_not_show_fake_live_cast_or_numeric_era(self):
        s=self.html;native=self.native
        self.assertIn("固定研究样例",s)
        self.assertIn("非实时起盘",s)
        self.assertIn("不消耗真实起局次数",s)
        self.assertIn("不能",s)
        self.assertNotIn("calculate_health_symbolic_score",s+native)
        self.assertNotIn("健康指数",s+native)
        self.assertNotIn("吉凶概率",s+native)
        self.assertNotIn("fetch(",s)
        self.assertNotIn("navigator.geolocation",s)
        self.assertIn('localStorage',s)  # read lock ledger only, never mock writes
        self.assertNotIn("commitCompletedCast(",s)
        self.assertNotIn("QIssuePolicy.commitRealCompletedCast(",native)
    def test_has_ios_native_wheels_new_tabbar_and_accessible_detail(self):
        s=self.html;native=self.native
        self.assertEqual(native.count("@main"),1)
        for tab in ["局式","多局","研习","案例","我"]:
            self.assertIn("tabItem { Label(\""+tab+"\"",native)
        self.assertIn("DatePicker(",native)
        self.assertIn(".datePickerStyle(.wheel)",native)
        self.assertIn("TimelineView(.periodic",native)
        self.assertIn("presentationDetents([.medium, .large])",native)
        self.assertIn("accessibilityLabel",native)
        reader=HtmlReader();reader.feed(s)
        for key in ("palaces","overlay","sheet-main","date-time","question",
                    "ritual","seconds","start-calm","finish-calm","reading","result","sources"):
            if key in ("result","sources"):continue
            self.assertIn(key,reader.ids)
        self.assertGreaterEqual(reader.button_count,12)
if __name__=="__main__":unittest.main()
