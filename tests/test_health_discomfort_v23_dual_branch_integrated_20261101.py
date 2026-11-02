"""V23 real original 200-cell branch audit and single-palace customer contract.
These are cultural source strength facts, not a clinical diagnosis.
"""
import json
import re
import unittest
from pathlib import Path

from src.wengua.health_discomfort_v19_parity import _power

ROOT=Path(__file__).resolve().parents[1]
CORE=ROOT/"ios/WenguaAppUI/WenguaNativeCore.swift"
SWIFT=ROOT/"ios/WenguaAppUI/WenguaNativeDiscomfortV15.swift"
PYTHON=ROOT/"src/wengua/health_discomfort_v19_parity.py"
ENERGY=ROOT/"data/mobile/health_vnext/health_energy_200.json"
TEMPLATE=ROOT/"data/templates/health_discomfort_v11/native_discomfort_v15.json"
PALACES={1:("子",),2:("未","申"),3:("卯",),4:("辰","巳"),
         6:("戌","亥"),7:("酉",),8:("丑","寅"),9:("午",)}
ELEMENTS=dict(zip("甲乙丙丁戊己庚辛壬癸",
                  ("木","木","火","火","土","土","金","金","水","水")))
TIERS={"极小","小","中等","大","极大"}

def true_stages():
    code=CORE.read_text(encoding="utf8")
    result={}
    for stem,row in re.findall(
        r'^\s*"([甲乙丙丁戊己庚辛壬癸])": \[([^\n]+)\],?\s*$',
        code,re.M):
        matches=dict(re.findall(r'"([子丑寅卯辰巳午未申酉戌亥])":"([^"]+)"',row))
        if len(matches)==12:
            result[stem]=matches
    if len(result)!=10:raise ValueError("Original 10x12 real stage source missing")
    return result

class V23BranchSourceAndPalace(unittest.TestCase):
    def test_400_stem_palace_month_combinations_and_45_unmerged_cases(self):
        stages=true_stages()
        tables=json.loads(ENERGY.read_text(encoding="utf8"))["tables"]
        self.assertEqual(len(tables["stem"]["rows"]),5)
        count=0
        conflicting=[]
        for stem in stages:
            for palace,branches in PALACES.items():
                for month in ("木","火","土","金","水"):
                    rowpowers=[]
                    for branch in branches:
                        stage={"branch":branch,"stage":stages[stem][branch]}
                        power=_power("stem",stem,{"id":palace},month,tables,[stage])
                        self.assertIn(power,TIERS,(stem,palace,month,branch))
                        rowpowers.append(power)
                    count+=1
                    if len(set(rowpowers))>1:
                        conflicting.append((stem,palace,month,rowpowers))
        self.assertEqual(count,400)
        self.assertEqual(len(conflicting),45)
        self.assertTrue(any(x[:3]==("丁",4,"木") and x[3]==["大","极大"]
                            for x in conflicting))
        # A specific *previously approved* Geng/Xun exception is not a
        # license to invent an "always take highest strength" global rule.
        self.assertIn('gengXun=symbol=="庚" && palace==4',(
            ROOT/"ios/WenguaAppUI/WenguaNativeVNextEngine.swift").read_text())
    def test_public_single_palace_contains_all_original_powers(self):
        swift=SWIFT.read_text(encoding="utf8")
        py=PYTHON.read_text(encoding="utf8")
        tmpl=json.loads(TEMPLATE.read_text(encoding="utf8"))
        self.assertEqual(tmpl["schema"],
            "wengua_health_discomfort_native_v23_integrated_palace_20261101")
        self.assertIn("stemBranchFacts",swift)
        self.assertIn("stem_branch_facts",py)
        self.assertIn("sourceStrength(\"stem\",stem,p,[stage])",swift)
        self.assertIn('source_strength("stem",stem,p,[stage])',py)
        self.assertIn('starDoorGodFull,formsFull,dangerFull',swift)
        self.assertIn('(originalLocation,starDoorGodFull,formsFull,dangerFull)',py)
        self.assertIn('"formation_full":"","danger_full":""',py)
        self.assertIn('"formation_full":"","danger_full":""',swift)
        self.assertIn('bodyEvidence.append',swift)
        self.assertIn('bodyEvidence.append',py)
        self.assertIn("本宫天地干伏吟",swift)
        self.assertIn("本宫天地干伏吟",py)
        self.assertNotIn('取最旺作为单一档位',swift)
    def test_real_native_random_case_guards_no_brackets_or_waiting(self):
        smoke=(ROOT/"ios/WenguaAppUI/NativeDiscomfortV15Smoke.swift").read_text()
        self.assertIn('!reading.sections.joinedDescription.contains("待核")',smoke)
        self.assertIn('!reading.sections.joinedDescription.contains("（")',smoke)
        self.assertIn('!reading.sections.joinedDescription.contains("）")',smoke)
        self.assertIn('reading.sections.first!.text.contains("天地格")',smoke)
        self.assertIn('id=="07_formation" || $0.id=="08_constraints"',smoke)

if __name__=="__main__":
    unittest.main()
