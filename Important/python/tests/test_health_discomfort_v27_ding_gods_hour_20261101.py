import unittest,json
from pathlib import Path
from src.wengua.health_discomfort_v19_parity import INNER_YANG,INNER_YIN,_discomfort_power
R=Path(__file__).resolve().parents[1]
class V27(unittest.TestCase):
    def test_customer_policy_and_original_source(self):
        src=json.loads((R/"data/knowledge/health_discomfort/three_source_stem_variants_v14_20261101.json").read_text())
        t=json.loads((R/"data/templates/health_discomfort_v11/native_discomfort_v15.json").read_text())
        self.assertEqual(src["mapping"]["丁"]["qimen_secret_vol13"][0],"齿")
        self.assertEqual(t["customer_stem_overrides"]["丁"]["sites"],["心脏","眼睛"])
        self.assertEqual(set(t["deity_disease_images"]),set("值符 螣蛇 六合 太阴 白虎 玄武 九地 九天".split()))
        self.assertEqual(INNER_YANG,{1,8,3,4});self.assertEqual(INNER_YIN,{9,2,7,6})
        for path in ("src/wengua/health_discomfort_v19_parity.py","ios/WenguaAppUI/WenguaNativeDiscomfortV15.swift"):
            code=(R/path).read_text()
            for token in ("内盘","外盘","时干","力量","deity_disease_images","customer_stem_overrides"):
                self.assertIn(token,code)
            self.assertNotIn("丁主齿",code)
            self.assertIn("脏腑泛象",code)
        table=json.loads((R/"data/mobile/health_vnext/health_energy_200.json").read_text())["tables"]
        self.assertEqual(_discomfort_power("stem","丁",{"id":4},"木",table,[{"branch":"辰","stage":"衰"},{"branch":"巳","stage":"帝旺"}]),"极大")
if __name__=="__main__":unittest.main()
