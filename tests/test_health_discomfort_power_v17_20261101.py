"""V17 body-location powers, immutable original sources, and source-hidden prose."""
from pathlib import Path
import json
import re
import unittest

ROOT=Path(__file__).resolve().parents[1]
NATIVE=ROOT/"ios/WenguaAppUI/WenguaNativeDiscomfortV15.swift"
TEMPLATE=ROOT/"data/templates/health_discomfort_v11/native_discomfort_v15.json"
ENERGY=ROOT/"data/mobile/health_vnext/health_energy_200.json"
PAIRS=ROOT/"data/knowledge/health_81_excel_20261025/81_pairs.tsv"
WORKFLOW=ROOT/".github/workflows/ios_v80_xcode_simulator_build.yml"

class SitePowerV17Test(unittest.TestCase):
    def test_all_200_cells_and_81_pair_rows_are_original(self):
        grids=json.loads(ENERGY.read_text(encoding="utf8"))["tables"]
        self.assertEqual(set(grids),{"star","door","stem","normal",
             "fake_void_attacker","fake_void_target","true_void_attacker","true_void_target"})
        self.assertTrue(all(len(t["columns"])==5 and len(t["rows"])==5 for t in grids.values()))
        self.assertEqual(sum(len(row) for t in grids.values() for row in t["rows"].values()),200)
        self.assertEqual(len(PAIRS.read_text(encoding="utf8").strip().splitlines()),82)

    def test_render_placeholders_are_bound(self):
        t=json.loads(TEMPLATE.read_text(encoding="utf8"))
        self.assertEqual(t["schema"],"wengua_health_discomfort_native_v20_conditional_injury_20261101")
        self.assertEqual(len(t["sections"]),9)
        native=NATIVE.read_text(encoding="utf8")
        match=re.search(r'let values:\[String:String\]=\[(.*?)\]\s*let required=',native,re.S)
        self.assertIsNotNone(match)
        keys=set(re.findall(r'"([a-z_]+)":',match.group(1)))
        placeholders=set(re.findall(r'\{([a-z_]+)\}',
            " ".join(s["text"] for s in t["sections"])))
        self.assertFalse(placeholders-keys,placeholders-keys)
        self.assertIn("sourceStrength(\"star\",\"天芮星\"",native)
        self.assertIn("sourceStrength(\"door\",\"伤门\"",native)
        self.assertIn("actualRolePower(actor.mainStem,actorCarrier",native)
        self.assertIn("WenguaNativeActorSource.jiaCarrier",native)
        self.assertIn("WenguaVNextEngine.godTiers",native)
        self.assertIn("formationNames.joined",native)
        self.assertIn("WenguaNativeEnergyBundle.fromData(energy)",native)
        self.assertIn('sourceStrength("stem",illness.earthStem,illness,illness.earthStages)',native)

    def test_exclude_internal_or_unhelpful_comments_from_customer_words(self):
        j=json.loads(TEMPLATE.read_text(encoding="utf8"))
        text="\n".join(s["text"] for s in j["sections"])
        for banned in ("涉及不同身体区域的分别列明","不把每个器官都说成同一个位置",
                       "illness_power","door_power","deity_power","sky_power",
                       "illness_focus","injury_focus","hour_focus","疼痛","强弱","凶",
                       "依《神奇之门》","《三命通会》","格分+","内部计分"):
            self.assertNotIn(banned,text)

    def test_never_confuse_negative_palace_score_with_power(self):
        native=NATIVE.read_text(encoding="utf8")
        self.assertNotIn("abs(",native)
        self.assertNotIn("roleScores",native)
        self.assertIn("voidState(illness)",native)
        self.assertIn('["极大","大"].contains(tier)',native)
        self.assertIn('["小","极小"].contains(injuryPower)',native)
        self.assertIn('["极大","大"]',native)
        self.assertIn('candidateSites.enumerated().map',native)
        self.assertIn('let leadSites=ranked.prefix(2)',native)
        self.assertIn('if illnessVoid=="true_void"',native)
        self.assertIn('let actorSiteHit=sourceLocation(patientPalace)',native)
        self.assertIn('let auxIDs=Set([actor.siblingAuxiliaryPalace',native)
        self.assertIn('output.trimmingCharacters(in:.whitespacesAndNewlines).isEmpty',native)
        self.assertIn('let birdPower=',native)
        self.assertIn('let birdStemPower=',native)
        self.assertIn('let deityPower=',native)

    def test_two_random_swift_clocks_get_both_source_tables(self):
        smoke=(ROOT/"ios/WenguaAppUI/NativeDiscomfortV15Smoke.swift").read_text()
        workflow=WORKFLOW.read_text()
        self.assertIn('energy:energy,pairs:pairs)',smoke)
        self.assertIn('Int.random(in:',smoke)
        self.assertIn('"父亲"',smoke)
        self.assertIn('"姐姐"',smoke)
        self.assertIn('actor.genderPalace==6',smoke)
        self.assertIn('actor.siblingAuxiliaryPalace==4',smoke)
        self.assertIn('data/mobile/health_vnext/health_energy_200.json',workflow)
        self.assertIn('data/knowledge/health_81_excel_20261025/81_pairs.tsv',workflow)
        self.assertIn("native_site_validation.txt",workflow)
        self.assertIn("V18_NATIVE_SITE_PASS 父亲 yin",workflow)
        self.assertIn("V18_NATIVE_SITE_PASS 姐姐 yang",workflow)

if __name__=="__main__":
    unittest.main()
