"""V26 client text must identify real stem organs and avoid meta-level calculations."""
from pathlib import Path
import unittest,json
ROOT=Path(__file__).resolve().parents[1]
class V26Wording(unittest.TestCase):
    def test_template_and_both_composers(self):
        t=json.loads((ROOT/"data/templates/health_discomfort_v11/native_discomfort_v15.json").read_text())
        self.assertEqual(t["schema"],"wengua_health_discomfort_native_v26_precise_injury_speech_20261101")
        for name in ("src/wengua/health_discomfort_v19_parity.py","ios/WenguaAppUI/WenguaNativeDiscomfortV15.swift"):
            code=(ROOT/name).read_text()
            for invalid in ("按较高一档取","这一干象较突出","可考虑此处受到病事牵连的象意"):
                self.assertNotIn(invalid,code)
            for needed in ("另宫刑墓：","有伤痛或损伤之象","受压闭藏、不易显露之象","与主病位分开核对"):
                self.assertIn(needed,code)
            self.assertNotIn("只作一次位置证据",code)
            self.assertNotIn("另宫只作病事参照",code)
            self.assertIn('脏腑泛象',code)
if __name__=="__main__":unittest.main()
