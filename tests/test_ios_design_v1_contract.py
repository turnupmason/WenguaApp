"""V3 UI contract: true Qimen professional nine palaces sourced from sealed V3.9.1.

Five-element glyph coloring is by actual symbol, not star/door/deity category.
Real 10-stem/12-life palaces and horse/void/heaven-vs-earth tomb shown on grid
and detail. This is not native Xcode runtime verification or medical prediction.
"""
from __future__ import annotations
import json,re,unittest
from html.parser import HTMLParser
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
HTML=ROOT/"ios/design-v1/preview.html"
COLORS=ROOT/"ios/design-v1/five-element-colors.js"
FIXTURE=ROOT/"ios/design-v1/chart-facts-v3.js"
SWIFT=ROOT/"ios/WenguaAppUI/WenguaDesignPreviewApp.swift"
POLICY=ROOT/"ios/design-v1/issue-policy.js"
AUDIT=ROOT/"data/evaluation/health_v391/four_fixed_random_real_hour_charts_SOURCE_AUDIT.json"
class Tags(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids=set()
    def handle_starttag(self,tag,attrs):
        d=dict(attrs)
        if d.get("id"):self.ids.add(d["id"])

def load_js_json(path,identifier):
    data=path.read_text("utf8")
    marker="root."+identifier+" = "
    start=data.index(marker)+len(marker)
    stop=data.index(";\n})(typeof",start)
    return json.loads(data[start:stop])

class V3SourceUI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html=HTML.read_text("utf8")
        cls.swift=SWIFT.read_text("utf8")
        cls.colors=COLORS.read_text("utf8")
        cls.fixture=load_js_json(FIXTURE,"WenguaVerifiedCharts")
        cls.audit=json.loads(AUDIT.read_text("utf8"))["samples"]
    def test_true_palace_data_and_all_sealed_v391_customer_readings(self):
        assert len(self.fixture["samples"])==len(self.audit)==4
        ids=[4,9,2,3,5,7,8,1,6]
        for x,old in zip(self.fixture["samples"],self.audit):
            self.assertEqual(x["iso"],old["local_datetime"])
            self.assertEqual(x["pillars"],old["four_pillars"])
            self.assertEqual(x["solarTerm"],old["solar_term"])
            self.assertEqual(x["originalReading"],old["v391_customer_reading_text"])
            self.assertEqual(x["readingSections"],old["new_v391_customer_sections"])
            self.assertEqual([p["p"] for p in x["palaces"]],ids)
            self.assertEqual(x["palaces"][4]["heaven"],[])
            original={p["palace"]:p for p in old["book_verifiable_chart_facts"]["complete_eight_palaces_full12"]["outer_eight_palaces"]}
            for p in x["palaces"]:
                if p["p"]==5:continue
                oldp=original[p["p"]]
                self.assertEqual(p["earth"],oldp["earth_stem"])
                self.assertEqual(p["door"],oldp["door"])
                self.assertEqual(p["deity"],oldp["deity"])
                self.assertEqual(p["heaven"],[{"star":v["star"].replace("星",""),
                    "stem":v["carried_stem"],"stages":v["lifecycle"]["actual_stage_facts"]}
                    for v in oldp["heaven"]])
    def test_actual_void_horse_tomb_are_recomputed_and_visible(self):
        h={"申":"寅","子":"寅","辰":"寅","寅":"申","午":"申","戌":"申",
           "巳":"亥","酉":"亥","丑":"亥","亥":"巳","卯":"巳","未":"巳"}
        tomb={"甲":"未","乙":"戌","丙":"戌","丁":"丑","戊":"戌","己":"丑",
              "庚":"丑","辛":"辰","壬":"辰","癸":"未"}
        for x in self.fixture["samples"]:
            self.assertEqual(x["hourHorse"],h[x["pillars"]["hour"][1]])
            for p in x["palaces"]:
                self.assertEqual(p["void"],[s for s in p["branches"] if s in x["voidBranches"]])
                self.assertEqual(p["horse"],x["hourHorse"] if x["hourHorse"] in p["branches"] else None)
                for t in p["tomb"]:
                    self.assertEqual(tomb[t["stem"]],t["branch"])
                    self.assertIn(t["branch"],p["branches"])
                    if t["plane"]=="天盘":
                        self.assertIn(t["stem"],[z["stem"] for z in p["heaven"]])
                    else:self.assertEqual(t["stem"],p["earth"])
        self.assertEqual(self.fixture["samples"][0]["palaces"][0]["horse"],"巳")
        self.assertEqual(self.fixture["samples"][0]["palaces"][8]["void"],["戌","亥"])
        self.assertTrue(any(t["plane"]=="地盘" for t in self.fixture["samples"][0]["palaces"][8]["tomb"]))
        self.assertTrue(any(t["plane"]=="天盘" for t in self.fixture["samples"][1]["palaces"][6]["tomb"]))
        self.assertIn("statusBadges(p)",self.html)
        self.assertIn("天盘与地盘分别实算",self.html)
        self.assertIn("驿马 · 入墓",self.html)
        self.assertIn('p.void.length',self.html)
    def test_true_five_element_color_map_not_category_colors(self):
        c=self.colors
        for text in ["ELEMENT_COLORS","const STEM=","const STAR=","const DOOR=",
                     "const DEITY=","玄武:\"水\"","白虎:\"金\"","九地:\"土\"",
                     "九天:\"金\"","杜门:\"木\"","天心:\"金\""]:
            self.assertIn(text,c)
        self.assertIn('color("deity",p.deity)',self.html)
        self.assertIn('color("star",z.star)',self.html)
        self.assertIn('color("door",p.door)',self.html)
        self.assertIn('color("stem",p.earth)',self.html)
        self.assertIn("enum QFive",self.swift)
        self.assertIn("QFive.shade(\"deity\"",self.swift)
        self.assertIn("QFive.shade(\"door\"",self.swift)
        self.assertIn("QFive.heavenTombs(palace)",self.swift)
        self.assertIn("QFive.earthTombs(palace)",self.swift)
    def test_sample_selector_updates_narrative_too(self):
        for fragment in ['id="sample-switcher"','chooseSample(i)','renderHeader(); renderBoard(); renderReading();',
            'demo.readingSections','sourceCharts=window.WenguaVerifiedCharts.samples',
            'document.querySelector("#palaces").addEventListener("click"', '五行颜色图例']:
            self.assertIn(fragment,self.html)
    def test_original_30second_and_15day_rules_survive(self):
        self.assertIn('30_000',self.html)
        self.assertIn('engineResultValidated',POLICY.read_text("utf8"))
        self.assertIn('persistedRecord!==true',POLICY.read_text("utf8"))
        self.assertNotIn("WenguaIssuePolicy.commitCompletedCast(",self.html)
        self.assertIn('15天',self.html)
    def test_all_screen_elements_and_no_fake_live_cast(self):
        parser=Tags();parser.feed(self.html)
        for id in ("board","setup","ritual","reading","palaces","overlay",
                   "sheet-main","seconds","question","sample-switcher"):
            self.assertIn(id,parser.ids)
        self.assertIn("非实时起盘",self.html)
        self.assertNotIn("calculate_health_symbolic_score",self.html)
        self.assertNotIn("吉凶概率",self.html)
        self.assertIn("QPalace.actualSourceFixture",self.swift)
        self.assertEqual(self.swift.count("@main"),1)
if __name__=="__main__":unittest.main()
