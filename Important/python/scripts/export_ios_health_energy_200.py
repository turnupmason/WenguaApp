"""Check exact active 8x25 matrices packaged to iOS, no retyping."""
import argparse,json
from pathlib import Path
from src.wengua.factor_energy_25_rules import USER_STAR_25,USER_STAR_RELATIONS
from src.wengua.user_domain_matrices_20261023 import (
  DOOR_POWER,DOOR_COLUMNS,STEM_POWER,STEM_COLUMNS,CONTROL_GRID_BY_ID,COLS)
ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/"data/mobile/health_vnext/health_energy_200.json"

def source_data():
    return {
      "schema":"wengua_ios_native_energy_200_vnext_20261026",
      "version":"user_20261023_v3_200_cells_preserved_as_20261026_app_resource",
      "source":["src/wengua/factor_energy_25_rules.py:USER_STAR_25",
                "src/wengua/user_domain_matrices_20261023.py:DOOR_POWER/STEM_POWER/CONTROL_GRID_BY_ID"],
      "note":"8x25 identical cells from current original Python. Native full scoring parity not approved.",
      "tables":{
        "star":{"columns":list(USER_STAR_RELATIONS),"rows":{k:list(v) for k,v in USER_STAR_25.items()}},
        "door":{"columns":list(DOOR_COLUMNS),"rows":{k:list(v) for k,v in DOOR_POWER.items()}},
        "stem":{"columns":list(STEM_COLUMNS),"rows":{k:list(v) for k,v in STEM_POWER.items()}},
        **{k:{"columns":list(COLS),"rows":{s:list(c) for s,c in v.items()}} for k,v in CONTROL_GRID_BY_ID.items()},
      }
    }
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--check",action="store_true")
    args=ap.parse_args()
    src=source_data()
    assert len(src["tables"])==8
    assert sum(len(row) for t in src["tables"].values() for row in t["rows"].values())==200
    if args.check:
        assert json.loads(DEST.read_text(encoding="utf8"))==src,"iOS matrices drift from authoritative Python!"
    else:
        DEST.parent.mkdir(parents=True,exist_ok=True)
        DEST.write_text(json.dumps(src,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
if __name__=="__main__":main()
