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
    def test_no_adjacent_anatomy_invented_by_summary(self):
        self.assertIn('lead=="左肩" {focusRegion="左肩一带"}',SWIFT)
        self.assertIn('lead=="右耳" {focusRegion="右耳周围"}',SWIFT)
        self.assertIn('elif lead=="左肩":focusRegion="左肩一带"',PYTHON)
        self.assertIn('elif lead=="右耳":focusRegion="右耳周围"',PYTHON)
        self.assertNotIn('左侧耳肩一带',SWIFT)
        self.assertNotIn('右侧耳肩一带',PYTHON)
    def test_original_symbol_symptoms_and_81_formed_full_prose(self):
        for token in ('selectedStemImage','formationMeaning','orderedFormations',
                      'let starDoorGodFull=','let doorPower=try sourceStrength',
                      'deityClue','badSigns(stem,illness)'):
            self.assertIn(token,SWIFT)
        for token in ('selected_stem_image','formation_meaning','orderedFormations',
                      'starDoorGodFull','GOD_TIERS','original_clue','flags(stem,illness)'):
            self.assertIn(token,PYTHON)
        self.assertIn('doorRel=="符号克宫"',SWIFT)
        self.assertIn('doorRel=="符号克宫"',PYTHON)
    def test_surgery_and_severe_pain_cannot_replace_tianrui_site(self):
        self.assertIn('var candidateSites=trauma ? injurySites : originalSites',SWIFT)
        self.assertIn('injurySites).prefix(1).map{$0}',SWIFT)
        self.assertIn('candidates=list(injurySites if trauma else originalSites)',PYTHON)
        self.assertIn('if trauma else injurySites[:1])',PYTHON)
        self.assertNotIn('else if useInjury {\n            for site in injurySites',SWIFT)
        self.assertNotIn('elif use_injury:\n        for site in injurySites:',PYTHON)
    def test_no_unconditional_injury_or_natal(self):
        self.assertIn('if useInjury',SWIFT)
        self.assertIn('if use_injury',PYTHON)
        self.assertIn('if (required[i]=="02_injury" && !useInjury)',SWIFT)
        self.assertIn('if x["id"]=="02_injury" and not use_injury:continue',PYTHON)

if __name__=="__main__":
    unittest.main()
