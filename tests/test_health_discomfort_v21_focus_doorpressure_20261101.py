"""V21 location-only regression: genuine door-over-palace pressure, no scattershot sites.
Traditional cultural positions are NOT clinically validated diagnosis.
"""
import unittest
from pathlib import Path
from src.wengua.health_discomfort_v19_parity import _directed, DOOR_ELEMENTS, ELEMENTS

ROOT=Path(__file__).resolve().parents[1]
SWIFT=(ROOT/"ios/WenguaAppUI/WenguaNativeDiscomfortV15.swift").read_text(encoding="utf8")
PYTHON=(ROOT/"src/wengua/health_discomfort_v19_parity.py").read_text(encoding="utf8")
SMOKE=(ROOT/"ios/WenguaAppUI/NativeDiscomfortV15Smoke.swift").read_text(encoding="utf8")

class V21FocusedDoorPressure(unittest.TestCase):
    def test_all_eight_door_pressure_real_directed_relations(self):
        # Door controls palace => pressure. Never call palace-controls-door pressure.
        where={"开门":(3,4),"休门":(9,),"生门":(1,),
               "伤门":(8,2),"杜门":(8,2),"景门":(6,7),
               "死门":(1,),"惊门":(3,4)}
        for door,ids in where.items():
            actual=[p for p in ELEMENTS if _directed(DOOR_ELEMENTS[door],ELEMENTS[p])=="符号克宫"]
            self.assertEqual(set(actual),set(ids),door)
        opposite={"开门":9,"休门":8,"生门":3,"伤门":6,
                  "杜门":7,"景门":1,"死门":4,"惊门":9}
        for door,p in opposite.items():
            self.assertEqual(_directed(DOOR_ELEMENTS[door],ELEMENTS[p]),"宫克符号")
    def test_source_mapped_sites_not_replaced_by_unrelated_doors(self):
        for code in (SWIFT,PYTHON):
            self.assertIn('doorRel=="符号克宫"',code)
            self.assertIn('secondSite=""',code)
            self.assertIn('头发',code)
            self.assertIn("与时干同符同在",code)
            self.assertIn("长辈辅宫",code)
            self.assertIn("门迫",code)
        self.assertNotIn('doorRel=="宫克符号" &&',SWIFT)
        self.assertNotIn('doorRel=="宫克符号" and',PYTHON)
        self.assertIn('let leadSites=ranked.prefix(1)',SWIFT)
        self.assertIn('leadSites=[x[0] for x in ranked[:1]]',PYTHON)
        self.assertIn('V20_PREVIEW_BEGIN',SMOKE)
        self.assertIn('需以实际检查核实',SMOKE)
    def test_no_unconditional_injury_or_natal(self):
        self.assertIn('if useInjury',SWIFT)
        self.assertIn('if use_injury',PYTHON)
        self.assertIn('if (required[i]=="02_injury" && !useInjury)',SWIFT)
        self.assertIn('if x["id"]=="02_injury" and not use_injury:continue',PYTHON)

if __name__=="__main__":
    unittest.main()
