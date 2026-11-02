"""Check all current 8*25 source rows are byte-semantic equivalents in mobile bundle."""
import unittest,json
from pathlib import Path
from scripts.export_ios_health_energy_200 import source_data
ROOT=Path(__file__).resolve().parents[1]
class Mobile200Parity(unittest.TestCase):
    def test_actual_all_200_cells_match_python_exactly(self):
        data=json.loads((ROOT/"data/mobile/health_vnext/health_energy_200.json").read_text("utf8"))
        self.assertEqual(data,source_data())
        self.assertEqual(sum(len(row) for t in data["tables"].values() for row in t["rows"].values()),200)
if __name__=="__main__":unittest.main()
